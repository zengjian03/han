"""
@header({
  searchable: 1,
  filterable: 1,
  quickSearch: 1,
  title: '七猫小说',
  类型: '小说',
  logo: 'https://cdn-front.qimao.com/global/static/images/favicon2022.ico',
  lang: 'hipy'
})
"""

# coding=utf-8
# !/usr/bin/python

import sys

sys.path.append('..')

from base.spider import BaseSpider
import requests
from base.htmlParser import jsoup
import zlib
from typing import List
import base64
import json
from jinja2 import Environment, Template
import re
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import hashlib

TIMEOUT = 10


class Spider(BaseSpider):
    def getName(self):
        return "七猫小说"

    filterable = True
    searchable = True
    host = 'https://www.qimao.com'
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
    }
    sign_headers = {
        "app-version": "51110",
        "platform": "android",
        "reg": "0",
        "AUTHORIZATION": "",
        "application-id": "com.****.reader",
        "net-env": "1",
        "channel": "unknown",
        "qm-params": "",
        "sign": "fc697243ab534ebaf51d2fa80f251cb4"
    }

    def init(self, extend=""):
        print("============{0}============".format(extend))

    def getDependence(self):
        return []

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    @staticmethod
    def jinja_render(source: str, **context):
        # 构造环境
        env = Environment()
        template: Template = env.from_string(source)
        view = template.render(**context)
        return view

    def homeContent(self, filter):
        result = {}
        class_names = '全部&女生原创&男生原创&出版图书'.split('&')
        class_urls = 'a&1&0&2'.split('&')
        classes = []
        for i in range(len(class_names)):
            classes.append({
                'type_name': class_names[i],
                'type_id': class_urls[i]
            })
        result['class'] = classes
        result['type'] = '小说'
        result['filters'] = json.loads(self.ungzip(self.config['filter']))
        return result

    def homeVideoContent(self):
        result = {
            'list': []
        }
        return result

    def categoryContent(self, tid, pg, filter, extend):
        print('categoryContent:', tid, pg, filter, extend)
        filter_url = "{{fl.作品分类 or 'a'}}-a-{{fl.作品字数 or 'a'}}-{{fl.更新时间 or 'a'}}-a-{{fl.是否完结 or 'a'}}-{{fl.排序 or 'click'}}"
        api_url = f'{self.host}/shuku/fyclass-fyfilter-fypage/'
        url = api_url.replace('fyclass', str(tid)).replace('fyfilter', filter_url).replace('fypage', str(pg))
        url = self.jinja_render(url, fl=extend)
        url1 = "{{host}}/qimaoapi/api/classify/book-list?channel={{tid}}&category1={{fl.作品分类 or 'a'}}&category2=a&words={{fl.作品字数 or 'a'}}&update_time={{fl.更新时间 or 'a'}}&is_vip=a&is_over={{fl.是否完结 or 'a'}}&order={{fl.排序 or 'click'}}&page={{page}}"
        url1 = self.jinja_render(url1, fl=extend, host=self.host, tid=tid, page=pg)
        print('url:', url)
        print('url1:', url1)
        r = requests.get(url, headers=self.headers, timeout=TIMEOUT)
        html = r.text
        d = []
        jsp = jsoup(url)
        pdfh = jsp.pdfh
        pd = jsp.pdfh
        data = jsp.pdfa(html, 'ul.qm-cover-text&&li')
        # print(len(data))
        # if len(data) == 0:
        #     print(html)
        #     with open('public/1.html', 'w+', encoding='utf-8') as f:
        #         f.write(html)
        for it in data:
            d.append({
                "vod_name": pdfh(it, '.s-tit&&Text'),
                "vod_id": pd(it, 'a&&href'),
                "vod_remarks": pdfh(it, '.s-author&&Text'),
                "vod_pic": pd(it, 'img&&src'),
                "vod_content": pdfh(it, '.s-desc&&Text'),
            })
        try:
            r = requests.get(url1, headers=self.headers, timeout=TIMEOUT)
            json = r.json()
            book_list = json['data']['book_list']
            for book in d:
                book_extra = [x for x in book_list if x.get('read_url') == book['vod_id']]
                if len(book_extra) == 1:
                    book['vod_pic'] = book_extra[0].get('image_link') or book['vod_pic']
        except Exception:
            pass

        result = {}
        pagecount = 999  # 设置为1就只能1页不能翻页
        limit = 15  # 一页多少
        total = 999999
        result['list'] = d
        result['page'] = pg
        result['pagecount'] = pagecount
        result['limit'] = limit
        result['total'] = total
        return result

    def detailContent(self, ids):
        url = ids[0]
        r = requests.get(url, headers=self.headers, timeout=TIMEOUT)
        html = r.text
        jsp = jsoup(url)
        pdfh = jsp.pdfh
        pd = jsp.pd
        vod = {}
        vod['vod_name'] = pdfh(html, 'span.txt&&Text')
        vod['type_name'] = pdfh(html, '.qm-tag:eq(-1)&&Text')
        vod['vod_pic'] = pd(html, '.wrap-pic&&img&&src')
        vod['vod_content'] = pdfh(html, '.book-introduction-item&&.qm-with-title-tb&&Text')
        vod['vod_remarks'] = pdfh(html, '.qm-tag&&Text')
        vod['vod_year'] = ''
        vod['vod_area'] = ''
        vod['vod_actor'] = pdfh(html, '.sub-title&&span:eq(1)&&Text')
        vod['vod_director'] = pdfh(html, '.sub-title&&span&&a&&Text')
        vod['vod_play_from'] = pdfh(html, '.qm-sheader&&img&&alt')
        # print('vod:', vod)
        book_id = re.search(r'shuku/(\d+)', url).group(1) if re.search(r'shuku/(\d+)', url) else None
        chapter_url = 'https://www.qimao.com/api/book/chapter-list'
        # print('book_id:', book_id)
        chapter_url = self.buildUrl(chapter_url, {
            'book_id': book_id
        })
        r = requests.get(chapter_url, headers=self.headers, timeout=TIMEOUT)
        json = r.json()
        chapters = jsp.pjfa(json, 'data.chapters')
        # print('chapters:', chapters)
        lists = [[f'{it["title"]}${book_id}@@{it["id"]}@@{it["title"]}' for it in chapters]]
        vod['vod_play_url'] = '$$$'.join(['#'.join(ls) for ls in lists])
        result = {
            'list': [
                vod
            ]
        }
        return result

    def searchContent(self, key, quick, pg=1):
        url = 'https://api-bc.wtzw.com/search/v1/words'
        params = {
            'extend': '',
            'tab': '0',
            'gender': '0',
            'refresh_state': '8',
            'page': pg,
            'wd': key,
            'is_short_story_user': '0'
        }
        params['sign'] = self.get_sign_str(params)
        url = self.buildUrl(url, params)
        r = requests.get(url, headers=self.sign_headers, timeout=TIMEOUT)
        json = r.json()
        # print('json:', json)
        books = json['data']['books']
        d = [{
            'vod_name': book.get('original_title'),
            'vod_remarks': book.get('author'),
            'vod_pic': book.get('image_link'),
            'vod_id': f'https://www.qimao.com/shuku/{book["id"]}/',
        } for book in books if book.get('show_type') == '0']
        result = {
            'list': d
        }
        return result

    def playerContent(self, flag, id, vipFlags):
        params = {
            'id': id.split('@@')[0],
            'chapterId': id.split('@@')[1],
        }
        params['sign'] = self.get_sign_str(params)
        url = 'https://api-ks.wtzw.com/api/v1/chapter/content'
        url = self.buildUrl(url, params)
        title = id.split('@@')[2]
        r = requests.get(url, headers=self.sign_headers, timeout=TIMEOUT)
        json_str = r.json()
        result = json_str['data']['content']
        content = self.decode_content(result)
        ret = json.dumps({
            'title': title,
            'content': content,
        }, ensure_ascii=False)

        result = {}
        parse = 0
        url = 'novel://' + ret
        result["parse"] = parse  # 0=直接播放、1=嗅探
        result["playUrl"] = ''
        result["url"] = url
        # result['jx'] = 0  # VIP解析,0=不解析、1=解析
        result["header"] = ''
        return result

    config = {
        "player": {},
        "filter": "H4sIAAAAAAAAAO1W3U4aQRR+l72GZF1EGh+iL9AYs1GaEBUbKzSNIaEgLFDKlqJujURLCohpEaTErrtFXmZ+lrfoALszO3BRbrig2ZtN9vvOzPmZ+c6ZE0EUNl+dCHvh98KmAAZVWPkAc1n8YAo+ISofhOfRuLwfC08WRQkJM61RujWGyY8sJHw2XMpCtWfDwQ2GZ6+A8dHGN0SK49syfDIdfJ3iSNdRTrXxUJDZl06JPWwobJUkSpQepQdQTwHDwGc3lA6wKBrKSDPhnxSLRRJdTttN8PwNmJfkS2nmGwwqVqpHCZbcS/SzBjNpyoSExNaY44rb1tB5d664DrpQcQMi0BVgNoDuRL/Gc/7g+OvEQbkJ6l8TXSSryRT2S26WlWQKT3wWnFPlskNXfXTRRdrjSOuz7GbQxbKD9TuYzcxlFuJwyZUxRwT4sL524OcmvC9is+IKi0cXu9G/e2wBF5g1vLYGA6C3bUbkIyh9gYbq8u38815RMY9TT1AxR4pz3Xf2Izt77FIW8yhpsotCoHeHR7tvt6OxA2ZUTVrD8rTqtlHsza58HN4+jhDv7r3OHi1NZXu9luOHRxFiGIuPw9/ykQSX0RhwqQvM71YridLzRwzV+izJzpkoHaV/ceRsn8A/rlEhSfXH2otV+0Q6Ab9xyJOnJ8/Vlae0FHmiCwW2m1beQNWOc5TrTEdkohILXH8m85rSrNTYVPF9DRYe4FCjtOSmYUafuqC0ayorBs7nYFe1On2HDoYY3S3D0yE6v3QN3+ALT8OehldWw/IqjdhlP+n/McJX5cW/uo3Ueyt5ffZ/7LOJv/U9eHXlEAAA",
    }
    header = {}

    def localProxy(self, params):
        return [200, "video/MP2T", ""]

    @staticmethod
    def ungzip(b64_data: str) -> str:
        """
        解码 base64 字符串，进行 gzip 解压缩，并返回 UTF-8 字符串

        Args:
            b64_data: base64 编码的压缩数据

        Returns:
            解压缩后的 UTF-8 字符串
        """
        try:
            # 解码 base64 字符串
            compressed_data = base64.b64decode(b64_data)

            # 使用 zlib 进行 gzip 解压缩
            # wbits 参数设置为 15+32 表示自动检测 gzip 头部
            decompressed_data = zlib.decompress(compressed_data, zlib.MAX_WBITS | 32)

            # 将字节数据解码为 UTF-8 字符串
            return decompressed_data.decode('utf-8')

        except Exception as e:
            raise ValueError(f"解压缩过程中出错: {str(e)}")

    # 辅助函数：将字节数组转换为 UTF-8 字符串（如果需要）
    @staticmethod
    def utf8_array_to_str(data: List[int]) -> str:
        """将整数列表（字节值）转换为 UTF-8 字符串"""
        byte_array = bytes(data)
        return byte_array.decode('utf-8')

    @staticmethod
    def get_sign_str(params):
        # d3dGiJc651gSQ8w1
        sign_key = "d3dGiJc651gSQ8w1"

        # 对参数键进行排序
        keys = sorted(params.keys())

        # 构建签名字符串
        sign_str = ""
        for key in keys:
            sign_str += f"{key}={params[key]}"
        sign_str += sign_key

        # 计算 MD5 哈希值
        md5_hash = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
        return md5_hash

    @staticmethod
    def novel_content_decrypt(data, iv):
        # 将密钥从十六进制字符串转换为字节
        key_hex = "32343263636238323330643730396531"
        key = bytes.fromhex(key_hex)

        # 将 IV 从十六进制字符串转换为字节
        iv_bytes = bytes.fromhex(iv)

        # 将数据从十六进制字符串转换为字节
        data_bytes = bytes.fromhex(data)

        # 创建 AES 解密器
        cipher = AES.new(key, AES.MODE_CBC, iv_bytes)

        # 解密数据
        decrypted = cipher.decrypt(data_bytes)

        # 移除 PKCS7 填充
        try:
            unpadded = unpad(decrypted, AES.block_size)
        except ValueError:
            # 如果填充不正确，可能已经是未填充的数据
            unpadded = decrypted

        # 转换为 UTF-8 字符串
        return unpadded.decode('utf-8').strip()

    def decode_content(self, response):
        # 解码 Base64 响应
        decoded_bytes = base64.b64decode(response)

        # 转换为字符串（十六进制表示）
        hex_str = decoded_bytes.hex()

        # 提取前 32 个字符作为 IV
        iv = hex_str[:32]

        # 提取剩余部分作为内容
        content_hex = hex_str[32:]

        # 解密内容
        decrypted_content = self.novel_content_decrypt(content_hex, iv)

        return decrypted_content
