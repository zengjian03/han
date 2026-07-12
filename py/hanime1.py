# coding=utf-8
# hanime1.py —— TVBox / FongMi Python 爬虫
import re
import sys
import urllib.parse

sys.path.append('..')
from base.spider import Spider


class Spider(Spider):
    host = 'https://hanime1.me'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Referer': 'https://hanime1.me/',
        'Accept-Language': 'zh-TW,zh;q=0.9,zh-CN;q=0.8',
    }

    # (显示名-简体, type_id)
    # type_id 以 "sort:" 开头的表示用排序方式请求，其余直接当 genre 参数
    cates = [
        ('最新上市', 'sort:最新上市'),
        ('最新上传', 'sort:最新上傳'),
        ('里番', '裏番'),
        ('泡面番', '泡麵番'),
        ('Motion Anime', 'Motion Anime'),
        ('3DCG', '3DCG'),
        ('2.5D', '2.5D'),
        ('2D动画', '2D動畫'),
        ('AI生成', 'AI生成'),
        ('MMD', 'MMD'),
        ('Cosplay', 'Cosplay'),
        ('新番预告', '新番預告'),
    ]

    sorts = [
        {'n': '最新上市', 'v': '最新上市'},
        {'n': '最新上传', 'v': '最新上傳'},
        {'n': '本日排行', 'v': '本日排行'},
        {'n': '本周排行', 'v': '本週排行'},
        {'n': '本月排行', 'v': '本月排行'},
    ]

    # ---------- 基础 ----------
    def getName(self):
        return 'hanime1'

    def init(self, extend=''):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    def localProxy(self, param):
        return None

    def _get(self, url):
        try:
            return self.fetch(url, headers=self.headers, timeout=15).text
        except Exception:
            import requests
            return requests.get(url, headers=self.headers, timeout=15).text

    def _meta(self, html, prop):
        m = re.search(r'<meta[^>]+property="%s"[^>]+content="([^"]*)"' % prop, html)
        if not m:
            m = re.search(r'<meta[^>]+content="([^"]*)"[^>]+property="%s"' % prop, html)
        return m.group(1).strip() if m else ''

    # ---------- 列表解析（重写：以卡片块为单位整体提取，避免 vid 与标题错位） ----------
    def parse_list(self, html):
        videos = []
        seen = set()

        # 策略1：匹配完整卡片块 <div class="..."> ... </div>
        # hanime1 的视频卡片通常带有 home-rows-videos__video 或 search-doujin-videos 等 class
        # 用 <a href="/watch?v=vid"> 作为卡片锚点，向后截取到下一个卡片或页面结束
        card_pattern = re.compile(
            r'<a[^>]+href=["\'](?:https?://hanime1\.me)?/watch\?v=(\d+)["\'][^>]*>(.*?)</a>',
            re.S
        )

        for m in card_pattern.finditer(html):
            vid = m.group(1)
            if vid in seen:
                continue
            inner = m.group(2)  # <a> 标签内部 HTML

            # 从 inner 里提取标题
            title = ''
            # 优先找 class 含 title 的标签
            t = re.search(
                r'class="[^"]*(?:title|name)[^"]*"[^>]*>\s*([^<]+?)\s*<',
                inner, re.S
            )
            if t:
                title = t.group(1).strip()
            # 其次找 <img alt="...">
            if not title:
                t = re.search(r'<img[^>]+alt="([^"]+)"', inner)
                if t:
                    title = t.group(1).strip()
            # 再找 <a title="..."> 自身属性
            if not title:
                t = re.search(r'title="([^"]+)"', m.group(0))
                if t:
                    title = t.group(1).strip()

            if not title:
                continue

            # 从 inner 里提取封面
            pic = ''
            for img in re.findall(
                r'<img[^>]+(?:data-src|src)="(http[^"]+)"', inner
            ):
                if '.gif' in img or 'icon' in img or 'avatar' in img:
                    continue
                pic = img
                break

            seen.add(vid)
            videos.append({
                'vod_id': vid,
                'vod_name': title,
                'vod_pic': pic,
                'vod_remarks': ''
            })

        # 策略2：如果策略1一无所获（页面结构不同），退回旧逻辑但加强去重
        if not videos:
            videos = self._parse_list_fallback(html)

        return videos

    def _parse_list_fallback(self, html):
        """按 watch?v=vid 顺序匹配，但从 <a> 标签自身属性/紧邻文本取标题，避免串位"""
        videos = []
        seen = set()
        # 匹配 <a href="...watch?v=vid" title="标题"> 或 <a href="...watch?v=vid">标题</a>
        for m in re.finditer(
            r'<a[^>]+href=["\'][^"\']*watch\?v=(\d+)["\']([^>]*)>(.*?)</a>',
            html, re.S
        ):
            vid = m.group(1)
            if vid in seen:
                continue
            attrs = m.group(2)
            inner = m.group(3)

            # 先从 title 属性取
            t = re.search(r'title="([^"]+)"', attrs)
            title = t.group(1).strip() if t else ''
            # 再从内部文本取（去掉子标签）
            if not title:
                title = re.sub(r'<[^>]+>', '', inner).strip()
            if not title:
                continue

            seen.add(vid)
            videos.append({
                'vod_id': vid,
                'vod_name': title,
                'vod_pic': '',
                'vod_remarks': ''
            })
        return videos

    # ---------- 首页 ----------
    def homeContent(self, filter):
        classes = [{'type_name': n, 'type_id': v} for n, v in self.cates]
        filters = {}
        for _, v in self.cates:
            if not v.startswith('sort:'):
                filters[v] = [{'key': 'sort', 'name': '排序', 'value': self.sorts}]
        return {'class': classes, 'filters': filters}

    def homeVideoContent(self):
        html = self._get(self.host)
        return {'list': self.parse_list(html)[:30]}

    # ---------- 分类 ----------
    def categoryContent(self, tid, pg, filter, extend):
        if tid.startswith('sort:'):
            sort_val = tid[len('sort:'):]
            url = '{}/search?sort={}&page={}'.format(
                self.host, urllib.parse.quote(sort_val), pg)
        else:
            url = '{}/search?genre={}&page={}'.format(
                self.host, urllib.parse.quote(tid), pg)
            if extend and extend.get('sort'):
                url += '&sort=' + urllib.parse.quote(extend['sort'])

        html = self._get(url)
        videos = self.parse_list(html)
        return {
            'list': videos,
            'page': int(pg),
            'pagecount': int(pg) + (1 if len(videos) >= 20 else 0),
            'limit': 30,
            'total': 999999
        }

    # ---------- 详情 ----------
    def detailContent(self, ids):
        vid = ids[0]
        html = self._get('{}/watch?v={}'.format(self.host, vid))
        vod = {
            'vod_id': vid,
            'vod_name': self._meta(html, 'og:title'),
            'vod_pic': self._meta(html, 'og:image'),
            'vod_content': self._meta(html, 'og:description'),
            'vod_play_from': 'Hanime1',
            'vod_play_url': '播放$' + vid
        }
        return {'list': [vod]}

    # ---------- 搜索 ----------
    def searchContent(self, key, quick, pg='1'):
        url = '{}/search?query={}&page={}'.format(
            self.host, urllib.parse.quote(key), pg)
        html = self._get(url)
        return {'list': self.parse_list(html), 'page': int(pg)}

    # ---------- 播放 ----------
    def playerContent(self, flag, id, vipFlags):
        html = self._get('{}/watch?v={}'.format(self.host, id))
        play = ''
        sources = re.findall(r'<source[^>]+src="([^"]+)"[^>]*size="(\d+)"', html)
        if sources:
            sources.sort(key=lambda x: int(x[1]), reverse=True)
            play = sources[0][0]
        if not play:
            m = re.search(r'"contentUrl"\s*:\s*"([^"]+)"', html)
            if m:
                play = m.group(1).replace('\\/', '/')
        if not play:
            m = re.search(r'(https?://[^\s\'"]+\.(?:m3u8|mp4)[^\s\'"]*)', html)
            if m:
                play = m.group(1)
        return {
            'parse': 0 if play else 1,
            'url': play or '{}/watch?v={}'.format(self.host, id),
            'header': self.headers
        }