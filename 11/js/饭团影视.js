var rule = {
    title:'饭团影视',
    模板:'vfed',
    host:'https://fantuansjz.com',
    homeUrl:'/',
    url: '/sjvodtype/fyclass/page/fypage.html',
    searchUrl: '/sjvodsearch/**------------fypage---.html',
    searchable: 2,
    quickSearch: 0,
    filterable: 0,
    headers: {
        'User-Agent': 'UC_UA'
    },
    class_parse: '.fed-pops-navbar&&ul.fed-pops-list&&li;a&&Text;a&&href;.*/(.*?).html',
    play_parse: true,
    lazy: `js:
  let html = request(input);
  let hconf = html.match(/r player_.*?=(.*?)</)[1];
  let json = JSON5.parse(hconf);
  let url = json.url;
  if (json.encrypt == '1') {
    url = unescape(url);
  } else if (json.encrypt == '2') {
    url = unescape(base64Decode(url));
  }
  if (/\.(m3u8|mp4|m4a|mp3)/.test(url)) {
    input = {
      parse: 0,
      jx: 0,
      url: url,
    };
  } else {
    input;
  }`,
    limit: 6,
    double: true,
    推荐: 'ul.fed-list-info.fed-part-rows;li;a.fed-list-title&&Text;a.fed-list-pics&&data-original;.fed-list-remarks&&Text;a&&href',
    一级: '.fed-list-info&&li;a.fed-list-title&&Text;a.fed-list-pics&&data-original;.fed-list-remarks&&Text;a&&href',
    二级: {
        title: 'h3.fed-part-eone&&Text;.fed-deta-content&&li:eq(2)&&a&&Text',
        img: '.fed-deta-images&&a.fed-list-pics&&data-original',
        desc: '.fed-deta-content&&li:eq(1)&&Text;.fed-deta-content&&li:eq(2)&&a&&Text;.fed-deta-content&&li:eq(3)&&a&&Text;.fed-deta-content&&li:eq(4)&&a&&Text;.fed-deta-content&&li:eq(5)&&a&&Text',
        content: '.fed-conv-text&&Text',
        tabs: '.fed-tabs-foot&&ul.fed-part-rows&&li',
        lists: '.fed-tabs-btm:eq(#id)&&li',
    },
    搜索: '.fed-list-info;h3.fed-part-eone&&Text;a.fed-list-pics&&data-original;.fed-list-remarks&&Text;a&&href;.fed-deta-content&&Text',
}
