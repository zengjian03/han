// 从壳子内置目录加载cheerio 或者本地自备
import cheerio from 'assets://js/lib/cheerio.min.js';
// import cheerio from '../lib/cheerio.min.js';

import quarkApi, { getVideosFromShareLink, getPlayDatafromVideoInfo, checkIfExitVideosFromShareLink } from '../lib/quarkApi.js'
import { formatVideoName } from '../lib/utils.js'

const appConfig = {
    siteName: "枫叶4k影院",
    siteUrl: 'https://www.cd-zj.com'
}
const Headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": appConfig.siteUrl+"/",
}
async function init(ext) {
    const { quarkck } = ext
    const quarkCookie = await req(quarkck).content
    await quarkApi.setCookie(quarkCookie)
}
function getYearFilter() {
    let years = [{ "n": "全部", "v": "" }];
    const currentYear = new Date().getFullYear().toString();
    for (let y = currentYear; y >= currentYear - 22; y--) {
        years.push({ "n": String(y), "v": String(y) });
    }
    return { "key": "year", "name": "年份", "value": years };
}

function getLetterFilter() {
    return {
        "key": "letter", "name": "字母", "value": [
            { "n": "全部", "v": "" },
            { "n": "A", "v": "A" }, { "n": "B", "v": "B" }, { "n": "C", "v": "C" }, { "n": "D", "v": "D" },
            { "n": "E", "v": "E" }, { "n": "F", "v": "F" }, { "n": "G", "v": "G" }, { "n": "H", "v": "H" },
            { "n": "I", "v": "I" }, { "n": "J", "v": "J" }, { "n": "K", "v": "K" }, { "n": "L", "v": "L" },
            { "n": "M", "v": "M" }, { "n": "N", "v": "N" }, { "n": "O", "v": "O" }, { "n": "P", "v": "P" },
            { "n": "Q", "v": "Q" }, { "n": "R", "v": "R" }, { "n": "S", "v": "S" }, { "n": "T", "v": "T" },
            { "n": "U", "v": "U" }, { "n": "V", "v": "V" }, { "n": "W", "v": "W" }, { "n": "X", "v": "X" },
            { "n": "Y", "v": "Y" }, { "n": "Z", "v": "Z" }, { "n": "0-9", "v": "0-9" }
        ]
    }
}
const OtherFilters = [

    {
        "key": "area", "name": "地区", "value": [
            { "n": "全部", "v": "" }, { "n": "大陆", "v": "大陆" }, { "n": "香港", "v": "香港" },
            { "n": "台湾", "v": "台湾" }, { "n": "美国", "v": "美国" }, { "n": "韩国", "v": "韩国" },
            { "n": "日本", "v": "日本" }, { "n": "泰国", "v": "泰国" }, { "n": "新加坡", "v": "新加坡" },
            { "n": "马来西亚", "v": "马来西亚" }, { "n": "印度", "v": "印度" }, { "n": "英国", "v": "英国" },
            { "n": "法国", "v": "法国" }, { "n": "加拿大", "v": "加拿大" }, { "n": "西班牙", "v": "西班牙" },
            { "n": "俄罗斯", "v": "俄罗斯" }, { "n": "其它", "v": "其它" }
        ]
    },
    getYearFilter(),
    {
        "key": "lang", "name": "语言", "value": [
            { "n": "全部", "v": "" }, { "n": "国语", "v": "国语" }, { "n": "英语", "v": "英语" },
            { "n": "粤语", "v": "粤语" }, { "n": "闽南语", "v": "闽南语" }, { "n": "韩语", "v": "韩语" },
            { "n": "日语", "v": "日语" }, { "n": "其它", "v": "其它" }
        ]
    },
    getLetterFilter()
];

const myFilters = {
    // 
    "2": [
        {
            key: "type", "name": "类型", value: [
                { "n": "全部", "v": "2" },
                { "n": "国产剧", "v": "13" },
                { "n": "日韩剧", "v": "15" },
                { "n": "海外剧", "v": "16" },

            ]
        },
        {
            "key": "class", "name": "剧情", "value": [
                { "n": "全部", "v": "" }, { "n": "古装", "v": "古装" }, { "n": "战争", "v": "战争" },
                { "n": "青春偶像", "v": "青春偶像" }, { "n": "喜剧", "v": "喜剧" }, { "n": "家庭", "v": "家庭" },
                { "n": "犯罪", "v": "犯罪" }, { "n": "动作", "v": "动作" }, { "n": "奇幻", "v": "奇幻" },
                { "n": "剧情", "v": "剧情" }, { "n": "历史", "v": "历史" }, { "n": "经典", "v": "经典" },
                { "n": "乡村", "v": "乡村" }, { "n": "情景", "v": "情景" }, { "n": "商战", "v": "商战" },
                { "n": "网剧", "v": "网剧" }, { "n": "其他", "v": "其他" }
            ]
        },
        ...OtherFilters
    ],
    "1": [
        {
            "key": "type", "name": "类型", "value": [
                { "n": "全部", "v": "1" },
                { "n": "动作片", "v": "6" },
                { "n": "喜剧片", "v": "7" },
                { "n": "恐怖片", "v": "8" },
                { "n": "科幻片", "v": "9" },
                { "n": "爱情片", "v": "10" },
                { "n": "剧情片", "v": "11" }
            ]
        },
        {
            "key": "class", "name": "剧情", "value": [
                { "n": "全部", "v": "" },
                { "n": "喜剧", "v": "喜剧" },
                { "n": "爱情", "v": "爱情" },
                { "n": "恐怖", "v": "恐怖" },
                { "n": "动作", "v": "动作" },
                { "n": "科幻", "v": "科幻" },
                { "n": "剧情", "v": "剧情" },
                { "n": "战争", "v": "战争" },
                { "n": "警匪", "v": "警匪" },
                { "n": "犯罪", "v": "犯罪" },
                { "n": "动画", "v": "动画" },
                { "n": "奇幻", "v": "奇幻" },
                { "n": "武侠", "v": "武侠" },
                { "n": "冒险", "v": "冒险" },
                { "n": "枪战", "v": "枪战" },
                { "n": "悬疑", "v": "悬疑" },
                { "n": "惊悚", "v": "惊悚" },
                { "n": "经典", "v": "经典" },
                { "n": "青春", "v": "青春" },
                { "n": "文艺", "v": "文艺" },
                { "n": "微电影", "v": "微电影" },
                { "n": "古装", "v": "古装" },
                { "n": "历史", "v": "历史" },
                { "n": "运动", "v": "运动" },
                { "n": "农村", "v": "农村" },
                { "n": "儿童", "v": "儿童" },
                { "n": "网络电影", "v": "网络电影" }
            ]
        },
        ...OtherFilters
    ],
    "4": [
        {
            "key": "type", "name": "类型", "value": [
                { "n": "全部", "v": "4" },
                { "n": "国产动漫", "v": "25" },
                { "n": "日韩动漫", "v": "26" },

            ]
        },
        {
            "key": "class", "name": "剧情", "value": [
                { "n": "全部", "v": "" },
                { "n": "情感", "v": "情感" },
                { "n": "科幻", "v": "科幻" },
                { "n": "热血", "v": "热血" },
                { "n": "推理", "v": "推理" },
                { "n": "搞笑", "v": "搞笑" },
                { "n": "冒险", "v": "冒险" },
                { "n": "萝莉", "v": "萝莉" },
                { "n": "校园", "v": "校园" },
                { "n": "动作", "v": "动作" },
                { "n": "机战", "v": "机战" },
                { "n": "运动", "v": "运动" },
                { "n": "战争", "v": "战争" },
                { "n": "少年", "v": "少年" },
                { "n": "少女", "v": "少女" },
                { "n": "社会", "v": "社会" },
                { "n": "原创", "v": "原创" },
                { "n": "亲子", "v": "亲子" },
                { "n": "益智", "v": "益智" },
                { "n": "励志", "v": "励志" },
                { "n": "其他", "v": "其他" }
            ]
        },
        ...OtherFilters
    ],
    "3": [
        {
            "key": "type", "name": "类型", "value": [
                { "n": "全部", "v": "3" },
                { "n": "大陆综艺", "v": "21" },
                { "n": "日韩综艺", "v": "22" },

            ]
        },
        {
            "key": "class", "name": "剧情", "value": [
                { "n": "全部", "v": "" },
                { "n": "选秀", "v": "选秀" },
                { "n": "情感", "v": "情感" },
                { "n": "访谈", "v": "访谈" },
                { "n": "播报", "v": "播报" },
                { "n": "旅游", "v": "旅游" },
                { "n": "音乐", "v": "音乐" },
                { "n": "美食", "v": "美食" },
                { "n": "纪实", "v": "纪实" },
                { "n": "曲艺", "v": "曲艺" },
                { "n": "生活", "v": "生活" },
                { "n": "游戏互动", "v": "游戏互动" },
                { "n": "财经", "v": "财经" },
                { "n": "求职", "v": "求职" }
            ]
        },
        ...OtherFilters
    ],
    "5": [
        getYearFilter(),
        getLetterFilter()

    ],

};
async function home(filter) {
    return JSON.stringify({
        class: [
            { type_id: "2", type_name: "电视剧" },
            { type_id: "1", type_name: "电影" },
            { type_id: "4", type_name: "动漫" },
            { type_id: "3", type_name: "综艺" },
            { type_id: "5", type_name: "热门短剧" },
            { type_id: "/label/qq", type_name: "腾讯VIP精选" },
            { type_id: "/label/bli", type_name: "B站VIP精选" },
            { type_id: "/label/youku", type_name: "优酷VIP精选" }
        ],
        filters: myFilters
    });
}

async function category(tid, pg, filter, extend) {

    pg = pg || 1;
    let type = extend.type || tid;

    const isLanel = tid.startsWith("/label");

    let url = "";
    if (isLanel) {
        // 1. 获取VIP精选标签页
        url = appConfig.siteUrl + tid + `/page/${pg}.html`;
    } else {
        // 2. 提取各个筛选项
        let classVal = extend.class || ''; // 剧情 (古装)
        let areaVal = extend.area || ''; // 地区 (大陆)
        let langVal = extend.lang || ''; // 语言 (国语)
        let letterVal = extend.letter || ''; // 字母 (空)
        let orderVal = extend.orderBy || ''; // 排序 (空)
        let yearVal = extend.year || ''; // 年份 (2026)

        // 3. 严格对照图片的 11 个横杠精准拼接 (不编码)
        // 结构：分类-地区-空-剧情-语言-字母-排序-空-页码-空-空-年份
        url = `${appConfig.siteUrl}/cupfox-list/${type}-${areaVal}-${''}-${classVal}-${langVal}-${letterVal}-${orderVal}-${''}-${pg}-${''}-${''}-${yearVal}.html`;
    }



    const html = (await req(url)).content;

    const $ = cheerio.load(html);
    let list = [];

    $(".public-list-div.public-list-bj").each(function (index, el) {

        let vod_id = $(el).find("a.public-list-exp").attr("href");
        let vod_name = $(el).find("a.public-list-exp").attr("title").trim();
        let is4k = $(el).find(".public-prt-g").text().trim() == '4K'
        let vod_pic = $(el).find(".public-list-exp img").attr("data-src");
        let vod_remarks = $(el).find(".public-list-exp i.ft2").text().trim();
        list.push({
            vod_id,
            vod_name,
            vod_pic,
            vod_remarks: is4k ? '4K ' + vod_remarks : vod_remarks
        });
    });

    // 当前1/429页
    const pageStr = $('.page-tip').text().trim()
    console.log('pageStr:', pageStr)

    const pagecount = pageStr.match(/\d+\/(\d+)页/)?.[1] || 1

    return JSON.stringify({
        list,
        pagecount
    });

}

async function search(wd, quick, page) {
    if (page >= 2) {
        // 不需要再请求下一页了
        return JSON.stringify({ list: [], pagecount: 1 });
    }
    try {
        const url = `https://www.cd-zj.com/cupfox-search/-------------.html?wd=${wd}`;
        const html = (await req(url)).content;
        const $ = cheerio.load(html);
        let list = [];
        $('.search-box').each((i, el) => {
            const vod_id = $(el).find(".thumb-txt a").attr('href') || '';
            const vod_name = $(el).find(".thumb-txt a").text().trim()
            const vod_pic = $(el).find('.left img').attr('data-src') || '';
            const vod_remarks = $(el).find('.public-list-prb').text().trim()
            list.push({
                vod_id,
                vod_name,
                vod_pic,
                vod_remarks
            });
        })

        return JSON.stringify({
            list: list,
            pagecount: 1  // 假设只有一页
        });
    } catch (e) {
        console.error("❌ search 遭遇内部崩溃 =", e.message);
        return JSON.stringify({ list: [] });
    }
}

async function detail(ids) {
    let videoId = Array.isArray(ids) ? ids[0] : ids;
    const url = appConfig.siteUrl + videoId;
    const html = (await req(url)).content;
    const $ = cheerio.load(html);

    let vod_name = $('.slide-info-title').text().trim();
    let vod_pic = appConfig.siteUrl + $('.detail-pic img').attr("data-src");

    let vod_actor = $('.detail-info .slide-info').eq(2).text().trim().replace("演员：", "")
    let vod_remarks = $('.detail-info .slide-info').eq(4).text().trim().replace("连载 :", "")
    let vod_content = $('#height_limit').text().trim();

    const lines = [];
    $('.swiper-slide').each((i, el) => {

        const lineName = $(el).clone().find('i, span').remove().end().text().trim();


        lines.push(lineName);
    });
    const vod_play_from = lines.join("$$$");

    const playlistArray = [];

    $('.anthology-list-box').each((lineIndex, poolEl) => {
        const episodes = [];
        // 遍历当前线路下的所有集数 A 标签
        $(poolEl).find('a').each((episodeIndex, epEl) => {


            const name = $(epEl).text().trim();
            const href = $(epEl).attr('href') || '';

            if (!name || !href) {
                console.log("detail: 线路无集数", lineIndex, episodeIndex, name, href);
            }

            if (name && href) {
                episodes.push(`${name}\$${href}`);
            }
        });
        playlistArray.push(episodes.join('#'));
    });

    const vod_play_url = playlistArray.join('$$$');

    console.log("detail: vod_play_from", vod_play_from);
    console.log("detail: vod_play_url", vod_play_url);

    const vod = {
        vod_id: videoId,
        vod_actor,
        vod_remarks,
        vod_name,
        vod_pic,
        vod_content,
        vod_play_from,
        vod_play_url
    };

    return JSON.stringify({
        list: [vod]
    });
}

// 判断是否为直接播放链接
function isDirectUrl(url) {
    return url.startsWith('http') && url.endsWith(".m3u8")
}
async function parsePLayUrl(is2kLine, url) {
    // 2k线路和4k线路的解析接口不同
    const parseApiUrl = is2kLine ? "https://zzrs.mfdyvip.com/player/" : "https://fgsrg.hzqingshan.com/player/"
    try {
        const html = (await req(`${parseApiUrl}?url=${url}`, {
            method: 'GET',
            headers: Headers
        })).content

        const $ = cheerio.load(html)
        const token = $('#player-data').attr('data-te');
        console.log("🚀 成功拿到 token:", token);

        let playData = await req(`${parseApiUrl}/mplayer.php`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            data: {
                url: url,
                token: token,
            }
        }).content
        playData = JSON.parse(playData)
        return playData.url
    } catch (e) {
        console.error("❌ play  encounters an internal crash =", e);
        return "";
    }
}

async function play(flag, id, flags) {
    try {
        // https://www.cd-zj.com/play/78244-6-5.html
        const html = (await req(`https://www.cd-zj.com/${id}`)).content;

        const url = getPlayUrl(html)

        if (isDirectUrl(url)) {
            return JSON.stringify({
                parse: 0,
                url,
            });
        }
        const is2kLine = flag.includes('2k')
        if (is2kLine) {
            console.log("🚀 检测到2k线路:", flag, id);
        }
        const playUrl = await parsePLayUrl(is2kLine, url)
        return JSON.stringify({
            parse: 0,
            url: playUrl
        });
    } catch (e) {
        console.error("❌ play 遭遇内部崩溃 =", e);
        return JSON.stringify({ parse: 0, url: "" });
    }

}
// 假设 html 是你请求播放页返回的完整网页源码文本
function getPlayUrl(html) {
    // 意思是：先找到 var player_aaaa，然后一直接着往下找，直到匹配到 "url": "..." 里的内容
    const match = html.match(/var\s+player_aaaa[\s\S]*?"url"\s*:\s*"([^"]+)"/);

    let url = match ? match[1] : '';
    url = url.replace(/\\/g, '');
    console.log("🚀 获取播放链接成功:", url);
    return url;
}
export default { init, home, category, detail, search, play };
