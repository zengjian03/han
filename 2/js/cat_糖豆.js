/**
    title: "糖豆影视",
    author: "Gemini",
    logo: "https://tdys.cc/mxtheme/images/logo.png",
    more: {
        sourceTag: "在线影视"
    }
*/
import { Crypto, load, _ } from 'assets://js/lib/cat.js';

let HOST = 'https://tdys.cc';
let siteKey = "", siteType = "", sourceKey = "", ext = "";

const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36';

function init(cfg) {
    siteKey = cfg.skey;
    siteType = cfg.stype;
    sourceKey = cfg.sourceKey;
    ext = cfg.ext;
    if (ext && ext.indexOf('http') == 0) HOST = ext;
}

async function home(filter) {
    const classes = [
        { type_id: "dianying", type_name: "电影" },
        { type_id: "juji", type_name: "剧集" },
        { type_id: "zongyi", type_name: "综艺" },
        { type_id: "dongman", type_name: "动漫" }
    ];

    const filterObj = {
        "dianying": [
            { 
                "key": "class", 
                "name": "剧情", 
                "value": [
                    { "n": "全部", "v": "" },
                    { "n": "动作", "v": "动作" },
                    { "n": "喜剧", "v": "喜剧" },
                    { "n": "爱情", "v": "爱情" },
                    { "n": "科幻", "v": "科幻" },
                    { "n": "剧情", "v": "剧情" },
                    { "n": "悬疑", "v": "悬疑" },
                    { "n": "惊悚", "v": "惊悚" },
                    { "n": "恐怖", "v": "恐怖" },
                    { "n": "犯罪", "v": "犯罪" },
                    { "n": "谍战", "v": "谍战" },
                    { "n": "冒险", "v": "冒险" },
                    { "n": "奇幻", "v": "奇幻" },
                    { "n": "灾难", "v": "灾难" },
                    { "n": "战争", "v": "战争" },
                    { "n": "动画", "v": "动画" },
                    { "n": "歌舞", "v": "歌舞" },
                    { "n": "历史", "v": "历史" },
                    { "n": "纪录", "v": "纪录" },
                    { "n": "其他", "v": "其他" }
                ]
            },
            { 
                "key": "area", 
                "name": "地区", 
                "value": [
                    { "n": "全部", "v": "" },
                    { "n": "大陆", "v": "大陆" },
                    { "n": "香港", "v": "香港" },
                    { "n": "台湾", "v": "台湾" },
                    { "n": "美国", "v": "美国" },
                    { "n": "法国", "v": "法国" },
                    { "n": "英国", "v": "英国" },
                    { "n": "日本", "v": "日本" },
                    { "n": "韩国", "v": "韩国" },
                    { "n": "德国", "v": "德国" },
                    { "n": "泰国", "v": "泰国" },
                    { "n": "印度", "v": "印度" },
                    { "n": "意大利", "v": "意大利" },
                    { "n": "西班牙", "v": "西班牙" },
                    { "n": "加拿大", "v": "加拿大" },
                    { "n": "其他", "v": "其他" }
                ]
            },
            { 
                "key": "lang", 
                "name": "语言", 
                "value": [
                    { "n": "全部", "v": "" },
                    { "n": "国语", "v": "国语" },
                    { "n": "英语", "v": "英语" },
                    { "n": "粤语", "v": "粤语" },
                    { "n": "闽南语", "v": "闽南语" },
                    { "n": "韩语", "v": "韩语" },
                    { "n": "日语", "v": "日语" },
                    { "n": "法语", "v": "法语" },
                    { "n": "德语", "v": "德语" },
                    { "n": "其它", "v": "其它" }
                ]
            },
            { 
                "key": "year", 
                "name": "年份", 
                "value": [
                    { "n": "全部", "v": "" },
                    { "n": "2024", "v": "2024" },
                    { "n": "2023", "v": "2023" },
                    { "n": "2022", "v": "2022" },
                    { "n": "2021", "v": "2021" },
                    { "n": "2020", "v": "2020" },
                    { "n": "2019", "v": "2019" },
                    { "n": "2018", "v": "2018" },
                    { "n": "2017", "v": "2017" },
                    { "n": "2016", "v": "2016" },
                    { "n": "2015", "v": "2015" },
                    { "n": "2014", "v": "2014" },
                    { "n": "2013", "v": "2013" },
                    { "n": "2012", "v": "2012" },
                    { "n": "2011", "v": "2011" },
                    { "n": "2010", "v": "2010" }
                ]
            },
            { 
                "key": "letter", 
                "name": "字母", 
                "value": [
                    { "n": "字母", "v": "" },
                    { "n": "A", "v": "A" },
                    { "n": "B", "v": "B" },
                    { "n": "C", "v": "C" },
                    { "n": "D", "v": "D" },
                    { "n": "E", "v": "E" },
                    { "n": "F", "v": "F" },
                    { "n": "G", "v": "G" },
                    { "n": "H", "v": "H" },
                    { "n": "I", "v": "I" },
                    { "n": "J", "v": "J" },
                    { "n": "K", "v": "K" },
                    { "n": "L", "v": "L" },
                    { "n": "M", "v": "M" },
                    { "n": "N", "v": "N" },
                    { "n": "O", "v": "O" },
                    { "n": "P", "v": "P" },
                    { "n": "Q", "v": "Q" },
                    { "n": "R", "v": "R" },
                    { "n": "S", "v": "S" },
                    { "n": "T", "v": "T" },
                    { "n": "U", "v": "U" },
                    { "n": "V", "v": "V" },
                    { "n": "W", "v": "W" },
                    { "n": "X", "v": "X" },
                    { "n": "Y", "v": "Y" },
                    { "n": "Z", "v": "Z" },
                    { "n": "0-9", "v": "0-9" }
                ]
            },
            { 
                "key": "by", 
                "name": "排序", 
                "value": [
                    { "n": "时间排序", "v": "time" },
                    { "n": "人气排序", "v": "hits" },
                    { "n": "评分排序", "v": "score" }
                ]
            }
        ],
        "juji": [
            { 
                "key": "class", 
                "name": "剧情", 
                "value": [
                    { "n": "全部", "v": "" },
                    { "n": "古装", "v": "古装" },
                    { "n": "战争", "v": "战争" },
                    { "n": "青春偶像", "v": "青春偶像" },
                    { "n": "喜剧", "v": "喜剧" },
                    { "n": "家庭", "v": "家庭" },
                    { "n": "犯罪", "v": "犯罪" },
                    { "n": "动作", "v": "动作" },
                    { "n": "奇幻", "v": "奇幻" },
                    { "n": "剧情", "v": "剧情" },
                    { "n": "历史", "v": "历史" },
                    { "n": "经典", "v": "经典" },
                    { "n": "乡村", "v": "乡村" },
                    { "n": "情景", "v": "情景" },
                    { "n": "悬疑", "v": "悬疑" },
                    { "n": "网剧", "v": "网剧" },
                    { "n": "其他", "v": "其他" }
                ]
            },
            { 
                "key": "area", 
                "name": "地区", 
                "value": [
                    { "n": "全部", "v": "" },
                    { "n": "大陆", "v": "大陆" },
                    { "n": "香港", "v": "香港" },
                    { "n": "台湾", "v": "台湾" },
                    { "n": "美国", "v": "美国" },
                    { "n": "法国", "v": "法国" },
                    { "n": "英国", "v": "英国" },
                    { "n": "日本", "v": "日本" },
                    { "n": "韩国", "v": "韩国" },
                    { "n": "德国", "v": "德国" },
                    { "n": "泰国", "v": "泰国" },
                    { "n": "印度", "v": "印度" },
                    { "n": "意大利", "v": "意大利" },
                    { "n": "西班牙", "v": "西班牙" },
                    { "n": "加拿大", "v": "加拿大" },
                    { "n": "其他", "v": "其他" }
                ]
            },
            { 
                "key": "lang", 
                "name": "语言", 
                "value": [
                    { "n": "全部", "v": "" },
                    { "n": "国语", "v": "国语" },
                    { "n": "英语", "v": "英语" },
                    { "n": "粤语", "v": "粤语" },
                    { "n": "闽南语", "v": "闽南语" },
                    { "n": "韩语", "v": "韩语" },
                    { "n": "日语", "v": "日语" },
                    { "n": "法语", "v": "法语" },
                    { "n": "德语", "v": "德语" },
                    { "n": "其它", "v": "其它" }
                ]
            },
            { 
                "key": "year", 
                "name": "年份", 
                "value": [
                    { "n": "全部", "v": "" },
                    { "n": "2024", "v": "2024" },
                    { "n": "2023", "v": "2023" },
                    { "n": "2022", "v": "2022" },
                    { "n": "2021", "v": "2021" },
                    { "n": "2020", "v": "2020" },
                    { "n": "2019", "v": "2019" },
                    { "n": "2018", "v": "2018" },
                    { "n": "2017", "v": "2017" },
                    { "n": "2016", "v": "2016" },
                    { "n": "2015", "v": "2015" },
                    { "n": "2014", "v": "2014" },
                    { "n": "2013", "v": "2013" },
                    { "n": "2012", "v": "2012" },
                    { "n": "2011", "v": "2011" },
                    { "n": "2010", "v": "2010" }
                ]
            },
            { 
                "key": "letter", 
                "name": "字母", 
                "value": [
                    { "n": "字母", "v": "" },
                    { "n": "A", "v": "A" },
                    { "n": "B", "v": "B" },
                    { "n": "C", "v": "C" },
                    { "n": "D", "v": "D" },
                    { "n": "E", "v": "E" },
                    { "n": "F", "v": "F" },
                    { "n": "G", "v": "G" },
                    { "n": "H", "v": "H" },
                    { "n": "I", "v": "I" },
                    { "n": "J", "v": "J" },
                    { "n": "K", "v": "K" },
                    { "n": "L", "v": "L" },
                    { "n": "M", "v": "M" },
                    { "n": "N", "v": "N" },
                    { "n": "O", "v": "O" },
                    { "n": "P", "v": "P" },
                    { "n": "Q", "v": "Q" },
                    { "n": "R", "v": "R" },
                    { "n": "S", "v": "S" },
                    { "n": "T", "v": "T" },
                    { "n": "U", "v": "U" },
                    { "n": "V", "v": "V" },
                    { "n": "W", "v": "W" },
                    { "n": "X", "v": "X" },
                    { "n": "Y", "v": "Y" },
                    { "n": "Z", "v": "Z" },
                    { "n": "0-9", "v": "0-9" }
                ]
            },
            { 
                "key": "by", 
                "name": "排序", 
                "value": [
                    { "n": "时间排序", "v": "time" },
                    { "n": "人气排序", "v": "hits" },
                    { "n": "评分排序", "v": "score" }
                ]
            }
        ],
        "zongyi": [
            { 
                "key": "class", 
                "name": "剧情", 
                "value": [
                    { "n": "全部", "v": "" },
                    { "n": "脱口秀", "v": "脱口秀" },
                    { "n": "真人秀", "v": "真人秀" },
                    { "n": "选秀", "v": "选秀" },
                    { "n": "八卦", "v": "八卦" },
                    { "n": "访谈", "v": "访谈" },
                    { "n": "情感", "v": "情感" },
                    { "n": "生活", "v": "生活" },
                    { "n": "晚会", "v": "晚会" },
                    { "n": "搞笑", "v": "搞笑" },
                    { "n": "音乐", "v": "音乐" },
                    { "n": "时尚", "v": "时尚" },
                    { "n": "游戏", "v": "游戏" },
                    { "n": "少儿", "v": "少儿" },
                    { "n": "体育", "v": "体育" },
                    { "n": "纪实", "v": "纪实" },
                    { "n": "科教", "v": "科教" },
                    { "n": "曲艺", "v": "曲艺" },
                    { "n": "歌舞", "v": "歌舞" },
                    { "n": "财经", "v": "财经" },
                    { "n": "汽车", "v": "汽车" },
                    { "n": "播报", "v": "播报" },
                    { "n": "其他", "v": "其他" }
                ]
            },
            { 
                "key": "area", 
                "name": "地区", 
                "value": [
                    { "n": "全部", "v": "" },
                    { "n": "大陆", "v": "大陆" },
                    { "n": "香港", "v": "香港" },
                    { "n": "台湾", "v": "台湾" },
                    { "n": "美国", "v": "美国" },
                    { "n": "法国", "v": "法国" },
                    { "n": "英国", "v": "英国" },
                    { "n": "日本", "v": "日本" },
                    { "n": "韩国", "v": "韩国" },
                    { "n": "德国", "v": "德国" },
                    { "n": "泰国", "v": "泰国" },
                    { "n": "印度", "v": "印度" },
                    { "n": "意大利", "v": "意大利" },
                    { "n": "西班牙", "v": "西班牙" },
                    { "n": "加拿大", "v": "加拿大" },
                    { "n": "其他", "v": "其他" }
                ]
            },
            { 
                "key": "lang", 
                "name": "语言", 
                "value": [
                    { "n": "全部", "v": "" },
                    { "n": "国语", "v": "国语" },
                    { "n": "英语", "v": "英语" },
                    { "n": "粤语", "v": "粤语" },
                    { "n": "闽南语", "v": "闽南语" },
                    { "n": "韩语", "v": "韩语" },
                    { "n": "日语", "v": "日语" },
                    { "n": "法语", "v": "法语" },
                    { "n": "德语", "v": "德语" },
                    { "n": "其它", "v": "其它" }
                ]
            },
            { 
                "key": "year", 
                "name": "年份", 
                "value": [
                    { "n": "全部", "v": "" },
                    { "n": "2024", "v": "2024" },
                    { "n": "2023", "v": "2023" },
                    { "n": "2022", "v": "2022" },
                    { "n": "2021", "v": "2021" },
                    { "n": "2020", "v": "2020" },
                    { "n": "2019", "v": "2019" },
                    { "n": "2018", "v": "2018" },
                    { "n": "2017", "v": "2017" },
                    { "n": "2016", "v": "2016" },
                    { "n": "2015", "v": "2015" },
                    { "n": "2014", "v": "2014" },
                    { "n": "2013", "v": "2013" },
                    { "n": "2012", "v": "2012" },
                    { "n": "2011", "v": "2011" },
                    { "n": "2010", "v": "2010" }
                ]
            },
            { 
                "key": "letter", 
                "name": "字母", 
                "value": [
                    { "n": "字母", "v": "" },
                    { "n": "A", "v": "A" },
                    { "n": "B", "v": "B" },
                    { "n": "C", "v": "C" },
                    { "n": "D", "v": "D" },
                    { "n": "E", "v": "E" },
                    { "n": "F", "v": "F" },
                    { "n": "G", "v": "G" },
                    { "n": "H", "v": "H" },
                    { "n": "I", "v": "I" },
                    { "n": "J", "v": "J" },
                    { "n": "K", "v": "K" },
                    { "n": "L", "v": "L" },
                    { "n": "M", "v": "M" },
                    { "n": "N", "v": "N" },
                    { "n": "O", "v": "O" },
                    { "n": "P", "v": "P" },
                    { "n": "Q", "v": "Q" },
                    { "n": "R", "v": "R" },
                    { "n": "S", "v": "S" },
                    { "n": "T", "v": "T" },
                    { "n": "U", "v": "U" },
                    { "n": "V", "v": "V" },
                    { "n": "W", "v": "W" },
                    { "n": "X", "v": "X" },
                    { "n": "Y", "v": "Y" },
                    { "n": "Z", "v": "Z" },
                    { "n": "0-9", "v": "0-9" }
                ]
            },
            { 
                "key": "by", 
                "name": "排序", 
                "value": [
                    { "n": "时间排序", "v": "time" },
                    { "n": "人气排序", "v": "hits" },
                    { "n": "评分排序", "v": "score" }
                ]
            }
        ],
        "dongman": [
            { 
                "key": "class", 
                "name": "剧情", 
                "value": [
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
                    { "n": "少年", "v": "少年" }
                ]
            },
            { 
                "key": "area", 
                "name": "地区", 
                "value": [
                    { "n": "全部", "v": "" },
                    { "n": "大陆", "v": "大陆" },
                    { "n": "香港", "v": "香港" },
                    { "n": "台湾", "v": "台湾" },
                    { "n": "美国", "v": "美国" },
                    { "n": "法国", "v": "法国" },
                    { "n": "英国", "v": "英国" },
                    { "n": "日本", "v": "日本" },
                    { "n": "韩国", "v": "韩国" },
                    { "n": "德国", "v": "德国" },
                    { "n": "泰国", "v": "泰国" },
                    { "n": "印度", "v": "印度" },
                    { "n": "意大利", "v": "意大利" },
                    { "n": "西班牙", "v": "西班牙" },
                    { "n": "加拿大", "v": "加拿大" },
                    { "n": "其他", "v": "其他" }
                ]
            },
            { 
                "key": "lang", 
                "name": "语言", 
                "value": [
                    { "n": "全部", "v": "" },
                    { "n": "国语", "v": "国语" },
                    { "n": "英语", "v": "英语" },
                    { "n": "粤语", "v": "粤语" },
                    { "n": "闽南语", "v": "闽南语" },
                    { "n": "韩语", "v": "韩语" },
                    { "n": "日语", "v": "日语" },
                    { "n": "法语", "v": "法语" },
                    { "n": "德语", "v": "德语" },
                    { "n": "其它", "v": "其它" }
                ]
            },
            { 
                "key": "year", 
                "name": "年份", 
                "value": [
                    { "n": "全部", "v": "" },
                    { "n": "2024", "v": "2024" },
                    { "n": "2023", "v": "2023" },
                    { "n": "2022", "v": "2022" },
                    { "n": "2021", "v": "2021" },
                    { "n": "2020", "v": "2020" },
                    { "n": "2019", "v": "2019" },
                    { "n": "2018", "v": "2018" },
                    { "n": "2017", "v": "2017" },
                    { "n": "2016", "v": "2016" },
                    { "n": "2015", "v": "2015" },
                    { "n": "2014", "v": "2014" },
                    { "n": "2013", "v": "2013" },
                    { "n": "2012", "v": "2012" },
                    { "n": "2011", "v": "2011" },
                    { "n": "2010", "v": "2010" }
                ]
            },
            { 
                "key": "letter", 
                "name": "字母", 
                "value": [
                    { "n": "字母", "v": "" },
                    { "n": "A", "v": "A" },
                    { "n": "B", "v": "B" },
                    { "n": "C", "v": "C" },
                    { "n": "D", "v": "D" },
                    { "n": "E", "v": "E" },
                    { "n": "F", "v": "F" },
                    { "n": "G", "v": "G" },
                    { "n": "H", "v": "H" },
                    { "n": "I", "v": "I" },
                    { "n": "J", "v": "J" },
                    { "n": "K", "v": "K" },
                    { "n": "L", "v": "L" },
                    { "n": "M", "v": "M" },
                    { "n": "N", "v": "N" },
                    { "n": "O", "v": "O" },
                    { "n": "P", "v": "P" },
                    { "n": "Q", "v": "Q" },
                    { "n": "R", "v": "R" },
                    { "n": "S", "v": "S" },
                    { "n": "T", "v": "T" },
                    { "n": "U", "v": "U" },
                    { "n": "V", "v": "V" },
                    { "n": "W", "v": "W" },
                    { "n": "X", "v": "X" },
                    { "n": "Y", "v": "Y" },
                    { "n": "Z", "v": "Z" },
                    { "n": "0-9", "v": "0-9" }
                ]
            },
            { 
                "key": "by", 
                "name": "排序", 
                "value": [
                    { "n": "时间排序", "v": "time" },
                    { "n": "人气排序", "v": "hits" },
                    { "n": "评分排序", "v": "score" }
                ]
            }
        ]
    };

    return JSON.stringify({ class: classes, filters: filterObj });
}

async function homeVod() {
    try {
        const res = await req(`${HOST}/`, { headers: { 'User-Agent': UA } });
        const $ = load(res.content);
        const items = $('.module-poster-item.module-item');
        const videos = _.map(items, (item) => {
            const $item = $(item);
            return {
                vod_id: $item.attr('href'),
                vod_name: $item.attr('title'),
                vod_pic: $item.find('img.lazyload').attr('data-original'),
                vod_remarks: $item.find('.module-item-note').text().trim()
            };
        });
        return JSON.stringify({ list: videos });
    } catch (e) { return null; }
}

async function category(tid, pg, filter, extend) {
    if (pg <= 0) pg = 1;
    
    // 严格对应：id-area-by-class-lang-letter---pg---year.html
    // 如果对应项为空，确保连字符占位正确
    let area = extend['area'] || '';
    let by = extend['by'] || 'time';
    let cls = extend['class'] || '';
    let year = extend['year'] || '';
    let lang = ''; 
    let letter = '';

    // 重新构建符合标准的路径 (注意中间的连字符数量)
    // 很多这类网站如果不选具体项，中间会留空如：/show/dianying-美国-time-动作片---1---2024.html
    const link = `${HOST}/show/${tid}-${area}-${by}-${cls}-${lang}-${letter}---${pg}---${year}.html`;
    
    try {
        const res = await req(link, { headers: { 'User-Agent': UA } });
        if (!res.content || res.content.length < 500) return JSON.stringify({ list: [] }); // 可能是反爬或404

        const $ = load(res.content);
        // 如果这个类名拿不到数据，尝试通用的 .module-item
        const items = $('.module-item'); 
        
        const videos = _.map(items, (item) => {
            const $item = $(item);
            // 确保优先获取 a 标签，因为有的结构 a 标签包裹在外面
            const $a = $item.hasClass('module-item') && $item.is('a') ? $item : $item.find('a').first();
            
            return {
                vod_id: $a.attr('href'),
                vod_name: $a.attr('title') || $item.find('.module-item-title').text(),
                vod_pic: $item.find('img.lazyload').attr('data-original'),
                vod_remarks: $item.find('.module-item-note').text().trim()
            };
        }).filter(v => v.vod_id); // 过滤掉没有ID的干扰项

        return JSON.stringify({ list: videos, page: pg });
    } catch (e) { 
        return JSON.stringify({ list: [] }); 
    }
}

async function search(wd) {
    // 构建搜索URL，使用实际观察到的格式
    const searchUrl = `${HOST}/so/${encodeURIComponent(wd)}----------2---.html`;
    
    try {
        const res = await req(searchUrl, { headers: { 'User-Agent': UA } });
        const $ = load(res.content);
        
        // 根据实际HTML结构选择搜索结果项
        const items = $('.module-card-item.module-item');
        const videos = _.map(items, (item) => {
            const $item = $(item);
            
            // 获取详情页链接
            const detailLink = $item.find('.module-card-item-poster').attr('href') || 
                              $item.find('a[href^="/vod-detail/"]').attr('href');
            
            // 获取图片
            const $img = $item.find('.module-item-pic img.lazyload');
            const pic = $img.attr('data-original') || $img.attr('src');
            
            // 获取标题
            const title = $item.find('.module-card-item-title strong').text().trim() || 
                         $item.find('.module-card-item-title a').text().trim();
            
            // 获取备注（集数/状态）
            const remarks = $item.find('.module-item-note').text().trim();
            
            // 获取分类/类型信息
            const category = $item.find('.module-card-item-class').text().trim();
            
            // 获取详细信息（年份、地区、类型）
            const infoContent = $item.find('.module-info-item-content').first().text().trim();
            
            return {
                vod_id: detailLink,
                vod_name: title,
                vod_pic: pic,
                vod_remarks: remarks || category || infoContent.split('/')[0]?.trim() || '',
                // 可以添加更多字段
                vod_year: infoContent.split('/')[0]?.trim() || '',
                vod_area: infoContent.split('/')[1]?.trim() || '',
                vod_type: infoContent.split('/')[2]?.trim() || category
            };
        }).filter(v => v.vod_id && v.vod_name); // 过滤掉无效结果
        
        return JSON.stringify({ 
            list: videos,
            page: 1 
        });
    } catch (e) {
        console.error('Search error:', e);
        return JSON.stringify({ list: [] });
    }
}

async function detail(id) {
    try {
        const url = id.startsWith('http') ? id : HOST + id;
        const res = await req(url, { headers: { 'User-Agent': UA } });
        const $ = load(res.content);
        
        // 获取影片类型/分类
        const typeLinks = [];
        $('.module-info-tag-link a').each((i, el) => {
            const href = $(el).attr('href') || '';
            // 排除年份和地区链接，只保留分类链接
            if (!href.includes('year=') && !href.includes('area=') && !$(el).attr('title')) {
                typeLinks.push($(el).text().trim());
            }
        });
        
        // 获取导演
        let director = '';
        const directorItem = $('.module-info-item:contains("导演：")');
        if (directorItem.length) {
            director = directorItem.find('.module-info-item-content a').map((i, a) => $(a).text().trim()).get().join(',');
        }
        
        // 获取主演
        let actor = '';
        const actorItem = $('.module-info-item:contains("主演：")');
        if (actorItem.length) {
            actor = actorItem.find('.module-info-item-content a').map((i, a) => $(a).text().trim()).get().join(',');
        }
        
        // 获取上映年份
        let year = '';
        const yearItem = $('.module-info-item:contains("上映：")');
        if (yearItem.length) {
            year = yearItem.find('.module-info-item-content').text().trim();
        }
        
        // 获取更新信息/集数
        let remarks = '';
        const updateItem = $('.module-info-item:contains("更新：")');
        if (updateItem.length) {
            remarks = updateItem.find('.module-info-item-content').text().trim();
        }
        
        // 获取集数信息
        let episodeInfo = '';
        const episodeItem = $('.module-info-item:contains("集数：")');
        if (episodeItem.length) {
            episodeInfo = episodeItem.find('.module-info-item-content').text().trim();
            if (episodeInfo && !remarks) {
                remarks = episodeInfo;
            } else if (episodeInfo && remarks) {
                remarks = remarks + ' ' + episodeInfo;
            }
        }
        
        // 获取剧情简介
        let content = '';
        const contentItem = $('.module-info-introduction-content');
        if (contentItem.length) {
            content = contentItem.text().trim().replace(/\s+/g, ' ');
        }
        
        // 获取播放列表
        const playFrom = [];
        const playUrls = [];
        
        // 获取播放来源（线路）- 从module-tab-items-box中获取
        $('.module-tab-items-box .module-tab-item').each((i, el) => {
            const sourceName = $(el).find('span').first().text().trim();
            if (sourceName) {
                playFrom.push(sourceName);
            }
        });
        
        // 获取各线路的播放列表 - 对应每个tab-list
        $('.tab-list.module-list').each((i, list) => {
            // 跳过非播放列表的tab-list（比如可能有其他tab）
            if (!$(list).hasClass('his-tab-list')) return;
            
            const episodes = [];
            $(list).find('.module-play-list-content a.module-play-list-link').each((j, a) => {
                const episodeName = $(a).find('span').text().trim() || $(a).text().trim();
                const episodeLink = $(a).attr('href');
                if (episodeName && episodeLink) {
                    episodes.push(episodeName + '$' + episodeLink);
                }
            });
            
            if (episodes.length > 0) {
                playUrls.push(episodes.join('#'));
            }
        });
        
        // 确保playFrom和playUrls数量一致
        if (playFrom.length !== playUrls.length) {
            console.log('线路数量和播放列表数量不匹配:', playFrom.length, playUrls.length);
            // 取较小值，避免数组越界
            const minLength = Math.min(playFrom.length, playUrls.length);
            playFrom.splice(minLength);
            playUrls.splice(minLength);
        }
        
        const vod = {
            vod_id: id,
            vod_name: $('h1').text().trim(),
            vod_pic: $('.module-info-poster img').attr('data-original') || $('.module-info-poster img').attr('src'),
            vod_type: typeLinks.join(','),
            vod_actor: actor,
            vod_director: director,
            vod_year: year,
            vod_remarks: remarks,
            vod_content: content,
            vod_play_from: playFrom.join('$$$'),
            vod_play_url: playUrls.join('$$$')
        };
        
        return JSON.stringify({ list: [vod] });
    } catch (e) { 
        console.error('Detail error:', e);
        return null; 
    }
}

async function play(flag, id, flags) {
    try {
        const url = id.startsWith('http') ? id : HOST + id;
        const res = await req(url, { headers: { 'User-Agent': UA } });
        const html = res.content;
        
        const playerStart = html.indexOf('var player_aaaa=');
        if (playerStart === -1) {
            throw new Error();
        }
        
        const playerEnd = html.indexOf('</script>', playerStart);
        if (playerEnd === -1) {
            throw new Error();
        }
        
        const playerScript = html.substring(playerStart + 'var player_aaaa='.length, playerEnd);
        const cleanScript = playerScript.split(';')[0].trim();
        const playerData = JSON.parse(cleanScript);
        if (!playerData) {
            throw new Error();
        }

        let videoUrl = playerData.url || '';
        const encrypt = String(playerData.encrypt || '0');

        if (encrypt === '1') {
            videoUrl = decodeURIComponent(videoUrl);
        } else if (encrypt === '2') {
            const base64Str = Crypto.enc.Base64.parse(videoUrl).toString(Crypto.enc.Utf8);
            videoUrl = decodeURIComponent(base64Str);
        }

        videoUrl = videoUrl.trim();
        const directVideoPattern = /\.(m3u8|mp4|mkv|flv|avi|mov|wmv|webm)(\?.*)?$/i;
        const isDirectVideo = directVideoPattern.test(videoUrl);
        
        if (videoUrl && isDirectVideo) {
            return JSON.stringify({ parse: 0, url: videoUrl });
        } else if (videoUrl) {
            // 使用FreeOK的解析器
            const parserUrl = `https://svip.qlplayer.cyou/?url=${encodeURIComponent(videoUrl)}`;
            
            try {
                const parserRes = await req(parserUrl);
                const parserHtml = parserRes.content;
                
                if (parserHtml) {
                    const apiTokenMatch = parserHtml.match(/apiToken:\s*"([^"]+)"/);
                    if (apiTokenMatch && apiTokenMatch[1]) {
                        const apiToken = apiTokenMatch[1];
                        const resolveApiUrl = `https://svip.qlplayer.cyou/api/resolve.php?token=${encodeURIComponent(apiToken)}`;
                        
                        const resolveRes = await req(resolveApiUrl);
                        
                        if (resolveRes.content) {
                            const resolveData = JSON.parse(resolveRes.content);
                            
                            if (resolveData.code === 200 && resolveData.url) {
                                const videoUrlResolved = resolveData.url.replace(/\\\//g, '/');
                                return JSON.stringify({ parse: 0, url: videoUrlResolved });
                            }
                        }
                    }
                }
            } catch (apiError) {
                // 忽略解析错误，回退到默认播放
            }
            
            return JSON.stringify({ parse: 1, url: url });
        } else {
            throw new Error();
        }
    } catch {
        return JSON.stringify({ parse: 0, url: id });
    }
}

export function __jsEvalReturn() {
    return { 
        init, home, homeVod, category, detail, play, search 
    };
}