import req from './util/req.js';
import { load } from 'cheerio';


let url = 'https://godamanga.com';

async function request(reqUrl) {
    let resp = await req.get(reqUrl, {
        headers: {
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'User-Agent':agentSp || UA,
        },
    });
    return resp.data;
}

async function init(_inReq, _outResp) {
    return {};
}

async function home(_inReq, _outResp) {
    var html = await request(url+"/manga-genre");
    const $ = load(html);
    let classes = [];
    for (const a of $('div.overflow-x-auto > a[href!="/manga"]')) {
        classes.push({
            type_id: a.attribs.href,
            type_name: $(a).find(".abutton").text().trim().replace("#",'')
        });
    }
    return {
        class: classes,
    };
}

async function category(inReq, _outResp) {
    const tid= inReq.body.id;
    const pg =inReq.body.page;
    let page = pg || 1;
    if (page == 0) page = 1;
    var html = await request(url + `/${tid}/page/${pg}`);
    const $ = load(html);
    let books = [];
    for (const pb of $('div.pb-2')) {
        const a = $(pb).find('a:first')[0];
        const img = $(a).find('img:first')[0];
        const h3 = $(pb).find('h3:first')[0];
        books.push({
            book_id: a.attribs.href,
            book_name: h3.children[0].data.trim(),
            book_pic: img.attribs.src
        });
    }
    return {
        page: pg,
        pagecount: $('a:contains(下一页)').length === 0 ? pg + 1 : pg,
        list: books,
    };
}

async function detail(inReq, _outResp) {
    const ids = [inReq.body.id];
    const books = [];
    for (const id of ids) {
    var info = id.split('/');
        var html = await request(url+`/${id}`);
        let $ = load(html);
        let book = {
            book_name: $('h1').text().trim(),
            book_director: $('div.text-small>a[href*="/author/"]')
                .map((_, a) => $(a).text().trim())
                .get()
                .join('/'),
            book_content: $('#info > div:nth-child(1) > div.block.text-left.mx-auto > p').text().trim(),
        };
        html = await request(url + `/chapterlist/${info[2]}`);
        $ = load(html);
        let urls = [];
        const links = $('div.chapteritem>a[href*="/m.cocolamanhua.com/manga/"]');
        for (const l of links) {
            var name = $(l).text().trim();
            var link = l.attribs.href;
            urls.push(name + '$' + link);
        }
        book.volumes = '全卷';
        book.urls = urls.join('#');
        books.push(book);
    }
    return {
        list: books,
     };
}

async function play(inReq, _outResp) {
    let id = inReq.body.id;
    var html = await request(id);
    let $ = load(html);
    var content = [];
   for (const l of $('.w-full> img')){
       const img = $(l).attr('data-src');
       // const jpg = sharp(img.toString()).toFormat('jpeg')
        content.push(img);
    }
    return {
        content: content
    };
}


async function search(inReq, _outResp) {
    const wd = inReq.body.wd;
    const html = await req.get(`${url}/s/${encodeURIComponent(wd)}`);
    const $ = load(html);
    let books = [];
    for (const pb of $('div.pb-2')) {
        const a = $(pb).find('a:first')[0];
        const img = $(a).find('img:first')[0];
        const h3 = $(pb).find('h3:first')[0];
        books.push({
            book_id: a.attribs.href,
            book_name: h3.children[0].data.trim(),
            book_pic: img.attribs.src,
        });
        console.log(books)
    }
    return {
        tline: 2,
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
        key: 'coco',
        name: 'CoCo漫画',
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
