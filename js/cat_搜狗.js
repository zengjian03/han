import { _ } from 'assets://js/lib/cat.js';

const host = 'https://waptv.sogou.com';
const PC_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36';
const MOBILE_UA = 'Mozilla/5.0 (Linux; Android 10; Total_Build) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36';

async function init(cfg) {}

// 通用网络请求辅助
async function request(url, useMobile = false) {
    const res = await req(url, {
        method: 'get',
        headers: {
            'User-Agent': useMobile ? MOBILE_UA : PC_UA,
            'Referer': host
        }
    });
    return res.content;
}

// 首页分类与高级筛选项
async function home() {
    const classes = [
        { type_id: 'teleplay', type_name: '电视剧' },
        { type_id: 'film', type_name: '电影' },
        { type_id: 'cartoon', type_name: '动漫' },
        { type_id: 'tvshow', type_name: '综艺' },
        { type_id: 'documentary', type_name: '纪录片' }
    ];

    const filters = {
        'teleplay': [
            { 'key': 'style', 'name': '类型', 'value': [{ 'n': '全部', 'v': '' }, { 'n': '爱情', 'v': '爱情' }, { 'n': '喜剧', 'v': '喜剧' }, { 'n': '都市', 'v': '都市' }, { 'n': '悬疑', 'v': '悬疑' }, { 'n': '古装', 'v': '古装' }, { 'n': '偶像', 'v': '偶像' }, { 'n': '犯罪', 'v': '犯罪' }, { 'n': '历史', 'v': '历史' }, { 'n': '战争', 'v': '战争' }, { 'n': '武侠', 'v': '武侠' }, { 'n': '警匪', 'v': '警匪' }, { 'n': '科幻', 'v': '科幻' }, { 'n': '奇幻', 'v': '奇幻' }, { 'n': '谍战', 'v': '谍战' }, { 'n': '农村', 'v': '农村' }, { 'n': '其他', 'v': '其他' }] },
            { 'key': 'zone', 'name': '地区', 'value': [{ 'n': '全部', 'v': '' }, { 'n': '内地', 'v': '内地' }, { 'n': '香港', 'v': '香港' }, { 'n': '台湾', 'v': '台湾' }, { 'n': '韩国', 'v': '韩国' }, { 'n': '泰国', 'v': '泰国' }, { 'n': '日本', 'v': '日本' }, { 'n': '美国', 'v': '美国' }, { 'n': '英国', 'v': '英国' }, { 'n': '新加坡', 'v': '新加坡' }, { 'n': '其他', 'v': '其他' }] },
            { 'key': 'year', 'name': '年代', 'value': [{ 'n': '全部', 'v': '' }, { 'n': '2026', 'v': '2026' }, { 'n': '2025', 'v': '2025' }, { 'n': '2024', 'v': '2024' }, { 'n': '2023', 'v': '2023' }, { 'n': '2022', 'v': '2022' }, { 'n': '2021', 'v': '2021' }, { 'n': '2020', 'v': '2020' }, { 'n': '2019', 'v': '2019' }, { 'n': '2018', 'v': '2018' }, { 'n': '2017', 'v': '2017' }, { 'n': '2016', 'v': '2016' }, { 'n': '2015', 'v': '2015' }, { 'n': '2014', 'v': '2014' }, { 'n': '更早', 'v': '更早' }] },
            { 'key': 'fee', 'name': '资源', 'value': [{ 'n': '全部', 'v': '' }, { 'n': '正片', 'v': '正片' }, { 'n': '免费正片', 'v': '免费正片' }, { 'n': '付费正片', 'v': '付费正片' }] },
            { 'key': 'order', 'name': '排序', 'value': [{ 'n': '全部', 'v': '' }, { 'n': '最新', 'v': '最新' }, { 'n': '好评', 'v': '好评' }] }
        ],
        'film': [
            { 'key': 'style', 'name': '类型', 'value': [{ 'n': '全部', 'v': '' }, { 'n': '喜剧', 'v': '喜剧' }, { 'n': '爱情', 'v': '爱情' }, { 'n': '动作', 'v': '动作' }, { 'n': '恐怖', 'v': '恐怖' }, { 'n': '科幻', 'v': '科幻' }, { 'n': '惊悚', 'v': '惊悚' }, { 'n': '犯罪', 'v': '犯罪' }, { 'n': '奇幻', 'v': '奇幻' }, { 'n': '战争', 'v': '战争' }, { 'n': '悬疑', 'v': '悬疑' }, { 'n': '动画', 'v': '动画' }, { 'n': '文艺', 'v': '文艺' }, { 'n': '传记', 'v': '传记' }, { 'n': '歌舞', 'v': '歌舞' }, { 'n': '古装', 'v': '古装' }, { 'n': '警匪', 'v': '警匪' }, { 'n': '其他', 'v': '其他' }] },
            { 'key': 'zone', 'name': '地区', 'value': [{ 'n': '全部', 'v': '' }, { 'n': '内地', 'v': '内地' }, { 'n': '香港', 'v': '香港' }, { 'n': '台湾', 'v': '台湾' }, { 'n': '韩国', 'v': '韩国' }, { 'n': '泰国', 'v': '泰国' }, { 'n': '日本', 'v': '日本' }, { 'n': '美国', 'v': '美国' }, { 'n': '英国', 'v': '英国' }, { 'n': '新加坡', 'v': '新加坡' }, { 'n': '其他', 'v': '其他' }] },
            { 'key': 'year', 'name': '年代', 'value': [{ 'n': '全部', 'v': '' }, { 'n': '2026', 'v': '2026' }, { 'n': '2025', 'v': '2025' }, { 'n': '2024', 'v': '2024' }, { 'n': '2023', 'v': '2023' }, { 'n': '2022', 'v': '2022' }, { 'n': '2021', 'v': '2021' }, { 'n': '2020', 'v': '2020' }, { 'n': '2019', 'v': '2019' }, { 'n': '2018', 'v': '2018' }, { 'n': '2017', 'v': '2017' }, { 'n': '2016', 'v': '2016' }, { 'n': '2015', 'v': '2015' }, { 'n': '2014', 'v': '2014' }, { 'n': '更早', 'v': '更早' }] },
            { 'key': 'fee', 'name': '资源', 'value': [{ 'n': '全部', 'v': '' }, { 'n': '正片', 'v': '正片' }, { 'n': '免费正片', 'v': '免费正片' }, { 'n': '付费正片', 'v': '付费正片' }] },
            { 'key': 'order', 'name': '排序', 'value': [{ 'n': '全部', 'v': '' }, { 'n': '最新', 'v': '最新' }, { 'n': '好评', 'v': '好评' }] }
        ],
        'cartoon': [
            { 'key': 'style', 'name': '类型', 'value': [{ 'n': '全部', 'v': '' }, { 'n': '搞笑', 'v': '搞笑' }, { 'n': '热血', 'v': '热血' }, { 'n': '冒险', 'v': '冒险' }, { 'n': '美少女', 'v': '美少女' }, { 'n': '科幻', 'v': '科幻' }, { 'n': '校园', 'v': '校园' }, { 'n': '恋爱', 'v': '恋爱' }, { 'n': '神魔', 'v': '神魔' }, { 'n': '机战', 'v': '机战' }, { 'n': '益智', 'v': '益智' }, { 'n': '亲子', 'v': '亲子' }, { 'n': '励志', 'v': '励志' }, { 'n': '童话', 'v': '童话' }, { 'n': '青春', 'v': '青春' }, { 'n': '原创', 'v': '原创' }, { 'n': '动作', 'v': '动作' }, { 'n': '耽美', 'v': '耽美' }, { 'n': '魔幻', 'v': '魔幻' }, { 'n': '其他', 'v': '其他' }] },
            { 'key': 'zone', 'name': '地区', 'value': [{ 'n': '全部', 'v': '' }, { 'n': '日本', 'v': '日本' }, { 'n': '欧美', 'v': '欧美' }, { 'n': '国产', 'v': '国产' }, { 'n': '其他', 'v': '其他' }] },
            { 'key': 'year', 'name': '年代', 'value': [{ 'n': '全部', 'v': '' }, { 'n': '2026', 'v': '2026' }, { 'n': '2025', 'v': '2025' }, { 'n': '2024', 'v': '2024' }, { 'n': '2023', 'v': '2023' }, { 'n': '2022', 'v': '2022' }, { 'n': '2021', 'v': '2021' }, { 'n': '2020', 'v': '2020' }, { 'n': '2019', 'v': '2019' }, { 'n': '2018', 'v': '2018' }, { 'n': '2017', 'v': '2017' }, { 'n': '2016', 'v': '2016' }, { 'n': '2015', 'v': '2015' }, { 'n': '2014', 'v': '2014' }, { 'n': '更早', 'v': '更早' }] },
            { 'key': 'fee', 'name': '资源', 'value': [{ 'n': '全部', 'v': '' }, { 'n': '正片', 'v': '正片' }, { 'n': '免费正片', 'v': '免费正片' }, { 'n': '付费正片', 'v': '付费正片' }] },
            { 'key': 'order', 'name': '排序', 'value': [{ 'n': '全部', 'v': '' }, { 'n': '最新', 'v': '最新' }, { 'n': '好评', 'v': '好评' }] }
        ],
        'tvshow': [
            { 'key': 'style', 'name': '类型', 'value': [{ 'n': '全部', 'v': '' }, { 'n': '真人秀', 'v': '真人秀' }, { 'n': '生活', 'v': '生活' }, { 'n': '搞笑', 'v': '搞笑' }, { 'n': '访谈', 'v': '访谈' }, { 'n': '时尚', 'v': '时尚' }, { 'n': '音乐', 'v': '音乐' }, { 'n': '选秀', 'v': '选秀' }, { 'n': '美食', 'v': '美食' }, { 'n': '游戏', 'v': '游戏' }, { 'n': '纪实', 'v': '纪实' }, { 'n': '旅游', 'v': '旅游' }, { 'n': '情感', 'v': '情感' }, { 'n': '恶搞', 'v': '恶搞' }, { 'n': '吐槽', 'v': '吐槽' }, { 'n': '原创', 'v': '原创' }, { 'n': '歌舞', 'v': '歌舞' }, { 'n': '播报', 'v': '播报' }, { 'n': '曲艺', 'v': '曲艺' }, { 'n': '科教', 'v': '科教' }, { 'n': '其他', 'v': '其他' }] },
            { 'key': 'zone', 'name': '地区', 'value': [{ 'n': '全部', 'v': '' }, { 'n': '内地', 'v': '内地' }, { 'n': '台湾', 'v': '台湾' }, { 'n': '日韩', 'v': '日韩' }, { 'n': '欧美', 'v': '欧美' }, { 'n': '其他', 'v': '其他' }] },
            { 'key': 'emcee', 'name': '明星', 'value': [{ 'n': '全部', 'v': '' }, { 'n': '何炅', 'v': '何炅' }, { 'n': '撒贝宁', 'v': '撒贝宁' }, { 'n': '王筱磊', 'v': '王筱磊' }, { 'n': '张绍刚', 'v': '张绍刚' }, { 'n': '鲁健', 'v': '鲁健' }, { 'n': '王世林', 'v': '王世林' }, { 'n': '倪萍', 'v': '倪萍' }, { 'n': '汪涵', 'v': '汪涵' }, { 'n': '舒冬', 'v': '舒冬' }, { 'n': '齐思钧', 'v': '齐思钧' }, { 'n': '白岩松', 'v': '白岩松' }, { 'n': '曲洪禹', 'v': '曲洪禹' }, { 'n': '康辉', 'v': '康辉' }, { 'n': '章亭', 'v': '章亭' }, { 'n': '刘洪悦', 'v': '刘洪悦' }, { 'n': '尼格买提', 'v': '尼格买提' }, { 'n': '钱枫', 'v': '钱枫' }, { 'n': '刘婧', 'v': '刘婧' }, { 'n': '赵川', 'v': '赵川' }, { 'n': '谢娜', 'v': '谢娜' }] },
            { 'key': 'order', 'name': '排序', 'value': [{ 'n': '全部', 'v': '' }, { 'n': '最新', 'v': '最新' }, { 'n': '好评', 'v': '好评' }] }
        ],
        'documentary': [
            { 'key': 'style', 'name': '类型', 'value': [{ 'n': '全部', 'v': '' }, { 'n': '历史', 'v': '历史' }, { 'n': '自然', 'v': '自然' }, { 'n': '动物', 'v': '动物' }, { 'n': '社会', 'v': '社会' }, { 'n': '传记', 'v': '传记' }, { 'n': '人文', 'v': '人文' }, { 'n': '文化', 'v': '文化' }, { 'n': '军事', 'v': '军事' }, { 'n': '科技', 'v': '科技' }, { 'n': '人物', 'v': '人物' }, { 'n': '探索', 'v': '探索' }, { 'n': '美食', 'v': '美食' }, { 'n': '旅行', 'v': '旅行' }, { 'n': '探险', 'v': '探险' }, { 'n': '其他', 'v': '其他' }] },
            { 'key': 'zone', 'name': '地区', 'value': [{ 'n': '全部', 'v': '' }, { 'n': '内地', 'v': '内地' }, { 'n': '香港', 'v': '香港' }, { 'n': '台湾', 'v': '台湾' }, { 'n': '韩国', 'v': '韩国' }, { 'n': '泰国', 'v': '泰国' }, { 'n': '日本', 'v': '日本' }, { 'n': '美国', 'v': '美国' }, { 'n': '英国', 'v': '英国' }, { 'n': '新加坡', 'v': '新加坡' }, { 'n': '其他', 'v': '其他' }] },
            { 'key': 'year', 'name': '年代', 'value': [{ 'n': '全部', 'v': '' }, { 'n': '2026', 'v': '2026' }, { 'n': '2025', 'v': '2025' }, { 'n': '2024', 'v': '2024' }, { 'n': '2023', 'v': '2023' }, { 'n': '2022', 'v': '2022' }, { 'n': '2021', 'v': '2021' }, { 'n': '2020', 'v': '2020' }, { 'n': '2019', 'v': '2019' }, { 'n': '2018', 'v': '2018' }, { 'n': '2017', 'v': '2017' }, { 'n': '2016', 'v': '2016' }, { 'n': '2015', 'v': '2015' }, { 'n': '2014', 'v': '2014' }, { 'n': '更早', 'v': '更早' }] },
            { 'key': 'fee', 'name': '资源', 'value': [{ 'n': '全部', 'v': '' }, { 'n': '正片', 'v': '正片' }, { 'n': '免费正片', 'v': '免费正片' }, { 'n': '付费正片', 'v': '付费正片' }] },
            { 'key': 'order', 'name': '排序', 'value': [{ 'n': '全部', 'v': '' }, { 'n': '最新', 'v': '最新' }, { 'n': '好评', 'v': '好评' }] }
        ]
    };

    return JSON.stringify({ class: classes, filters: filters });
}

async function homeVod() { return JSON.stringify({ list: [] }); }

// 一级分类页 (对齐 drpy 扁平化传参逻辑，解决二级编码导致筛选挂掉的问题)
async function category(tid, pg, filter, extend) {
    const page = parseInt(pg);
    const start = (page - 1) * 15;
    
    let style = extend.style || '';
    let zone = extend.zone || '';
    let year = extend.year || '';
    let fee = extend.fee || '';
    let order = extend.order || '';
    let emcee = extend.emcee || '';

    let url = `${host}/napi/video/classlist?abtest=0&iploc=CN1304&spver=&listTab=${tid}&style=${encodeURIComponent(style)}&zone=${encodeURIComponent(zone)}&year=${encodeURIComponent(year)}&fee=${encodeURIComponent(fee)}&order=${encodeURIComponent(order)}&emcee=${encodeURIComponent(emcee)}&start=${start}&len=15`;

    try {
        const content = await request(url);
        const html = JSON.parse(content);
        const list = html.listData.results || [];
        let vodList = [];

        list.forEach(it => {
            let desc1 = it.ipad_play_for_list.finish_episode ? (it.ipad_play_for_list.episode === it.ipad_play_for_list.finish_episode ? "全集" + it.ipad_play_for_list.finish_episode : "连载" + it.ipad_play_for_list.episode + "/" + it.ipad_play_for_list.finish_episode) : "";
            let desc2 = it.score ? "评分:" + it.score : "";
            let desc3 = it.date ? "更至:" + it.date : "";
            
            let targetUrl = "https://v.sogou.com" + it.url.replace("teleplay", "series").replace("cartoon", "series");

            vodList.push({
                vod_id: targetUrl,
                vod_name: it.name,
                vod_pic: it.v_picurl,
                vod_remarks: desc1 || desc2 || desc3
            });
        });

        return JSON.stringify({ page: page, list: vodList });
    } catch (e) {
        return JSON.stringify({ page: page, list: [] });
    }
}

// 二级影片详情
async function detail(id) {
    try {
        const html = await request(id);
        const match = html.match(/INITIAL_STATE.*?({.*});/);
        if (!match) return JSON.stringify({ list: [] });

        const json = JSON.parse(match[1]).detail.itemData;
        const key = json.dockey;
        const name = json.name;
        const zone = json.zone;
        const score = json.score ? json.score : "暂无";
        const style = json.style;
        const emcee = json.emcee ? "主持：" + json.emcee : json.name;
        let director = json.director ? "导演：" + json.director : name;
        director = director.replace(/;/g, "\t");
        let starring = json.starring ? "演员：" + json.starring : "声优：" + json.shengyou;
        starring = starring.replace(/.*undefined/, "").replace(/;/g, "\t");
        const update = json.update_wordstr ? json.update_wordstr : "";
        const tv_station = json.tv_station ? json.tv_station : zone;
        const introduction = json.introduction;
        
        const plays = json.play.item_list || [];
        const shows = json.play_from_open_index;

        let vod = {
            vod_id: id,
            vod_name: name,
            vod_director: director,
            vod_actor: starring,
            vod_remarks: style + " 评分:" + score + "," + update,
            vod_content: introduction,
            vod_area: emcee + "," + tv_station
        };

        // 获取封面图
        let pic = "";
        let picMatch = html.match(/id="thumb_img"[^>]*src="(.*?)"/);
        if (picMatch) {
            pic = picMatch[1];
        } else if (json.photo && json.photo.item_list && json.photo.item_list.length > 0) {
            pic = json.photo.item_list[0];
        }
        vod.vod_pic = pic;

        let tabs = [];
        let vod_lists = [];

        plays.forEach((it, idex) => {
            const item = it.info;
            let tbn = it.sitename[0] || it.site.replace(".com", "");
            tbn = tbn.split("").join(" ");
            tabs.push(tbn);

            let tmp = [];
            if (item || shows) {
                if (item && Array.isArray(item) && item.length > 1) {
                    item.slice(1).forEach(its => {
                        let finalUrl = its.url.startsWith("http") ? its.url : "https://v.sogou.com" + its.url;
                        tmp.push(its.index + "$" + finalUrl);
                    });
                }
                if (shows && shows.item_list && shows.item_list[idex]) {
                    let arr = [];
                    let zy = shows.item_list[idex];
                    if (zy.date) {
                        zy.date.forEach(date => {
                            let day = date.day;
                            for (let j = 0; j < day.length; j++) {
                                let dayy = day[j][0] >= 10 ? day[j][0] : "0" + day[j][0];
                                let Tdate = date.year + date.month + dayy;
                                arr.push(Tdate);
                            }
                        });
                    }
                    for (let k = 0; k < arr.length; k++) {
                        let url = `https://v.sogou.com/vc/eplay?query=${arr[k]}&date=${arr[k]}&key=${key}&st=5&tvsite=${it.site}`;
                        tmp.push("第" + arr[k] + "期" + "$" + url);
                    }
                }
            } else if (it.site) {
                let finalUrl = it.url.startsWith("http") ? it.url : "https://v.sogou.com" + it.url;
                if (!it.flag_list.includes("trailer")) {
                    tmp.push(it.sitename[0] + "$" + finalUrl);
                } else {
                    tmp.push(it.sitename[0] + "—预告" + "$" + finalUrl);
                }
            }
            vod_lists.push(tmp.join("#"));
        });

        vod.vod_play_from = tabs.join("$$$");
        vod.vod_play_url = vod_lists.join("$$$");

        return JSON.stringify({ list: [vod] });
    } catch (e) {
        return JSON.stringify({ list: [] });
    }
}

// 播放嗅探逻辑
async function play(flag, id, flags) {
    try {
        const html = await request(id, true);
        const rurlMatch = html.match(/window\.open\('(.*?)',/);
        let rurl = rurlMatch ? rurlMatch[1] : id;
        
        if (rurl.startsWith('//')) {
            rurl = 'https:' + rurl;
        }
        return JSON.stringify({ parse: 1, jx: 1, url: rurl });
    } catch (e) {
        return JSON.stringify({ parse: 1, jx: 1, url: id });
    }
}

// 搜索逻辑
async function search(wd, quick) {
    const url = `${host}/film/result?ie=utf8&query=${encodeURIComponent(wd)}`;
    try {
        const html = await request(url);
        const match = html.match(/INITIAL_STATE.*?({.*});/);
        if (!match) return JSON.stringify({ list: [] });

        let jsonA = JSON.parse(match[1]);
        const results = jsonA.result.resultData.searchData.results || [];
        let d = [];

        results.forEach(it => {
            let name = it.name || "";
            let introduction = it.introduction;
            let pic = it.v_picurl;
            let targetUrl = it.tiny_url || "";
            
            if (it.play_info && it.play_info.play_list) {
                d.push({
                    vod_id: "https://v.sogou.com" + targetUrl.replace(/teleplay|cartoon/g, 'series'),
                    vod_name: name.replace(//g, "").replace(//g, ""), 
                    vod_pic: pic,
                    vod_remarks: it.listCategory ? it.listCategory.join(",") : "",
                    vod_content: introduction
                });
            }
        });

        return JSON.stringify({ list: d });
    } catch (e) {
        return JSON.stringify({ list: [] });
    }
}

export function __jsEvalReturn() {
    return { init, home, homeVod, category, detail, play, search };
}
