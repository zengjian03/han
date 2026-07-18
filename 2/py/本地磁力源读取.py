# -*- coding: utf-8 -*-
import os, base64, gc, re, shutil, zipfile, urllib.parse
from base.spider import Spider

class Spider(Spider):
    # ==========================================================================
    # 💎 【1. 核心导航配置区】 - Excel+文本 双引擎智能分片门阀极速版 v100.1   磁力
    # ==========================================================================
    SCAN_DIR_LIST = [
                  "TVData",               #👈小百合专用文件夹，把磁力文件放在这里# 👈 u盘也用这个文件夹 
               # "tvbox",           #👈电视📺专用文件夹，把磁力文件放在这里# 👈 u盘也用这个文件夹                                      
              # "lz",  "江湖"      # 👈 前面加#关闭   这里可以修改任意大佬包名 
          ]  
    P2P_PAGE_SIZE = 20
    LSX_PAGE_SIZE = 10      # 🎯 门阀配置：Excel 专属小分片
    BLACK_FINGERPRINTS = [b'termux']

    def __init__(self):
        super().__init__()
        self.inited = False
        self.cache = {"categories": [], "file_index": {}} 
        self.all_files_for_search = [] 
        self.adaptive_tag = "Magnet_Xlsx_Fast" 

    def getName(self):
        return f"⚡_PureMagnet_v100.1_{self.adaptive_tag}"

    def _format_size(self, size_bytes):
        if size_bytes < 1024: return f"{int(size_bytes)}B"
        if size_bytes < 1048576: return f"{int(size_bytes/1024)}K"  
        return f"{size_bytes/1048576:.1f}M"

    # ==========================================================================
    # 🧪 【极致提速核心：Excel 底层二进制流式碰撞引擎】
    # ==========================================================================
    def _extract_ed2k_name(self, ed2k):
        """ 从电驴链接中提取并清洗标准文件名 """
        name = None
        file_match = re.search(r'\|file\|([^|]+)\|', ed2k, re.I)
        if file_match:
            name = file_match.group(1)
        else:
            last_slash = ed2k.rfind('/')
            if last_slash != -1:
                temp = ed2k[last_slash + 1:]
                pipe_pos = temp.find('|')
                if pipe_pos != -1: name = temp[:pipe_pos]
                else: name = temp
        
        if name:
            name = name.replace('\n', ' ').replace('\r', ' ').strip()
            try: name = urllib.parse.unquote(name)
            except: pass
            if len(name) > 100: name = name[:97] + '...'
        return name

    def _fast_check_xlsx(self, f_path):
        """ 🔥 首页优化版：底层二进制轻量盲扫门禁。完美解决隐藏在单个 Sheet 或公式里的链接显示问题 """
        try:
            if not zipfile.is_zipfile(f_path): return False
            with zipfile.ZipFile(f_path, 'r') as zf:
                for name in zf.namelist():
                    if name.endswith('.xml'):
                        try:
                            with zf.open(name) as f:
                                # 核心优化：每次只读前 48KB 字节流片段，绝不全量解压，杜绝内存阻塞
                                chunk = f.read(49152).lower()
                                if b"magnet:?" in chunk or b"ed2k://" in chunk:
                                    return True
                        except: pass
        except: pass
        return False

    def _read_xlsx_to_pure_pairs_full(self, f_path):
        """ 🎬 详情页/二级列表专属：全量无漏深度正则提纯引擎（点击时才触发） """
        pairs = []
        try:
            if not zipfile.is_zipfile(f_path): return pairs
            all_text = ""
            with zipfile.ZipFile(f_path, 'r') as zf:
                for name in zf.namelist():
                    if name.endswith('.xml'):
                        try:
                            content = zf.read(name).decode('utf-8', errors='ignore')
                            all_text += content
                        except: pass
            
            if not all_text: return pairs

            magnet_pattern = re.compile(r'magnet:\?[^\s\'"<>《》]+', re.I)
            magnets = sorted(list(set(magnet_pattern.findall(all_text))))
            
            ed2k_pattern = re.compile(r'ed2k://[^\s\'"<>《》]+', re.I)
            ed2ks = sorted(list(set(ed2k_pattern.findall(all_text))))

            for idx, magnet in enumerate(magnets):
                name_match = re.search(r'dn=([^&]+)', magnet)
                if name_match:
                    try: name = urllib.parse.unquote(name_match.group(1))
                    except: name = f"磁力链接 {idx+1}"
                else:
                    name = f"磁力链接 {idx+1}"
                name = name.replace('\n', ' ').replace('\r', ' ').strip().replace('|', ' - ')
                if len(name) > 100: name = name[:97] + '...'
                pairs.append(f"{name}${magnet}")

            for idx, ed2k in enumerate(ed2ks):
                name = self._extract_ed2k_name(ed2k)
                if not name or len(name) < 1:
                    name = f"电驴链接 {idx+1}"
                name = name.replace('|', ' - ')
                pairs.append(f"{name}${ed2k}")
        except: pass
        return pairs

    # ==========================================================================
    # 📂 【核心初始化：全量快速索引门禁，多格式一秒聚合进首页】
    # ==========================================================================
    def init(self, extend):
        if self.inited: return

        scan_roots = ["/storage/emulated/0"]
        try:
            if os.path.exists("/storage"):
                for s in os.listdir("/storage"):
                    if s not in ["self", "emulated", "knox", "sdcard0", "runtime"]:
                        scan_roots.append(os.path.join("/storage", s))
        except: pass
        if extend and os.path.isdir(extend): scan_roots.insert(0, extend)

        all_raw_cats, final_index, unique_paths = [], {}, set()
        self.all_files_for_search = [] 

        for root_p in scan_roots:
            is_ext = not root_p.startswith("/storage/emulated/0")
            for zone_weight, target in enumerate(self.SCAN_DIR_LIST):
                base_p = os.path.join(root_p, target)
                if not os.path.isdir(base_p): continue
                
                is_special_dir = target.lower() in ["tvbox", "bhh", "bh"]
                star = "☆" if is_ext else "" 

                for root, dirs, files in os.walk(base_p):
                    rel_path = os.path.relpath(root, base_p)
                    depth = 0 if rel_path == "." else len(rel_path.split(os.sep))

                    if depth > 3:
                        dirs[:] = []
                        continue
                    
                    if not is_special_dir and depth == 0:
                        continue

                    valid_files_in_folder = []
                    for f in files:
                        f_lower = f.lower()
                        if not any(f_lower.endswith(ext) for ext in ['.txt', '.ed2k', '.torrent', '.xlsx']): continue
                        
                        f_path = os.path.join(root, f)
                        try:
                            # 🚀 采用全新升级的轻量全局快扫二进制门禁
                            if f_lower.endswith('.xlsx'):
                                if self._fast_check_xlsx(f_path):
                                    valid_files_in_folder.append(f_path)
                                    self.all_files_for_search.append(f_path)
                            else:
                                with open(f_path, 'rb') as f_check:
                                    chunk_raw = f_check.read(49152) 
                                    if any(bad in chunk_raw for bad in self.BLACK_FINGERPRINTS): continue
                                    
                                    chunk_low = chunk_raw.lower()
                                    if b"magnet:?" in chunk_low or b"ed2k://" in chunk_low:
                                        valid_files_in_folder.append(f_path)
                                        self.all_files_for_search.append(f_path)
                        except: continue

                    if not valid_files_in_folder: continue
                    
                    real_root = os.path.realpath(root)
                    if real_root in unique_paths: continue
                    unique_paths.add(real_root)

                    folder_display = target if rel_path == "." else f"{target}/{rel_path.replace(os.sep, '/')}"

                    for f_path in valid_files_in_folder:
                        try:
                            st_info = os.stat(f_path)
                            sz_raw = st_info.st_size
                            
                            f_base = os.path.basename(f_path).rsplit('.', 1)[0]
                            u_key = f"{folder_display}/{f_base}({self._format_size(sz_raw)}){star}"          
                            
                            tid = base64.b64encode(f"SINGLE|{f_path}".encode()).decode().rstrip('=')
                            final_index[tid] = [f_path]
                            all_raw_cats.append({
                                "type_id": tid, "type_name": u_key, 
                                "sk": (zone_weight, 1, 1, sz_raw, 1 if is_ext else 0, folder_display, f_base)
                            })
                        except: continue

        self.cache["categories"] = [{"type_id": c["type_id"], "type_name": c["type_name"]} for c in sorted(all_raw_cats, key=lambda x: x['sk'])]
        self.cache["file_index"] = final_index
        self.inited = True
        gc.collect()

    def homeContent(self, filter): 
        return {"class": self.cache["categories"]}

    # ==========================================================================
    # 📂 【二级列表引擎】 - 深度进化：Excel 采用分块流碰撞计数，维持毫秒响应
    # ==========================================================================
    def categoryContent(self, tid, pg, filter, ext):
        if str(pg) != "1": return {"list": []}
        v_list = []
        try:
            target_files = self.cache["file_index"].get(tid, [])
            
            for f_path in target_files:
                if not os.path.exists(f_path): continue
                
                f_name = os.path.basename(f_path).rsplit('.', 1)[0]
                is_xlsx_format = f_path.lower().endswith('.xlsx')
                
                # 🎯 智能分片门阀：如果是 xlsx 则采用 LSX_PAGE_SIZE(10条)，文本采用 P2P_PAGE_SIZE(30条)
                limit = getattr(self, 'LSX_PAGE_SIZE', 10) if is_xlsx_format else getattr(self, 'P2P_PAGE_SIZE', 30)
                
                magnet_count = 0
                ed2k_count = 0
                chunk_fingerprints = []
                
                if is_xlsx_format:
                    # 🚀 Excel 深度流优化：采用 64KB 二进制块流式碰撞计数，不产生大内存拼接
                    try:
                        with zipfile.ZipFile(f_path, 'r') as zf:
                            for name in zf.namelist():
                                if name.endswith('.xml'):
                                    with zf.open(name) as f_xml:
                                        while True:
                                            chunk = f_xml.read(65536)
                                            if not chunk: break
                                            chunk_low = chunk.lower()
                                            magnet_count += chunk_low.count(b'magnet:?')
                                            ed2k_count += chunk_low.count(b'ed2k://')
                    except: pass
                    real_count = magnet_count + ed2k_count
                else:
                    # 纯文本二进制高速碰撞计数引擎
                    with open(f_path, 'rb') as f_b:
                        while True:
                            chunk = f_b.read(65536)
                            if not chunk: break
                            chunk_low = chunk.lower()
                            magnet_count += chunk_low.count(b'magnet:?')
                            ed2k_count += chunk_low.count(b'ed2k://')
                    
                    real_count = magnet_count + ed2k_count
                    if real_count == 0:
                        total_physical_lines = 0
                        with open(f_path, 'rb') as f_b:
                            for line in f_b: total_physical_lines += 1
                        real_count = (total_physical_lines + 1) // 2

                parts = (real_count + limit - 1) // limit if real_count > 0 else 1
                parts = int(parts)
                is_mainly_ed2k = ed2k_count > 0

                for i in range(parts):
                    v_id_str = "P|%d|%d|%s" % (i, real_count, f_path)
                    v_id = base64.b64encode(v_id_str.encode('utf-8')).decode('utf-8').rstrip('=')
                    
                    d_name = "%s (第%d/%d集)" % (f_name, i+1, parts) if parts > 1 else f_name
                    v_remarks = f"第{i+1}页  共{real_count}条"
                    
                    # 🎯 三轨自适应图标分流：Excel 独享高清电影图标，文本按特征区分
                    if is_xlsx_format:
                        v_pic = "https://bpic.51yuansu.com/pic3/cover/02/16/52/6784c97004cfb_800.jpg?x-oss-process=image/sharpen,100"
                    elif is_mainly_ed2k:
                        v_pic = "https://img2.baidu.com/it/u=3561577485,3196894867&fm=253&fmt=auto&app=138&f=PNG?w=243&h=243"
                    else:
                        v_pic = "https://img.icons8.com/color/200/magnet.png"
                    
                    v_list.append({
                        "vod_id": v_id, 
                        "vod_name": d_name,
                        "vod_pic": v_pic,
                        "vod_remarks": v_remarks
                    })
        except Exception as e:
            v_list.append({"vod_name": "数据载入失败", "vod_remarks": str(e)})
            
        return {"list": v_list}

    # ==========================================================================
    # 💎 【核心解析：无漏提取流，完美保留首集高保真输出】
    # ==========================================================================
    def detailContent(self, array):
        try:
            v_id_raw = str(array[0])
            v_id_raw += "=" * ((4 - len(v_id_raw) % 4) % 4)
            raw = base64.b64decode(v_id_raw).decode('utf-8', 'ignore')
            
            parts_info = raw.split('|')
            if len(parts_info) >= 4:
                p_idx = int(parts_info[1])
                final_total = parts_info[2]  
                f_path = parts_info[3]
                has_sync = True
            else:
                p_idx = int(parts_info[1]) if len(parts_info) > 1 else 0
                f_path = parts_info[-1]
                final_total = "0"
                has_sync = False
            
            if not os.path.exists(f_path): return {"list": []}
            is_xlsx_format = f_path.lower().endswith('.xlsx')

            # 🎯 智能分片门阀：解析端步长与生成端保持严格咬合
            limit = getattr(self, 'LSX_PAGE_SIZE', 10) if is_xlsx_format else getattr(self, 'P2P_PAGE_SIZE', 30)
            start_pos = p_idx * limit
            end_pos = (p_idx + 1) * limit

            P2P_ZONE = "[⚡]电驴磁力线路"
            genre_dict = {P2P_ZONE: []}
            scan_count, page_item_count = 0, 0

            if is_xlsx_format:
                # 🎯 详情页延迟提纯技术：点进来时精准正则解析该文件的内容，防止整体拖慢系统
                xlsx_pairs = self._read_xlsx_to_pure_pairs_full(f_path)
                for pair in xlsx_pairs:
                    if '$' in pair:
                        scan_count += 1
                        if scan_count <= start_pos: continue
                        if scan_count > end_pos: break
                        genre_dict[P2P_ZONE].append(pair)
                        page_item_count += 1
            else:
                enc = 'utf-8'
                with open(f_path, 'rb') as f_b:
                    h = f_b.read(4096)
                    for e in ['utf-8', 'gb18030', 'cp936']:
                        try: h.decode(e); enc = e; break
                        except: pass

                temp_name = ""
                with open(f_path, 'r', encoding=enc, errors='ignore') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#EXTM3U") or line.startswith("{"): continue

                        if '://' in line or 'ed2k://' in line or 'magnet:?' in line:
                            scan_count += 1
                            if scan_count <= start_pos: 
                                if ',' in line and not line.startswith('http'): pass
                                else: temp_name = ""
                                continue
                            if scan_count > end_pos: break 

                            clean_line = line.replace('$$$', '#').strip()
                            clean_line = re.sub(r'\w+[-]?\w+=["\'].*?["\']', '', clean_line).strip()

                            mkv_match = re.search(r'^([^,]+),(ed2k://\|file\|[^|]+\|\d+\|[A-F0-9]{32}\|/|magnet:\?[^\s\"\'#$]+)', clean_line, re.I)
                            if mkv_match:
                                m_name, m_url = mkv_match.group(1).strip(), mkv_match.group(2).strip()
                                m_name = m_name.replace('|', ' - ')
                                genre_dict[P2P_ZONE].append(f"{m_name}${m_url}")
                                page_item_count += 1
                            elif '$' in clean_line and not clean_line.endswith('$'):
                                line_parts = clean_line.split(',', 1)
                                base_name = line_parts[0].strip() if len(line_parts) > 1 else temp_name
                                content_all = line_parts[1].strip() if len(line_parts) > 1 else clean_line

                                eps = content_all.split('$')
                                for idx, ep in enumerate(eps):
                                    if 'ed2k://' not in ep.lower() and 'magnet:?' not in ep.lower(): continue
                                    sub_parts = ep.split('#')
                                    u = sub_parts[0].strip() if ('://' in sub_parts[0] or 'magnet:?' in sub_parts[0]) else sub_parts[1].strip()
                                    n = sub_parts[1].strip() if ('://' in sub_parts[0] or 'magnet:?' in sub_parts[0]) else sub_parts[0].strip()
                                    
                                    u_m = re.search(r'(ed2k://\|file\|[^|]+\|\d+\|[A-F0-9]{32}\|/|magnet:\?[^\s\"\'#$]+)', u, re.I)
                                    if u_m:
                                        real_url = u_m.group(1)
                                        if real_url.lower().startswith('ed2k://'):
                                            ed2k_name_match = re.search(r'ed2k://\|file\|([^|]+)\|', real_url, re.I)
                                            if ed2k_name_match: n = ed2k_name_match.group(1)
                                        
                                        final_n = n if n else (f"{base_name} 第1集" if idx == 0 and base_name else f"第{idx+1:02d}集")
                                        genre_dict[P2P_ZONE].append(f"{final_n}${real_url}")
                                page_item_count += 1
                            else:
                                parts = clean_line.split(',') if ',' in clean_line else [clean_line]
                                url, name = "", ""
                                for p in parts:
                                    p = p.strip()
                                    if ('ed2k://' in p.lower() or 'magnet:?' in p.lower()) and not url:
                                        u_m = re.search(r'(ed2k://\|file\|[^|]+\|\d+\|[A-F0-9]{32}\|/|magnet:\?[^\s\"\'#$]+)', p, re.I)
                                        if u_m: 
                                            url = u_m.group(1)
                                            if url.lower().startswith('ed2k://'):
                                                ed2k_name_match = re.search(r'ed2k://\|file\|([^|]+)\|', url, re.I)
                                                if ed2k_name_match: name = ed2k_name_match.group(1)
                                    elif p and not name:
                                        name = p

                                final_n = name if name else (temp_name if temp_name else f"数据行_第{scan_count}条")
                                final_n = final_n.replace('|', ' - ')
                                if url:
                                    genre_dict[P2P_ZONE].append(f"{final_n}${url}")
                                    page_item_count += 1
                            temp_name = ""
                        else:
                            if len(line) > 1 and not line.startswith('#'): temp_name = line

            from_names = [P2P_ZONE]
            urls_list = ["#".join(genre_dict[P2P_ZONE])] if genre_dict[P2P_ZONE] else ["本片区无更多内容$http://0.0.0.0"]
            
            try: f_size_str = self._format_size(os.path.getsize(f_path))
            except: f_size_str = "未知"

            display_total = final_total if has_sync else scan_count
            v_content = f"📊 数据统计: 共 {display_total} 条有效链接\n⚖️ 文本大小: {f_size_str}\n🚩 当前分页: 第 {start_pos + 1} 至 {min(int(display_total), end_pos)} 条\n✅ 本页提取: {page_item_count} 条载入成功\n📍 物理路径: {f_path}"
            
            return {"list": [{
                "vod_name": os.path.basename(f_path).rsplit('.', 1)[0],
                "vod_play_from": "$$$".join(from_names),
                "vod_play_url": "$$$".join(urls_list),
                "vod_content": v_content
            }]}
        except Exception as e:
            return {"list": [{"vod_name": "解析失败", "vod_content": str(e)}]}

    def playerContent(self, flag, id, vipFlags):
        url = id.split('$')[-1] if '$' in id else id
        url = url.strip()
        if url.lower().startswith('ed2k://') or url.lower().startswith('magnet:'):
            return {
                "url": url,
                "parse": 0,
                "header": {
                    "ijk-timeout": "980000000",       
                    "timeout": "980",                 
                    "rtmp_transport": "tcp",          
                    "Buffer-Size": "1048576"          
                }
            }
        return {"url": url, "parse": 0}

    def searchContent(self, key, quick):
        res = []
        for f in self.all_files_for_search:
            if key in os.path.basename(f):
                res.append({
                    "vod_id": base64.b64encode(f"P|0|0|{f}".encode()).decode().rstrip('='),
                    "vod_name": os.path.basename(f).replace(".txt", "").replace(".xlsx", ""),
                    "vod_pic": "https://img.icons8.com/color/200/magnet.png",
                    "vod_remarks": "精准搜索"
                })
        return {"list": res}

    def destroy(self): 
        try:
            safe_only_path = "/storage/emulated/0/.tmp"
            if os.path.exists(safe_only_path):
                for root, dirs, files in os.walk(safe_only_path):
                    for f in files:
                        if f.lower().endswith(('.tmp', '.cache')):
                            try: os.remove(os.path.join(root, f))
                            except: pass
        except: pass
        finally:
            gc.collect()