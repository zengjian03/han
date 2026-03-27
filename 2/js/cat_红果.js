// 多源聚合短剧源 - 同时从多个API获取数据
let headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 13; M2102J2SC Build/TKQ1.221114.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/141.0.7390.17 Mobile Safari/537.36',
    'Referer': 'https://mov.cenguigui.cn/',
    'Origin': 'https://mov.cenguigui.cn'
};

// 多个短剧API源配置
const SOURCES = [
    {
        name: '主源',
        host: 'https://mov.cenguigui.cn/duanju/api.php?',
        enabled: true
    },
    {
        name: '备用1',
        host: 'https://api-store.qmplaylet.com/api/v1/playlet/index',  // 如果有其他源可以添加
        enabled: false
    }
];

// 分类映射 - 将标准分类名映射到各源的实际参数
const CATEGORY_MAP = {
    "逆袭": ["逆袭", "强者回归", "战神归来"],
    "霸总": ["霸总", "豪门恩怨"],
    "现代言情": ["现代言情", "现言甜宠", "闪婚"],
    "古装": ["古装", "古风言情", "古风权谋", "王妃", "皇后"],
    "穿越": ["穿越", "重生", "穿书"],
    "都市": ["都市日常", "都市修仙", "都市玄幻", "职场"],
    "神豪": ["神豪", "马甲", "无敌神医"],
    "虐恋": ["虐恋", "追妻", "破镜重圆"],
    "小人物": ["小人物", "乡村", "亲情"],
    "大女主": ["大女主", "女性成长", "女帝", "团宠"],
    "玄幻": ["玄幻仙侠", "异能", "奇幻脑洞", "系统"],
    "悬疑": ["悬疑推理", "刑侦破案", "玄学"],
    "喜剧": ["喜剧", "欢喜冤家", "萌宝"]
};

async function init(cfg) {}

// 从单个源获取数据
async function fetchFromSource(source, category, page = 1) {
    try {
        let url = source.host + "classname=" + encodeURIComponent(category) + "&page=" + page;
        let resp = await req(url, { headers: headers, timeout: 5000 });

        if (!resp || !resp.content) return [];

        let data;
        try {
            data = JSON.parse(resp.content);
        } catch (e) {
            return [];
        }

        if (!data || !data.data || !Array.isArray(data.data)) return [];

        return data.data.map(it => ({
            book_id: it.book_id ? it.book_id.toString() : null,
            title: it.title,
            cover: it.cover || '',
            episode_cnt: it.episode_cnt || 0,
            source_name: source.name,
            raw_data: it
        })).filter(it => it.book_id && it.title);
    } catch (e) {
        return [];
    }
}

// 聚合多个分类的数据
async function fetchAggregated(category, maxPerSource = 3) {
    let allVideos = [];
    let seenIds = new Set();

    // 获取该分类对应的别名列表
    const aliases = CATEGORY_MAP[category] || [category];

    // 从主源获取多个别名的数据
    const mainSource = SOURCES[0];
    if (mainSource.enabled) {
        for (let alias of aliases) {
            for (let page = 1; page <= maxPerSource; page++) {
                try {
                    const items = await fetchFromSource(mainSource, alias, page);

                    items.forEach(it => {
                        if (!seenIds.has(it.book_id)) {
                            seenIds.add(it.book_id);
                            allVideos.push({
                                vod_id: it.book_id,
                                vod_name: it.title,
                                vod_pic: it.cover,
                                vod_remarks: "共" + it.episode_cnt + "集 | " + alias,
                                source_alias: alias
                            });
                        }
                    });

                    // 如果这页数据少，说明可能没更多数据了
                    if (items.length < 5) break;

                } catch (e) {
                    break;
                }
            }
        }
    }

    return allVideos;
}

async function home(filter) {
    // 简化分类，只保留主要分类
    return JSON.stringify({
        class: [
            {"type_id":"逆袭","type_name":"🔥 逆袭"},
            {"type_id":"霸总","type_name":"💼 霸总"},
            {"type_id":"现代言情","type_name":"💕 现代言情"},
            {"type_id":"古装","type_name":"👘 古装"},
            {"type_id":"穿越","type_name":"🌀 穿越/重生"},
            {"type_id":"都市","type_name":"🏙️ 都市"},
            {"type_id":"神豪","type_name":"💰 神豪"},
            {"type_id":"虐恋","type_name":"💔 虐恋"},
            {"type_id":"小人物","type_name":"👤 小人物"},
            {"type_id":"大女主","type_name":"👑 大女主"},
            {"type_id":"玄幻","type_name":"✨ 玄幻"},
            {"type_id":"悬疑","type_name":"🔍 悬疑"},
            {"type_id":"喜剧","type_name":"😄 喜剧"}
        ]
    });
}

async function homeVod() {
    try {
        // 首页聚合多个热门分类的数据
        let allVideos = [];
        let seenIds = new Set();

        const hotCategories = ["逆袭", "霸总", "现代言情", "古装"];

        for (let cat of hotCategories) {
            const videos = await fetchAggregated(cat, 1); // 每类只取1页
            videos.forEach(v => {
                if (!seenIds.has(v.vod_id)) {
                    seenIds.add(v.vod_id);
                    allVideos.push(v);
                }
            });
        }

        // 打乱顺序，让首页更丰富
        allVideos.sort(() => Math.random() - 0.5);

        return JSON.stringify({
            list: allVideos.slice(0, 50),
            code: 1
        });
    } catch (e) {
        return JSON.stringify({
            list: [],
            code: 0,
            msg: e.message
        });
    }
}

async function category(tid, pg, filter, extend) {
    try {
        // 聚合该分类下所有数据
        const videos = await fetchAggregated(tid, 5); // 取5页

        return JSON.stringify({
            list: videos,
            page: 1,
            pagecount: 1,
            total: videos.length,
            code: 1
        });
    } catch (e) {
        return JSON.stringify({
            list: [],
            page: 1,
            pagecount: 1,
            total: 0,
            code: 0,
            msg: e.message
        });
    }
}

async function detail(id) {
    try {
        // 尝试从主源获取详情
        const mainSource = SOURCES[0];
        const url = mainSource.host + "book_id=" + id;

        let resp = await req(url, { headers: headers, timeout: 10000 });

        if (!resp || !resp.content) {
            return JSON.stringify({
                list: [],
                code: 0,
                msg: "获取详情失败"
            });
        }

        let json;
        try {
            json = JSON.parse(resp.content);
        } catch (e) {
            return JSON.stringify({
                list: [],
                code: 0,
                msg: "数据解析失败"
            });
        }

        if (!json || !json.data || !Array.isArray(json.data)) {
            return JSON.stringify({
                list: [],
                code: 0,
                msg: "无数据"
            });
        }

        // 剧集去重
        let seenEpisodes = new Set();
        let uniqueEpisodes = [];

        json.data.forEach(it => {
            const epKey = (it.episode_num || it.video_id || '').toString();
            if (epKey && !seenEpisodes.has(epKey)) {
                seenEpisodes.add(epKey);
                uniqueEpisodes.push(it);
            }
        });

        const playUrl = uniqueEpisodes.map(it => {
            const title = it.title || '第' + it.episode_num + '集';
            const videoUrl = "https://mov.cenguigui.cn/duanju/api.php?video_id=" + it.video_id + "&type=mp4";
            return title + "$" + videoUrl;
        }).join('#');

        return JSON.stringify({
            list: [{
                vod_id: id,
                vod_name: json.book_name || '',
                vod_pic: json.book_pic || '',
                vod_year: json.time || '',
                vod_remarks: "更新至" + (json.total || uniqueEpisodes.length) + "集" + "|" + "时长:" + (json.duration || '未知'),
                type_name: (json.category_names || []).join(','),
                vod_director: json.author || '',
                vod_content: json.desc || '',
                vod_play_from: '拾光聚合',
                vod_play_url: playUrl
            }],
            code: 1
        });
    } catch (e) {
        return JSON.stringify({
            list: [],
            code: 0,
            msg: e.message
        });
    }
}

async function search(wd, quick, pg) {
    const p = pg || 1;

    try {
        // 搜索时尝试多个相关分类
        let allVideos = [];
        let seenIds = new Set();

        // 直接从主源搜索
        const mainSource = SOURCES[0];
        for (let page = 1; page <= 3; page++) {
            try {
                let url = mainSource.host + "name=" + encodeURIComponent(wd) + "&page=" + page;
                let resp = await req(url, { headers: headers, timeout: 5000 });

                if (!resp || !resp.content) break;

                let data;
                try {
                    data = JSON.parse(resp.content);
                } catch (e) {
                    break;
                }

                if (!data || !data.data || !Array.isArray(data.data)) break;

                data.data.forEach(it => {
                    if (it.book_id && it.title) {
                        const id = it.book_id.toString();
                        if (!seenIds.has(id)) {
                            seenIds.add(id);
                            allVideos.push({
                                vod_id: id,
                                vod_name: it.title,
                                vod_pic: it.cover || '',
                                vod_remarks: "共" + (it.episode_cnt || '0') + "集"
                            });
                        }
                    }
                });

                if (data.data.length < 10) break;
            } catch (e) {
                break;
            }
        }

        return JSON.stringify({
            list: allVideos,
            page: 1,
            pagecount: 1,
            total: allVideos.length,
            code: 1
        });
    } catch (e) {
        return JSON.stringify({
            list: [],
            page: 1,
            pagecount: 1,
            total: 0,
            code: 0,
            msg: e.message
        });
    }
}

async function play(flag, id, flags) {
    return JSON.stringify({
        parse: 0,
        url: id,
        headers: headers,
        code: 1
    });
}

export default {
    init,
    home,
    homeVod,
    category,
    detail,
    search,
    play
};