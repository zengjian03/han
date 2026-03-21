var rule = {
  title: '听书阁',
  host: 'https://www.yilukan.com/',
  url: '/yilu/fyclass-fypage.html',
  searchUrl: '/search.php?page=fypage&searchword=**&searchtype=',
  searchable: 2,
  quickSearch: 0,
  filterable: 0,
  headers: {
    'User-Agent': 'UC_UA',
  },
  class_parse: '.stui-header__menu li:gt(0):lt(8);a&&Text;a&&href;.*/(.*?).html',
  play_parse: true,
  lazy: $js.toString(() => {
    var html = request(input);
    var regs = [
      /var\s+now\s*=\s*["'](.*?)["']/,
      /var\s+now_url\s*=\s*["'](.*?)["']/,
      /var\s+play_url\s*=\s*["'](.*?)["']/,
      /var\s+url\s*=\s*["'](.*?)["']/,
      /["'](https?:\/\/.*?\.(?:mp3|m4a|aac|wav|flac|m3u8))["']/i,
      /["'](\/\/.*?\.(?:mp3|m4a|aac|wav|flac|m3u8))["']/i
    ];
    var url = '';
    for (var i = 0; i < regs.length; i++) {
      var m = html.match(regs[i]);
      if (m && m[1]) {
        url = m[1];
        break;
      }
    }
    if (!url) return input;
    url = url.replace(/\\\//g, '/');
    if (url.startsWith('//')) url = 'https:' + url;
    if (!url.startsWith('http')) url = rule.host + url;
    return {
      parse: 0,
      url: url,
      header: {
        'User-Agent': 'UC_UA',
        'Referer': input
      }
    };
  }),
  limit: 6,
  double: true,
  推荐: 'ul.stui-vodlist.clearfix;li;a&&title;.lazyload&&data-original;.pull-right&&Text;a&&href',
  一级: '.stui-vodlist li;a&&title;a&&data-original;.pic-text&&Text;a&&href',
  二级: {
    title: '.stui-content__detail .title&&Text;.stui-content__detail p.data:eq(2)&&Text',
    title1: '.stui-content__detail .title&&Text;.stui-content__detail&&p&&Text',
    img: '.stui-content__thumb .lazyload&&data-original',
    desc: '.stui-content__detail p&&Text;.stui-content__detail&&p:eq(1)&&a:eq(0)&&Text;.stui-content__detail&&p:eq(3)&&a:eq(0)&&Text;.stui-content__detail p:eq(6)&&Text;.stui-content__detail p:eq(5)&&Text',
    content: '.desc&&Text',
    tabs: '.stui-vodlist__head h4',
    lists: '.stui-content__playlist:eq(#id) li',
  },
  搜索: 'ul.stui-vodlist__media,ul.stui-vodlist,#searchList li;a&&title;.lazyload&&data-original;.pic-text&&Text;a&&href;.detail&&Text',
}