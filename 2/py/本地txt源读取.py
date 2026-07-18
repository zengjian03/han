# -*- coding: utf-8 -*-
import os, base64, gc, re
from base.spider import Spider

class Spider(Spider):
    # ==========================================================================
    # 💎 【1. 核心导航配置区】   txt
    # ==========================================================================
    # 📂 扫描存储根目录下的这些文件夹，顺序决定了显示的优先级
    SCAN_DIR_LIST = [
                "TVData",         #电视📺专用文件夹，把db文件放在这里# 👈 u盘也用这个文件夹                                          
             #  "lz", "纯福利",  "江湖",           # 👈 前面加#关闭   这里可以修改任意大佬包名 
             #  "VodPlus", "peekpili/php-scripts"                       #同上
     ]
    
    # ⚙️ [分页设置]：首页一个频道分类下最多显示多少个文件
    CHANNEL_PAGE_SIZE = 1000  
    
    # 🔍 [特征码指纹]：用于二进制流扫描，判断是否为合法的直播源格式
    PROTO_M = b'://'            # 必须包含协议头
    GENRE_M = b',#genre#'       # 或者包含分类标识
    COMMA = b',h'                 # 必须包含逗号分隔符
    
    # 🚫 [拦截门阀]：如果文件头包含这些关键字，则判定为“非播放文件”，直接过滤
    BLACK_FINGERPRINTS = [b'serv00', b'termux', b'xlsx', b'ed2k', b'ss://', b'magnet', b'static IP', b'aa.json']

    def __init__(self):
        super().__init__()
        self.inited = False
        self.cache = {"categories": [], "file_index": {}} # 频道列表和文件索引缓存
        self.info_cache = {} # 文件指纹缓存 (大小、条数、修改时间)
        self.all_files_for_search = [] # 扁平化路径，用于全局搜索
# ♦单页显示的播放链接条数 (自适应调整)
        self.line_limit = 2000 # 单页显示的播放链接条数 (自适应调整)
        self.adaptive_tag = "" # 性能档位标签

    def getName(self):
        """ 返回插件名称，实时显示当前性能档位 """
        return f"LocalTXT_Vertical_v86.2_{self.adaptive_tag}"

    def _get_adaptive_config(self):
        """ 性能自适应：根据手机内存总量，动态决定单页解析的负载压力 """
        total_kb = 0
        try:
            with open('/proc/meminfo', 'r') as f:
                content = f.read()
                m = re.search(r'MemTotal:\s+(\d+)', content)
                if m: total_kb = int(m.group(1))
        except: total_kb = 2097152 # 默认 2GB
        
        if total_kb <= 3145728: # 3GB 以下
#♦设置自适应限制每片行数
            return {"limit": 1500, "tag": "Eco"}   #分片限制3000一片
        elif total_kb < 25165824: # 24GB 以下
            return {"limit": 8000, "tag": "Balance"}
        else: # 高端旗舰机
            return {"limit": 30000, "tag": "Ultra"}

    def _format_size(self, size_bytes):
        """ 字节单位转换 """
        if size_bytes < 1024: return f"{int(size_bytes)}B"
        if size_bytes < 1048576: return f"{int(size_bytes/1024)}K"  
        return f"{size_bytes/1048576:.1f}M"
#设置准入门槛范围
    def _get_file_base_stats(self, f_path):
        """ 延迟统计引擎：全量扫描文件以准确获取频道总数 """
        try:
            st = os.stat(f_path)
            # 命中缓存则直接返回
            if f_path in self.info_cache and self.info_cache[f_path]['mtime'] == st.st_mtime and 'count' in self.info_cache[f_path]:
                return self.info_cache[f_path]
            
            g_count, l_count = 0, 0
            is_m3u_type = False
            # 采用 1MB 缓冲分块循环读取，既不卡死又能数准全量
            with open(f_path, 'rb') as f:
                head_sample = f.read(4096)
                # 🚀 增强 M3U 侦察，确保跨行文件也能被识别为“M3U型”
                if any(k in head_sample for k in [b"#EXTINF", b"#EXTM3U", b"group-title="]):
                    is_m3u_type = True
                
                # 💡 核心计数：必须回到文件头，数准全文件的链接总数，分页才不会乱
                f.seek(0)
                while True:
                    buf = f.read(1024 * 1024) # 每次读 1MB
                    if not buf: break
                    
                    # 统计分类标识
                    if self.GENRE_M in buf or b"group-title=" in buf:
                        g_count += buf.count(self.GENRE_M) + buf.count(b"group-title=")
                    
                    # 统计链接总数
                    l_count += buf.count(b'://') 
            
            f_size_str = self._format_size(st.st_size)
            # 增加类型标记
            type_tag = "M3U型" if is_m3u_type else "标准TXT"
            data = {
                'mtime': st.st_mtime, 
                'rem': f"{f_size_str} {max(1, g_count)}类 {l_count}条 | {type_tag}", 
                'count': l_count, 
                'size_str': f_size_str,
                'size_raw': st.st_size, 
                'is_m3u': is_m3u_type 
            }
            self.info_cache[f_path] = data
            return data
        except: return {'rem': "0B 0类 0条", 'count': 0, 'size_str': "0B", 'size_raw': 0, 'is_m3u': False}

    # ==========================================================================
    # 📂 【核心初始化：差异化扫描与全能识别系统】
    # ==========================================================================
    def init(self, extend):
        if self.inited: return
        config = self._get_adaptive_config()
        self.line_limit = config["limit"]
        self.adaptive_tag = config["tag"]

        # 1. 扫描根路径自动发现
        scan_roots = ["/storage/emulated/0"]
        try:
            if os.path.exists("/storage"):
                for s in os.listdir("/storage"):
                    if s not in ["self", "emulated", "knox", "sdcard0", "runtime"]:
                        scan_roots.append(os.path.join("/storage", s))
        except: pass
        if extend and os.path.isdir(extend): scan_roots.insert(0, extend)

        all_raw_cats, final_index, unique_paths = [], {}, set()
        sort_w = {"TXT": 1}
        folder_groups = {} 
        p_size = self.CHANNEL_PAGE_SIZE if self.CHANNEL_PAGE_SIZE > 0 else 1000
        self.all_files_for_search = [] 

        # 🚀 [开始差异化扫描]
        for root_p in scan_roots:
            is_ext = not root_p.startswith("/storage/emulated/0")
            for zone_weight, target in enumerate(self.SCAN_DIR_LIST):
                base_p = os.path.join(root_p, target)
                if not os.path.isdir(base_p): continue
                
                # 📺 差异化规则：专用文件夹允许显示根目录文件
                is_special_dir = target.lower() in ["tvbox", "bhh", "bh"]
                star = "☆" if is_ext else "" 

                for root, dirs, files in os.walk(base_p):
                    rel_path = os.path.relpath(root, base_p)
                    depth = 0 if rel_path == "." else len(rel_path.split(os.sep))

                    # 🛑 [规则1]：层级限制
                    if depth > 3:
                        dirs[:] = []
                        continue
                    
                    # 🛑 [规则2]：差异扫描。非专用文件夹跳过 0 级（根目录）
                    if not is_special_dir and depth == 0:
                        continue

                    valid_files_in_folder = []
#准入门阀开始🔛
                    for f in files:
                        if not f.lower().endswith('.txt'): continue
                        
                        f_path = os.path.join(root, f)
                        try:
                            # 增加读取长度到 32KB，防止文件头杂质多
                            with open(f_path, 'rb') as f_check:
                                chunk_raw = f_check.read(32768) 
                                if any(bad in chunk_raw for bad in self.BLACK_FINGERPRINTS): continue
                                
                                # 💡 只要包含协议头，就认为是潜在的播放列表，放行！
                                # 不再强制要求包含 self.COMMA (逗号)
                                is_m3u_feat = any(k in chunk_raw for k in [b"#EXTINF", b"#EXTM3U", b"group-title="])
                                has_proto = b'://' in chunk_raw 
                                
                                if is_m3u_feat or has_proto:
                                    valid_files_in_folder.append(f_path)
                                    self.all_files_for_search.append(f_path)
                        except: continue
#准入门槛结束🔚
                    if not valid_files_in_folder: continue
                    
                    real_root = os.path.realpath(root)
                    if real_root in unique_paths: continue
                    unique_paths.add(real_root)

                    folder_display = target if rel_path == "." else f"{target}/{rel_path.replace(os.sep, '/')}"

                    for f_path in valid_files_in_folder:
                        try:
                            st_info = os.stat(f_path)
                            sz_raw = st_info.st_size
                            
                            # 大文件独立逻辑 (5MB+)
                            if sz_raw >= 1024*1024*3:    #5242880
                                f_base = os.path.basename(f_path).rsplit('.', 1)[0]
                                u_key = f"📄{folder_display}/{f_base}({self._format_size(sz_raw)}){star}"          #全路径显示，隐藏路径，用下面这一行
                                #u_key = f"📄{os.path.basename(folder_display)}/{f_base}({self._format_size(sz_raw)}){star}"     #保留一个文件夹信息
                                #u_key = f"📄{f_base}({self._format_size(sz_raw)}){star}"         #只保留文件名和大小

                                tid = base64.b64encode(f"SINGLE|{f_path}".encode()).decode().rstrip('=')
                                final_index[tid] = [f_path]
                                all_raw_cats.append({
                                    "type_id": tid, "type_name": u_key, 
                                    "sk": (zone_weight, 1, 1, sz_raw, 1 if is_ext else 0, folder_display)
                                })
                            else: 
                                # 小文件归类逻辑
                                group_key = f"📁{folder_display}"     #显示路径
                                #group_key = f"📁{os.path.basename(folder_display)}"  #显示路径，用这一句
                                if group_key not in folder_groups: 
                                    folder_groups[group_key] = {
                                        "files": [], "star": star, "total_size": 0, 
                                        "sk_base": (zone_weight, 1, 0, 1 if is_ext else 0, folder_display)
                                    }
                                folder_groups[group_key]["files"].append(f_path)
                                folder_groups[group_key]["total_size"] += sz_raw
                        except: continue

        # 📦 文件夹分页处理
        for g_name, g_data in folder_groups.items():
            g_files = sorted(g_data["files"], key=lambda x: os.path.getsize(x))
            for i in range(0, len(g_files), p_size):
                chunk = g_files[i : i + p_size]
                page_num = (i // p_size) + 1
                suffix = f"[{page_num}]" if len(g_files) > p_size else ""
                final_t_name = f"{g_name}({self._format_size(g_data['total_size'])}){g_data['star']}{suffix}"
                # 🛠️ 这里的 tid 编码要确保 detailContent 能拆开
                tid = base64.b64encode(final_t_name.encode()).decode().rstrip('=')
                final_index[tid] = chunk
                all_raw_cats.append({
                    "type_id": tid, "type_name": final_t_name, 
                    "sk": g_data["sk_base"] + (page_num,)
                })
        
        self.cache["categories"] = [{"type_id": c["type_id"], "type_name": c["type_name"]} for c in sorted(all_raw_cats, key=lambda x: x['sk'])]
        self.cache["file_index"] = final_index
        self.inited = True
        gc.collect()

#♥ 准入，差异扫描，排列从小到大结束
    def homeContent(self, filter): 
        """ 渲染首页大类列表 """
        return {"class": self.cache["categories"]}
     # ==========================================================================
     #♦侦测真假txt，把清单统计装入频道
     # 📂 【二级列表引擎】 - 支持长蛇阵精准计数与物理分片
    # ==========================================================================
    def categoryContent(self, tid, pg, filter, ext):
        if str(pg) != "1": return {"list": []}
        v_list = []
        try:
            target_files = self.cache["file_index"].get(tid, [])
            limit = self.line_limit
            
            for f_path in target_files:
                if not os.path.exists(f_path): continue
                
                f_name = os.path.basename(f_path).rsplit('.', 1)[0]
                f_size_raw = os.stat(f_path).st_size
                
                # --- 🎯 1. 500K 以下小文件强制不分片，确保稳定性 ---
                force_single_part = f_size_raw < 512000 
                
                real_count = 0
                is_m3u_type = False
                
                # 嗅探编码与文件类型 (兼容 M3U 特征)
                with open(f_path, 'rb') as f_b:
                    sample = f_b.read(4096)
                    is_m3u_type = b"#EXTM3U" in sample or b"#EXTINF" in sample
                    enc = 'utf-8'
                    for e in ['utf-8', 'gb18030', 'cp936', 'big5']:
                        try:
                            sample.decode(e)
                            enc = e
                            break
                        except: pass
                
                # --- 🎯 2. 精准对账：核心计数逻辑 (平移 M3U 长蛇处理) ---
                with open(f_path, 'r', encoding=enc, errors='ignore') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#EXTM3U'): continue
                        
                        # 【核心判定】：识别一行多频道的长蛇行
                        inf_in_line = line.count("#EXTINF:")
                        if inf_in_line > 1:
                            real_count += inf_in_line
                        # 常规 M3U 标签行：跳过计数（计数由下一行的 URL 承担）
                        elif line.startswith("#EXTINF:"):
                            continue
                        # 常规 URL 行 (包含 TXT 格式和标准 M3U 链接行)
                        elif '://' in line:
                            real_count += 1

                # --- 🎯 3. 分片决策 ---
                if force_single_part:
                    parts = 1
                else:
                    # 只有大文件才按 limit 计算总页数
                    parts = (real_count + limit - 1) // limit if real_count > 0 else 1
                
                parts = int(parts)
                v_pic = "https://img.icons8.com/color/200/video-file.png" if is_m3u_type else "https://img.icons8.com/color/200/txt.png"
                type_str = "M3U" if is_m3u_type else "TXT"

                # --- 🎯 4. 循环生成分页条目 ---
                for i in range(parts):
                    # 💡 关键 ID 锚点：P | 页码 | 总数 | 路径
                    # 这里的 real_count 会传递给 detailContent，确保两端扫描范围一致
                    v_id_str = "P|%d|%d|%s" % (i, real_count, f_path)
                    v_id = base64.b64encode(v_id_str.encode('utf-8')).decode('utf-8').rstrip('=')
                    
                    # 格式化名称：如 "电影列表(1/3)"
                    d_name = "%s(%d/%d)" % (f_name, i+1, parts) if parts > 1 else f_name
                    
                    v_list.append({
                        "vod_id": v_id, 
                        "vod_name": d_name,
                        "vod_pic": v_pic,
                        # 副标题展示：实时显示当前分片的条数情况
                        "vod_remarks": "第%d页 | 共%d条 | %s" % (i+1, real_count, type_str)
                    })
        except Exception as e:
            v_list.append({"vod_name": "列表载入失败", "vod_remarks": str(e)})
            
        return {"list": v_list}

    # ==========================================================================
    # 💎 【核心解析：优质解析代码，智能特区设置，万能嗅探逻辑缝合版】
    # 💎 【全能解析引擎】：支持长蛇阵分片、一行多集、标准M3U及TXT
    # ==========================================================================
    def detailContent(self, array):
        try:
            # 1. 基础解码与数据同步
            v_id_raw = str(array[0])
            v_id_raw += "=" * ((4 - len(v_id_raw) % 4) % 4)
            raw = base64.b64decode(v_id_raw).decode('utf-8', 'ignore')
            
            # --- 🎯 核心锚点：拆解 4 段式 ID [P, 页码, 总数, 路径] ---
            parts_info = raw.split('|')
            if len(parts_info) >= 4:
                p_idx = int(parts_info[1])
                final_total = parts_info[2]  # 💡 列表页传来的精准总数
                f_path = parts_info[3]
                has_sync = True
            else:
                # 兼容旧格式逻辑
                p_idx = int(parts_info[1]) if len(parts_info) > 1 else 0
                f_path = parts_info[-1]
                final_total = "0"
                has_sync = False
            
            # --- 物理参数：受 line_limit 阀门约束 ---
            limit = getattr(self, 'line_limit', 1000)
            start_pos = p_idx * limit
            end_pos = (p_idx + 1) * limit

            # 2. 编码识别
            enc = 'utf-8'
            if not os.path.exists(f_path): return {"list": []}
            with open(f_path, 'rb') as f_b:
                h = f_b.read(4096)
                for e in ['utf-8', 'gb18030', 'cp936']:
                    try: h.decode(e); enc = e; break
                    except: pass

            # 3. 核心容器
            genre_dict = {} 
            genre_order = [] 
            curr_g, scan_count, page_item_count = "默认分类", 0, 0
            temp_name = ""
            pending_first_ep_name = ""

            with open(f_path, 'r', encoding=enc, errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#EXTM3U") or line.startswith("{"): continue

                    # ==========================================================
                    # 【核心嫁接 A】：处理“横向长蛇阵” (一行包含多个 #EXTINF)
                    # ==========================================================
                    if line.count("#EXTINF:") > 1:
                        segments = line.split("#EXTINF:")
                        for seg in segments:
                            if not seg.strip(): continue
                            scan_count += 1
                            if scan_count <= start_pos: continue
                            if scan_count > end_pos: break 
                            
                            pseudo_line = "#EXTINF:" + seg
                            n_match = re.search(r',([^,]+?)\s+(https?://[^\s]+)', pseudo_line)
                            if n_match:
                                g_match = re.search(r'group-title=["\'](.*?)["\']', pseudo_line, re.I)
                                tmp_g = g_match.group(1).strip() if g_match else curr_g
                                
                                if tmp_g not in genre_order: genre_order.append(tmp_g)
                                if tmp_g not in genre_dict: genre_dict[tmp_g] = []
                                
                                name, url = n_match.group(1).strip(), n_match.group(2).strip()
                                genre_dict[tmp_g].append(f"{name}${url}")
                                page_item_count += 1
                        
                        if scan_count > end_pos: break
                        continue
                        
                    # --- A. 分类判定 ---
                    g_match = re.search(r'group-title=["\'](.*?)["\']', line, re.I)
                    if g_match:
                        curr_g = g_match.group(1).strip()
                    elif "#genre#" in line.lower():
                        curr_g = line.split(',')[0].strip()
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
                            temp_name = ""; pending_first_ep_name = ""; continue
                        if scan_count > end_pos: break 

                        if curr_g not in genre_order: genre_order.append(curr_g)
                        if curr_g not in genre_dict: genre_dict[curr_g] = []

                        # 1. 预清洗
                        clean_line = line.replace('$$$', '#').strip()
                        clean_line = re.sub(r'\w+[-]?\w+=["\'].*?["\']', '', clean_line).strip()

                        # 2. 【核心增强】：针对 MKV 等 名,URL 格式的特殊识别
                        # 如果行中包含逗号，且逗号后紧跟 http，判定为 [名称,链接] 格式
                        mkv_match = re.search(r'^([^,]+),(https?://[^\s]+)', clean_line)
                        
                        if mkv_match:
                            m_name, m_url = mkv_match.group(1).strip(), mkv_match.group(2).strip()
                            # 进一步处理 "歌手|歌名" 为 "歌手 - 歌名" 增加可读性
                            m_name = m_name.replace('|', ' - ')
                            genre_dict[curr_g].append(f"{m_name}${m_url}")
                        
                        elif '$' in clean_line and not clean_line.endswith('$'):
                            # --- 【一行多集/长蛇特区】 ---
                            line_parts = clean_line.split(',', 1)
                            if len(line_parts) > 1:
                                base_name, content_all = line_parts[0].strip(), line_parts[1].strip()
                            else:
                                base_name, content_all = (pending_first_ep_name or temp_name), clean_line

                            eps = content_all.split('$')
                            for idx, ep in enumerate(eps):
                                if '://' not in ep: continue
                                sub_parts = ep.split('#')
                                u, n = "", ""
                                if len(sub_parts) > 1:
                                    u = sub_parts[0].strip() if '://' in sub_parts[0] else sub_parts[1].strip()
                                    n = sub_parts[1].strip() if '://' in sub_parts[0] else sub_parts[0].strip()
                                else:
                                    u, n = ep.strip(), ""
                                
                                final_n = n if n else (base_name if idx == 0 else f"第{idx+1:02d}集")
                                u_m = re.search(r'(https?://[^\s\"\'#$]+)', u)
                                if u_m:
                                    entry = f"{final_n}${u_m.group(1)}"
                                    if entry not in genre_dict[curr_g]:
                                        genre_dict[curr_g].append(entry)

                        else:
                            # --- 【常规通道】 ---
                            parts = []
                            if '#' in clean_line:
                                parts = clean_line.split('#')
                            elif ',' in clean_line:
                                parts = clean_line.split(',')
                            else:
                                parts = [clean_line]

                            url, name = "", ""
                            for p in parts:
                                p = p.strip()
                                if '://' in p and not url:
                                    u_m = re.search(r'(https?://[^\s\"\'#$]+)', p)
                                    if u_m: url = u_m.group(1)
                                elif p and not name:
                                    name = p

                            final_n = name if name else (temp_name if temp_name else f"第{scan_count}集")
                            final_n = final_n.replace('|', ' - ')
                            if url:
                                genre_dict[curr_g].append(f"{final_n}${url}")

                        page_item_count += 1
                        temp_name = ""; pending_first_ep_name = ""

            # 4. 组装输出
            from_names, urls_list = [], []
            ordered_keys = []
            if "默认分类" in genre_dict and genre_dict["默认分类"]:
                ordered_keys.append("默认分类")
            for g in genre_order:
                if g != "默认分类" and g not in ordered_keys: ordered_keys.append(g)

            for g in ordered_keys:
                if g in genre_dict and genre_dict[g]:
                    from_names.append(g.replace('$', '').strip() or "其他")
                    urls_list.append("#".join(genre_dict[g]))
            
            if not from_names:
                from_names, urls_list = ["解析完毕"], ["本页无更多内容$http://0.0.0.0"]

            # 5. 简介信息封装
            try:
                f_size_raw = os.path.getsize(f_path)
                f_size_str = self._format_size(f_size_raw) if hasattr(self, '_format_size') else f"{f_size_raw / 1024 / 1024:.1f}M"
            except:
                f_size_str = "未知"

            display_total = final_total if has_sync else scan_count
            v_content = f"📊 数据统计: {display_total} 条有效数据\n"
            v_content += f"⚖️ 文件大小: {f_size_str}\n"
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

#♦解析优质代码结束🔚
    def playerContent(self, flag, id, vipFlags):
        # 1. 提取真实 URL
        url = id.split('$')[-1] if '$' in id else id
        url = url.strip()

        # 2. 强力去反代（解决 down.xxx.cn/http://... 这种嵌套）
        match = re.search(r'/(https?://|vip\.|dytt-|cdn\.|img\.)', url)
        if match:
            url = url[match.start()+1:]
            if not url.startswith("http"): url = "https://" + url

        # 3. 注入欺骗头 (UA 和 Referer)
        return {
            "url": url, 
            "header": {
                "User-Agent": "Mozilla/5.0 (Linux; Android 12; mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 okhttp/3.15.0",
                "Referer": url.split('/', 3)[0] + '/', # 自动取域名作为来源
                "Connection": "keep-alive"
            }, 
            "parse": 0
        }
#
    def searchContent(self, key, quick):
        res = []
        for f in self.cache.get("all_files", []):
            if key in os.path.basename(f):
                res.append({
                    "vod_id": base64.b64encode(f"P|0|{f}".encode()).decode().rstrip('='),
                    "vod_name": os.path.basename(f).replace(".txt", ""),
                    "vod_pic": "https://img.icons8.com/color/200/txt.png",
                    "vod_remarks": "本地匹配"
                })
        return {"list": res}

    def destroy(self): gc.collect() 
