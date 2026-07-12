import { _ } from 'assets://js/lib/cat.js';

const host = 'https://www.youku.com';
const PC_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36';
const COOKIE = 'cna=VvNvGX3e0ywCAavVEXlnA2bg; __ysuid=1626676228345Rl1; __ayft=1652434048647; __arycid=dm-1-00; __arcms=dm-1-00; __ayvstp=85; __arpvid=1667204023100cWWdgM-1667204023112; __ayscnt=10; __aypstp=60; isg=BBwcqxvvk3BxkWQGugbLpUSf7TrOlcC_U7GAj_YdfYfvQbzLHqYGT4Hgp6m5TvgX; tfstk=c3JOByYUH20ilVucLOhh0pCtE40lZfGc-PjLHLLfuX7SWNyAiQvkeMBsIw7PWDC..; l=eBQguS-PjdJFGJT-BOfwourza77OSIRA_uPzaNbMiOCPOb1B5UxfW6yHp4T6C3GVhsGJR3rp2umHBeYBqQd-nxvOF8qmSVDmn';

const globalSessionCache = {};

async function init(cfg) {}

async function request(url) {
    const res = await req(url, {
        method: 'get',
        headers: {
            'User-Agent': PC_UA,
            'Cookie': COOKIE,
            'Referer': 'https://www.youku.com'
        }
    });
    return JSON.parse(res.content);
}

// 首页与筛选配置项（年份已从2026年开始排列）
async function home() {
    const classes = [
        { type_id: '电视剧', type_name: '电视剧' },
        { type_id: '电影', type_name: '电影' },
        { type_id: '综艺', type_name: '综艺' },
        { type_id: '动漫', type_name: '动漫' },
        { type_id: '少儿', type_name: '少儿' },
        { type_id: '纪录片', type_name: '纪录片' },
        { type_id: '文化', type_name: '文化' },
        { type_id: '亲子', type_name: '亲子' },
        { type_id: '教育', type_name: '教育' },
        { type_id: '搞笑', type_name: '搞笑' },
        { type_id: '生活', type_name: '生活' },
        { type_id: '体育', type_name: '体育' },
        { type_id: '音乐', type_name: '音乐' },
        { type_id: '游戏', type_name: '游戏' }
    ];

    const filters = {
        "电视剧": [
            { "key": "main_area", "name": "全部地区", "value": [{ "n": "全部地区", "v": "" }, { "n": "内地剧", "v": "中国内地" }, { "n": "港剧", "v": "中国香港" }, { "n": "台剧", "v": "中国台湾" }, { "n": "韩剧", "v": "韩国" }, { "n": "美剧", "v": "美国" }, { "n": "英剧", "v": "英国" }, { "n": "日剧", "v": "日本" }, { "n": "泰剧", "v": "泰国" }] },
            { "key": "tags", "name": "全部类型", "value": [{ "n": "全部类型", "v": "" }, { "n": "青春", "v": "青春" }, { "n": "古装", "v": "古装" }, { "n": "爱情", "v": "爱情" }, { "n": "都市", "v": "都市" }, { "n": "喜剧", "v": "喜剧,搞笑" }, { "n": "战争", "v": "战争" }, { "n": "军旅", "v": "军旅" }, { "n": "谍战", "v": "谍战" }, { "n": "偶像", "v": "偶像" }, { "n": "警匪", "v": "警匪" }, { "n": "冒险", "v": "冒险" }, { "n": "穿越", "v": "穿越" }, { "n": "仙侠", "v": "仙侠" }, { "n": "武侠", "v": "武侠" }, { "n": "悬疑", "v": "悬疑" }, { "n": "罪案", "v": "罪案" }, { "n": "家庭", "v": "家庭" }, { "n": "历史", "v": "历史" }, { "n": "年代", "v": "年代" }, { "n": "农村", "v": "农村" }] },
            { "key": "year", "name": "全部年份", "value": [{ "n": "全部年份", "v": "" }, { "n": "2026", "v": "2026" }, { "n": "2025", "v": "2025" }, { "n": "2024", "v": "2024" }, { "n": "2023", "v": "2023" }, { "n": "2022", "v": "2022" }, { "n": "2021", "v": "2021" }, { "n": "2020", "v": "2020" }, { "n": "2019", "v": "2019" }, { "n": "2018", "v": "2018" }, { "n": "2017", "v": "2017" }, { "n": "2016", "v": "2016" }, { "n": "2015", "v": "2015" }, { "n": "2014-2011", "v": "2011-2014" }, { "n": "更早", "v": "-2010" }] },
            { "key": "status", "name": "全部规格", "value": [{ "n": "全部规格", "v": "" }, { "n": "全网独播", "v": "1" }, { "n": "优酷自制", "v": "2" }, { "n": "已完结", "v": "3" }, { "n": "即将上线", "v": "4" }, { "n": "短剧", "v": "5" }] },
            { "key": "pay_type", "name": "付费类型", "value": [{ "n": "付费类型", "v": "" }, { "n": "免费", "v": "0" }, { "n": "VIP", "v": "2" }, { "n": "付费", "v": "1" }] },
            { "key": "sort", "name": "综合排序", "value": [{ "n": "综合排序", "v": "" }, { "n": "热度最高", "v": "7" }, { "n": "最新上线", "v": "1" }, { "n": "最好评", "v": "3" }, { "n": "最多播放", "v": "2" }] }
        ],
        "电影": [
            { "key": "main_area", "name": "全部地区", "value": [{ "n": "全部地区", "v": "" }, { "n": "内地", "v": "中国内地" }, { "n": "中国香港", "v": "中国香港" }, { "n": "中国台湾", "v": "中国台湾" }, { "n": "美国", "v": "アメリカ" }, { "n": "印度", "v": "印度" }, { "n": "日韩", "v": "韩国,日本" }, { "n": "泰国", "v": "泰国" }, { "n": "欧洲", "v": "欧洲" }] },
            { "key": "tags", "name": "全部类型", "value": [{ "n": "全部类型", "v": "" }, { "n": "喜剧", "v": "喜剧,搞笑" }, { "n": "动作", "v": "动作" }, { "n": "怪兽", "v": "怪兽" }, { "n": "战争", "v": "战争" }, { "n": "爱情", "v": "爱情" }, { "n": "悬疑", "v": "悬疑" }, { "n": "武侠", "v": "武侠" }, { "n": "奇幻", "v": "奇幻" }, { "n": "科幻", "v": "科幻" }, { "n": "冒险", "v": "冒险" }, { "n": "警匪", "v": "警匪" }, { "n": "动画", "v": "动画" }, { "n": "惊悚", "v": "惊悚" }, { "n": "犯罪", "v": "犯罪" }, { "n": "恐怖", "v": "恐怖" }, { "n": "剧情", "v": "剧情" }, { "n": "历史", "v": "历史" }, { "n": "纪录片", "v": "纪录片" }, { "n": "传记", "v": "传记" }, { "n": "歌舞", "v": "歌舞" }, { "n": "短片", "v": "短片" }, { "n": "其他", "v": "其他" }] },
            { "key": "source", "name": "全部规格", "value": [{ "n": "全部规格", "v": "" }, { "n": "院线", "v": "1" }, { "n": "网络电影", "v": "0" }, { "n": "独播", "v": "2" }, { "n": "高清修复", "v": "3" }, { "n": "1080P", "v": "4" }] },
            { "key": "year", "name": "全部年份", "value": [{ "n": "全部年份", "v": "" }, { "n": "2026", "v": "2026" }, { "n": "2025", "v": "2025" }, { "n": "2024", "v": "2024" }, { "n": "2023", "v": "2023" }, { "n": "2022", "v": "2022" }, { "n": "2021", "v": "2021" }, { "n": "2020", "v": "2020" }, { "n": "2019", "v": "2019" }, { "n": "2018", "v": "2018" }, { "n": "2017", "v": "2017" }, { "n": "2016", "v": "2016" }, { "n": "2015", "v": "2015" }, { "n": "2014-2010", "v": "2010-2014" }, { "n": "2009-2000", "v": "2000-2009" }, { "n": "90年代", "v": "1990-1999" }, { "n": "80年代", "v": "1980-1989" }, { "n": "70年代", "v": "1970-1979" }, { "n": "更早", "v": "-1969" }] },
            { "key": "pay_type", "name": "付费类型", "value": [{ "n": "付费类型", "v": "" }, { "n": "免费", "v": "0" }, { "n": "会员", "v": "2" }, { "n": "点播", "v": "1" }] },
            { "key": "sort", "name": "综合排序", "value": [{ "n": "综合排序", "v": "" }, { "n": "热度最高", "v": "7" }, { "n": "最多播放", "v": "2" }, { "n": "最新上线", "v": "1" }, { "n": "最好评", "v": "3" }] },
            { "key": "tag_label_name", "name": "为你推荐", "value": [{ "n": "为你推荐", "v": "" }, { "n": "高分必看", "v": "高分必看" }, { "n": "卖座电影", "v": "卖座电影" }, { "n": "小说改编", "v": "小说改编" }, { "n": "铁血硬汉", "v": "铁血硬汉" }, { "n": "视效大片", "v": "视效大片" }, { "n": "漫画改编", "v": "漫画改编" }, { "n": "绝地求生", "v": "绝地求生" }, { "n": "真人真事改编", "v": "真人真事改编" }, { "n": "范伟", "v": "范伟" }, { "n": "火爆枪战", "v": "火爆枪战" }, { "n": "影史经典", "v": "影史经典" }, { "n": "拯救世界", "v": "拯救世界" }, { "n": "万茜", "v": "万茜" }, { "n": "马思纯", "v": "马思纯" }, { "n": "王俊凯", "v": "王俊凯" }, { "n": "豪华阵容", "v": "豪华阵容" }, { "n": "李玉", "v": "李玉" }, { "n": "无厘头喜剧", "v": "无厘头喜剧" }, { "n": "超能力", "v": "超能力" }, { "n": "欢喜搭档", "v": "欢喜搭档" }] }
        ],
        "综艺": [
            { "key": "main_area", "name": "全部地区", "value": [{ "n": "全部地区", "v": "" }, { "n": "内地", "v": "中国内地" }, { "n": "中国台湾", "v": "中国台湾" }, { "n": "美国", "v": "美国" }, { "n": "英国", "v": "英国" }] },
            { "key": "tags", "name": "全部类型", "value": [{ "n": "全部类型", "v": "" }, { "n": "偶像", "v": "偶像" }, { "n": "舞蹈", "v": "舞蹈" }, { "n": "音乐", "v": "音乐" }, { "n": "情感", "v": "情感" }, { "n": "喜剧", "v": "喜剧,搞笑" }, { "n": "体育", "v": "体育" }, { "n": "游戏", "v": "游戏" }, { "n": "相声", "v": "相声" }, { "n": "婚恋", "v": "婚恋" }, { "n": "时尚", "v": "时尚" }, { "n": "晚会", "v": "晚会" }, { "n": "明星访谈", "v": "明星访谈" }, { "n": "亲子", "v": "亲子" }, { "n": "生活", "v": "生活" }, { "n": "文化", "v": "文化" }, { "n": "美食", "v": "美食" }, { "n": "旅游", "v": "旅游" }, { "n": "益智", "v": "益智" }] },
            { "key": "year", "name": "全部年份", "value": [{ "n": "全部年份", "v": "" }, { "n": "2026", "v": "2026" }, { "n": "2025", "v": "2025" }, { "n": "2024", "v": "2024" }, { "n": "2023", "v": "2023" }, { "n": "2022", "v": "2022" }, { "n": "2021", "v": "2021" }, { "n": "2020", "v": "2020" }, { "n": "2019", "v": "2019" }, { "n": "2018", "v": "2018" }, { "n": "2017", "v": "2017" }, { "n": "2016", "v": "2016" }, { "n": "2015", "v": "2015" }, { "n": "2014-2011", "v": "2011-2014" }, { "n": "更早", "v": "-2010" }] },
            { "key": "status", "name": "全部规格", "value": [{ "n": "全部规格", "v": "" }, { "n": "优酷自制", "v": "2" }, { "n": "优酷独播", "v": "1" }, { "n": "电视综艺", "v": "6" }, { "n": "已完结", "v": "3" }, { "n": "即将上线", "v": "4" }] },
            { "key": "pay_type", "name": "付费类型", "value": [{ "n": "付费类型", "v": "" }, { "n": "免费", "v": "0" }, { "n": "VIP", "v": "2" }, { "n": "付费", "v": "1" }] },
            { "key": "sort", "name": "热度最高", "value": [{ "n": "热度最高", "v": "" }, { "n": "最新更新", "v": "8" }, { "n": "最近开播", "v": "9" }, { "n": "最多评论", "v": "4" }] },
            { "key": "tag_label_name", "name": "为你推荐", "value": [{ "n": "为你推荐", "v": "" }, { "n": "舞台竞演", "v": "舞台竞演" }, { "n": "刘雨昕", "v": "刘雨昕" }, { "n": "王一博", "v": "王一博" }, { "n": "韩庚", "v": "韩庚" }, { "n": "李承铉", "v": "李承铉" }, { "n": "户外竞技", "v": "户外竞技" }, { "n": "浙江卫视", "v": "浙江卫视" }, { "n": "东方卫视", "v": "东方卫视" }, { "n": "岳云鹏", "v": "岳云鹏" }, { "n": "王迅", "v": "王迅" }, { "n": "杨迪", "v": "杨迪" }, { "n": "杨超越", "v": "杨超越" }, { "n": "黄明昊", "v": "黄明昊" }, { "n": "郭京飞", "v": "郭京飞" }, { "n": "欧阳娜娜", "v": "欧阳娜娜" }, { "n": "德云社", "v": "德云社" }, { "n": "郑恺", "v": "郑恺" }, { "n": "华少", "v": "华少" }, { "n": "郭德纲", "v": "郭德纲" }, { "n": "贾玲", "v": "贾玲" }] }
        ],
        "动漫": [
            { "key": "sort", "name": "综合排序", "value": [{ "n": "综合排序", "v": "" }, { "n": "最多播放", "v": "2" }, { "n": "最好评", "v": "3" }, { "n": "最新上线", "v": "1" }] },
            { "key": "main_area", "name": "全部地区", "value": [{ "n": "全部地区", "v": "" }, { "n": "内地", "v": "中国内地" }, { "n": "日本", "v": "日本" }, { "n": "美国", "v": "美国" }, { "n": "中国台湾", "v": "中国台湾" }, { "n": "其他", "v": "其他" }] },
            { "key": "tags", "name": "全部类型", "value": [{ "n": "全部类型", "v": "" }, { "n": "热血", "v": "热血,战斗" }, { "n": "励志", "v": "励志" }, { "n": "玄幻", "v": "玄幻" }, { "n": "古风", "v": "历史,古风" }, { "n": "恋爱", "v": "恋爱" }, { "n": "青春", "v": "青春" }, { "n": "校园", "v": "校园" }, { "n": "运动", "v": "社团,运动" }, { "n": "科幻", "v": "科幻" }, { "n": "冒险", "v": "冒险" }, { "n": "魔法", "v": "魔法" }, { "n": "日常", "v": "日常" }, { "n": "治愈", "v": "治愈" }, { "n": "机战", "v": "机战" }, { "n": "推理", "v": "推理" }, { "n": "都市", "v": "都市" }, { "n": "小说改", "v": "小说改编" }, { "n": "游戏改", "v": "游戏改编" }, { "n": "漫画改", "v": "漫画改编" }, { "n": "动态漫", "v": "动态漫画" }, { "n": "特摄", "v": "特摄" }, { "n": "布袋戏", "v": "布袋戏" }] },
            { "key": "completed", "name": "连载情况", "value": [{ "n": "连载情况", "v": "" }, { "n": "更新中", "v": "0" }, { "n": "已完结", "v": "1" }] },
            { "key": "pay_type", "name": "付费类型", "value": [{ "n": "付费类型", "v": "" }, { "n": "免费", "v": "0" }, { "n": "会员", "v": "2" }] },
            { "key": "year", "name": "全部年份", "value": [{ "n": "全部年份", "v": "" }, { "n": "2026", "v": "2026" }, { "n": "2025", "v": "2025" }, { "n": "2024", "v": "2024" }, { "n": "2023", "v": "2023" }, { "n": "2022", "v": "2022" }, { "n": "2021", "v": "2021" }, { "n": "2020", "v": "2020" }, { "n": "2019", "v": "2019" }, { "n": "2018", "v": "2018" }, { "n": "2017", "v": "2017" }, { "n": "2016", "v": "2016" }, { "n": "2015", "v": "2015" }, { "n": "2014", "v": "2014" }, { "n": "2013", "v": "2013" }, { "n": "2012", "v": "2012" }, { "n": "2011", "v": "2011" }, { "n": "00年代", "v": "2000-2010" }, { "n": "更早", "v": "-1999" }] },
            { "key": "tag_label_name", "name": "为你推荐", "value": [{ "n": "为你推荐", "v": "" }, { "n": "3D动画", "v": "3D动画" }, { "n": "搞笑日常", "v": "搞笑日常" }, { "n": "大男主", "v": "大男主" }, { "n": "高燃", "v": "高燃" }, { "n": "萌系", "v": "萌系" }, { "n": "修真", "v": "修真" }, { "n": "怀旧", "v": "怀旧" }, { "n": "超级英雄", "v": "超级英雄" }, { "n": "水树奈奈", "v": "水树奈奈" }, { "n": "张杰", "v": "张杰" }, { "n": "石田彰", "v": "石田彰" }, { "n": "守护地球", "v": "守护地球" }, { "n": "圆谷", "v": "圆谷" }, { "n": "山新", "v": "山新" }, { "n": "复仇", "v": "复仇" }, { "n": "废柴逆袭", "v": "废柴逆袭" }, { "n": "侦探", "v": "侦探" }, { "n": "无厘头", "v": "无厘头" }, { "n": "青山刚昌", "v": "青山刚昌" }, { "n": "悬疑", "v": "悬疑" }] }
        ]
    };

    return JSON.stringify({ class: classes, filters: filters });
}

async function homeVod() { return JSON.stringify({ list: [] }); }

// 分类展现（支持多条件复合扩展筛选，结合条件打包生成唯一的 Session 路由 Key）
async function category(tid, pg, filter, extend) {
    const page = parseInt(pg);
    
    // 1. 深度组装优酷 PC 网页端的多条件复合 params 结构
    const filterParams = { type: tid };
    
    // 如果外壳在滑动选择切换中传入了有效的过滤扩展，全量混入
    if (extend) {
        for (let key in extend) {
            if (extend[key] !== undefined && extend[key] !== null) {
                filterParams[key] = extend[key];
            }
        }
    }
    const paramsStr = encodeURIComponent(JSON.stringify(filterParams));
    
    // 生成基于“当前分类+筛选参数”的唯一会话令牌 Key，彻底防跨类/跨筛选产生分页互相污染覆盖
    const uniqueSessionKey = `${tid}_${JSON.stringify(extend || {})}`;

    let url = '';
    if (page === 1) {
        // 第一页：刷新/激活滚动锚点
        url = `https://www.youku.com/category/data?optionRefresh=1&pageNo=1&params=${paramsStr}`;
    } else {
        // 第二页及后续页：携带上一页更新存储下来的那个特定筛选线路 session
        const currentSession = globalSessionCache[uniqueSessionKey] || '{}';
        url = `https://www.youku.com/category/data?session=${encodeURIComponent(currentSession)}&pageNo=${page}&params=${paramsStr}`;
    }

    try {
        const res = await request(url);
        let list = [];

        if (res && res.data && res.data.filterData) {
            const filterData = res.data.filterData;
            
            // 2. 捕获优酷服务端下发的最新页 session 标志，并刷新绑定到该筛选线路的 Key 下
            if (filterData.session) {
                globalSessionCache[uniqueSessionKey] = typeof filterData.session === 'object' ? JSON.stringify(filterData.session) : filterData.session;
            }
            
            // 3. 解析该条件组合下渲染的 listData 剧集列表
            if (filterData.listData && filterData.listData.length > 0) {
                filterData.listData.forEach(it => {
                    let vid = "";
                    if (it.videoLink && it.videoLink.includes("id_")) {
                        vid = it.videoLink.split("id_")[1].split(".html")[0];
                    }
                    
                    if (vid) {
                        list.push({
                            vod_id: vid,
                            vod_name: it.title,
                            vod_pic: it.img.startsWith('//') ? 'https:' + it.img : it.img,
                            vod_remarks: it.summary || it.subTitle || ""
                        });
                    }
                });
            }
        }
        
        return JSON.stringify({ page: page, list: list });
    } catch (e) {
        return JSON.stringify({ page: page, list: [] });
    }
}

// 详情页面：PC端详情补全剧集树和元数据
async function detail(id) {
    const url = `https://search.youku.com/api/search?appScene=show_episode&showIds=${id}`;
    const res = await request(url);
    const video_lists = res.serisesList || [];

    let vod = {
        vod_id: id,
        vod_name: video_lists.length > 0 ? video_lists[0].title.replace(/(\d+)/g, "") : "影片详情",
        vod_pic: video_lists.length > 0 ? video_lists[0].thumbUrl : "",
        vod_play_from: '优酷',
        vod_play_url: '',
        vod_actor: '',
        vod_director: '',
        vod_year: '',
        vod_type: '',
        vod_content: ''
    };

    try {
        let detailUrl = `https://v.youku.com/v_getvideo_info/?showId=${id}`;
        let detailRes = await request(detailUrl);
        if (detailRes && detailRes.data) {
            let d = detailRes.data;
            vod.vod_actor = d._personNameStr || '';      
            vod.vod_director = d.directorName || '';      
            vod.vod_year = d.lastUpdate || '';             
            vod.vod_type = d.showVideotype || '';          
            vod.vod_content = d.showdesc || '';             
            if (d.showLogo) vod.vod_pic = d.showLogo;
            if (d.showTitle) vod.vod_name = d.showTitle;
        }
    } catch (e) {}

    vod.vod_play_url = video_lists.map(it => {
        const ep = it.showVideoStage ? it.showVideoStage.replace("期", "集") : it.displayName || it.title;
        return `${ep}$https://v.youku.com/v_show/id_${it.videoId}.html`;
    }).join('#');

    return JSON.stringify({ list: [vod] });
}

// 播放逻辑
async function play(flag, id, flags) {
    const privateApi = 'shturl.cc/WgqJ6zyYutcUmai';
    try {
        const res = await req(privateApi + encodeURIComponent(id), { headers: { 'User-Agent': PC_UA } });
        const json = JSON.parse(res.content);
        if (json.url || (json.data && json.data.url)) {
            return JSON.stringify({ parse: 0, url: json.url || json.data.url });
        }
    } catch (e) {}
    return JSON.stringify({ parse: 1, jx: 1, url: id });
}

// 搜索逻辑
async function search(wd, quick) {
    const url = `https://search.youku.com/api/search?pg=1&keyword=${encodeURIComponent(wd)}`;
    const res = await request(url);
    const list = (res.pageComponentList || []).filter(it => it.commonData).map(it => {
        const d = it.commonData;
        return {
            vod_id: d.showId,
            vod_name: d.titleDTO ? d.titleDTO.displayName : "未知",
            vod_pic: d.posterDTO ? d.posterDTO.vThumbUrl : "",
            vod_remarks: d.stripeBottom || ""
        };
    });
    return JSON.stringify({ list: list });
}

export function __jsEvalReturn() {
    return { init, home, homeVod, category, detail, play, search };
}
