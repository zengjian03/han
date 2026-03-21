var rule = {
    author: 'Jack',
    title: '高清影院',
    类型: '影视',
    host: 'https://www.esuppy.com',
    headers: {
    'User-Agent': 'MOBILE_UA',
    'Referer': '',
     'Cookie': ''
       },
    编码: 'utf-8',
    timeout: 5000,
    homeUrl: '/',
    
    
   url: '/gqsw/fyfilter.html',
   // url: '/gqdt/fyclass-fypage.html',
    detailUrl: '/gqdt//fyid.html',    
 // searchUrl: 'http://www.zjqhdq.com/search/**/fypage.html',    
  
  filter_url: '{{fl.cateId or "fyclass"}}-{{fl.area}}-{{fl.by}}--{{fl.lang}}----fypage---{{fl.year}}',
 // https://www.esuppy.com/gqsw/17-韩国-hits--国语----2---2025.html
  searchUrl: '/gqsc/**----------fypage---.html',
  //   搜索: 'json:list;name;pic;en;id',  
//https://jin-bang.com.cn/vodsearch/%E7%88%B1%E6%83%85----------3---.html
    searchable: 1,
    quickSearch: 1,
    filterable: 1,
    limit: 10,
    double: false,
    class_name: '电影&电视剧&综艺&动漫&短剧&动作片&喜剧片&爱情片&科幻片&恐怖片&剧情片&战争片&纪录片&悬疑片&犯罪片&奇幻片&动画片&预告片&国产剧&港台剧',
    //静态分类值
    class_url: '1&2&3&4&5&6&7&8&9&10&11&12&13&14&15&16&31&32&17&18',
    推荐: '*',
    //推荐页的json模式
    //推荐: 'json:list;vod_name;vod_pic;vod_remarks;vod_id',
    一级: '.stui-vodlist li;a&&title;a&&data-original;.pic-text&&Text;a&&href',
    

  二级: $js.toString(() => {
    let html = request(input);
    VOD = {};
 VOD.vod_id = input;
 VOD.vod_name = pdfh(html, 'h1&&Text');
 VOD.type_name = pdfh(html, 'p:contains(类型)&&Text').replace('分类：','');
 VOD.vod_pic = pd(html, 'img&&data-original');
 VOD.vod_remarks = pdfh(html, 'p:contains(状态)&&Text');
 VOD.vod_year = pdfh(html, 'p:contains(年份)&&Text').replace('年份：','');
VOD.vod_area = pdfh(html, 'p:contains(地区)&&Text').replace('地区：','');
VOD.vod_director = pdfh(html, 'p:contains(导演)&&Text').replace('导演：','');
 VOD.vod_actor = pdfh(html, 'p:contains(演员)&&Text').replace('演员：','');
 VOD.vod_content = pdfh(html, 'p:contains(简介)&&Text').replace('简介：','');
    //线路
    let r_ktabs = pdfa(html, '.stui-vodlist__head h3');
    let ktabs = r_ktabs.map(it => pdfh(it, 'h3&&Text'));
    VOD.vod_play_from = ktabs.join('$$$');

    let klists = [];
    let r_plists = pdfa(html, '.stui-content__playlist');
    r_plists.forEach((rp) => {
        let klist = pdfa(rp, 'a').map((it) => {
            return pdfh(it, 'a&&Text') + '$' + pd(it, 'a&&href', input);
        });
        klist = klist.join('#');
        klists.push(klist);
    });
    VOD.vod_play_url = klists.join('$$$');
}),
     搜索: '*',
    //是否启用辅助嗅探: 1,0
    sniffer: 0,
    // 辅助嗅探规则
    isVideo: 'http((?!http).){26,}\\.(m3u8|mp4|flv|avi|mkv|wmv|mpg|mpeg|mov|ts|3gp|rm|rmvb|asf|m4a|mp3|wma)',

  play_parse: true,
    //播放地址通用解析
   lazy: $js.toString(() => {
let kcode = JSON.parse(fetch(input).split('aaaa=')[1].split('<')[0]);
let kurl = kcode.url;
if (/\.(m3u8|mp4)/.test(kurl)) {
    input = { jx: 0, parse: 0, url: kurl, header: {'User-Agent': MOBILE_UA, 'Referer': getHome(kurl)} }
} else {
    input = { jx: 0, parse: 1, url: input }
}
}),

}




    
