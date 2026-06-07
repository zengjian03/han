"""
@header({
  searchable: 0,
  filterable: 0,
  quickSearch: 0,
  title: '动作代理测试',
  lang: 'hipy'
})
"""

# coding=utf-8
# !/usr/bin/python
import json
import sys
import time

sys.path.append('..')
try:
    from base.spider import BaseSpider
except ImportError:
    from t4.base.spider import BaseSpider


class Spider(BaseSpider):
    def getName(self):
        return "动作代理测试"

    filterate = False

    def init(self, extend=""):
        print("============{0}============".format(extend))

    def getDependence(self):
        return []

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def homeContent(self, filter):
        return {
            'class': [],
            'type_flag': '3-00-S'
        }

    def homeVideoContent(self):
        print('homeVod...')
        videos = [{
            "vod_id": json.dumps({
                'actionId': '代理地址',
                'id': 'proxy_url',
                'type': 'input',
                'title': '直接用的代理m3u链接',
                'tip': '..',
                'value': self.getProxyUrl() + '&flag=live'
            }, ensure_ascii=False),
            'vod_pic': 'clan://assets/tab.png?bgcolor=0',
            'vod_name': '复制代理地址',
            'vod_tag': 'action'
        }]

        return {
            'list': videos
        }

    def categoryContent(self, tid, pg, filter, extend):
        print('categoryContent:', tid, pg, filter, extend)
        return {}

    def detailContent(self, array):
        vod = {}
        result = {
            'list': [
                vod
            ]
        }
        return result

    def searchContent(self, key, quick, pg=1):
        videos = []
        result = {
            'list': videos
        }
        return result

    def playerContent(self, flag, id, vipFlags):
        result = {}
        parse = 1
        url = id
        result["parse"] = parse  # 0=直接播放、1=嗅探
        result["playUrl"] = ''
        result["url"] = url
        result['jx'] = 0  # VIP解析,0=不解析、1=解析
        result["header"] = ''
        return result

    config = {
        "player": {},
        "filter": {}
    }
    header = {}

    def localProxy(self, params):
        return [404, 'text/plain', 'localProxy response with 404 not found']

    def action(self, action, value):
        if action == '代理地址':
            json_dict = json.loads(value)
            return {
                'action': {
                    'actionId': '__copy__',
                    'content': json_dict.get('proxy_url', '')
                },

                'toast': '直播源已复制到剪贴板',
            }
