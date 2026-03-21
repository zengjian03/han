# 本地资源管理.py - 完整修复版（修复JSON显示格式和TXT直播源识别）
# 修改内容：所有直播源统一使用线路在上、电视台在下格式，修复HEIC图片识别

import sys
import re
import json
import os
import base64
import hashlib
import time
import urllib.parse
import sqlite3
import glob
import zlib
import xml.etree.ElementTree as ET
import random
from pathlib import Path
from base.spider import Spider

# ==================== 在线直播配置 ====================
ONLINE_LIVE_SOURCES = [
    {
        "id": "migu_live",
        "name": "咪咕直播",
        "url": "https://gh-proxy.org/https://raw.githubusercontent.com/develop202/migu_video/refs/heads/main/interface.txt",
        "color": "#FF6B6B",
        "remarks": "央视/卫视直播",
        "type": "m3u",
        "ua": "com.android.chrome/3.7.0 (Linux;Android 15)",
        "playerType": 2
    },
    {
        "id": "gongdian_live",
        "name": "宫殿直播",
        "url": "https://gongdian.top/tv/iptv",
        "color": "#4ECDC4",
        "remarks": "宫殿直播源",
        "type": "m3u",
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "playerType": 2
    },
    {
        "id": "simple_live",
        "name": "简单直播",
        "url": "http://gh-proxy.org/raw.githubusercontent.com/Supprise0901/TVBox_live/main/live.txt",
        "color": "#6BCB77",
        "remarks": "简单直播源",
        "type": "txt"
    },
    {
        "id": "kulao_tv",
        "name": "裤佬TV直播",
        "url": "https://gh-proxy.org/https://raw.githubusercontent.com/Jsnzkpg/Jsnzkpg/Jsnzkpg/Jsnzkpg1.m3u",
        "color": "#9D65C9",
        "remarks": "裤佬TV直播源",
        "type": "m3u",
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "playerType": 2
    }
]

LIVE_CATEGORY_ID = "online_live"
LIVE_CATEGORY_NAME = "📡 在线直播"
LIVE_CACHE_DURATION = 600

# ==================== 全局请求头自动适配配置 ====================
COMMON_HEADERS_LIST = [
    {
        "name": "Chrome浏览器",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive"
        }
    },
    {
        "name": "Firefox浏览器",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Connection": "keep-alive"
        }
    },
    {
        "name": "okhttp/3",
        "headers": {
            "User-Agent": "okhttp/3.12.11",
            "Accept": "*/*",
            "Connection": "Keep-Alive"
        }
    },
    {
        "name": "手机浏览器",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive"
        }
    },
    {
        "name": "Edge浏览器",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive"
        }
    },
    {
        "name": "Safari浏览器",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive"
        }
    },
    {
        "name": "Android Chrome",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Linux; Android 15) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive"
        }
    }
]

DOMAIN_SPECIFIC_HEADERS = {
    "miguvideo.com": [
        {
            "name": "咪咕专用-Android Chrome",
            "headers": {
                "User-Agent": "com.android.chrome/3.7.0 (Linux;Android 15)",
                "Accept": "*/*",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Connection": "keep-alive",
                "Referer": "https://www.miguvideo.com/"
            }
        },
        {
            "name": "咪咕专用-okhttp",
            "headers": {
                "User-Agent": "okhttp/3.12.11",
                "Accept": "*/*",
                "Connection": "Keep-Alive",
                "Referer": "https://www.miguvideo.com/"
            }
        }
    ],
    "gongdian.top": [
        {
            "name": "宫殿直播专用",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "*/*",
                "Referer": "https://gongdian.top/",
                "Connection": "keep-alive"
            }
        }
    ],
    "t.061899.xyz": [
        {
            "name": "t源专用",
            "headers": {
                "User-Agent": "okhttp/3.12.11",
                "Referer": "http://t.061899.xyz/",
                "Accept": "*/*"
            }
        }
    ],
    "rihou.cc": [
        {
            "name": "日后源专用-Chrome",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Referer": "https://rihou.cc:555/",
                "Accept": "*/*",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Connection": "keep-alive"
            }
        },
        {
            "name": "日后源专用-okhttp",
            "headers": {
                "User-Agent": "okhttp/3.12.11",
                "Referer": "http://rihou.cc:555/",
                "Accept": "*/*",
                "Connection": "Keep-Alive"
            }
        }
    ]
}

# ==================== 路径配置 ====================
ROOT_PATHS = [
    '/storage/emulated/0/Movies/',
    '/storage/emulated/0/Music/',
    '/storage/emulated/0/Download/KuwoMusic/music/',
    '/storage/emulated/0/Download/',
    '/storage/emulated/0/DCIM/Camera/',
    '/storage/emulated/0/Pictures/',
    '/storage/emulated/0/Books/',
    '/storage/emulated/0/VodPlus/wwwroot/lz/',
    '/storage/emulated/0/'
  
]

PATH_TO_CHINESE = {
    '/storage/emulated/0/Movies/': '电影',
    '/storage/emulated/0/Music/': '音乐',
    '/storage/emulated/0/Download/KuwoMusic/music/': '酷我音乐',
    '/storage/emulated/0/Download/': '下载',
    '/storage/emulated/0/DCIM/Camera/': '相机',
    '/storage/emulated/0/Pictures/': '图片',
    '/storage/emulated/0/Books/': '小说',
    '/storage/emulated/0/VodPlus/wwwroot/lz/': '老张',
    '/storage/emulated/0/': '根目录'
}

# ==================== 数据库兼容配置 ====================
DB_COMPAT_MODE = True
MAX_DB_RESULTS = 50000

DB_FIELD_MAPPING = {
    'id': ['id', 'vid', 'video_id', 'film_id', 'vod_id'],
    'name': ['name', 'title', 'vod_name', 'vod_title'],
    'url': ['url', 'link', 'play_url', 'video_url', 'vod_url', 'vod_play_url'],
    'image': ['image', 'pic', 'cover', 'poster', 'vod_pic'],
    'remarks': ['remarks', 'vod_remarks', 'remark', 'note']
}

print("ℹ️ 本地资源管理加载成功 - 完整修复版 + 统一直播源格式 + 修复HEIC图片识别")

# ==================== 数据库读取器 ====================
class DatabaseReader:
    """数据库读取器"""
    
    def __init__(self):
        self.cache = {}
        self.cache_time = {}
        self.cache_duration = 600
    
    def read_sqlite(self, db_path, limit=50000):
        cache_key = f"{db_path}_{os.path.getmtime(db_path)}_{limit}"
        current_time = time.time()
        
        if cache_key in self.cache and current_time - self.cache_time.get(cache_key, 0) < self.cache_duration:
            print(f"📊 使用缓存数据: {os.path.basename(db_path)}, {len(self.cache[cache_key])} 条记录")
            return self.cache[cache_key]
        
        if not os.path.exists(db_path) or not os.access(db_path, os.R_OK):
            return []
        
        out = []
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("PRAGMA cache_size = 10000")
            cursor.execute("PRAGMA page_size = 4096")
            cursor.execute("PRAGMA mmap_size = 30000000000")
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE 'android_%'")
            tables = cursor.fetchall()
            
            skip_tables = ['android_metadata', 'db_config', 'meta', 'crawl_state', 'sqlite_sequence']
            
            for table in tables:
                table_name = table[0]
                if table_name in skip_tables:
                    continue
                items = self.parse_table(cursor, conn, table_name, limit)
                if items:
                    out.extend(items)
                if len(out) >= limit:
                    out = out[:limit]
                    break
            
            conn.close()
        except Exception as e:
            print(f"数据库读取错误: {e}")
            return []
        
        self.cache[cache_key] = out
        self.cache_time[cache_key] = current_time
        return out
    
    def parse_table(self, cursor, conn, table, limit):
        res = []
        try:
            cursor.execute(f"PRAGMA table_info(`{table}`)")
            cols = cursor.fetchall()
            col_names = [col[1] for col in cols]
            
            title_field = self.find_best_match(col_names, ['vod_name', 'name', 'title'])
            url_field = self.find_best_match(col_names, ['play_url', 'vod_play_url', 'vod_url', 'url'])
            pic_field = self.find_best_match(col_names, ['image', 'vod_pic', 'pic'])
            remarks_field = self.find_best_match(col_names, ['vod_remarks', 'remarks'])
            
            if not title_field or not url_field:
                return []
            
            cursor.execute(f"SELECT * FROM `{table}` WHERE `{url_field}` IS NOT NULL AND `{url_field}` != '' LIMIT {limit}")
            rows = cursor.fetchall()
            
            for row in rows:
                row_dict = dict(row)
                play_url_raw = str(row_dict.get(url_field, '')).strip()
                if not play_url_raw:
                    continue
                
                title = str(row_dict.get(title_field, '未命名')).strip()
                
                is_multi = '$' in play_url_raw or '#' in play_url_raw or '$$$' in play_url_raw
                
                item = {
                    'name': title,
                    'url': '' if is_multi else play_url_raw,
                    'play_url': play_url_raw if is_multi else '',
                    'pic': row_dict.get(pic_field, '') if pic_field else '',
                    'remarks': row_dict.get(remarks_field, '') if remarks_field else '',
                }
                res.append(item)
        except Exception as e:
            print(f"解析表 {table} 错误: {e}")
        return res
    
    def find_best_match(self, column_names, candidates):
        for cand in candidates:
            for col in column_names:
                if col.lower() == cand.lower():
                    return col
        for cand in candidates:
            for col in column_names:
                if cand.lower() in col.lower():
                    return col
        return None


# ==================== 小说解析器 ====================
class NovelParser:
    """小说文件解析器"""
    
    @staticmethod
    def parse_txt_novel(file_path):
        """解析TXT小说文件"""
        chapters = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            patterns = [
                r'第[一二三四五六七八九十百千万0-9]+章\s*[^\n]{0,50}',
                r'第[一二三四五六七八九十百千万0-9]+节\s*[^\n]{0,50}',
                r'序章\s*[^\n]{0,50}|楔子\s*[^\n]{0,50}|尾声\s*[^\n]{0,50}',
                r'正文\s+第[一二三四五六七八九十百千万0-9]+章',
                r'Chapter\s+[0-9]+[.:]?\s*[^\n]{0,50}'
            ]
            
            matches = []
            for p in patterns:
                for m in re.finditer(p, content, re.MULTILINE):
                    title = m.group().strip()
                    if title and len(title) > 2 and not title.strip().isdigit():
                        matches.append((m.start(), title))
            
            matches = list(set(matches))
            matches.sort(key=lambda x: x[0])
            
            if matches:
                for i, (pos, title) in enumerate(matches):
                    start = pos
                    end = matches[i + 1][0] if i + 1 < len(matches) else len(content)
                    chap_content = content[start:end].strip()
                    chapters.append({
                        'title': title,
                        'content': chap_content,
                        'index': i
                    })
            else:
                chapters.append({
                    'title': os.path.splitext(os.path.basename(file_path))[0],
                    'content': content,
                    'index': 0
                })
        except Exception as e:
            print(f"解析小说失败: {e}")
        return chapters


# ==================== 主爬虫类 ====================
class Spider(Spider):
    def getName(self):
        return "本地资源管理"
    
    def init(self, extend=""):
        super().init(extend)
        self.root_paths = ROOT_PATHS
        self.path_to_chinese = PATH_TO_CHINESE
        
        # 在线直播配置
        self.online_live_sources = ONLINE_LIVE_SOURCES
        self.live_category_id = LIVE_CATEGORY_ID
        self.live_category_name = LIVE_CATEGORY_NAME
        self.live_cache = {}
        self.live_cache_time = {}
        self.live_cache_duration = LIVE_CACHE_DURATION
        
        # 请求头适配
        self.common_headers_list = COMMON_HEADERS_LIST
        self.domain_specific_headers = DOMAIN_SPECIFIC_HEADERS
        self.successful_headers_cache = {}
        
        self.default_colors = [
            "#FF6B6B", "#4ECDC4", "#FFD93D", "#6BCB77", "#9D65C9", 
            "#FF8C42", "#A2D729", "#FF6B8B", "#45B7D1", "#96CEB4"
        ]
        
        # 文件类型定义 - 添加HEIC/HEIF格式
        self.media_exts = ['mp4', 'mkv', 'avi', 'rmvb', 'mov', 'wmv', 'flv', 'm4v', 'ts', 'm3u8']
        self.audio_exts = ['mp3', 'm4a', 'aac', 'flac', 'wav', 'ogg', 'wma', 'ape']
        self.image_exts = ['jpg', 'jpeg', 'png', 'webp', 'gif', 'bmp', 'ico', 'svg', 'heic', 'heif']
        self.list_exts = ['m3u', 'txt', 'json', 'm3u8']
        self.lrc_exts = ['lrc', 'krc', 'qrc', 'yrc', 'trc']
        self.db_exts = ['db', 'sqlite', 'sqlite3', 'db3']
        self.magnet_exts = ['magnets', 'magnet', 'bt', 'torrent', 'mgt']
        
        # 直播源关键词
        self.live_keywords = ['cctv', '卫视', '频道', '直播', '电视台', 'iptv', 'm3u8', 'live', '咪咕', '央卫', '香港', '台湾', '澳门', '体育', '新闻', '音乐', '综合']
        # 小说关键词
        self.novel_keywords = ['第', '章', '节', '卷', '部', '篇', '集', '小说', '故事', '作者']
        
        self.file_icons = {
            'folder': 'https://img.icons8.com/color/96/000000/folder-invoices.png',
            'video': 'https://img.icons8.com/color/96/000000/video.png',
            'video_playlist': 'https://img.icons8.com/color/96/000000/playlist.png',
            'audio': 'https://img.icons8.com/color/96/000000/audio-file.png',
            'audio_playlist': 'https://img.icons8.com/color/96/000000/musical-notes.png',
            'image': 'https://img.icons8.com/color/96/000000/image.png',
            'image_playlist': 'https://img.icons8.com/color/96/000000/image-gallery.png',
            'list': 'https://img.icons8.com/color/96/000000/list.png',
            'lrc': 'https://img.icons8.com/color/96/000000/lyrics.png',
            'database': 'https://img.icons8.com/color/96/000000/database.png',
            'magnet': 'https://img.icons8.com/color/96/000000/magnet.png',
            'novel': 'https://img.icons8.com/color/96/000000/book.png',
            'text': 'https://img.icons8.com/color/96/000000/document.png',
            'file': 'https://img.icons8.com/color/96/000000/file.png'
        }
        
        self.TRANSPARENT_GIF = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'
        
        # 前缀常量
        self.V_DIR_PREFIX = 'vdir://'
        self.V_ITEM_PREFIX = 'vitem://'
        self.URL_B64U_PREFIX = 'b64u://'
        self.V_ALL_PREFIX = 'vall://'
        self.A_ALL_PREFIX = 'aall://'
        self.FOLDER_PREFIX = 'folder://'
        self.LIST_PREFIX = 'list://'
        self.PICS_PREFIX = 'pics://'
        self.MP3_PREFIX = 'mp3://'
        self.CAMERA_ALL_PREFIX = 'camall://'
        self.MAGNET_PREFIX = 'magnet://'
        self.LIVE_PREFIX = 'live://'
        self.NOVEL_PREFIX = 'novel://'
        self.TEXT_PREFIX = 'text://'

        self.lrc_cache = {}
        self.m3u8_cache = {}
        self.db_reader = DatabaseReader()
        
        # 海报缓存
        self.poster_cache = {}
        
        # 逐字歌词缓存
        self.word_lyrics_cache = {}
        
        # 小说相关缓存
        self.novel_path_cache = {}
        self.novel_chapters_cache = {}
        self.current_novel = {'encoded_path': None, 'file_path': None, 'chapters': []}
        
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        self.session = requests.Session()
        retries = Retry(total=2, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        self.debug_mode = True

    def log(self, msg):
        if self.debug_mode:
            print(f"🔍 [DEBUG] {msg}")

    # ==================== 工具函数 ====================
    
    def b64u_encode(self, data):
        if isinstance(data, str):
            data = data.encode('utf-8')
        encoded = base64.b64encode(data).decode('ascii')
        return encoded.replace('+', '-').replace('/', '_').rstrip('=')
    
    def b64u_decode(self, data):
        data = data.replace('-', '+').replace('_', '/')
        pad = len(data) % 4
        if pad:
            data += '=' * (4 - pad)
        try:
            return base64.b64decode(data).decode('utf-8')
        except:
            return ''
    
    def get_file_ext(self, filename):
        idx = filename.rfind('.')
        if idx == -1:
            return ''
        return filename[idx + 1:].lower()
    
    def is_media_file(self, ext):
        return ext in self.media_exts
    
    def is_audio_file(self, ext):
        return ext in self.audio_exts
    
    def is_image_file(self, ext):
        return ext in self.image_exts
    
    def is_list_file(self, ext):
        return ext in self.list_exts
    
    def is_lrc_file(self, ext):
        return ext in self.lrc_exts
    
    def is_db_file(self, ext):
        return ext in self.db_exts
    
    def is_magnet_file(self, ext):
        return ext in self.magnet_exts
    
    def scan_directory(self, dir_path):
        try:
            if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
                return []
            
            files = []
            for name in os.listdir(dir_path):
                if name.startswith('.') or name in ['.', '..']:
                    continue
                
                full_path = os.path.join(dir_path, name)
                is_dir = os.path.isdir(full_path)
                ext = self.get_file_ext(name)
                
                files.append({
                    'name': name,
                    'path': full_path,
                    'is_dir': is_dir,
                    'ext': ext,
                    'mtime': os.path.getmtime(full_path) if not is_dir else 0,
                })
            
            files.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
            return files
        except:
            return []
    
    def collect_videos_in_dir(self, dir_path):
        files = self.scan_directory(dir_path)
        return [f for f in files if not f['is_dir'] and f['ext'] in self.media_exts]
    
    def collect_audios_in_dir(self, dir_path):
        files = self.scan_directory(dir_path)
        return [f for f in files if not f['is_dir'] and f['ext'] in self.audio_exts]
    
    def collect_images_in_dir(self, dir_path):
        files = self.scan_directory(dir_path)
        return [f for f in files if not f['is_dir'] and f['ext'] in self.image_exts]
    
    def get_file_icon(self, ext, is_dir=False):
        if is_dir:
            return '📁'
        if ext in self.media_exts:
            return '🎬'
        if ext in self.audio_exts:
            return '🎵'
        if ext in self.image_exts:
            return '📷'
        if ext in self.list_exts:
            return '📋'
        if ext in self.lrc_exts:
            return '📝'
        if ext in self.db_exts:
            return '🗄️'
        if ext in self.magnet_exts:
            return '🧲'
        return '📄'
    
    def is_playable_url(self, url):
        u = str(url).lower().strip()
        if not u:
            return False
        
        protocols = [
            'http://', 'https://', 'rtmp://', 'rtsp://', 'udp://', 'rtp://', 
            'file://', 'pics://', 'mp3://', 'magnet:', 'ed2k://', 'thunder://', 'ftp://',
            'vod://', 'bilibili://', 'youtube://', 'rtmps://', 'rtmpt://', 'hls://',
            'http-live://', 'https-live://', 'tvbus://', 'tvbox://', 'live://', 'novel://', 'text://'
        ]
        if any(u.startswith(p) for p in protocols):
            return True
        
        exts = [
            '.mp4', '.mkv', '.avi', '.rmvb', '.mov', '.wmv', '.flv', 
            '.m3u8', '.ts', '.mp3', '.m4a', '.aac', '.flac', '.wav', 
            '.webm', '.ogg', '.m4v', '.f4v', '.3gp', '.mpg', '.mpeg',
            '.m3u', '.pls', '.asf', '.asx', '.wmx'
        ]
        if any(ext in u for ext in exts):
            return True
        
        patterns = [
            'youtu.be/', 'youtube.com/', 'bilibili.com/', 'iqiyi.com/', 
            'v.qq.com/', 'youku.com/', 'tudou.com/', 'mgtv.com/',
            'sohu.com/', 'acfun.cn/', 'douyin.com/', 'kuaishou.com/',
            'huya.com/', 'douyu.com/', 'twitch.tv/', 'live.'
        ]
        return any(p in u for p in patterns)
    
    # ==================== 彩色图标生成 ====================
    
    def _generate_colored_icon(self, color, text):
        """生成彩色图标框"""
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
            <rect width="200" height="200" rx="40" ry="40" fill="{color}"/>
            <text x="100" y="140" font-size="120" text-anchor="middle" fill="white" font-family="Arial" font-weight="bold">{text}</text>
        </svg>'''
        return f"data:image/svg+xml;base64,{base64.b64encode(svg.encode()).decode()}"
    
    # ==================== JSON文件解析（修复版）====================
    
    def parse_json_file(self, file_path):
        """解析JSON文件，支持各种格式（直播源、视频列表、数据库导出等）"""
        items = []
        try:
            self.log(f"开始解析JSON文件: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(30 * 1024 * 1024)  # 读取30MB以内
            
            # 移除BOM头
            if content.startswith('\ufeff'):
                content = content[1:]
            
            data = json.loads(content)
            
            # ===== 处理不同结构的JSON =====
            
            # 1. 如果是列表，直接处理
            if isinstance(data, list):
                item_list = data
                self.log(f"📋 JSON是数组格式，共 {len(item_list)} 项")
            
            # 2. 如果是字典，尝试提取列表字段
            elif isinstance(data, dict):
                # 检查是否是TVBox格式的VOD数据
                if 'vod_play_url' in data:
                    self.log("📺 检测到TVBox单视频格式")
                    return self._handle_vod_format(data, file_path)
                
                # 检查是否是多线路TVBox格式
                if 'vod_play_from' in data and 'vod_play_url' in data:
                    self.log("📺 检测到TVBox多线路格式")
                    return self._handle_multi_line_vod(data, file_path)
                
                # 常见的列表字段名称
                possible_keys = [
                    'list', 'data', 'items', 'videos', 'vod', 'results', 'rows',
                    'datas', 'data_list', 'video_list', 'movie_list', 'programs',
                    'channels', 'lives', 'live', 'playlist', 'medias', 'files',
                    'play_url', 'urls', 'sources', 'source'
                ]
                
                item_list = None
                for key in possible_keys:
                    if key in data and isinstance(data[key], list):
                        item_list = data[key]
                        self.log(f"🔑 找到键 '{key}'，包含 {len(item_list)} 项")
                        break
                
                # 如果没有找到列表字段，但字典的值都是字典，则将所有值作为列表
                if item_list is None and all(isinstance(v, dict) for v in data.values()):
                    item_list = list(data.values())
                    self.log(f"📚 将字典所有值作为列表，共 {len(item_list)} 项")
                
                # 如果还是没找到，将整个字典作为单一项
                if item_list is None:
                    item_list = [data]
                    self.log("📄 将整个字典作为单个项目处理")
            else:
                self.log(f"⚠️ 未知的JSON类型: {type(data)}")
                return items
            
            # ===== 解析每一项 =====
            for idx, item in enumerate(item_list):
                if not isinstance(item, dict):
                    # 如果项是字符串且是可播放链接，直接添加
                    if isinstance(item, str) and self.is_playable_url(item):
                        items.append({
                            'name': f'链接{idx+1}',
                            'url': item,
                            'pic': '',
                            'remarks': ''
                        })
                    continue
                
                # 提取名称
                name = self._extract_json_field(item, ['name', 'title', 'vod_name', 'video_name', 'show_name', 'channel_name', 'program_name'])
                if not name:
                    name = f"项目{idx+1}"
                
                # 提取URL
                url = self._extract_json_field(item, ['url', 'link', 'play_url', 'video_url', 'vod_url', 'vod_play_url', 'src', 'href', 'm3u8', 'stream', 'address'])
                
                # 如果没有直接URL，检查是否有vod_play_url（可能包含多个节目）
                if not url:
                    play_url_raw = self._extract_json_field(item, ['vod_play_url', 'play_url'])
                    if play_url_raw and ('$' in play_url_raw or '#' in play_url_raw):
                        # 解析多节目
                        episodes = self._parse_multi_episodes(play_url_raw, name)
                        for ep in episodes:
                            ep_item = {
                                'name': ep['name'],
                                'url': ep['url'],
                                'pic': self._extract_json_field(item, ['pic', 'cover', 'image', 'vod_pic', 'thumbnail'], True),
                                'remarks': self._extract_json_field(item, ['remarks', 'vod_remarks', 'note', 'desc', 'description'])
                            }
                            items.append(ep_item)
                        continue
                    elif play_url_raw:
                        url = play_url_raw
                
                # 如果还没找到URL，跳过
                if not url or not self.is_playable_url(url):
                    continue
                
                # 提取图片
                pic = self._extract_json_field(item, ['pic', 'cover', 'image', 'vod_pic', 'thumbnail', 'poster', 'img', 'picture'], True)
                
                # 提取备注
                remarks = self._extract_json_field(item, ['remarks', 'vod_remarks', 'note', 'desc', 'description', 'type', 'category', 'class', 'quality', 'resolution'])
                
                items.append({
                    'name': name,
                    'url': url,
                    'pic': pic,
                    'remarks': remarks
                })
            
            self.log(f"✅ JSON解析完成: {os.path.basename(file_path)}, 共 {len(items)} 条记录")
            
        except json.JSONDecodeError as e:
            self.log(f"❌ JSON解析失败: {e}")
            # 尝试修复常见JSON问题
            try:
                # 尝试去除注释
                content = re.sub(r'//.*?$|/\*.*?\*/', '', content, flags=re.MULTILINE|re.DOTALL)
                data = json.loads(content)
                self.log("✅ 去除注释后解析成功")
                # 重新调用解析逻辑
                return self._parse_json_data(data, file_path)
            except:
                pass
        except Exception as e:
            self.log(f"❌ JSON解析异常: {e}")
            import traceback
            traceback.print_exc()
        
        return items

    def _parse_json_data(self, data, file_path):
        """解析JSON数据（内部调用）"""
        items = []
        if isinstance(data, list):
            item_list = data
        elif isinstance(data, dict):
            if 'vod_play_url' in data:
                return self._handle_vod_format(data, file_path)
            if 'vod_play_from' in data and 'vod_play_url' in data:
                return self._handle_multi_line_vod(data, file_path)
            
            possible_keys = ['list', 'data', 'items', 'videos', 'vod', 'results', 'rows']
            item_list = None
            for key in possible_keys:
                if key in data and isinstance(data[key], list):
                    item_list = data[key]
                    break
            if item_list is None and all(isinstance(v, dict) for v in data.values()):
                item_list = list(data.values())
            else:
                item_list = [data]
        else:
            return items
        
        for idx, item in enumerate(item_list):
            if not isinstance(item, dict):
                if isinstance(item, str) and self.is_playable_url(item):
                    items.append({'name': f'链接{idx+1}', 'url': item})
                continue
            
            name = self._extract_json_field(item, ['name', 'title', 'vod_name'])
            if not name:
                name = f"项目{idx+1}"
            
            url = self._extract_json_field(item, ['play_url', 'vod_play_url', 'url', 'link'])
            if not url or not self.is_playable_url(url):
                play_url_raw = self._extract_json_field(item, ['vod_play_url', 'play_url'])
                if play_url_raw and ('$' in play_url_raw or '#' in play_url_raw):
                    episodes = self._parse_multi_episodes(play_url_raw, name)
                    for ep in episodes:
                        items.append({
                            'name': ep['name'],
                            'url': ep['url'],
                            'pic': self._extract_json_field(item, ['pic', 'cover', 'image', 'vod_pic'], True),
                            'remarks': self._extract_json_field(item, ['remarks', 'vod_remarks', 'note'])
                        })
                continue
            
            pic = self._extract_json_field(item, ['pic', 'cover', 'image', 'vod_pic'], True)
            remarks = self._extract_json_field(item, ['remarks', 'vod_remarks', 'note'])
            
            items.append({'name': name, 'url': url, 'pic': pic, 'remarks': remarks})
        
        return items

    def _handle_vod_format(self, data, file_path):
        """处理TVBox单视频格式"""
        items = []
        name = data.get('vod_name') or data.get('name') or os.path.splitext(os.path.basename(file_path))[0]
        play_url = data.get('vod_play_url', '')
        pic = data.get('vod_pic') or data.get('pic') or ''
        remarks = data.get('vod_remarks', '')
        
        if play_url and ('$' in play_url or '#' in play_url):
            episodes = self._parse_multi_episodes(play_url, name)
            for ep in episodes:
                items.append({
                    'name': ep['name'],
                    'url': ep['url'],
                    'pic': pic,
                    'remarks': remarks
                })
        else:
            items.append({
                'name': name,
                'url': play_url,
                'pic': pic,
                'remarks': remarks
            })
        return items

    def _handle_multi_line_vod(self, data, file_path):
        """处理TVBox多线路格式"""
        items = []
        vod_name = data.get('vod_name') or data.get('name') or os.path.splitext(os.path.basename(file_path))[0]
        vod_pic = data.get('vod_pic') or data.get('pic') or ''
        
        # 处理多线路
        play_from = data.get('vod_play_from', '')
        play_url = data.get('vod_play_url', '')
        
        # 分割线路
        from_list = play_from.split('$$$') if play_from else ['默认线路']
        url_list = play_url.split('$$$') if play_url else ['']
        
        for from_name, url_group in zip(from_list, url_list):
            if url_group and ('$' in url_group or '#' in url_group):
                episodes = self._parse_multi_episodes(url_group, f"{vod_name}[{from_name}]")
                for ep in episodes:
                    items.append({
                        'name': ep['name'],
                        'url': ep['url'],
                        'pic': vod_pic,
                        'remarks': f'线路:{from_name}'
                    })
        
        return items

    def _parse_multi_episodes(self, play_url_raw, base_name):
        """解析多节目源（支持$和#分隔）"""
        episodes = []
        
        # 先按$$$分组（不同线路组）
        groups = play_url_raw.split('$$$')
        for group_idx, group in enumerate(groups):
            if not group:
                continue
            
            # 按#分割（同一线路的不同剧集）
            parts = group.split('#')
            for part_idx, part in enumerate(parts):
                if not part:
                    continue
                
                if '$' in part:
                    # 格式: 名称$URL
                    ep_name, ep_url = part.split('$', 1)
                    episodes.append({
                        'name': ep_name.strip(),
                        'url': ep_url.strip()
                    })
                else:
                    # 只有URL的情况
                    episodes.append({
                        'name': f"{base_name} - 节目{len(episodes)+1}",
                        'url': part.strip()
                    })
        
        return episodes

    def _extract_json_field(self, item, field_names, is_image=False):
        """从JSON对象中提取字段值"""
        for field in field_names:
            if field in item and item[field]:
                value = item[field]
                
                # 处理嵌套字典
                if isinstance(value, dict):
                    # 尝试提取URL
                    for url_field in ['url', 'src', 'path', 'file']:
                        if url_field in value and value[url_field]:
                            return str(value[url_field])
                    # 如果是图片，尝试取第一个非空值
                    if is_image:
                        for img_field in ['large', 'medium', 'small', 'thumb']:
                            if img_field in value and value[img_field]:
                                return str(value[img_field])
                    return str(value)
                
                # 处理列表
                elif isinstance(value, list) and value:
                    if is_image:
                        # 图片列表取第一项
                        first = value[0]
                        if isinstance(first, dict):
                            for url_field in ['url', 'src', 'path']:
                                if url_field in first and first[url_field]:
                                    return str(first[url_field])
                            return str(first)
                        else:
                            return str(first)
                    else:
                        # 其他字段取第一个非空字符串
                        for v in value:
                            if v and isinstance(v, str):
                                return v
                        return str(value[0]) if value else ''
                
                # 普通值
                else:
                    return str(value).strip()
        
        return ''
    
    # ==================== 数据库文件解析 ====================
    
    def parse_db_file(self, file_path):
        return self.db_reader.read_sqlite(file_path, MAX_DB_RESULTS)
    
    # ==================== 逐字歌词支持 ====================
    
    def parse_krc_lyrics(self, krc_data):
        try:
            key = bytearray([64, 71, 97, 100, 50, 45, 48, 51, 55, 56, 53, 51, 51, 51, 50, 52])
            if krc_data.startswith(b'krc1'):
                krc_data = krc_data[4:]
            decoded = bytearray()
            for i, b in enumerate(krc_data):
                decoded.append(b ^ key[i % 16])
            try:
                import zlib
                decompressed = zlib.decompress(decoded[4:])
                text = decompressed.decode('utf-8')
            except:
                text = decoded.decode('utf-8', errors='ignore')
            return self._parse_krc_text(text)
        except Exception as e:
            self.log(f"KRC解析失败: {e}")
            return None

    def _parse_krc_text(self, text):
        lines = text.split('\n')
        metadata = {}
        word_lyrics = []
        lrc_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith('[ar:') or line.startswith('[ti:') or line.startswith('[al:') or line.startswith('[by:'):
                metadata[line[1:3]] = line[4:-1]
                lrc_lines.append(line)
                continue
            match = re.match(r'\[(\d+),(\d+)\](.*)', line)
            if match:
                line_start = int(match.group(1))
                line_end = int(match.group(2))
                content = match.group(3)
                words = []
                for w_match in re.finditer(r'<(\d+),(\d+),([^>]*)>', content):
                    word_start = int(w_match.group(1))
                    word_duration = int(w_match.group(2))
                    word_text = w_match.group(3)
                    words.append({
                        'start': line_start + word_start,
                        'end': line_start + word_start + word_duration,
                        'text': word_text
                    })
                word_line = {
                    'start': line_start,
                    'end': line_end,
                    'words': words,
                    'text': ''.join([w['text'] for w in words])
                }
                word_lyrics.append(word_line)
                minutes = line_start // 60000
                seconds = (line_start % 60000) // 1000
                milliseconds = (line_start % 1000) // 10
                lrc_lines.append(f"[{minutes:02d}:{seconds:02d}.{milliseconds:02d}] {word_line['text']}")
        
        return {'metadata': metadata, 'word_lyrics': word_lyrics, 'lrc_text': '\n'.join(lrc_lines)}

    def read_word_lyrics_file(self, file_path):
        ext = self.get_file_ext(file_path)
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            if ext == 'krc':
                return self.parse_krc_lyrics(data)
            return None
        except Exception as e:
            self.log(f"读取逐字歌词文件失败: {e}")
            return None
    
    def _is_valid_lyrics(self, text):
        if not text or len(text) < 20:
            return False
        markers = ['[ti:', '[ar:', '[al:', '[by:', '[00:', '[01:', '[02:', '作词', '作曲', '编曲', '演唱', '歌词']
        if any(m in text for m in markers):
            return True
        if re.search(r'\[\d{2}:\d{2}\.\d{2,}\]', text):
            return True
        chinese = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        return chinese > 10 and len(text) > 100
    
    def decode_lyrics_data(self, data):
        if not data:
            return None
        encodings = [('utf-8', 'UTF-8'), ('gbk', 'GBK'), ('gb18030', 'GB18030'), ('gb2312', 'GB2312'), ('big5', 'Big5'), ('utf-16', 'UTF-16')]
        all_attempts = []
        for enc, name in encodings:
            try:
                decoded = data.decode(enc)
                if self._is_valid_lyrics(decoded):
                    print(f"✅ 使用 {name} 解码成功")
                    return decoded
                all_attempts.append((len(decoded), decoded))
            except:
                continue
        if all_attempts:
            best = max(all_attempts, key=lambda x: x[0])
            print(f"⚠️ 使用备选解码，长度: {best[0]}")
            return best[1]
        try:
            forced = data.decode('utf-8', errors='ignore')
            if len(forced) > 50:
                print(f"⚠️ 使用强制 UTF-8 解码")
                return forced
        except:
            pass
        return None
    
    def read_lrc_file(self, lrc_path):
        try:
            with open(lrc_path, 'rb') as f:
                data = f.read()
            return self.decode_lyrics_data(data)
        except Exception as e:
            print(f"读取歌词文件失败: {e}")
            return None
    
    def find_local_lrc(self, audio_path):
        audio_dir = os.path.dirname(audio_path)
        audio_name = os.path.splitext(os.path.basename(audio_path))[0]
        try:
            for name in os.listdir(audio_dir):
                if name.startswith('.'):
                    continue
                full_path = os.path.join(audio_dir, name)
                if not os.path.isfile(full_path):
                    continue
                ext = self.get_file_ext(name)
                if not self.is_lrc_file(ext):
                    continue
                lrc_name = os.path.splitext(name)[0]
                if lrc_name == audio_name or lrc_name.lower() == audio_name.lower():
                    print(f"✅ 找到本地歌词: {name} (格式: {ext})")
                    return full_path, ext
        except:
            pass
        return None, None
    
    def clean_filename(self, filename):
        name = os.path.splitext(filename)[0]
        patterns = [
            r'【.*?】', r'\[.*?\]', r'\(.*?\)', r'\{.*?\}', r'（.*?）',
            r'\-? ?\d{3,4}kbps', r'\-? ?\d{3,4}Kbps', r'\-? ?\d{3,4}K',
            r'\-? ?\d{3,4}MB', r'\-? ?\d{3,4}Mb', r'\-? ?HQ', r'\-? ?SQ',
            r'\-? ?无损', r'\-? ?高品质', r'\-? ?高音质',
            r'\-? ?320k', r'\-? ?128k', r'\-? ?192k',
            r'\-? ?歌词版', r'\-? ?伴奏版', r'\-? ?纯音乐',
            r'\-? ?Live', r'\-? ?现场版', r'\-? ?演唱会',
        ]
        for pattern in patterns:
            name = re.sub(pattern, '', name)
        name = re.sub(r'\s+', ' ', name).strip()
        return name
    
    def extract_song_info(self, filename):
        name = self.clean_filename(filename)
        artist = ""
        song = name
        separators = [r'\s+-\s+', r'-\s+', r'\s+-', r'·', r'•', r'–', r'—', r'：', r':', r'、', r'／', r'/']
        for sep in separators:
            parts = re.split(sep, name, maxsplit=1)
            if len(parts) == 2:
                left, right = parts[0].strip(), parts[1].strip()
                left_is_artist = 1 < len(left) < 30
                right_is_artist = 1 < len(right) < 30
                if left_is_artist and not right_is_artist:
                    artist, song = left, right
                elif right_is_artist and not left_is_artist:
                    artist, song = right, left
                elif left_is_artist and right_is_artist:
                    artist, song = (left, right) if len(left) < len(right) else (right, left)
                else:
                    artist, song = left, right
                break
        song = re.sub(r'[《》〈〉『』〔〕]', '', song).strip()
        return artist, song
    
    # ==================== 网络歌词获取 ====================
    
    def _qq_search(self, artist, song):
        keyword = f"{artist} {song}".strip()
        if not keyword:
            return None
        try:
            resp = self.session.get(
                "https://c.y.qq.com/soso/fcgi-bin/client_search_cp",
                params={"w": keyword, "format": "json", "p": 1, "n": 5},
                headers={"User-Agent": "Mozilla/5.0", "Referer": "https://y.qq.com/"},
                timeout=8
            )
            if resp.status_code != 200:
                return None
            data = resp.json()
            if data.get('code') != 0 or not data.get('data', {}).get('song', {}).get('list'):
                return None
            for song_item in data['data']['song']['list'][:3]:
                song_mid = song_item.get('songmid')
                if not song_mid:
                    continue
                lrc_resp = self.session.get(
                    "https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg",
                    params={"songmid": song_mid, "format": "json"},
                    headers={"Referer": "https://y.qq.com/portal/player.html"},
                    timeout=5
                )
                match = re.search(r'({.*})', lrc_resp.text)
                if match:
                    lrc_data = json.loads(match.group(1))
                    if lrc_data.get('lyric'):
                        return base64.b64decode(lrc_data['lyric']).decode('utf-8')
        except Exception as e:
            self.log(f"QQ音乐搜索失败: {e}")
        return None
    
    def _netease_search(self, artist, song):
        keyword = f"{artist} {song}".strip()
        if not keyword:
            return None
        try:
            resp = self.session.post(
                "https://music.163.com/api/search/get/web",
                data={"s": keyword, "type": 1, "offset": 0, "limit": 5},
                headers={"User-Agent": "Mozilla/5.0", "Referer": "https://music.163.com/"},
                timeout=8
            )
            if resp.status_code != 200:
                return None
            data = resp.json()
            if data.get('code') != 200 or not data.get('result', {}).get('songs'):
                return None
            for song_item in data['result']['songs'][:3]:
                song_id = song_item.get('id')
                if not song_id:
                    continue
                lrc_resp = self.session.get(
                    "https://music.163.com/api/song/lyric",
                    params={"id": song_id, "lv": 1},
                    timeout=5
                )
                if lrc_resp.status_code == 200:
                    lrc_data = lrc_resp.json()
                    lrc = lrc_data.get('lrc', {}).get('lyric')
                    if lrc and len(lrc) > 50:
                        return lrc
        except Exception as e:
            self.log(f"网易云搜索失败: {e}")
        return None
    
    def _get_online_lyrics(self, artist, song):
        if not artist and not song:
            return None
        cache_key = f"{artist}_{song}"
        if cache_key in self.lrc_cache:
            return self.lrc_cache[cache_key]
        lrc = self._qq_search(artist, song)
        if not lrc and artist:
            lrc = self._qq_search("", song)
        if not lrc:
            lrc = self._netease_search(artist, song)
        if not lrc and artist:
            lrc = self._netease_search("", song)
        if lrc:
            self.lrc_cache[cache_key] = lrc
        return lrc
    
    def extract_mp3_lyrics(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            pos = data.find(b'USLT')
            if pos < 0:
                return None
            pos += 10
            while pos < len(data) and data[pos] != 0:
                pos += 1
            pos += 1
            end = pos
            while end < len(data) and data[end] != 0:
                end += 1
            return self.decode_lyrics_data(data[pos:end])
        except Exception as e:
            self.log(f"MP3提取失败: {e}")
            return None
    
    def extract_flac_lyrics(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            pos = data.find(b'LYRICS')
            if pos < 0:
                pos = data.find(b'DESCRIPTION')
            if pos < 0:
                return None
            while pos < len(data) and data[pos] != 0:
                pos += 1
            pos += 1
            end = pos
            while end < len(data):
                if data[end] == 0 and end + 4 < len(data):
                    if data[end+1:end+5] in [b'LYRI', b'DESC', b'COMM', b'TITL']:
                        break
                end += 1
            return self.decode_lyrics_data(data[pos:end])
        except Exception as e:
            self.log(f"FLAC提取失败: {e}")
            return None
    
    def get_lrc_for_audio(self, file_path):
        filename = os.path.basename(file_path)
        print(f"\n{'='*60}\n🎵 [歌词获取] {filename}\n{'='*60}")
        cache_key = f"audio_{file_path}"
        if cache_key in self.lrc_cache:
            print(f"📦 使用缓存歌词")
            return self.lrc_cache[cache_key]
        
        artist, song = self.extract_song_info(filename)
        print(f"📝 解析: 歌手='{artist}', 歌曲='{song}'")
        
        lrc_info = self.find_local_lrc(file_path)
        if lrc_info[0]:
            lrc_path, lrc_format = lrc_info
            print(f"📁 找到本地歌词: {lrc_path} (格式: {lrc_format})")
            if lrc_format in ['krc', 'qrc', 'yrc', 'trc']:
                word_lyrics = self.read_word_lyrics_file(lrc_path)
                if word_lyrics:
                    result = {'format': lrc_format, 'word_lyrics': word_lyrics.get('word_lyrics', []), 'lrc_text': word_lyrics.get('lrc_text', '')}
                    self.lrc_cache[cache_key] = result
                    return result
            else:
                lrc_content = self.read_lrc_file(lrc_path)
                if lrc_content:
                    result = {'format': 'lrc', 'lrc_text': lrc_content}
                    self.lrc_cache[cache_key] = result
                    return result
        
        online = self._get_online_lyrics(artist, song)
        if online:
            result = {'format': 'lrc', 'lrc_text': online}
            self.lrc_cache[cache_key] = result
            return result
        
        ext = self.get_file_ext(file_path)
        embedded = None
        if ext == 'mp3':
            embedded = self.extract_mp3_lyrics(file_path)
        elif ext == 'flac':
            embedded = self.extract_flac_lyrics(file_path)
        if embedded:
            result = {'format': 'lrc', 'lrc_text': embedded}
            self.lrc_cache[cache_key] = result
            return result
        
        print("❌ 未找到歌词")
        return None
    
    # ==================== 海报获取 ====================
    
    def _get_song_poster(self, artist, song, audio_path=None):
        cache_key = f"{artist}_{song}"
        if cache_key in self.poster_cache:
            return self.poster_cache[cache_key]
        if audio_path:
            local = self._get_local_poster(audio_path)
            if local:
                self.poster_cache[cache_key] = local
                return local
        poster = self._qq_poster(artist, song) or self._netease_poster(artist, song)
        if poster:
            self.poster_cache[cache_key] = poster
        return poster
    
    def _get_local_poster(self, audio_path):
        audio_dir = os.path.dirname(audio_path)
        audio_name = os.path.splitext(os.path.basename(audio_path))[0]
        patterns = [
            f"{audio_name}.jpg", f"{audio_name}.jpeg", f"{audio_name}.png",
            "cover.jpg", "cover.png", "folder.jpg", "folder.png",
            "album.jpg", "album.png", "poster.jpg", "poster.png"
        ]
        try:
            for name in os.listdir(audio_dir):
                if name.startswith('.'):
                    continue
                full_path = os.path.join(audio_dir, name)
                if not os.path.isfile(full_path):
                    continue
                lower_name = name.lower()
                if lower_name in patterns:
                    return f"file://{full_path}"
                keywords = ['cover', 'folder', 'album', 'poster', 'artwork']
                if any(k in lower_name for k in keywords):
                    return f"file://{full_path}"
        except:
            pass
        return None
    
    def _qq_poster(self, artist, song):
        keyword = f"{artist} {song}".strip()
        if not keyword:
            return None
        try:
            resp = self.session.get(
                "https://c.y.qq.com/soso/fcgi-bin/client_search_cp",
                params={"w": keyword, "format": "json", "p": 1, "n": 3},
                timeout=5
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get('code') == 0 and data.get('data', {}).get('song', {}).get('list'):
                    album_mid = data['data']['song']['list'][0].get('albummid')
                    if album_mid:
                        return f"https://y.gtimg.cn/music/photo_new/T002R300x300M000{album_mid}.jpg"
        except:
            pass
        return None
    
    def _netease_poster(self, artist, song):
        keyword = f"{artist} {song}".strip()
        if not keyword:
            return None
        try:
            resp = self.session.post(
                "https://music.163.com/api/search/get/web",
                data={"s": keyword, "type": 1, "offset": 0, "limit": 3},
                timeout=5
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get('code') == 200 and data.get('result', {}).get('songs'):
                    album = data['result']['songs'][0].get('album')
                    if album and album.get('picUrl'):
                        return album['picUrl']
        except:
            pass
        return None
    
    # ==================== 在线直播 ====================
    
    def _fetch_with_auto_headers(self, url):
        domain = self._get_domain_from_url(url)
        self.log(f"获取直播源: {domain}")
        
        if domain in self.domain_specific_headers:
            for headers_info in self.domain_specific_headers[domain]:
                try:
                    resp = self.session.get(url, headers=headers_info['headers'], timeout=15)
                    if resp.status_code == 200:
                        return resp.text
                except:
                    continue
        
        for headers_info in self.common_headers_list:
            try:
                resp = self.session.get(url, headers=headers_info['headers'], timeout=10)
                if resp.status_code == 200:
                    return resp.text
            except:
                continue
        
        return None
    
    def _get_domain_from_url(self, url):
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            return domain.split(':')[0] if ':' in domain else domain
        except:
            return ""
    
    def _get_live_programs(self, source):
        source_id = source['id']
        current_time = time.time()
        
        if source_id in self.live_cache and current_time - self.live_cache_time.get(source_id, 0) < self.live_cache_duration:
            return self.live_cache[source_id]
        
        content = self._fetch_with_auto_headers(source['url'])
        if not content:
            return []
        
        programs = self._parse_live_content(content, source)
        
        if programs:
            self.live_cache[source_id] = programs
            self.live_cache_time[source_id] = current_time
        
        return programs
    
    def _parse_live_content(self, content, source):
        if source.get('type') == 'txt' or ',#genre#' in content:
            return self._parse_txt_live(content)
        elif content.strip().startswith(('{', '[')):
            return self._parse_json_live(content)
        else:
            return self._parse_m3u_live(content)
    
    def _parse_m3u_live(self, content):
        programs = []
        lines = content.split('\n')
        current_name = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith('#EXTINF:'):
                name_match = re.search(r',(.+)$', line) or re.search(r'tvg-name="([^"]+)"', line)
                current_name = name_match.group(1).strip() if name_match else None
            elif line and not line.startswith('#') and current_name:
                if self.is_playable_url(line):
                    programs.append({'name': current_name, 'url': line})
                current_name = None
        return programs
    
    def _parse_txt_live(self, content):
        programs = []
        lines = content.split('\n')
        current_cat = None
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if ',#genre#' in line:
                current_cat = line.split(',')[0].strip()
                continue
            if ',' in line:
                parts = line.split(',', 1)
                name = parts[0].strip()
                url = parts[1].strip()
                if self.is_playable_url(url):
                    display_name = f"[{current_cat}] {name}" if current_cat else name
                    programs.append({'name': display_name, 'url': url})
        return programs
    
    def _parse_json_live(self, content):
        programs = []
        try:
            data = json.loads(content)
            items = []
            if isinstance(data, dict):
                for key in ['list', 'data', 'items', 'videos']:
                    if key in data and isinstance(data[key], list):
                        items = data[key]
                        break
                if not items:
                    items = [data]
            else:
                items = data
            for item in items:
                if isinstance(item, dict):
                    name = item.get('name') or item.get('title')
                    url = item.get('url') or item.get('play_url')
                    if name and url and self.is_playable_url(url):
                        programs.append({'name': name, 'url': url})
        except:
            pass
        return programs
    
    # ==================== 首页和分类 ====================
    
    def homeContent(self, filter):
        classes = []
        
        for i, path in enumerate(self.root_paths):
            if os.path.exists(path):
                name = self.path_to_chinese.get(path, os.path.basename(path.rstrip('/')) or f'目录{i}')
                classes.append({"type_id": f"root_{i}", "type_name": name})
        
        classes.append({"type_id": "recent", "type_name": "最近添加"})
        classes.append({"type_id": self.live_category_id, "type_name": self.live_category_name})
        
        return {'class': classes}
    
    def categoryContent(self, tid, pg, filter, extend):
        pg = int(pg)
        
        if tid == self.live_category_id:
            return self._live_category_content(pg)
        
        if tid == 'recent':
            return self._recent_content(pg)
        
        path = self._resolve_path(tid)
        if not path or not os.path.exists(path) or not os.path.isdir(path):
            return {'list': [], 'page': pg, 'pagecount': 1}
        
        files = self.scan_directory(path)
        total = len(files)
        
        per_page = 50
        start = (pg - 1) * per_page
        end = min(start + per_page, total)
        page_files = files[start:end]
        
        vlist = []
        
        # 返回上一级
        parent_item = self._create_parent_item(path)
        if parent_item:
            vlist.append(parent_item)
        
        # 文件列表
        for f in page_files:
            item = self._create_file_item(f)
            if item:
                vlist.append(item)
        
        return {
            'list': vlist,
            'page': pg,
            'pagecount': (total + per_page - 1) // per_page,
            'limit': per_page,
            'total': total
        }
    
    def _resolve_path(self, tid):
        if tid.startswith('root_'):
            try:
                idx = int(tid[5:])
                return self.root_paths[idx] if idx < len(self.root_paths) else None
            except:
                return None
        elif tid.startswith(self.FOLDER_PREFIX):
            return self.b64u_decode(tid[len(self.FOLDER_PREFIX):])
        return tid if os.path.exists(tid) else None
    
    def _create_parent_item(self, current_path):
        parent = os.path.dirname(current_path)
        
        for root in self.root_paths:
            if os.path.normpath(current_path) == os.path.normpath(root.rstrip('/')):
                return None
        
        if not parent or parent == current_path:
            return None
        
        for i, root in enumerate(self.root_paths):
            if os.path.normpath(parent) == os.path.normpath(root.rstrip('/')):
                parent_id = f"root_{i}"
                parent_name = self.path_to_chinese.get(root, os.path.basename(parent))
                break
        else:
            parent_id = self.FOLDER_PREFIX + self.b64u_encode(parent)
            parent_name = os.path.basename(parent)
        
        return {
            'vod_id': parent_id,
            'vod_name': f'⬅️ 返回 {parent_name}',
            'vod_pic': self.file_icons['folder'],
            'vod_remarks': '',
            'vod_tag': 'folder',
            'style': {'type': 'list'}
        }
    
    # ==================== 文件项创建（优化TXT直播源识别，修复HEIC图片识别）====================
    
    def _create_file_item(self, f):
        icon = self.get_file_icon(f['ext'], f['is_dir'])
        
        # 1. 文件夹
        if f['is_dir']:
            return {
                'vod_id': self.FOLDER_PREFIX + self.b64u_encode(f['path']),
                'vod_name': f"{icon} {f['name']}",
                'vod_pic': self.file_icons['folder'],
                'vod_remarks': '文件夹',
                'vod_tag': 'folder',
                'style': {'type': 'list'}
            }
        
        # 2. 图片文件（包括HEIC/HEIF格式）- 放在最前面优先识别
        if self.is_image_file(f['ext']) or f['ext'].lower() in ['heic', 'heif']:
            return {
                'vod_id': f['path'],
                'vod_name': f"📷 {f['name']}",
                'vod_pic': f"file://{f['path']}",
                'vod_play_url': f"查看${self.PICS_PREFIX}file://{f['path']}",
                'vod_remarks': '照片' if f['ext'].lower() in ['heic', 'heif'] else '照片',
                'vod_tag': 'image',
                'style': {'type': 'grid', 'ratio': 1},
                'vod_player': '画'  # 设置为 "画"，表示图片浏览模式
            }
        
        # 3. 音频文件
        if self.is_audio_file(f['ext']):
            return {
                'vod_id': f['path'],
                'vod_name': f"🎵 {f['name']}",
                'vod_pic': self.file_icons['audio'],
                'vod_play_url': f"播放${self.MP3_PREFIX + f['path']}",
                'vod_remarks': '音频',
                'vod_tag': 'audio',
                'style': {'type': 'list'},
                'vod_player': '听'
            }
        
        # 4. 视频文件
        if self.is_media_file(f['ext']):
            return {
                'vod_id': f['path'],
                'vod_name': f"🎬 {f['name']}",
                'vod_pic': self.file_icons['video'],
                'vod_remarks': '视频',
                'vod_tag': 'video',
                'style': {'type': 'list'}
            }
        
        # 5. M3U/M3U8直播源文件
        if f['ext'] in ['m3u', 'm3u8']:
            colors = ["#FF6B6B", "#4ECDC4", "#FFD93D", "#6BCB77", "#9D65C9", "#FF8C42", "#A2D729", "#FF6B8B", "#45B7D1", "#96CEB4"]
            color = colors[hash(f['name']) % len(colors)]
            first_char = f['name'][0].upper() if f['name'] else "M"
            icon_svg = self._generate_colored_icon(color, first_char)
            
            return {
                'vod_id': self.LIST_PREFIX + self.b64u_encode(f['path']),
                'vod_name': f['name'],
                'vod_pic': icon_svg,
                'vod_play_url': f"播放${self.LIST_PREFIX + self.b64u_encode(f['path'])}",
                'vod_remarks': '直播源',
                'vod_tag': 'live_m3u',
                'style': {'type': 'list'}
            }
        
        # 6. 数据库文件
        if self.is_db_file(f['ext']):
            return {
                'vod_id': self.LIST_PREFIX + self.b64u_encode(f['path']),
                'vod_name': f"🗄️ {f['name']}",
                'vod_pic': self.file_icons['database'],
                'vod_remarks': '数据库',
                'vod_tag': 'database',
                'style': {'type': 'list'}
            }
        
        # 7. 磁力链接文件
        if self.is_magnet_file(f['ext']):
            return {
                'vod_id': self.MAGNET_PREFIX + self.b64u_encode(f['path']),
                'vod_name': f"🧲 {f['name']}",
                'vod_pic': self.file_icons['magnet'],
                'vod_remarks': '磁力链接',
                'vod_tag': 'magnet',
                'style': {'type': 'list'}
            }
        
        # 8. 歌词文件
        if self.is_lrc_file(f['ext']):
            return {
                'vod_id': f['path'],
                'vod_name': f"📝 {f['name']}",
                'vod_pic': self.file_icons['lrc'],
                'vod_remarks': '歌词',
                'vod_tag': 'lrc',
                'style': {'type': 'list'}
            }
        
        # 9. JSON文件
        if f['ext'] == 'json':
            return {
                'vod_id': self.LIST_PREFIX + self.b64u_encode(f['path']),
                'vod_name': f"📋 {f['name']}",
                'vod_pic': self.file_icons['list'],
                'vod_remarks': 'JSON数据',
                'vod_tag': 'json',
                'style': {'type': 'list'}
            }
        
        # 10. TXT文件 - 优化直播源判断逻辑
        if f['ext'] == 'txt':
            # 读取文件内容判断是否为直播源
            is_live_source = False
            url_count = 0
            
            try:
                with open(f['path'], 'r', encoding='utf-8', errors='ignore') as ff:
                    # 读取整个文件内容
                    content = ff.read(2048)  # 读取前2KB判断
                    
                    # 检测直播源特征
                    if ',#genre#' in content.lower():
                        is_live_source = True
                    else:
                        # 按行处理
                        lines = content.split('\n')
                        for line in lines[:30]:
                            line = line.strip()
                            line_lower = line.lower()
                            
                            # 检测 "名称,URL" 格式（逗号分隔，且第二部分是URL）
                            if ',' in line:
                                parts = line.split(',', 1)
                                if len(parts) == 2:
                                    url = parts[1].strip()
                                    # 检查URL格式
                                    if url.startswith(('http://', 'https://')):
                                        # 进一步验证是否是视频流地址
                                        if any(ext in url.lower() for ext in ['.m3u8', '.mp4', '.flv', '.ts']):
                                            url_count += 1
                                        elif re.match(r'https?://[\d.]+:\d+', url):
                                            url_count += 1
                            
                            # 检测直接URL（没有逗号分隔）
                            elif self.is_playable_url(line):
                                # 检查是否是视频流地址
                                if any(ext in line_lower for ext in ['.m3u8', '.mp4', '.flv', '.ts']):
                                    url_count += 1
                            
                            # 如果已经找到足够链接，提前结束
                            if url_count >= 3:  # 有3个以上链接就肯定是直播源
                                break
            except Exception as e:
                self.log(f"读取TXT文件失败: {e}")
            
            # 判断逻辑：如果找到至少3个有效的视频流URL，就当作直播源
            if is_live_source or url_count >= 3:
                # 直播源TXT - 使用 LIST_PREFIX
                colors = ["#FF6B6B", "#4ECDC4", "#FFD93D", "#6BCB77", "#9D65C9", "#FF8C42", "#A2D729", "#FF6B8B", "#45B7D1", "#96CEB4"]
                color = colors[hash(f['name']) % len(colors)]
                first_char = f['name'][0].upper() if f['name'] else "T"
                icon_svg = self._generate_colored_icon(color, first_char)
                
                return {
                    'vod_id': self.LIST_PREFIX + self.b64u_encode(f['path']),
                    'vod_name': f['name'],
                    'vod_pic': icon_svg,
                    'vod_play_url': f"播放${self.LIST_PREFIX + self.b64u_encode(f['path'])}",
                    'vod_remarks': f'直播源 ({url_count}个链接)',
                    'vod_tag': 'live_txt',
                    'style': {'type': 'list'}
                }
            else:
                # 没有找到任何视频链接的TXT文件才当作小说
                encoded = self.b64u_encode(f['path'])
                novel_url = f"{self.NOVEL_PREFIX}{encoded}"
                return {
                    'vod_id': novel_url,
                    'vod_name': f"📄 {f['name']}",
                    'vod_pic': self.file_icons['text'],
                    'vod_play_url': f"阅读${novel_url}",
                    'vod_remarks': '文本',
                    'vod_tag': 'text',
                    'style': {'type': 'list'},
                    'vod_player': '书'
                }
        
        # 11. 其他已知格式
        if f['ext'] in ['xml', 'html', 'htm', 'css', 'js', 'py', 'sh']:
            return {
                'vod_id': self.TEXT_PREFIX + self.b64u_encode(f['path']),
                'vod_name': f"📄 {f['name']}",
                'vod_pic': self.file_icons['text'],
                'vod_remarks': '代码文件',
                'vod_tag': 'code',
                'style': {'type': 'list'}
            }
        
        # 12. 未知类型
        if f['ext']:
            return {
                'vod_id': f['path'],
                'vod_name': f"📁 {f['name']}",
                'vod_pic': self.file_icons['file'],
                'vod_remarks': f'{f["ext"].upper()}文件',
                'vod_tag': 'unknown',
                'style': {'type': 'list'}
            }
        else:
            return {
                'vod_id': f['path'],
                'vod_name': f"📁 {f['name']}",
                'vod_pic': self.file_icons['file'],
                'vod_remarks': '无扩展名',
                'vod_tag': 'unknown',
                'style': {'type': 'list'}
            }
    
    def _live_category_content(self, pg):
        vlist = []
        
        for idx, source in enumerate(self.online_live_sources):
            programs = self._get_live_programs(source)
            color = source.get('color', self.default_colors[idx % len(self.default_colors)])
            first_char = source['name'][0] if source['name'] else "直"
            icon = self._generate_colored_icon(color, first_char)
            
            remarks = source.get('remarks', '')
            if programs:
                remarks += f" {len(programs)}个节目"
            else:
                remarks += " 加载失败"
            
            vlist.append({
                'vod_id': self.LIVE_PREFIX + self.b64u_encode(source['id']),
                'vod_name': source['name'],
                'vod_pic': icon,
                'vod_remarks': remarks,
                'vod_tag': 'live_source',
                'style': {'type': 'list'},
                'type': 'live'
            })
        
        return {
            'list': vlist,
            'page': pg,
            'pagecount': 1,
            'limit': len(vlist),
            'total': len(vlist)
        }
    
    def _recent_content(self, pg):
        all_files = []
        
        for path in self.root_paths:
            if os.path.exists(path):
                self._scan_recent_files(path, all_files)
        
        all_files.sort(key=lambda x: x['mtime'], reverse=True)
        all_files = all_files[:200]
        
        per_page = 50
        start = (pg - 1) * per_page
        end = min(start + per_page, len(all_files))
        
        vlist = []
        for f in all_files[start:end]:
            item = self._create_recent_item(f)
            if item:
                vlist.append(item)
        
        return {
            'list': vlist,
            'page': pg,
            'pagecount': (len(all_files) + per_page - 1) // per_page,
            'limit': per_page,
            'total': len(all_files)
        }
    
    def _scan_recent_files(self, path, file_list, depth=0, max_depth=2):
        if depth > max_depth:
            return
        
        try:
            for name in os.listdir(path):
                if name.startswith('.'):
                    continue
                
                full_path = os.path.join(path, name)
                
                if os.path.isdir(full_path):
                    self._scan_recent_files(full_path, file_list, depth + 1, max_depth)
                else:
                    ext = self.get_file_ext(name)
                    if (self.is_media_file(ext) or self.is_audio_file(ext) or 
                        self.is_image_file(ext) or self.is_list_file(ext) or
                        self.is_db_file(ext) or self.is_magnet_file(ext) or
                        ext == 'txt'):
                        
                        mtime = os.path.getmtime(full_path)
                        if time.time() - mtime < 7 * 24 * 3600:
                            file_list.append({
                                'name': name,
                                'path': full_path,
                                'ext': ext,
                                'mtime': mtime,
                            })
        except:
            pass
    
    def _create_recent_item(self, f):
        icon = self.get_file_icon(f['ext'], False)
        
        # 图片文件 - 添加 vod_player 字段，值为 "画"（包括HEIC/HEIF）
        if self.is_image_file(f['ext']) or f['ext'].lower() in ['heic', 'heif']:
            return {
                'vod_id': self.URL_B64U_PREFIX + self.b64u_encode(self.PICS_PREFIX + "file://" + f['path']),
                'vod_name': f"📷 {f['name']}",
                'vod_pic': f"file://{f['path']}",
                'vod_play_url': f"查看${self.PICS_PREFIX}file://{f['path']}",
                'vod_remarks': self._format_time(f['mtime']),
                'style': {'type': 'grid', 'ratio': 1},
                'vod_player': '画'
            }
        
        # 音频文件
        if self.is_audio_file(f['ext']):
            return {
                'vod_id': self.URL_B64U_PREFIX + self.b64u_encode(self.MP3_PREFIX + f['path']),
                'vod_name': f"🎵 {f['name']}",
                'vod_pic': self.file_icons['audio'],
                'vod_play_url': f"播放${self.MP3_PREFIX + f['path']}",
                'vod_remarks': self._format_time(f['mtime']),
                'style': {'type': 'grid', 'ratio': 1},
                'vod_player': '听'
            }
        
        if self.is_media_file(f['ext']):
            return {
                'vod_id': f['path'],
                'vod_name': f"🎬 {f['name']}",
                'vod_pic': self.file_icons['video'],
                'vod_remarks': self._format_time(f['mtime']),
                'style': {'type': 'grid', 'ratio': 1}
            }
        
        # 直播源文件 (m3u/m3u8)
        if f['ext'] in ['m3u', 'm3u8']:
            colors = ["#FF6B6B", "#4ECDC4", "#FFD93D", "#6BCB77", "#9D65C9", "#FF8C42", "#A2D729", "#FF6B8B", "#45B7D1", "#96CEB4"]
            color = colors[hash(f['name']) % len(colors)]
            first_char = f['name'][0].upper() if f['name'] else "M"
            icon_svg = self._generate_colored_icon(color, first_char)
            return {
                'vod_id': self.LIST_PREFIX + self.b64u_encode(f['path']),
                'vod_name': f['name'],
                'vod_pic': icon_svg,
                'vod_remarks': self._format_time(f['mtime']),
                'style': {'type': 'grid', 'ratio': 1}
            }
        
        if self.is_db_file(f['ext']):
            return {
                'vod_id': self.LIST_PREFIX + self.b64u_encode(f['path']),
                'vod_name': f"🗄️ {f['name']}",
                'vod_pic': self.file_icons['database'],
                'vod_remarks': self._format_time(f['mtime']),
                'style': {'type': 'grid', 'ratio': 1}
            }
        
        if self.is_magnet_file(f['ext']):
            return {
                'vod_id': self.MAGNET_PREFIX + self.b64u_encode(f['path']),
                'vod_name': f"🧲 {f['name']}",
                'vod_pic': self.file_icons['magnet'],
                'vod_remarks': self._format_time(f['mtime']),
                'style': {'type': 'grid', 'ratio': 1}
            }
        
        if self.is_lrc_file(f['ext']):
            return {
                'vod_id': f['path'],
                'vod_name': f"📝 {f['name']}",
                'vod_pic': self.file_icons['lrc'],
                'vod_remarks': self._format_time(f['mtime']),
                'style': {'type': 'grid', 'ratio': 1}
            }
        
        # JSON文件
        if f['ext'] == 'json':
            return {
                'vod_id': self.LIST_PREFIX + self.b64u_encode(f['path']),
                'vod_name': f"📋 {f['name']}",
                'vod_pic': self.file_icons['list'],
                'vod_remarks': self._format_time(f['mtime']),
                'style': {'type': 'grid', 'ratio': 1}
            }
        
        # TXT文件 - 优化直播源判断逻辑
        if f['ext'] == 'txt':
            # 判断是否为直播源
            is_live = False
            url_count = 0
            try:
                with open(f['path'], 'r', encoding='utf-8', errors='ignore') as ff:
                    content = ff.read(2048)
                    
                    if ',#genre#' in content.lower():
                        is_live = True
                    else:
                        lines = content.split('\n')
                        for line in lines[:30]:
                            line = line.strip()
                            line_lower = line.lower()
                            
                            # 检测 "名称,URL" 格式
                            if ',' in line:
                                parts = line.split(',', 1)
                                if len(parts) == 2:
                                    url = parts[1].strip()
                                    if url.startswith(('http://', 'https://')):
                                        if any(ext in url.lower() for ext in ['.m3u8', '.mp4', '.flv', '.ts']):
                                            url_count += 1
                                        elif re.match(r'https?://[\d.]+:\d+', url):
                                            url_count += 1
                            
                            # 检测直接URL
                            elif self.is_playable_url(line):
                                if any(ext in line_lower for ext in ['.m3u8', '.mp4', '.flv', '.ts']):
                                    url_count += 1
                            
                            if url_count >= 3 or is_live:
                                break
            except:
                pass
            
            if is_live or url_count >= 3:
                # 直播源 - 用 LIST_PREFIX
                colors = ["#FF6B6B", "#4ECDC4", "#FFD93D", "#6BCB77", "#9D65C9", "#FF8C42", "#A2D729", "#FF6B8B", "#45B7D1", "#96CEB4"]
                color = colors[hash(f['name']) % len(colors)]
                first_char = f['name'][0].upper() if f['name'] else "T"
                icon_svg = self._generate_colored_icon(color, first_char)
                return {
                    'vod_id': self.LIST_PREFIX + self.b64u_encode(f['path']),
                    'vod_name': f['name'],
                    'vod_pic': icon_svg,
                    'vod_remarks': self._format_time(f['mtime']),
                    'style': {'type': 'grid', 'ratio': 1}
                }
            else:
                # 其他所有TXT - 用 NOVEL_PREFIX
                encoded = self.b64u_encode(f['path'])
                novel_url = f"{self.NOVEL_PREFIX}{encoded}"
                return {
                    'vod_id': novel_url,
                    'vod_name': f"📄 {f['name']}",
                    'vod_pic': self.file_icons['text'],
                    'vod_remarks': self._format_time(f['mtime']),
                    'style': {'type': 'grid', 'ratio': 1},
                    'vod_player': '书'
                }
        
        # 其他已知格式
        if f['ext'] in ['xml', 'html', 'htm', 'css', 'js', 'py', 'sh']:
            return {
                'vod_id': self.TEXT_PREFIX + self.b64u_encode(f['path']),
                'vod_name': f"📄 {f['name']}",
                'vod_pic': self.file_icons['text'],
                'vod_remarks': self._format_time(f['mtime']),
                'style': {'type': 'grid', 'ratio': 1}
            }
        
        # 未知类型
        return {
            'vod_id': f['path'],
            'vod_name': f"📁 {f['name']}",
            'vod_pic': self.file_icons['file'],
            'vod_remarks': self._format_time(f['mtime']),
            'style': {'type': 'grid', 'ratio': 1}
        }
    
    def _format_time(self, timestamp):
        diff = time.time() - timestamp
        if diff < 3600:
            return f"{int(diff/60)}分钟前"
        elif diff < 86400:
            return f"{int(diff/3600)}小时前"
        else:
            return time.strftime('%m-%d %H:%M', time.localtime(timestamp))
    
    # ==================== 详情页 ====================
    
    def detailContent(self, ids):
        id_val = ids[0]
        self.log(f"详情页请求: {id_val}")
        
        # 处理各种协议
        if id_val.startswith(self.LIVE_PREFIX):
            source_id = self.b64u_decode(id_val[len(self.LIVE_PREFIX):])
            return self._live_source_detail(source_id)
        
        # 小说协议 - 添加 vod_player 字段
        if id_val.startswith(self.NOVEL_PREFIX):
            encoded = id_val[len(self.NOVEL_PREFIX):]
            file_path = self.b64u_decode(encoded)
            self.novel_path_cache[encoded] = file_path
            vod_data = self._handle_novel_detail(file_path, id_val, encoded)
            # 为小说详情添加 vod_player 字段
            if vod_data and "list" in vod_data and len(vod_data["list"]) > 0:
                vod_data["list"][0]["vod_player"] = "书"
            return vod_data
        
        # 文本协议 - 添加 vod_player 字段
        if id_val.startswith(self.TEXT_PREFIX):
            encoded = id_val[len(self.TEXT_PREFIX):]
            file_path = self.b64u_decode(encoded)
            vod_data = self._handle_text_detail(file_path, id_val)
            # 为文本详情添加 vod_player 字段
            if vod_data and "list" in vod_data and len(vod_data["list"]) > 0:
                vod_data["list"][0]["vod_player"] = "书"
            return vod_data
        
        if id_val.startswith(self.FOLDER_PREFIX):
            folder_path = self.b64u_decode(id_val[len(self.FOLDER_PREFIX):])
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                return self.categoryContent(folder_path, 1, None, None)
            return {'list': []}
        
        # 图片连播协议 - 添加 vod_player 字段
        if id_val.startswith(self.PICS_PREFIX + 'slideshow/'):
            dir_path = self.b64u_decode(id_val[len(self.PICS_PREFIX + 'slideshow/'):])
            images = self.collect_images_in_dir(dir_path)
            if not images:
                return {'list': []}
            
            pic_urls = [f"file://{img['path']}" for img in images]
            vod = {
                'vod_id': id_val,
                'vod_name': f"📷 图片连播 - {os.path.basename(dir_path)} ({len(images)}张)",
                'vod_pic': self.file_icons['image_playlist'],
                'vod_play_from': '图片浏览',
                'vod_play_url': f"浏览${self.PICS_PREFIX + '&&'.join(pic_urls)}",
                'style': {'type': 'list'},
                'vod_player': '画'
            }
            return {'list': [vod]}
        
        if id_val.startswith(self.URL_B64U_PREFIX):
            decoded = self.b64u_decode(id_val[len(self.URL_B64U_PREFIX):])
            if decoded and decoded.startswith(self.PICS_PREFIX):
                return self._handle_pics_detail(decoded, id_val)
        
        if id_val.startswith(self.CAMERA_ALL_PREFIX):
            dir_path = self.b64u_decode(id_val[len(self.CAMERA_ALL_PREFIX):])
            images = self.collect_images_in_dir(dir_path)
            if not images:
                return {'list': []}
            
            pic_urls = [f"file://{img['path']}" for img in images]
            vod = {
                'vod_id': id_val,
                'vod_name': f"📷 相机照片 ({len(images)}张)",
                'vod_pic': self.file_icons['image_playlist'],
                'vod_play_from': '照片查看',
                'vod_play_url': f"浏览${self.PICS_PREFIX + '&&'.join(pic_urls)}",
                'style': {'type': 'list'},
                'vod_player': '画'
            }
            return {'list': [vod]}
        
        if id_val.startswith(self.MAGNET_PREFIX):
            file_path = self.b64u_decode(id_val[len(self.MAGNET_PREFIX):])
            return self._handle_magnet_detail(file_path, id_val)
        
        if id_val.startswith(self.LIST_PREFIX):
            file_path = self.b64u_decode(id_val[len(self.LIST_PREFIX):])
            return self._handle_list_detail(file_path, id_val)
        
        if id_val.startswith(self.A_ALL_PREFIX):
            dir_path = self.b64u_decode(id_val[len(self.A_ALL_PREFIX):])
            return self._handle_audio_all_detail(dir_path, id_val)
        
        if id_val.startswith(self.V_ALL_PREFIX):
            dir_path = self.b64u_decode(id_val[len(self.V_ALL_PREFIX):])
            return self._handle_video_all_detail(dir_path, id_val)
        
        # 普通文件或目录
        if not os.path.exists(id_val):
            return {'list': []}
        
        if os.path.isdir(id_val):
            return self.categoryContent(id_val, 1, None, None)
        
        return self._handle_file_detail(id_val)
    
    def _handle_pics_detail(self, decoded, id_val):
        pics_data = decoded[len(self.PICS_PREFIX):]
        
        if '&&' in pics_data:
            pic_urls = pics_data.split('&&')
            return {'list': [{
                'vod_id': id_val,
                'vod_name': f'图片相册 ({len(pic_urls)}张)',
                'vod_pic': pic_urls[0],
                'vod_play_from': '图片查看',
                'vod_play_url': f"浏览${self.PICS_PREFIX + '&&'.join(pic_urls)}",
                'style': {'type': 'list'},
                'vod_player': '画'
            }]}
        else:
            file_name = os.path.basename(pics_data.split('?')[0])
            if pics_data.startswith('file://'):
                file_name = os.path.basename(pics_data[7:])
            
            return {'list': [{
                'vod_id': id_val,
                'vod_name': file_name,
                'vod_pic': pics_data,
                'vod_play_from': '图片查看',
                'vod_play_url': f"查看${self.PICS_PREFIX + pics_data}",
                'style': {'type': 'list'},
                'vod_player': '画'
            }]}
    
    def _handle_magnet_detail(self, file_path, vod_id):
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return {'list': []}
        
        items = self._parse_magnet_file(file_path)
        
        if not items:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    magnet = re.search(r'(magnet:\?[^\s\'"<>]+)', content)
                    if magnet:
                        return {'list': [{
                            'vod_id': vod_id,
                            'vod_name': os.path.basename(file_path),
                            'vod_pic': self.file_icons['magnet'],
                            'vod_play_from': '磁力链接',
                            'vod_play_url': f"{os.path.splitext(os.path.basename(file_path))[0]}${magnet.group(1)}",
                            'style': {'type': 'list'}
                        }]}
            except:
                pass
            
            return {'list': [{
                'vod_id': vod_id,
                'vod_name': os.path.basename(file_path),
                'vod_pic': self.file_icons['magnet'],
                'vod_play_from': '磁力链接',
                'vod_play_url': f"打开文件$file://{file_path}",
                'style': {'type': 'list'}
            }]}
        
        play_urls = [f"{item['name']}${item['url']}" for item in items if item.get('url', '').startswith('magnet:')]
        
        return {'list': [{
            'vod_id': vod_id,
            'vod_name': os.path.basename(file_path),
            'vod_pic': self.file_icons['magnet'],
            'vod_play_from': '磁力链接列表',
            'vod_play_url': '#'.join(play_urls) if play_urls else f"打开文件$file://{file_path}",
            'style': {'type': 'list'}
        }]}
    
    def _parse_magnet_file(self, file_path):
        items = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            magnet_pattern = re.compile(r'(magnet:\?[^\s\'"<>]+)', re.I)
            lines = content.split('\n')
            
            for line in lines[:5000]:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if ',' in line:
                    parts = line.split(',', 1)
                    name = parts[0].strip()
                    magnet = magnet_pattern.search(parts[1])
                    if magnet:
                        items.append({'name': name, 'url': magnet.group(1)})
                else:
                    magnet = magnet_pattern.search(line)
                    if magnet:
                        name = f"磁力{len(items)+1}"
                        items.append({'name': name, 'url': magnet.group(1)})
        except:
            pass
        
        return items
    
    def _handle_list_detail(self, file_path, vod_id):
        """处理列表文件详情页 - 修复显示多条的问题"""
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return {'list': []}
        
        ext = self.get_file_ext(file_path)
        self.log(f"处理列表文件: {file_path}, 类型: {ext}")
        
        items = []
        
        # 处理JSON文件
        if ext == 'json':
            items = self.parse_json_file(file_path)
            self.log(f"JSON解析到 {len(items)} 条记录")
        
        # 处理数据库文件
        elif self.is_db_file(ext):
            items = self.parse_db_file(file_path)
            self.log(f"数据库解析到 {len(items)} 条记录")
        
        # 处理M3U文件 - 直播源
        elif ext in ['m3u', 'm3u8']:
            items = self._parse_m3u_file(file_path)
            self.log(f"M3U解析到 {len(items)} 条记录")
            
            # 如果是直播源（有大量频道），使用线路在上、电视台在下的格式
            if len(items) > 5:  # 判断为直播源
                return self._format_live_source(items, file_path, vod_id, ext)
        
        # 处理TXT文件 - 可能是直播源或小说
        elif ext == 'txt':
            # 先判断是否为直播源
            is_live_source = False
            url_count = 0
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(2048)  # 读取前2KB判断
                    
                    # 检测直播源特征
                    if ',#genre#' in content.lower():
                        is_live_source = True
                    else:
                        lines = content.split('\n')
                        for line in lines[:30]:
                            line = line.strip()
                            if ',' in line:
                                parts = line.split(',', 1)
                                if len(parts) == 2:
                                    url = parts[1].strip()
                                    if self.is_playable_url(url):
                                        if any(ext in url.lower() for ext in ['.m3u8', '.mp4', '.flv', '.ts']):
                                            url_count += 1
                                        elif re.match(r'https?://[\d.]+:\d+', url):
                                            url_count += 1
                            elif self.is_playable_url(line):
                                if any(ext in line.lower() for ext in ['.m3u8', '.mp4', '.flv', '.ts']):
                                    url_count += 1
            except:
                pass
            
            # 如果是直播源
            if is_live_source or url_count >= 3:  # 有3个以上视频链接就是直播源
                items = self._parse_txt_file(file_path)
                self.log(f"TXT直播源解析到 {len(items)} 条记录")
                return self._format_live_source(items, file_path, vod_id, ext)
            else:
                # 普通TXT文件，作为小说处理
                items = self._parse_txt_file(file_path)
                self.log(f"TXT小说解析到 {len(items)} 条记录")
        
        # 如果没有解析到任何项目
        if not items:
            self.log(f"⚠️ 未解析到任何项目，使用默认播放")
            name = os.path.splitext(os.path.basename(file_path))[0]
            return {'list': [self._create_fallback_vod(file_path, 'list', vod_id, name)]}
        
        # 构建播放URL - 确保所有项目都被正确格式化
        play_urls = self._build_play_urls(items)
        
        if not play_urls:
            return {'list': [self._create_fallback_vod(file_path, 'list', vod_id, os.path.splitext(os.path.basename(file_path))[0])]}
        
        # 获取第一个项目的图片作为封面
        pic = items[0].get('pic', '') if items else ''
        if not pic:
            pic = self.file_icons['list']
        
        # 使用'#'连接所有URL，确保格式正确：名称1$URL1#名称2$URL2
        play_url_str = '#'.join(play_urls)
        
        self.log(f"最终播放URL长度: {len(play_url_str)} 字符")
        self.log(f"预览: {play_url_str[:200]}...")
        
        return {'list': [{
            'vod_id': vod_id,
            'vod_name': os.path.basename(file_path),
            'vod_pic': pic,
            'vod_play_from': '播放列表',
            'vod_play_url': play_url_str,
            'vod_remarks': f'共{len(items)}条',
            'style': {'type': 'list'}
        }]}
    
    def _format_live_source(self, items, file_path, vod_id, ext):
        """将直播源格式化为线路在上、电视台在下的格式"""
        self.log(f"格式化直播源: {os.path.basename(file_path)}")
        
        # 按频道名称分组
        channels = {}
        for item in items:
            name = item.get('name', '').strip()
            url = item.get('url', '')
            
            if not name or not url:
                continue
            
            # 清理频道名称
            clean_name = re.sub(r'^\[[^\]]+\]\s*', '', name)
            clean_name = re.sub(r'\s*[\[\(（]\s*\d+\s*[\]\)）]\s*$', '', clean_name)
            clean_name = re.sub(r'\s*[线|L|l]ine?\s*\d+$', '', clean_name, flags=re.I)
            clean_name = clean_name.strip()
            
            if clean_name not in channels:
                channels[clean_name] = []
            channels[clean_name].append({'name': name, 'url': url})
        
        if not channels:
            # 如果没有分组成功，使用原始items
            play_urls = self._build_play_urls(items)
            pic = items[0].get('pic', '') if items else self.file_icons['list']
            return {'list': [{
                'vod_id': vod_id,
                'vod_name': os.path.basename(file_path),
                'vod_pic': pic,
                'vod_play_from': '播放列表',
                'vod_play_url': '#'.join(play_urls),
                'vod_remarks': f'共{len(items)}条',
                'style': {'type': 'list'}
            }]}
        
        # 找出最大线路数
        max_lines = 0
        for links in channels.values():
            max_lines = max(max_lines, len(links))
        
        # 构建线路在上、电视台在下的格式
        from_list = []  # 线路名称列表（显示在上面）
        url_list = []   # 对应的URL列表（每个线路对应的所有电视台，显示在下面）
        
        # 为每条线路创建一个组
        for line_idx in range(max_lines):
            line_name = f"线路{line_idx + 1}"
            from_list.append(line_name)
            
            # 收集这条线路对应的所有电视台
            channel_urls = []
            for channel_name, links in channels.items():
                if line_idx < len(links):
                    # 这条线路有这个频道
                    channel_urls.append(f"{channel_name}${links[line_idx]['url']}")
                # 没有该线路的频道跳过
            
            # 所有电视台用#连接
            url_list.append('#'.join(channel_urls))
        
        # 生成彩色图标
        colors = ["#FF6B6B", "#4ECDC4", "#FFD93D", "#6BCB77", "#9D65C9", "#FF8C42", "#A2D729", "#FF6B8B", "#45B7D1", "#96CEB4"]
        color = colors[hash(os.path.basename(file_path)) % len(colors)]
        first_char = os.path.basename(file_path)[0].upper() if os.path.basename(file_path) else "L"
        icon_svg = self._generate_colored_icon(color, first_char)
        
        # 获取当前日期作为更新时间
        current_date = time.strftime('%Y.%m.%d', time.localtime())
        
        vod = {
            'vod_id': vod_id,
            'vod_name': os.path.basename(file_path),
            'vod_pic': icon_svg,
            'vod_play_from': '$$$'.join(from_list),  # 线路名称（显示在上面）
            'vod_play_url': '$$$'.join(url_list),     # 电视台列表（显示在下面）
            'vod_remarks': f'更新时间{current_date}',
            'vod_content': f'共 {len(channels)} 个频道，{sum(len(v) for v in channels.values())} 条节目线路',
            'style': {'type': 'list'},
            'type': 'live',
            'vod_type': 4,
            'vod_class': 'live',
            'vod_style': {'type': 'live'},
            'playerType': 2
        }
        
        return {'list': [vod]}
    
    def _parse_m3u_file(self, file_path):
        items = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            current_name = None
            for line in lines[:10000]:
                line = line.strip()
                if line.startswith('#EXTINF:'):
                    name_match = re.search(r',(.+)$', line) or re.search(r'tvg-name="([^"]+)"', line)
                    current_name = name_match.group(1).strip() if name_match else None
                elif line and not line.startswith('#'):
                    if self.is_playable_url(line):
                        items.append({
                            'name': current_name or f"线路{len(items)+1}",
                            'url': line
                        })
                    current_name = None
        except:
            pass
        return items
    
    def _parse_txt_file(self, file_path):
        """解析TXT文件，支持名称,URL格式和纯URL格式"""
        items = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 处理换行被截断的情况
            # 合并被换行分割的URL
            lines = []
            current_line = ""
            for line in content.split('\n'):
                line = line.strip()
                if not line:
                    if current_line:
                        lines.append(current_line)
                        current_line = ""
                    continue
                
                # 如果当前行以http开头，且上一行有内容但没有http开头，说明可能是换行分割的URL
                if line.startswith(('http://', 'https://')) and current_line and not current_line.startswith(('http://', 'https://')):
                    # 合并
                    current_line = current_line + line
                elif current_line:
                    lines.append(current_line)
                    current_line = line
                else:
                    current_line = line
            
            if current_line:
                lines.append(current_line)
            
            # 解析每一行
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if ',' in line:
                    parts = line.split(',', 1)
                    name = parts[0].strip()
                    url = parts[1].strip()
                    if self.is_playable_url(url):
                        # 检查URL是否包含多个$$$，如果是则只取第一个
                        if '$$$' in url:
                            url = url.split('$$$')[0]
                        items.append({'name': name, 'url': url})
                elif self.is_playable_url(line):
                    # 纯URL，使用文件名或序号作为名称
                    url = line
                    if '$$$' in url:
                        url = url.split('$$$')[0]
                    name = f"节目{len(items)+1}"
                    items.append({'name': name, 'url': url})
        except Exception as e:
            self.log(f"解析TXT文件失败: {e}")
        
        return items
    
    def _handle_novel_detail(self, file_path, vod_id, encoded):
        """处理小说详情"""
        if not os.path.isfile(file_path):
            return {'list': []}
        
        cache_key = f"chapters_{encoded}"
        if cache_key in self.novel_chapters_cache:
            chapters = self.novel_chapters_cache[cache_key]
        else:
            chapters = NovelParser.parse_txt_novel(file_path)
            self.novel_chapters_cache[cache_key] = chapters
        
        self.current_novel = {'encoded_path': encoded, 'file_path': file_path, 'chapters': chapters}
        
        urls = []
        for i, c in enumerate(chapters):
            title = c['title']
            if title and len(title) > 2 and not title.strip().isdigit():
                urls.append(f"{title}$chapter{i}")
        
        return {'list': [{
            'vod_id': vod_id,
            'vod_name': os.path.basename(file_path),
            'vod_pic': self.file_icons['novel'],
            'vod_play_from': '小说章节',
            'vod_play_url': '#'.join(urls),
            'vod_remarks': f'共{len(chapters)}章',
            'style': {'type': 'list'}
        }]}
    
    def _handle_text_detail(self, file_path, vod_id):
        """处理普通文本文件详情"""
        if not os.path.isfile(file_path):
            return {'list': []}
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            return {'list': [{
                'vod_id': vod_id,
                'vod_name': os.path.basename(file_path),
                'vod_pic': self.file_icons['text'],
                'vod_play_from': '文本阅读',
                'vod_play_url': f"阅读${vod_id}",
                'vod_content': content[:5000],  # 预览内容
                'vod_remarks': f'共{len(content)}字',
                'style': {'type': 'list'}
            }]}
        except Exception as e:
            self.log(f"读取文本失败: {e}")
            return {'list': []}
    
    def _create_fallback_vod(self, file_path, file_type, vod_id, name=None):
        return {
            'vod_id': vod_id,
            'vod_name': os.path.basename(file_path),
            'vod_pic': self.file_icons[file_type],
            'vod_play_from': file_type,
            'vod_play_url': f"{name or os.path.splitext(os.path.basename(file_path))[0]}$file://{file_path}",
            'style': {'type': 'list'}
        }
    
    def _build_play_urls(self, items):
        """构建播放URL列表，确保正确格式：名称$URL（不能有多余的$）"""
        play_urls = []
        for item in items:
            url = item.get('url') or item.get('play_url', '')
            if url:
                # 确保名称不为空
                name = item.get('name', '').strip()
                if not name:
                    name = f"节目{len(play_urls)+1}"
                
                # 移除名称中的特殊字符
                name = re.sub(r'[#$]', '', name)
                
                # 处理URL中可能包含的$$$（多线路格式）
                if '$$$' in url:
                    # 如果是多线路，只取第一个可用的URL
                    first_url = url.split('$$$')[0]
                    # 检查第一个URL是否还包含$（线路标识）
                    if '$' in first_url:
                        # 如果包含$，说明是 线路名$URL 格式，需要提取真正的URL
                        url_parts = first_url.split('$', 1)
                        if len(url_parts) == 2:
                            # 使用第二个部分作为URL
                            play_urls.append(f"{name}${url_parts[1]}")
                        else:
                            play_urls.append(f"{name}${first_url}")
                    else:
                        play_urls.append(f"{name}${first_url}")
                else:
                    # 正常格式：直接使用
                    play_urls.append(f"{name}${url}")
        
        # 调试输出
        self.log(f"构建了 {len(play_urls)} 个播放URL")
        if play_urls:
            self.log(f"第一个: {play_urls[0][:100]}")
            if len(play_urls) > 1:
                self.log(f"最后一个: {play_urls[-1][:100]}")
        
        return play_urls
    
    def _handle_audio_all_detail(self, dir_path, vod_id):
        """音频播放列表详情页"""
        audios = self.collect_audios_in_dir(dir_path)
        
        if not audios:
            return {'list': []}
        
        play_urls = [f"{os.path.splitext(a['name'])[0] or '未知歌曲'}${self.MP3_PREFIX + a['path']}" for a in audios]
        
        poster = self.file_icons['audio_playlist']
        if audios:
            artist, song = self.extract_song_info(audios[0]['name'])
            fetched = self._get_song_poster(artist, song, audios[0]['path'])
            if fetched:
                poster = fetched
        
        return {'list': [{
            'vod_id': vod_id,
            'vod_name': f"🎵 音频播放列表 - {os.path.basename(dir_path)} ({len(audios)}首)",
            'vod_pic': poster,
            'vod_play_from': '本地音乐',
            'vod_play_url': '#'.join(play_urls),
            'vod_remarks': f'共{len(audios)}首歌曲',
            'style': {'type': 'list'},
            'vod_player': '听'
        }]}
    
    def _handle_video_all_detail(self, dir_path, vod_id):
        """视频播放列表详情页"""
        videos = self.collect_videos_in_dir(dir_path)
        
        if not videos:
            return {'list': []}
        
        play_urls = [f"{os.path.splitext(v['name'])[0]}$file://{v['path']}" for v in videos]
        
        return {'list': [{
            'vod_id': vod_id,
            'vod_name': f"🎬 视频播放列表 - {os.path.basename(dir_path)} ({len(videos)}集)",
            'vod_pic': self.file_icons['video_playlist'],
            'vod_play_from': '本地视频',
            'vod_play_url': '#'.join(play_urls),
            'vod_remarks': f'共{len(videos)}集',
            'style': {'type': 'list'}
        }]}
    
    def _handle_file_detail(self, file_path):
        name = os.path.basename(file_path)
        ext = self.get_file_ext(name)
        
        vod = {
            'vod_id': file_path,
            'vod_name': name,
            'vod_play_from': '本地播放',
            'vod_play_url': '',
            'style': {'type': 'list'}
        }
        
        # 图片文件 - 添加 vod_player 字段，值为 "画"（包括HEIC/HEIF）
        if self.is_image_file(ext) or ext.lower() in ['heic', 'heif']:
            # 获取同目录下所有图片文件
            dir_path = os.path.dirname(file_path)
            all_images = self.collect_images_in_dir(dir_path)
            
            if len(all_images) > 1:
                # 找到点击的图片在列表中的位置
                clicked_index = -1
                for i, img in enumerate(all_images):
                    if img['path'] == file_path:
                        clicked_index = i
                        break
                
                # 重新排列播放列表：点击的图片 -> 后面的图片 -> 前面的图片
                reordered_images = []
                if clicked_index >= 0:
                    # 先添加点击的图片及其后面的图片
                    for i in range(clicked_index, len(all_images)):
                        reordered_images.append(all_images[i])
                    # 再添加点击的图片前面的图片
                    for i in range(0, clicked_index):
                        reordered_images.append(all_images[i])
                else:
                    reordered_images = all_images
                
                # 创建图片连播URL
                pic_urls = []
                for img in reordered_images:
                    pic_urls.append(f"file://{img['path']}")
                
                vod.update({
                    'vod_play_url': f"浏览${self.PICS_PREFIX + '&&'.join(pic_urls)}",
                    'vod_name': f"📷 {name} (当前目录 {len(all_images)}张)",
                    'vod_pic': f"file://{file_path}",
                    'vod_play_from': '图片浏览',
                    'vod_remarks': f'共{len(all_images)}张照片，循环播放',
                    'vod_player': '画'
                })
            else:
                # 如果只有一张图片，直接查看
                vod.update({
                    'vod_play_url': f"查看${self.PICS_PREFIX}file://{file_path}",
                    'vod_pic': f"file://{file_path}",
                    'vod_name': f"🖼️ {name}",
                    'vod_player': '画'
                })
        elif self.is_audio_file(ext):
            # 获取同目录下所有音频文件
            dir_path = os.path.dirname(file_path)
            all_audios = self.collect_audios_in_dir(dir_path)
            
            if len(all_audios) > 1:
                # 找到点击的歌曲在列表中的位置
                clicked_index = -1
                for i, audio in enumerate(all_audios):
                    if audio['path'] == file_path:
                        clicked_index = i
                        break
                
                # 重新排列播放列表：点击的歌曲 -> 后面的歌曲 -> 前面的歌曲
                reordered_audios = []
                if clicked_index >= 0:
                    # 先添加点击的歌曲及其后面的歌曲
                    for i in range(clicked_index, len(all_audios)):
                        reordered_audios.append(all_audios[i])
                    # 再添加点击的歌曲前面的歌曲
                    for i in range(0, clicked_index):
                        reordered_audios.append(all_audios[i])
                else:
                    reordered_audios = all_audios
                
                # 创建播放列表URL
                play_urls = []
                for audio in reordered_audios:
                    audio_name = os.path.splitext(audio['name'])[0]
                    play_urls.append(f"{audio_name}${self.MP3_PREFIX + audio['path']}")
                
                # 使用当前点击的歌曲的封面作为列表封面
                artist, song = self.extract_song_info(name)
                poster = self._get_song_poster(artist, song, file_path)
                if not poster:
                    poster = self.file_icons['audio_playlist']
                
                vod.update({
                    'vod_play_url': '#'.join(play_urls),
                    'vod_name': f"🎵 {name} (当前目录 {len(all_audios)}首)",
                    'vod_pic': poster,
                    'vod_play_from': '本地音乐',
                    'vod_remarks': f'共{len(all_audios)}首歌曲，循环播放',
                    'vod_player': '听'
                })
            else:
                # 如果只有一个音频文件，直接播放
                vod.update({
                    'vod_play_url': f"{os.path.splitext(name)[0]}${self.MP3_PREFIX + file_path}",
                    'vod_name': f"🎵 {name}",
                    'vod_pic': self.file_icons['audio'],
                    'vod_player': '听'
                })
                
                artist, song = self.extract_song_info(name)
                poster = self._get_song_poster(artist, song, file_path)
                if poster:
                    vod['vod_pic'] = poster
                    
        elif self.is_media_file(ext):
            # 获取同目录下所有视频文件
            dir_path = os.path.dirname(file_path)
            all_videos = self.collect_videos_in_dir(dir_path)
            
            if len(all_videos) > 1:
                # 找到点击的视频在列表中的位置
                clicked_index = -1
                for i, video in enumerate(all_videos):
                    if video['path'] == file_path:
                        clicked_index = i
                        break
                
                # 重新排列播放列表：点击的视频 -> 后面的视频 -> 前面的视频
                reordered_videos = []
                if clicked_index >= 0:
                    # 先添加点击的视频及其后面的视频
                    for i in range(clicked_index, len(all_videos)):
                        reordered_videos.append(all_videos[i])
                    # 再添加点击的视频前面的视频
                    for i in range(0, clicked_index):
                        reordered_videos.append(all_videos[i])
                else:
                    reordered_videos = all_videos
                
                play_urls = []
                for video in reordered_videos:
                    video_name = os.path.splitext(video['name'])[0]
                    play_urls.append(f"{video_name}$file://{video['path']}")
                
                vod.update({
                    'vod_play_url': '#'.join(play_urls),
                    'vod_name': f"🎬 {name} (当前目录 {len(all_videos)}集)",
                    'vod_pic': self.file_icons['video_playlist'],
                    'vod_play_from': '本地视频',
                    'vod_remarks': f'共{len(all_videos)}集，循环播放'
                })
            else:
                # 如果只有一个视频文件，直接播放
                vod.update({
                    'vod_play_url': f"{os.path.splitext(name)[0]}$file://{file_path}",
                    'vod_name': f"🎬 {name}",
                    'vod_pic': self.file_icons['video']
                })
        elif self.is_list_file(ext) or self.is_db_file(ext) or self.is_magnet_file(ext):
            prefix = self.MAGNET_PREFIX if self.is_magnet_file(ext) else self.LIST_PREFIX
            return self.detailContent([prefix + self.b64u_encode(file_path)])
        elif ext == 'txt':
            # 判断是否为直播源
            preview = ''
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    preview = f.read(2048)  # 读取更多内容判断
            except:
                pass
            
            is_live = False
            url_count = 0
            
            if preview:
                # 检测直播源特征
                if ',#genre#' in preview.lower():
                    is_live = True
                else:
                    lines = preview.split('\n')
                    for line in lines[:20]:
                        line = line.strip()
                        # 检测 "名称,URL" 格式
                        if ',' in line:
                            parts = line.split(',', 1)
                            if len(parts) == 2:
                                url = parts[1].strip()
                                if url.startswith(('http://', 'https://')):
                                    if any(ext in url.lower() for ext in ['.m3u8', '.mp4', '.flv', '.ts']):
                                        url_count += 1
                                    elif re.match(r'https?://[\d.]+:\d+', url):
                                        url_count += 1
                        # 检测纯URL
                        elif line.startswith(('http://', 'https://')):
                            if any(ext in line.lower() for ext in ['.m3u8', '.mp4', '.flv', '.ts']):
                                url_count += 1
                            elif re.match(r'https?://[\d.]+:\d+', line):
                                url_count += 1
                        
                        if url_count >= 3 or is_live:
                            break
            
            if is_live or url_count >= 3:
                return self.detailContent([self.LIST_PREFIX + self.b64u_encode(file_path)])
            else:
                # 普通文本文件 - 用小说阅读器
                vod_data = self.detailContent([self.NOVEL_PREFIX + self.b64u_encode(file_path)])
                # 为文本文件添加 vod_player 字段
                if vod_data and "list" in vod_data and len(vod_data["list"]) > 0:
                    vod_data["list"][0]["vod_player"] = "书"
                return vod_data
        
        return {'list': [vod]}
    
    def _live_source_detail(self, source_id):
        """直播源详情页 - 线路在上，电视台在下"""
        source = next((s for s in self.online_live_sources if s['id'] == source_id), None)
        if not source:
            return {'list': []}
        
        idx = self.online_live_sources.index(source)
        color = source.get('color', self.default_colors[idx % len(self.default_colors)])
        first_char = source['name'][0] if source['name'] else "直"
        icon = self._generate_colored_icon(color, first_char)
        
        programs = self._get_live_programs(source)
        if not programs:
            return {'list': [{
                'vod_id': self.LIVE_PREFIX + self.b64u_encode(source_id),
                'vod_name': source['name'],
                'vod_pic': icon,
                'vod_play_from': '直播源',
                'vod_play_url': '提示$无法获取直播源，请稍后重试',
                'vod_content': f"直播源: {source['url']}\n状态: 获取失败",
                'style': {'type': 'list'},
                'type': 'live',
                'vod_type': 4,
                'vod_class': 'live',
                'vod_style': {'type': 'live'},
                'playerType': source.get('playerType', 2)
            }]}
        
        # 按频道分组
        channels = {}
        for p in programs:
            name = p['name']
            # 清理频道名称
            clean_name = re.sub(r'^\[[^\]]+\]\s*', '', name)
            clean_name = re.sub(r'\s*[\[\(（]\s*\d+\s*[\]\)）]\s*$', '', clean_name)
            
            if clean_name not in channels:
                channels[clean_name] = []
            channels[clean_name].append(p)
        
        # 找出最大线路数
        max_lines = 0
        for links in channels.values():
            max_lines = max(max_lines, len(links))
        
        # 构建数据 - 线路在上，电视台在下
        from_list = []  # 线路名称列表（显示在上面）
        url_list = []   # 对应的URL列表（每个线路对应的所有电视台，显示在下面）
        
        # 为每条线路创建一个组
        for line_idx in range(max_lines):
            line_name = f"线路{line_idx + 1}"
            from_list.append(line_name)
            
            # 收集这条线路对应的所有电视台
            channel_urls = []
            for channel_name, links in channels.items():
                if line_idx < len(links):
                    # 这条线路有这个频道
                    channel_urls.append(f"{channel_name}${links[line_idx]['url']}")
                # 没有该线路的频道跳过
            
            # 所有电视台用#连接
            url_list.append('#'.join(channel_urls))
        
        # 获取当前日期作为更新时间
        current_date = time.strftime('%Y.%m.%d', time.localtime())
        
        vod = {
            'vod_id': self.LIVE_PREFIX + self.b64u_encode(source_id),
            'vod_name': source['name'],
            'vod_pic': icon,
            'vod_play_from': '$$$'.join(from_list),  # 线路名称（显示在上面）
            'vod_play_url': '$$$'.join(url_list),     # 电视台列表（显示在下面）
            'vod_remarks': f'更新时间{current_date}',
            'vod_content': f"共 {len(channels)} 个频道，{sum(len(v) for v in channels.values())} 条节目线路",
            'vod_style': {
                'type': 'live'
            },
            'vod_type': 4,
            'vod_class': 'live',
            'type': 'live',
            'style': {
                'type': 'live'
            },
            'playerType': source.get('playerType', 2)
        }
        
        return {'list': [vod]}
    
    # ==================== 播放页 ====================

    def playerContent(self, flag, id, vipFlags):
        self.log(f"播放请求: flag={flag}, id={id}")
        
        # 处理pics协议 - 添加 vod_player 字段
        if id.startswith(self.PICS_PREFIX):
            return {
                "parse": 0, 
                "playUrl": "", 
                "url": id, 
                "header": {},
                "vod_player": "画"
            }
        
        # 处理文本协议 - 添加 vod_player 字段
        if id.startswith(self.TEXT_PREFIX):
            encoded = id[len(self.TEXT_PREFIX):]
            file_path = self.b64u_decode(encoded)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                data = {"title": os.path.basename(file_path), "content": content}
                return {
                    "parse": 0,
                    "playUrl": "",
                    "url": self.TEXT_PREFIX + json.dumps(data, ensure_ascii=False),
                    "header": "",
                    "content": content,
                    "vod_player": "书"
                }
            except Exception as e:
                self.log(f"读取文本失败: {str(e)}")
                return {"parse": 0, "playUrl": "", "url": "", "header": ""}
        
        # 处理mp3协议
        if id.startswith(self.MP3_PREFIX):
            return self._handle_mp3_play(id)
        
        # 处理小说协议 - 添加 vod_player 字段
        if id.startswith(self.NOVEL_PREFIX):
            full_id = id[len(self.NOVEL_PREFIX):]
            
            chapter_index = 0
            encoded_path = full_id
            
            if '#chapter' in full_id:
                parts = full_id.split('#chapter', 1)
                encoded_path = parts[0]
                try:
                    chapter_index = int(parts[1])
                except (ValueError, IndexError):
                    chapter_index = 0
            
            if encoded_path in self.novel_path_cache:
                file_path = self.novel_path_cache[encoded_path]
            else:
                file_path = self.b64u_decode(encoded_path)
                self.novel_path_cache[encoded_path] = file_path
            
            try:
                cache_key = f"chapters_{encoded_path}"
                if cache_key in self.novel_chapters_cache:
                    chapters = self.novel_chapters_cache[cache_key]
                else:
                    chapters = NovelParser.parse_txt_novel(file_path)
                    self.novel_chapters_cache[cache_key] = chapters
                
                if chapters and 0 <= chapter_index < len(chapters):
                    title = chapters[chapter_index]['title']
                    content = chapters[chapter_index]['content']
                else:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    title = os.path.basename(file_path)
                
                data = {"title": title, "content": content}
                return {
                    "parse": 0,
                    "playUrl": "",
                    "url": "novel://" + json.dumps(data, ensure_ascii=False),
                    "header": "",
                    "content": content,
                    "vod_player": "书"
                }
            except Exception as e:
                self.log(f"读取小说失败: {str(e)}")
                return {"parse": 0, "playUrl": "", "url": "", "header": ""}
        
        # 处理chapterX格式的请求
        if id.startswith('chapter') and flag == '小说章节' and self.current_novel['chapters']:
            try:
                idx = int(id.replace('chapter', ''))
                if 0 <= idx < len(self.current_novel['chapters']):
                    c = self.current_novel['chapters'][idx]
                    data = {"title": c['title'], "content": c['content']}
                    return {
                        "parse": 0, 
                        "playUrl": "", 
                        "url": "novel://" + json.dumps(data, ensure_ascii=False), 
                        "header": "",
                        "vod_player": "书"
                    }
            except:
                pass
        
        # 提取真实URL
        url = id
        if '$' in url:
            parts = url.split('$', 1)
            if len(parts) == 2:
                url = parts[1]
        
        if url.startswith(('http://', 'https://', 'file://')):
            pass
        else:
            try:
                decoded = base64.b64decode(url).decode('utf-8')
                if decoded.startswith(('http://', 'https://', 'file://')):
                    url = decoded
            except:
                pass
        
        # 处理dytt分享链接
        if 'dytt-' in url and '/share/' in url and not url.endswith('.m3u8'):
            real_url = self._extract_real_m3u8_url(url)
            if real_url:
                url = real_url
        
        # 构建请求头
        headers = self._build_headers(flag, url)
        
        result = {
            "parse": 0,
            "playUrl": "",
            "url": url,
            "header": headers
        }
        
        # 音频文件处理
        if url.startswith('file://'):
            file_path = url[7:]
            if os.path.exists(file_path) and self.is_audio_file(self.get_file_ext(file_path)):
                self._add_audio_info(result, file_path)
                result["vod_player"] = "听"
        
        # 图片文件处理（包括HEIC/HEIF）
        if url.startswith('file://'):
            ext = self.get_file_ext(url[7:])
            if self.is_image_file(ext) or ext.lower() in ['heic', 'heif']:
                result["vod_player"] = "画"
        
        self.log(f"播放器返回: {result}")
        return result

    def _handle_mp3_play(self, id):
        file_path = id.replace(self.MP3_PREFIX, '')
        
        if not os.path.exists(file_path) and not file_path.startswith('/storage/'):
            test_path = '/storage/emulated/0/' + file_path.lstrip('/')
            if os.path.exists(test_path):
                file_path = test_path
        
        result = {
            "parse": 0,
            "playUrl": "",
            "url": 'http://127.0.0.1:9978/file' + file_path,
            "header": {},
            "vod_player": "听"
        }
        
        if os.path.exists(file_path) and self.is_audio_file(self.get_file_ext(file_path)):
            self._add_audio_info(result, file_path)
        
        return result

    def _add_audio_info(self, result, file_path):
        filename = os.path.basename(file_path)
        artist, song = self.extract_song_info(filename)
        
        poster = self._get_song_poster(artist, song, file_path)
        if poster:
            result["poster"] = poster
        
        lyrics = self.get_lrc_for_audio(file_path)
        if lyrics:
            if isinstance(lyrics, dict):
                if lyrics.get('lrc_text'):
                    result["lrc"] = lyrics['lrc_text']
                if lyrics.get('word_lyrics'):
                    result["word_lyrics"] = lyrics['word_lyrics']
                    result["lyrics_format"] = lyrics.get('format', 'lrc')
            else:
                result["lrc"] = lyrics

    def _extract_real_m3u8_url(self, page_url):
        if page_url in self.m3u8_cache:
            return self.m3u8_cache[page_url]
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(page_url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": base_url + "/",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            }
            
            response = self.session.get(page_url, headers=headers, timeout=10)
            if response.status_code != 200:
                return None
            
            html = response.text
            
            patterns = [
                r'(https?://[^\s"\']+\.m3u8[^\s"\']*)',
                r'(//[^\s"\']+\.m3u8[^\s"\']*)',
                r'url["\']?\s*[:=]\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
                r'src["\']?\s*[:=]\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                if matches:
                    url = matches[0]
                    if url.startswith('//'):
                        url = 'https:' + url
                    elif url.startswith('/'):
                        url = base_url + url
                    self.m3u8_cache[page_url] = url
                    return url
            
            iframe_pattern = r'<iframe[^>]+src=["\']([^"\']+)["\']'
            iframe_match = re.search(iframe_pattern, html, re.IGNORECASE)
            if iframe_match:
                iframe_url = iframe_match.group(1)
                if iframe_url.startswith('//'):
                    iframe_url = 'https:' + iframe_url
                elif iframe_url.startswith('/'):
                    iframe_url = base_url + iframe_url
                elif not iframe_url.startswith('http'):
                    iframe_url = base_url + '/' + iframe_url.lstrip('/')
                return self._extract_real_m3u8_url(iframe_url)
            
            return None
        except Exception as e:
            self.log(f"提取真实地址失败: {e}")
            return None

    def _build_headers(self, flag, url):
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "*/*"
        }
        
        if flag == 'migu_live':
            headers.update({
                "User-Agent": "com.android.chrome/3.7.0 (Linux;Android 15)",
                "Referer": "https://www.miguvideo.com/"
            })
        elif flag == 'gongdian_live':
            headers.update({
                "Referer": "https://gongdian.top/"
            })
        
        if 't.061899.xyz' in domain:
            headers.update({
                "User-Agent": "okhttp/3.12.11",
                "Referer": "http://t.061899.xyz/"
            })
        elif 'rihou.cc' in domain:
            headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": "https://rihou.cc:555/"
            })
        elif 'miguvideo.com' in domain:
            headers.update({
                "User-Agent": "com.android.chrome/3.7.0 (Linux;Android 15)",
                "Referer": "https://www.miguvideo.com/"
            })
        elif 'gongdian.top' in domain:
            headers.update({
                "Referer": "https://gongdian.top/"
            })
        elif 'dytt-film.com' in domain:
            headers.update({
                "Referer": "https://vip.dytt-film.com/",
                "Origin": "https://vip.dytt-film.com"
            })
        elif domain:
            headers["Referer"] = f"https://{domain}/"
        
        if "Range" in headers and '.m3u8' in url:
            del headers["Range"]
        
        return headers
    
    # ==================== 搜索 ====================
    
    def searchContent(self, key, quick, pg=1):
        pg = int(pg)
        results = []
        
        clean_key = re.sub(r'^[📁📂🎬🎵📷📋📝🗄️🧲📄🖼️🎞️⬅️\s]+', '', key.lower())
        
        for path in self.root_paths:
            if not os.path.exists(path):
                continue
            
            all_files = []
            self._scan_for_search(path, all_files)
            
            for f in all_files:
                if clean_key in f['name'].lower():
                    item = self._create_search_item(f)
                    if item:
                        results.append(item)
        
        results.sort(key=lambda x: (clean_key not in x['vod_name'].lower(), x['vod_name']))
        
        per_page = 50
        start = (pg - 1) * per_page
        end = min(start + per_page, len(results))
        
        return {
            'list': results[start:end],
            'page': pg,
            'pagecount': (len(results) + per_page - 1) // per_page,
            'limit': per_page,
            'total': len(results)
        }
    
    def _scan_for_search(self, path, file_list, depth=0, max_depth=3):
        if depth > max_depth:
            return
        
        try:
            for name in os.listdir(path):
                if name.startswith('.'):
                    continue
                
                full_path = os.path.join(path, name)
                
                if os.path.isdir(full_path):
                    self._scan_for_search(full_path, file_list, depth + 1, max_depth)
                else:
                    file_list.append({
                        'name': name,
                        'path': full_path,
                        'ext': self.get_file_ext(name),
                    })
        except:
            pass
    
    def _create_search_item(self, f):
        # 图片文件（包括HEIC/HEIF）- 放在最前面优先识别
        if self.is_image_file(f['ext']) or f['ext'].lower() in ['heic', 'heif']:
            return {
                'vod_id': self.URL_B64U_PREFIX + self.b64u_encode(self.PICS_PREFIX + "file://" + f['path']),
                'vod_name': f"📷 {f['name']}",
                'vod_pic': f"file://{f['path']}",
                'vod_play_url': f"查看${self.PICS_PREFIX}file://{f['path']}",
                'vod_remarks': '',
                'style': {'type': 'grid', 'ratio': 1},
                'vod_player': '画'
            }
        
        # 音频文件
        if self.is_audio_file(f['ext']):
            return {
                'vod_id': self.URL_B64U_PREFIX + self.b64u_encode(self.MP3_PREFIX + f['path']),
                'vod_name': f"🎵 {f['name']}",
                'vod_pic': self.file_icons['audio'],
                'vod_play_url': f"播放${self.MP3_PREFIX + f['path']}",
                'vod_remarks': '',
                'style': {'type': 'list'},
                'vod_player': '听'
            }
        
        if self.is_media_file(f['ext']):
            return {
                'vod_id': f['path'],
                'vod_name': f"🎬 {f['name']}",
                'vod_pic': self.file_icons['video'],
                'vod_remarks': '',
                'style': {'type': 'list'}
            }
        
        if f['ext'] in ['m3u', 'm3u8']:
            colors = ["#FF6B6B", "#4ECDC4", "#FFD93D", "#6BCB77", "#9D65C9", "#FF8C42", "#A2D729", "#FF6B8B", "#45B7D1", "#96CEB4"]
            color = colors[hash(f['name']) % len(colors)]
            first_char = f['name'][0].upper() if f['name'] else "M"
            icon_svg = self._generate_colored_icon(color, first_char)
            return {
                'vod_id': self.LIST_PREFIX + self.b64u_encode(f['path']),
                'vod_name': f['name'],
                'vod_pic': icon_svg,
                'vod_remarks': '',
                'style': {'type': 'list'}
            }
        
        if self.is_db_file(f['ext']):
            return {
                'vod_id': self.LIST_PREFIX + self.b64u_encode(f['path']),
                'vod_name': f"🗄️ {f['name']}",
                'vod_pic': self.file_icons['database'],
                'vod_remarks': '',
                'style': {'type': 'list'}
            }
        
        if self.is_magnet_file(f['ext']):
            return {
                'vod_id': self.MAGNET_PREFIX + self.b64u_encode(f['path']),
                'vod_name': f"🧲 {f['name']}",
                'vod_pic': self.file_icons['magnet'],
                'vod_remarks': '',
                'style': {'type': 'list'}
            }
        
        if self.is_lrc_file(f['ext']):
            return {
                'vod_id': f['path'],
                'vod_name': f"📝 {f['name']}",
                'vod_pic': self.file_icons['lrc'],
                'vod_remarks': '',
                'style': {'type': 'list'}
            }
        
        if f['ext'] == 'json':
            return {
                'vod_id': self.LIST_PREFIX + self.b64u_encode(f['path']),
                'vod_name': f"📋 {f['name']}",
                'vod_pic': self.file_icons['list'],
                'vod_remarks': '',
                'style': {'type': 'list'}
            }
        
        if f['ext'] == 'txt':
            # 简单判断是否为直播源
            is_live = False
            if any(k in f['name'].lower() for k in self.live_keywords):
                is_live = True
            
            if is_live:
                # 直播源 - 用 LIST_PREFIX
                colors = ["#FF6B6B", "#4ECDC4", "#FFD93D", "#6BCB77", "#9D65C9", "#FF8C42", "#A2D729", "#FF6B8B", "#45B7D1", "#96CEB4"]
                color = colors[hash(f['name']) % len(colors)]
                first_char = f['name'][0].upper() if f['name'] else "T"
                icon_svg = self._generate_colored_icon(color, first_char)
                return {
                    'vod_id': self.LIST_PREFIX + self.b64u_encode(f['path']),
                    'vod_name': f['name'],
                    'vod_pic': icon_svg,
                    'vod_remarks': '',
                    'style': {'type': 'list'}
                }
            else:
                # 其他所有TXT - 用 NOVEL_PREFIX
                encoded = self.b64u_encode(f['path'])
                novel_url = f"{self.NOVEL_PREFIX}{encoded}"
                return {
                    'vod_id': novel_url,
                    'vod_name': f"📄 {f['name']}",
                    'vod_pic': self.file_icons['text'],
                    'vod_remarks': '',
                    'style': {'type': 'list'},
                    'vod_player': '书'
                }
        
        # 其他已知格式
        if f['ext'] in ['xml', 'html', 'htm', 'css', 'js', 'py', 'sh']:
            return {
                'vod_id': self.TEXT_PREFIX + self.b64u_encode(f['path']),
                'vod_name': f"📄 {f['name']}",
                'vod_pic': self.file_icons['text'],
                'vod_remarks': '',
                'style': {'type': 'list'}
            }
        
        # 未知类型
        return {
            'vod_id': f['path'],
            'vod_name': f"📁 {f['name']}",
            'vod_pic': self.file_icons['file'],
            'vod_remarks': '',
            'style': {'type': 'list'}
        }