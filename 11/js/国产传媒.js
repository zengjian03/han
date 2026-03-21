let host = 'https://fdff888.gcgqcm.buzz';
let headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; M2102J2SC Build/TKQ1.221114.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/143.0.7499.3 Mobile Safari/537.36"
};
async function init(cfg) {}
function getList(html) {
    let videos = [];
    let items = pdfa(html, ".vod");
    items.forEach(it => {
        let idMatch = it.match(/\/index.php\/vod\/detail\/id\/(\d+)\.html/);
        let nameMatch = it.match(/<div class="vod-txt">[\s\S]*?>(.*?)<\/a>/);
        let picMatch = it.match(/data-original="(.*?)"/) || it.match(/src="(.*?)"/);
        if (idMatch && nameMatch) {
            let pic = picMatch ? (picMatch[1] || picMatch[2]) : "";
            videos.push({
                vod_id: idMatch[1],
                vod_name: nameMatch[1].replace(/<.*?>/g, ""),
                vod_pic: pic.startsWith('/') ? host + pic : pic
            });
        }
    });
    return videos;
}
async function home(filter) {
    return JSON.stringify({
        "class": [{"type_id": "134","type_name": "女同性恋"},{"type_id": "133","type_name": "变性伪娘"},{"type_id": "132","type_name": "动漫卡通"},{"type_id": "131","type_name": "主奴调教"},{"type_id": "130","type_name": "人妻熟女"},{"type_id": "129","type_name": "欧美激情"},{"type_id": "128","type_name": "韩国三级"},{"type_id": "127","type_name": "强奸乱伦"},{"type_id": "125","type_name": "凌辱快感"},{"type_id": "124","type_name": "多人群交"},{"type_id": "123","type_name": "无码流出"},{"type_id": "122","type_name": "中文字幕"},{"type_id": "120","type_name": "制服诱惑"},{"type_id": "121","type_name": "丝袜美腿"},{"type_id": "119","type_name": "重口性癖"},{"type_id": "118","type_name": "V R 视角"},{"type_id": "135","type_name": "野外露出"},{"type_id": "116","type_name": "反差母狗"},{"type_id": "115","type_name": "足浴撩妹"},{"type_id": "113","type_name": "淫妻作乐"},{"type_id": "112","type_name": "A V 解说"},{"type_id": "111","type_name": "清纯学生"},{"type_id": "110","type_name": "传媒探花"},{"type_id": "109","type_name": "网曝事件"},{"type_id": "86","type_name": "国产大制作"},{"type_id": "87","type_name": "乱伦毁三观"},{"type_id": "88","type_name": "嫖妓全过程"},{"type_id": "89","type_name": "淫乱学生妹"},{"type_id": "90","type_name": "黑料不打烊"},{"type_id": "107","type_name": "自拍偷拍"},{"type_id": "92","type_name": "主播网红"},{"type_id": "93","type_name": "高清无码"},{"type_id": "95","type_name": "媚黑母狗"},{"type_id": "106","type_name": "国产乱伦"},{"type_id": "105","type_name": "国产主播"},{"type_id": "98","type_name": "中文剧情"},{"type_id": "99","type_name": "燃烧荷尔蒙"},{"type_id": "100","type_name": "3D动漫"},{"type_id": "101","type_name": "剧情故事"},{"type_id": "104","type_name": "精品推荐"}]});
}
async function homeVod() {
    let resp = await req(host, { headers });
    return JSON.stringify({ list: getList(resp.content) });
}
async function category(tid, pg, filter, extend) {
    let p = pg || 1;
    let targetId = (extend && extend.class) ? extend.class : tid;
    let url = host + "/index.php/vod/type/id/" + targetId + "/" + (parseInt(p) > 1 ? "page/" + p + ".html" : "");
    let resp = await req(url, { headers });
    return JSON.stringify({ list: getList(resp.content), page: parseInt(p) });
}
async function detail(id) {
    let url = host + '/index.php/vod/detail/id/' + id + '.html';
    let resp = await req(url, { headers });
    let html = resp.content;

    let playFrom = pdfa(html, ".stui-content h3")
        .map(it => (it.match(/>(.*?)</) || ["", "线路"])[1]).join('$$$');

    let playUrl = pdfa(html, ".stui-content__detail").map(list =>
        pdfa(list, "a").map(a => {
            let n = (a.match(/">(.*?)<\/a>/) || ["", "播放"])[1];
            let v = a.match(/href="(.*?)"/);
            let urlPart = v ? v[1].replace('#', '%23') : "";                        
            return n + '$' + urlPart;
        }).join('#')
    ).join('$$$');
    return JSON.stringify({
        list: [{
            vod_id: id,
            vod_name: (html.match(/<h3 class="title">(.*?)<\/h3>/) || ["", ""])[1],
            vod_pic: (html.match(/data-original="(.*?)"/) || ["", ""])[1],
            vod_content: (html.match(/<h3 class="title">(.*?)<\/h3>/) || ["", ""])[1].replace(/<.*?>/g, ""),
            vod_play_from: playFrom,
            vod_play_url: playUrl
        }]
    });
}
async function search(wd, quick, pg) {
    let p = pg || 1;
    let url = host + "/index.php/vod/search/" + (parseInt(p) > 1 ? "page/" + p + "/" : "") + "wd/" + encodeURIComponent(wd) + ".html";
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
