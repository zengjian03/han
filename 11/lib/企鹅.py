# coding=utf-8
#!/usr/bin/python
# 精彩
import json
import sys
import uuid
import copy
import traceback
sys.path.append('..')
from base.spider import Spider
from pyquery import PyQuery as pq
from concurrent.futures import ThreadPoolExecutor, as_completed


class Spider(Spider):

    def init(self, extend=""):
        self.dbody = {
            "page_params": {
                "channel_id": "",
                "filter_params": "sort=75",
                "page_type": "channel_operation",
                "page_id": "channel_list_second_page"
            }
        }
        self.body = self.dbody
        pass

    def getName(self):
        return "腾讯视频"

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    host = 'https://v.qq.com'
    apihost = 'https://pbaccess.video.qq.com'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5410.0 Safari/537.36',
        'origin': host,
        'referer': f'{host}/'
    }

    def homeContent(self, filter):
        cdata = {
            "电视剧": "100113",
            "电影": "100173",
            "综艺": "100109",
            "纪录片": "100105",
            "动漫": "100119",
            "少儿": "100150",
            "短剧": "110755"
        }
        result = {}
        classes = []
        filters = {}
        for k in cdata:
            classes.append({
                'type_name': k,
                'type_id': cdata[k]
            })
        
        # 修复：添加异常处理
        with ThreadPoolExecutor(max_workers=len(classes)) as executor:
            futures = {executor.submit(self.get_filter_data, item['type_id']): item['type_id'] for item in classes}
            for future in as_completed(futures):
                cid = futures[future]
                try:
                    _, data = future.result()
                    if not data.get('data', {}).get('module_list_datas'):
                        continue
                    filter_dict = {}
                    try:
                        # 安全获取嵌套数据
                        module_list = data['data']['module_list_datas']
                        if not module_list:
                            continue
                        last_module = module_list[-1]
                        if not last_module.get('module_datas'):
                            continue
                        module_datas = last_module['module_datas']
                        if not module_datas:
                            continue
                        item_lists = module_datas[-1].get('item_data_lists', {}).get('item_datas', [])
                        
                        for item in item_lists:
                            if not item.get('item_params', {}).get('index_item_key'):
                                continue
                            params = item['item_params']
                            filter_key = params['index_item_key']
                            if filter_key not in filter_dict:
                                filter_dict[filter_key] = {
                                    'key': filter_key,
                                    'name': params.get('index_name', ''),
                                    'value': []
                                }
                            filter_dict[filter_key]['value'].append({
                                'n': params.get('option_name', ''),
                                'v': params.get('option_value', '')
                            })
                    except (IndexError, KeyError, TypeError) as e:
                        print(f"处理分类 {cid} 筛选数据时出错: {str(e)}")
                        continue
                    filters[cid] = list(filter_dict.values())
                except Exception as e:
                    print(f"获取分类 {cid} 筛选失败: {str(e)}")
                    continue
                    
        result['class'] = classes
        result['filters'] = filters
        return result

    def homeVideoContent(self):
        vlist = []
        try:
            data = self.gethtml(self.host)
            its = data('script')
            s = None
            for it in its.items():
                text = it.text()
                if text and 'window.__INITIAL_STATE__' in text:
                    s = text
                    break
            if s:
                index = s.find('=')
                if index != -1:
                    json_str = s[index + 1:].strip()
                    try:
                        sd = json.loads(json_str)
                    except json.JSONDecodeError as e:
                        print(f"JSON解析错误: {str(e)}")
                        return {'list': []}
                        
                    channels_map = sd.get('storeModulesData', {}).get('channelsModulesMap', {})
                    choice_data = channels_map.get('choice', {})
                    if choice_data and choice_data.get('cardListData'):
                        for its in choice_data['cardListData']:
                            if its and its.get('children_list', {}).get('list', {}).get('cards'):
                                for it in its['children_list']['list']['cards']:
                                    if it and it.get('params'):
                                        p = it['params']
                                        # 安全解析JSON标签
                                        tag = {}
                                        try:
                                            tag_str = p.get('uni_imgtag') or p.get('imgtag', '{}')
                                            if tag_str:
                                                tag = json.loads(tag_str)
                                        except (json.JSONDecodeError, TypeError):
                                            tag = {}
                                            
                                        id = it.get('id') or p.get('cid')
                                        name = p.get('mz_title') or p.get('title')
                                        if name and id and 'http' not in str(id):
                                            vlist.append({
                                                'vod_id': id,
                                                'vod_name': name,
                                                'vod_pic': p.get('image_url'),
                                                'vod_year': tag.get('tag_2', {}).get('text', ''),
                                                'vod_remarks': tag.get('tag_4', {}).get('text', '')
                                            })
        except Exception as e:
            print(f"首页内容获取失败: {str(e)}")
            traceback.print_exc()
            
        return {'list': vlist}

    def categoryContent(self, tid, pg, filter, extend):
        result = {}
        params = {
            "sort": extend.get('sort', '75'),
            "attr": extend.get('attr', '-1'),
            "itype": extend.get('itype', '-1'),
            "ipay": extend.get('ipay', '-1'),
            "iarea": extend.get('iarea', '-1'),
            "iyear": extend.get('iyear', '-1'),
            "theater": extend.get('theater', '-1'),
            "award": extend.get('award', '-1'),
            "recommend": extend.get('recommend', '-1')
        }
        if pg == '1':
            self.body = self.dbody.copy()
        self.body['page_params']['channel_id'] = tid
        self.body['page_params']['filter_params'] = self.josn_to_params(params)
        
        try:
            response = self.post(
                f'{self.apihost}/trpc.universal_backend_service.page_server_rpc.PageServer/GetPageData?video_appid=1000005&vplatform=2&vversion_name=8.9.10&new_mark_label_enabled=1',
                json=self.body, headers=self.headers)
            data = response.json()
        except Exception as e:
            print(f"分类请求失败: {str(e)}")
            return {'list': [], 'page': pg, 'pagecount': 0, 'limit': 90, 'total': 0}
            
        ndata = data.get('data', {})
        if not ndata:
            return {'list': [], 'page': pg, 'pagecount': 0, 'limit': 90, 'total': 0}
            
        if ndata.get('has_next_page'):
            result['pagecount'] = 9999
            self.body['page_context'] = ndata.get('next_page_context', '')
        else:
            result['pagecount'] = int(pg)
            
        vlist = []
        try:
            # 安全获取列表数据
            module_list = ndata.get('module_list_datas', [])
            if module_list and module_list[-1].get('module_datas'):
                item_datas = module_list[-1]['module_datas'][-1].get('item_data_lists', {}).get('item_datas', [])
                for its in item_datas:
                    id = its.get('item_params', {}).get('cid')
                    if id:
                        p = its['item_params']
                        tag = {}
                        try:
                            tag_str = p.get('uni_imgtag') or p.get('imgtag', '{}')
                            if tag_str:
                                tag = json.loads(tag_str)
                        except (json.JSONDecodeError, TypeError):
                            tag = {}
                            
                        name = p.get('mz_title') or p.get('title')
                        pic = p.get('new_pic_hz') or p.get('new_pic_vt')
                        vlist.append({
                            'vod_id': id,
                            'vod_name': name,
                            'vod_pic': pic,
                            'vod_year': tag.get('tag_2', {}).get('text', ''),
                            'vod_remarks': tag.get('tag_4', {}).get('text', '')
                        })
        except (IndexError, KeyError, TypeError) as e:
            print(f"解析分类数据失败: {str(e)}")
            
        result['list'] = vlist
        result['page'] = pg
        result['limit'] = 90
        result['total'] = 999999
        return result

    def detailContent(self, ids):
        if not ids:
            return self.handle_exception(None, "Empty ids")
            
        vbody = {
            "page_params": {
                "req_from": "web",
                "cid": ids[0],
                "vid": "",
                "lid": "",
                "page_type": "detail_operation",
                "page_id": "detail_page_introduction"
            },
            "has_cache": 1
        }

        body = {
            "page_params": {
                "req_from": "web_vsite",
                "page_id": "vsite_episode_list",
                "page_type": "detail_operation",
                "id_type": "1",
                "page_size": "",
                "cid": ids[0],
                "vid": "",
                "lid": "",
                "page_num": "",
                "page_context": "",
                "detail_page_type": "1"
            },
            "has_cache": 1
        }

        vdata = {}
        data = {}
        
        # 修复：添加异常处理
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_detail = executor.submit(self.get_vdata, vbody)
            future_episodes = executor.submit(self.get_vdata, body)
            
            try:
                vdata = future_detail.result()
            except Exception as e:
                print(f"获取详情失败: {str(e)}")
                
            try:
                data = future_episodes.result()
            except Exception as e:
                print(f"获取剧集失败: {str(e)}")

        pdata = self.process_tabs(data, body, ids)
        if not pdata:
            return self.handle_exception(None, "No pdata available")

        try:
            # 安全获取演员列表
            actors = []
            try:
                star_list = vdata.get('data', {}).get('module_list_datas', [{}])[0].get('module_datas', [{}])[0].get('item_data_lists', {}).get('item_datas', [{}])[0].get('sub_items', {}).get('star_list', {}).get('item_datas', [])
                actors = [star.get('item_params', {}).get('name', '') for star in star_list if star.get('item_params', {}).get('name')]
            except (IndexError, KeyError, AttributeError):
                pass
                
            names = ['腾讯视频', '预告片']
            plist, ylist = self.process_pdata(pdata, ids)
            if not plist:
                names = [n for n in names if n != '腾讯视频']
            if not ylist:
                names = [n for n in names if n != '预告片']
                
            vod = self.build_vod(vdata, actors, plist, ylist, names)
            return {'list': [vod]}
        except Exception as e:
            return self.handle_exception(e, "Error processing detail")

    def searchContent(self, key, quick, pg="1"):
        body = {
            "version": "24072901", 
            "clientType": 1, 
            "filterValue": "", 
            "uuid": str(uuid.uuid4()), 
            "retry": 0,
            "query": key, 
            "pagenum": int(pg) - 1, 
            "pagesize": 30, 
            "queryFrom": 0, 
            "searchDatakey": "",
            "transInfo": "", 
            "isneedQc": True, 
            "preQid": "", 
            "adClientInfo": "",
            "extraInfo": {"isNewMarkLabel": "1", "multi_terminal_pc": "1"}
        }
        
        try:
            response = self.post(
                f'{self.apihost}/trpc.videosearch.mobile_search.MultiTerminalSearch/MbSearch?vplatform=2',
                json=body, headers=self.headers)
            data = response.json()
        except Exception as e:
            print(f"搜索请求失败: {str(e)}")
            return {'list': [], 'page': pg}
            
        vlist = []
        try:
            area_box_list = data.get('data', {}).get('areaBoxList', [])
            if area_box_list:
                for k in area_box_list[-1].get('itemList', []):
                    if k.get('doc', {}).get('id'):
                        img_tag = k.get('videoInfo', {}).get('imgTag', '{}')
                        tag = {}
                        if isinstance(img_tag, str):
                            try:
                                tag = json.loads(img_tag)
                            except json.JSONDecodeError:
                                tag = {}
                                
                        pic = k.get('videoInfo', {}).get('imgUrl', '')
                        vlist.append({
                            'vod_id': k['doc']['id'],
                            'vod_name': k.get('videoInfo', {}).get('title', ''),
                            'vod_pic': pic,
                            'vod_year': tag.get('tag_2', {}).get('text', ''),
                            'vod_remarks': tag.get('tag_4', {}).get('text', '')
                        })
        except (IndexError, KeyError, TypeError) as e:
            print(f"解析搜索结果失败: {str(e)}")
            
        return {'list': vlist, 'page': pg}

    def playerContent(self, flag, id, vipFlags):
        ids = id.split('@')
        if len(ids) < 2:
            return {'parse': 0, 'url': '', 'header': ''}
        url = f"{self.host}/x/cover/{ids[0]}/{ids[1]}.html"
        parse_url = f"https://jx.xmflv.com/?url={url}"
        return {'parse': 1, 'url': parse_url, 'header': ''}
        
    def localProxy(self, param):
        pass

    def gethtml(self, url):
        try:
            rsp = self.fetch(url, headers=self.headers)
            text = self.cleanText(rsp.text)
            # 修复：确保传入字符串给PyQuery
            return pq(text)
        except Exception as e:
            print(f"获取HTML失败 {url}: {str(e)}")
            # 返回空的PyQuery对象避免崩溃
            return pq('<html></html>')

    def get_filter_data(self, cid):
        try:
            hbody = self.dbody.copy()
            hbody['page_params']['channel_id'] = cid
            response = self.post(
                f'{self.apihost}/trpc.universal_backend_service.page_server_rpc.PageServer/GetPageData?video_appid=1000005&vplatform=2&vversion_name=8.9.10&new_mark_label_enabled=1',
                json=hbody, headers=self.headers)
            return cid, response.json()
        except Exception as e:
            print(f"获取筛选数据失败 {cid}: {str(e)}")
            return cid, {}

    def get_vdata(self, body):
        try:
            vdata = self.post(
                f'{self.apihost}/trpc.universal_backend_service.page_server_rpc.PageServer/GetPageData?video_appid=3000010&vplatform=2&vversion_name=8.2.96',
                json=body, headers=self.headers
            ).json()
            return vdata
        except Exception as e:
            print(f"Error in get_vdata: {str(e)}")
            return {'data': {'module_list_datas': []}}

    def process_pdata(self, pdata, ids):
        plist = []
        ylist = []
        if not pdata:
            return plist, ylist
            
        for k in pdata:
            if k.get('item_id'):
                try:
                    title = k.get('item_params', {}).get('union_title', '')
                    pid = f"{title}${ids[0]}@{k['item_id']}"
                    if '预告' in title:
                        ylist.append(pid)
                    else:
                        plist.append(pid)
                except Exception as e:
                    continue
        return plist, ylist

    def build_vod(self, vdata, actors, plist, ylist, names):
        try:
            d = vdata['data']['module_list_datas'][0]['module_datas'][0]['item_data_lists']['item_datas'][0]['item_params']
        except (KeyError, IndexError):
            d = {}
            
        urls = []
        if plist:
            urls.append('#'.join(plist))
        if ylist:
            urls.append('#'.join(ylist))
            
        vod = {
            'type_name': d.get('sub_genre', ''),
            'vod_name': d.get('title', ''),
            'vod_year': d.get('year', ''),
            'vod_area': d.get('area_name', ''),
            'vod_remarks': d.get('holly_online_time', '') or d.get('hotval', ''),
            'vod_actor': ','.join(actors) if actors else '',
            'vod_content': d.get('cover_description', ''),
            'vod_play_from': '$$$'.join(names) if names else '',
            'vod_play_url': '$$$'.join(urls) if urls else ''
        }
        return vod

    def handle_exception(self, e, message):
        if e:
            print(f"{message}: {str(e)}")
            traceback.print_exc()
        return {'list': [{'vod_play_from': '哎呀翻车啦', 'vod_play_url': '翻车啦#555'}]}

    def process_tabs(self, data, body, ids):
        try:
            pdata = data['data']['module_list_datas'][-1]['module_datas'][-1]['item_data_lists']['item_datas']
            tabs = data['data']['module_list_datas'][-1]['module_datas'][-1]['module_params'].get('tabs')
            
            if tabs:
                try:
                    tabs = json.loads(tabs)
                except json.JSONDecodeError:
                    tabs = []
                    
                if len(tabs) > 1:
                    remaining_tabs = tabs[1:]
                    task_queue = []
                    for tab in remaining_tabs:
                        nbody = copy.deepcopy(body)
                        nbody['page_params']['page_context'] = tab.get('page_context', '')
                        task_queue.append(nbody)
                        
                    with ThreadPoolExecutor(max_workers=min(10, len(task_queue))) as executor:
                        future_map = {executor.submit(self.get_vdata, task): idx for idx, task in enumerate(task_queue)}
                        results = [None] * len(task_queue)
                        for future in as_completed(future_map.keys()):
                            idx = future_map[future]
                            try:
                                results[idx] = future.result()
                            except Exception as e:
                                print(f"获取标签页 {idx} 失败: {str(e)}")
                                
                        for result in results:
                            if result and isinstance(result, dict):
                                try:
                                    page_data = result['data']['module_list_datas'][-1]['module_datas'][-1]['item_data_lists']['item_datas']
                                    pdata.extend(page_data)
                                except (KeyError, IndexError, TypeError):
                                    continue
            return pdata
        except Exception as e:
            print(f"Error processing episodes: {str(e)}")
            return []

    def josn_to_params(self, params, skip_empty=False):
        query = []
        for k, v in params.items():
            if skip_empty and not v:
                continue
            query.append(f"{k}={v}")
        return "&".join(query)
