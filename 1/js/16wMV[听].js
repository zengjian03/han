var mv_list = [];
var authors = [];
const starAuthors = '周杰伦,汪苏泷,李荣浩,蔡依林,筷子兄弟,凤凰传奇,程响';
const alphabetList = Array.from({length: 26}, (_, index) => {
    const uppercase = String.fromCharCode(65 + index); // 大写字母 A-Z
    const lowercase = String.fromCharCode(97 + index); // 小写字母 a-z
    // return {n: uppercase, v: lowercase};
    return {n: uppercase, v: uppercase};
});
alphabetList.unshift({n: '全部', v: ''});
var rule = {
    类型: '搜索',
    title: '16wMV',
    alias: '16wMV搜索引擎',
    desc: '仅搜索源纯js写法',
    host: 'hiker://empty',
    url: '',
    searchUrl: 'hiker://empty',
    headers: {
        'User-Agent': 'PC_UA',
    },
    searchable: 1,
    quickSearch: 0,
    filterable: 1,
    double: true,
    play_parse: true,
    limit: 100,
    class_name: '歌手',
    class_url: 'author',
    filter: {
        author: [
            {key: 'letters', name: '首字母', value: alphabetList}
        ]
    },
    // 推荐样式
    hikerListCol: 'icon_round_2',
    // 分类列表样式
    hikerClassListCol: 'avatar',
    // home_flag: '3-0-S',
    home_flag: '3',
    // class_flag: '3-11-S',
    class_flag: '1',
    预处理: async function () {
        let t1 = (new Date()).getTime();
        let _url = rule.params;
        log(`传入参数:${_url}`);
        mv_list = (await request(_url)).split('\n').map((it) => {
            it = it.trim();
            let _tt = it.split(',')[0];
            let _uu = it.split(',')[1];
            if (_tt.includes('-')) {
                return {title: _tt, url: _uu, author: _tt.split('-')[0].trim() || '未知', name: _tt.split('-')[1].trim()}
            } else {
                return {title: _tt, url: _uu, author: '未知', name: _tt.trim()}
            }
        });
        authors = [...new Set(mv_list.filter(it => !it.author.includes('+')).map(it => it.author.trim()))];
        // log(mv_list.slice(0, 3));
        // authors = naturalSort(authors, 'author'); // 不要使用排序，数据太大了排不了
        authors = authors.sort((a, b) => a.localeCompare(b, 'zh-CN', {numeric: true, sensitivity: 'base'}));
        let t2 = (new Date()).getTime();
        log(`读取文件并转json耗时:${t2 - t1}毫秒`);
    },
    lazy: async function (flag, id, flags) {
        return {parse: 0, url: id}
    },
    proxy_rule: async function (params) {
        let {input, proxyPath, getProxyUrl} = this;
        let resp_not_found = [404, 'text/plain', 'not found'];
        return resp_not_found
    },
    action: async function (action, value) {
        if (action === 'only_search') {
            return '此源为纯搜索源，你直接全局搜索这个源或者使用此页面的源内搜索就好了'
        }
        if (action === '源内搜索') {
            let content = JSON.parse(value);
            return JSON.stringify({
                action: {
                    actionId: '__self_search__',
                    skey: '', //目标源key，可选，未设置或为空则使用当前源
                    name: '搜索: ' + content.wd,
                    tid: content.wd,
                    flag: '1',
                    msg: '源内搜索'
                }
            });
        }
        return `没有动作:${action}的可执行逻辑`
    },
    推荐: async function () {
        let {publicUrl} = this;
        let searchIcon = urljoin(publicUrl, './images/icon_cookie/搜索.jpg');
        let selectData = starAuthors.split(',').map(it => `${it}:=${it}`).join(',');
        return [{
            vod_id: 'only_search',
            vod_name: '这是个纯搜索源哦',
            vod_pic: searchIcon,
            vod_remarks: `歌手数量:${authors.length}`,
            vod_tag: 'action'
        },
            {
                vod_id: JSON.stringify({
                    actionId: '源内搜索',
                    id: 'wd',
                    type: 'input',
                    title: '源内搜索',
                    tip: '请输入搜索内容',
                    value: '',
                    selectData: selectData
                }),
                vod_name: '源内搜索',
                vod_pic: searchIcon,
                vod_tag: 'action',
            }
        ]
    },
    一级: async function (tid, pg, filter, extend) {
        let {MY_FL} = this;
        let d = [];
        if (tid === 'author') {
            let _f = rule.limit * (pg - 1);
            let _t = rule.limit * pg;
            let _d = [];
            let _authors = authors;
            // log('_f:', _f, '_t:', _t);
            // log('MY_FL.letters:', MY_FL.letters);
            if (MY_FL.letters) {
                _authors = authors.filter(_author => getFirstLetter(_author).startsWith(MY_FL.letters));
            }
            _d = _authors.slice(_f, _t);
            _d.forEach(it => {
                d.push({
                    vod_name: it,
                    vod_id: 'author#' + it,
                });
            });
            return d;
        }
        // 仅搜索作者允许翻页，其他情况只有3个固定按钮
        if (Number(pg) > 1) {
            return []
        }
        d.push({
            vod_name: '按歌手搜索',
            vod_id: 'author#' + tid,
            vod_remarks: '',
        });
        d.push({
            vod_name: '按歌名搜索',
            vod_id: 'name#' + tid,
            vod_remarks: '',
        });
        d.push({
            vod_name: '全名模糊搜索',
            vod_id: 'all#' + tid,
            vod_remarks: '',
        });
        return d
    },
    二级: async function () {
        let {orId} = this;
        let _stype = orId.split('#')[0];
        let _sname = orId.split('#')[1];
        let _vname = '';
        let data = [];
        switch (_stype) {
            case 'author':
                // log('_sname:', _sname);
                _vname = '按歌手搜索';
                data = mv_list.filter(it => it.author.includes(_sname));
                break;
            case 'name':
                _vname = '按歌名搜索';
                data = mv_list.filter(it => it.name.includes(_sname));
                break;
            default:
                _vname = '全名模糊搜索';
                data = mv_list.filter(it => it.title.includes(_sname));
                break;
        }
        return {
            vod_id: orId,
            vod_name: `${_vname}:${_sname}`,
            vod_remarks: `共计${data.length}`,
            vod_play_from: '道长源内搜索',
            vod_play_url: data.map(it => it.title + '$' + it.url).join('#')
        }
    },
    搜索: async function (wd, quick, pg) {
        if (Number(pg) > 1) {
            return []
        }
        let d = [];
        d.push({
            vod_name: '按歌手搜索:' + wd,
            vod_id: 'author#' + wd,
            vod_remarks: '',
        });
        d.push({
            vod_name: '按歌名搜索:' + wd,
            vod_id: 'name#' + wd,
            vod_remarks: '',
        });
        d.push({
            vod_name: '全名模糊搜索:' + wd,
            vod_id: 'all#' + wd,
            vod_remarks: '',
        });
        return d
    }
}
