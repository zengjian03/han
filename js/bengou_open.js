import req from '../../util/req.js';
import { PC_UA } from '../../util/misc.js';
import { load } from 'cheerio';
import CryptoJS from 'crypto-js';

let url = 'https://www.bengou.co';

async function request(reqUrl) {
    let resp = await req.get(reqUrl, {
        headers: {
            'User-Agent': PC_UA,
        },
    });
    return resp.data;
}

// cfg = {skey: siteKey, ext: extend}
async function init(_inReq, _outResp) {
    return {};
}

async function home(_inReq, _outResp) {
    let fiters = '';
    const classes = [{'type_id':'all','type_name':'all'}];
    const filterObj = {
        'all':[
            {'key':'type','name':'进度','init':'all','value':[{'n':'全部','v':'all'},{'n':'连载','v':'lianzai'},{'n':'完结','v':'wanjie'}]},
            {'key':'type','name':'地区','init':'all','value':[{'n':'日韩','v':'rihan'},{'n':'内地','v':'neidi'},{'n':'港台','v':'gangntai'},{'n':'欧美','v':'oumei'},{'n':'其他','v':'qita'}]},
            {'key':'type','name':'读者','init':'all','value':[{'n':'少年','v':'shaonianqu'},{'n':'少女','v':'shaonvqu'},{'n':'青年','v':'qingnian'},{'n':'少儿','v':'shaoer'}]},
            {'key':'type','name':'题材','init':'all','value':[{'n':'热血','v':'rexue'},{'n':'格斗','v':'gedou'},{'n':'科幻','v':'kehuan'},{'n':'竞技','v':'jingji'},{'n':'搞笑','v':'gaoxiao'},{'n':'推理','v':'tuili'},{'n':'恐怖','v':'kongbu'},{'n':'耽美','v':'danmei'},{'n':'少女','v':'shaonv'},{'n':'恋爱','v':'lianai'},{'n':'生活','v':'shenghuo'},{'n':'战争','v':'zhanzheng'},{'n':'故事','v':'gushi'},{'n':'冒险','v':'maoxian'},{'n':'魔幻','v':'mohuan'},{'n':'玄幻','v':'xuanhuan'},{'n':'校园','v':'xiaoyuan'},{'n':'悬疑','v':'xuanyi'},{'n':'萌系','v':'mengxi'},{'n':'穿越','v':'chuanyue'},{'n':'后宫','v':'hougong'},{'n':'都市','v':'dushi'},{'n':'武侠','v':'wuxia'},{'n':'历史','v':'lishi'},{'n':'同人','v':'tongren'},{'n':'励志','v':'lizhi'},{'n':'百合','v':'baihe'},{'n':'治愈','v':'zhiyu'},{'n':'机甲','v':'jijia'},{'n':'纯爱','v':'chunai'},{'n':'美食','v':'meishi'},{'n':'血腥','v':'xuexing'},{'n':'僵尸','v':'jiangshi'},{'n':'恶搞','v':'egao'},{'n':'虐心','v':'nuexin'},{'n':'动作','v':'dongzuo'},{'n':'惊险','v':'jingxian'},{'n':'唯美','v':'weimei'},{'n':'震撼','v':'zhenhan'},{'n':'复仇','v':'fuchou'},{'n':'侦探','v':'zhentan'},{'n':'脑洞','v':'naodong'},{'n':'奇幻','v':'qihuan'},{'n':'宫斗','v':'gongdou'},{'n':'爆笑','v':'baoxiao'},{'n':'运动','v':'yundong'},{'n':'青春','v':'qingchun'},{'n':'灵异','v':'lingyi'},{'n':'古风','v':'gufeng'},{'n':'权谋','v':'quanmou'},{'n':'节操','v':'jiecao'},{'n':'明星','v':'mingxing'},{'n':'暗黑','v':'anhei'},{'n':'社会','v':'shehui'},{'n':'浪漫','v':'langman'},{'n':'栏目','v':'lanmu'},{'n':'仙侠','v':'xianxia'}]},
            {'key':'type','name':'字母','init':'all','value':[{'n':'A','v':'lettera'},{'n':'B','v':'letterb'},{'n':'C','v':'letterc'},{'n':'D','v':'letterd'},{'n':'E','v':'lettere'},{'n':'F','v':'letterf'},{'n':'G','v':'letterg'},{'n':'H','v':'letterh'},{'n':'I','v':'letteri'},{'n':'J','v':'letterj'},{'n':'K','v':'letterk'},{'n':'L','v':'letterl'},{'n':'M','v':'letterm'},{'n':'N','v':'lettern'},{'n':'O','v':'lettero'},{'n':'P','v':'letterp'},{'n':'Q','v':'letterq'},{'n':'R','v':'letterr'},{'n':'S','v':'letters'},{'n':'T','v':'lettert'},{'n':'U','v':'letteru'},{'n':'V','v':'letterv'},{'n':'W','v':'letterw'},{'n':'X','v':'letterx'},{'n':'Y','v':'lettery'},{'n':'Z','v':'letterz'}]},
        ],
    };
    return JSON.stringify({
        class: classes,
        filters: filterObj,
    });
}

async function category(inReq, _outResp) {
    let pg = inReq.body.page;
    const extend = inReq.body.filters;
    if (pg == 0) pg = 1;
    let page = '';
    if (pg > 1) {
        page = `${pg}.html`;
    }
    const link = url + `/${extend.type || 'all'}/${page}`;
    const html = await request(link);
    const $ = load(html);
    // const books = _.map(list, (item) => {
    //     const $item = $(item);
    //     const $a = $item.find('dt a:first');
    //     const $img = $item.find('img:first');
    //     const $span = $item.find('span:first');
    //     return {
    //         book_id: $a.attr('href'),
    //         book_name: $a.text(),
    //         book_pic: $img.attr('src'),
    //         book_remarks: $span.text(),
    //     };
    // });
    const books=[];
    for(const list of  $('.dmList li') ){
        const a = $(list).find('dt a:first');
        const img = $(list).find('img:first');
        const span = $(list).find('span:first');
        books.push({
            book_id:a.attr('href'),
            book_name:a.text(),
            book_pic:img.attr('src'),
            book_remarks: span.text()
        });
    }
    const hasMore = $('.NewPages a:contains(下一页)').length > 0;
    return {
        page: pg,
        pagecount: hasMore ? pg + 1 : pg,
        list: books,
    };
}

async function detail(inReq, _outResp) {
    const id = inReq.body.id;
    const html = await request(url + id);
    const $ = load(html);
    const book = {
        book_name: $('.title h1').text(),
        book_director: $('.info p:contains(原著作者) a').text().trim(),
        book_content: $('.introduction').text().trim(),
        book_remarks: $('.title a:first').text(),
    };
    // const urls = _.map(list, (item) => {
    //     const $item = $(item);
    //     let title = $item.text().trim();
    //     if (_.isEmpty(title)) {
    //         title = '观看'
    //     }
    //     const href = $item.attr('href');
    //     return title + '$' + href;
    // }).join('#');
    let urls=[];
    for(const item of $('.plist a')){
        let title =$(item).text().trim();
        if(title===null){
            title = '观看'
        }
        const href = $(item).attr('href');
        urls.push(title+'$'+href);
    }
    book.volumes = '笨狗';
    book.urls = urls.join('#');

    return {
        list: [book],
    };
}

async function play(inReq, _outResp) {
        const id = inReq.body.id;
        const html = await request(url + id);
        const matches = html.match(/var qTcms_S_m_murl_e=\"(.*)\";/);
        const decoded = base64Decode(matches[1]);
        const picList = decoded.split('$');
        const content = [];
        for (let i = 0; i < picList.length; i += 2) {
            content.push(picList[i]);
        }
        return {
            content: content,
        };
}

function base64Decode(text) {
    return CryptoJS.enc.Utf8.stringify(CryptoJS.enc.Base64.parse(text));
}

async function search(inReq, _outResp) {
    let pg = inReq.body.page;
    const wd = inReq.body.wd;
    if (pg == 0) pg = 1;
    let page = '';
    if (pg > 1) {
        page = `&page=${pg}`;
    }
    const link = url + `/statics/search.aspx?key=${encodeURIComponent(wd)}${page}`;
    const html = await request(link);
    const $ = load(html);
    const books=[];
    for(const list of  $('.dmList li') ){
        const a = $(list).find('dt a:first');
        const img = $(list).find('img:first');
        const span = $(list).find('span:first');
        books.push({
            book_id:a.attr('href'),
            book_name:a.text(),
            book_pic:img.attr('src'),
            book_remarks: span.text()
        });
    }
    const hasMore = $('.NewPages a:contains(下一页)').length > 0;
    return {
        page: pg,
        pagecount: hasMore ? pg + 1 : pg,
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
            wd: '爱',
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
        key: 'bg',
        name: '笨狗漫画',
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
