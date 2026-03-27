// 本资源来源于互联网公开渠道，仅可用于个人学习爬虫技术。
// 严禁将其用于任何商业用途，下载后请于 24 小时内删除，搜索结果均来自源站，本人不承担任何责任。

let host = 'https://a131.ybbyelc.com';
let key = '58928cae68092afc';
let iv = 'e9d732a1edcdcc0a';
let siteKey = '';
let siteType = 3;
let block_id = new Set();
let dj_id = '3';
let categories = {};
const headers = {
    'User-Agent': 'Dart/3.8 (dart:io)',
    'version': '1.0.0',
    'clienttype': 'mobile'
};

async function init(cfg) {
    try {
        const ext = typeof cfg.ext === 'string' ? JSON.parse(cfg.ext) : cfg.ext;
        if (ext) {
            host = ext.host || host;
            key = ext.key || key;
            iv = ext.iv || iv;
        }
    } catch (e) {}
    try {
        siteKey = cfg.skey;
        siteType = cfg.stype;
        const url = `${host}/addons/appto/app.php/tindex/home_config2`;
        const resp = await req(url, { method: 'POST', postType: 'form', data: {}, headers: getHeaders() });
        const json = JSON.parse(resp.content);
        const data = decode(json.data);
        if (data) {
            if (Array.isArray(data.viphome)) {
                data.viphome.forEach(i => block_id.add(i.id));
            }
            if (Array.isArray(data.collections)) {
                const dj = data.collections.find(j => j.title === '短剧');
                if (dj) dj_id = String(dj.id);
            }
            categories = {
                itemsValue: data.itemsValue || [],
                collections: data.collections || []
            };
        }
    } catch (e) {}
}

async function home(filter) {
    if (!host || !categories.itemsValue?.length) return '{}';
    const shortDramaMap = new Map();
    (categories.collections || []).forEach(item => {
        if (item.short === '1') {
            shortDramaMap.set(item.title, `short@${item.title}`);
        }
    });
    const classes = [];
    const filters = {};
    const itemsValueMap = new Map();
    categories.itemsValue.forEach(item => {
        if (item.title === '全部') return;
        itemsValueMap.set(item.title, item);
        const type_id = shortDramaMap.get(item.title) || item.title;
        classes.push({ type_id, type_name: item.title });
    });
    classes.forEach(cls => {
        const { type_id, type_name } = cls;
        const query_title = type_id.includes('@') ? type_id.split('@')[1] : type_name;
        const item = itemsValueMap.get(query_title);
        if (!item) return;
        const filterList = [];
        if (item.Classes) {
            const clsList = parseTags(item.Classes);
            const uniqueCls = clsList.filter(c => !blackListRegex.test(c));
            if (uniqueCls.length > 0) {
                filterList.push({
                    key: 'class',
                    name: '类型',
                    init: '',
                    value: [{ n: '全部', v: '' }, ...uniqueCls.map(v => ({ n: v, v: v }))]
                });
            }
        }
        if (item.Areas) {
            const areaList = parseTags(item.Areas);
            if (areaList.length > 0) {
                filterList.push({
                    key: 'area',
                    name: '地区',
                    init: '',
                    value: [{ n: '全部', v: '' }, ...areaList.map(v => ({ n: v, v: v }))]
                });
            }
        }
        if (item.Years) {
            const yearList = parseTags(item.Years);
            if (yearList.length > 0) {
                filterList.push({
                    key: 'year',
                    name: '年份',
                    init: '',
                    value: [{ n: '全部', v: '' }, ...yearList.map(v => ({ n: v, v: v }))]
                });
            }
        }
        filterList.push({
            key: 'sort',
            name: '排序',
            init: 'Time',
            value: [
                { n: '最新', v: 'Time' },
                { n: '评分', v: 'Score' },
                { n: '人气', v: 'Hits' }
            ]
        });
        filters[type_id] = filterList;
    });
    return JSON.stringify({ class: classes, filters: filters });
}

function parseTags(str) {
    if (!str) return [];
    return [...new Set(str.split(',').map(s => s.trim()).filter(Boolean))];
}

async function homeVod() {
    if (!host) return '{}';
    try {
        const resp = await req(`${host}/addons/appto/app.php/tindex/home_vod_list2`, {
            method: 'POST',
            postType: 'form',
            data: { 'Id': '0', 'Type': '1', 'Page': '1', 'Limit': '10' },
            headers: getHeaders()
        });
        const data = decode(JSON.parse(resp.content).data);
        let vods = [];
        if (data) {
            if (data.sections) {
                data.sections.forEach(s => {
                    if (s.vods) vods.push(...s.vods);
                });
            }
            if (data.vods) {
                vods.push(...data.vods);
            }
        }
        return JSON.stringify({ list: arr2vods(vods) });
    } catch (e) {
        return '{}';
    }
}

async function category(tid, pg, filter, extend) {
    if (!host) return '{}';
    let tab = '影视';
    let typeId = tid;
    if (tid.startsWith('short@') || tid.includes('短剧')) {
        tab = '短剧';
        typeId = tid.replace(/^short@/, '');
    }

    const payload = {
        'Page': String(pg),
        'Limit': '44',
        'Tab': tab,
        'Type': typeId,
        'Class': extend.class ?? '',
        'Year': extend.year ?? '',
        'Area': extend.area ?? '中国大陆',
        'Sort': extend.sort ?? ''
    };

    try {
        const resp = await req(`${host}/addons/appto/app.php/tindex/page_vod_lists`, {
            method: 'POST',
            postType: 'form',
            data: payload,
            headers: getHeaders()
        });
        const data = decode(JSON.parse(resp.content).data);
        return JSON.stringify({
            list: arr2vods(data.list),
            page: parseInt(pg),
            pagecount: pageCount(data.limit || 44, data.total || 0),
            limit: parseInt(data.limit || 44),
            total: parseInt(data.total || 0)
        });
    } catch (e) {
        return JSON.stringify({ list: [], page: 1, pagecount: 1 });
    }
}

async function search(wd, quick, pg = 1) {
    if (!host) return '{}';
    try {
        const resp = await req(`${host}/addons/appto/app.php/tindex/search_film`, {
            method: 'POST',
            postType: 'form',
            data: {
                'Limit': '10',
                'Page': String(pg || 1),
                'Search': wd,
                'type': null
            },
            headers: getHeaders()
        });
        const data = decode(JSON.parse(resp.content).data);
        const vodsData = data?.vods || { list: [], limit: 10, total: 0 };
        return JSON.stringify({
            list: arr2vods(vodsData.list),
            page: parseInt(pg),
            pagecount: pageCount(vodsData.limit, vodsData.total)
        });
    } catch (e) {
        return JSON.stringify({ list: [], page: 1, pagecount: 1 });
    }
}

async function detail(id) {
    if (!host) return '{}';
    try {
        const resp = await req(`${host}/addons/appto/app.php/tindex/page_player`, {
            method: 'POST',
            postType: 'form',
            data: { 'id': id },
            headers: getHeaders()
        });
        const data = decode(JSON.parse(resp.content).data);
        if (block_id.has(data.type_id) || data.group_id !== 0) {
            return JSON.stringify({ list: [] });
        }
        const play_from = [];
        const play_urls = [];
        if (Array.isArray(data.vod_play_list)) {
            data.vod_play_list.forEach(i => {
                if (!Array.isArray(i.urls)) return;
                const urls = i.urls.map(j => {
                    const prefix = String(data.type_id) === dj_id ? 'direct@' : '';
                    return `${j.name}$${prefix}${j.url}`;
                });
                if (urls.length > 0) {
                    play_urls.push(urls.join('#'));
                    play_from.push(i.from);
                }
            });
        }
        const video = {
            vod_id: data.vod_id,
            vod_name: data.vod_name,
            vod_pic: formatPic(data.vod_pic_thumb || data.vod_pic_vertical || data.vod_pic),
            vod_content: data.vod_blurb,
            vod_remarks: data.vod_remarks,
            vod_year: data.vod_year,
            vod_area: data.vod_area,
            vod_actor: data.vod_actor,
            vod_director: data.vod_director,
            vod_play_from: play_from.join('$$$'),
            vod_play_url: play_urls.join('$$$'),
            type_name: data.vod_class
        };

        return JSON.stringify({ list: [video] });
    } catch (e) {
        return JSON.stringify({ list: [] });
    }
}

async function play(flag, id, flags) {
    let url = id;
    if (id.startsWith('direct@')) {
        url = id.slice(7)
    } else if (id.includes('.m3u8')) {
        url = await js2Proxy(false, siteType, siteKey, encodeURIComponent(id), headers);
    }
    return JSON.stringify({ parse: 0, url: url, header: headers });
}

async function proxy(params) {
    try {
        const url = decodeURIComponent(params.url ?? params[0]);
        const m3u8Content = await m3u8(url);
        return JSON.stringify({
            code: 200,
            content: m3u8Content,
            headers: { "Content-Type": "application/vnd.apple.mpegurl" }
        });
    } catch (e) {
        return JSON.stringify({ code: 500, content: "ERROR:" + e.message, headers: {} });
    }
}

function resolveUrl(baseUrl, relativeUrl) {
    if (!relativeUrl) return baseUrl;
    if (relativeUrl.startsWith('http')) return relativeUrl;
    if (relativeUrl.startsWith('//')) return 'http:' + relativeUrl;
    try {
        const baseMatch = baseUrl.match(/^(https?:\/\/[^\/]+)(.*)$/);
        if (!baseMatch) return baseUrl + relativeUrl;
        const origin = baseMatch[1];
        const fullPath = baseMatch[2];
        const basePath = fullPath.substring(0, fullPath.lastIndexOf('/') + 1);
        if (relativeUrl.startsWith('/')) {
            return origin + relativeUrl;
        }
        const cleanBasePath = basePath.startsWith('/') ? basePath.slice(1) : basePath;
        if (cleanBasePath && relativeUrl.startsWith(cleanBasePath)) {
            return origin + '/' + relativeUrl;
        }
        return origin + basePath + relativeUrl;
    } catch (e) {
        return relativeUrl;
    }
}

async function m3u8(url) {
    let currentUrl = url;
    const res = await req(currentUrl, { headers: getHeaders() });
    let content = res.content;
    if (!content) throw new Error('Fetch failed: ' + currentUrl);
    if (content.includes('#EXT-X-STREAM-INF:')) {
        const lines = content.split('\n');
        let bestBandwidth = 0;
        let bestUrl = '';
        for (let i = 0; i < lines.length; i++) {
            if (lines[i].includes('#EXT-X-STREAM-INF:')) {
                const bwMatch = lines[i].match(/BANDWIDTH=(\d+)/);
                if (bwMatch) {
                    const bw = parseInt(bwMatch[1]);
                    if (bw > bestBandwidth) {
                        const nextLine = lines[i + 1]?.trim();
                        if (nextLine && !nextLine.startsWith('#')) {
                            bestBandwidth = bw;
                            bestUrl = resolveUrl(currentUrl, nextLine);
                        }
                    }
                }
            }
        }
        if (bestUrl) return await m3u8(bestUrl);
    }
    const lines = content.split('\n');
    const segments = [];
    let firstSegLineIdx = -1;
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        if (line.startsWith('#EXTINF:')) {
            const match = line.match(/#EXTINF:([\d.]+),/);
            if (match) {
                if (firstSegLineIdx === -1) firstSegLineIdx = i;
                segments.push({
                    dur: parseFloat(match[1]),
                    idx: i
                });
            }
        }
    }
    const removeLineIndices = new Set();
    const durs = segments.map(s => s.dur);
    let removeCount = 0;
    let filterRuleName = "";
    if (durs.length >= 2) {
        const dur2Str = durs[1].toFixed(3);
        if (dur2Str.endsWith('67')) {
            removeCount = 2;
            filterRuleName = `规则A: 第二分片时长尾数.67 (Dur: ${dur2Str})`;
        }
        else if (durs.length >= 3) {
            const dur3Str = durs[2].toFixed(3);
            if (dur3Str.endsWith('67')) {
                removeCount = 3;
                filterRuleName = `规则B: 第三分片时长尾数.67 (Dur: ${dur3Str})`;
            }
            else if (durs.length >= 5) {
                const d3 = parseFloat(durs[2].toFixed(3));
                const d4 = parseFloat(durs[3].toFixed(3));
                const d5 = parseFloat(durs[4].toFixed(3));
                if (d3 === d4 && d4 === d5) {
                    const d1 = parseFloat(durs[0].toFixed(3));
                    const d2 = parseFloat(durs[1].toFixed(3));
                    if (!(d1 === d2 && d2 === d3)) {
                        const sum12 = parseFloat((durs[0] + durs[1]).toFixed(3));
                        if (sum12 === 4.0) {
                            removeCount = 2;
                            filterRuleName = `规则C: 前两段和为4.0且后三段重复 (Sum1+2: ${sum12}, D3=D4=D5: ${d3})`;
                        }
                    }
                }
            }
        }
    }
    if (removeCount > 0) {
        console.log(`[58YS M3U8 Filter] 触发规则: [${filterRuleName}]`);
        console.log(`[58YS M3U8 Filter] 计划移除前 ${removeCount} 个分片:`);
        for (let k = 0; k < removeCount; k++) {
            const seg = segments[k];
            const lineIdx = seg.idx;
            let segmentUrl = "未知URL";
            if (lines[lineIdx + 1]) {
                segmentUrl = lines[lineIdx + 1].trim();
            }
            console.log(`  - 分片#${k + 1}: 时长=${seg.dur}s, 原始行号=${lineIdx}, URL=${segmentUrl}`);
            removeLineIndices.add(lineIdx);
            removeLineIndices.add(lineIdx + 1);
        }
    }
    const output = [];
    for (let i = 0; i < lines.length; i++) {
        let line = lines[i].trim();
        if (!line) continue;
        if (removeLineIndices.has(i)) continue;

        if (line.startsWith('#EXT-X-KEY:')) {
            line = line.replace(/URI="([^"]+)"/, (_, uri) => `URI="${resolveUrl(currentUrl, uri)}"`);
            output.push(line);
        }
        else if (!line.startsWith('#') && i > firstSegLineIdx) {
            output.push(resolveUrl(currentUrl, line));
        }
        else {
            output.push(line);
        }
    }
    if (output.length === 0 || !output[0].startsWith('#EXTM3U')) {
        output.unshift('#EXTM3U');
    }
    return output.join('\n');
}

function getHeaders() {
    return { ...headers, timestamp: String(Date.now()) };
}

function decode(ciphertext) {
    if (!ciphertext) return null;
    try {
        if (typeof ciphertext === 'object') return ciphertext;
        if (typeof ciphertext === 'string') {
            const decrypted = aesX('AES/CBC/PKCS7', false, ciphertext, true, key, iv, false);
            return JSON.parse(decrypted);
        }
    } catch (e) {
        console.log('decode error: ' + e.message);
    }
    return null;
}

const idCodes = [[31785, 21699], [25439, 34060], [20928, 30368], [36436, 30368], [22182, 25281], [25439, 36925]];
const blackListWords = idCodes.map(g => String.fromCharCode(...g.map(n => n - 666)));
const blackListRegex = new RegExp(blackListWords.join('|'));

function arr2vods(arr) {
    const videos = [];
    if (!Array.isArray(arr)) return videos;
    for (const i of arr) {
        if (i.vod_class && blackListRegex.test(i.vod_class)) continue;
        if (i.group_id !== 0) continue;
        if (block_id.has(i.type_id)) continue;
        if (i.vod_class?.includes('banner')) continue;
        if (i.vod_type_name?.includes('会员')) continue;
        let remarks = i.vod_remarks;
        if ((i.vod_total || 0) > 1) {
            remarks = i.vod_total + '集';
        } else if (!remarks) {
            remarks = '评分：' + (i.vod_score || '0.0');
        }
        videos.push({
            vod_id: i.vod_id,
            vod_name: i.vod_name,
            vod_pic: formatPic(i.vod_pic_thumb || i.vod_pic_vertical || i.vod_pic),
            vod_remarks: remarks,
            vod_year: i.vod_year
        });
    }
    return videos;
}

function formatPic(url) {
    return url ? url.replace('mac://', 'https://') : '';
}

function pageCount(limit, total) {
    const l = parseInt(limit) || 0;
    const t = parseInt(total) || 0;
    if (l <= 0 || t <= 0) return 1;
    return Math.ceil(t / l);
}

export function __jsEvalReturn() {
    return {
        init: init,
        home: home,
        homeVod: homeVod,
        category: category,
        search: search,
        detail: detail,
        play: play,
        proxy: proxy
    };
}