var rule = {
    title: '178体育直播',
    host: 'https://178sz33.j804y.com',
    url: '/api/live_lists/fyclass',
    class_name: '全部&足球&篮球',
    class_url: '99&1&2',
    headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://178sz33.j804y.com/'
    },
    play_parse: true,
    double: true,

    一级: $js.toString(() => {
        let items = [];
        let html = request(url);
        let jo = JSON.parse(html);
        let list = jo.data.list || jo.banner || jo.hot || [];
        list.forEach(it => {
            let home = it.home_team_zh || it.home_team || '未知主队';
            let away = it.away_team_zh || it.away_team || '未知客队';
            let league = it.league_name_zh || it.league_name || '未知赛事';
            let time = it.start_time || '';
            let viewer = it.viewer || it.ip_count || 0;
            
            items.push({
                title: home + ' VS ' + away,
                desc: (time ? '[' + time + '] ' : '') + league + ' | 👤' + viewer,
                pic_url: it.cover || 'https://via.placeholder.com/300x400?text=178zb',
                url: 'match$' + (it.uid || it.member_id) + '|' + (it.tournament_id || it.id)
            });
        });
        setResult(items);
    }),

    二级: $js.toString(() => {
        let str = orId.split('$')[1];
        let uid = str.split('|')[0];
        let id = str.split('|')[1];
        
        let detailUrl = rule.host + '/api/web_match/1/detail/' + id;
        let html = request(detailUrl, {
            method: 'POST',
            body: JSON.stringify({ "member_id": uid })
        });
        
        let jo = JSON.parse(html);
        let data = jo.data;
        let detail = data.detail;

        VOD = {
            vod_name: (detail.home_team_zh || '未知') + ' VS ' + (detail.away_team_zh || '未知'),
            vod_pic: detail.cover,
            type_name: detail.league_name_zh || '体育赛事',
            vod_remarks: '🔥人气: ' + (detail.viewer || 0),
            vod_content: '主播: ' + (detail.username || '官方') + ' \\n比分: ' + (detail.home_score || 0) + ':' + (detail.away_score || 0) + ' \\n状态: ' + (detail.on_time ? '进行中(' + detail.on_time + '分)' : '直播中') + ' \\n公告: ' + (detail.room_notice || '绿色直播，禁言广告'),
            vod_actor: '赛事: ' + (detail.league_name_zh || '体育直播')
        };

        let playSources = [];
        let playUrls = [];

        let extractLinks = (obj) => {
            let links = [];
            if (obj.screen_url_m3u8) links.push('M3U8$' + obj.screen_url_m3u8);
            if (obj.stream && obj.stream.indexOf('.m3u8') > -1) links.push('蓝光M3U8$' + obj.stream);
            if (obj.flvurl) links.push('高清FLV$' + obj.flvurl);
            if (obj.url && obj.url !== obj.flvurl) links.push('备用FLV$' + obj.url);
            if (obj.screen_url && obj.screen_url.indexOf('.flv') > -1 && obj.screen_url !== obj.flvurl) {
                links.push('移动FLV$' + obj.screen_url);
            }
            return links.join('#');
        };

        let mainStream = extractLinks(detail);
        if (mainStream) {
            playSources.push((detail.username || '主线路') + '(极速)');
            playUrls.push(mainStream);
        }

        if (data.more && data.more.length > 0) {
            data.more.forEach(m => {
                if (m.member_id != detail.member_id) {
                    let moreStream = extractLinks(m);
                    if (moreStream) {
                        playSources.push(m.username + ' | 👥' + (m.viewer || 0));
                        playUrls.push(moreStream);
                    }
                }
            });
        }

        VOD.vod_play_from = playSources.join('$$$');
        VOD.vod_play_url = playUrls.join('$$$');
    }),
    
    搜索: '*'
};