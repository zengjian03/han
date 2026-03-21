# -*- coding: utf-8 -*-
import sys
import re
import requests
from pyquery import PyQuery as pq

sys.path.append('..')
from base.spider import Spider


class Spider(Spider):

    UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    # ================= 基础 =================

    def getName(self):
        return "聚合色播"

    def init(self, extend=""):
        self.kbj_home = "https://kbj.im"
        self.sebo_api = "http://api.hclyz.com:81/mf"

    # ================= 首页 =================

    def homeContent(self, filter):
        return {
            "class": [
                {"type_name": "Korean BJ", "type_id": "kbj"},
                {"type_name": "Sebo MF", "type_id": "sebo"}
            ]
        }

    def homeVideoContent(self):
        return self.kbj_category(1)

    # ================= 分类 =================

    def categoryContent(self, tid, pg, filter, extend):
        pg = int(pg)
        if tid == "kbj":
            return self.kbj_category(pg)
        if tid == "sebo":
            return self.sebo_category(pg)
        return {"list": []}

    # ================= Korean BJ =================

    def kbj_category(self, pg):
        if pg <= 1:
            url = self.kbj_home + "/"
        else:
            url = self.kbj_home + f"/?page={pg}"
        return self.kbj_videos(url, pg)

    def kbj_videos(self, url, pg):
        rsp = self._fetch(url)
        d = pq(rsp.text)
        videos = []

        for item in d('div.grid > div').items():
            link = item('a[href*="/posts/"]').eq(0)
            title = item('h2').text().strip()
            if not link or not title:
                continue

            videos.append({
                "vod_id": "kbj_" + link.attr('href').split('/')[-1],
                "vod_name": title,
                "vod_pic": item('img').attr('src'),
                "vod_remarks": item('time').text().strip()
            })

        # ===== 核心修复：通过 Pagination 计算总页数 =====
        pagecount = pg
        pagination = d('nav[aria-label="Pagination Navigation"]')

        if pagination:
            max_p = pg
            for a in pagination('a[href*="page="]').items():
                href = a.attr('href')
                m = re.search(r'page=(\d+)', href)
                if m:
                    p = int(m.group(1))
                    if p > max_p:
                        max_p = p
            pagecount = max_p
        else:
            # 没分页但内容不少，保守给下一页
            if len(videos) >= 12:
                pagecount = pg + 1

        return {
            "list": videos,
            "page": pg,
            "pagecount": pagecount,
            "limit": len(videos),
            "total": 999
        }

    def kbj_detail(self, tid):
        url = self.kbj_home + "/posts/" + tid
        root = pq(self._fetch(url).text)

        vod = {
            "vod_id": tid,
            "vod_name": root('h1').text().strip(),
            "vod_pic": root('meta[property="og:image"]').attr('content'),
            "vod_remarks": root('time').attr('datetime') or "",
            "type_name": "Korean BJ"
        }

        play_from = []
        play_urls = []

        for btn in root('button[data-url]').items():
            name = btn.attr('data-server') or btn.text().strip() or "线路"
            purl = btn.attr('data-url')
            if purl:
                play_from.append(name)
                play_urls.append(f"播放${purl}")

        if play_from:
            vod['vod_play_from'] = "$$$".join(play_from)
            vod['vod_play_url'] = "$$$".join(play_urls)
        else:
            iframe = root('iframe').attr('src')
            if iframe:
                vod['vod_play_from'] = "默认"
                vod['vod_play_url'] = f"正片${iframe}"

        return {"list": [vod]}

    # ================= 色播聚合 =================

    def sebo_category(self, pg):
        home = self.fetch(f'{self.sebo_api}/json.txt').json()
        data = home.get("pingtai", [])[1:]

        videos = [{
            "vod_id": "sebo_" + item['address'],
            "vod_name": item['title'],
            "vod_pic": item['xinimg'],
            "vod_remarks": item['Number'],
            "style": {"type": "rect", "ratio": 0.68}
        } for item in sorted(data, key=lambda x: int(x['Number']), reverse=True)]

        return {
            "page": 1,
            "pagecount": 1,
            "limit": len(videos),
            "total": len(videos),
            "list": videos
        }

    def sebo_detail(self, sid):
        data = self.fetch(f'{self.sebo_api}/{sid}').json()
        zhubo = data.get('zhubo', [])

        playUrls = '#'.join([
            f"{v['title']}${v['address']}" for v in zhubo
        ])

        return {
            "list": [{
                "vod_play_from": "sebo",
                "vod_play_url": playUrls,
                "vod_content": ""
            }]
        }

    # ================= 详情分流 =================

    def detailContent(self, array):
        vid = array[0]

        if vid.startswith("kbj_"):
            return self.kbj_detail(vid.replace("kbj_", ""))

        if vid.startswith("sebo_"):
            return self.sebo_detail(vid.replace("sebo_", ""))

        return {"list": []}

    # ================= 播放 =================

    def playerContent(self, flag, id, vipFlags):
        if flag == "sebo":
            return {
                "parse": 0,
                "url": id
            }

        return {
            "parse": 1,
            "url": id,
            "header": {
                "User-Agent": self.UA,
                "Referer": self.kbj_home + "/",
                "Origin": self.kbj_home
            }
        }

    # ================= 请求 =================

    def _fetch(self, url, **kwargs):
        return requests.get(
            url,
            timeout=10,
            verify=False,
            headers={"User-Agent": self.UA},
            **kwargs
        )