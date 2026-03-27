let host = 'https://www.esuppy.com';
let headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; M2102J2SC Build/TKQ1.221114.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/143.0.7499.3 Mobile Safari/537.36"
};
async function init(cfg) {}
function getList(html) {
    let videos = [];
    let items = pdfa(html, ".stui-vodlist__box");
    items.forEach(it => {
        let idMatch = it.match(/\/gqdt\/(\d+).html/);
        let nameMatch = it.match(/title="(.*?)"/) || it.match(/alt="(.*?)"/);
        let picMatch = it.match(/data-original="(.*?)"/) || it.match(/src="(.*?)"/);
        let remarksMatch = it.match(/<span class="pic-text text-right">(.*?)<\/span>/);
        if (idMatch && nameMatch) {
            let pic = picMatch ? (picMatch[1] || picMatch[2]) : "";
            videos.push({
                vod_id: idMatch[1],
                vod_name: nameMatch[1].replace(/<.*?>/g, ""),
                vod_pic: pic.startsWith('/') ? host + pic : pic,
                vod_remarks: (remarksMatch || ["", ""])[1].replace(/<.*?>/g, "")
            });
        }
    });
    return videos;
}
async function home(filter) {
    return JSON.stringify({
        "class": [{"type_id": "1","type_name": "电影"},{"type_id": "2","type_name": "电视剧"},{"type_id": "3","type_name": "综艺"},{"type_id": "4","type_name": "动漫"},{"type_id": "5","type_name": "短剧"},{"type_id": "6","type_name": "动作片"},{"type_id": "7","type_name": "喜剧片"},{"type_id": "8","type_name": "爱情片"},{"type_id": "9","type_name": "科幻片"},{"type_id": "10","type_name": "恐怖片"},{"type_id": "11","type_name": "剧情片"},{"type_id": "12","type_name": "战争片"},{"type_id": "13","type_name": "纪录片"},{"type_id": "14","type_name": "悬疑片"},{"type_id": "15","type_name": "犯罪片"},{"type_id": "16","type_name": "奇幻片"},{"type_id": "31","type_name": "动画片"},{"type_id": "32","type_name": "预告片"},{"type_id": "17","type_name": "国产剧"},{"type_id": "18","type_name": "港台剧"}]});
}
async function homeVod() {
    let resp = await req(host, { headers });
    return JSON.stringify({ list: getList(resp.content) });
}
async function category(tid, pg, filter, extend) {
    let p = pg || 1;
    let targetId = (extend && extend.class) ? extend.class : tid;
    let url = host + "/gqsw/" + targetId + "--------" + (parseInt(p) > 1 ? p + "---.html" : "1---.html");
    let resp = await req(url, { headers });
    return JSON.stringify({ list: getList(resp.content), page: parseInt(p) });
}
async function detail(id) {
    let url = host + '/gqdt/' + id + '.html';
    let resp = await req(url, { headers });
    let html = resp.content;

    let playFrom = pdfa(html, ".stui-vodlist__head h3")
        .map(it => (it.match(/>(.*?)</) || ["", "线路"])[1]).join('$$$');

    let playUrl = pdfa(html, ".stui-content__playlist").map(list =>
        pdfa(list, "a").map(a => {
            let n = (a.match(/">(.*?)<\/a>/) || ["", "播放"])[1];
            let v = a.match(/href="(.*?)"/);
            return n + '$' + (v ? v[1] : "");
        }).join('#')
    ).join('$$$');
    return JSON.stringify({
        list: [{
            vod_id: id,
            vod_name: (html.match(/<h1 class="title">(.*?)<\/h1>/) || ["", ""])[1],
            vod_pic: (html.match(/data-original="(.*?)"/) || ["", ""])[1],
            vod_year: (html.match(/<a href="\/gqsc\/-------------.*?.html" target="_blank">(.*?)<\/a>/) || ["", ""])[1],
            vod_area: (html.match(/<a href="\/gqsc\/--.*?-----------.html" target="_blank">(.*?)<\/a>/) || ["", ""])[1],
            vod_remarks: (html.match(/<p class="data">更新：(.*?)<\/p>/) || ["", ""])[1],
            type_name: (html.match(/<a href="\/gqsc\/----.*?---------.html" target="_blank">(.*?)<\/a>/) || ["", ""])[1],
            vod_actor: Array.from(
                html.match(/<p class="data">\s*主演：([\s\S]*?)<\/p>/)?.[1]?.matchAll(/<a [^>]*>([^<]+)<\/a>/g) || []).map(m => m[1]).join(' / ') || '',
            vod_director: Array.from(
                html.match(/<p class="data">\s*导演：([\s\S]*?)<\/p>/)?.[1]?.matchAll(/<a [^>]*>([^<]+)<\/a>/g) || []).map(m => m[1]).join(' / ') || '',
            vod_content: (html.match(/<span class="detail-content.*?>(.*?)<\/span>/) || ["", ""])[1].replace(/<.*?>/g, ""),
            vod_play_from: playFrom,
            vod_play_url: playUrl
        }]
    });
}
async function search(wd, quick, pg) {
    let p = pg || 1;
    let url = host + "/gqsc/" +encodeURIComponent(wd) + "----------" + (parseInt(p) > 1 ? parseInt(p) + "---.html" : "1---.html");
    let resp = await req(url, { headers });
    return JSON.stringify({ list: getList(resp.content) });
}
async function play(flag, id, flags) {
    let url = host + id;
    let resp = await req(url, { headers });
    let m3u8 = resp.content.match(/"url":"([^"]+\.m3u8)"/);
    if (m3u8) {
        return JSON.stringify({
            parse: 0,
            url: m3u8[1].replace(/\\/g, ""),
            header: headers
        });
    }
    let jump = resp.content.match(/(?:iframe|video)\s+[^>]*\bsrc\s*=\s*["']([^"']+\.m3u8(?:\?[^"']*)?)["']/i) ||
               resp.content.match(/location\.href\s*=\s*["']([^"']+\.m3u8(?:\?[^"']*)?)["']/i);
    if (jump) {
        let realUrl = jump[1].startsWith("http") ? jump[1] : host + jump[1];
        return JSON.stringify({
            parse: 0,
            url: realUrl,
            header: headers
        });
    }
    return JSON.stringify({
        parse: 1,
        url: url,
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
