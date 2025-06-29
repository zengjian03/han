import req from '../../util/req.js';
import { MOBILE_UA } from '../../util/misc.js';
import { load } from 'cheerio';

let url = 'https://cn.baozimh.com';
const img = 'https://static-tw.baozimh.com/cover/';
const img2 = '?w=285&h=375&q=100';

async function request(reqUrl) {
    let resp = await req.get(reqUrl, {
        headers: {
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'User-Agent': MOBILE_UA,
        },
    });
    return resp.data;
}

async function init(_inReq, _outResp) {
    return {};
}

async function home(_inReq, _outResp) {
    var html = await request(url + '/classify');
    const $ = load(html);
    let filterObj = { c1: [] };
    for (const nav of $('div.classify div.nav')) {
        const as = $(nav).find('a.item');
        const checkUrl = decodeURIComponent(as[1].attribs.href);
        const reg = /type=(.*)&region=(.*)&state=(.*)&filter=(.*)/;
        const matchs = checkUrl.match(reg);
        let typeKey = '';
        let typeIdx = 1;
        if (matchs[1] != 'all') {
            typeKey = 'type';
            typeIdx = 1;
        } else if (matchs[2] != 'all') {
            typeKey = 'region';
            typeIdx = 2;
        } else if (matchs[3] != 'all') {
            typeKey = 'state';
            typeIdx = 3;
        } else if (matchs[4] != '*') {
            typeKey = 'filter';
            typeIdx = 4;
        }
        const tvals = [];
        for (const a of as) {
            tvals.push({
                n: $(a).text().trim(),
                v: decodeURIComponent(a.attribs.href).match(reg)[typeIdx],
            });
        }
        filterObj['c1'].push({
            key: typeKey,
            name: '',
            wrap: typeIdx == 1 ? 1 : 0,
            init: typeIdx == 4 ? '*' : 'all',
            value: tvals,
        });
    }

    return {
        class: [{ type_name: 'all', type_id: 'c1' }],
        filters: filterObj,
    };
}

async function category(inReq, _outResp) {
    const tid= inReq.body.id;
    const pg =inReq.body.page;
    const extend = inReq.body.filters;
    let page = pg || 1;
    if (page == 0) page = 1;
    let link = `${url}/api/bzmhq/amp_comic_list?type=${extend.type || 'all'}&region=${extend.region || 'all'}&state=${extend.state || 'all'}&filter=${extend.filter || '*'}`;
    link += '&page=' + page + '&limit=36&language=cn';
    var html = await request(link);
    let books = [];
    for (const book of html.items) {
        books.push({
            book_id: book.comic_id,
            book_name: book.name,
            book_pic: img + book.topic_img + img2,
            book_remarks: book.author || '',
        });
    }
    return {
        page: page,
        pagecount: books.length == 36 ? page + 1 : page,
        list: books,
    };
}

async function detail(inReq, _outResp) {
    const ids = !Array.isArray(inReq.body.id) ? [inReq.body.id] : inReq.body.id;
    const books = [];
    for(const id of ids){
    var html = await request(`${url}/comic/${id}`);
    const $ = load(html);
    let book = {
        book_director: $('[data-hid$=og:novel:author]')[0].attribs.content || '',
        book_content: $('[data-hid$=og:description]')[0].attribs.content || '',
    };
    const formatUrl = (_, a) => {
        return $(a).text().replace(/\$|#/g, '').trim() + '$' + decodeURIComponent(a.attribs.href);
    };
    let urls =$('div#chapter-items a.comics-chapters__item').map(formatUrl).get();
    urls.push(...$('div#chapters_other_list a.comics-chapters__item').map(formatUrl).get());
    if (urls.length == 0) {
        urls = $('div.pure-g a.comics-chapters__item').map(formatUrl).get().reverse();
    }
    book.volumes = '默认';
    book.urls = urls.join('#');
    books.push(book);
}
    return {
        list: books,
    };
}

async function play(inReq, _outResp) {
    let id = inReq.body.id;
    var html = await request(url + id);
        const $ = load(html);

        var content = [];
        for (const img of $('amp-img')) {
            content.push(img.attribs.src);
        }
        return {
            content: content,
        };
}

async function search(inReq, _outResp) {
    const wd = inReq.body.wd;
    var html = await request(`${url}/search?q=${wd}`);
    const $ = load(html);
    const books = [];
    for (const a of $('div.classify-items a.comics-card__poster')) {
        books.push({
            book_id: a.attribs.href.replace('/comic/', ''),
            book_name: a.attribs.title,
            book_pic: $(a).find('amp-img:first')[0].attribs.src,
            book_remarks: '',
        });
    }
    return {
        page: 1,
        pagecount: 1,
        list: books,
    };
}

async function test(inReq, outResp) {
    try {
        const printErr = function (json) {
            if (json.statusCode && json.statusCode == 500) {
                console.error(json);
            }
        };
        const prefix = inReq.server.prefix;
        const dataResult = {};
        let resp = await inReq.server.inject().post(`${prefix}/init`);
        dataResult.init = resp.json();
        printErr(resp.json());
        resp = await inReq.server.inject().post(`${prefix}/home`);
        dataResult.home = resp.json();
        printErr(resp.json());
        if (dataResult.home.class.length > 0) {
            resp = await inReq.server.inject().post(`${prefix}/category`).payload({
                id: dataResult.home.class[0].type_id,
                page: 1,
                filter: true,
                filters: {},
            });
            dataResult.category = resp.json();
            printErr(resp.json());
            if (dataResult.category.list.length > 0) {
                resp = await inReq.server.inject().post(`${prefix}/detail`).payload({
                    id: dataResult.category.list[0].book_id, // dataResult.category.list.map((v) => v.vod_id),
                });
                dataResult.detail = resp.json();
                printErr(resp.json());
                if (dataResult.detail.list && dataResult.detail.list.length > 0) {
                    dataResult.play = [];
                    for (const book of dataResult.detail.list) {
                        const flags = book.volumes.split('$$$');
                        const ids = book.urls.split('$$$');
                        for (let j = 0; j < flags.length; j++) {
                            const flag = flags[j];
                            const urls = ids[j].split('#');
                            for (let i = 0; i < urls.length && i < 2; i++) {
                                resp = await inReq.server
                                    .inject()
                                    .post(`${prefix}/play`)
                                    .payload({
                                        flag: flag,
                                        id: urls[i].split('$')[1],
                                    });
                                dataResult.play.push(resp.json());
                            }
                        }
                    }
                }
            }
        }
        resp = await inReq.server.inject().post(`${prefix}/search`).payload({
            wd: '入手',
            page: 1,
        });
        dataResult.search = resp.json();
        printErr(resp.json());
        return dataResult;
    } catch (err) {
        console.error(err);
        outResp.code(500);
        return { err: err.message, tip: 'check debug console output' };
    }
}

export default {
    meta: {
        key: 'baozimh',
        name: '包子漫画',
        type: 20,
    },
    api: async (fastify) => {
        fastify.post('/init', init);
        fastify.post('/home', home);
        fastify.post('/category', category);
        fastify.post('/detail', detail);
        fastify.post('/play', play);
        fastify.post('/search', search);
        fastify.get('/test', test);
    },
};
