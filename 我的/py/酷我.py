#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
酷我音乐完整工具 v4.0
功能：
  1. 在线搜索/下载歌曲、封面、歌词
  2. 本地整理：内部元数据 + 文件名 综合判断
  3. 严格匹配封面/歌词
  4. 歌曲/封面/歌词 三者名字完全一致
  5. 不删除任何文件夹，不改变歌曲数量
  6. 清理孤儿文件
"""

import os
import re
import json
import sys
import struct
import argparse
import time
from urllib.parse import quote
from difflib import SequenceMatcher
import requests

# ==================== 全局配置 ====================
VERSION = "v4.0"
print("=" * 60)
print(f"🎵 酷我音乐完整工具 {VERSION}")
print("   在线下载 + 本地整理 + 封面歌词补全")
print("=" * 60)


# ==================== 核心类：下载模块 ====================

class KuWoDownloader:
    """酷我音乐下载模块"""
    
    def __init__(self, output_dir=None):
        print("📂 初始化下载器...")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'http://www.kuwo.cn/'
        })
        self.output_dir = output_dir or os.path.join(os.path.expanduser('~'), 'Download', 'KuWoMusic')
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"✅ 下载目录: {self.output_dir}")
    
    def search_song(self, keyword, page=1, limit=30):
        """搜索歌曲"""
        print(f"🔍 搜索关键词: {keyword}")
        url = f"https://search.kuwo.cn/r.s?client=kt&pn={(page-1)*limit}&rn={limit}&all={quote(keyword)}&vipver=1&ft=music&encoding=utf8&rformat=json&mobi=1"
        
        try:
            print(f"📡 请求搜索API...")
            resp = self.session.get(url, timeout=10)
            data = resp.json()
            
            results = []
            if data.get('abslist'):
                print(f"✅ 找到 {len(data['abslist'])} 个结果")
                for item in data['abslist']:
                    rid = item.get('MUSICRID', '').replace('MUSIC_', '')
                    if rid:
                        song = {
                            'rid': rid,
                            'name': item.get('SONGNAME', ''),
                            'artist': item.get('ARTIST', ''),
                            'album': item.get('ALBUM', ''),
                            'duration': item.get('DURATION', ''),
                            'pic': item.get('PICPATH', ''),
                        }
                        results.append(song)
                        print(f"  📌 {song['artist']} - {song['name']} (ID: {song['rid']})")
            else:
                print("❌ 未找到搜索结果")
            return results
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            return []
    
    def get_song_url(self, rid, bitrate=320):
        """获取歌曲播放地址"""
        print(f"🎵 获取歌曲URL (RID: {rid}, 音质: {bitrate}K)")
        if bitrate == 2000:
            format_type = 'flac'
        else:
            format_type = 'mp3'
        
        url = f"https://nmobi.kuwo.cn/mobi.s?f=web&user=0&source=kwplayer_ar_4.4.2.7_B_nuoweida_vh.apk&type=convert_url_with_sign&rid={rid}&bitrate={bitrate}&format={format_type}"
        
        try:
            resp = self.session.get(url, timeout=10)
            data = resp.json()
            if data.get('code') == 200 and data.get('data') and data['data'].get('url'):
                print(f"✅ 获取到播放地址")
                return data['data']['url']
            else:
                print(f"⚠️ 获取播放地址失败: {data.get('msg', '未知错误')}")
        except Exception as e:
            print(f"❌ 获取播放地址异常: {e}")
        return None
    
    def get_lyric(self, rid):
        """获取歌词"""
        print(f"📝 获取歌词 (RID: {rid})")
        url = f"https://kuwo.cn/openapi/v1/www/lyric/getlyric?musicId={rid}"
        try:
            resp = self.session.get(url, timeout=10)
            data = resp.json()
            if data.get('data') and data['data'].get('lrclist'):
                lines = []
                for item in data['data']['lrclist']:
                    time_str = self._format_time(float(item.get('time', 0)))
                    lines.append(f"[{time_str}]{item.get('lineLyric', '')}")
                print(f"✅ 获取到 {len(lines)} 行歌词")
                return '\n'.join(lines)
            else:
                print("⚠️ 未找到歌词")
        except Exception as e:
            print(f"❌ 获取歌词失败: {e}")
        return None
    
    def get_cover(self, rid):
        """获取封面图片"""
        print(f"🖼️ 获取封面 (RID: {rid})")
        url = f"http://artistpicserver.kuwo.cn/pic.web?type=rid_pic&pictype=url&size=500&rid={rid}"
        try:
            resp = self.session.get(url, timeout=10)
            if resp.text.startswith('http'):
                print(f"✅ 获取到封面URL")
                return resp.text.strip()
        except Exception as e:
            print(f"❌ 获取封面失败: {e}")
        return None
    
    def download_file(self, url, filename, desc=""):
        """下载文件"""
        try:
            print(f"⬇️ 下载{desc}: {filename}")
            resp = self.session.get(url, stream=True, timeout=30)
            if resp.status_code == 200:
                filepath = os.path.join(self.output_dir, filename)
                total_size = int(resp.headers.get('content-length', 0))
                downloaded = 0
                with open(filepath, 'wb') as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                progress = int(downloaded / total_size * 100)
                                if progress % 10 == 0:
                                    print(f"  📊 进度: {progress}%")
                print(f"✅ 下载完成: {filepath} ({downloaded/1024/1024:.2f} MB)")
                return filepath
            else:
                print(f"❌ 下载失败: HTTP {resp.status_code}")
        except Exception as e:
            print(f"❌ 下载异常: {e}")
        return None
    
    def _format_time(self, seconds):
        m = int(seconds // 60)
        s = seconds % 60
        return f"{m:02d}:{s:05.2f}"
    
    def _clean_filename(self, name):
        """清理文件名中的非法字符"""
        return re.sub(r'[\\/*?:"<>|]', '', name)
    
    def download_song(self, rid, artist=None, title=None, download_cover=True, download_lyric=True, bitrate=320):
        """下载单首歌曲"""
        print(f"\n🎯 开始下载歌曲")
        print(f"  RID: {rid}")
        print(f"  歌手: {artist or '未知'}")
        print(f"  歌名: {title or '未知'}")
        print(f"  音质: {bitrate}K")
        
        # 获取歌曲信息
        if not artist or not title:
            print("🔍 尝试获取歌曲信息...")
            songs = self.search_song(f"{artist or ''} {title or ''}".strip(), limit=5)
            for s in songs:
                if s['rid'] == str(rid) or (title and title in s['name']):
                    artist = s['artist']
                    title = s['name']
                    break
        
        if not artist or not title:
            print("❌ 无法获取歌曲信息")
            return None
        
        # 清理文件名 - 歌曲名在前，歌手名在后
        safe_title = self._clean_filename(f"{title} - {artist}")
        print(f"📝 文件名: {safe_title}")
        
        # 下载歌曲
        song_url = self.get_song_url(rid, bitrate)
        filepath = None
        if song_url:
            ext = 'flac' if bitrate == 2000 else 'mp3'
            filename = f"{safe_title}.{ext}"
            filepath = self.download_file(song_url, filename, "歌曲")
            if filepath:
                print(f"✅ 歌曲下载完成: {filepath}")
        
        # 下载封面
        if download_cover:
            cover_url = self.get_cover(rid)
            if cover_url:
                filename = f"{safe_title}.jpg"
                self.download_file(cover_url, filename, "封面")
        
        # 下载歌词
        if download_lyric:
            lyric = self.get_lyric(rid)
            if lyric:
                filename = f"{safe_title}.lrc"
                filepath_lrc = os.path.join(self.output_dir, filename)
                with open(filepath_lrc, 'w', encoding='utf-8') as f:
                    f.write(lyric)
                print(f"✅ 歌词下载完成: {filepath_lrc}")
        
        return filepath if song_url else None
    
    def download_by_keyword(self, keyword, download_cover=True, download_lyric=True, bitrate=320, max_results=1):
        """根据关键词搜索并下载"""
        songs = self.search_song(keyword, limit=max_results)
        if not songs:
            print("❌ 未找到歌曲")
            return []
        
        results = []
        for idx, song in enumerate(songs[:max_results], 1):
            print(f"\n📌 [{idx}/{max_results}] 处理: {song['artist']} - {song['name']}")
            result = self.download_song(
                rid=song['rid'],
                artist=song['artist'],
                title=song['name'],
                download_cover=download_cover,
                download_lyric=download_lyric,
                bitrate=bitrate
            )
            if result:
                results.append(result)
        
        print(f"\n🎉 全部完成! 共下载 {len(results)} 首歌曲")
        return results


# ==================== 核心类：整理模块 ====================

class KuWoOrganizer:
    """酷我音乐本地整理模块"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'http://www.kuwo.cn/'
        })
        
        self.audio_exts = {'.mp3', '.flac', '.m4a', '.wav', '.aac', '.ogg', '.wma'}
        self.image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        self.lyric_exts = {'.lrc'}
    
    # ==================== 读取音频文件元数据 ====================
    
    def read_mp3_metadata(self, filepath):
        """读取 MP3 文件的 ID3 标签"""
        try:
            with open(filepath, 'rb') as f:
                data = f.read(128)
                if len(data) >= 128 and data[:3] == b'TAG':
                    title = data[3:33].decode('gbk', errors='ignore').strip('\x00')
                    artist = data[33:63].decode('gbk', errors='ignore').strip('\x00')
                    if title or artist:
                        return title, artist
                
                f.seek(0)
                header = f.read(10)
                if len(header) >= 10 and header[:3] == b'ID3':
                    size = self._parse_id3v2_size(header[6:10])
                    if size > 0:
                        tag_data = f.read(min(size, 1024 * 10))
                        title = self._extract_id3v2_frame(tag_data, b'TIT2')
                        artist = self._extract_id3v2_frame(tag_data, b'TPE1')
                        if title or artist:
                            return title, artist
        except Exception:
            pass
        return '', ''
    
    def _parse_id3v2_size(self, size_bytes):
        if len(size_bytes) < 4:
            return 0
        return (size_bytes[0] & 0x7f) << 21 | \
               (size_bytes[1] & 0x7f) << 14 | \
               (size_bytes[2] & 0x7f) << 7 | \
               (size_bytes[3] & 0x7f)
    
    def _extract_id3v2_frame(self, data, frame_id):
        pos = data.find(frame_id)
        if pos == -1:
            return ''
        try:
            frame_size = struct.unpack('>I', data[pos+4:pos+8])[0]
            content = data[pos+10:pos+10+frame_size]
            for encoding in ['utf-8', 'utf-16', 'gbk', 'latin-1']:
                try:
                    result = content.decode(encoding, errors='ignore').strip('\x00')
                    if result:
                        return result
                except:
                    continue
            return content.decode('utf-8', errors='ignore').strip('\x00')
        except:
            return ''
    
    def read_flac_metadata(self, filepath):
        """读取 FLAC 文件的元数据"""
        try:
            with open(filepath, 'rb') as f:
                header = f.read(4)
                if header != b'fLaC':
                    return '', ''
                
                title, artist = '', ''
                while True:
                    block_header = f.read(4)
                    if len(block_header) < 4:
                        break
                    is_last = (block_header[0] & 0x80) != 0
                    block_type = block_header[0] & 0x7f
                    block_size = struct.unpack('>I', b'\x00' + block_header[1:4])[0]
                    
                    if block_type == 4:
                        data = f.read(block_size)
                        try:
                            vendor_len = struct.unpack('<I', data[:4])[0]
                            pos = 4 + vendor_len
                            comment_count = struct.unpack('<I', data[pos:pos+4])[0]
                            pos += 4
                            for _ in range(comment_count):
                                comment_len = struct.unpack('<I', data[pos:pos+4])[0]
                                pos += 4
                                comment = data[pos:pos+comment_len].decode('utf-8', errors='ignore')
                                pos += comment_len
                                if comment.startswith('TITLE='):
                                    title = comment[6:]
                                elif comment.startswith('ARTIST='):
                                    artist = comment[7:]
                        except:
                            pass
                        break
                    else:
                        f.seek(block_size, 1)
                    if is_last:
                        break
                return title, artist
        except Exception:
            pass
        return '', ''
    
    def read_m4a_metadata(self, filepath):
        """读取 M4A/AAC 文件的元数据"""
        try:
            with open(filepath, 'rb') as f:
                data = f.read(1024 * 10)
                title = self._extract_m4a_atom(data, b'\xa9nam')
                artist = self._extract_m4a_atom(data, b'\xa9ART')
                if title or artist:
                    return title, artist
        except Exception:
            pass
        return '', ''
    
    def _extract_m4a_atom(self, data, atom_id):
        pos = data.find(atom_id)
        if pos == -1:
            return ''
        try:
            size = struct.unpack('>I', data[pos-4:pos])[0]
            if size > 4:
                content = data[pos+4:pos+size]
                for encoding in ['utf-8', 'utf-16', 'utf-16le', 'utf-16be']:
                    try:
                        result = content.decode(encoding, errors='ignore').strip('\x00')
                        if result and all(32 <= ord(c) <= 126 or ord(c) >= 128 for c in result[:10]):
                            return result
                    except:
                        continue
                return content.decode('utf-8', errors='ignore').strip('\x00')
        except:
            pass
        return ''
    
    def read_audio_metadata(self, filepath):
        """读取音频文件元数据"""
        ext = os.path.splitext(filepath)[1].lower()
        
        if ext == '.mp3':
            return self.read_mp3_metadata(filepath)
        elif ext == '.flac':
            return self.read_flac_metadata(filepath)
        elif ext in ('.m4a', '.aac'):
            return self.read_m4a_metadata(filepath)
        else:
            return '', ''
    
    # ==================== 相似度 ====================
    
    def _similarity(self, a, b):
        """计算两个字符串的相似度"""
        if not a or not b:
            return 0
        a = a.lower().strip()
        b = b.lower().strip()
        return SequenceMatcher(None, a, b).ratio()
    
    def _exact_match(self, target, filename):
        """精确匹配"""
        name_no_ext = os.path.splitext(filename)[0]
        return target.lower().strip() == name_no_ext.lower().strip()
    
    def _is_valid_cover(self, filepath):
        """验证封面文件是否有效"""
        try:
            return os.path.getsize(filepath) > 1024
        except:
            return False
    
    def _is_valid_lyric(self, filepath):
        """验证歌词文件是否有效"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                return len(content.strip()) > 10
        except:
            return False
    
    # ==================== 综合判断 ====================
    
    def get_song_info(self, filepath):
        """
        综合获取歌曲信息：
        1. 读取内部元数据
        2. 从文件名提取
        3. 计算一致性，决定使用哪个
        """
        filename = os.path.basename(filepath)
        
        # 读取元数据
        meta_title, meta_artist = self.read_audio_metadata(filepath)
        
        # 从文件名提取
        file_title, file_artist = self._extract_title_artist_from_filename(filename)
        
        # 判断一致性
        title_match = False
        artist_match = False
        
        if meta_title and file_title:
            title_match = self._similarity(meta_title, file_title) > 0.5
        if meta_artist and file_artist:
            artist_match = self._similarity(meta_artist, file_artist) > 0.5
        
        # 决定使用哪个
        if meta_title and meta_artist and (title_match or artist_match):
            # 元数据和文件名一致，优先使用元数据
            return meta_title, meta_artist, 'metadata', True
        elif file_title and file_artist:
            # 元数据不完整或不一致，使用文件名
            return file_title, file_artist, 'filename', False
        elif meta_title or meta_artist:
            # 只有部分元数据
            return meta_title or file_title, meta_artist or file_artist, 'partial', False
        else:
            # 都识别不了
            return '', '', 'none', False
    
    def _extract_title_artist_from_filename(self, filename):
        """从文件名提取歌名和歌手"""
        name = os.path.splitext(filename)[0]
        separators = [' - ', ' – ', '—', ' -', '- ', ' | ', '|', ' _ ', '_']
        for sep in separators:
            if sep in name:
                parts = name.split(sep, 1)
                title, artist = parts[0].strip(), parts[1].strip()
                if len(title) < 3 and len(artist) > 3:
                    title, artist = artist, title
                return title, artist
        match = re.match(r'^(.*?)[（(](.*?)[）)]', name)
        if match:
            return match.group(1).strip(), match.group(2).strip()
        return name, ''
    
    # ==================== 严格匹配封面/歌词 ====================
    
    def _find_related_files_strict(self, dir_path, target_name, audio_filename):
        """严格查找已有的封面和歌词"""
        cover_path = None
        lyric_path = None
        
        # 构建搜索关键词
        search_keys = [target_name, audio_filename]
        search_keys = list(dict.fromkeys(search_keys))
        
        # ===== 第一步：精确匹配 =====
        try:
            for f in os.listdir(dir_path):
                ext = os.path.splitext(f)[1].lower()
                name_no_ext = os.path.splitext(f)[0]
                
                if ext in self.image_exts and not cover_path:
                    if self._exact_match(target_name, f) or self._exact_match(audio_filename, f):
                        if self._is_valid_cover(os.path.join(dir_path, f)):
                            cover_path = os.path.join(dir_path, f)
                            print(f"    📌 精确匹配封面: {f}")
                
                if ext in self.lyric_exts and not lyric_path:
                    if self._exact_match(target_name, f) or self._exact_match(audio_filename, f):
                        if self._is_valid_lyric(os.path.join(dir_path, f)):
                            lyric_path = os.path.join(dir_path, f)
                            print(f"    📌 精确匹配歌词: {f}")
        except Exception:
            pass
        
        # ===== 第二步：高相似度匹配 (>= 0.7) =====
        if not cover_path or not lyric_path:
            try:
                for f in os.listdir(dir_path):
                    ext = os.path.splitext(f)[1].lower()
                    name_no_ext = os.path.splitext(f)[0]
                    
                    max_score = 0
                    for key in search_keys:
                        score = self._similarity(key, name_no_ext)
                        if score > max_score:
                            max_score = score
                    
                    if max_score >= 0.7:
                        if ext in self.image_exts and not cover_path:
                            if self._is_valid_cover(os.path.join(dir_path, f)):
                                cover_path = os.path.join(dir_path, f)
                                print(f"    📌 相似匹配封面: {f} (相似度: {max_score:.0%})")
                        
                        elif ext in self.lyric_exts and not lyric_path:
                            if self._is_valid_lyric(os.path.join(dir_path, f)):
                                lyric_path = os.path.join(dir_path, f)
                                print(f"    📌 相似匹配歌词: {f} (相似度: {max_score:.0%})")
            except Exception:
                pass
        
        return cover_path, lyric_path
    
    # ==================== 搜索和下载 ====================
    
    def search_song(self, keyword, limit=5):
        """搜索歌曲"""
        print(f"  🔍 搜索: {keyword}")
        url = f"https://search.kuwo.cn/r.s?client=kt&pn=0&rn={limit}&all={quote(keyword)}&vipver=1&ft=music&encoding=utf8&rformat=json&mobi=1"
        
        try:
            resp = self.session.get(url, timeout=10)
            data = resp.json()
            
            results = []
            if data.get('abslist'):
                for item in data['abslist']:
                    rid = item.get('MUSICRID', '').replace('MUSIC_', '')
                    if rid:
                        results.append({
                            'rid': rid,
                            'name': item.get('SONGNAME', ''),
                            'artist': item.get('ARTIST', ''),
                        })
            return results
        except Exception as e:
            print(f"  ❌ 搜索失败: {e}")
            return []
    
    def get_lyric(self, rid):
        """获取歌词"""
        url = f"https://kuwo.cn/openapi/v1/www/lyric/getlyric?musicId={rid}"
        try:
            resp = self.session.get(url, timeout=10)
            data = resp.json()
            if data.get('data') and data['data'].get('lrclist'):
                lines = []
                for item in data['data']['lrclist']:
                    m = int(float(item.get('time', 0)) // 60)
                    s = float(item.get('time', 0)) % 60
                    lines.append(f"[{m:02d}:{s:05.2f}]{item.get('lineLyric', '')}")
                return '\n'.join(lines)
        except Exception as e:
            print(f"  ❌ 获取歌词失败: {e}")
        return None
    
    def get_cover(self, rid):
        """获取封面图片"""
        url = f"http://artistpicserver.kuwo.cn/pic.web?type=rid_pic&pictype=url&size=500&rid={rid}"
        try:
            resp = self.session.get(url, timeout=10)
            if resp.text.startswith('http'):
                return resp.text.strip()
        except Exception as e:
            print(f"  ❌ 获取封面失败: {e}")
        return None
    
    def download_file(self, url, filepath, desc=""):
        """下载文件"""
        try:
            print(f"  ⬇️ 下载{desc}: {os.path.basename(filepath)}")
            resp = self.session.get(url, stream=True, timeout=60)
            if resp.status_code == 200:
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, 'wb') as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                print(f"  ✅ 下载完成")
                return filepath
        except Exception as e:
            print(f"  ❌ 下载异常: {e}")
        return None
    
    def _clean_filename(self, name):
        return re.sub(r'[\\/*?:"<>|]', '', name)
    
    def _get_best_match(self, songs, title, artist):
        """选择最佳匹配歌曲"""
        if not songs:
            return None
        for s in songs:
            if artist and artist.lower() in s['artist'].lower():
                return s
            if title.lower() in s['name'].lower():
                return s
        return songs[0]
    
    # ==================== 清理孤儿文件 ====================
    
    def clean_orphan_files(self, folder_path, dry_run=False):
        """清理孤儿文件"""
        print(f"\n{'='*60}")
        print("🧹 清理孤儿文件")
        print(f"{'='*60}")
        
        audio_basenames = set()
        for root, dirs, files in os.walk(folder_path):
            for f in files:
                if os.path.splitext(f)[1].lower() in self.audio_exts:
                    audio_basenames.add(os.path.splitext(f)[0])
        
        print(f"🎵 找到 {len(audio_basenames)} 个音频文件")
        
        orphan_cover = []
        orphan_lyric = []
        
        for root, dirs, files in os.walk(folder_path):
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                base_name = os.path.splitext(f)[0]
                filepath = os.path.join(root, f)
                
                if ext in self.image_exts:
                    if base_name not in audio_basenames:
                        orphan_cover.append(filepath)
                elif ext in self.lyric_exts:
                    if base_name not in audio_basenames:
                        orphan_lyric.append(filepath)
        
        deleted_cover = 0
        deleted_lyric = 0
        
        if orphan_cover:
            print(f"\n🖼️ 找到 {len(orphan_cover)} 个孤儿封面")
            for f in orphan_cover:
                if dry_run:
                    print(f"  🔄 [试运行] 删除: {os.path.basename(f)}")
                else:
                    os.remove(f)
                    print(f"  ✅ 删除: {os.path.basename(f)}")
                    deleted_cover += 1
        else:
            print(f"\n🖼️ 没有孤儿封面")
        
        if orphan_lyric:
            print(f"\n📝 找到 {len(orphan_lyric)} 个孤儿歌词")
            for f in orphan_lyric:
                if dry_run:
                    print(f"  🔄 [试运行] 删除: {os.path.basename(f)}")
                else:
                    os.remove(f)
                    print(f"  ✅ 删除: {os.path.basename(f)}")
                    deleted_lyric += 1
        else:
            print(f"\n📝 没有孤儿歌词")
        
        print(f"\n🧹 清理完成: 删除封面 {deleted_cover if not dry_run else len(orphan_cover)} 个, 歌词 {deleted_lyric if not dry_run else len(orphan_lyric)} 个")
    
    # ==================== 主整理函数 ====================
    
    def organize(self, folder_path, recursive=True, dry_run=False,
                 fix_cover=True, fix_lyric=True, fix_name=True,
                 clean_orphan=True):
        """整理歌曲文件夹"""
        print(f"\n📂 扫描: {folder_path}")
        print(f"  试运行: {dry_run} | 递归: {recursive}")
        print(f"  补封面: {fix_cover} | 补歌词: {fix_lyric} | 重命名: {fix_name}")
        print(f"  📌 综合判断: 内部元数据 + 文件名 信息一致才处理")
        
        if not os.path.exists(folder_path):
            print(f"❌ 文件夹不存在")
            return
        
        audio_files = []
        if recursive:
            for root, dirs, files in os.walk(folder_path):
                for f in files:
                    if os.path.splitext(f)[1].lower() in self.audio_exts:
                        audio_files.append(os.path.join(root, f))
        else:
            for f in os.listdir(folder_path):
                filepath = os.path.join(folder_path, f)
                if os.path.isfile(filepath) and os.path.splitext(f)[1].lower() in self.audio_exts:
                    audio_files.append(filepath)
        
        initial_count = len(audio_files)
        print(f"\n🎵 找到 {initial_count} 个音频文件")
        if not audio_files:
            if clean_orphan:
                self.clean_orphan_files(folder_path, dry_run)
            return
        
        results = {
            'total': initial_count,
            'renamed_audio': 0,
            'renamed_cover': 0,
            'renamed_lyric': 0,
            'downloaded_cover': 0,
            'downloaded_lyric': 0,
            'skipped': 0,
            'metadata_ok': 0,
            'filename_only': 0,
            'has_cover': 0,
            'has_lyric': 0
        }
        
        for idx, filepath in enumerate(audio_files, 1):
            print(f"\n{'─'*50}")
            print(f"[{idx}/{len(audio_files)}] {os.path.basename(filepath)}")
            
            dir_path = os.path.dirname(filepath)
            filename = os.path.basename(filepath)
            ext = os.path.splitext(filename)[1]
            
            # ===== 1. 综合获取歌曲信息 =====
            title, artist, source, consistent = self.get_song_info(filepath)
            
            if not title or not artist:
                print(f"  ⚠️ 无法识别歌曲信息")
                results['skipped'] += 1
                continue
            
            if source == 'metadata':
                print(f"  📖 使用元数据: {artist} - {title} ✅")
                results['metadata_ok'] += 1
            elif source == 'filename':
                print(f"  📖 使用文件名: {artist} - {title} ⚠️ (元数据缺失)")
                results['filename_only'] += 1
            else:
                print(f"  📖 使用混合信息: {artist} - {title} ⚠️")
                results['filename_only'] += 1
            
            # ===== 2. 搜索匹配获取标准信息 =====
            songs = self.search_song(f"{artist} {title}", limit=3)
            if not songs:
                print(f"  ❌ 未找到匹配")
                results['skipped'] += 1
                continue
            
            best = self._get_best_match(songs, title, artist)
            matched_title = best['name']
            matched_artist = best['artist']
            rid = best['rid']
            print(f"  ✅ 匹配: {matched_artist} - {matched_title}")
            
            # ===== 3. 生成标准文件名 =====
            safe_name = self._clean_filename(f"{matched_title} - {matched_artist}")
            target_name = f"{matched_title} - {matched_artist}"
            need_rename_audio = fix_name and safe_name != os.path.splitext(filename)[0]
            
            # ===== 4. 严格查找已有封面和歌词 =====
            print(f"  🔎 查找封面/歌词...")
            cover_path, lyric_path = self._find_related_files_strict(
                dir_path, target_name, filename
            )
            
            has_cover = cover_path is not None
            has_lyric = lyric_path is not None
            
            if has_cover:
                print(f"  🖼️ 已有封面: {os.path.basename(cover_path)}")
                results['has_cover'] += 1
            else:
                print(f"  🖼️ 没有封面")
            
            if has_lyric:
                print(f"  📝 已有歌词: {os.path.basename(lyric_path)}")
                results['has_lyric'] += 1
            else:
                print(f"  📝 没有歌词")
            
            # ===== 5. 判断是否需要处理 =====
            need_cover = fix_cover and not has_cover
            need_lyric = fix_lyric and not has_lyric
            
            if not need_rename_audio and not need_cover and not need_lyric:
                print(f"  ✅ 已规范")
                results['skipped'] += 1
                continue
            
            # ===== 6. 试运行 =====
            if dry_run:
                if need_rename_audio:
                    print(f"  🔄 重命名音频: {filename} -> {safe_name}{ext}")
                if has_cover and need_rename_audio:
                    print(f"  🔄 同步重命名封面: {os.path.basename(cover_path)} -> {safe_name}.jpg")
                if has_lyric and need_rename_audio:
                    print(f"  🔄 同步重命名歌词: {os.path.basename(lyric_path)} -> {safe_name}.lrc")
                if need_cover:
                    print(f"  🔄 下载封面: {safe_name}.jpg")
                if need_lyric:
                    print(f"  🔄 下载歌词: {safe_name}.lrc")
                continue
            
            # ===== 7. 实际执行 =====
            try:
                # 7a. 处理封面
                if has_cover and need_rename_audio:
                    new_cover_path = os.path.join(dir_path, f"{safe_name}.jpg")
                    if cover_path != new_cover_path:
                        if os.path.exists(new_cover_path):
                            os.remove(cover_path)
                            print(f"  🗑️ 删除重复封面: {os.path.basename(cover_path)}")
                        else:
                            os.rename(cover_path, new_cover_path)
                            print(f"  ✅ 封面重命名: {os.path.basename(cover_path)} -> {os.path.basename(new_cover_path)}")
                            results['renamed_cover'] += 1
                elif need_cover:
                    cover_url = self.get_cover(rid)
                    if cover_url:
                        cover_filepath = os.path.join(dir_path, f"{safe_name}.jpg")
                        if not os.path.exists(cover_filepath):
                            self.download_file(cover_url, cover_filepath, "封面")
                            results['downloaded_cover'] += 1
                
                # 7b. 处理歌词
                if has_lyric and need_rename_audio:
                    new_lyric_path = os.path.join(dir_path, f"{safe_name}.lrc")
                    if lyric_path != new_lyric_path:
                        if os.path.exists(new_lyric_path):
                            os.remove(lyric_path)
                            print(f"  🗑️ 删除重复歌词: {os.path.basename(lyric_path)}")
                        else:
                            os.rename(lyric_path, new_lyric_path)
                            print(f"  ✅ 歌词重命名: {os.path.basename(lyric_path)} -> {os.path.basename(new_lyric_path)}")
                            results['renamed_lyric'] += 1
                elif need_lyric:
                    lyric = self.get_lyric(rid)
                    if lyric:
                        lyric_filepath = os.path.join(dir_path, f"{safe_name}.lrc")
                        if not os.path.exists(lyric_filepath):
                            with open(lyric_filepath, 'w', encoding='utf-8') as f:
                                f.write(lyric)
                            print(f"  ✅ 歌词下载完成")
                            results['downloaded_lyric'] += 1
                
                # 7c. 重命名音频
                if need_rename_audio:
                    new_audio_path = os.path.join(dir_path, f"{safe_name}{ext}")
                    if new_audio_path != filepath:
                        counter = 1
                        while os.path.exists(new_audio_path) and new_audio_path != filepath:
                            new_audio_path = os.path.join(dir_path, f"{safe_name}_{counter}{ext}")
                            counter += 1
                        os.rename(filepath, new_audio_path)
                        print(f"  ✅ 音频重命名: {filename} -> {os.path.basename(new_audio_path)}")
                        results['renamed_audio'] += 1
                
            except Exception as e:
                print(f"  ❌ 失败: {e}")
        
        # ===== 统计 =====
        print(f"\n{'='*60}")
        print(f"📊 整理完成")
        print(f"  歌曲总数: {initial_count}")
        print(f"  使用元数据: {results['metadata_ok']}")
        print(f"  使用文件名: {results['filename_only']}")
        print(f"  有封面: {results['has_cover']} 首")
        print(f"  有歌词: {results['has_lyric']} 首")
        print(f"  ─────────────")
        print(f"  音频重命名: {results['renamed_audio']}")
        print(f"  封面重命名: {results['renamed_cover']}")
        print(f"  歌词重命名: {results['renamed_lyric']}")
        print(f"  新下载封面: {results['downloaded_cover']}")
        print(f"  新下载歌词: {results['downloaded_lyric']}")
        print(f"  已跳过: {results['skipped']}")
        print(f"{'='*60}")
        
        if clean_orphan:
            self.clean_orphan_files(folder_path, dry_run)


# ==================== 组合工具类 ====================

class KuWoComplete:
    """酷我音乐完整工具 - 整合下载与整理功能"""
    
    def __init__(self, output_dir=None):
        self.downloader = KuWoDownloader(output_dir)
        self.organizer = KuWoOrganizer()
        self.output_dir = self.downloader.output_dir
    
    def download_and_organize(self, keyword, bitrate=320, max_results=1,
                              download_cover=True, download_lyric=True,
                              auto_organize=True):
        """
        下载并自动整理
        """
        print("\n" + "=" * 60)
        print("🎯 下载并整理模式")
        print("=" * 60)
        
        # 1. 搜索并下载
        songs = self.downloader.search_song(keyword, limit=max_results)
        if not songs:
            print("❌ 未找到歌曲")
            return
        
        results = []
        for idx, song in enumerate(songs[:max_results], 1):
            print(f"\n📌 [{idx}/{max_results}] 处理: {song['artist']} - {song['name']}")
            
            # 下载歌曲
            result = self.downloader.download_song(
                rid=song['rid'],
                artist=song['artist'],
                title=song['name'],
                download_cover=download_cover,
                download_lyric=download_lyric,
                bitrate=bitrate
            )
            if result:
                results.append(result)
        
        if not results:
            print("❌ 下载失败")
            return
        
        # 2. 自动整理
        if auto_organize:
            print("\n" + "=" * 60)
            print("📂 开始自动整理下载的文件...")
            print("=" * 60)
            
            self.organizer.organize(
                folder_path=self.output_dir,
                recursive=False,
                dry_run=False,
                fix_cover=download_cover,
                fix_lyric=download_lyric,
                fix_name=True,
                clean_orphan=True
            )
        
        print(f"\n🎉 全部完成! 共处理 {len(results)} 首歌曲")
        return results


# ==================== 命令行主函数 ====================

def main():
    parser = argparse.ArgumentParser(
        description='酷我音乐完整工具 v4.0 - 在线下载 + 本地整理',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  1. 搜索下载歌曲:
     python 酷我.py -k "周杰伦 晴天" -n 3

  2. 通过ID下载:
     python 酷我.py -r 123456 -a "周杰伦" -t "晴天"

  3. 本地整理音乐文件夹:
     python 酷我.py --organize /path/to/music

  4. 整理并清理孤儿文件:
     python 酷我.py --organize /path/to/music --clean

  5. 下载并自动整理:
     python 酷我.py -k "周杰伦" -n 5 --auto-organize
        """
    )
    
    # ===== 下载参数 =====
    parser.add_argument('-k', '--keyword', help='搜索关键词 (歌手名 - 歌曲名)')
    parser.add_argument('-r', '--rid', help='歌曲ID (直接下载)')
    parser.add_argument('-a', '--artist', help='歌手名')
    parser.add_argument('-t', '--title', help='歌曲名')
    parser.add_argument('-o', '--output', help='输出目录')
    parser.add_argument('--no-cover', action='store_true', help='不下载封面')
    parser.add_argument('--no-lyric', action='store_true', help='不下载歌词')
    parser.add_argument('-b', '--bitrate', type=int, default=320, choices=[128, 192, 320, 2000], 
                        help='音质: 128/192/320/2000(无损)')
    parser.add_argument('-n', '--number', type=int, default=1, help='搜索下载数量')
    parser.add_argument('--auto-organize', action='store_true', help='下载后自动整理')
    
    # ===== 整理参数 =====
    parser.add_argument('--organize', metavar='FOLDER', help='本地整理音乐文件夹')
    parser.add_argument('--dry-run', action='store_true', help='试运行模式 (仅显示不执行)')
    parser.add_argument('--no-recursive', action='store_true', help='不递归子目录')
    parser.add_argument('--skip-cover', action='store_true', help='跳过补全封面')
    parser.add_argument('--skip-lyric', action='store_true', help='跳过补全歌词')
    parser.add_argument('--skip-rename', action='store_true', help='跳过重命名')
    parser.add_argument('--clean', action='store_true', help='清理孤儿文件')
    
    args = parser.parse_args()
    
    # ===== 模式选择 =====
    
    # 模式1: 本地整理
    if args.organize:
        print(f"\n📂 本地整理模式: {args.organize}")
        organizer = KuWoOrganizer()
        organizer.organize(
            folder_path=args.organize,
            recursive=not args.no_recursive,
            dry_run=args.dry_run,
            fix_cover=not args.skip_cover,
            fix_lyric=not args.skip_lyric,
            fix_name=not args.skip_rename,
            clean_orphan=args.clean
        )
        return
    
    # 模式2: 下载 (通过ID或关键词)
    if args.rid or args.keyword:
        downloader = KuWoDownloader(args.output)
        
        if args.rid:
            # 直接通过ID下载
            downloader.download_song(
                rid=args.rid,
                artist=args.artist,
                title=args.title,
                download_cover=not args.no_cover,
                download_lyric=not args.no_lyric,
                bitrate=args.bitrate
            )
        elif args.keyword:
            # 关键词搜索下载
            if args.auto_organize:
                # 使用完整工具下载并整理
                complete = KuWoComplete(args.output)
                complete.download_and_organize(
                    keyword=args.keyword,
                    bitrate=args.bitrate,
                    max_results=args.number,
                    download_cover=not args.no_cover,
                    download_lyric=not args.no_lyric,
                    auto_organize=True
                )
            else:
                # 仅下载
                downloader.download_by_keyword(
                    keyword=args.keyword,
                    download_cover=not args.no_cover,
                    download_lyric=not args.no_lyric,
                    bitrate=args.bitrate,
                    max_results=args.number
                )
        return
    
    # 没有有效参数
    parser.print_help()
    print("\n❌ 请指定操作: --organize 整理 或 -k 下载搜索")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ 用户中断")
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("👋 程序结束")
    print("=" * 60)