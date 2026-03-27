var rule = {
    title: '咖啡直播',
    host: 'https://kafeizhibo.com',
    url: '/api/v1/schedule?type=fyclass&page=fypage&size=30',
    class_name: '全部&NBA&足球&篮球',
    class_url: 'all&nba&1&2',
    headers: {
        'User-Agent': 'MOBILE_UA',
        'Referer': 'https://kafeizhibo.com/'
    },
    play_parse: true,
    double: true,

    一级: $js.toString(() => {
        let items = [];
        let html = request(input);
        let jo = JSON.parse(html);
        if (jo.code === 200 && jo.data) {
            jo.data.forEach(it => {
                let home = it.home_team || '未知主队';
                let away = it.away_team || '未知客队';
                let league = it.league_name || '体育赛事';
                let statusLabel = it.status === 'live' ? '●直播中 ' : (it.status === 'preview' ? '⏳未开播 ' : '⚫已结束 ');
                let scoreStr = (it.status === 'live' || it.status === 'end') ? ` [${it.home_score}-${it.away_score}] ` : ' vs ';
                let pic = it.screenshot || it.home_team_logo || '';
                if (pic && !pic.startsWith('http')) {
                    pic = rule.host + pic;
                }
                let roomId = it.archor ? it.archor.room_id : '';
                if (roomId) {
                    items.push({
                        title: home + scoreStr + away,
                        desc: statusLabel + (it.start_time || '') + ' | ' + league,
                        pic_url: pic,
                        url: rule.host + '/api/v1/room/' + roomId
                    });
                }
            });
        }
        setResult(items);
    }),

    二级: $js.toString(() => {
        let detailUrl = input;
        let html = request(detailUrl);
        let jo = JSON.parse(html);
        if (jo.code === 200 && jo.data) {
            let data = jo.data;
            let room = data.room_info || {};
            let archor = data.archor || {};
            let teams = data.teams || {};
            let vod_pic = '';
            if (teams.home && teams.home.logo) {
                vod_pic = teams.home.logo;
            } else if (archor.screenshot) {
                vod_pic = archor.screenshot.startsWith('http') ? archor.screenshot : (rule.host + archor.screenshot);
            }
            VOD = {
                vod_name: room.title || (room.home_team + ' VS ' + room.away_team),
                vod_pic: vod_pic,
                type_name: room.league || '体育直播',
                vod_remarks: (data.status === 'live' ? '🔴正在直播' : '⏳未开始') + ' | 🔥热度:' + (archor.heat || 0),
                vod_actor: (room.home_team || '主队') + ' VS ' + (room.away_team || '客队'),
                vod_content: '公告: ' + (room.notice || '欢迎观赛')
            };
            let playSources = [];
            let playUrls = [];
            if (data.signals && data.signals.length > 0) {
                data.signals.forEach(sig => {
                    if (sig.stream_url) {
                        playSources.push(sig.name);
                        playUrls.push('播放$' + sig.stream_url);
                    }
                });
            }
            if (playUrls.length === 0 && archor.stream_url) {
                playSources.push(archor.name || '默认线路');
                playUrls.push('播放$' + archor.stream_url);
            }
            VOD.vod_play_from = playSources.join('$$$');
            VOD.vod_play_url = playUrls.join('$$$');
        }
    }),
    
    搜索: '*'
};