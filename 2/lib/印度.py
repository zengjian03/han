# -*- coding: utf-8 -*-
import sys
sys.path.append('..')
from base.spider import Spider
import requests
from bs4 import BeautifulSoup
import re
import urllib.parse

# 禁用 SSL 警告，保持日志干净
requests.packages.urllib3.disable_warnings()

class Spider(Spider):

    def init(self, extend=""):
        self.host = "https://jable.tv"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }

    def getName(self):
        return "Jable"

    def isVideoFormat(self, url):
        return False

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    def get_html(self, url):
        try:
            # verify=False 忽略证书错误，适配部分网络环境
            res = requests.get(url, headers=self.headers, timeout=15, verify=False)
            res.encoding = 'utf-8'
            return res.text
        except Exception as e:
            print(f"请求报错: {e}")
            return ""

    def parse_vod_list(self, html):
        """通用列表解析"""
        soup = BeautifulSoup(html, "html.parser")
        videos = []
        for item in soup.select('.video-img-box'):
            try:
                a_tag = item.select_one('.title a')
                if not a_tag:
                    continue
                
                url = a_tag.get('href', '')
                if url and not url.startswith('http'):
                    url = self.host + url
                    
                title = a_tag.text.strip()
                
                img_tag = item.select_one('img')
                pic = img_tag.get('data-src') or img_tag.get('src') if img_tag else ''
                
                label_tag = item.select_one('.absolute-bottom-right .label')
                remark = label_tag.text.strip() if label_tag else ''
                
                videos.append({
                    "vod_id": url,
                    "vod_name": title,
                    "vod_pic": pic,
                    "vod_remarks": remark
                })
            except Exception:
                continue
        return videos

    def homeContent(self, filter):
        classes = [
            {"type_name": "热门影片", "type_id": "hot"},
            {"type_name": "最新上市", "type_id": "new"},
            {"type_name": "中文字幕", "type_id": "chinese"},
            {"type_name": "女优分类", "type_id": "actress"},
            {"type_name": "衣着分类", "type_id": "clothes"},
            {"type_name": "剧情分类", "type_id": "plot"},
            {"type_name": "地点分类", "type_id": "location"},
            {"type_name": "身材分类", "type_id": "body"},
            {"type_name": "角色分类", "type_id": "role"},
            {"type_name": "交合分类", "type_id": "intercourse"},
            {"type_name": "玩法分类", "type_id": "play"},
            {"type_name": "主题分类", "type_id": "theme"},
            {"type_name": "杂项分类", "type_id": "misc"}
        ]
        
        common_sort = [
            {"n": "最近更新", "v": "post_date"}, 
            {"n": "最多观看", "v": "video_viewed"}, 
            {"n": "最多收藏", "v": "most_favourited"}
        ]
        
        filters = {
            "hot": [{"key": "sort_by", "name": "排序", "value": [
                {"n": "今日热门", "v": "video_viewed_today"}, {"n": "本周热门", "v": "video_viewed_week"}, 
                {"n": "本月热门", "v": "video_viewed_month"}, {"n": "所有时间", "v": "video_viewed"}
            ]}],
            "new": [{"key": "sort_by", "name": "排序", "value": [
                {"n": "最新发布", "v": "latest-updates"}, {"n": "最多观看", "v": "video_viewed"}, {"n": "最多收藏", "v": "most_favourited"}
            ]}],
            "chinese": [{"key": "sort_by", "name": "排序", "value": common_sort}],
            
            # 海量细分分类字典，完美还原 JS
            "actress": [
                {"key": "url", "name": "选择女优", "value": [
                    {"n": "三上悠亚", "v": "/s1/models/yua-mikami/"}, {"n": "楪可怜", "v": "/models/86b2f23f95cc485af79fe847c5b9de8d/"},
                    {"n": "小野夕子", "v": "/models/2958338aa4f78c0afb071e2b8a6b5f1b/"}, {"n": "大槻响", "v": "/models/hibiki-otsuki/"},
                    {"n": "藤森里穗", "v": "/models/riho-fujimori/"}, {"n": "JULIA", "v": "/models/julia/"},
                    {"n": "明里䌷", "v": "/models/tsumugi-akari/"}, {"n": "桃乃木香奈", "v": "/models/momonogi-kana/"},
                    {"n": "水户香奈", "v": "/models/kana-mito/"}, {"n": "篠田ゆう", "v": "/s1/models/shinoda-yuu/"},
                    {"n": "枫可怜", "v": "/models/kaede-karen/"}, {"n": "吉泽明步", "v": "/models/akiho-yoshizawa/"},
                    {"n": "羽月希", "v": "/models/21e145d3f4d7c8c818fc7eae19342a7a/"}, {"n": "美谷朱里", "v": "/s1/models/mitani-akari/"},
                    {"n": "山岸逢花", "v": "/models/yamagishi-aika/"}, {"n": "佐佐木明希", "v": "/models/sasaki-aki/"},
                    {"n": "神木麗", "v": "/models/ef9b1ab9a21b58d6ee4d7d97ab883288/"}, {"n": "七泽美亚", "v": "/models/nanasawa-mia/"},
                    {"n": "濑户环奈", "v": "/models/1a71be5a068c6f9e00fac285b31019f9/"}, {"n": "辻本杏", "v": "/models/7ffb432871f53eda0b4d80be34fff86a/"},
                    {"n": "さくらわかな", "v": "/models/0b96db26c8b192b0a54e24d878380765/"}, {"n": "彩月七绪", "v": "/models/e82b22cd3275fd0e569147d82fa1999d/"},
                    {"n": "铃乃ウト", "v": "/models/559904d22cbf03091f790258aa4e9b8c/"}, {"n": "三田真铃", "v": "/models/7749dd641e0426f55342972d920513a7/"},
                    {"n": "七ツ森りり", "v": "/models/9ed214792a2144520430dd494c93f651/"}, {"n": "七岛舞", "v": "/models/6ab2e738a33eafc3db27cab0b83cf5cd/"},
                    {"n": "八挂うみ", "v": "/models/83397477054d35cd07e2c48685335a86/"}, {"n": "八木奈々", "v": "/models/3610067a1d725dab8ee8cd3ffe828850/"},
                    {"n": "宫下玲奈", "v": "/models/b435825a4941964079157dd2fc0a8e5a/"}, {"n": "小凑よつ叶", "v": "/models/ff8ce98f2419126e00a90bc1f3385824/"},
                    {"n": "小野六花", "v": "/models/0478c4db9858c4e6c60af7fbf828009a/"}, {"n": "工藤ゆら", "v": "/models/e7ba849893aa7ce8afcc3003a4075c20/"},
                    {"n": "本庄铃", "v": "/models/honjou-suzu/"}, {"n": "樱空もも", "v": "/models/sakura-momo/"},
                    {"n": "枫ふうあ", "v": "/models/f88e49c4c1adb0fd1bae71ac122d6b82/"}, {"n": "河北彩伽", "v": "/models/saika-kawakita2/"},
                    {"n": "矢埜爱茉", "v": "/models/0903b1921df6c616c29041be11c3d2e8/"}, {"n": "石川澪", "v": "/models/a855133fa44ca5e7679cac0a0ab7d1cb/"},
                    {"n": "美ノ岛めぐり", "v": "/models/d1ebb3d61ee367652e6b1f35b469f2b6/"}, {"n": "野々浦暖", "v": "/models/6b0ce5c4944edce04ab48d4bb608fd4c/"},
                    {"n": "青空ひかり", "v": "/models/4c7a2cfa27b343e3e07659650400f61d/"}, {"n": "香澄りこ", "v": "/models/6c2e861e04b9327701a80ca77a088814/"},
                    {"n": "新ありな", "v": "/models/e763382dc86aa703456d964ca25d0e8b/"}, {"n": "未步なな", "v": "/models/c9535c2f157202cd0e934d62ef582e2e/"},
                    {"n": "凪ひかる", "v": "/models/91fca8d824e07075d09de0282f6e9076/"}, {"n": "三宫つばき", "v": "/models/f0e279c00b2a7e1aca2ef4d31d611020/"},
                    {"n": "蓝芽みずき", "v": "/models/679c69a5488daa35a5544749b75556c6/"}, {"n": "つばさ舞", "v": "/models/0d7709a62cc199f923107c120d30893b/"},
                    {"n": "朝日りお", "v": "/models/ad0935cfa1449ab126dde2b0c0929ad0/"}, {"n": "日下部加奈", "v": "/models/dfea76fd68bc52e0888a78e0fedce073/"},
                    {"n": "弓乃りむ", "v": "/models/06c22ca98d8ec82963046ad17e0fad4a/"}, {"n": "夏希まろん", "v": "/models/1c0f1b4475962e88b541f9f0db1584fe/"},
                    {"n": "水川スミレ", "v": "/models/7415fde573b12a4e87e83ef33ea354d5/"}, {"n": "实浜みき", "v": "/models/299c2d256b9c509f80302d261ea0b5a9/"},
                    {"n": "弥生みづき", "v": "/s1/models/mizuki-yayoi/"}, {"n": "天川そら", "v": "/models/3e69d39a117c2d25a407dfd57e204e48/"},
                    {"n": "新名あみん", "v": "/models/0dba31ccef2f1fca3563c56dbcf3fa7d/"}, {"n": "小泽菜穗", "v": "/models/2ec30dc8e35906a29fe5c8f5b97e6c89/"},
                    {"n": "三原ほのか", "v": "/models/mihara-honoka/"}, {"n": "凉森れむ", "v": "/models/7cadf3e484f607dc7d0f1c0e7a83b007/"},
                    {"n": "森日向子", "v": "/models/1a7543f89b125421e489d98de472ebf4/"}, {"n": "金松季步", "v": "/models/48ace5552227a2a4f867af73efa18f2d/"}
                ]},
                {"key": "sort_by", "name": "排序", "value": common_sort}
            ],
            "clothes": [
                {"key": "url", "name": "选择衣着", "value": [
                    {"n": "黑丝", "v": "/tags/black-pantyhose/"}, {"n": "肉丝", "v": "/tags/flesh-toned-pantyhose/"},
                    {"n": "丝袜", "v": "/tags/pantyhose/"}, {"n": "兽耳", "v": "/tags/kemonomimi/"},
                    {"n": "渔网", "v": "/tags/fishnets/"}, {"n": "水着", "v": "/tags/swimsuit/"},
                    {"n": "校服", "v": "/tags/school-uniform/"}, {"n": "旗袍", "v": "/tags/cheongsam/"},
                    {"n": "婚纱", "v": "/tags/wedding-dress/"}, {"n": "女仆", "v": "/tags/maid/"},
                    {"n": "和服", "v": "/tags/kimono/"}, {"n": "眼镜娘", "v": "/tags/glasses/"},
                    {"n": "过膝袜", "v": "/tags/knee-socks/"}, {"n": "运动装", "v": "/tags/sportswear/"},
                    {"n": "兔女郎", "v": "/tags/bunny-girl/"}, {"n": "Cosplay", "v": "/tags/Cosplay/"}
                ]},
                {"key": "sort_by", "name": "排序", "value": common_sort}
            ],
            "plot": [
                {"key": "url", "name": "选择剧情", "value": [
                    {"n": "出轨", "v": "/tags/affair/"}, {"n": "醉男", "v": "/tags/ugly-man/"},
                    {"n": "亲属", "v": "/tags/kinship/"}, {"n": "童贞", "v": "/tags/virginity/"},
                    {"n": "复仇", "v": "/tags/avenge/"}, {"n": "巨汉", "v": "/tags/giant/"},
                    {"n": "媚药", "v": "/tags/love-potion/"}, {"n": "催眠", "v": "/tags/hypnosis/"},
                    {"n": "偷拍", "v": "/tags/private-cam/"}, {"n": "NTR", "v": "/tags/ntr/"},
                    {"n": "年龄差", "v": "/tags/age-difference/"}, {"n": "下雨天", "v": "/tags/rainy-day/"},
                    {"n": "时间停止", "v": "/tags/time-stop/"}
                ]},
                {"key": "sort_by", "name": "排序", "value": common_sort}
            ],
            "location": [
                {"key": "url", "name": "选择地点", "value": [
                    {"n": "电车", "v": "/tags/tram/"}, {"n": "处女", "v": "/tags/first-night/"},
                    {"n": "监狱", "v": "/tags/prison/"}, {"n": "温泉", "v": "/tags/hot-spring/"},
                    {"n": "泳池", "v": "/tags/swimming-pool/"}, {"n": "汽车", "v": "/tags/car/"},
                    {"n": "厕所", "v": "/tags/toilet/"}, {"n": "学校", "v": "/tags/school/"},
                    {"n": "魔镜号", "v": "/tags/magic-mirror/"}, {"n": "洗浴场", "v": "/tags/bathing-place/"},
                    {"n": "图书馆", "v": "/tags/library/"}, {"n": "健身房", "v": "/tags/gym-room/"},
                    {"n": "便利店", "v": "/tags/store/"}
                ]},
                {"key": "sort_by", "name": "排序", "value": common_sort}
            ],
            "body": [
                {"key": "url", "name": "选择身材", "value": [
                    {"n": "长身", "v": "/tags/tall/"}, {"n": "软体", "v": "/tags/flexible-body/"},
                    {"n": "贫乳", "v": "/tags/small-tits/"}, {"n": "美腿", "v": "/tags/beautiful-leg/"},
                    {"n": "美尻", "v": "/tags/beautiful-butt/"}, {"n": "纹身", "v": "/tags/tattoo/"},
                    {"n": "短发", "v": "/tags/short-hair/"}, {"n": "白虎", "v": "/tags/hairless-pussy/"},
                    {"n": "熟女", "v": "/tags/mature-woman/"}, {"n": "巨乳", "v": "/tags/big-tits/"},
                    {"n": "少女", "v": "/tags/girl/"}, {"n": "娇小", "v": "/tags/dainty/"}
                ]},
                {"key": "sort_by", "name": "排序", "value": common_sort}
            ],
            "role": [
                {"key": "url", "name": "选择角色", "value": [
                    {"n": "人妻", "v": "/tags/wife/"}, {"n": "医生", "v": "/tags/doctor/"},
                    {"n": "护士", "v": "/tags/nurse/"}, {"n": "老师", "v": "/tags/teacher/"},
                    {"n": "空姐", "v": "/tags/flight-attendant/"}, {"n": "逃犯", "v": "/tags/fugitive/"},
                    {"n": "情侣", "v": "/tags/couple/"}, {"n": "主播", "v": "/tags/female-anchor/"},
                    {"n": "风俗娘", "v": "/tags/club-hostess-and-sex-worker/"}, {"n": "家政妇", "v": "/tags/housewife/"},
                    {"n": "搜查官", "v": "/tags/detective/"}, {"n": "未亡人", "v": "/tags/widow/"},
                    {"n": "家庭教师", "v": "/tags/private-teacher/"}, {"n": "球队经理", "v": "/tags/team-manager/"}
                ]},
                {"key": "sort_by", "name": "排序", "value": common_sort}
            ],
            "intercourse": [
                {"key": "url", "name": "选择交合", "value": [
                    {"n": "颜射", "v": "/tags/facial/"}, {"n": "足交", "v": "/tags/footjob/"},
                    {"n": "痉挛", "v": "/tags/spasms/"}, {"n": "潮吹", "v": "/tags/squirting/"},
                    {"n": "深喉", "v": "/tags/deep-throat/"}, {"n": "接吻", "v": "/tags/kiss/"},
                    {"n": "口爆", "v": "/tags/cum-in-mouth/"}, {"n": "口交", "v": "/tags/blowjob/"},
                    {"n": "乳交", "v": "/tags/tit-wank/"}, {"n": "中出", "v": "/tags/creampie/"}
                ]},
                {"key": "sort_by", "name": "排序", "value": common_sort}
            ],
            "play": [
                {"key": "url", "name": "选择玩法", "value": [
                    {"n": "露出", "v": "/tags/outdoor/"}, {"n": "侵犯", "v": "/tags/intrusion/"},
                    {"n": "调教", "v": "/tags/tune/"}, {"n": "捆绑", "v": "/tags/bondage/"},
                    {"n": "痴汉", "v": "/tags/chikan/"}, {"n": "痴女", "v": "/tags/chizyo/"},
                    {"n": "男M", "v": "/tags/masochism-guy/"}, {"n": "泥醉", "v": "/tags/crapulence/"},
                    {"n": "泡姬", "v": "/tags/soapland/"}, {"n": "母乳", "v": "/tags/breast-milk/"},
                    {"n": "放尿", "v": "/tags/piss/"}, {"n": "按摩", "v": "/tags/massage/"},
                    {"n": "多P", "v": "/tags/groupsex/"}, {"n": "瞬间插入", "v": "/tags/quickie/"},
                    {"n": "集团侵犯", "v": "/tags/gang-intrusion/"}
                ]},
                {"key": "sort_by", "name": "排序", "value": common_sort}
            ],
            "theme": [
                {"key": "url", "name": "选择主题", "value": [
                    {"n": "角色剧情", "v": "/categories/roleplay/"}, {"n": "制服诱惑", "v": "/categories/uniform/"},
                    {"n": "直接开啪", "v": "/categories/sex-only/"}, {"n": "丝袜美腿", "v": "/categories/pantyhose/"},
                    {"n": "主奴调教", "v": "/categories/bdsm/"}, {"n": "多P群交", "v": "/categories/groupsex/"},
                    {"n": "男友视角", "v": "/categories/pov/"}, {"n": "凌辱快感", "v": "/categories/insult/"},
                    {"n": "盗摄偷拍", "v": "/categories/private-cam/"}, {"n": "无码解放", "v": "/categories/uncensored/"},
                    {"n": "女同欢愉", "v": "/categories/lesbian/"}
                ]},
                {"key": "sort_by", "name": "排序", "value": common_sort}
            ],
            "misc": [
                {"key": "url", "name": "选择杂项", "value": [
                    {"n": "录像", "v": "/tags/video-recording/"}, {"n": "综艺", "v": "/tags/variety-show/"},
                    {"n": "感谢祭", "v": "/tags/thanksgiving/"}, {"n": "节日主题", "v": "/tags/festival/"},
                    {"n": "四小时以上", "v": "/tags/more-than-4-hours/"}, {"n": "处女作/隐退作", "v": "/tags/debut-retires/"}
                ]},
                {"key": "sort_by", "name": "排序", "value": common_sort}
            ]
        }
        
        return {'class': classes, 'filters': filters}

    def homeVideoContent(self):
        url = f"{self.host}/hot/?mode=async&function=get_block&block_id=list_videos_common_videos_list&sort_by=video_viewed_today"
        html = self.get_html(url)
        return {'list': self.parse_vod_list(html)}

    def categoryContent(self, tid, pg, filter, extend):
        defaults = {
            "actress": "/s1/models/yua-mikami/", "clothes": "/tags/black-pantyhose/",
            "plot": "/tags/affair/", "location": "/tags/tram/", "body": "/tags/tall/",
            "role": "/tags/wife/", "intercourse": "/tags/facial/", "play": "/tags/outdoor/",
            "theme": "/categories/roleplay/", "misc": "/tags/video-recording/"
        }
        
        if tid == "hot":
            base_url = "/hot/"
        elif tid == "new":
            base_url = "/new-release/"
        elif tid == "chinese":
            base_url = "/categories/chinese-subtitle/"
        else:
            base_url = extend.get("url", defaults.get(tid, "/"))

        url = f"{self.host}{base_url}?mode=async&function=get_block&block_id=list_videos_common_videos_list&from={pg}"
        
        if 'sort_by' in extend:
            url += f"&sort_by={extend['sort_by']}"
            
        html = self.get_html(url)
        videos = self.parse_vod_list(html)
        
        return {
            'list': videos,
            'page': pg,
            'pagecount': int(pg) + 1 if len(videos) > 0 else int(pg),
            'limit': 24,
            'total': 9999
        }

    def detailContent(self, ids):
        url = ids[0]
        html = self.get_html(url)
        
        # 提取标题和图片
        soup = BeautifulSoup(html, 'html.parser')
        title_tag = soup.select_one('meta[property="og:title"]')
        title = title_tag['content'] if title_tag else url
        title = title.replace(' - Jable.tv', '')
        
        pic_tag = soup.select_one('meta[property="og:image"]')
        pic = pic_tag['content'] if pic_tag else ''
        
        # 提取真实 HLS 播放地址（M3U8）
        hlsUrl = url
        match = re.search(r'var\s+hlsUrl\s*=\s*[\'"](.*?)[\'"]', html, re.IGNORECASE)
        if match:
            hlsUrl = match.group(1)
            
        return {
            'list': [{
                'vod_id': url,
                'vod_name': title,
                'vod_pic': pic,
                'vod_play_from': 'Jable',
                'vod_play_url': f'播放${hlsUrl}'
            }]
        }

    def searchContent(self, key, quick, pg="1"):
        keyword = urllib.parse.quote(key)
        url = f"{self.host}/search/{keyword}/?mode=async&function=get_block&block_id=list_videos_videos_list_search_result&q={keyword}&from={pg}"
        html = self.get_html(url)
        videos = self.parse_vod_list(html)
        return {
            'list': videos,
            'page': pg,
            'pagecount': int(pg) + 1 if len(videos) > 0 else int(pg),
            'limit': 24,
            'total': 9999
        }

    def playerContent(self, flag, id, vipFlags):
        # 核心防盗链修复：强行携带 Origin 和 Referer 解决视频加载和无声问题
        return {
            "parse": 0,
            "url": id,
            "header": {
                "User-Agent": self.headers['User-Agent'],
                "Referer": "https://jable.tv/",
                "Origin": "https://jable.tv"
            }
        }

    def localProxy(self, param):
        pass
