# -*- coding: utf-8 -*-
import os, base64, gc, re, json
from base.spider import Spider

class Spider(Spider):
    # ==========================================================================
    # 💎 【1. 核心导航配置区】    m3u
    # ==========================================================================
    # ⚙️ [控制分页]：控制首页频道列表每页显示的条数，若文件极多建议保持 2000
    CHANNEL_PAGE_SIZE = 2000  

    # 📂 [大类权重配置]：扫描目标的物理文件夹名。
    # ⚠️ 严格按此数组顺序排列首页频道，不同大类之间绝不混排，显示完一个大类再显示下一个。
    SCAN_DIR_LIST = [
                    "TVData",      #电视📺专用文件夹，把db文件放在这里# 👈 u盘也用这个文件夹                                          
              #  "lz", "纯福利", "私藏视频",  "江湖", "粉妹"           # 👈 前面加#关闭   这里可以修改任意大佬包名 
              #  "VodPlus", "peekpili/php-scripts"                       #同上
     ]

    # 🚫 [核心黑名单]：精准拦截不希望出现的文件名或路径片段（支持文件夹名或具体路径）
    BLACK_LIST = ["本地仓"]
     
    # 📝 [严格白名单]：仅处理指定的流媒体格式，在物理扫描层直接过滤非相关文件（如 .py, .txt）
    WHITE_EXTS = ('.m3u', '.m3u8')

    # 📍 [扫描深度控制]：设置搜索文件夹的最大深度（1-3级）。
    # 1级：仅扫描大类根目录；2-3级：向下探测子文件夹。
    MAX_DEPTH = 3    #修改扫描速度
    # --------------------------------------------------------------------------

    # 定义 M3U 特征常量（用于二进制流快速匹配）
    PROTO_M = b'://'
    GENRE_M = b',#genre#'
    COMMA = b',h'

    def __init__(self):
        super().__init__()
        self.inited = False
        # 缓存容器：categories 存放分类/频道列表，file_index 存放频道ID与文件的映射
        self.cache = {"categories": [], "file_index": {}}
        self.info_cache = {} # 文件状态缓存：存储修改时间、频道总数、格式化大小等
        self.line_limit = 2000    
        self.adaptive_tag = "" # 性能档位标签

    def getName(self):
        # 动态返回插件名，包含当前版本的性能档位
        return f"LocalM3U_TurboLazy_v62_{self.adaptive_tag}"

    # --- ⚙️ 核心引擎1：内存自适应补偿系统 ---
    def _get_adaptive_config(self):
        """ 
      #  性能自适应：根据系统 MemTotal 自动决定单页展示的数据条数。
      #  确保在低端设备（电视盒）上不因单页数据过多而闪退。
        """
        total_kb = 0
        try:
            if os.path.exists('/proc/meminfo'):
                with open('/proc/meminfo', 'r') as f:
                    content = f.read()
                    m = re.search(r'MemTotal:\s+(\d+)', content)
                    if m: total_kb = int(m.group(1))
        except: 
            total_kb = 2097152 # 默认按 2G 内存处理

        if total_kb <= 3145728: 
            return {"limit": 1500, "tag": "Eco"}   #低档机分片限制1500条
        elif total_kb < 25165824: 
            return {"limit": 10000, "tag": "Balance"}
        else: 
            return {"limit": 50000, "tag": "Ultra"}

    def _format_size(self, size_bytes):
        """ 将字节数转换(K/M) """
        if size_bytes < 1024: return f"{int(size_bytes)}B"
        if size_bytes < 1048576: return f"{int(size_bytes/1024)}K"  
        return f"{size_bytes/1048576:.1f}M"

    # --- ⚙️ 核心引擎2：延迟触发扫描引擎 ---
    def _get_file_base_stats(self, f_path):
        try:
            st = os.stat(f_path)
            if f_path in self.info_cache and self.info_cache[f_path].get('mtime') == st.st_mtime and 'count' in self.info_cache[f_path]:
                return self.info_cache[f_path]
            
            count = 0
            with open(f_path, 'rb') as f:
                while True:
                    buf = f.read(1024 * 1024) 
                    if not buf: break
                    # --- 🎯 核心统计锚点：同时数普通链接和长蛇阵标签 ---
                    # 统计所有以 http 开头的链接，或者一行里隐藏的 #EXTINF 数量
                    # 使用正则：(?i) 表示忽略大小写
                    count += len(re.findall(rb'#EXTINF:', buf, re.I))
            
            # 如果文件里没有 #EXTINF（比如纯链接格式），则按原逻辑数链接
            if count == 0:
                with open(f_path, 'rb') as f:
                    f.seek(0)
                    buf = f.read(1024 * 1024)
                    count = len(re.findall(rb'\n\s*(?!#)\w+://', b'\n' + buf))

            f_size_str = self._format_size(st.st_size)
            data = {
                'mtime': st.st_mtime, 
                'rem': f"{f_size_str} {count}条", 
                'count': count, 
                'size_bytes': st.st_size,
                'size_str': f_size_str
            }
            self.info_cache[f_path] = data 
            return data
        except: 
            return {'rem': "0B 0条", 'count': 0, 'size_bytes': 0, 'size_str': "0B"}

    # ==========================================================================
    # 📂 【核心初始化引擎】 - 实现深度控制、大类隔离与路径命名   差异化扫描逻辑
    # ==========================================================================

    def init(self, extend):
        if self.inited: return
        config = self._get_adaptive_config()
        self.line_limit = config["limit"]
        self.adaptive_tag = config["tag"]

        # 1. 扫描路径准备
        scan_roots = ["/storage/emulated/0"]
        try:
            if os.path.exists("/storage"):
                for s in os.listdir("/storage"):
                    if s not in ["self", "emulated", "knox", "sdcard0", "runtime"]:
                        scan_roots.append(os.path.join("/storage", s))
        except: pass
        if extend and os.path.isdir(extend): scan_roots.insert(0, extend)

        all_raw_cats, final_index, unique_paths = [], {}, set()
        folder_groups = {} 
        all_m3u_paths_for_search = []
        sort_w = {"M3U": 1}
        p_size = self.CHANNEL_PAGE_SIZE if self.CHANNEL_PAGE_SIZE > 0 else 2000

        # 🚀 [开始扫描任务]
        for r_root in scan_roots:
            is_ext = not r_root.startswith("/storage/emulated/0")
            star = "☆" if is_ext else "" 
            
            for zone_weight, target in enumerate(self.SCAN_DIR_LIST):
                base_p = os.path.join(r_root, target)
                if not os.path.isdir(base_p): continue
                
                # 🛠️ 【恢复：差异化扫描识别】
                # 识别电视专用文件夹 (tvbox, bh, bhh)，这些文件夹允许扫描根目录
                is_special_dir = target.lower() in ["tvbox", "bhh", "bh"]
                
                for root, dirs, files in os.walk(base_p):
                    # 📂 [层级计算]
                    rel_path = os.path.relpath(root, base_p)
                    depth = 0 if rel_path == "." else len(rel_path.split(os.sep))

                    # 🛑 [规则1]：深度限制
                    if depth > self.MAX_DEPTH:
                        dirs[:] = []
                        continue
                    
                    # 🛑 [规则2]：差异化过滤
                    # 非专用文件夹 (如自定义添加的其他目录)，跳过 0 级（根目录文件），直接从子目录提取
                    if not is_special_dir and depth == 0:
                        continue

                    # 检查文件夹黑名单
                    if os.path.basename(root) in getattr(self, 'DIR_BLACK_LIST', []):
                        dirs[:] = [] 
                        continue

                    valid_files_in_folder = []
                    for f in files:
                        if not f.lower().endswith(('.m3u', '.m3u8')): continue
                        f_path = os.path.join(root, f)
                        
                        # 核心黑名单拦截
                        if any(bl in f_path for bl in self.BLACK_LIST): continue
                        
                        try:
                            # 基础校验：只要有内容就通过，不再强求 #EXTINF 字符串出现在前2048字节
                            if os.path.getsize(f_path) > 0:
                                valid_files_in_folder.append(f_path)
                                all_m3u_paths_for_search.append(f_path)
                        except: continue

                    if not valid_files_in_folder: continue
                    
                    real_root = os.path.realpath(root)
                    if real_root in unique_paths: continue
                    unique_paths.add(real_root)

                    folder_display = target if rel_path == "." else f"{target}/{rel_path.replace(os.sep, '/')}"

                    # 🚀 [分类与聚合逻辑]
                    for f_path in valid_files_in_folder:
                        try:
                            sz_raw = os.stat(f_path).st_size
                            f_info_str = self._format_size(sz_raw)
                            is_ext_val = 1 if is_ext else 0
                            type_w = sort_w.get("M3U", 99)
                            
                            # 5MB 以上大文件独立成台
                            if sz_raw >= 1024*1024*3:      #5242880: # 5MB
                                f_base = os.path.basename(f_path).rsplit('.', 1)[0]
                                u_key = f"📄{folder_display}/{f_base}({self._format_size(sz_raw)}){star}"          #全路径显示，隐藏路径，用下面这一行
                                #u_key = f"📄{os.path.basename(folder_display)}/{f_base}({self._format_size(sz_raw)}){star}"     #保留一个文件夹信息
                                #u_key = f"📄{f_base}({self._format_size(sz_raw)}){star}"         #只保留文件名和大小
                                
                                tid = base64.b64encode(f"SINGLE|{f_path}|{u_key}".encode()).decode()
                                final_index[tid] = [f_path]
                                all_raw_cats.append({
                                    "type_id": tid, 
                                    "type_name": u_key, 
                                    "sk": (zone_weight, type_w, 1, sz_raw, is_ext_val, folder_display)
                                })
                            else: 
                                # 小文件按文件夹归类
                                group_key = f"📁{folder_display}"     #显示路径
                                #group_key = f"📁{os.path.basename(folder_display)}"  #隐藏路径，用这一行

                              
                                if group_key not in folder_groups: 
                                    folder_groups[group_key] = {
                                        "files": [], "star": star, "total_size": 0, 
                                        "sk_base": (zone_weight, type_w, 0, is_ext_val, folder_display)
                                    }
                                folder_groups[group_key]["files"].append(f_path)
                                folder_groups[group_key]["total_size"] += sz_raw
                        except: continue

        # 📦 [处理文件夹的分页]
        for g_name, g_data in folder_groups.items():
            g_files = sorted(g_data["files"])
            formatted_total = self._format_size(g_data["total_size"])
            for i in range(0, len(g_files), p_size):
                chunk = g_files[i : i + p_size]
                page_num = (i // p_size) + 1
                suffix = f"[{page_num}]" if len(g_files) > p_size else ""
                final_t_name = f"{g_name}({formatted_total}){g_data['star']}{suffix}"
                tid = base64.b64encode(f"GROUP|{final_t_name}".encode()).decode()
                final_index[tid] = chunk
                all_raw_cats.append({
                    "type_id": tid, 
                    "type_name": final_t_name, 
                    "sk": (g_data["sk_base"][0], g_data["sk_base"][1], 0, g_data["total_size"], g_data["sk_base"][2], g_data["sk_base"][3], page_num)
                })

        # 🎯 [排序并保存]
        sorted_cats = sorted(all_raw_cats, key=lambda x: x['sk'])
        self.cache["categories"] = [{"type_id": c["type_id"], "type_name": c["type_name"]} for c in sorted_cats]
        self.cache["file_index"] = final_index
        self.cache["all_files"] = all_m3u_paths_for_search
        self.inited = True
        gc.collect() 
#        
        #♥    排列从小到大结束
    def homeContent(self, filter):
        return {"class": self.cache["categories"]}
    # ==========================================================================
    def categoryContent(self, tid, pg, filter, ext):
        """ 🎯 [M3U 专用版] 移除 TXT 判断，强化分片与计数 """
        if str(pg) != "1": return {"list": []}
        v_list = []
        try:
            # 获取目标文件列表
            target_files = self.cache.get("file_index", {}).get(tid, [])
            limit = getattr(self, 'line_limit', 1000)
            
            for f_path in target_files:
                if not os.path.exists(f_path): continue
                
                f_name = os.path.basename(f_path).rsplit('.', 1)[0]
                f_size_raw = os.stat(f_path).st_size
                
                # --- 🎯 1. 500K 以下小文件强制不分片 ---
                force_single_part = f_size_raw < 512000 
                
                real_count = 0
                
                # 嗅探编码（专为 M3U 优化）
                with open(f_path, 'rb') as f_b:
                    sample = f_b.read(4096)
                    enc = 'utf-8'
                    for e in ['utf-8', 'gb18030', 'cp936', 'big5']:
                        try:
                            sample.decode(e)
                            enc = e
                            break
                        except: pass
                
                # --- 🎯 2. M3U 核心计数 (处理长蛇行与标准行) ---
                with open(f_path, 'r', encoding=enc, errors='ignore') as f:
                    for line in f:
                        line = line.strip()
                        # 过滤掉 M3U 头部标识
                        if not line or line.startswith('#EXTM3U'): continue
                        
                        # 识别一行多频道的非标长蛇 M3U
                        inf_in_line = line.count("#EXTINF:")
                        if inf_in_line > 1:
                            real_count += inf_in_line
                        # 标准 M3U 逻辑：#EXTINF 只是标签，计数交给随后的链接行
                        elif line.startswith("#EXTINF:"):
                            continue
                        elif '://' in line:
                            real_count += 1

                # --- 🎯 3. 分片决策 ---
                if force_single_part:
                    parts = 1
                else:
                    parts = (real_count + limit - 1) // limit if real_count > 0 else 1
                
                # 统一图标：既然是 M3U 专版，直接指定视频图标
                v_pic = "https://img.icons8.com/color/200/video-file.png"

                # --- 🎯 4. 生成分页条目 ---
                for i in range(int(parts)):
                    # ID 锚点：页码|总数|路径
                    v_id_str = "P|%d|%d|%s" % (i, real_count, f_path)
                    v_id = base64.b64encode(v_id_str.encode('utf-8')).decode('utf-8').rstrip('=')
                    
                    v_list.append({
                        "vod_id": v_id, 
                        "vod_name": "%s(%d/%d)" % (f_name, i+1, int(parts)) if parts > 1 else f_name,
                        "vod_pic": v_pic,
                        "vod_remarks": "第%d页 | 共%d条频道" % (i+1, real_count)
                    })
        except Exception as e:
            v_list.append({"vod_name": "M3U解析失败", "vod_remarks": str(e)})
            
        return {"list": v_list}

    # ==========================================================================
    # 🌟 【黄金代码核心注入区】 - 全能解析
    # ==========================================================================
    def detailContent(self, array):
        try:
            # 1. 基础解码与数据同步 (处理 P|页码|路径 或 P|页码|总数|路径)
            v_id_raw = str(array[0])
            v_id_raw += "=" * ((4 - len(v_id_raw) % 4) % 4)
            raw = base64.b64decode(v_id_raw).decode('utf-8', 'ignore')
            
            parts_info = raw.split('|')
            # 兼容处理：自动识别是 3 段式还是 4 段式 ID
            if len(parts_info) >= 4:
                p_idx, final_total, f_path = int(parts_info[1]), parts_info[2], parts_info[3]
                has_sync = True
            else:
                # 兼容原代码的 P|idx|path 格式
                p_idx = int(parts_info[1]) if len(parts_info) > 1 else 0
                f_path = parts_info[-1]
                final_total = "0"
                has_sync = False
            
            # 使用原类中的 line_limit，确保性能档位一致
            limit = getattr(self, 'line_limit', 2000)
            start_pos, end_pos = p_idx * limit, (p_idx + 1) * limit

            if not os.path.exists(f_path): 
                return {"list": [{"vod_name": "文件不存在", "vod_content": f_path}]}

            # 2. 编码识别（增强版）
            enc = 'utf-8'
            with open(f_path, 'rb') as f_b:
                h = f_b.read(4096)
                for e in ['utf-8', 'gb18030', 'cp936', 'big5']:
                    try:
                        h.decode(e)
                        enc = e
                        break
                    except: pass

            # 3. 核心容器
            genre_dict, genre_order = {}, [] 
            curr_g, scan_count, page_item_count = "默认分类", 0, 0
            pending_first_ep_name = ""
            temp_name = ""

            with open(f_path, 'r', encoding=enc, errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#EXTM3U") or line.startswith("{"): continue

                    # ==========================================================
                    # 【通道 A】：处理“横向长蛇 M3U” (一行包含多个 #EXTINF)
                    # ==========================================================
                    if line.count("#EXTINF:") > 1:
                        # 核心思路：将这一行切开，但每一段都要计入 scan_count 以支持分片
                        segments = line.split("#EXTINF:")
                        for seg in segments:
                            if not seg.strip(): continue
                            
                            # 1. 计数器累加（每个 #EXTINF 代表一个频道）
                            scan_count += 1
                            
                            # 2. 分片控制：不在当前页范围内的片段直接跳过
                            if scan_count <= start_pos: continue
                            if scan_count > end_pos: break # 超过本页限制，直接跳出循环
                            
                            # 3. 解析当前片段
                            pseudo_line = "#EXTINF:" + seg
                            # 匹配名字和URL（支持带空格或不带空格的复杂情况）
                            n_match = re.search(r',([^,]+?)\s+(https?://[^\s]+)', pseudo_line)
                            if n_match:
                                # 提取分类 (group-title)
                                g_match = re.search(r'group-title=["\'](.*?)["\']', pseudo_line, re.I)
                                tmp_g = g_match.group(1).strip() if g_match else curr_g
                                
                                if tmp_g not in genre_order: genre_order.append(tmp_g)
                                if tmp_g not in genre_dict: genre_dict[tmp_g] = []
                                
                                name, url = n_match.group(1).strip(), n_match.group(2).strip()
                                genre_dict[tmp_g].append(f"{name}${url}")
                                page_item_count += 1
                        
                        # 如果已经由于 scan_count > end_pos 退出，则不再处理后续行
                        if scan_count > end_pos: break
                        continue

                    # --- 常规分类判定 ---
                    g_match = re.search(r'group-title=["\'](.*?)["\']', line, re.I)
                    if g_match:
                        curr_g = g_match.group(1).strip()
                        pending_first_ep_name = ""
                    elif "#genre#" in line.lower():
                        curr_g = line.split(',')[0].strip()
                        pending_first_ep_name = curr_g 
                        if curr_g not in genre_order: genre_order.append(curr_g)
                        if curr_g not in genre_dict: genre_dict[curr_g] = []
                        continue 

                    if line.startswith("#EXTINF:"):
                        temp_name = line.split(',')[-1].strip()
                        continue

                    # --- 链接处理区 ---
                    if '://' in line:
                        scan_count += 1
                        if scan_count <= start_pos: 
                            pending_first_ep_name = ""; temp_name = ""; continue
                        if scan_count > end_pos: break 

                        if curr_g not in genre_order: genre_order.append(curr_g)
                        if curr_g not in genre_dict: genre_dict[curr_g] = []

                        # --- 【通道 B】：一行多集特区 ---
                        if '$' in line and ('集' in line or '#' in line):
                            clean_line = re.sub(r'\w+[-]?\w+=["\'].*?["\']', '', line).strip()
                            if pending_first_ep_name:
                                first_url = re.search(r'(https?://[^\s#$]+)', clean_line)
                                if first_url:
                                    genre_dict[curr_g].append(f"{pending_first_ep_name}${first_url.group(1)}")
                            
                            eps = clean_line.replace('$$$', '#').split('$')
                            for ep in eps:
                                if '://' not in ep: continue
                                u_m = re.search(r'(https?://[^\s#$]+)', ep)
                                if not u_m: continue
                                url = u_m.group(1)
                                sub_parts = ep.split('#')
                                name = ""
                                if len(sub_parts) > 1:
                                    name = sub_parts[1].strip() if '://' in sub_parts[0] else sub_parts[0].strip()
                                if name == pending_first_ep_name: continue
                                if not name: name = f"第{len(genre_dict[curr_g])+1}集"
                                genre_dict[curr_g].append(f"{name}${url}")
                            pending_first_ep_name = ""
                        
                        # --- 【常规通道】：单行 TXT / M3U ---
                        else:
                            clean_line = re.sub(r'\w+[-]?\w+=["\'].*?["\']', '', line).strip()
                            parts = [p.strip() for p in clean_line.split(',') if p.strip()]
                            url = next((p for p in parts if "://" in p), line)
                            u_m = re.search(r'(https?://[^\s#$]+)', url)
                            if u_m:
                                # 优先使用 EXTINF 提取的名字
                                name = temp_name if temp_name else next((p for p in parts if "://" not in p), f"P_{scan_count}")
                                genre_dict[curr_g].append(f"{name}${u_m.group(1)}")

                        page_item_count += 1
                        temp_name = ""

            # 4. 组装输出 (支持 $$$ 多线路切换)
            from_names, urls_list = [], []
            check_keys = ["默认分类"] + genre_order
            seen_keys = set()
            for g in check_keys:
                if g in genre_dict and genre_dict[g] and g not in seen_keys:
                    from_names.append(g.strip())
                    urls_list.append("#".join(genre_dict[g]))
                    seen_keys.add(g)
            
            if not from_names: 
                from_names, urls_list = ["解析完毕"], ["本页无更多内容$http://0.0.0.0"]

            # 5. 简介信息封装
            try:
                # 获取文件的物理大小并格式化
                f_size_raw = os.path.getsize(f_path)
                f_size_str = self._format_size(f_size_raw) if hasattr(self, '_format_size') else f"{f_size_raw / 1024 / 1024:.1f}M"
            except:
                f_size_str = "未知"

            display_total = final_total if has_sync else scan_count
            v_content = f"📊 数据统计: {display_total} 条有效数据\n"
            v_content += f"⚖️ 文件大小: {f_size_str}\n"  # <--- 这里添加了大小展示
            v_content += f"🚩 当前分页: 第 {start_pos + 1} 至 {min(int(display_total), end_pos)} 条\n"
            v_content += f"✅ 本页成功: {page_item_count} 条 | 索引: {p_idx + 1}\n"
            v_content += f"⚡ 性能档位: {getattr(self, 'adaptive_tag', 'Balance')}\n"
            v_content += f"📍 物理路径: {f_path}"
            
            return {"list": [{
                "vod_name": os.path.basename(f_path).rsplit('.', 1)[0],
                "vod_play_from": "$$$".join(from_names),
                "vod_play_url": "$$$".join(urls_list),
                "vod_content": v_content
            }]}

        except Exception as e:
            return {"list": [{"vod_name": "解析失败", "vod_content": str(e)}]} 

    # ==========================================================================
    # 🎬 【播放与清理区】
    # ==========================================================================
    def playerContent(self, flag, id, vipFlags): 
        """ 
        播放器加固：注入标准 UA 和 Referer，防止源被拦截。
        针对 api.php 类接口，统一伪装成常用的 okhttp 客户端。
        """
        # 兼容性处理：如果 id 中包含 '$' 符号（常见于带名称的播放链接），仅提取 URL 部分
        url = id.split('$')[-1] if '$' in id else id
        
        return {
            "url": url.strip(), 
            "header": {
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; TV) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
                "Referer": "http://bxtv.3a.ink/", # 动态调整了来源
                "Accept": "*/*",
                "Connection": "keep-alive"
            },
            "parse": 0 # 0 表示直接播放，不走二次解析
        }
        
    def destroy(self):
        """ 退出插件时强制垃圾回收，确保低端机型内存及时释放 """
        gc.collect() 