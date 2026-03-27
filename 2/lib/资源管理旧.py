# 本地资源管理.py - 完整修复版（整合原代码所有功能）
# 基于原代码完整恢复：JSON解析、数据库读取、逐字歌词支持、在线直播、最近添加
# 整合：地址解析、请求头处理、分享页面解析

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
    '/storage/emulated/0/'
]

PATH_TO_CHINESE = {
    '/storage/emulated/0/Movies/': '电影',
    '/storage/emulated/0/Music/': '音乐',
    '/storage/emulated/0/Download/KuwoMusic/music/': '酷我音乐',
    '/storage/emulated/0/Download/': '下载',
    '/storage/emulated/0/DCIM/Camera/': '相机',
    '/storage/emulated/0/Pictures/': '图片',
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

print("ℹ️ 本地资源管理加载成功 - 完整修复版（整合原代码）")

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
        
        # 文件类型定义
        self.media_exts = ['mp4', 'mkv', 'avi', 'rmvb', 'mov', 'wmv', 'flv', 'm4v', 'ts', 'm3u8']
        self.audio_exts = ['mp3', 'm4a', 'aac', 'flac', 'wav', 'ogg', 'wma', 'ape']
        self.image_exts = ['jpg', 'jpeg', 'png', 'webp', 'gif', 'bmp', 'ico', 'svg']
        self.list_exts = ['m3u', 'txt', 'json', 'm3u8']
        self.lrc_exts = ['lrc', 'krc', 'qrc', 'yrc', 'trc']
        self.db_exts = ['db', 'sqlite', 'sqlite3', 'db3']
        self.magnet_exts = ['magnets', 'magnet', 'bt', 'torrent', 'mgt']
        
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

        self.lrc_cache = {}
        self.m3u8_cache = {}
        self.db_reader = DatabaseReader()
        
        # 海报缓存
        self.poster_cache = {}
        
        # 逐字歌词缓存
        self.word_lyrics_cache = {}
        
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
        videos = []
        for f in files:
            if not f['is_dir'] and self.is_media_file(f['ext']):
                videos.append(f)
        videos.sort(key=lambda x: x['name'].lower())
        return videos
    
    def collect_audios_in_dir(self, dir_path):
        files = self.scan_directory(dir_path)
        audios = []
        for f in files:
            if not f['is_dir'] and self.is_audio_file(f['ext']):
                audios.append(f)
        audios.sort(key=lambda x: x['name'].lower())
        return audios
    
    def collect_images_in_dir(self, dir_path):
        files = self.scan_directory(dir_path)
        images = []
        for f in files:
            if not f['is_dir'] and self.is_image_file(f['ext']):
                images.append(f)
        images.sort(key=lambda x: x['name'].lower())
        return images
    
    def collect_lrc_in_dir(self, dir_path):
        files = self.scan_directory(dir_path)
        lrcs = []
        for f in files:
            if not f['is_dir'] and self.is_lrc_file(f['ext']):
                lrcs.append(f)
        return lrcs
    
    def collect_dbs_in_dir(self, dir_path):
        files = self.scan_directory(dir_path)
        dbs = []
        for f in files:
            if not f['is_dir'] and self.is_db_file(f['ext']):
                dbs.append(f)
        dbs.sort(key=lambda x: x['name'].lower())
        return dbs
    
    def collect_magnets_in_dir(self, dir_path):
        files = self.scan_directory(dir_path)
        magnets = []
        for f in files:
            if not f['is_dir'] and self.is_magnet_file(f['ext']):
                magnets.append(f)
        magnets.sort(key=lambda x: x['name'].lower())
        return magnets
    
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
            'http-live://', 'https-live://', 'tvbus://', 'tvbox://', 'live://'
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
    
    # ==================== JSON文件解析（完整修复版）====================
    
    def parse_json_file(self, file_path):
        """
        解析JSON文件，支持各种格式
        重点修复：正确解析剧集数据，支持线路和选集
        """
        items = []
        try:
            self.log(f"开始解析JSON文件: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(30 * 1024 * 1024)  # 限制30MB
            
            # 去除BOM头
            if content.startswith('\ufeff'):
                content = content[1:]
            
            data = json.loads(content)
            self.log(f"JSON解析成功，数据类型: {type(data)}")
            
            # ========== 处理各种JSON结构 ==========
            
            # 情况1：直接是数组
            if isinstance(data, list):
                item_list = data
                self.log(f"直接使用数组，项目数: {len(item_list)}")
            
            # 情况2：是字典
            elif isinstance(data, dict):
                item_list = None
                
                # 2.1 检查是否有vod_play_url（影视剧格式）
                if 'vod_play_url' in data:
                    self.log("检测到影视剧格式（单条数据）")
                    return self._handle_vod_format(data, file_path)
                
                # 2.2 检查是否有vod_play_from（多线路格式）
                if 'vod_play_from' in data and 'vod_play_url' in data:
                    self.log("检测到多线路影视剧格式")
                    return self._handle_multi_line_vod(data, file_path)
                
                # 2.3 检查常见的列表键
                possible_keys = [
                    'list', 'data', 'items', 'videos', 'vod', 'movie', 
                    'results', 'rows', 'datas', 'data_list', 'video_list', 
                    'movie_list', 'playlist', 'episodes', 'sources',
                    'series', 'seasons', 'episodes_list', 'vod_list',
                    'programs', 'channels', 'tv', 'lives'
                ]
                
                for key in possible_keys:
                    if key in data and isinstance(data[key], list):
                        item_list = data[key]
                        self.log(f"找到顶层键: {key}, 项目数: {len(item_list)}")
                        break
                
                # 2.4 如果还是没有，检查是否是字典的值都是对象
                if item_list is None and all(isinstance(v, dict) for v in data.values()):
                    item_list = list(data.values())
                    self.log(f"使用字典值作为列表，项目数: {len(item_list)}")
                
                # 2.5 最后尝试作为单条数据处理
                if item_list is None:
                    item_list = [data]
                    self.log("将整个字典作为单个项目处理")
            
            else:
                self.log(f"不支持的JSON类型: {type(data)}")
                return items
            
            # ========== 解析每个项目 ==========
            for idx, item in enumerate(item_list):
                if not isinstance(item, dict):
                    # 如果是字符串且是URL，直接添加
                    if isinstance(item, str) and self.is_playable_url(item):
                        items.append({
                            'name': f'链接{idx+1}',
                            'url': item
                        })
                    continue
                
                # 检查是否是多集格式（直接包含vod_play_url）
                if 'vod_play_url' in item:
                    play_url_raw = item['vod_play_url']
                    name = self._extract_json_field(item, ['vod_name', 'name', 'title']) or f"剧集{idx+1}"
                    
                    if '$' in play_url_raw or '#' in play_url_raw or '$$$' in play_url_raw:
                        self.log(f"检测到多集格式: {name}")
                        episodes = self._parse_multi_episodes(play_url_raw, name)
                        items.extend(episodes)
                        continue
                
                # 提取名称
                name = self._extract_json_field(item, [
                    'name', 'title', 'vod_name', 'video_name', 'show_name',
                    'episode_name', 'program_name', 'channel_name', 'vod_title',
                    'display_name', 'label', 'text', 'caption', 'series_name',
                    'movie_name', 'film_name', 'episode'
                ])
                
                if not name:
                    name = f"项目{idx+1}"
                
                # 提取URL（先检查play_url相关字段）
                url = self._extract_json_field(item, [
                    'play_url', 'vod_play_url', 'video_url', 'stream_url', 'src',
                    'url', 'link', 'vod_url', 'uri', 'path', 'file', 'm3u8',
                    'mp4', 'playlink', 'video_link', 'play_path'
                ])
                
                if not url or not self.is_playable_url(url):
                    # 检查是否是多集格式（包含$或#）
                    play_url_raw = self._extract_json_field(item, [
                        'vod_play_url', 'play_url', 'vod_url', 'play_list'
                    ])
                    
                    if play_url_raw and ('$' in play_url_raw or '#' in play_url_raw):
                        self.log(f"检测到多集格式: {name}")
                        episodes = self._parse_multi_episodes(play_url_raw, name)
                        items.extend(episodes)
                        continue
                    else:
                        continue
                
                # 提取图片
                pic = self._extract_json_field(item, [
                    'pic', 'cover', 'image', 'thumbnail', 'poster', 
                    'vod_pic', 'img', 'picture', 'thumb', 'cover_img'
                ], is_image=True)
                
                # 提取备注
                remarks = self._extract_json_field(item, [
                    'remarks', 'remark', 'note', 'vod_remarks', 'type', 
                    'category', 'class', 'desc', 'description', 'info',
                    'episode', 'duration', 'time', 'year', 'area', 'lang',
                    'status', 'state'
                ])
                
                items.append({
                    'name': name,
                    'url': url,
                    'pic': pic,
                    'remarks': remarks
                })
            
            self.log(f"JSON解析完成: {os.path.basename(file_path)}, 共 {len(items)} 条有效记录")
            
        except json.JSONDecodeError as e:
            self.log(f"JSON解析错误: {e}")
            # 尝试使用json5解析
            try:
                import json5
                data = json5.loads(content)
                return self.parse_json_file(file_path)
            except:
                pass
        except Exception as e:
            self.log(f"JSON文件解析异常: {e}")
            import traceback
            traceback.print_exc()
        
        return items
    
    def _handle_vod_format(self, data, file_path):
        """处理影视剧单条数据格式"""
        items = []
        
        name = data.get('vod_name') or data.get('name') or data.get('title') or os.path.splitext(os.path.basename(file_path))[0]
        play_url = data.get('vod_play_url', '')
        pic = data.get('vod_pic') or data.get('pic') or data.get('cover') or ''
        
        if play_url and ('$' in play_url or '#' in play_url):
            episodes = self._parse_multi_episodes(play_url, name)
            for ep in episodes:
                ep['pic'] = pic
                items.append(ep)
        else:
            items.append({
                'name': name,
                'url': play_url,
                'pic': pic,
                'remarks': data.get('vod_remarks', '')
            })
        
        return items
    
    def _handle_multi_line_vod(self, data, file_path):
        """处理多线路影视剧格式"""
        items = []
        
        vod_name = data.get('vod_name') or data.get('name') or os.path.splitext(os.path.basename(file_path))[0]
        vod_pic = data.get('vod_pic') or data.get('pic') or ''
        
        play_from = data.get('vod_play_from', '').split('$$$')
        play_url = data.get('vod_play_url', '').split('$$$')
        
        for from_name, url_group in zip(play_from, play_url):
            if url_group and ('$' in url_group or '#' in url_group):
                episodes = self._parse_multi_episodes(url_group, from_name)
                for ep in episodes:
                    ep['pic'] = vod_pic
                    items.append(ep)
        
        return items
    
    def _parse_multi_episodes(self, play_url_raw, base_name):
        """解析多集格式（支持$和#分隔）"""
        episodes = []
        
        # 处理多个线路组（$$$分隔）
        groups = play_url_raw.split('$$$')
        for group in groups:
            if not group:
                continue
            
            # 处理单组内的多个剧集（#分隔）
            parts = group.split('#')
            for part in parts:
                if not part:
                    continue
                
                if '$' in part:
                    ep_name, ep_url = part.split('$', 1)
                    episodes.append({
                        'name': ep_name.strip(),
                        'url': ep_url.strip()
                    })
                else:
                    episodes.append({
                        'name': f"{base_name} - 集{len(episodes)+1}",
                        'url': part.strip()
                    })
        
        return episodes
    
    def _extract_json_field(self, item, field_names, is_image=False):
        """从JSON对象中提取字段值"""
        for field in field_names:
            if field in item and item[field]:
                value = item[field]
                
                # 处理嵌套的对象
                if isinstance(value, dict):
                    if 'url' in value:
                        return str(value['url'])
                    elif 'src' in value:
                        return str(value['src'])
                    elif 'large' in value:
                        return str(value['large'])
                    elif 'medium' in value:
                        return str(value['medium'])
                    elif 'thumbnail' in value:
                        return str(value['thumbnail'])
                elif isinstance(value, list) and value and is_image:
                    # 如果是图片数组，取第一个
                    if isinstance(value[0], dict) and 'url' in value[0]:
                        return str(value[0]['url'])
                    return str(value[0])
                else:
                    return str(value)
        return ''
    
    # ==================== 数据库文件解析 ====================
    
    def parse_db_file(self, file_path):
        """解析数据库文件"""
        return self.db_reader.read_sqlite(file_path, MAX_DB_RESULTS)
    
    # ==================== 逐字歌词支持 ====================
    
    def parse_krc_lyrics(self, krc_data):
        """解析酷狗KRC逐字歌词"""
        try:
            # KRC解密密钥
            key = bytearray([64, 71, 97, 100, 50, 45, 48, 51, 55, 56, 53, 51, 51, 51, 50, 52])
            
            # 移除头部标记
            if krc_data.startswith(b'krc1'):
                krc_data = krc_data[4:]
            
            # XOR解密
            decoded = bytearray()
            for i, b in enumerate(krc_data):
                decoded.append(b ^ key[i % 16])
            
            # 解压缩
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
        """解析KRC文本格式为逐字歌词"""
        lines = text.split('\n')
        metadata = {}
        word_lyrics = []
        lrc_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 解析元数据
            if line.startswith('[ar:') or line.startswith('[ti:') or line.startswith('[al:') or line.startswith('[by:'):
                metadata[line[1:3]] = line[4:-1]
                lrc_lines.append(line)
                continue
            
            # 解析歌词行
            match = re.match(r'\[(\d+),(\d+)\](.*)', line)
            if match:
                line_start = int(match.group(1))
                line_end = int(match.group(2))
                content = match.group(3)
                
                # 解析逐字信息
                words = []
                word_pattern = r'<(\d+),(\d+),([^>]*)>'
                for w_match in re.finditer(word_pattern, content):
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
                
                # 生成普通LRC
                minutes = line_start // 60000
                seconds = (line_start % 60000) // 1000
                milliseconds = (line_start % 1000) // 10
                lrc_lines.append(f"[{minutes:02d}:{seconds:02d}.{milliseconds:02d}] {word_line['text']}")
        
        return {
            'metadata': metadata,
            'word_lyrics': word_lyrics,
            'lrc_text': '\n'.join(lrc_lines)
        }

    def read_word_lyrics_file(self, file_path):
        """读取逐字歌词文件"""
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
        """验证是否为有效歌词"""
        if not text or len(text) < 20:
            return False
        
        markers = ['[ti:', '[ar:', '[al:', '[by:', '[00:', '[01:', '[02:', 
                  '作词', '作曲', '编曲', '演唱', '歌词']
        
        if any(marker in text for marker in markers):
            return True
        
        if re.search(r'\[\d{2}:\d{2}\.\d{2,}\]', text):
            return True
        
        chinese_count = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        return chinese_count > 10 and len(text) > 100
    
    def decode_lyrics_data(self, data):
        """解码歌词数据"""
        if not data:
            return None
        
        encodings = [
            ('utf-8', 'UTF-8'),
            ('gbk', 'GBK'),
            ('gb18030', 'GB18030'),
            ('gb2312', 'GB2312'),
            ('big5', 'Big5'),
            ('utf-16', 'UTF-16'),
        ]
        
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
        """读取普通LRC文件"""
        try:
            with open(lrc_path, 'rb') as f:
                data = f.read()
            return self.decode_lyrics_data(data)
        except Exception as e:
            print(f"读取歌词文件失败: {e}")
            return None
    
    def find_local_lrc(self, audio_path):
        """查找本地歌词文件（支持逐字歌词）"""
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
        """清理文件名"""
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
        """从文件名提取歌手和歌曲名"""
        name = self.clean_filename(filename)
        
        artist = ""
        song = name
        
        separators = [
            r'\s+-\s+', r'-\s+', r'\s+-', r'·', r'•', r'–', r'—', r'：', r':', r'、', r'／', r'/'
        ]
        
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
        """QQ音乐搜索"""
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
        """网易云音乐搜索"""
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
        """获取网络歌词"""
        if not artist and not song:
            return None
        
        cache_key = f"{artist}_{song}"
        if cache_key in self.lrc_cache:
            return self.lrc_cache[cache_key]
        
        # QQ音乐优先
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
        """提取MP3内嵌歌词"""
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
        """提取FLAC内嵌歌词"""
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
        """获取音频歌词 - 本地优先 -> 网络次之 -> 内嵌最后"""
        filename = os.path.basename(file_path)
        
        print(f"\n{'='*60}")
        print(f"🎵 [歌词获取] {filename}")
        print(f"{'='*60}")
        
        cache_key = f"audio_{file_path}"
        if cache_key in self.lrc_cache:
            print(f"📦 使用缓存歌词")
            return self.lrc_cache[cache_key]
        
        artist, song = self.extract_song_info(filename)
        print(f"📝 解析: 歌手='{artist}', 歌曲='{song}'")
        
        # 第一步：本地歌词
        lrc_info = self.find_local_lrc(file_path)
        if lrc_info[0]:
            lrc_path, lrc_format = lrc_info
            print(f"📁 找到本地歌词: {lrc_path} (格式: {lrc_format})")
            
            if lrc_format in ['krc', 'qrc', 'yrc', 'trc']:
                word_lyrics = self.read_word_lyrics_file(lrc_path)
                if word_lyrics:
                    result = {
                        'format': lrc_format,
                        'word_lyrics': word_lyrics.get('word_lyrics', []),
                        'lrc_text': word_lyrics.get('lrc_text', '')
                    }
                    self.lrc_cache[cache_key] = result
                    return result
            else:
                lrc_content = self.read_lrc_file(lrc_path)
                if lrc_content:
                    result = {'format': 'lrc', 'lrc_text': lrc_content}
                    self.lrc_cache[cache_key] = result
                    return result
        
        # 第二步：网络歌词
        online = self._get_online_lyrics(artist, song)
        if online:
            result = {'format': 'lrc', 'lrc_text': online}
            self.lrc_cache[cache_key] = result
            return result
        
        # 第三步：内嵌歌词
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
        """获取歌曲海报"""
        cache_key = f"{artist}_{song}"
        if cache_key in self.poster_cache:
            return self.poster_cache[cache_key]
        
        # 本地优先
        if audio_path:
            local = self._get_local_poster(audio_path)
            if local:
                self.poster_cache[cache_key] = local
                return local
        
        # 网络次之
        poster = self._qq_poster(artist, song) or self._netease_poster(artist, song)
        if poster:
            self.poster_cache[cache_key] = poster
        
        return poster
    
    def _get_local_poster(self, audio_path):
        """获取本地封面"""
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
        """QQ音乐海报"""
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
        """网易云海报"""
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
    
    def _generate_colored_icon(self, color, text):
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
            <rect width="200" height="200" rx="40" ry="40" fill="{color}"/>
            <text x="100" y="140" font-size="120" text-anchor="middle" fill="white" font-family="Arial" font-weight="bold">{text}</text>
        </svg>'''
        return f"data:image/svg+xml;base64,{base64.b64encode(svg.encode()).decode()}"
    
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
        
        # 连播列表（第一页）
        if pg == 1:
            videos = self.collect_videos_in_dir(path)
            if videos:
                vlist.append({
                    'vod_id': self.V_ALL_PREFIX + self.b64u_encode(path),
                    'vod_name': f'视频连播 ({len(videos)}个视频)',
                    'vod_pic': self.file_icons['video_playlist'],
                    'vod_remarks': '顺序播放',
                    'vod_tag': 'video_playlist',
                    'style': {'type': 'list'}
                })
            
            audios = self.collect_audios_in_dir(path)
            if audios:
                poster = self.file_icons['audio_playlist']
                artist, song = self.extract_song_info(audios[0]['name'])
                fetched = self._get_song_poster(artist, song, audios[0]['path'])
                if fetched:
                    poster = fetched
                
                vlist.append({
                    'vod_id': self.A_ALL_PREFIX + self.b64u_encode(path),
                    'vod_name': f'音频连播 ({len(audios)}首歌曲)',
                    'vod_pic': poster,
                    'vod_remarks': '顺序播放',
                    'vod_tag': 'audio_playlist',
                    'style': {'type': 'list'}
                })
            
            images = self.collect_images_in_dir(path)
            if images:
                vlist.append({
                    'vod_id': self.PICS_PREFIX + 'slideshow/' + self.b64u_encode(path),
                    'vod_name': f'图片连播 ({len(images)}张照片)',
                    'vod_pic': self.file_icons['image_playlist'],
                    'vod_remarks': '点击浏览全部照片',
                    'vod_tag': 'image_playlist',
                    'style': {'type': 'list'}
                })
        
        # 文件列表
        for f in page_files:
            vlist.append(self._create_file_item(f))
        
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
    
    def _create_file_item(self, f):
        icon = self.get_file_icon(f['ext'], f['is_dir'])
        
        if f['is_dir']:
            return {
                'vod_id': self.FOLDER_PREFIX + self.b64u_encode(f['path']),
                'vod_name': f"{icon} {f['name']}",
                'vod_pic': self.file_icons['folder'],
                'vod_remarks': '文件夹',
                'vod_tag': 'folder',
                'style': {'type': 'list'}
            }
        
        if self.is_audio_file(f['ext']):
            return {
                'vod_id': f['path'],
                'vod_name': f"{icon} {f['name']}",
                'vod_pic': self.file_icons['audio'],
                'vod_play_url': f"播放${self.MP3_PREFIX + f['path']}",
                'vod_remarks': '音频',
                'vod_tag': 'audio',
                'style': {'type': 'list'}
            }
        
        if self.is_image_file(f['ext']):
            return {
                'vod_id': f['path'],
                'vod_name': f"{icon} {f['name']}",
                'vod_pic': f"file://{f['path']}",
                'vod_play_url': f"查看${self.PICS_PREFIX}file://{f['path']}",
                'vod_remarks': '照片',
                'vod_tag': 'image',
                'style': {'type': 'grid', 'ratio': 1}
            }
        
        if self.is_media_file(f['ext']):
            return {
                'vod_id': f['path'],
                'vod_name': f"{icon} {f['name']}",
                'vod_pic': self.file_icons['video'],
                'vod_remarks': '视频',
                'vod_tag': 'video',
                'style': {'type': 'list'}
            }
        
        if self.is_list_file(f['ext']):
            return {
                'vod_id': self.LIST_PREFIX + self.b64u_encode(f['path']),
                'vod_name': f"{icon} {f['name']}",
                'vod_pic': self.file_icons['list'],
                'vod_remarks': '播放列表',
                'vod_tag': 'list',
                'style': {'type': 'list'}
            }
        
        if self.is_lrc_file(f['ext']):
            return {
                'vod_id': f['path'],
                'vod_name': f"{icon} {f['name']}",
                'vod_pic': self.file_icons['lrc'],
                'vod_remarks': '歌词',
                'vod_tag': 'lrc',
                'style': {'type': 'list'}
            }
        
        if self.is_db_file(f['ext']):
            return {
                'vod_id': self.LIST_PREFIX + self.b64u_encode(f['path']),
                'vod_name': f"{icon} {f['name']}",
                'vod_pic': self.file_icons['database'],
                'vod_remarks': '数据库',
                'vod_tag': 'database',
                'style': {'type': 'list'}
            }
        
        if self.is_magnet_file(f['ext']):
            return {
                'vod_id': self.MAGNET_PREFIX + self.b64u_encode(f['path']),
                'vod_name': f"{icon} {f['name']}",
                'vod_pic': self.file_icons['magnet'],
                'vod_remarks': '磁力链接',
                'vod_tag': 'magnet',
                'style': {'type': 'list'}
            }
        
        return {
            'vod_id': f['path'],
            'vod_name': f"{icon} {f['name']}",
            'vod_pic': self.file_icons['file'],
            'vod_remarks': '文件',
            'vod_tag': 'file',
            'style': {'type': 'list'}
        }
    
    def _live_category_content(self, pg):
        vlist = []
        
        for idx, source in enumerate(self.online_live_sources):
            programs = self._get_live_programs(source)
            color = source.get('color', self.default_colors[idx % len(self.default_colors)])
            icon = self._generate_colored_icon(color, source['name'][0] if source['name'] else "直")
            
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
                'style': {'type': 'list'}
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
                        self.is_db_file(ext) or self.is_magnet_file(ext)):
                        
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
        if self.is_image_file(f['ext']):
            return {
                'vod_id': self.URL_B64U_PREFIX + self.b64u_encode(self.PICS_PREFIX + "file://" + f['path']),
                'vod_name': f"📷 {f['name']}",
                'vod_pic': f"file://{f['path']}",
                'vod_play_url': f"查看${self.PICS_PREFIX}file://{f['path']}",
                'vod_remarks': self._format_time(f['mtime']),
                'style': {'type': 'grid', 'ratio': 1}
            }
        
        if self.is_audio_file(f['ext']):
            return {
                'vod_id': self.URL_B64U_PREFIX + self.b64u_encode(self.MP3_PREFIX + f['path']),
                'vod_name': f"🎵 {f['name']}",
                'vod_pic': self.file_icons['audio'],
                'vod_play_url': f"播放${self.MP3_PREFIX + f['path']}",
                'vod_remarks': self._format_time(f['mtime']),
                'style': {'type': 'grid', 'ratio': 1}
            }
        
        if self.is_media_file(f['ext']):
            return {
                'vod_id': f['path'],
                'vod_name': f"🎬 {f['name']}",
                'vod_pic': self.file_icons['video'],
                'vod_remarks': self._format_time(f['mtime']),
                'style': {'type': 'grid', 'ratio': 1}
            }
        
        if self.is_list_file(f['ext']):
            return {
                'vod_id': self.LIST_PREFIX + self.b64u_encode(f['path']),
                'vod_name': f"📋 {f['name']}",
                'vod_pic': self.file_icons['list'],
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
        
        return {
            'vod_id': f['path'],
            'vod_name': f"📄 {f['name']}",
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
        
        if id_val.startswith(self.FOLDER_PREFIX):
            folder_path = self.b64u_decode(id_val[len(self.FOLDER_PREFIX):])
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                return self.categoryContent(folder_path, 1, None, None)
            return {'list': []}
        
        if id_val.startswith(self.PICS_PREFIX + 'slideshow/'):
            dir_path = self.b64u_decode(id_val[len(self.PICS_PREFIX + 'slideshow/'):])
            images = self.collect_images_in_dir(dir_path)
            if not images:
                return {'list': []}
            
            pic_urls = [f"file://{img['path']}" for img in images]
            return {'list': [{
                'vod_id': id_val,
                'vod_name': f"📷 图片连播 - {os.path.basename(dir_path)} ({len(images)}张)",
                'vod_pic': self.file_icons['image_playlist'],
                'vod_play_from': '图片浏览',
                'vod_play_url': f"浏览${self.PICS_PREFIX + '&&'.join(pic_urls)}",
                'style': {'type': 'list'}
            }]}
        
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
            return {'list': [{
                'vod_id': id_val,
                'vod_name': f"📷 相机照片 ({len(images)}张)",
                'vod_pic': self.file_icons['image_playlist'],
                'vod_play_from': '照片查看',
                'vod_play_url': f"浏览${self.PICS_PREFIX + '&&'.join(pic_urls)}",
                'style': {'type': 'list'}
            }]}
        
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
                'style': {'type': 'list'}
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
                'style': {'type': 'list'}
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
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return {'list': []}
        
        ext = self.get_file_ext(file_path)
        self.log(f"处理列表文件: {file_path}, 类型: {ext}")
        
        if self.is_db_file(ext):
            items = self.parse_db_file(file_path)
            self.log(f"数据库解析到 {len(items)} 条记录")
            
            if not items:
                return {'list': [self._create_fallback_vod(file_path, 'database', vod_id)]}
            
            play_urls = self._build_play_urls(items)
            pic = items[0].get('pic', '') if items[0].get('pic') else self.file_icons['database']
            
            return {'list': [{
                'vod_id': vod_id,
                'vod_name': os.path.basename(file_path),
                'vod_pic': pic,
                'vod_play_from': '数据库播放列表',
                'vod_play_url': '#'.join(play_urls),
                'style': {'type': 'list'}
            }]}
        
        items = []
        if ext in ['m3u', 'm3u8']:
            items = self._parse_m3u_file(file_path)
        elif ext == 'txt':
            items = self._parse_txt_file(file_path)
        elif ext == 'json':
            items = self.parse_json_file(file_path)
        
        self.log(f"列表文件解析到 {len(items)} 条记录")
        
        if not items:
            name = os.path.splitext(os.path.basename(file_path))[0]
            return {'list': [self._create_fallback_vod(file_path, 'list', vod_id, name)]}
        
        play_urls = self._build_play_urls(items)
        
        return {'list': [{
            'vod_id': vod_id,
            'vod_name': os.path.basename(file_path),
            'vod_pic': items[0].get('pic', '') or self.file_icons['list'],
            'vod_play_from': '播放列表',
            'vod_play_url': '#'.join(play_urls),
            'style': {'type': 'list'}
        }]}
    
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
        items = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    if ',' in line:
                        parts = line.split(',', 1)
                        name = parts[0].strip()
                        url = parts[1].strip()
                        if self.is_playable_url(url):
                            items.append({'name': name, 'url': url})
        except:
            pass
        
        return items
    
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
        play_urls = []
        for item in items:
            url = item.get('url') or item.get('play_url', '')
            if url:
                play_urls.append(f"{item['name']}${url}")
        return play_urls
    
    def _handle_audio_all_detail(self, dir_path, vod_id):
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
            'vod_name': f"音频连播 - {os.path.basename(dir_path)} ({len(audios)}首)",
            'vod_pic': poster,
            'vod_play_from': '本地音乐',
            'vod_play_url': '#'.join(play_urls),
            'style': {'type': 'list'}
        }]}
    
    def _handle_video_all_detail(self, dir_path, vod_id):
        videos = self.collect_videos_in_dir(dir_path)
        
        if not videos:
            return {'list': []}
        
        play_urls = [f"{os.path.splitext(v['name'])[0]}$file://{v['path']}" for v in videos]
        
        return {'list': [{
            'vod_id': vod_id,
            'vod_name': f"视频连播 - {os.path.basename(dir_path)} ({len(videos)}集)",
            'vod_pic': self.file_icons['video_playlist'],
            'vod_play_from': '本地视频',
            'vod_play_url': '#'.join(play_urls),
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
        
        if self.is_image_file(ext):
            vod.update({
                'vod_play_url': f"查看${self.PICS_PREFIX}file://{file_path}",
                'vod_pic': f"file://{file_path}",
                'vod_name': f"🖼️ {name}"
            })
        elif self.is_audio_file(ext):
            vod.update({
                'vod_play_url': f"{os.path.splitext(name)[0]}${self.MP3_PREFIX + file_path}",
                'vod_name': f"🎵 {name}",
                'vod_pic': self.file_icons['audio']
            })
            
            artist, song = self.extract_song_info(name)
            poster = self._get_song_poster(artist, song, file_path)
            if poster:
                vod['vod_pic'] = poster
        elif self.is_media_file(ext):
            vod.update({
                'vod_play_url': f"{os.path.splitext(name)[0]}$file://{file_path}",
                'vod_pic': self.file_icons['video']
            })
        elif self.is_list_file(ext) or self.is_db_file(ext) or self.is_magnet_file(ext):
            prefix = self.MAGNET_PREFIX if self.is_magnet_file(ext) else self.LIST_PREFIX
            return self.detailContent([prefix + self.b64u_encode(file_path)])
        
        return {'list': [vod]}
    
    def _live_source_detail(self, source_id):
        source = next((s for s in self.online_live_sources if s['id'] == source_id), None)
        if not source:
            return {'list': []}
        
        idx = self.online_live_sources.index(source)
        color = source.get('color', self.default_colors[idx % len(self.default_colors)])
        icon = self._generate_colored_icon(color, source['name'][0] if source['name'] else "直")
        
        programs = self._get_live_programs(source)
        if not programs:
            return {'list': [{
                'vod_id': self.LIVE_PREFIX + self.b64u_encode(source_id),
                'vod_name': source['name'],
                'vod_pic': icon,
                'vod_play_from': '直播源',
                'vod_play_url': '提示$无法获取直播源，请稍后重试',
                'vod_content': f"直播源: {source['url']}\n状态: 获取失败",
                'style': {'type': 'list'}
            }]}
        
        # 按频道分组
        channels = {}
        for p in programs:
            name = p['name']
            clean_name = re.sub(r'^\[[^\]]+\]\s*', '', name)
            clean_name = re.sub(r'\s*[\[\(（]\s*\d+\s*[\]\)）]\s*$', '', clean_name)
            
            if clean_name not in channels:
                channels[clean_name] = []
            channels[clean_name].append(p)
        
        from_list, url_list = [], []
        for name, links in channels.items():
            from_list.append(name)
            if len(links) > 1:
                link_parts = [f"线路{i+1}${l['url']}" for i, l in enumerate(links)]
                url_list.append('#'.join(link_parts))
            else:
                url_list.append(f"{name}${links[0]['url']}")
        
        vod = {
            'vod_id': self.LIVE_PREFIX + self.b64u_encode(source_id),
            'vod_name': source['name'],
            'vod_pic': icon,
            'vod_play_from': '$$$'.join(from_list),
            'vod_play_url': '$$$'.join(url_list),
            'vod_content': f"共 {len(channels)} 个频道，{sum(len(v) for v in channels.values())} 条线路"
        }
        
        if source.get('playerType'):
            vod['playerType'] = source['playerType']
        
        return {'list': [vod]}
    
    # ==================== 播放页（整合原代码的地址解析）====================

    def playerContent(self, flag, id, vipFlags):
        self.log(f"播放请求: flag={flag}, id={id}")
        
        original_id = id
        
        # 处理pics协议
        if id.startswith(self.PICS_PREFIX):
            return {"parse": 0, "playUrl": "", "url": id, "header": {}}
        
        # 处理mp3协议
        if id.startswith(self.MP3_PREFIX):
            return self._handle_mp3_play(id)
        
        # 提取真实URL（处理$符号）
        url = self._extract_real_url(id)
        self.log(f"提取到的URL: {url}")
        
        # ===== 从原代码整合：检测并处理特殊地址（dytt分享链接）=====
        if 'dytt-' in url and '/share/' in url and not url.endswith('.m3u8'):
            self.log(f"检测到dytt分享链接，尝试提取真实地址")
            real_url = self._extract_real_m3u8_url(url)
            if real_url:
                self.log(f"✅ 提取到真实m3u8地址: {real_url}")
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
            "url": 'file://' + file_path,
            "header": {}
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

    def _extract_real_url(self, id):
        """从原代码整合：提取真实URL（处理$符号和base64）"""
        url = id
        
        # 处理 $ 符号（移除剧集名称）
        if '$' in url:
            parts = url.split('$', 1)
            if len(parts) == 2:
                url = parts[1]
                self.log(f"从 {id} 提取真实URL: {url}")
        
        # 已经是标准协议的直接返回
        if url.startswith(('http://', 'https://', 'file://')):
            return url
        
        # 尝试base64解码
        try:
            decoded = base64.b64decode(url).decode('utf-8')
            if decoded.startswith(('http://', 'https://', 'file://')):
                self.log(f"标准base64解码成功: {decoded[:50]}...")
                return decoded
        except:
            pass
        
        # 尝试自定义b64u解码
        if url.startswith(self.URL_B64U_PREFIX):
            try:
                decoded = self.b64u_decode(url[len(self.URL_B64U_PREFIX):])
                if decoded:
                    self.log(f"b64u解码成功: {decoded[:50]}...")
                    return decoded
            except:
                pass
        
        return url

    def _extract_real_m3u8_url(self, page_url):
        """
        从原代码整合：从页面提取真实m3u8地址
        原代码中的 _extract_real_m3u8_url 方法
        """
        # 检查缓存
        if page_url in self.m3u8_cache:
            cached = self.m3u8_cache[page_url]
            if cached:
                self.log(f"✅ 使用缓存的m3u8地址: {cached}")
            else:
                self.log(f"⚠️ 缓存中无有效地址: {page_url}")
            return cached
        
        try:
            self.log(f"🔍 尝试从页面提取真实m3u8地址: {page_url}")
            
            from urllib.parse import urlparse
            parsed = urlparse(page_url)
            domain = parsed.netloc
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            
            self.log(f"域名: {domain}, 基础URL: {base_url}")
            
            # 使用浏览器风格的请求头
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Referer": base_url + "/",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
            }
            
            # 获取页面内容
            response = self.session.get(page_url, headers=headers, timeout=10)
            if response.status_code != 200:
                self.log(f"❌ 获取页面失败: {response.status_code}")
                self.m3u8_cache[page_url] = None
                return None
            
            html = response.text
            self.log(f"✅ 页面获取成功，内容长度: {len(html)}")
            
            # 多种匹配模式（从原代码继承）
            m3u8_patterns = [
                r'(https?://[^\s"\']+\.m3u8[^\s"\']*)',
                r'(//[^\s"\']+\.m3u8[^\s"\']*)',
                r'url["\']?\s*[:=]\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
                r'src["\']?\s*[:=]\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
                r'video_url["\']?\s*[:=]\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
                r'play_url["\']?\s*[:=]\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
                r'var\s+videoUrl\s*=\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
                r'var\s+url\s*=\s*["\']([^"\']+\.m3u8[^"\']*)["\']'
            ]
            
            for pattern in m3u8_patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                if matches:
                    url = matches[0]
                    # 处理相对地址
                    if url.startswith('//'):
                        url = 'https:' + url
                    elif url.startswith('/'):
                        url = base_url + url
                    self.log(f"✅ 找到m3u8地址: {url}")
                    self.m3u8_cache[page_url] = url
                    return url
            
            # 尝试查找iframe（递归解析）
            iframe_pattern = r'<iframe[^>]+src=["\']([^"\']+)["\']'
            iframe_match = re.search(iframe_pattern, html, re.IGNORECASE)
            if iframe_match:
                iframe_url = iframe_match.group(1)
                self.log(f"找到iframe: {iframe_url}")
                
                # 处理相对地址
                if iframe_url.startswith('//'):
                    iframe_url = 'https:' + iframe_url
                elif iframe_url.startswith('/'):
                    iframe_url = base_url + iframe_url
                elif not iframe_url.startswith('http'):
                    iframe_url = base_url + '/' + iframe_url.lstrip('/')
                
                # 递归解析iframe
                return self._extract_real_m3u8_url(iframe_url)
            
            self.log(f"❌ 未能提取到真实m3u8地址")
            self.m3u8_cache[page_url] = None
            return None
            
        except Exception as e:
            self.log(f"❌ 提取真实地址失败: {e}")
            import traceback
            traceback.print_exc()
            self.m3u8_cache[page_url] = None
            return None

    def _build_headers(self, flag, url):
        """构建请求头 - 从原代码整合域名专用头"""
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "*/*"
        }
        
        self.log(f"构建请求头: flag={flag}, domain={domain}")
        
        # ========== 根据flag设置特定头（从原代码整合）==========
        if flag == 'migu_live':
            headers.update({
                "User-Agent": "com.android.chrome/3.7.0 (Linux;Android 15)",
                "Referer": "https://www.miguvideo.com/"
            })
            self.log("使用咪咕直播专用请求头")
        
        elif flag == 'gongdian_live':
            headers.update({
                "Referer": "https://gongdian.top/"
            })
            self.log("使用宫殿直播专用请求头")
        
        # ========== 根据域名设置特定头（从原代码整合）==========
        
        # t.061899.xyz 专用
        if 't.061899.xyz' in domain:
            headers.update({
                "User-Agent": "okhttp/3.12.11",
                "Referer": "http://t.061899.xyz/",
                "Accept": "*/*"
            })
            self.log(f"✅ 使用 t.061899.xyz 专用请求头")
        
        # rihou.cc 专用
        elif 'rihou.cc' in domain:
            headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Referer": "https://rihou.cc:555/",
                "Accept": "*/*"
            })
            self.log(f"✅ 使用 rihou.cc 专用请求头")
        
        # miguvideo.com 专用
        elif 'miguvideo.com' in domain:
            headers.update({
                "User-Agent": "com.android.chrome/3.7.0 (Linux;Android 15)",
                "Referer": "https://www.miguvideo.com/"
            })
            self.log(f"✅ 使用 miguvideo.com 专用请求头")
        
        # gongdian.top 专用
        elif 'gongdian.top' in domain:
            headers.update({
                "Referer": "https://gongdian.top/"
            })
            self.log(f"✅ 使用 gongdian.top 专用请求头")
        
        # dytt-film.com 专用（新增）
        elif 'dytt-film.com' in domain:
            headers.update({
                "Referer": "https://vip.dytt-film.com/",
                "Origin": "https://vip.dytt-film.com"
            })
            self.log(f"✅ 使用 dytt-film.com 专用请求头")
        
        # 其他域名添加通用Referer
        elif domain:
            headers["Referer"] = f"https://{domain}/"
            self.log(f"添加通用Referer: {headers['Referer']}")
        
        # 移除可能导致问题的Range头
        if "Range" in headers:
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
        if self.is_image_file(f['ext']):
            return {
                'vod_id': self.URL_B64U_PREFIX + self.b64u_encode(self.PICS_PREFIX + "file://" + f['path']),
                'vod_name': f"📷 {f['name']}",
                'vod_pic': f"file://{f['path']}",
                'vod_play_url': f"查看${self.PICS_PREFIX}file://{f['path']}",
                'vod_remarks': '',
                'style': {'type': 'grid', 'ratio': 1}
            }
        
        if self.is_audio_file(f['ext']):
            return {
                'vod_id': self.URL_B64U_PREFIX + self.b64u_encode(self.MP3_PREFIX + f['path']),
                'vod_name': f"🎵 {f['name']}",
                'vod_pic': self.file_icons['audio'],
                'vod_play_url': f"播放${self.MP3_PREFIX + f['path']}",
                'vod_remarks': '',
                'style': {'type': 'list'}
            }
        
        if self.is_media_file(f['ext']):
            return {
                'vod_id': f['path'],
                'vod_name': f"🎬 {f['name']}",
                'vod_pic': self.file_icons['video'],
                'vod_remarks': '',
                'style': {'type': 'list'}
            }
        
        if self.is_list_file(f['ext']):
            return {
                'vod_id': self.LIST_PREFIX + self.b64u_encode(f['path']),
                'vod_name': f"📋 {f['name']}",
                'vod_pic': self.file_icons['list'],
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
        
        return {
            'vod_id': f['path'],
            'vod_name': f"📄 {f['name']}",
            'vod_pic': self.file_icons['file'],
            'vod_remarks': '',
            'style': {'type': 'list'}
        }