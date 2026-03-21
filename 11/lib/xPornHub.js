let host = 'https://www.xpornhub4.top';
let headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; M2102J2SC Build/TKQ1.221114.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/144.0.7559.31 Mobile Safari/537.36"
};
async function init(cfg) {}

function getList(html) {
    let videos = [];


    let selector = '';
    if (html.includes('class="video_item"')) selector = '.video_item';
    else if (html.includes('class="data"')) selector = '.data';
    if (!selector) return videos;
    const items = pdfa(html, selector);
    items.forEach(it => {
        const idM = it.match(/href="([\s\S]*?)"/);
        const nameM = it.match(/title">([\s\S]*?)</);
        const picM = it.match(/data-src="([\s\S]*?)"|data-bg="([\s\S]*?)"/);
        const subM = it.match(/category[\s\S]*?>([^<]*)<\/a>/);
        if (idM && nameM) {
            videos.push({
                vod_id: idM[1],
                vod_name: nameM[1],
                vod_pic: picM ? (picM[1] || picM[2]) : '',
                vod_remarks: subM[1]
            });
        }
    });
    return videos;
}

async function home(filter) {
    return JSON.stringify({
        "class": [{
            "type_id": "国产自拍1",
            "type_name": "国产自拍1"
        }, {
            "type_id": "美女主播1",
            "type_name": "美女主播1"
        }, {
            "type_id": "日本无码1",
            "type_name": "日本无码1"
        }, {
            "type_id": "国产自拍",
            "type_name": "国产自拍"
        }, {
            "type_id": "美女主播",
            "type_name": "美女主播"
        }, {
            "type_id": "日本无码",
            "type_name": "日本无码"
        }, {
            "type_id": "自拍偷拍",
            "type_name": "自拍偷拍"
        }, {
            "type_id": "美女自慰",
            "type_name": "美女自慰"
        }, {
            "type_id": "高潮喷水",
            "type_name": "高潮喷水"
        }, {
            "type_id": "吃瓜爆料",
            "type_name": "吃瓜爆料"
        }, {
            "type_id": "重口调教",
            "type_name": "重口调教"
        }, {
            "type_id": "萝莉少女",
            "type_name": "萝莉少女"
        }, {
            "type_id": "ai换脸",
            "type_name": "ai换脸"
        }, {
            "type_id": "岛国素人",
            "type_name": "岛国素人"
        }, {
            "type_id": "乱伦中出",
            "type_name": "乱伦中出"
        }, {
            "type_id": "黑人洋屌",
            "type_name": "黑人洋屌"
        }, {
            "type_id": "日本有码",
            "type_name": "日本有码"
        }, {
            "type_id": "传媒原创",
            "type_name": "传媒原创"
        }, {
            "type_id": "av解说",
            "type_name": "av解说"
        }, {
            "type_id": "岛国女优",
            "type_name": "岛国女优"
        }, {
            "type_id": "韩国直播",
            "type_name": "韩国直播"
        }, {
            "type_id": "欧美精品",
            "type_name": "欧美精品"
        }, {
            "type_id": "角色扮演",
            "type_name": "角色扮演"
        }, {
            "type_id": "中文字幕",
            "type_name": "中文字幕"
        }, {
            "type_id": "人妻熟女",
            "type_name": "人妻熟女"
        }, {
            "type_id": "热门视频",
            "type_name": "热门视频"
        }, {
            "type_id": "户外打野",
            "type_name": "户外打野"
        }, {
            "type_id": "岛国群交",
            "type_name": "岛国群交"
        }, {
            "type_id": "口爆颜射",
            "type_name": "口爆颜射"
        }, {
            "type_id": "电车痴汉",
            "type_name": "电车痴汉"
        }]
    });
}
async function homeVod() {
    let resp = await req(host + "/video/", {
        headers
    });
    return JSON.stringify({
        list: getList(resp.content)
    });
}
async function category(tid, pg, filter, extend) {
    let p = pg || 1;
    let targetId = (extend && extend.class) ? extend.class : tid;
    let url = `${host}/video/category/${tid}?page=${p}`;
    let resp = await req(url, {
        headers
    });
    return JSON.stringify({
        list: getList(resp.content),
        page: parseInt(p)
    });
}
async function detail(id) {
    const url = host + id;
    const resp = await req(url, {
        headers
    });
    const html = resp.content;
    const v = html.match(/var\s+videoSrc\s*=\s*["'](https?:\/\/[^"']+)["']/)?.[1] || '';
    const playPairs = [{
        name: 'xPornHub',
        url: `立即播放$${v}`
    }];
    const playFrom = playPairs.map(p => p.name).join('$$$');
    const playUrl = playPairs.map(p => p.url).join('$$$');
    return JSON.stringify({
        list: [{
            vod_id: id,
            vod_play_from: playFrom,
            vod_play_url: playUrl
        }]
    });
}
async function search(wd, quick, pg) {
    let p = pg || 1;
    let url = `${host}/video/search/?keyword=${wd}&page=${p}`;
    let resp = await req(url, {
        headers
    });
    return JSON.stringify({
        list: getList(resp.content)
    });
}
async function play(flag, id, flags) {
    return JSON.stringify({
        parse: 1,
        url: id,
        header: headers
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