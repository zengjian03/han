# -*- coding: utf-8 -*-
import os, base64, gc, re, json, time
from base.spider import Spider

class Spider(Spider):
    # ==========================================================================
    # 💎 【1. 核心导航配置区】   json
    # ==========================================================================
    # ⚙️ [门阀1.2：频道分页开关]：控制首页频道列表每页显示的条数
    CHANNEL_PAGE_SIZE = 2000  

    # 📂 [路径配置]：指定扫描内置/外置存储根目录下的哪些文件夹 (支持1-3级深度搜索)
    SCAN_DIR_LIST = [
                 "TVData",      #电视📺专用文件夹，把db文件放在这里# 👈 u盘也用这个文件夹                                          
             #   "lz", "纯福利", "私藏视频",  "江湖", "粉妹"           # 👈 前面加#关闭   这里可以修改任意大佬包名 
              #  "VodPlus", "peekpili/php-scripts"                       #同上
      ]
    
    # --------------------------------------------------------------------------

    def __init__(self):
        super().__init__()
        self.inited = False
        # cache["categories"]: 存储首页展示的频道对象列表
        # cache["file_index"]: 映射频道 ID 到对应的文件路径列表
        self.cache = {"categories": [], "file_index": {}} 
        self.info_cache = {} # 🎯 [延迟扫描缓存]：用于存储点击频道后扫描到的条数和指纹
        self.line_limit = 2000    # ⚙️ [默认阈值]：JSON分页的基础条数
        self.adaptive_tag = "" # 性能档位标签，用于 getName 辨识当前压感状态

#①   (黑白门阀)
        # ==========================================================================
    # 🚫 【拦截门阀】 - 深度指纹校验（过滤接口配置、爬虫规则、软件列表）
    # ==========================================================================
    def _is_illegal_source(self, f_path, head_str):
        """ 返回 True 表示拦截，False 表示通过 """
        head_low = head_str.lower()
        #🚫 1. 黑名单关键字：命中这些词的 JSON 通常是 TVBox 配置文件或接口菜单
        ILLEGAL_KEYS = ['"spider"', '"wallpaper"', '"lives"', '"config"', '"sites"', '"parses"', '"urls"', '"User-Agent"', '"数据列表"', '"header"']
        
        if f_path.lower().endswith('.json'):
            # ✔2. 白名单关键字：真正的点播源必须包含的核心字段
            VOD_MUST_HAVE = ['"vod_play_url"', '"vod_id"', '"list"', '"videos"', '"vod_name"']
            
            # 逻辑：如果包含黑名单词，或者 完全不包含影视核心词，则拦截
            if any(k in head_low for k in ILLEGAL_KEYS): return True
            if not any(v in head_low for v in VOD_MUST_HAVE): return True
                
        return False
      
    def getName(self):
        # 返回插件名称，标注为 LazyLoad 版本，方便在 UI 查看当前内存压感档位
        return f"LocalJSON_LazyTurbo_v84_Mixed_{self.adaptive_tag}"

    # ==========================================================================
    # ⚙️ 【性能补偿系统】 - 自动检测设备硬件环境
    # ==========================================================================
    def _get_adaptive_config(self):
        """ 性能自适应逻辑：通过读取系统内存信息，动态决定分页的大小，防止低端机 OOM """
        total_kb = 0
        try:
            if os.path.exists('/proc/meminfo'):
                with open('/proc/meminfo', 'r') as f:
                    content = f.read()
                    m = re.search(r'MemTotal:\s+(\d+)', content)
                    if m: total_kb = int(m.group(1))
        except: pass
        
        if total_kb == 0: total_kb = 2097152 # 默认 2G 档位
        
        if total_kb <= 3145728: return {"limit": 1500, "tag": "Eco"}
        elif total_kb < 12582912: return {"limit": 5000, "tag": "Balance"}
        else: return {"limit": 10000, "tag": "Ultra"}

    def _format_size(self, size_bytes):
        """ 字节数值 K/M 字符串 """
        if size_bytes < 1024: return f"{int(size_bytes)}B"
        if size_bytes < 1048576: return f"{int(size_bytes/1024)}K"  
        return f"{size_bytes/1048576:.1f}M"

    # ==========================================================================
    # 🚀 【核心性能组件】 - 延迟统计引擎 (仅在点击二级菜单时触发)
    # ==========================================================================
    def _get_json_stats_lazy(self, f_path):
        """ 🎯 [按需执行]：原本 init 里的 open 扫描逻辑被剥离至此。
            只有点击具体频道后，才会产生 IO 读取文件，极大地解放了首页初始化压力。 """
        try:
            st = os.stat(f_path)
            # 检查指纹缓存，避免在同一个 session 内对未修改的文件重复扫描
            if f_path in self.info_cache and self.info_cache[f_path].get('mtime') == st.st_mtime:
                if 'count' in self.info_cache[f_path]: return self.info_cache[f_path]

            sz_raw = st.st_size
            # 🎯 [点击触发点]：通过抽样计算 play_url 频次来预估总条数
            with open(f_path, 'rb') as f_cnt:
                sample = f_cnt.read(1024*512)
                c_sample = sample.count(b'"play_url"') if b'"play_url"' in sample else sample.count(b'"vod_play_url"')
                count = int((c_sample / len(sample)) * sz_raw) if len(sample) > 0 else 0
                if count == 0 and sz_raw > 0: count = 1
            
            res = {
                "mtime": st.st_mtime,
                "count": count,
                "size_raw": sz_raw,
                "size_str": self._format_size(sz_raw),
                "rem": f"{self._format_size(sz_raw)} 约{count}条"
            }
            self.info_cache[f_path] = res
            return res
        except:
            return {"count": 0, "size_raw": 0, "size_str": "0B", "rem": "读取错误"}
#③
    # ==========================================================================
    # 📂 【核心初始化引擎 - v84
    # ==========================================================================
    def init(self, extend):
        """ 🎯 [极速索引模式]：
            1. 深度搜索 1-3 级目录并美化路径显示。
            2. JSON 指纹过滤，自动剔除无效文件。
            3. 区域权重排序：json0 > bh > lz > 江湖。 """
        if self.inited: return
        gc.disable() 
        config = self._get_adaptive_config()
        self.line_limit = config["limit"]
        self.adaptive_tag = config["tag"]

        # 构建扫描起始任务
        scan_tasks = [{"root": "/storage/emulated/0", "is_ext": False}]
        try:
            if os.path.exists("/storage"):
                for folder in os.listdir("/storage"):
                    if folder not in ["emulated", "self", "knox", "sdcard0", "runtime"]:
                        ext_path = os.path.join("/storage", folder)
                        if os.path.isdir(ext_path): scan_tasks.append({"root": ext_path, "is_ext": True})
        except: pass
        if extend: scan_tasks.insert(0, {"root": extend.strip(), "is_ext": True})

#④   开始(大小排列)
        all_raw_cats, final_index, unique_paths = [], {}, set()
        # 💎 核心权重定义：JSON 始终优先级最高
        sort_w = {"JSON": 1}
        folder_groups = {} 
        p_size = self.CHANNEL_PAGE_SIZE if self.CHANNEL_PAGE_SIZE > 0 else 2000
        all_json_paths_for_search = []

        # 🚀 [开始扫描任务]
        for task in scan_tasks:
            # 根据 SCAN_DIR_LIST 的配置顺序，自动生成 zone_weight (区域权重)
            # 这决定了是 bh 靠前还是 lz 靠前
            for zone_weight, target_dir in enumerate(self.SCAN_DIR_LIST):
                bh_p = os.path.join(task['root'], target_dir)
                if not os.path.isdir(bh_p): continue
                star = "☆" if task['is_ext'] else "" 
                
                # 🛠️ 识别电视专用文件夹权限：深度 0 的根目录也允许显示
                is_special_dir = target_dir.lower() in ["tvbox", "bh", "lz"]
                
                for root, dirs, files in os.walk(bh_p):
                    # 📂 [路径深度解析]
                    rel_path = os.path.relpath(root, bh_p)
                    depth = 0 if rel_path == "." else len(rel_path.split(os.sep))

                    #  [熔断机制]：限制深度为 3 级，防止无限递归
                    if depth > 3:
                        dirs[:] = []
                        continue
                    
                    # 🛑 [深度跳过逻辑]：非核心目录跳过空的根部，保持列表清爽
                    if not is_special_dir and depth == 0:
                        continue

                    valid_files_in_folder = []
                    for f in files:
                        if not f.lower().endswith('.json'): continue
                        f_path = os.path.join(root, f)
                        
                        # --- [JSON 指纹内容硬核拦截] ---
                        try:
                            with open(f_path, 'r', encoding='utf-8', errors='ignore') as jf:
                                head = jf.read(2048)
                                # 只有包含影视站特征码的 JSON 才会准入    ✔准入门槛
                                if any(x in head for x in ['"play_url"', '"vod_play_url"', '"videos"', '"vod"']):
                                    valid_files_in_folder.append(f_path)
                                    all_json_paths_for_search.append(f_path)
                        except: continue
            #♦频道显示排列从小到大
                    if not valid_files_in_folder: continue
                    
                    # 物理路径去重
                    real_root = os.path.realpath(root)
                    if real_root in unique_paths: continue
                    unique_paths.add(real_root)

                    # 🎨 [路径美化展示]
                    folder_display = target_dir if rel_path == "." else f"{target_dir}/{rel_path.replace(os.sep, '/')}"

                    for f_path in valid_files_in_folder:
                        try:
                            # 1. 获取原始字节
                            st_info = os.stat(f_path)
                            sz_raw = st_info.st_size
                            
                            # 2. ⚡ 关键修复：立即换算成可读格式 (M/K/B)
                            # 确保你的类里有 def _format_size(self, size_bytes)
                            f_info_str = self._format_size(sz_raw) 
                            
                            is_ext_val = 1 if task['is_ext'] else 0
                            type_w = sort_w.get("JSON", 99)
                            final_zone = zone_weight
                            
                            # 🔥 置顶逻辑
                            if zone_weight == 0 and "json0" in f_path.lower():
                                type_w = 0
                                final_zone = -1 

                            # 🚀 大文件处理 (5MB = 5242880 Bytes)
                            if sz_raw >= 1024*1024*3:     #5242880
                                f_base = os.path.basename(f_path).rsplit('.', 1)[0]
                                # 影视仓风格显示：📄路径/文件名 (大小)☆
                                u_key = f"📄{folder_display}/{f_base}({self._format_size(sz_raw)}){star}"          #全路径显示，隐藏路径，用下面这一行
                                #u_key = f"📄{os.path.basename(folder_display)}/{f_base}({self._format_size(sz_raw)}){star}"     #保留一个文件夹信息
                                #u_key = f"📄{f_base}({self._format_size(sz_raw)}){star}"         #只保留文件名和大小
                                
                                tid = base64.b64encode(f"SINGLE|{f_path}|{u_key}".encode()).decode()
                                final_index[tid] = [f_path]
                                
                                all_raw_cats.append({
                                    "type_id": tid, 
                                    "type_name": u_key, 
                                    "sk": (final_zone, type_w, 1, sz_raw, is_ext_val, folder_display)     #大文件排列倒序 -sz_raw
                                })
                            else: 
                                # 🚀 小文件归类
                                group_key = f"📁{folder_display}"     #隐藏路径，用下面这一行
                                #group_key = f"📁{os.path.basename(folder_display)}"  

                                
                                if group_key not in folder_groups: 
                                    folder_groups[group_key] = {
                                        "files": [], "star": star, "total_size": 0, 
                                        "sk_base": (final_zone, type_w, 0, is_ext_val, folder_display)
                                    }
                                folder_groups[group_key]["files"].append(f_path)
                    #♦下面行文件夹排列倒序 -sz_raw
                                folder_groups[group_key]["total_size"] += sz_raw       #文件夹排列倒序 -sz_raw
                        except Exception as e:
                            # 如果报错，至少能看到路径，方便排查权限问题
                            continue

        # 📦 [处理文件夹频道的分页与排序]
        for g_name, g_data in folder_groups.items():
            g_files = sorted(g_data["files"])
            formatted_total = self._format_size(g_data["total_size"])
            g_star = g_data["star"]
            
            for i in range(0, len(g_files), p_size):
                chunk = g_files[i : i + p_size]
                page_num = (i // p_size) + 1
                suffix = f"[{page_num}]" if len(g_files) > p_size else ""
                # 影视仓风格：📁 + 路径 (总大小) + 星号 + 分页号
                final_t_name = f"{g_name}({formatted_total}){g_star}{suffix}"
                tid = base64.b64encode(f"GROUP|{final_t_name}".encode()).decode()
                final_index[tid] = chunk
                # 排序键：文件夹在单目录下优先级为 0 (靠前)
                all_raw_cats.append({
                    "type_id": tid, 
                    "type_name": final_t_name, 
            #♦下面行文件夹排列倒序设置 (0, -g_data["total_size"])
                    "sk": g_data["sk_base"][:2] + (0, g_data["total_size"]) + g_data["sk_base"][2:] + (page_num,)      #文件夹排列倒序 (0, -g_data["total_size"])
                })
        
        # 🎯 [执行影视仓式终极排序]
        sorted_cats = sorted(all_raw_cats, key=lambda x: x['sk'])
        self.cache["categories"] = [{"type_id": c["type_id"], "type_name": c["type_name"]} for c in sorted_cats]
        self.cache["file_index"] = final_index
        self.cache["all_files"] = all_json_paths_for_search
        self.inited = True
        gc.collect()
#⑤  #♦排列从小到大结束

    def homeContent(self, filter):
        """ 返回首页频道列表 """
        return {"class": self.cache["categories"]}

    def categoryContent(self, tid, pg, filter, ext):
        """ 🎯 [延迟加载触发区]：只有在此处才会真正解析文件格式及计算分页条数 """
        if str(pg) != "1": return {"list": []}
        target_files = self.cache["file_index"].get(tid, [])
        v_list = []
        for f_path in target_files:
            if not os.path.exists(f_path): continue
            f_base = os.path.basename(f_path).rsplit('.', 1)[0]
            try:
                # 统计条数与指纹
                info = self._get_json_stats_lazy(f_path)
                
                # 🚀 格式探测
                with open(f_path, 'r', encoding='utf-8', errors='ignore') as f_read:
                    peek = f_read.read(2048) # 读多一点确保能读到 vod
                    
                    # 🎯 【图片模式增强】：处理 "vod" 节点开头的影视站格式
                    if '"vod"' in peek:
                        f_read.seek(0)
                        data = json.loads(f_read.read())
                        # 这种格式通常直接在 vod 数组里
                        for item in data.get('vod', []):
                            v_name = item.get('vod_name', '影视')
                            v_id = base64.b64encode(f"VOD_IMG|{f_path}|{v_name}".encode()).decode()
                            v_list.append({
                                "vod_id": v_id, 
                                "vod_name": f"[{f_base}] {v_name}", 
                                "vod_pic": item.get('vod_pic', ''), 
                                "vod_remarks": item.get('vod_remarks', '图片模式')
                            })
                        continue

                    if '"videos"' in peek: 
                        # 新格式解析
                        f_read.seek(0)
                        data = json.loads(f_read.read())
                        for item in data.get('videos', []):
                            v_name = item.get('title', '未知')
                            v_id = base64.b64encode(f"NEW|{f_path}|{v_name}".encode()).decode()
                            v_list.append({
                                "vod_id": v_id, 
                                "vod_name": f"[{f_base}] {v_name}", 
                                "vod_pic": item.get('cover', ''), 
                                "vod_remarks": item.get('type', '新格式')
                            })
                        continue 

                # 旧格式虚拟分段
                count = info['count']
                parts = (count // self.line_limit) + 1 if count > 0 else 1
                for i in range(parts):
                    v_id = base64.b64encode(f"P|{i}|{f_path}".encode()).decode()
                    v_list.append({
                        "vod_id": v_id, 
                        "vod_name": f"{f_base}({i+1}/{parts})" if parts > 1 else f_base, 
                        "vod_pic": "https://img.icons8.com/color/200/json--v1.png", 
                        "vod_remarks": info['rem']
                    })
            except: continue
        return {"list": v_list}

#⑥   (详情页美化)
    def detailContent(self, array):
        """ 🎯 终极全兼容版：支持 vod/list/videos 嵌套 + 智能 ID 适配 + 小说风简介 """
        try:
            v_id_raw = str(array[0])
            # Base64 补齐与自动解码
            v_id_raw += "=" * ((4 - len(v_id_raw) % 4) % 4)
            raw_decoded = base64.b64decode(v_id_raw).decode('utf-8', errors='ignore')
            
            # --- 🚀 1. 增强型 ID 解析逻辑 ---
            # 支持格式：SINGLE|path, PATH|path, P|idx|path, 或纯 path
            p_idx = 0
            target_name = None
            if "|" in raw_decoded:
                parts = raw_decoded.split('|')
                if parts[0] in ["SINGLE", "PATH", "VOD_IMG", "NEW"]:
                    f_path = parts[1]
                    if len(parts) > 2: target_name = parts[2]
                elif parts[0] == "P":
                    p_idx = int(parts[1])
                    f_path = parts[2]
                else:
                    f_path = raw_decoded # 保底
            else:
                f_path = raw_decoded

            if not os.path.exists(f_path): 
                return {"list": [{"vod_name": "文件已移除", "vod_content": f"路径不存在: {f_path}"}]}

            with open(f_path, 'r', encoding='utf-8', errors='ignore') as f:
                full_text = f.read()

            def _clean_url(url_str):
                if not url_str or not isinstance(url_str, str): return ""
                match = re.search(r'/(https?://|vip\.|dytt-|cdn\.|img\.)', url_str)
                if match:
                    new_url = url_str[match.start()+1:]
                    return "https://" + new_url if not new_url.startswith("http") else new_url
                return url_str

            single_list_1, single_list_2 = [], []
            series_tabs_from, series_tabs_url = [], []
            last_pic = "https://img.icons8.com/color/200/json--v1.png"
            json_vod_content = ""
            has_multi_line = False 

            # --- 🚀 2. 深度内容解析 ---
            try:
                js_data = json.loads(full_text)
                # 兼容所有影视站标准节点
                items = js_data.get('vod') or js_data.get('list') or js_data.get('videos')
                if items is None:
                    items = [js_data] if isinstance(js_data, dict) else js_data
                
                # 过滤出当前分页或目标影片
                if target_name:
                    current_items = [it for it in items if (it.get('vod_name') or it.get('title')) == target_name]
                else:
                    skip = p_idx * self.line_limit
                    current_items = items[skip : skip + self.line_limit]
                
                for it in current_items:
                    name = str(it.get('vod_name') or it.get('title') or '未命名').replace('$', '').replace('#', '')
                    raw_url = str(it.get('vod_play_url') or it.get('play_url') or '')
                    pic = it.get('vod_pic') or it.get('pic') or it.get('cover') or ""
                    content = it.get('vod_content') or it.get('content') or it.get('desc') or ""
                    
                    if pic and "http" in pic: last_pic = pic
                    if content and not json_vod_content: json_vod_content = content
                    if not raw_url: continue

                    # 🎬 处理电影 (单集)
                    if "#" not in raw_url:
                        if "$$$" in raw_url:
                            has_multi_line = True
                            u_parts = raw_url.split('$$$')
                            single_list_1.append(f"{name}${_clean_url(u_parts[0])}")
                            single_list_2.append(f"{name}${_clean_url(u_parts[1] if len(u_parts)>1 else u_parts[0])}")
                        else:
                            single_list_1.append(f"{name}${_clean_url(raw_url)}")
                    # 📺 处理剧集 (连续剧)
                    else:
                        actual_url = raw_url.split('$$$')[0] if "$$$" in raw_url else raw_url
                        eps_group = []
                        for ep in actual_url.split('#'):
                            if '$' in ep:
                                ep_nm, ep_lk = ep.split('$', 1)
                                eps_group.append(f"{ep_nm}${_clean_url(ep_lk)}")
                            else:
                                eps_group.append(f"正片${_clean_url(ep)}")
                        series_tabs_from.append(name)
                        series_tabs_url.append("#".join(eps_group))
            except: pass

            # --- 🚀 3. 组装输出 (按需生成按钮) ---
            final_froms, final_urls = [], []
            if single_list_1:
                if has_multi_line:
                    final_froms.append("🎬 线路①"); final_urls.append("#".join(single_list_1))
                    final_froms.append("🎬 线路②"); final_urls.append("#".join(single_list_2))
                else:
                    final_froms.append("🎬 影片清单"); final_urls.append("#".join(single_list_1))
            
            if series_tabs_from:
                for i in range(len(series_tabs_from)):
                    final_froms.append(f"📺 {series_tabs_from[i]}")
                    final_urls.append(series_tabs_url[i])
#⑦
            # --- 🚀 4. 技术简介注入 (小说风格) ---
            file_real_name = os.path.basename(f_path).rsplit('.', 1)[0]
            tech_info = (
                f"{json_vod_content if json_vod_content else '此本地资源暂无详细剧情描述。'}"
                f"📊 统计: 电影 {len(single_list_1)} | 剧集 {len(series_tabs_from)}\n"
                f"📂 路径: {f_path}\n"
                f"⚡ 档位: {self.adaptive_tag}\n"
                f"🛡️ 状态: {'多线路引擎已激活' if has_multi_line else '单线路纯净模式'}\n"
        #        f"{'─' * 22}\n"
                
            )

            if not final_froms:
                final_froms.append("⚠️ 暂无有效链接")
                final_urls.append("empty$http://127.0.0.1/empty.m3u8")

            return {"list": [{
                "vod_name": file_real_name,
                "vod_pic": last_pic,
                "vod_play_from": "$$$".join(final_froms),
                "vod_play_url": "$$$".join(final_urls),
                "vod_content": tech_info 
            }]}
        except Exception as e: 
            return {"list": [{"vod_name": "解析崩溃", "vod_content": f"错误详情: {str(e)}"}]}


    def _clean_url(self, link):
        """ 统一清洗去反带逻辑 """
        link = link.strip()
        match = re.search(r'/(https?://|vip\.|dytt-|cdn\.|img\.)', link)
        if match:
            link = link[match.start()+1:]
            if not link.startswith("http"): link = "https://" + link
        return link
#⑧
    def searchContent(self, key, quick):
        """ 本地全局搜索 """
        res = []
        for f in self.cache.get("all_files", []):
            if key in os.path.basename(f):
                res.append({
                    "vod_id": base64.b64encode(f"P|0|{f}".encode()).decode(), 
                    "vod_name": os.path.basename(f).rsplit('.', 1)[0], 
                    "vod_pic": "https://img.icons8.com/color/200/search--v1.png", 
                    "vod_remarks": "搜索结果"
                })
        return {"list": res}

    def playerContent(self, flag, id, vipFlags):
        """ 🎯 增强型播放处理：深度伪装绕过 VPN 干扰 """
        url = id.split('$')[-1] if '$' in id else id
        url = url.strip()
        domain_match = re.search(r'https?://[^/]+/', url)
        base_url = domain_match.group(0) if domain_match else url
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 12; mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Mobile Safari/537.36 okhttp/3.15.0",
            "Referer": base_url,
            "Origin": base_url.rstrip('/'),
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive"
        }
        return {"url": url, "header": headers, "parse": 0}

    def destroy(self):
        """ 内存回收与资源释放 """
        gc.collect(); gc.enable(); return "destroy"