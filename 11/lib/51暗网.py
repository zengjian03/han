import json
import re
import sys
import hashlib
import time
from base64 import b64decode, b64encode
from urllib.parse import urlparse, urljoin

import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from pyquery import PyQuery as pq

sys.path.append('..')
from base.spider import Spider as BaseSpider

# 图片缓存，避免重复解密
img_cache = {}

class Spider(BaseSpider):

    def init(self, extend=""):
        try:
            self.proxies = json.loads(extend)
        except:
            self.proxies = {}
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1'
        }
        self.host = self.get_working_host()
        self.headers.update({'Origin': self.host, 'Referer': f"{self.host}/"})
        print(f"使用站点: {self.host}")

    def getName(self):
        return "🌈 吃瓜网|Pro增强版"

    def isVideoFormat(self, url):
        return any(ext in (url or '').lower() for ext in ['.m3u8', '.mp4', '.ts', '.flv', '.mkv', '.avi'])

    def manualVideoCheck(self):
        return False

    def destroy(self):
        global img_cache
        img_cache.clear()

    def get_working_host(self):
        dynamic_urls = [
            'https://basic.xhhcfqf.cc/'
        ]
        for url in dynamic_urls:
            try:
                # 减少超时时间，加快检测
                response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=3)
                if response.status_code == 200:
                    return url.rstrip('/')
            except Exception:
                continue
        return dynamic_urls[0].rstrip('/')

    def homeContent(self, filter):
        try:
            response = requests.get(self.host, headers=self.headers, proxies=self.proxies, timeout=10)
            if response.status_code != 200: 
                return {'class': [], 'list': []}
            
            response.encoding = response.apparent_encoding
            data = self.getpq(response.text)
            
            classes = []
            # 增加选择器范围
            nav_items = data('nav a, .menu a, .nav a, #header a, .header a, ul.navbar-nav a, .category-list a, .scroll-content a')
            seen_hrefs = set()
            bad_words = ['登录', '注册', '搜索', '首页', 'Home', 'Login', 'Search', '联系', '关于', '留言', 'RSS', '推特', 'TG', 'Q群', '合作', '公告', 'APP', '下载', '问题', '往期', '代理', '导航']
            
            for k in nav_items.items():
                href = (k.attr('href') or '').strip()
                name = k.text().strip()
                if not href or href == '#' or href == '/' or 'javascript' in href: continue
                if not name or len(name) < 2 or len(name) > 12: continue # 放宽长度限制
                if any(bw in name for bw in bad_words): continue
                if href in seen_hrefs: continue
                
                # 规范化 href
                if not href.startswith('http'):
                     href = urljoin(self.host, href)
                     
                classes.append({'type_name': name, 'type_id': href})
                seen_hrefs.add(href)
                if len(classes) >= 25: break
            
            if not classes:
                classes = [{'type_name': '最新', 'type_id': '/latest/'}, {'type_name': '热门', 'type_id': '/hot/'}]
            
            videos = self.getlist(data, '#content article, #main article, .posts article, .container .row article, article, .video-list .video-item')
            return {'class': classes, 'list': videos}
        except Exception as e:
            print(f"Home Error: {e}")
            return {'class': [], 'list': []}

    def homeVideoContent(self):
        # 复用 homeContent 逻辑，减少代码冗余
        res = self.homeContent(None)
        return {'list': res.get('list', [])}

    def categoryContent(self, tid, pg, filter, extend):
        try:
            if '@folder' in tid:
                v = self.getfod(tid.replace('@folder', ''))
                return {'list': v, 'page': 1, 'pagecount': 1, 'limit': 90, 'total': len(v)}
            
            pg = int(pg) if pg else 1
            url = tid if tid.startswith('http') else f"{self.host}{tid if tid.startswith('/') else '/'+tid}"
            url = url.rstrip('/')
            
            real_url = f"{url}/" if pg == 1 else f"{url}/{pg}/"
            # 兼容某些站点的分页参数 ?page=2
            if 'page=' in url or 'pg=' in url:
                 real_url = url.replace('{pg}', str(pg))
                
            response = requests.get(real_url, headers=self.headers, proxies=self.proxies, timeout=10)
            if response.status_code != 200: 
                return {'list': [], 'page': pg, 'pagecount': 9999, 'limit': 90, 'total': 0}
                
            data = self.getpq(response.text)
            videos = self.getlist(data, '#content article, #main article, .posts article, article, .video-list .video-item', tid)
            return {'list': videos, 'page': pg, 'pagecount': 9999, 'limit': 90, 'total': 999999}
        except Exception as e:
            return {'list': [], 'page': pg, 'pagecount': 9999, 'limit': 90, 'total': 0}

    def detailContent(self, ids):
        try:
            url = ids[0] if ids[0].startswith('http') else f"{self.host}{ids[0]}"
            response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=10)
            html_text = response.text
            data = self.getpq(html_text)
            
            plist = []
            unique_urls = set()

            def add_play_url(name, u):
                if not u or u in unique_urls: return
                # 处理相对路径
                if not u.startswith('http'):
                    u = urljoin(self.host, u)
                unique_urls.add(u)
                plist.append(f"{name}${u}")

            # --- 1. 原始规则：优先匹配 Script 中的 m3u8/mp4 ---
            scripts = data('script')
            for s in scripts.items():
                txt = s.text()
                if 'url' in txt and ('.m3u8' in txt or '.mp4' in txt):
                    # 优化正则，防止匹配到 truncated 字符串
                    urls = re.findall(r'[\"\'](http[^\"\']+\.(?:m3u8|mp4)[^\"\']*)[\"\']', txt)
                    for u in urls:
                        add_play_url("精选源", u)
                        break 
            
            # --- 2. 原始规则：DPlayer ---
            if data('.dplayer'):
                for c, k in enumerate(data('.dplayer').items(), start=1):
                    config_attr = k.attr('data-config')
                    if config_attr:
                        try:
                            config = json.loads(config_attr)
                            video_url = config.get('video', {}).get('url', '')
                            add_play_url(f"云播{c}", video_url)
                        except: pass

            # --- 3. 新增通用规则：HTML5 Video 标签 ---
            for v in data('video').items():
                src = v.attr('src')
                if src: add_play_url("HTML5直连", src)
                for src_tag in v('source').items():
                     add_play_url("HTML5源", src_tag.attr('src'))

            # --- 4. 新增通用规则：Iframe 嗅探 ---
            for iframe in data('iframe').items():
                src = iframe.attr('src') or iframe.attr('data-src')
                if src and any(x in src for x in ['.m3u8', '.mp4', 'upload', 'cloud', 'player']):
                    if 'google' not in src and 'facebook' not in src: # 排除常见广告
                        add_play_url("云解析", src)

            # --- 5. 新增通用规则：常见变量/Json正则 (核心增强) ---
            # 匹配常见的 CMS 播放器配置变量
            common_patterns = [
                r'var\s+main\s*=\s*[\"\']([^\"\']+)[\"\']',
                r'url\s*:\s*[\"\']([^\"\']+\.(?:m3u8|mp4))[\"\']',
                r'vurl\s*=\s*[\"\']([^\"\']+)[\"\']',
                r'vid\s*:\s*[\"\']([^\"\']+\.(?:m3u8|mp4))[\"\']',
                r'"url"\s*:\s*"([^"]+)"',
                r'video_url\s*=\s*[\'"]([^\'"]+)[\'"]',
            ]
            for pat in common_patterns:
                if match := re.search(pat, html_text):
                    u = match.group(1)
                    # 忽略非视频链接
                    if any(ext in u for ext in ['.m3u8', '.mp4', '.flv', 'http']):
                        add_play_url("通用嗅探", u)

            # --- 6. 原始规则兜底：文本链接 ---
            if not plist:
                content_area = data('.post-content, article, .content, .video-info')
                for i, link in enumerate(content_area('a').items(), start=1):
                    link_text = link.text().strip()
                    link_href = link.attr('href')
                    if link_href and any(kw in link_text for kw in ['点击观看', '观看', '播放', '视频', '第一弹', '线路']):
                        ep_name = link_text.replace('点击观看：', '').replace('点击观看', '').strip()
                        if not ep_name: ep_name = f"线路{i}"
                        add_play_url(ep_name, link_href)

            play_url = '#'.join(plist) if plist else f"无视频源，请尝试网页播放${url}"
            
            # 标题获取优化
            vod_title = data('h1').text().strip() 
            if not vod_title: vod_title = data('.post-title').text().strip()
            if not vod_title: vod_title = data('title').text().split('|')[0].strip()
            
            return {'list': [{'vod_play_from': '吃瓜网Pro', 'vod_play_url': play_url, 'vod_content': vod_title}]}
        except Exception as e:
            print(f"Detail Error: {e}")
            return {'list': [{'vod_play_from': '吃瓜网Pro', 'vod_play_url': '获取失败'}]}

    def searchContent(self, key, quick, pg="1"):
        try:
            pg = int(pg) if pg else 1
            url = f"{self.host}/?s={key}" 
            response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=10)
            data = self.getpq(response.text)
            return {'list': self.getlist(data, 'article, .search-result, .post, .video-item'), 'page': pg, 'pagecount': 9999}
        except:
            return {'list': [], 'page': pg, 'pagecount': 9999}

    def playerContent(self, flag, id, vipFlags):
        # 如果是 iframe 的 src，通常需要 webview 解析，flag=1
        # 如果是直接的 .m3u8/.mp4，flag=0
        if 'html' in id or 'php' in id:
            parse = 1
        elif self.isVideoFormat(id):
            parse = 0
        else:
            parse = 1 # 默认解析
        
        url = self.proxy(id) if '.m3u8' in id else id
        return {'parse': parse, 'url': url, 'header': self.headers}

    def localProxy(self, param):
        try:
            type_ = param.get('type')
            url = param.get('url')
            if type_ == 'cache':
                key = param.get('key')
                if content := img_cache.get(key):
                    return [200, 'image/jpeg', content]
                return [404, 'text/plain', b'Expired']
            elif type_ == 'img':
                real_url = self.d64(url) if not url.startswith('http') else url
                # 图片是加密的，所以必须解密
                res = requests.get(real_url, headers=self.headers, proxies=self.proxies, timeout=10)
                content = self.aesimg(res.content)
                return [200, 'image/jpeg', content]
            elif type_ == 'm3u8':
                return self.m3Proxy(url)
            else:
                return self.tsProxy(url)
        except:
            return [404, 'text/plain', b'']

    def proxy(self, data, type='m3u8'):
        if data and self.proxies: return f"{self.getProxyUrl()}&url={self.e64(data)}&type={type}"
        return data

    def m3Proxy(self, url):
        url = self.d64(url)
        res = requests.get(url, headers=self.headers, proxies=self.proxies)
        data = res.text
        base = res.url.rsplit('/', 1)[0]
        lines = []
        for line in data.split('\n'):
            if '#EXT' not in line and line.strip():
                if not line.startswith('http'):
                    # 修正 m3u8 相对路径拼接问题
                    if line.startswith('/'):
                         host_base = '/'.join(res.url.split('/')[:3])
                         line = f"{host_base}{line}"
                    else:
                         line = f"{base}/{line}"
                lines.append(self.proxy(line, 'ts'))
            else:
                lines.append(line)
        return [200, "application/vnd.apple.mpegurl", '\n'.join(lines)]

    def tsProxy(self, url):
        return [200, 'video/mp2t', requests.get(self.d64(url), headers=self.headers, proxies=self.proxies).content]

    def e64(self, text):
        return b64encode(str(text).encode()).decode()

    def d64(self, text):
        return b64decode(str(text).encode()).decode()

    def aesimg(self, data):
        if len(data) < 16: return data
        # 保留原有的密钥，这是该站点特有的解密逻辑
        keys = [(b'f5d965df75336270', b'97b60394abc2fbe1'), (b'75336270f5d965df', b'abc2fbe197b60394')]
        for k, v in keys:
            try:
                dec = unpad(AES.new(k, AES.MODE_CBC, v).decrypt(data), 16)
                # 增加对常见图片头的检测
                if dec.startswith(b'\xff\xd8') or dec.startswith(b'\x89PNG') or dec.startswith(b'GIF8'): return dec
            except: pass
            try:
                dec = unpad(AES.new(k, AES.MODE_ECB).decrypt(data), 16)
                if dec.startswith(b'\xff\xd8'): return dec
            except: pass
        return data

    def getlist(self, data_pq, selector, tid=''):
        videos = []
        is_folder = '/mrdg' in (tid or '')
        
        items = data_pq(selector)
        # 如果默认选择器没找到，尝试宽泛搜索
        if len(items) == 0:
            items = data_pq('a:has(img)')
        
        seen_ids = set()
        ad_keywords = ['娱乐', '棋牌', '澳门', '葡京', '太阳城', '彩票', 'AV', '约炮', '直播', '发牌', '荷官', '备用', '导航', '回家', '路口', 'APP', '下载', '群', '充值']

        for k in items.items():
            if k.is_('a'):
                a = k
                container = k.parent() 
            else:
                a = k('a').eq(0)
                container = k

            href = a.attr('href')
            if not href: continue
            
            if any(x in href for x in ['/category/', '/tag/', '/feed/', '/page/', '/author/', 'gitlub', 'homeway', 'faq']):
                continue
            if href == '/' or href.strip() == '#': continue

            title = container.find('h2, h3, .title, .video-title').text()
            if not title: title = a.attr('title')
            if not title: title = a.find('img').attr('alt')
            if not title: title = a.text()
            
            if not title or len(title.strip()) < 2: continue
            if any(ad in title for ad in ad_keywords): continue

            card_html = k.outer_html() if hasattr(k, 'outer_html') else str(k)
            script_text = k('script').text() # 提取 script 内容用于查找图片变量
            
            # 传入 script 文本，确保 getimg 能优先匹配到 var img_url
            img = self.getimg(script_text, k, card_html)
            
            if not img: continue
            if '.gif' in img.lower(): continue 
            
            if href in seen_ids: continue
            
            # 补全 href
            if not href.startswith('http'):
                href = urljoin(self.host, href)
                
            seen_ids.add(href)

            remark = container.find('time, .date, .meta, .views, .video-duration').text() or ''

            videos.append({
                'vod_id': f"{href}{'@folder' if is_folder else ''}",
                'vod_name': title.strip(),
                'vod_pic': img,
                'vod_remarks': remark,
                'vod_tag': 'folder' if is_folder else '',
                'style': {"type": "rect", "ratio": 1.33}
            })
            
        return videos

    def getimg(self, text, elem=None, html_content=None):
        # 1. 优先匹配 script 中的 var img_url (吃瓜网特色)
        if m := re.search(r'var\s+img_url\s*=\s*[\'"]([^\'"]+)[\'"]', text or ''):
            return self._proc_url(m.group(1))
        
        # 2. 匹配 loadBannerDirect
        if m := re.search(r"loadBannerDirect\('([^']+)'", text or ''):
            return self._proc_url(m.group(1))
            
        if html_content is None and elem is not None:
             html_content = elem.outer_html() if hasattr(elem, 'outer_html') else str(elem)
        if not html_content: return ''

        html_content = html_content.replace('&quot;', '"').replace('&apos;', "'").replace('&amp;', '&')

        # 3. 匹配普通 src (排除 data:image 占位符)
        # 许多延迟加载使用 data-src 或 data-original
        if m := re.search(r'data-src\s*=\s*[\"\']([^\"\']+)[\"\']', html_content, re.I):
             return self._proc_url(m.group(1))
        if m := re.search(r'data-original\s*=\s*[\"\']([^\"\']+)[\"\']', html_content, re.I):
             return self._proc_url(m.group(1))

        # 4. 匹配 http 链接
        if m := re.search(r'(https?://[^"\'\s)]+\.(?:jpg|png|jpeg|webp))', html_content, re.I):
            return self._proc_url(m.group(1))

        if 'url(' in html_content:
            m = re.search(r'url\s*\(\s*[\'"]?([^"\'\)]+)[\'"]?\s*\)', html_content, re.I)
            if m: return self._proc_url(m.group(1))
            
        return ''

    def _proc_url(self, url):
        if not url: return ''
        url = url.strip('\'" ')
        if url.startswith('data:'):
            # 处理 data 协议
            try:
                _, b64_str = url.split(',', 1)
                raw = b64decode(b64_str)
                # 如果不是标准图片头，尝试 AES 解密
                if not (raw.startswith(b'\xff\xd8') or raw.startswith(b'\x89PNG') or raw.startswith(b'GIF8')):
                    raw = self.aesimg(raw)
                key = hashlib.md5(raw).hexdigest()
                img_cache[key] = raw
                return f"{self.getProxyUrl()}&type=cache&key={key}"
            except: return ""
            
        if not url.startswith('http'):
            url = urljoin(self.host, url)
        
        # 强制所有图片走代理进行解密 (修复点)
        return f"{self.getProxyUrl()}&url={self.e64(url)}&type=img"

    def getfod(self, id):
        return []

    def getpq(self, data):
        try: return pq(data)
        except: return pq(data.encode('utf-8'))
