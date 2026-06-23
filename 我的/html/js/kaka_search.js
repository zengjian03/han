// WebHome extension for 卡卡搜索 (pan.nblizhe.top)
// Strategy: Search pan resources from multiple sources
(function() {
  "use strict";

  var CONFIG = {
    id: "fm-kaka-search",
    name: "卡卡搜索",
    apiBase: "https://pan.nblizhe.top/api",
    maxSearchItems: 48,
    scanDelay: 200,
    rootId: "fm-kaka-root",
    sourceMap: {
      "quark": { label: "夸克", host: "pan.quark.cn" },
      "baidu": { label: "百度", host: "pan.baidu.com" },
      "aliyun": { label: "阿里", host: "aliyundrive.com" },
      "123": { label: "123", host: "123pan.com" },
      "115": { label: "115", host: "115.com" },
      "xunlei": { label: "迅雷", host: "pan.xunlei.com" },
      "magnet": { label: "磁力", host: "" }
    }
  };

  var TYPE_LABEL = {
    quark: "夸克网盘",
    aliyun: "阿里云盘",
    baidu: "百度网盘",
    uc: "UC网盘",
    xunlei: "迅雷网盘",
    tianyi: "天翼云",
    "123": "123网盘",
    "115": "115网盘",
    mobile: "移动云",
    magnet: "磁力链接",
    ed2k: "电驴",
    thunder: "Thunder",
    media: "直链"
  };

  var state = {
    scanTimer: 0,
    searchItems: [],
    activeTitle: "",
    activePic: "",
    activeWallPic: "",
    panelMode: "idle",
    busy: false
  };

  function log() {
    var args = Array.prototype.slice.call(arguments);
    if (typeof GM_log === "function") GM_log.apply(null, args);
    else if (window.console && console.log) console.log.apply(console, ["[kaka]"].concat(args));
  }

  function ready(fn) {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", fn, { once: true });
    else fn();
  }

  function whenFm() {
    if (window.fm) return Promise.resolve(window.fm);
    return new Promise(function(resolve) {
      window.addEventListener("fmsdk", function() { resolve(window.fm); }, { once: true });
    });
  }

  function toast(message) {
    if (window.fm && window.fm.ext && window.fm.ext.toast) {
      window.fm.ext.toast(message).catch(function() {});
    } else {
      log(message);
    }
  }

  function cleanText(value) {
    return String(value || "").replace(/\s+/g, " ").replace(/^\s+|\s+$/g, "");
  }

  function getAttr(el, name) {
    return el && el.getAttribute ? cleanText(el.getAttribute(name)) : "";
  }

  function matchesSelector(el, selector) {
    if (!el || el.nodeType !== 1) return false;
    var fn = el.matches || el.msMatchesSelector || el.webkitMatchesSelector;
    if (!fn) return false;
    try { return fn.call(el, selector); } catch (e) { return false; }
  }

  function closest(el, selector) {
    var node = el;
    while (node && node.nodeType === 1) {
      if (matchesSelector(node, selector)) return node;
      node = node.parentElement;
    }
    return null;
  }

  function queryAll(selector, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(selector));
  }

  function requestText(url, options) {
    var opts = options || {};
    if (window.fm && window.fm.req) {
      return window.fm.req(url, {
        method: opts.method || "GET",
        headers: opts.headers || {},
        body: opts.body || "",
        responseType: "text",
        timeout: opts.timeout || 15,
        credentials: opts.credentials || "include"
      }).then(function(resp) {
        return resp || { ok: false, status: 500, body: "", error: "empty" };
      });
    }
    if (!window.fetch) return Promise.resolve({ ok: false, status: 500, body: "", error: "fetch unavailable" });
    return window.fetch(url, {
      method: opts.method || "GET",
      headers: opts.headers || {},
      credentials: "include"
    }).then(function(resp) {
      return resp.text().then(function(text) {
        return { ok: resp.ok, status: resp.status, body: text, error: resp.ok ? "" : "HTTP " + resp.status };
      });
    }).catch(function(err) {
      return { ok: false, status: 500, body: "", error: err && err.message || String(err) };
    });
  }

  function classifyUrl(url) {
    var lower = cleanText(url).toLowerCase();
    if (/^magnet:/i.test(lower)) return "magnet";
    if (/^ed2k:/i.test(lower)) return "ed2k";
    if (/^thunder:/i.test(lower)) return "thunder";
    if (/\.(m3u8|mp4|mkv|flv|mov|avi|webm)(\?|#|$)/i.test(lower)) return "media";
    if (lower.indexOf("pan.quark.cn") >= 0) return "quark";
    if (lower.indexOf("aliyundrive.com") >= 0 || lower.indexOf("alipan.com") >= 0) return "aliyun";
    if (lower.indexOf("pan.baidu.com") >= 0) return "baidu";
    if (lower.indexOf("drive.uc.cn") >= 0) return "uc";
    if (lower.indexOf("pan.xunlei.com") >= 0) return "xunlei";
    if (lower.indexOf("cloud.189.cn") >= 0) return "tianyi";
    if (lower.indexOf("123pan.") >= 0 || lower.indexOf("123684.") >= 0) return "123";
    if (lower.indexOf("115.com") >= 0 || lower.indexOf("115cdn.com") >= 0) return "115";
    if (lower.indexOf("yun.139.com") >= 0) return "mobile";
    return "http";
  }

  function extractPassword(url) {
    var text = String(url || "");
    var patterns = [/[?&]pwd=([a-zA-Z0-9]{4})/i, /[?&]password=([a-zA-Z0-9]{4})/i, /提取码[:：]\s*([a-zA-Z0-9]{4})/i];
    for (var i = 0; i < patterns.length; i++) {
      var match = text.match(patterns[i]);
      if (match && match[1]) return match[1];
    }
    return "";
  }

  function buildSearchUrl(keyword, page) {
    return CONFIG.apiBase + "/search?keyword=" + encodeURIComponent(keyword) + "&page=" + (page || 1) + "&pageSize=20";
  }

  function fetchSearch(keyword, page) {
    state.busy = true;
    renderLoading("搜索中: " + keyword);
    requestText(buildSearchUrl(keyword, page), {
      method: "GET",
      headers: { "Accept": "application/json" },
      timeout: 20
    }).then(function(resp) {
      state.busy = false;
      if (!resp || !resp.ok) {
        renderNotice("搜索请求失败", "error");
        return;
      }
      try {
        var json = JSON.parse(resp.body);
        if (json.code === 200 && json.data && json.data.items) {
          state.searchItems = json.data.items.map(function(item) {
            return {
              id: item.id,
              title: cleanText(item.title || item.name),
              url: item.url,
              time: item.times || "",
              views: item.page_views || 0,
              type: classifyUrl(item.url)
            };
          });
          renderSearch(state.searchItems, keyword);
        } else {
          renderNotice("未找到相关资源", "warn");
        }
      } catch(e) {
        renderNotice("JSON解析失败", "error");
      }
    }).catch(function(err) {
      state.busy = false;
      renderNotice("搜索失败: " + (err && err.message || String(err)), "error");
    });
  }

  function ensureRoot() {
    var root = document.getElementById(CONFIG.rootId);
    if (root) return root;
    root = document.createElement("div");
    root.id = CONFIG.rootId;
    root.className = "fm-kaka-root fm-kaka-collapsed";
    root.innerHTML = ""
      + "<div class=\"fm-kaka-panel\">"
      + "<div class=\"fm-kaka-head\"><b>卡卡搜索</b><button type=\"button\" data-fm-kaka-action=\"toggle\">收起</button></div>"
      + "<div class=\"fm-kaka-body\" id=\"fm-kaka-body\"></div>"
      + "</div>";
    document.body.appendChild(root);
    return root;
  }

  function bodyEl() {
    ensureRoot();
    return document.getElementById("fm-kaka-body");
  }

  function escapeHtml(text) {
    return String(text || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').split(String.fromCharCode(34)).join('&' + 'quot;');
  }

  function openPanel() {
    var root = ensureRoot();
    root.className = root.className.replace(/\bfm-kaka-collapsed\b/g, "");
  }

  function addClass(el, name) {
    if (!el || !name) return;
    var classes = " " + (el.className || "") + " ";
    if (classes.indexOf(" " + name + " ") >= 0) return;
    el.className = cleanText((el.className || "") + " " + name);
  }

  function renderNotice(text, tone) {
    var body = bodyEl();
    state.panelMode = "notice";
    body.innerHTML = "<div class=\"fm-kaka-msg fm-kaka-" + (tone || "info") + "\">" + escapeHtml(text) + "</div>";
    if (tone === "error" || tone === "warn" || tone === "loading") openPanel();
    return bodyEl();
  }

  function renderLoading(text) {
    state.panelMode = "loading";
    openPanel();
    bodyEl().innerHTML = "<div class=\"fm-kaka-msg fm-kaka-loading\">" + escapeHtml(text || "加载中...") + "</div>";
  }

  function renderSearch(items, keyword) {
    state.panelMode = "search";
    var body = bodyEl();
    if (!items || !items.length) {
      body.innerHTML = "<div class=\"fm-kaka-msg\">未找到资源: " + escapeHtml(keyword) + "</div>";
      return;
    }
    var html = "<div class=\"fm-kaka-msg\">找到 " + items.length + " 条资源</div>";
    for (var i = 0; i < Math.min(items.length, CONFIG.maxSearchItems); i++) {
      var item = items[i];
      html += "<div class=\"fm-kaka-item\">"
        + "<div class=\"fm-kaka-title\">" + escapeHtml(item.title) + "</div>"
        + "<div class=\"fm-kaka-sub\">" + escapeHtml(TYPE_LABEL[item.type] || item.type) + " · " + escapeHtml(item.time || "") + " · " + (item.views || 0) + "次浏览</div>"
        + "<button type=\"button\" data-fm-kaka-action=\"play-link\" data-fm-kaka-index=\"" + i + "\">App播放</button>"
        + "</div>";
    }
    body.innerHTML = html;
    openPanel();
  }

  function playLink(link) {
    if (!link || !link.url) return;
    log("playLink called", link);
    toast("正在推送: " + (link.title || "资源"));
    whenFm().then(function(sdk) {
      log("fm SDK ready", sdk);
      if (!sdk) throw new Error("SDK is null");
      if (!sdk.pan) throw new Error("sdk.pan not found");
      log("sdk.pan available", sdk.pan);
      var panType = link.type;
      if (panType === "magnet") panType = "magnet";
      else if (panType === "media" || panType === "http") panType = "http";
      else if (!panType) panType = "http";
      log("pan type:", panType, "url:", link.url);
      return sdk.pan.play({
        type: panType,
        url: link.url,
        password: link.password || "",
        title: link.title || "卡卡资源",
        pic: state.activePic || "",
        wallPic: state.activeWallPic || ""
      });
    }).then(function(result) {
      log("push success", result);
      toast("推送成功");
    }).catch(function(err) {
      log("play failed", err && (err.stack || err.message || err));
      toast("推送失败: " + (err && err.message || "未知错误"));
    });
  }

  function firstResourceUrl(text) {
    text = String(text || "");
    var patterns = [
      /magnet:\?xt=urn:btih:[a-zA-Z0-9]+[^\s<>'"]*/i,
      /ed2k:\/\/[^\s<>'"]+/i,
      /thunder:\/\/[^\s<>'"]+/i,
      /https?:\/\/pan\.quark\.cn\/s\/[a-zA-Z0-9]+/i,
      /https?:\/\/pan\.baidu\.com\/s\/[a-zA-Z0-9_-]+(?:\?pwd=[a-zA-Z0-9]{4,8})?/i,
      /https?:\/\/(?:www\.)?(?:alipan|aliyundrive)\.com\/s\/[a-zA-Z0-9]+/i,
      /https?:\/\/pan\.xunlei\.com\/s\/[a-zA-Z0-9]+(?:\?pwd=[a-zA-Z0-9]{4,8})?/i,
      /https?:\/\/drive\.uc\.cn\/s\/[a-zA-Z0-9]+[^\s<>'"]*/i,
      /https?:\/\/(?:www\.)?123(?:684|685|865|912|pan|592)\.(?:com|cn)\/s\/[a-zA-Z0-9_-]+[^\s<>'"]*/i,
      /https?:\/\/(?:115\.com|115cdn\.com|anxia\.com)\/s\/[a-zA-Z0-9]+[^\s<>'"]*/i
    ];
    for (var i = 0; i < patterns.length; i++) {
      var m = text.match(patterns[i]);
      if (m && m[0]) return m[0].replace(/&amp;/g, "&");
    }
    return "";
  }

  function titleFromNode(node) {
    var text = cleanText(node && node.textContent || document.title || "卡卡资源");
    text = text.replace(/转存结果|获取成功|资源地址|资源10分钟失效，请尽快保存|复制链接|打开链接|关闭/g, " ");
    text = cleanText(text);
    return text || state.activeTitle || "卡卡资源";
  }

  function routeOriginalPanClick(event) {
    var node = closest(event.target, "button,a,[role='button'],.el-button");
    if (!node) return false;
    var hint = cleanText(node.textContent) + " " + getAttr(node, "class") + " " + getAttr(node, "href");
    if (!/(打开链接|复制链接|App播放|播放|转存|pan\.quark|pan\.baidu|aliyundrive|alipan|123pan|115\.com|magnet)/i.test(hint)) return false;
    var host = closest(node, ".el-dialog,.el-dialog__wrapper,.van-dialog,.modal,.dialog,[role='dialog']") || node.parentElement || document.body;
    var url = firstResourceUrl(getAttr(node, "href") + " " + getAttr(node, "data-url") + " " + getAttr(node, "data-href") + " " + getAttr(node, "data-clipboard-text") + " " + (host.textContent || ""));
    if (!url) return false;
    if (event.cancelable !== false) event.preventDefault();
    event.stopPropagation();
    event.stopImmediatePropagation();
    playLink({ url: url, title: titleFromNode(host), type: classifyUrl(url), password: extractPassword(url) });
    return true;
  }

  function enhanceOriginalModal() {
    var nodes = queryAll(".el-dialog,.van-dialog,.modal,.dialog,[role='dialog']");
    for (var i = 0; i < nodes.length; i++) {
      var host = nodes[i];
      if (!host || host.querySelector && host.querySelector(".fm-kaka-origin-play")) continue;
      var url = firstResourceUrl(host.textContent || "");
      if (!url) continue;
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "fm-kaka-origin-play";
      btn.textContent = "App播放";
      btn.setAttribute("data-fm-kaka-action", "origin-play");
      btn.setAttribute("data-fm-kaka-url", url);
      btn.setAttribute("data-fm-kaka-title", titleFromNode(host));
      var footer = host.querySelector && (host.querySelector(".el-dialog__footer,.dialog-footer,.van-dialog__footer") || host.querySelector("button") && host.querySelector("button").parentElement);
      if (footer && footer.querySelector && footer.querySelector(".fm-kaka-origin-play")) continue;
      (footer || host).appendChild(btn);
    }
  }

  function onPanelClick(event) {
    if (routeOriginalPanClick(event)) return;
    var target = closest(event.target, "[data-fm-kaka-action]");
    if (!target) return;
    event.preventDefault();
    event.stopPropagation();
    var action = getAttr(target, "data-fm-kaka-action");
    if (action === "toggle") {
      var root = ensureRoot();
      if (/\bfm-kaka-collapsed\b/.test(root.className)) root.className = root.className.replace(/\bfm-kaka-collapsed\b/g, "");
      else root.className += " fm-kaka-collapsed";
      return;
    }
    if (action === "play-link") {
      var index = Number(getAttr(target, "data-fm-kaka-index"));
      var item = state.searchItems[index];
      if (item) {
        state.activeTitle = item.title;
        playLink({ url: item.url, title: item.title, type: item.type, password: item.password || "" });
      }
      return;
    }
    if (action === "origin-play") {
      playLink({ url: getAttr(target, "data-fm-kaka-url"), title: getAttr(target, "data-fm-kaka-title") || "卡卡资源", type: classifyUrl(getAttr(target, "data-fm-kaka-url")), password: extractPassword(getAttr(target, "data-fm-kaka-url")) });
      return;
    }
    if (action === "search") {
      var input = document.querySelector("#kaka-search-input");
      var keyword = input ? cleanText(input.value) : "";
      if (keyword) fetchSearch(keyword, 1);
      return;
    }
  }

  function initSearchBox() {
    var existing = document.getElementById("fm-kaka-search-box");
    if (existing) return;
    var searchBox = document.createElement("div");
    searchBox.id = "fm-kaka-search-box";
    searchBox.innerHTML = ""
      + "<input type=\"text\" id=\"kaka-search-input\" placeholder=\"输入关键词搜索...\" style=\""
      + "padding:8px 12px;border:1px solid #ddd;border-radius:6px;width:200px;font-size:14px;margin-right:8px;"
      + "\">"
      + "<button type=\"button\" data-fm-kaka-action=\"search\" style=\""
      + "padding:8px 16px;background:#ff6b6b;color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:14px;"
      + "\">搜索</button>";
    var target = document.querySelector(".search-box-wrapper, .search-input-box, .home-main");
    if (target) {
      target.insertBefore(searchBox, target.firstChild);
    }
  }

  function installStyle() {
    if (document.getElementById("fm-kaka-style")) return;
    var css = ""
      + "#" + CONFIG.rootId + "{position:fixed;right:12px;bottom:calc(12px + var(--fm-safe-bottom,0px));z-index:2147483647;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC',sans-serif;color:#333;}"
      + "#" + CONFIG.rootId + " *{box-sizing:border-box;}"
      + ".fm-kaka-panel{width:360px;max-width:calc(100vw - 24px);max-height:70vh;margin-bottom:8px;border:1px solid rgba(0,0,0,.15);border-radius:16px;background:rgba(255,255,255,.98);box-shadow:0 20px 60px rgba(0,0,0,.3);overflow:hidden;}"
      + ".fm-kaka-collapsed .fm-kaka-panel{display:none!important;}"
      + ".fm-kaka-head{min-height:44px;padding:10px 12px;border-bottom:1px solid rgba(0,0,0,.1);display:flex;justify-content:space-between;align-items:center;}"
      + ".fm-kaka-head b{font-size:15px;}"
      + ".fm-kaka-head button{padding:4px 12px;border:1px solid #ddd;border-radius:6px;background:#f5f5f5;cursor:pointer;}"
      + ".fm-kaka-body{max-height:calc(70vh - 46px);overflow:auto;padding:10px;}"
      + ".fm-kaka-msg{padding:10px;margin-bottom:8px;border-radius:10px;background:#f8f8f8;font-size:13px;}"
      + ".fm-kaka-warn{border-left:3px solid #ffa940;}"
      + ".fm-kaka-error{border-left:3px solid #ff6b6b;}"
      + ".fm-kaka-ok{border-left:3px solid #52c41a;}"
      + ".fm-kaka-loading{border-left:3px solid #1890ff;}"
      + ".fm-kaka-item{padding:10px;margin-bottom:8px;border:1px solid #eee;border-radius:10px;background:#fafafa;}"
      + ".fm-kaka-title{font-size:14px;font-weight:600;margin-bottom:4px;}"
      + ".fm-kaka-sub{font-size:12px;color:#666;margin-bottom:6px;}"
      + ".fm-kaka-item button,.fm-kaka-origin-play{padding:6px 14px;background:#ff6b6b;color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:12px;margin:4px;}"
      + ".fm-kaka-item button:active,.fm-kaka-origin-play:active{background:#e65a5a;}"
      + "#fm-kaka-search-box{position:absolute;left:20px;top:20px;z-index:100;}"
      + "@media (max-width:768px){"
      + "#" + CONFIG.rootId + "{right:8px;bottom:8px;}"
      + ".fm-kaka-panel{width:calc(100vw - 16px);}"
      + "}";
    var style = document.createElement("style");
    style.id = "fm-kaka-style";
    style.textContent = css;
    (document.head || document.documentElement).appendChild(style);
  }

  function scanPage() {
    if (!document.body) return;
    ensureRoot();
    installStyle();
    initSearchBox();
    enhanceOriginalModal();
    if (state.panelMode === "idle") {
      renderNotice("在搜索框输入关键词开始搜索网盘资源", "info");
    }
  }

  function scheduleScan() {
    clearTimeout(state.scanTimer);
    state.scanTimer = setTimeout(scanPage, CONFIG.scanDelay);
  }

  function boot() {
    ready(function() {
      ensureRoot();
      document.addEventListener("click", onPanelClick, true);
      new MutationObserver(scheduleScan).observe(document.documentElement, { childList: true, subtree: true });
      scheduleScan();
    });
    window.addEventListener("fmurlchange", scheduleScan);
    log("ready", location.href);
  }

  boot();
})();