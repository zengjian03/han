var rule = {
    title: '哔嘀影视',
    host: 'https://www.bdtv.org',
    url: '/vodshow/fyclass--------fypage---.html',
    searchUrl: '/vodsearch/**----------fypage---.html',
    searchable: 1,
    quickSearch: 0,
    filterable: 1,
    headers: {
        'User-Agent': 'PC_UA',
    },
    class_parse: '.nav-menu-items&&li;a&&Text;a&&href;/(\\d+)\\.html',
    cate_exclude: '首页|排行榜',
    double: false,
    推荐: '.module-items .module-item;a&&title;img&&data-src||img&&src;.module-item-text&&Text;a&&href',
    一级: '.module-items .module-item;a&&title;img&&data-src||img&&src;.module-item-text&&Text;a&&href',
    二级: {
        title: 'h1&&Text;.tag-link:eq(-1)&&Text',
        img: '.pic&&img&&data-src||img&&src',
        desc: '.data:eq(0)&&Text;.data:eq(1)&&Text;.data:eq(2)&&Text;.data:eq(3)&&Text;.data:eq(4)&&Text',
        content: '.desc&&Text',
        tabs: '.module-tab-item',
        lists: '.module-play-list:eq(#id)&&a',
        tab_text: 'div--small&&Text',
    },
    搜索: '.module-items .module-item;a&&title;img&&data-src||img&&src;.module-item-text&&Text;a&&href',
    lazy: `js:
        var html = request(input);
        var conf = html.match(/r player_.*?=(.*?)</);
        if (conf) {
            var json = JSON5.parse(conf[1]);
            var url = json.url;
            if (json.encrypt == '1') url = unescape(url);
            if (json.encrypt == '2') url = unescape(base64Decode(url));
            if (/\\.(m3u8|mp4|m4a|mp3)/.test(url)) {
                input = {parse: 0, url: url};
            } else {
                input = {parse: 1, url: input};
            }
        } else {
            input = {parse: 1, url: input};
        }
    `,
}
