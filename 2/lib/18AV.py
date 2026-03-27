# coding=utf-8
# !/usr/bin/python

"""

 🚓 内容均从互联网收集而来 仅供交流学习使用 版权归原创者所有 如侵犯了您的权益 请通知作者 将及时删除侵权内容
                    ====================Diudiumiao====================

"""

from Crypto.Util.Padding import unpad
from Crypto.Util.Padding import pad
from urllib.parse import unquote
from Crypto.Cipher import ARC4
from urllib.parse import quote
from base.spider import Spider
from Crypto.Cipher import AES
from datetime import datetime
from bs4 import BeautifulSoup
from base64 import b64decode
import urllib.request
import urllib.parse
import datetime
import binascii
import requests
import base64
import json
import time
import sys
import re
import os

sys.path.append('..')

headerx = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36'
          }

class Spider(Spider):

    def getName(self):
        return "丢丢喵"

    def init(self, extend):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def extract_middle_text(self, text, start_str, end_str, pl, start_index1: str = '', end_index2: str = ''):
        if pl == 3:
            plx = []
            while True:
                start_index = text.find(start_str)
                if start_index == -1:
                    break
                end_index = text.find(end_str, start_index + len(start_str))
                if end_index == -1:
                    break
                middle_text = text[start_index + len(start_str):end_index]
                plx.append(middle_text)
                text = text.replace(start_str + middle_text + end_str, '')
            if len(plx) > 0:
                purl = ''
                for i in range(len(plx)):
                    matches = re.findall(start_index1, plx[i])
                    output = ""
                    for match in matches:
                        match3 = re.search(r'(?:^|[^0-9])(\d+)(?:[^0-9]|$)', match[1])
                        if match3:
                            number = match3.group(1)
                        else:
                            number = 0
                        if 'http' not in match[0]:
                            output += f"#{match[1]}${number}{xurl}{match[0]}"
                        else:
                            output += f"#{match[1]}${number}{match[0]}"
                    output = output[1:]
                    purl = purl + output + "$$$"
                purl = purl[:-3]
                return purl
            else:
                return ""
        else:
            start_index = text.find(start_str)
            if start_index == -1:
                return ""
            end_index = text.find(end_str, start_index + len(start_str))
            if end_index == -1:
                return ""

        if pl == 0:
            middle_text = text[start_index + len(start_str):end_index]
            return middle_text.replace("\\", "")

        if pl == 1:
            middle_text = text[start_index + len(start_str):end_index]
            matches = re.findall(start_index1, middle_text)
            if matches:
                jg = ' '.join(matches)
                return jg

        if pl == 2:
            middle_text = text[start_index + len(start_str):end_index]
            matches = re.findall(start_index1, middle_text)
            if matches:
                new_list = [f'{item}' for item in matches]
                jg = '$$$'.join(new_list)
                return jg

    def fetch_html_go_url(self):
        try:
            detail = requests.get(url="https://ganb.18oaoaoa5m.cc/%E8%B0%83%E7%A0%94%E8%B5%84%E6%96%99/%E6%8A%A5%E5%91%8A.html",headers=headerx,timeout=10)
            detail.raise_for_status()
            detail.encoding = "utf-8"
            res = detail.text
            return self._parse_html_go_url(res)
        except requests.RequestException as e:
            raise ValueError(f"网络请求失败: {e}")
        except Exception as e:
            raise ValueError(f"解析URL失败: {e}")

    def _parse_html_go_url(self, html_content):
        sub_str_match = re.search(r'var\s+sub_str\s*=\s*"([^"]+)"', html_content)
        tdn_str_match = re.search(r'var\s+tdn_str\s*=\s*"([^"]+)"', html_content)
        qpon_match = re.search(r"html_go\s*\+=\s*'(\.[^']+)';", html_content)
        oaoaoa_match = re.search(r"html_go\s*\+=\s*'(/[^'/]+/)';", html_content)
        if not sub_str_match or not tdn_str_match:
            raise ValueError("无法解析页面中的关键变量")
        sub_str = sub_str_match.group(1)
        tdn_str = tdn_str_match.group(1)
        qpon_suffix = qpon_match.group(1) if qpon_match else ''
        oaoaoa_path = oaoaoa_match.group(1) if oaoaoa_match else ''
        html_go = f"https://{sub_str}.{tdn_str}{qpon_suffix}{oaoaoa_path}"
        return html_go

    def homeContent(self, filter):
        try:
            html_go = self.fetch_html_go_url()
            result = {"class": []}
            detail = requests.get(url=html_go, headers=headerx, timeout=10)
            detail.raise_for_status()
            detail.encoding = "utf-8"
            res = detail.text
            return self._parse_home_content(res)
        except requests.RequestException as e:
            raise ValueError(f"网络请求失败: {e}")
        except Exception as e:
            raise ValueError(f"解析首页内容失败: {e}")

    def _parse_home_content(self, html_content):
        result = {"class": []}
        doc = BeautifulSoup(html_content, "lxml")
        soups = doc.find('div', class_="wn_keyword_wrapper")
        if not soups:
            raise ValueError("未找到关键词包装器")
        vods = soups.find_all('a')
        for vod in vods:
            name = vod.text.strip()
            if name:
                result["class"].append({"type_id": name, "type_name": "精彩🌠" + name})
        return result

    def homeVideoContent(self):
        pass

    def categoryContent(self, cid, pg, filter, ext):
        try:
            page = int(pg) if pg else 1
            html_go = self.fetch_html_go_url()
            url = self._build_category_url(html_go, cid, page)
            detail = requests.get(url=url, headers=headerx, timeout=10)
            detail.raise_for_status()
            detail.encoding = "utf-8"
            res = detail.text
            videos = self._parse_category_videos(res)
            result = {
                'list': videos,
                'page': pg,
                'pagecount': 9999,
                'limit': 90,
                'total': 999999
                     }
            return result
        except requests.RequestException as e:
            raise ValueError(f"网络请求失败: {e}")
        except Exception as e:
            raise ValueError(f"解析分类内容失败: {e}")

    def _build_category_url(self, base_url, category_id, page):
        fenge = base_url.split("/")
        return f'https://{fenge[2]}/vodsearch/{category_id}----------{str(page)}---/'

    def _parse_category_videos(self, html_content):
        videos = []
        doc = BeautifulSoup(html_content, "lxml")
        soups = doc.find_all('ul', class_="thumbnail-group")
        for soup in soups:
            vods = soup.find_all('li')
            for vod in vods:
                try:
                    video = self._parse_single_video(vod)
                    if video:
                        videos.append(video)
                except Exception:
                    continue
        return videos

    def _parse_single_video(self, vod_element):
        try:
            name = vod_element.find('img')['alt']
            ids = vod_element.find('div', class_="video-info")
            id = ids.find('a')['href']
            pic = vod_element.find('img')['src']
            remarks = vod_element.find('span', class_="type-badge")
            remark = remarks.text.strip() if remarks else ""
            return {
                "vod_id": id,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": remark
                   }
        except (KeyError, AttributeError):
            return None

    def detailContent(self, ids):
        try:
            did = ids[0]
            html_go = self.fetch_html_go_url()
            fenge = html_go.split("/")
            detail = requests.get(url=f"https://{fenge[2]}{did}",headers=headerx,timeout=10)
            detail.raise_for_status()
            detail.encoding = "utf-8"
            res = detail.text
            videos = self._parse_detail_videos(res, did, fenge[2])
            result = {'list': videos}
            return result
        except requests.RequestException as e:
            raise ValueError(f"网络请求失败: {e}")
        except Exception as e:
            raise ValueError(f"解析详情内容失败: {e}")

    def _parse_detail_videos(self, html_content, did, domain):
        videos = []
        doc = BeautifulSoup(html_content, "lxml")
        play_span = doc.find('span', class_='wn_block_link_item_name',string=lambda text: text and '在线播放' in text)
        if play_span:
            parent_a = play_span.parent
            if parent_a.name == 'a':
                href_value = parent_a.get('href')
                if href_value:
                    videos.append({
                        "vod_id": did,
                        "vod_play_from": "精彩专线",
                        "vod_play_url": f"https://{domain}{href_value}"
                                 })
        return videos

    def playerContent(self, flag, id, vipFlags):
        try:
            detail = requests.get(url=id, headers=headerx, timeout=10)
            detail.raise_for_status()
            detail.encoding = "utf-8"
            res = detail.text
            url = self._extract_video_url(res)
            result = {
                "parse": 0,
                "playUrl": '',
                "url": url,
                "header": headerx
                     }
            return result
        except requests.RequestException as e:
            raise ValueError(f"网络请求失败: {e}")
        except Exception as e:
            raise ValueError(f"解析播放内容失败: {e}")

    def _extract_video_url(self, html_content):
        url = self.extract_middle_text(html_content, '"","url":"', '"', 0)
        return url.replace('\\', '')

    def searchContentPage(self, key, quick, pg):
        try:
            page = int(pg) if pg else 1
            html_go = self.fetch_html_go_url()
            url = self._build_search_url(html_go, key, page)
            detail = requests.get(url=url, headers=headerx, timeout=10)
            detail.raise_for_status()
            detail.encoding = "utf-8"
            res = detail.text
            videos = self._parse_search_videos(res)
            result = {
                'list': videos,
                'page': pg,
                'pagecount': 9999,
                'limit': 90,
                'total': 999999
                     }
            return result
        except requests.RequestException as e:
            raise ValueError(f"网络请求失败: {e}")
        except Exception as e:
            raise ValueError(f"解析搜索内容失败: {e}")

    def _build_search_url(self, base_url, key, page):
        fenge = base_url.split("/")
        return f'https://{fenge[2]}/vodsearch/{key}----------{str(page)}---/'

    def _parse_search_videos(self, html_content):
        videos = []
        doc = BeautifulSoup(html_content, "lxml")
        soups = doc.find_all('ul', class_="thumbnail-group")
        for soup in soups:
            vods = soup.find_all('li')
            for vod in vods:
                try:
                    video = self._parse_single_video(vod)
                    if video:
                        videos.append(video)
                except Exception:
                    continue
        return videos

    def _parse_single_video(self, vod_element):
        try:
            name = vod_element.find('img')['alt']
            ids = vod_element.find('div', class_="video-info")
            id = ids.find('a')['href']
            pic = vod_element.find('img')['src']
            remarks = vod_element.find('span', class_="type-badge")
            remark = remarks.text.strip() if remarks else ""
            return {
                "vod_id": id,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": remark
                   }
        except (KeyError, AttributeError):
            return None

    def searchContent(self, key, quick, pg="1"):
        return self.searchContentPage(key, quick, '1')

    def localProxy(self, params):
        if params['type'] == "m3u8":
            return self.proxyM3u8(params)
        elif params['type'] == "media":
            return self.proxyMedia(params)
        elif params['type'] == "ts":
            return self.proxyTs(params)
        return None










