// @name 芸芸音乐[听]
// @version 1.0.1
// @author Silent1566
// @origin repo.tvshare.cn/api/files/download/[REDACTED]
// @push 0
// @downloadURL https://gh-proxy.org/https://github.com/Silent1566/OmniBox-Spider/raw/refs/heads/main/音乐/芸芸音乐.js

const OmniBox = require("omnibox_sdk");
const runner = require("spider_runner");

module.exports = { home, category, detail, search, play };
runner.run(module.exports);

const SOURCE_NAME = "芸芸音乐";
const GD_API = "https://music-api.gdstudio.xyz/api.php";
const NETEASE_HOST = "https://music.163.com";
const UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1";

const CLASSES = [
  { type_id: "recommend", type_name: "推荐歌单" },
  { type_id: "toplist", type_name: "排行榜" },
  { type_id: "hot", type_name: "热门歌单" },
  { type_id: "artist", type_name: "热门歌手" },
];

const HOT_CATS = ["全部", "华语", "流行", "摇滚", "民谣", "电子", "轻音乐", "影视原声", "ACG", "欧美", "日语", "韩语", "粤语"];
const FILTERS = {
  recommend: [{ key: "area", name: "分类", value: CLASSES.map(c => ({ n: c.type_name, v: c.type_id })) }],
  toplist: [{ key: "area", name: "分类", value: CLASSES.map(c => ({ n: c.type_name, v: c.type_id })) }],
  hot: [
    { key: "area", name: "分类", value: CLASSES.map(c => ({ n: c.type_name, v: c.type_id })) },
    { key: "cat", name: "歌单标签", value: HOT_CATS.map(v => ({ n: v, v })) },
  ],
  artist: [{ key: "area", name: "分类", value: CLASSES.map(c => ({ n: c.type_name, v: c.type_id })) }],
};

function logInfo(message, data) {
  return OmniBox.log("info", `[芸芸音乐] ${message}${data ? `: ${JSON.stringify(data)}` : ""}`);
}

function logError(message, error) {
  return OmniBox.log("error", `[芸芸音乐] ${message}: ${error?.message || error}`);
}

function safeJSONParse(input, fallback = {}) {
  if (!input) return fallback;
  if (typeof input === "object") return input;
  try {
    return JSON.parse(String(input));
  } catch {
    return fallback;
  }
}

function getResponseBody(res) {
  if (!res) return "";
  if (typeof res === "string") return res;
  return res.body ?? res.content ?? res.data ?? "";
}

async function requestText(url, options = {}) {
  const headers = {
    "User-Agent": UA,
    Referer: "https://music.163.com/",
    Accept: "*/*",
    ...(options.headers || {}),
  };
  const res = await OmniBox.request(url, {
    method: options.method || "GET",
    headers,
    data: options.data,
    timeout: options.timeout || 12000,
  });
  const statusCode = res?.statusCode || res?.status || 200;
  if (statusCode >= 400) throw new Error(`HTTP ${statusCode} @ ${url}`);
  return getResponseBody(res);
}

async function requestJson(url, fallback = {}) {
  const body = await requestText(url);
  return safeJSONParse(body, fallback);
}

function getPicUrl(pic, size = "500y500") {
  if (!pic) return "";
  const clean = String(pic).replace(/\?param=\d+y\d+$/i, "");
  if (!/^https?:\/\//i.test(clean)) return clean;
  return `${clean}?param=${size}`;
}

function getSongPic(song = {}, defaultPic = "", size = "300y300") {
  return getPicUrl(song.al?.picUrl || song.album?.picUrl || song.picUrl || defaultPic, size);
}

function getArtistName(song = {}) {
  return song.ar?.map(a => a.name).filter(Boolean).join("/")
    || song.artists?.map(a => a.name).filter(Boolean).join("/")
    || song.artist
    || "";
}

function formatNumber(num) {
  const value = Number(num || 0);
  if (!value) return "0";
  if (value >= 100000000) return `${(value / 100000000).toFixed(1)}亿`;
  if (value >= 10000) return `${(value / 10000).toFixed(1)}万`;
  return String(value);
}

function b64Encode(obj) {
  return Buffer.from(JSON.stringify(obj), "utf8").toString("base64");
}

function b64Decode(text) {
  try {
    return JSON.parse(Buffer.from(String(text || ""), "base64").toString("utf8"));
  } catch {
    return {};
  }
}

function makePlayId(song, defaultPic = "") {
  const artist = getArtistName(song);
  const pic = getSongPic(song, defaultPic, "500y500");
  return `songplay:${b64Encode({
    id: String(song.id || song.songId || ""),
    name: song.name || "未知歌曲",
    artist,
    pic,
  })}`;
}

function decodePlayId(playId) {
  const id = String(playId || "");
  if (id.startsWith("songplay:")) return b64Decode(id.slice("songplay:".length));
  if (id.startsWith("song@")) return { id: id.slice("song@".length) };
  if (/^\d+$/.test(id)) return { id };
  return b64Decode(id);
}

function makeSongVod(song, defaultPic = "") {
  const artist = getArtistName(song);
  const name = song.name || "未知歌曲";
  const displayName = artist ? `${name} - ${artist}` : name;
  const pic = getSongPic(song, defaultPic, "300y300");
  return {
    vod_id: `song@${song.id}`,
    vod_name: displayName,
    vod_pic: pic,
    vod_remarks: song.al?.name || song.album?.name || artist || SOURCE_NAME,
    type_id: "music",
    type_name: "音乐",
    vod_tag: "music",
  };
}

function makeDetailVodId(type, id) {
  return `detail:${type}@${id}`;
}

function unwrapDetailVodId(videoId = "") {
  const raw = String(videoId || "");
  return raw.startsWith("detail:") ? raw.slice("detail:".length) : raw;
}

function isDetailVodId(videoId = "") {
  return /^(?:detail:)?(?:playlist|toplist|artist)@/.test(String(videoId || ""));
}

function buildEpisodes(tracks = [], defaultPic = "") {
  return tracks.filter(s => s?.id).map((song, index) => {
    const artist = getArtistName(song);
    const name = artist ? `${song.name} - ${artist}` : (song.name || `歌曲${index + 1}`);
    return { name, playId: makePlayId(song, defaultPic) };
  });
}

function buildLegacyPlayUrl(episodes = []) {
  return episodes.map(ep => `${String(ep.name || "播放").replace(/[$#]/g, " ")}$${ep.playId}`).join("#");
}

function getFilters(params = {}) {
  return params.filters || params.extend || params.ext || {};
}

async function getList(type, page, filters = {}) {
  const limit = 20;
  const offset = (Math.max(Number(page || 1), 1) - 1) * limit;
  const list = [];
  const area = filters.area || type;

  if (area && area !== type && ["recommend", "toplist", "hot", "artist"].includes(area)) {
    type = area;
  }

  await logInfo("分类请求", { type, page, filters });

  if (type === "recommend") {
    const json = await requestJson(`${NETEASE_HOST}/api/personalized/playlist?limit=${Math.max(limit, offset + limit)}`, {});
    (json.result || []).slice(offset, offset + limit).forEach(it => {
      list.push({
        vod_id: makeDetailVodId("playlist", it.id),
        vod_name: it.name || "推荐歌单",
        vod_pic: getPicUrl(it.picUrl, "300y300"),
        vod_remarks: `🎧${formatNumber(it.playCount)}`,
        vod_tag: "video",
        type_id: "music",
        type_name: "音乐",
      });
    });
  } else if (type === "toplist") {
    const json = await requestJson(`${NETEASE_HOST}/api/toplist`, {});
    (json.list || []).slice(offset, offset + limit).forEach(it => {
      list.push({
        vod_id: makeDetailVodId("toplist", it.id),
        vod_name: it.name || "排行榜",
        vod_pic: getPicUrl(it.coverImgUrl || it.picUrl, "300y300"),
        vod_remarks: it.updateFrequency || `${it.trackCount || 0}首`,
        vod_tag: "video",
        type_id: "music",
        type_name: "音乐",
      });
    });
  } else if (type === "artist") {
    const json = await requestJson(`${NETEASE_HOST}/api/artist/top?limit=${limit}&offset=${offset}`, {});
    (json.artists || []).forEach(it => {
      list.push({
        vod_id: makeDetailVodId("artist", it.id),
        vod_name: it.name || "歌手",
        vod_pic: getPicUrl(it.img1v1Url || it.picUrl, "300y300"),
        vod_remarks: `${it.albumSize || 0}张专辑`,
        vod_tag: "video",
        type_id: "music",
        type_name: "音乐",
      });
    });
  } else {
    const cat = filters.cat || "全部";
    const json = await requestJson(`${NETEASE_HOST}/api/playlist/list?cat=${encodeURIComponent(cat)}&limit=${limit}&offset=${offset}&order=hot`, {});
    (json.playlists || []).forEach(it => {
      list.push({
        vod_id: makeDetailVodId("playlist", it.id),
        vod_name: it.name || "热门歌单",
        vod_pic: getPicUrl(it.coverImgUrl, "300y300"),
        vod_remarks: it.playCount ? `🎧${formatNumber(it.playCount)}` : "热门歌单",
        vod_tag: "video",
        type_id: "music",
        type_name: "音乐",
      });
    });
  }

  return list;
}

async function home(params, context) {
  try {
    const listResult = await category({ categoryId: "recommend", page: 1 }, context);
    const list = (listResult.list || []).slice(0, 20);
    await logInfo("首页完成", { classCount: CLASSES.length, listCount: list.length });
    return { class: CLASSES, filters: FILTERS, list };
  } catch (e) {
    await logError("首页失败", e);
    return { class: CLASSES, filters: FILTERS, list: [] };
  }
}

async function category(params, context) {
  const page = Math.max(Number(params?.page || 1), 1);
  const categoryId = String(params?.categoryId || params?.type_id || "recommend");
  try {
    // 兼容部分宿主：即使列表项已标记为 video，仍可能把 playlist/toplist/artist 当 category 打开。
    // 这里直接返回详情里的歌曲列表，避免用户点击歌单后只是刷新推荐分组。
    if (isDetailVodId(categoryId)) {
      const detailResult = await detail({ videoId: categoryId }, context);
      const vod = detailResult?.list?.[0] || null;
      const episodes = vod?.vod_play_sources?.[0]?.episodes || [];
      const list = episodes.map((ep, index) => ({
        vod_id: `songplay:${String(ep.playId || "").replace(/^songplay:/, "")}`,
        vod_name: ep.name || `歌曲${index + 1}`,
        vod_pic: vod?.vod_play_pic?.split("#")?.[index] || vod?.vod_pic || "",
        vod_remarks: vod?.vod_name || SOURCE_NAME,
        type_id: "music",
        type_name: "音乐",
        vod_tag: "music",
      }));
      await logInfo("分类命中详情ID，已展开歌曲列表", { categoryId, page, listCount: list.length });
      return { page, pagecount: page, total: list.length, list };
    }

    const filters = getFilters(params);
    const list = await getList(categoryId, page, filters);
    await logInfo("分类完成", { categoryId, page, listCount: list.length });
    return {
      page,
      pagecount: list.length >= 20 ? page + 1 : page,
      total: list.length >= 20 ? page * 20 + 1 : (page - 1) * 20 + list.length,
      list,
    };
  } catch (e) {
    await logError("分类失败", e);
    return { page, pagecount: page, total: 0, list: [] };
  }
}

async function getSongDetail(songId) {
  const json = await requestJson(`${NETEASE_HOST}/api/song/detail?ids=[${encodeURIComponent(songId)}]`, {});
  return json.songs?.[0] || null;
}

async function detail(params, context) {
  const videoId = String(params?.videoId || "");
  try {
    await logInfo("详情入口", { videoId });
    const realVideoId = unwrapDetailVodId(videoId);
    const [type, ...rest] = realVideoId.split("@");
    const id = rest.join("@");
    if (!type || !id) return { list: [] };

    if (type === "song") {
      const song = await getSongDetail(id);
      if (!song) return { list: [] };
      const episodes = buildEpisodes([song]);
      const artist = getArtistName(song);
      const pic = getSongPic(song, "", "500y500");
      const vod = {
        vod_id: videoId,
        vod_name: artist ? `${song.name} - ${artist}` : song.name,
        vod_pic: pic,
        vod_actor: artist,
        type_id: "music",
        type_name: "音乐",
        vod_content: song.al?.name || song.album?.name || song.name,
        vod_play_sources: [{ name: SOURCE_NAME, episodes }],
        vod_play_from: SOURCE_NAME,
        vod_play_url: buildLegacyPlayUrl(episodes),
        vod_play_pic: pic,
        vod_play_pic_ratio: 1.0,
      };
      await logInfo("单曲详情完成", { songId: id, episodeCount: episodes.length });
      return { list: [vod] };
    }

    let json = {};
    let data = {};
    let tracks = [];
    if (type === "artist") {
      json = await requestJson(`${NETEASE_HOST}/api/artist/${encodeURIComponent(id)}`, {});
      data = json.artist || {};
      tracks = json.hotSongs || [];
    } else {
      json = await requestJson(`${NETEASE_HOST}/api/v6/playlist/detail?id=${encodeURIComponent(id)}`, {});
      data = json.playlist || json.result || {};
      tracks = data.tracks || [];
    }

    const defaultPic = getPicUrl(data.coverImgUrl || data.picUrl || data.img1v1Url, "500y500");
    const episodes = buildEpisodes(tracks, defaultPic);
    const vod = {
      vod_id: videoId,
      vod_name: data.name || (type === "artist" ? "未知歌手" : "未知歌单"),
      vod_pic: defaultPic,
      vod_actor: type === "artist" ? (data.name || "") : "",
      type_id: "music",
      type_name: "音乐",
      vod_remarks: type === "artist" ? `共${episodes.length}首` : `${formatNumber(data.playCount || 0)} | 共${episodes.length}首`,
      vod_content: data.description || data.briefDesc || data.name || "",
      vod_play_sources: [{ name: SOURCE_NAME, episodes }],
      vod_play_from: SOURCE_NAME,
      vod_play_url: buildLegacyPlayUrl(episodes),
      vod_play_pic: episodes.map(ep => decodePlayId(ep.playId.slice("songplay:".length))?.pic || "").join("#"),
      vod_play_pic_ratio: 1.0,
    };
    await logInfo("详情完成", { type, id, episodeCount: episodes.length });
    return { list: [vod] };
  } catch (e) {
    await logError("详情失败", e);
    return { list: [] };
  }
}

async function search(params, context) {
  const keyword = String(params?.keyword || params?.wd || "").trim();
  const page = Math.max(Number(params?.page || 1), 1);
  try {
    if (!keyword) return { page, pagecount: page, total: 0, list: [] };
    const json = await requestJson(`${NETEASE_HOST}/api/search/get?s=${encodeURIComponent(keyword)}&type=1&offset=${(page - 1) * 30}&limit=30`, {});
    const songs = json.result?.songs || json.songs || [];
    const list = songs.filter(s => s?.id).map(makeSongVod);
    await logInfo("搜索完成", { keyword, page, listCount: list.length });
    return {
      page,
      pagecount: list.length >= 30 ? page + 1 : page,
      total: list.length >= 30 ? page * 30 + 1 : (page - 1) * 30 + list.length,
      list,
    };
  } catch (e) {
    await logError("搜索失败", e);
    return { page, pagecount: page, total: 0, list: [] };
  }
}

async function gdGetUrl(songId, br) {
  const json = await requestJson(`${GD_API}?types=url&id=${encodeURIComponent(songId)}&source=netease&br=${br}`, null);
  return json;
}

async function getLyric(songId) {
  try {
    const json = await requestJson(`${NETEASE_HOST}/api/song/lyric?id=${encodeURIComponent(songId)}&lv=1&kv=1&tv=-1`, {});
    let lrc = json.lrc?.lyric || "";
    if (json.tlyric?.lyric) lrc += `\n\n【翻译】\n${json.tlyric.lyric}`;
    return lrc;
  } catch (e) {
    await logError("歌词获取失败", e);
    return "";
  }
}

async function play(params, context) {
  const playId = String(params?.playId || "").trim();
  const flag = String(params?.flag || SOURCE_NAME);
  try {
    const meta = decodePlayId(playId);
    const songId = String(meta.id || "").trim();
    if (!songId) throw new Error("songId 为空");

    const qualities = [
      { name: "FLAC无损", br: 2000 },
      { name: "HQ高品质", br: 320 },
      { name: "标准品质", br: 192 },
      { name: "AAC流畅", br: 128 },
    ];

    const urls = [];
    const seen = new Set();
    for (const q of qualities) {
      try {
        const res = await gdGetUrl(songId, q.br);
        const url = res?.url || res?.data?.url || "";
        if (url && /^https?:\/\//i.test(url) && !seen.has(url)) {
          seen.add(url);
          urls.push({ name: q.name, url });
        }
      } catch (e) {
        await logError(`音质地址获取失败 ${q.name}`, e);
      }
    }

    if (!urls.length) throw new Error("未获取到可播放地址");
    const [lrc, songInfo] = await Promise.all([
      getLyric(songId),
      meta.pic ? Promise.resolve(null) : getSongDetail(songId).catch(() => null),
    ]);
    const cover = meta.pic || getSongPic(songInfo || {}, "", "500y500");
    await logInfo("播放完成", { songId, urlCount: urls.length, hasLrc: !!lrc, hasCover: !!cover });
    return {
      urls,
      url: urls[0].url,
      parse: 0,
      header: { "User-Agent": UA, Referer: "https://music.163.com/" },
      pic: cover,
      cover,
      lrc,
      height: 720};
  } catch (e) {
    await logError("播放失败", e);
    return { urls: [], parse: 0, header: { "User-Agent": UA, Referer: "https://music.163.com/" } };
  }
}
