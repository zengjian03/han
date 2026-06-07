
import requests
from urllib.parse import urljoin, quote
import re
import json

class Spider:
    # 站点基础配置
    site_name = "A123TV"
    site_url = "https://a123tv.com"
    header = {
        "User-Agent": "Mozilla/5.0",
        "Referer": site_url
    }
    
    # 分类映射表：页面分类名 -> (分类ID, 扩展参数)
    category_map = {
        # 电影
        "电影": ("movie", "电影"),
        "动作片": ("movie", "动作片"),
        "喜剧片": ("movie", "喜剧片"),
        "爱情片": ("movie", "爱情片"),
        "科幻片": ("movie", "科幻片"),
        "恐怖片": ("movie", "恐怖片"),
        "剧情片": ("movie", "剧情片"),
        "战争片": ("movie", "战争片"),
        "纪录片": ("movie", "纪录片"),
        "动漫电影": ("movie", "动漫电影"),
        "奇幻片": ("movie", "奇幻片"),
        "动画片": ("movie", "动画片"),
        "犯罪片": ("movie", "犯罪片"),
        "悬疑片": ("movie", "悬疑片"),
        "邵氏电影": ("movie", "邵氏电影"),
        "歌舞片": ("movie", "歌舞片"),
        "家庭片": ("movie", "家庭片"),
        "古装片": ("movie", "古装片"),
        "历史片": ("movie", "历史片"),
        "4K电影": ("movie", "4K电影"),
        # 连续剧
        "连续剧": ("tv", "连续剧"),
        "国产剧": ("tv", "国产剧"),
        "香港剧": ("tv", "香港剧"),
        "台湾剧": ("tv", "台湾剧"),
        "韩国剧": ("tv", "韩国剧"),
        "欧美剧": ("tv", "欧美剧"),
        "日本剧": ("tv", "日本剧"),
        "泰国剧": ("tv", "泰国剧"),
        "港台剧": ("tv", "港台剧"),
        "日韩剧": ("tv", "日韩剧"),
        "海外剧": ("tv", "海外剧"),
        # 综艺
        "综艺": ("variety", "综艺"),
        "内地综艺": ("variety", "内地综艺"),
        "港台综艺": ("variety", "港台综艺"),
        "日韩综艺": ("variety", "日韩综艺"),
        "欧美综艺": ("variety", "欧美综艺"),
        "国外综艺": ("variety", "国外综艺"),
        # 动漫
        "动漫": ("anime", "动漫"),
        "国产动漫": ("anime", "国产动漫"),
        "日韩动漫": ("anime", "日韩动漫"),
        "欧美动漫": ("anime", "欧美动漫"),
        "海外动漫": ("anime", "海外动漫"),
        # 福利
        "福利": ("special", "福利"),
        "韩国情色片": ("special", "韩国情色片"),
        "日本情色片": ("special", "日本情色片"),
        "大陆情色片": ("special", "大陆情色片"),
        "香港情色片": ("special", "香港情色片"),
        "台湾情色片": ("special", "台湾情色片"),
        "美国情色片": ("special", "美国情色片"),
        "欧洲情色片": ("special", "欧洲情色片"),
        "印度情色片": ("special", "印度情色片"),
        "东南亚情色片": ("special", "东南亚情色片"),
        "其它情色片": ("special", "其它情色片"),
    }

    def _request(self, url):
        """发送网络请求"""
        try:
            response = requests.get(url, headers=self.header, timeout=10)
            response.encoding = 'utf-8'
            return response.text
        except Exception as e:
            print(f"请求失败: {url}, 错误: {e}")
            return ""

    def _get_categories(self):
        """获取所有分类结构"""
        cats = []
        main_cats = ["电影", "连续剧", "综艺", "动漫", "福利"]
        for main_cat in main_cats:
            cat_id = self.category_map[main_cat][0]
            cats.append({
                "type_id": cat_id,
                "type_name": main_cat,
                "type_flag": "1" if main_cat == "福利" else "0"
            })
        return cats

    # 核心接口 1: 首页内容
    def homeContent(self, filter):
        result = {
            "class": self._get_categories(),
            "list": []
        }
        html = self._request(self.site_url)
        # 使用正则匹配首页所有视频卡片：标题、封面、链接
        pattern = r'<a[^>]*href="([^"]*)"[^>]*>.*?<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"[^>]*>'
        matches = re.findall(pattern, html, re.DOTALL)
        for link, img, title in matches:
            if title:
                result["list"].append({
                    "vod_id": link,
                    "vod_name": title.strip(),
                    "vod_pic": img,
                    "vod_remarks": ""
                })
        return result

    # 核心接口 2: 分类内容
    def categoryContent(self, tid, pg, filter, extend):
        # 根据 category_map 找到对应分类名
        cat_name = None
        for name, (cat_id, sub) in self.category_map.items():
            if cat_id == tid:
                cat_name = name
                break
        if not cat_name:
            return {"page": pg, "pagecount": 1, "limit": 20, "total": 0, "list": []}
        # 构建分类页URL（假设有分页参数）
        url = f"{self.site_url}/?type={cat_name}&page={pg}"
        html = self._request(url)
        result = {
            "page": int(pg),
            "pagecount": 1,
            "limit": 20,
            "total": 0,
            "list": []
        }
        # 提取视频卡片
        pattern = r'<a[^>]*href="([^"]*)"[^>]*>.*?<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"[^>]*>'
        matches = re.findall(pattern, html, re.DOTALL)
        for link, img, title in matches:
            if title:
                result["list"].append({
                    "vod_id": link,
                    "vod_name": title.strip(),
                    "vod_pic": img,
                    "vod_remarks": ""
                })
        return result

    # 核心接口 3: 视频详情
    def detailContent(self, ids):
        # ids 可能是一个列表，取第一个
        vod_id = ids[0] if isinstance(ids, list) else ids
        detail_url = urljoin(self.site_url, vod_id)
        html = self._request(detail_url)
        result = {"list": []}
        # 提取详情信息（简化版：标题、简介、播放列表）
        title_match = re.search(r'<h1[^>]*>([^<]*)</h1>', html)
        vod_name = title_match.group(1).strip() if title_match else "未知"
        # 提取播放线路（常见格式：线路名$格式$链接#链接...）
        vod_play_url = ""
        vod_play_from = ""
        # 假设存在播放按钮或链接
        play_links = re.findall(r'href="([^"]*)"[^>]*>(.*?第\d+集|.*?\d+)</a>', html)
        if play_links:
            vod_play_from = "默认线路"
            urls = []
            for link, label in play_links:
                urls.append(f"{label}${link}")
            vod_play_url = "#".join(urls)
        result["list"].append({
            "vod_id": vod_id,
            "vod_name": vod_name,
            "vod_play_from": vod_play_from,
            "vod_play_url": vod_play_url,
            "vod_director": "",
            "vod_actor": "",
            "vod_pic": "",
            "vod_content": ""
        })
        return result

    # 核心接口 4: 搜索
    def searchContent(self, keyword, quick, pg):
        search_url = f"{self.site_url}/?q={quote(keyword)}&page={pg}"
        html = self._request(search_url)
        result = {
            "page": int(pg),
            "pagecount": 1,
            "limit": 20,
            "total": 0,
            "list": []
        }
        pattern = r'<a[^>]*href="([^"]*)"[^>]*>.*?<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"[^>]*>'
        matches = re.findall(pattern, html, re.DOTALL)
        for link, img, title in matches:
            if title:
                result["list"].append({
                    "vod_id": link,
                    "vod_name": title.strip(),
                    "vod_pic": img,
                    "vod_remarks": ""
                })
        return result

    # 核心接口 5: 播放地址解析
    def playerContent(self, flag, id, vipFlags):
        # id 通常是直接播放地址
        return {
            "parse": 0,
            "url": id,
            "header": self.header
        }