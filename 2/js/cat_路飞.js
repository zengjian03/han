import 'assets://js/lib/crypto-js.js';
let host = 'https://www.lufys.com';
let headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 13; M2102J2SC Build/TKQ1.221114.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/144.0.7559.31 Mobile Safari/537.36',
};

function md5(string) {
    return CryptoJS.MD5(string).toString();
}

function getList(html) {
    let videos = [];
    let selector = '';
    if (html.includes('<div class="public-list-box')) selector = '.public-list-box';
    else if (html.includes('<div class="vod-detail')) selector = '.search-list';
    if (!selector) return videos;
    const list = pdfa(html, selector);
    list.forEach(it => {
        const id = pdfh(it, 'a&&href');
        const name = pdfh(it, 'a&&title') || pdfh(it, 'h3&&Text');
        const pic = pdfh(it, 'img&&data-src');
        const remark = pdfh(it, '.public-list-prb&&Text') || pdfh(it, '.slide-info-remarks&&Text');
        videos.push({
            vod_id: id,
            vod_name: name,
            vod_pic: pic,
            vod_remarks: remark
        });
    });
    return videos;
}
async function init(cfg) {}
async function home(filter) {
    return JSON.stringify({
        class: [{
                "type_id": "1",
                "type_name": "电影"
            },
            {
                "type_id": "2",
                "type_name": "剧集"
            },
            {
                "type_id": "3",
                "type_name": "综艺"
            },
            {
                "type_id": "4",
                "type_name": "动漫"
            },
            {
                "type_id": "39",
                "type_name": "短剧"
            }
        ],
        filters: {}
    });
}
async function homeVod() {
    let resp = await req(host, {
        headers
    });
    return JSON.stringify({
        list: getList(resp.content)
    });
}

async function category(tid, pg, filter, extend) {
    let timestamp = new Date().getTime().toString();
    let key = md5("DS" + timestamp + "DCC147D11943AF75");
    const cateId = extend.cateId || tid;
    const class_ = extend.class_ || '';
    const area = extend.area || '';
    const lang = extend.lang || '';
    const letter = extend.letter || '';
    const year = extend.year || '';
    const by = extend.by || '';
    let url = `${host}/index.php/api/vod?type=${cateId}&page=${pg}&time=${timestamp}&key=${key}&area=${area}&class=${class_}&by=${by}&lang=${lang}&letter=${letter}&year=${year}`;
    let payload = {
        headers: headers,
        method: 'POST'
    };
    let resp = await req(url, payload);
    let fdata = JSON.parse(resp.content);
    let videos = fdata.list.map(item => {
        return {
            vod_id: '/watch/' + item.vod_id + '.html',
            vod_name: item.vod_name,
            vod_pic: item.vod_pic,
            vod_remarks: item.vod_remarks
        };
    });
    return JSON.stringify({
        list: videos,
        page: parseInt(pg),
        pagecount: parseInt(pg) + 1
    });
}
async function detail(id) {
    const url = host + id;
    const resp = await req(url, {
        headers
    });
    const html = resp.content;
    let VOD = {};
    VOD.vod_id = id;
    VOD.vod_name = pdfh(html, '.gen-search-form&&li:contains(片名)&&Text').replace('片名：', '');
    VOD.type_name = pdfh(html, '.gen-search-form&&li:contains(类型)&&Text').replace('类型：', '');
    VOD.vod_pic = pdfh(html, '.detail-pic&&img&&data-src');
    VOD.vod_remarks = pdfh(html, '.gen-search-form&&li:contains(状态)&&Text').replace('状态：', '');
    VOD.vod_year = pdfh(html, '.gen-search-form&&li:contains(年份)&&Text').replace('年份：', '');
    VOD.vod_area = pdfh(html, '.gen-search-form&&li:contains(地区)&&Text').replace('地区：', '');
    VOD.vod_director = pdfh(html, '.gen-search-form&&li:contains(导演)&&Text').replace('导演：', '');
    VOD.vod_actor = pdfh(html, '.gen-search-form&&li:contains(主演)&&Text').replace('主演：', '');
    VOD.vod_content = pdfh(html, '.gen-search-form&&li:contains(简介)&&Text').replace('简介：', '');

    let r_ktabs = pdfa(html, '.anthology-tab&&a');
    let ktabs = r_ktabs.map(it => pdfh(it, 'Text').replace(/\s*\d+$/, '').trim());
    VOD.vod_play_from = ktabs.join('$$$');
    let klists = [];
    let r_plists = pdfa(html, '.anthology-list-play');
    r_plists.forEach((rp) => {
        let klist = pdfa(rp, 'a').map((it) => {
            return pdfh(it, 'a&&Text') + '$' + pd(it, 'a&&href', url);
        }).filter(item => {
            return !item.includes('APP播放');
        });
        klist = klist.join('#');
        klists.push(klist);
    });
    VOD.vod_play_url = klists.join('$$$');
    return JSON.stringify({
        list: [VOD]
    });
}
async function search(wd, quick, pg) {
    let p = pg || 1;
    const url = `${host}/search/page/${p}/wd/${wd}`;
    const resp = await req(url, {
        headers
    });
    return JSON.stringify({
        list: getList(resp.content),
        page: parseInt(p),
        pagecount: parseInt(p) + 1
    });
}
async function play(flag, id, flags) {
    try {
        let playUrl = !/^http/.test(id) ? `${host}${id}` : id;
        let resHtml = (await req(playUrl, {
            headers
        })).content;
        let kcode = null;
        let match = resHtml.match(/var\s+player_\w+\s*=\s*(\{[^]*?\})\s*</);
        if (match) {
            kcode = safeParseJSON(match[1]);
        }
        if (!kcode || !kcode.url) {
            let aaaaMatch = resHtml.split('aaaa=');
            if (aaaaMatch.length > 1) {
                kcode = safeParseJSON(aaaaMatch[1].split('<')[0]);
            }
        }
        let kurl = kcode?.url ?? '';
        let kp = /m3u8|mp4|mkv/i.test(kurl) ? 0 : 1;
        if (kp) {
            return JSON.stringify({
                jx: 0,
                parse: 1,
                url: playUrl,
                header: headers
            });
        } else {
            return JSON.stringify({
                jx: 0,
                parse: 0,
                url: kurl,
                header: {
                    'User-Agent': headers['User-Agent'],
                    'Referer': host
                }
            });
        }
    } catch (e) {
        return JSON.stringify({
            jx: 0,
            parse: 0,
            url: '',
            header: {}
        });
    }
}

function safeParseJSON(str) {
    try {
        return JSON.parse(str.trim().replace(/;+$/, ''));
    } catch {
        return null;
    }
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