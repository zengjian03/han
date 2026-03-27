var rule = {
    title: '看球吧[优]',
    host: 'https://zhiboapi3003.zb6.fun',
    url: '/api/live/getRealLives?categoryid=fyclass',
    searchUrl: '/api/live/getRealLives',
    searchable: 2,
    quickSearch: 0,
    filterable: 0,
    headers: {
        'User-Agent': 'MOBILE_UA',
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json'
    },
    timeout: 5000,
    class_name: '全部&足球&篮球',
    class_url: '0&1&2', 
    play_parse: true,
    lazy: '',
    
    一级: $js.toString(() => {
        let items = [];
        let html = request(input);
        let json = JSON.parse(html);
        let list = json.data.list || [];

        list.forEach(it => {
            let hot = (it.hot / 1000).toFixed(1) + 'k';
            let extra = [it.pull_url, it.start_time, it.badge_text, it.anchor.nick_name, it.title, it.thumb].join('|');
            items.push({
                title: it.title,
                img: it.thumb || 'https://via.placeholder.com/300x400?text=No+Image',
                desc: '🔥' + hot + ' | ' + it.badge_text + ' | ' + it.anchor.nick_name,
                url: extra
            });
        });
        setResult(items);
    }),

    二级: $js.toString(() => {
        let info = input.split('|');
        VOD = {
            vod_name: info[4],
            vod_pic: info[5],
            vod_remarks: '赛事：' + info[2],
            vod_content: '【直播标题】：' + info[4] + '\n' +
                         '【赛事分类】：' + info[2] + '\n' +
                         '【主播昵称】：' + info[3] + '\n' +
                         '【开播时间】：' + info[1] + '\n' +
                         '【信号状态】：正在直播\n' +
                         '【友情提示】：直播信号源于网络，请勿轻信广告。',
            vod_play_from: '看球吧',
            vod_play_url: '立即播放$' + info[0]
        };
    }),

    搜索: $js.toString(() => {
        let items = [];
        let html = request(host + '/api/live/getRealLives');
        let json = JSON.parse(html);
        let list = json.data.list || [];
        let key = wd.toLowerCase();

        list.forEach(it => {
            let title = it.title || "";
            let anchor = it.anchor.nick_name || "";
            let category = it.badge_text || "";
            
            if (title.toLowerCase().indexOf(key) >= 0 || anchor.toLowerCase().indexOf(key) >= 0 || category.toLowerCase().indexOf(key) >= 0) {
                let extra = [it.pull_url, it.start_time, it.badge_text, it.anchor.nick_name, it.title, it.thumb].join('|');
                items.push({
                    title: it.title,
                    img: it.thumb,
                    desc: '[' + it.badge_text + '] ' + it.anchor.nick_name,
                    url: extra
                });
            }
        });
        setResult(items);
    }),
}