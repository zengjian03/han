let HOST = '';
async function init(cfg) {
    try {
        let res = await req('https://doh.pub/resolve?name=app1.anisee.net&type=txt', {
            method: 'get',
            headers: { 'User-Agent': 'Dart/3.5 (dart:io)' }
        });
        let data = JSON.parse(res.content);
        if (data && data.Answer && data.Answer.length > 0) {
            let encryptedHost = data.Answer[0].data.replace(/"/g, '');
            let iv = null;
            if (typeof getProxy !== 'function') { iv = ''; }
            let decryptedHost = aesX('AES/ECB/PKCS7', false, encryptedHost, true, '94988a169eb10e09a60de57a02a59205', iv, false);
            if (decryptedHost) {
                let healthRes = await req(decryptedHost + '/app/api/health', { method: 'get', headers: { 'User-Agent': 'Dart/3.5 (dart:io)' } });

                if (healthRes && String(healthRes.code) === '200') {
                    HOST = decryptedHost;
                }
            }
        }
    } catch (e) {}
}

async function homeVod() {
    let videos = [];
    let data = await fetchAndDecrypt(HOST + '/app/api/home/tab/get?id=1');
    if (data && data.home_content && Array.isArray(data.home_content)) {
        for (let block of data.home_content) {
            videos = videos.concat(formatVodList(block.vods));
        }
    }
    return JSON.stringify({ list: videos });
}

async function home(filter) {
    let classes = [];
    let filterObj = {};
    let data = await fetchAndDecrypt(HOST + '/app/api/config?platform=android');
    if (data && data.ac_vod_type && Array.isArray(data.ac_vod_type)) {
        for (let type of data.ac_vod_type) {
            let typeId = type.type_id.toString();
            classes.push({ type_id: typeId, type_name: type.type_name });
            let typeFilters = [{
                key: 'sort', name: '排序', init: '0',
                value: [{ n: '最新', v: '0' }, { n: '热度最高', v: '1' }, { n: '好评', v: '2' }]
            }];
            if (type.type_extend && type.type_extend.class) {
                let classValues = [{ n: '全部', v: '' }];
                type.type_extend.class.split(',').forEach(c => {
                    if (c.trim()) classValues.push({ n: c.trim(), v: c.trim() });
                });
                typeFilters.push({ key: 'class', name: '类型', init: '', value: classValues });
            }
            if (type.type_extend && type.type_extend.year) {
                let yearValues = [{ n: '全部', v: '' }];
                type.type_extend.year.split(',').forEach(y => {
                    if (y.trim()) yearValues.push({ n: y.trim(), v: y.trim() });
                });
                typeFilters.push({ key: 'year', name: '年份', init: '', value: yearValues });
            }
            filterObj[typeId] = typeFilters;
        }
    }
    return JSON.stringify({ class: classes, filters: filterObj });
}

async function category(tid, pg, filter, extend) {
    let sort = extend.sort || '0';
    let url = `${HOST}/app/api/content/filter?type=${tid}&page=${pg}&sort=${sort}`;
    if (extend.year) url += `&year=${extend.year}`;
    if (extend.class) url += `&class=${encodeURIComponent(extend.class)}`;
    let data = await fetchAndDecrypt(url);
    let videos = data ? formatVodList(data.filter_vods) : [];
    return JSON.stringify({
        list: videos,
        page: parseInt(pg),
        pagecount: parseInt(pg) + (videos.length > 0 ? 1 : 0)
    });
}

async function search(wd, quick, pg = 1) {
    let url = `${HOST}/app/api/search/full?q=${encodeURIComponent(wd)}`;
    let data = await fetchAndDecrypt(url);
    let videos = data ? formatVodList(data.search_full) : [];

    return JSON.stringify({
        list: videos,
        page: parseInt(pg),
        pagecount: 1
    });
}

async function detail(id) {
    let vod = { vod_id: id, vod_play_from: '', vod_play_url: '' };
    let data = await fetchAndDecrypt(`${HOST}/app/api/vod/${id}`);

    if (data) {
        vod.vod_name = data.vod_name;
        vod.vod_pic = data.vod_pic;
        vod.type_name = data.vod_class || '';
        vod.vod_year = data.vod_year || '';
        vod.vod_remarks = data.vod_remarks || '';
        vod.vod_director = data.vod_author || '';
        vod.vod_content = data.vod_content || '';
        if (data.vod_score) vod.vod_score = data.vod_score.toString();
        let playFroms = [], playUrls = [];
        if (data.playerData && Array.isArray(data.playerData)) {
            for (let p of data.playerData) {
                if (p.name === p.player) {
                    playFroms.push(p.name);
                } else {
                    playFroms.push(`${p.name}\u2005(${p.player})`);
                }
                let epList = [];
                if (p.vids && Array.isArray(p.vids)) {
                    for (let v of p.vids) {
                        let parts = v.split('$');
                        if (parts.length === 2) {
                            epList.push(`${parts[0]}$${p.player},${parts[1]}`);
                        } else {
                            epList.push(v);
                        }
                    }
                }
                playUrls.push(epList.join('#'));
            }
        }
        vod.vod_play_from = playFroms.join('$$$');
        vod.vod_play_url = playUrls.join('$$$');
    }
    return JSON.stringify({ list: [vod] });
}

async function play(flag, vid, flags) {
    try {
        let player = '';
        let parts = vid.split(',',2);
        player = parts[0];
        vid = parts[1];
        if (!vid || !player) {throw new Error();}
        let data = await fetchAndDecrypt(HOST + '/app/api/vod/parse', 'post', { vid: vid, player: player });
        if (data && data.play_url) {
            return JSON.stringify({ parse: 0, url: data.play_url, header: { 'User-Agent': 'libmpv' } });
        }
    } catch (e) {}
    return JSON.stringify({ parse: 0, url: '', header: {} });
}

async function fetchAndDecrypt(url, method = 'get', postData = null) {
    try {
        let options = {
            method: method,
            headers: {
                'User-Agent': 'Dart/3.5 (dart:io)',
                'content-type': 'application/json; charset=utf-8'
            },
            data: postData || undefined
        };
        let res = await req(url, options);
        let json = JSON.parse(res.content);
        if (json && String(json.code) === '200' && json.data) {
            let iv = null;
            if (typeof getProxy !== 'function') { iv = ''; }
            let decryptedStr = aesX('AES/ECB/PKCS7', false, json.data, true, '12842a6b2c6a0d792737847cc028fe9d', iv, false);
            if (decryptedStr) {
                return JSON.parse(decryptedStr);
            }
        }
    } catch (e) {}
    return {};
}

function formatVodList(list) {
    let videos = [];
    if (list && Array.isArray(list)) {
        for (let vod of list) {
            videos.push({
                vod_id: vod.id.toString(),
                vod_name: vod.vod_name,
                vod_pic: vod.vod_pic,
                vod_remarks: vod.vod_remarks || ''
            });
        }
    }
    return videos;
}

export function __jsEvalReturn() {
    return {
        init: init,
        home: home,
        homeVod: homeVod,
        category: category,
        search: search,
        detail: detail,
        play: play
    };
}
