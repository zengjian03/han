/**
 * 已知问题：
    * [推荐]页面：'雷电模拟器'播放部份影片会出错，'播放器'改成'ijk' & '解码方式'改成'软解'，即可正常播放
 * 影视TV 超連結跳轉支持
 * 影视TV 弹幕支持
    * https://t.me/fongmi_offical/
    * https://github.com/FongMi/Release/tree/main/apk
 * 皮皮虾DMBox 弹幕支持
    * 设置 > 窗口预览 > 开启
    * https://t.me/pipixiawerun
    * vod_area:'bilidanmu'
 * Cookie设置
    * Cookie获取方法 https://ghproxy.net/https://raw.githubusercontent.com/UndCover/PyramidStore/main/list.md
 * Cookie设置方法1: DR-PY 后台管理界面
    * CMS后台管理 > 设置中心 > 环境变量 > {"bili_cookie":"XXXXXXX","vmid":"XXXXXX"} > 保存
 * Cookie设置方法2: 手动替换Cookie
    * 底下代码 headers的
    * "Cookie":"$bili_cookie"
    * 手动替换为
    * "Cookie":"将获取的Cookie黏贴在这"
 */

var rule = {
    title:'哔哩学习',
    host:'https://api.bilibili.com',
    // homeUrl:'/x/web-interface/search/type?search_type=video&keyword=小姐姐4K&page=1',
    homeUrl:'/x/web-interface/ranking/v2?rid=0&type=origin', // 排行 > 排行榜 > 原创
    url:'/x/web-interface/search/type?search_type=videofyfilter',
    class_name:'儿童&苏教版&人教版&沪教版&北师大版',
    class_url:'儿童&苏教版&人教版&沪教版&北师大版',
    filterable: 1,
    filter_url: '&keyword={{fl.tid}}&page=fypage&duration={{fl.duration}}&order={{fl.order}}',
    filter_def:{
        儿童:{tid:'儿童'},
        苏教版:{tid:'苏教版'},
        人教版:{tid:'人教版'},
        沪教版:{tid:'沪教版'},
        北师大版:{tid:'北师大版'}
 },
filters: {
"苏教版":[{"key":"order","name":"排序","value":[{"n":"综合排序","v":"0"},{"n":"最多点击","v":"click"},{"n":"最新发布","v":"pubdate"},{"n":"最多弹幕","v":"dm"},{"n":"最多收藏","v":"stow"}]},{"key":"tid","name":"年级科目","value":[{"n":"1年级语文","v":"苏教版1年级语文"},{"n":"1年级数学","v":"苏教版1年级数学"},{"n":"1年级英语","v":"苏教版1年级英语"},{"n":"2年级语文","v":"苏教版2年级语文"},{"n":"2年级数学","v":"苏教版2年级数学"},{"n":"2年级英语","v":"苏教版2年级英语"},{"n":"3年级语文","v":"苏教版3年级语文"},{"n":"3年级数学","v":"苏教版3年级数学"},{"n":"3年级英语","v":"苏教版3年级英语"},{"n":"4年级语文","v":"苏教版4年级语文"},{"n":"4年级数学","v":"苏教版4年级数学"},{"n":"4年级英语","v":"苏教版4年级英语"},{"n":"5年级语文","v":"苏教版5年级语文"},{"n":"5年级数学","v":"苏教版5年级数学"},{"n":"5年级英语","v":"苏教版5年级英语"},{"n":"6年级语文","v":"苏教版6年级语文"},{"n":"6年级数学","v":"苏教版6年级数学"},{"n":"6年级英语","v":"苏教版6年级英语"},{"n":"7年级语文","v":"苏教版7年级语文"},{"n":"7年级数学","v":"苏教版7年级数学"},{"n":"7年级英语","v":"苏教版7年级英语"},{"n":"7年级历史","v":"苏教版7年级历史"},{"n":"7年级地理","v":"苏教版7年级地理"},{"n":"7年级生物","v":"苏教版7年级生物"},{"n":"7年级物理","v":"苏教版7年级物理"},{"n":"7年级化学","v":"苏教版7年级化学"},{"n":"8年级语文","v":"苏教版8年级语文"},{"n":"8年级数学","v":"苏教版8年级数学"},{"n":"8年级英语","v":"苏教版8年级英语"},{"n":"8年级历史","v":"苏教版8年级历史"},{"n":"8年级地理","v":"苏教版8年级地理"},{"n":"8年级生物","v":"苏教版8年级生物"},{"n":"8年级物理","v":"苏教版8年级物理"},{"n":"8年级化学","v":"苏教版8年级化学"},{"n":"9年级语文","v":"苏教版9年级语文"},{"n":"9年级数学","v":"苏教版9年级数学"},{"n":"9年级英语","v":"苏教版9年级英语"},{"n":"9年级历史","v":"苏教版9年级历史"},{"n":"9年级地理","v":"苏教版9年级地理"},{"n":"9年级生物","v":"苏教版9年级生物"},{"n":"9年级物理","v":"苏教版9年级物理"},{"n":"9年级化学","v":"苏教版9年级化学"},{"n":"高一语文","v":"苏教版高一语文"},{"n":"高一数学","v":"苏教版高一数学"},{"n":"高一英语","v":"苏教版高一英语"},{"n":"高一思想政治","v":"苏教版高一思想政治"},{"n":"高一历史","v":"苏教版高一历史"},{"n":"高一地理","v":"苏教版高一地理"},{"n":"高一生物","v":"苏教版高一生物"},{"n":"高一物理","v":"苏教版高一物理"},{"n":"高一化学","v":"苏教版高一化学"},{"n":"高二语文","v":"苏教版高二语文"},{"n":"高二数学","v":"苏教版高二数学"},{"n":"高二英语","v":"苏教版高二英语"},{"n":"高二思想政治","v":"苏教版高二思想政治"},{"n":"高二历史","v":"苏教版高二历史"},{"n":"高二地理","v":"苏教版高二地理"},{"n":"高二生物","v":"苏教版高二生物"},{"n":"高二物理","v":"苏教版高二物理"},{"n":"高二化学","v":"苏教版高二化学"},{"n":"高三语文","v":"苏教版高三语文"},{"n":"高三数学","v":"苏教版高三数学"},{"n":"高三英语","v":"苏教版高三英语"},{"n":"高三思想政治","v":"苏教版高三思想政治"},{"n":"高三历史","v":"苏教版高三历史"},{"n":"高三地理","v":"苏教版高三地理"},{"n":"高三生物","v":"苏教版高三生物"},{"n":"高三物理","v":"苏教版高三物理"},{"n":"高三化学","v":"苏教版高三化学"}]},{"key":"duration","name":"时长","value":[{"n":"全部","v":"0"},{"n":"60分钟以上","v":"4"},{"n":"30~60分钟","v":"3"},{"n":"10~30分钟","v":"2"},{"n":"10分钟以下","v":"1"}]}],
"人教版":[{"key":"order","name":"排序","value":[{"n":"综合排序","v":"0"},{"n":"最多点击","v":"click"},{"n":"最新发布","v":"pubdate"},{"n":"最多弹幕","v":"dm"},{"n":"最多收藏","v":"stow"}]},{"key":"tid","name":"年级科目","value":[{"n":"1年级语文","v":"人教版1年级语文"},{"n":"1年级数学","v":"人教版1年级数学"},{"n":"1年级英语","v":"人教版1年级英语"},{"n":"2年级语文","v":"人教版2年级语文"},{"n":"2年级数学","v":"人教版2年级数学"},{"n":"2年级英语","v":"人教版2年级英语"},{"n":"3年级语文","v":"人教版3年级语文"},{"n":"3年级数学","v":"人教版3年级数学"},{"n":"3年级英语","v":"人教版3年级英语"},{"n":"4年级语文","v":"人教版4年级语文"},{"n":"4年级数学","v":"人教版4年级数学"},{"n":"4年级英语","v":"人教版4年级英语"},{"n":"5年级语文","v":"人教版5年级语文"},{"n":"5年级数学","v":"人教版5年级数学"},{"n":"5年级英语","v":"人教版5年级英语"},{"n":"6年级语文","v":"人教版6年级语文"},{"n":"6年级数学","v":"人教版6年级数学"},{"n":"6年级英语","v":"人教版6年级英语"},{"n":"7年级语文","v":"人教版7年级语文"},{"n":"7年级数学","v":"人教版7年级数学"},{"n":"7年级英语","v":"人教版7年级英语"},{"n":"7年级历史","v":"人教版7年级历史"},{"n":"7年级地理","v":"人教版7年级地理"},{"n":"7年级生物","v":"人教版7年级生物"},{"n":"7年级物理","v":"人教版7年级物理"},{"n":"7年级化学","v":"人教版7年级化学"},{"n":"8年级语文","v":"人教版8年级语文"},{"n":"8年级数学","v":"人教版8年级数学"},{"n":"8年级英语","v":"人教版8年级英语"},{"n":"8年级历史","v":"人教版8年级历史"},{"n":"8年级地理","v":"人教版8年级地理"},{"n":"8年级生物","v":"人教版8年级生物"},{"n":"8年级物理","v":"人教版8年级物理"},{"n":"8年级化学","v":"人教版8年级化学"},{"n":"9年级语文","v":"人教版9年级语文"},{"n":"9年级数学","v":"人教版9年级数学"},{"n":"9年级英语","v":"人教版9年级英语"},{"n":"9年级历史","v":"人教版9年级历史"},{"n":"9年级地理","v":"人教版9年级地理"},{"n":"9年级生物","v":"人教版9年级生物"},{"n":"9年级物理","v":"人教版9年级物理"},{"n":"9年级化学","v":"人教版9年级化学"},{"n":"高一语文","v":"人教版高一语文"},{"n":"高一数学","v":"人教版高一数学"},{"n":"高一英语","v":"人教版高一英语"},{"n":"高一思想政治","v":"人教版高一思想政治"},{"n":"高一历史","v":"人教版高一历史"},{"n":"高一地理","v":"人教版高一地理"},{"n":"高一生物","v":"人教版高一生物"},{"n":"高一物理","v":"人教版高一物理"},{"n":"高一化学","v":"人教版高一化学"},{"n":"高二语文","v":"人教版高二语文"},{"n":"高二数学","v":"人教版高二数学"},{"n":"高二英语","v":"人教版高二英语"},{"n":"高二思想政治","v":"人教版高二思想政治"},{"n":"高二历史","v":"人教版高二历史"},{"n":"高二地理","v":"人教版高二地理"},{"n":"高二生物","v":"人教版高二生物"},{"n":"高二物理","v":"人教版高二物理"},{"n":"高二化学","v":"人教版高二化学"},{"n":"高三语文","v":"人教版高三语文"},{"n":"高三数学","v":"人教版高三数学"},{"n":"高三英语","v":"人教版高三英语"},{"n":"高三思想政治","v":"人教版高三思想政治"},{"n":"高三历史","v":"人教版高三历史"},{"n":"高三地理","v":"人教版高三地理"},{"n":"高三生物","v":"人教版高三生物"},{"n":"高三物理","v":"人教版高三物理"},{"n":"高三化学","v":"人教版高三化学"}]},{"key":"duration","name":"时长","value":[{"n":"全部","v":"0"},{"n":"60分钟以上","v":"4"},{"n":"30~60分钟","v":"3"},{"n":"10~30分钟","v":"2"},{"n":"10分钟以下","v":"1"}]}],
"沪教版":[{"key":"order","name":"排序","value":[{"n":"综合排序","v":"0"},{"n":"最多点击","v":"click"},{"n":"最新发布","v":"pubdate"},{"n":"最多弹幕","v":"dm"},{"n":"最多收藏","v":"stow"}]},{"key":"tid","name":"年级科目","value":[{"n":"1年级语文","v":"沪教版1年级语文"},{"n":"1年级数学","v":"沪教版1年级数学"},{"n":"1年级英语","v":"沪教版1年级英语"},{"n":"2年级语文","v":"沪教版2年级语文"},{"n":"2年级数学","v":"沪教版2年级数学"},{"n":"2年级英语","v":"沪教版2年级英语"},{"n":"3年级语文","v":"沪教版3年级语文"},{"n":"3年级数学","v":"沪教版3年级数学"},{"n":"3年级英语","v":"沪教版3年级英语"},{"n":"4年级语文","v":"沪教版4年级语文"},{"n":"4年级数学","v":"沪教版4年级数学"},{"n":"4年级英语","v":"沪教版4年级英语"},{"n":"5年级语文","v":"沪教版5年级语文"},{"n":"5年级数学","v":"沪教版5年级数学"},{"n":"5年级英语","v":"沪教版5年级英语"},{"n":"6年级语文","v":"沪教版6年级语文"},{"n":"6年级数学","v":"沪教版6年级数学"},{"n":"6年级英语","v":"沪教版6年级英语"},{"n":"7年级语文","v":"沪教版7年级语文"},{"n":"7年级数学","v":"沪教版7年级数学"},{"n":"7年级英语","v":"沪教版7年级英语"},{"n":"7年级历史","v":"沪教版7年级历史"},{"n":"7年级地理","v":"沪教版7年级地理"},{"n":"7年级生物","v":"沪教版7年级生物"},{"n":"7年级物理","v":"沪教版7年级物理"},{"n":"7年级化学","v":"沪教版7年级化学"},{"n":"8年级语文","v":"沪教版8年级语文"},{"n":"8年级数学","v":"沪教版8年级数学"},{"n":"8年级英语","v":"沪教版8年级英语"},{"n":"8年级历史","v":"沪教版8年级历史"},{"n":"8年级地理","v":"沪教版8年级地理"},{"n":"8年级生物","v":"沪教版8年级生物"},{"n":"8年级物理","v":"沪教版8年级物理"},{"n":"8年级化学","v":"沪教版8年级化学"},{"n":"9年级语文","v":"沪教版9年级语文"},{"n":"9年级数学","v":"沪教版9年级数学"},{"n":"9年级英语","v":"沪教版9年级英语"},{"n":"9年级历史","v":"沪教版9年级历史"},{"n":"9年级地理","v":"沪教版9年级地理"},{"n":"9年级生物","v":"沪教版9年级生物"},{"n":"9年级物理","v":"沪教版9年级物理"},{"n":"9年级化学","v":"沪教版9年级化学"},{"n":"高一语文","v":"沪教版高一语文"},{"n":"高一数学","v":"沪教版高一数学"},{"n":"高一英语","v":"沪教版高一英语"},{"n":"高一思想政治","v":"沪教版高一思想政治"},{"n":"高一历史","v":"沪教版高一历史"},{"n":"高一地理","v":"沪教版高一地理"},{"n":"高一生物","v":"沪教版高一生物"},{"n":"高一物理","v":"沪教版高一物理"},{"n":"高一化学","v":"沪教版高一化学"},{"n":"高二语文","v":"沪教版高二语文"},{"n":"高二数学","v":"沪教版高二数学"},{"n":"高二英语","v":"沪教版高二英语"},{"n":"高二思想政治","v":"沪教版高二思想政治"},{"n":"高二历史","v":"沪教版高二历史"},{"n":"高二地理","v":"沪教版高二地理"},{"n":"高二生物","v":"沪教版高二生物"},{"n":"高二物理","v":"沪教版高二物理"},{"n":"高二化学","v":"沪教版高二化学"},{"n":"高三语文","v":"沪教版高三语文"},{"n":"高三数学","v":"沪教版高三数学"},{"n":"高三英语","v":"沪教版高三英语"},{"n":"高三思想政治","v":"沪教版高三思想政治"},{"n":"高三历史","v":"沪教版高三历史"},{"n":"高三地理","v":"沪教版高三地理"},{"n":"高三生物","v":"沪教版高三生物"},{"n":"高三物理","v":"沪教版高三物理"},{"n":"高三化学","v":"沪教版高三化学"}]},{"key":"duration","name":"时长","value":[{"n":"全部","v":"0"},{"n":"60分钟以上","v":"4"},{"n":"30~60分钟","v":"3"},{"n":"10~30分钟","v":"2"},{"n":"10分钟以下","v":"1"}]}],
"北师大版":[{"key":"order","name":"排序","value":[{"n":"综合排序","v":"0"},{"n":"最多点击","v":"click"},{"n":"最新发布","v":"pubdate"},{"n":"最多弹幕","v":"dm"},{"n":"最多收藏","v":"stow"}]},{"key":"tid","name":"年级科目","value":[{"n":"1年级语文","v":"北师大版1年级语文"},{"n":"1年级数学","v":"北师大版1年级数学"},{"n":"1年级英语","v":"北师大版1年级英语"},{"n":"2年级语文","v":"北师大版2年级语文"},{"n":"2年级数学","v":"北师大版2年级数学"},{"n":"2年级英语","v":"北师大版2年级英语"},{"n":"3年级语文","v":"北师大版3年级语文"},{"n":"3年级数学","v":"北师大版3年级数学"},{"n":"3年级英语","v":"北师大版3年级英语"},{"n":"4年级语文","v":"北师大版4年级语文"},{"n":"4年级数学","v":"北师大版4年级数学"},{"n":"4年级英语","v":"北师大版4年级英语"},{"n":"5年级语文","v":"北师大版5年级语文"},{"n":"5年级数学","v":"北师大版5年级数学"},{"n":"5年级英语","v":"北师大版5年级英语"},{"n":"6年级语文","v":"北师大版6年级语文"},{"n":"6年级数学","v":"北师大版6年级数学"},{"n":"6年级英语","v":"北师大版6年级英语"},{"n":"7年级语文","v":"北师大版7年级语文"},{"n":"7年级数学","v":"北师大版7年级数学"},{"n":"7年级英语","v":"北师大版7年级英语"},{"n":"7年级历史","v":"北师大版7年级历史"},{"n":"7年级地理","v":"北师大版7年级地理"},{"n":"7年级生物","v":"北师大版7年级生物"},{"n":"7年级物理","v":"北师大版7年级物理"},{"n":"7年级化学","v":"北师大版7年级化学"},{"n":"8年级语文","v":"北师大版8年级语文"},{"n":"8年级数学","v":"北师大版8年级数学"},{"n":"8年级英语","v":"北师大版8年级英语"},{"n":"8年级历史","v":"北师大版8年级历史"},{"n":"8年级地理","v":"北师大版8年级地理"},{"n":"8年级生物","v":"北师大版8年级生物"},{"n":"8年级物理","v":"北师大版8年级物理"},{"n":"8年级化学","v":"北师大版8年级化学"},{"n":"9年级语文","v":"北师大版9年级语文"},{"n":"9年级数学","v":"北师大版9年级数学"},{"n":"9年级英语","v":"北师大版9年级英语"},{"n":"9年级历史","v":"北师大版9年级历史"},{"n":"9年级地理","v":"北师大版9年级地理"},{"n":"9年级生物","v":"北师大版9年级生物"},{"n":"9年级物理","v":"北师大版9年级物理"},{"n":"9年级化学","v":"北师大版9年级化学"},{"n":"高一语文","v":"北师大版高一语文"},{"n":"高一数学","v":"北师大版高一数学"},{"n":"高一英语","v":"北师大版高一英语"},{"n":"高一思想政治","v":"北师大版高一思想政治"},{"n":"高一历史","v":"北师大版高一历史"},{"n":"高一地理","v":"北师大版高一地理"},{"n":"高一生物","v":"北师大版高一生物"},{"n":"高一物理","v":"北师大版高一物理"},{"n":"高一化学","v":"北师大版高一化学"},{"n":"高二语文","v":"北师大版高二语文"},{"n":"高二数学","v":"北师大版高二数学"},{"n":"高二英语","v":"北师大版高二英语"},{"n":"高二思想政治","v":"北师大版高二思想政治"},{"n":"高二历史","v":"北师大版高二历史"},{"n":"高二地理","v":"北师大版高二地理"},{"n":"高二生物","v":"北师大版高二生物"},{"n":"高二物理","v":"北师大版高二物理"},{"n":"高二化学","v":"北师大版高二化学"},{"n":"高三语文","v":"北师大版高三语文"},{"n":"高三数学","v":"北师大版高三数学"},{"n":"高三英语","v":"北师大版高三英语"},{"n":"高三思想政治","v":"北师大版高三思想政治"},{"n":"高三历史","v":"北师大版高三历史"},{"n":"高三地理","v":"北师大版高三地理"},{"n":"高三生物","v":"北师大版高三生物"},{"n":"高三物理","v":"北师大版高三物理"},{"n":"高三化学","v":"北师大版高三化学"}]},{"key":"duration","name":"时长","value":[{"n":"全部","v":"0"},{"n":"60分钟以上","v":"4"},{"n":"30~60分钟","v":"3"},{"n":"10~30分钟","v":"2"},{"n":"10分钟以下","v":"1"}]}],
//"儿童":[{"key":"order","name":"排序","value":[{"n":"综合排序","v":"0"},{"n":"最多点击","v":"click"},{"n":"最新发布","v":"pubdate"},{"n":"最多弹幕","v":"dm"},{"n":"最多收藏","v":"stow"}]},{"key":"tid","name":"分类","value":[{"n":"全部","v":"儿童"},{"n":"游戏","v":"儿童游戏"},{"n":"启蒙","v":"儿童启蒙"},{"n":"益智","v":"儿童益智"},{"n":"科普","v":"儿童科普"},{"n":"健身","v":"儿童健身"},{"n":"歌曲","v":"儿童歌曲"},{"n":"舞蹈","v":"儿童舞蹈"},{"n":"动画","v":"儿童动画"},{"n":"绘画","v":"儿童绘画"},{"n":"成语故事","v":"儿童成语故事"},{"n":"安全教育","v":"儿童安全教育"},{"n":"睡前故事","v":"儿童睡前故事"},{"n":"贝乐虎","v":"贝乐虎"},{"n":"兔小贝","v":"兔小贝"},{"n":"宝宝巴士","v":"宝宝巴士"},{"n":"贝瓦儿歌","v":"贝瓦儿歌"},{"n":"悟空识字","v":"悟空识字"},{"n":"儿童好声音","v":"儿童好声音"}]},{"key":"duration","name":"时长","value":[{"n":"全部","v":"0"},{"n":"60分钟以上","v":"4"},{"n":"30~60分钟","v":"3"},{"n":"10~30分钟","v":"2"},{"n":"10分钟以下","v":"1"}]}]},
    // detailUrl:'/x/web-interface/view?aid=fyid',//二级详情拼接链接(json格式用)
    "儿童":[{"key":"order","name":"排序","value":[{"n":"综合排序","v":"0"},{"n":"最多点击","v":"click"},{"n":"最新发布","v":"pubdate"},{"n":"最多弹幕","v":"dm"},{"n":"最多收藏","v":"stow"}]},{"key":"tid","name":"分类","value":[{"n":"全部","v":"儿童"},{"n":"教育","v":"儿童早教"},{"n":"歌曲","v":"贝瓦儿歌"},{"n":"舞蹈","v":"儿童舞蹈"},{"n":"成语故事","v":"儿童成语故事"},{"n":"安全教育","v":"儿童安全教育"},{"n":"睡前故事","v":"儿童睡前故事"},{"n":"贝乐虎","v":"贝乐虎"},{"n":"宝宝巴士","v":"宝宝巴士"},{"n":"儿童好声音","v":"儿童好声音"}]},{"key":"duration","name":"时长","value":[{"n":"全部","v":"0"},{"n":"60分钟以上","v":"4"},{"n":"30~60分钟","v":"3"},{"n":"10~30分钟","v":"2"},{"n":"10分钟以下","v":"1"}]}],
},
    detailUrl:'/x/web-interface/view/detail?aid=fyid',//二级详情拼接链接(json格式用)
    searchUrl:'/x/web-interface/search/type?search_type=video&keyword=**&page=fypage',
    searchable:2,
    quickSearch:0,
    headers:{
        "User-Agent":"PC_UA",
        "Referer": "https://www.bilibili.com",
        // "Cookie":"$bili_cookie"
        // "Cookie":"https://ghproxy.net/https://github.com/FongMi/CatVodSpider/raw/main/txt/cookie.txt"
        "Cookie":"http://127.0.0.1:9978/file/TV/bili_cookie.txt"
    },
    timeout:5000,
    limit:8,
    play_parse:true,
    lazy:`js:
        let ids = input.split('_');
        let dan = 'https://api.bilibili.com/x/v1/dm/list.so?oid=' + ids[1];
        let result = {};
        let iurl = 'https://api.bilibili.com:443/x/player/playurl?avid=' + ids[0] + '&cid=' + ids[1] + '&qn=116';
        let html = request(iurl);
        let jRoot = JSON.parse(html);
        let jo = jRoot.data;
        let ja = jo.durl;
        let maxSize = -1;
        let position = -1;
        ja.forEach(function(tmpJo, i) {
            if (maxSize < Number(tmpJo.size)) {
                maxSize = Number(tmpJo.size);
                position = i
            }
        });
        let purl = '';
        if (ja.length > 0) {
            if (position === -1) {
                position = 0
            }
            purl = ja[position].url
        }
        result.parse = 0;
        result.playUrl = '';
        result.url = unescape(purl);
        result.header = {
            'Referer': 'https://live.bilibili.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
        };
        if (/\\.flv/.test(purl)) {
            result.contentType = 'video/x-flv';
        } else {
            result.contentType = '';
        }
        result.danmaku = dan;
        input = result
    `,
    double:false,
    // 推荐:'*',
    推荐:`js:
        function stripHtmlTag(src) {
            return src.replace(/<\\/?[^>]+(>|$)/g, '').replace(/&.{1,5};/g, '').replace(/\\s{2,}/g, ' ');
        }
        function turnDHM(duration) {
            let min = '';
            let sec = '';
            try {
                min = duration.split(':')[0];
                sec = duration.split(':')[1];
            } catch (e) {
                min = Math.floor(duration / 60);
                sec = duration % 60;
            }
            if (isNaN(parseInt(duration))) {
                return '无效输入';
            }
            if (min == 0) {
                return sec + '秒'
            } else if (0 < min && min < 60) {
                return min + '分'
            } else if (60 <= min && min < 1440) {
                if (min % 60 == 0) {
                    let h = min / 60;
                    return h + '小时'
                } else {
                    let h = min / 60;
                    h = (h + '').split('.')[0];
                    let m = min % 60;
                    return h + '小时' + m + '分';
                }
            } else if (min >= 1440) {
                let d = min / 60 / 24;
                d = (d + '').split('.')[0];
                let h = min / 60 % 24;
                h = (h + '').split('.')[0];
                let m = min % 60;
                let dhm = '';
                if (d > 0) {
                    dhm = d + '天'
                }
                if (h >= 1) {
                    dhm = dhm + h + '小时'
                }
                if (m > 0) {
                    dhm = dhm + m + '分'
                }
                return dhm
            }
            return null
        }
        function ConvertNum(num) {
            let _ws = Math.pow(10, 1);
            let _b = 1e4;
            if (num < _b) {
                return num.toString();
            }
            let _r = '';
            let _strArg = ['', '万', '亿', '万亿'];
            let _i = Math.floor(Math.log(num) / Math.log(_b));
            if (_i > 3) {
                _i = 3;
            }
            _r = Math.floor(num / Math.pow(_b, _i) * _ws) / _ws + _strArg[_i];
            return _r;
        }
        let html = request(input);
        let vodList = JSON.parse(html).data.list;
        let videos = [];
        vodList.forEach(function(vod) {
            let aid = vod.aid;
            let title = stripHtmlTag(vod.title);
            let img = vod.pic;
            if (img.startsWith('//')) {
                img = 'https:' + img;
            }
            let remark = turnDHM(vod.duration) + ' ▶' + ConvertNum(vod.stat.view) + ' 🆙' + vod.owner.name;
            videos.push({
                vod_id: aid,
                vod_name: title,
                vod_pic: img,
                vod_remarks: remark
            })
        });
        VODS = videos
    `,
    // 一级:'js:let html=request(input);let msg=JSON.parse(html).message;function title_rep(title){if(/keyword/.test(title)){title=title.replace(\'<em class="keyword">\',"").replace("</em>","").replace("&quot;","\'");log("名称替换👉"+title)};return title}if(msg!=="0"){VODS=[{vod_name:KEY+"➢"+msg,vod_id:"no_data",vod_remarks:"别点,缺少bili_cookie",vod_pic:"https://ghproxy.net/https://raw.githubusercontent.com/hjdhnx/dr_py/main/404.jpg"}]}else{let videos=[];let vodList=JSON.parse(html).data.result;vodList.forEach(function(vod){let aid=vod["aid"];let title=vod["title"].trim();title=title_rep(title);title=title_rep(title);title=title_rep(title);title=title_rep(title);let img="https:"+vod["pic"];let remark=vod["duration"];videos.push({vod_id:aid,vod_name:title,vod_pic:img,vod_remarks:remark})});VODS=videos}',
    一级:`js:
        if (cateObj.tid.endsWith('_clicklink')) {
            cateObj.tid = cateObj.tid.split('_')[0];
            input = HOST + '/x/web-interface/search/type?search_type=video&keyword=' + cateObj.tid + '&page=' + MY_PAGE;
        }
        function stripHtmlTag(src) {
            return src.replace(/<\\/?[^>]+(>|$)/g, '').replace(/&.{1,5};/g, '').replace(/\\s{2,}/g, ' ');
        }
        function turnDHM(duration) {
            let min = '';
            let sec = '';
            try {
                min = duration.split(':')[0];
                sec = duration.split(':')[1];
            } catch (e) {
                min = Math.floor(duration / 60);
                sec = duration % 60;
            }
            if (isNaN(parseInt(duration))) {
                return '无效输入';
            }
            if (min == 0) {
                return sec + '秒'
            } else if (0 < min && min < 60) {
                return min + '分'
            } else if (60 <= min && min < 1440) {
                if (min % 60 == 0) {
                    let h = min / 60;
                    return h + '小时'
                } else {
                    let h = min / 60;
                    h = (h + '').split('.')[0];
                    let m = min % 60;
                    return h + '小时' + m + '分';
                }
            } else if (min >= 1440) {
                let d = min / 60 / 24;
                d = (d + '').split('.')[0];
                let h = min / 60 % 24;
                h = (h + '').split('.')[0];
                let m = min % 60;
                let dhm = '';
                if (d > 0) {
                    dhm = d + '天'
                }
                if (h >= 1) {
                    dhm = dhm + h + '小时'
                }
                if (m > 0) {
                    dhm = dhm + m + '分'
                }
                return dhm
            }
            return null
        }
        function ConvertNum(num) {
            let _ws = Math.pow(10, 1);
            let _b = 1e4;
            if (num < _b) {
                return num.toString();
            }
            let _r = '';
            let _strArg = ['', '万', '亿', '万亿'];
            let _i = Math.floor(Math.log(num) / Math.log(_b));
            if (_i > 3) {
                _i = 3;
            }
            _r = Math.floor(num / Math.pow(_b, _i) * _ws) / _ws + _strArg[_i];
            return _r;
        }
        let data = [];
        let vodList = [];
        if (MY_CATE === '推荐') {
            input = HOST + '/x/web-interface/index/top/rcmd?ps=14&fresh_idx=' + MY_PAGE + '&fresh_idx_1h=' + MY_PAGE;
            data = JSON.parse(request(input)).data;
            vodList = data.item;
        } else if (MY_CATE === '历史记录') {
            input = HOST + '/x/v2/history?pn=' + MY_PAGE;
            data = JSON.parse(request(input)).data;
            vodList = data;
        } else {
            data = JSON.parse(request(input)).data;
            vodList = data.result;
        }
        let videos = [];
        vodList.forEach(function(vod) {
            let aid = vod.aid?vod.aid:vod.id;
            let title = stripHtmlTag(vod.title);
            let img = vod.pic;
            if (img.startsWith('//')) {
                img = 'https:' + img;
            }
            let play = '';
            let danmaku = '';
            if (MY_CATE === '推荐') {
                play = ConvertNum(vod.stat.view);
                danmaku = vod.stat.danmaku;
            } else if (MY_CATE === '历史记录') {
                play = ConvertNum(vod.stat.view);
                danmaku = vod.stat.danmaku;
            } else {
                play = ConvertNum(vod.play);
                danmaku = vod.video_review;
            }
            let remark = turnDHM(vod.duration) + ' ▶' + play + ' 💬' + danmaku;
            videos.push({
                vod_id: aid,
                vod_name: title,
                vod_pic: img,
                vod_remarks: remark
            })
        });
        VODS = videos
    `,
    二级:`js:
        function stripHtmlTag(src) {
            return src.replace(/<\\/?[^>]+(>|$)/g, '').replace(/&.{1,5};/g, '').replace(/\\s{2,}/g, ' ');
        }
        let html = request(input);
        let jo = JSON.parse(html).data.View;
        // 历史记录
        let cookies = rule_fetch_params.headers.Cookie.split(';');
        let bili_jct = '';
        cookies.forEach(cookie => {
            if (cookie.includes('bili_jct')) {
                bili_jct = cookie.split('=')[1];
            }
        });
        if (bili_jct !== '') {
            let historyReport = 'https://api.bilibili.com/x/v2/history/report';
            let dataPost = {
                aid: jo.aid,
                cid: jo.cid,
                csrf: bili_jct,
            };
            post(historyReport, dataPost, 'form');
        }

        let stat = jo.stat;
        let up_info = JSON.parse(html).data.Card;
        let relation = up_info.following ? '已关注' : '未关注';
        let aid = jo.aid;
        let title = stripHtmlTag(jo.title);
        let pic = jo.pic;
        let desc = jo.desc;

        let date = new Date(jo.pubdate * 1000);
        let yy = date.getFullYear().toString();
        let mm = date.getMonth()+1;
        mm = mm < 10 ? ('0' + mm) : mm;
        let dd = date.getDate();
        dd = dd < 10 ? ('0' + dd) : dd;

        let up_name = jo.owner.name;
        let typeName = jo.tname;
        // let remark = jo.duration;
        let vod = {
            vod_id: aid,
            vod_name: title,
            vod_pic: pic,
            type_name: typeName,
            vod_year: yy+mm+dd,
            vod_area: 'bilidanmu',
            // vod_remarks: remark,
            vod_tags: 'mv',
            // vod_director: '🆙 ' + up_name + '　👥 ' + up_info.follower + '　' + relation,
            vod_director: '🆙 ' + '[a=cr:' + JSON.stringify({'id':up_name + '_clicklink','name':up_name}) + '/]' + up_name + '[/a]' + '　👥 ' + up_info.follower + '　' + relation,
            vod_actor: '▶' + stat.view + '　' + '💬' + stat.danmaku + '　' + '👍' + stat.like + '　' + '💰' + stat.coin + '　' + '⭐' + stat.favorite,
            vod_content: desc
        };
        let ja = jo.pages;
        let treeMap = {};
        let playurls = [];
        ja.forEach(function(tmpJo) {
            let cid = tmpJo.cid;
            let part = tmpJo.part.replaceAll('#', '﹟').replaceAll('$', '﹩');
            playurls.push(
                part + '$' + aid + '_' + cid
            )
        });
        treeMap['B站'] = playurls.join('#');
        let relatedData = JSON.parse(html).data.Related;
        playurls = [];
        relatedData.forEach(function(rd) {
            let ccid = rd.cid;
            let title = rd.title.replaceAll('#', '﹟').replaceAll('$', '﹩');
            let aaid = rd.aid;
            playurls.push(
                title + '$' + aaid + '_' + ccid
            )
        });
        treeMap['相关推荐'] = playurls.join('#');
        vod.vod_play_from = Object.keys(treeMap).join("$$$");
        vod.vod_play_url = Object.values(treeMap).join("$$$");
        VOD = vod;
    `,
    // 搜索:'*',
    搜索:`js:
        let html = request(input);
        function stripHtmlTag(src) {
            return src.replace(/<\\/?[^>]+(>|$)/g, '').replace(/&.{1,5};/g, '').replace(/\\s{2,}/g, ' ');
        }
        function turnDHM(duration) {
            let min = '';
            let sec = '';
            try {
                min = duration.split(':')[0];
                sec = duration.split(':')[1];
            } catch (e) {
                min = Math.floor(duration / 60);
                sec = duration % 60;
            }
            if (isNaN(parseInt(duration))) {
                return '无效输入';
            }
            if (min == 0) {
                return sec + '秒'
            } else if (0 < min && min < 60) {
                return min + '分'
            } else if (60 <= min && min < 1440) {
                if (min % 60 == 0) {
                    let h = min / 60;
                    return h + '小时'
                } else {
                    let h = min / 60;
                    h = (h + '').split('.')[0];
                    let m = min % 60;
                    return h + '小时' + m + '分';
                }
            } else if (min >= 1440) {
                let d = min / 60 / 24;
                d = (d + '').split('.')[0];
                let h = min / 60 % 24;
                h = (h + '').split('.')[0];
                let m = min % 60;
                let dhm = '';
                if (d > 0) {
                    dhm = d + '天'
                }
                if (h >= 1) {
                    dhm = dhm + h + '小时'
                }
                if (m > 0) {
                    dhm = dhm + m + '分'
                }
                return dhm
            }
            return null
        }
        let videos = [];
        let vodList = JSON.parse(html).data.result;
        vodList.forEach(function(vod) {
            let aid = vod.aid;
            let title = stripHtmlTag(vod.title);
            let img = vod.pic;
            if (img.startsWith('//')) {
                img = 'https:' + img;
            }
            let remark = turnDHM(vod.duration);
            videos.push({
                vod_id: aid,
                vod_name: title,
                vod_pic: img,
                vod_remarks: remark
            })
        });
        VODS = videos
    `,
    // 预处理:'if(rule_fetch_params.headers.Cookie.startsWith("http")){rule_fetch_params.headers.Cookie=fetch(rule_fetch_params.headers.Cookie);setItem(RULE_CK,cookie)};log(rule_fetch_params.headers.Cookie)',
}