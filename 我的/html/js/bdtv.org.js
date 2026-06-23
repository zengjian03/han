// WebHome extension for https://www.bdtv.org/
// Optimized behavior:
// - Build one clean native playback panel on the play page.
// - Parse embedded player_aaaa variable to extract m3u8 URL.
// - On detail page: intercept episode clicks to route to native playback.
// - On play page: hide iframe player, show direct-play panel with all routes.
// - Proxy images via fm.res() for WebView compatibility.
// - Simplify mobile pages into a search-first movie UI with TV focus states.
(function () {
  var CONFIG = {
    panelId: "fm-bdtv-panel",
    searchId: "fm-bdtv-search",
    name: "fm-bdtv",
    // Page detection
    detailRegex: /\/voddetail\/\d+\.html/i,
    playRegex: /\/vodplay\/\d+-\d+-\d+\.html/i,
    listRegex: /\/vodshow\/|\/vodtype\/|\/vodsearch\//i,
    // Selectors
    titleSelector: ".stui-content__detail h1.title",
    detailInfoSelector: ".stui-content__detail",
    itemSelector: ".stui-vodlist > li",
    itemThumbSelector: ".stui-vodlist__thumb",
    itemTitleSelector: ".stui-vodlist__detail h4.title a",
    episodeSelector: ".stui-content__playlist a.btn",
    routeTabSelector: ".nav-tabs > li > a",
    playerContainerSelector: ".stui-player__video",
    playerIframeSelector: ".MacPlayer #playleft iframe",
    playlistContainerSelector: ".stui-pannel-box.b.playlist",
    scanDelay: 200
  };

  var state = {
    activeTab: "online",
    items: {
      online: []
    },
    parsed: false,
    playerData: null,
    imagesProxied: false
  };

  function log() {
    var args = Array.prototype.slice.call(arguments);
    if (typeof GM_log === "function") GM_log.apply(null, args);
    else console.log.apply(console, ["[fm-bdtv]"].concat(args));
  }

  function toast(msg) {
    try {
      if (window.fm && fm.ext && fm.ext.toast) return fm.ext.toast(msg);
    } catch (e) { /* ignore */ }
    return Promise.resolve();
  }

  function whenFm() {
    if (window.fm) return Promise.resolve(window.fm);
    return new Promise(function (resolve) {
      window.addEventListener("fmsdk", function () { resolve(window.fm); }, { once: true });
    });
  }

  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn, { once: true });
    } else {
      fn();
    }
  }

  function cleanText(text) {
    return String(text || "").replace(/\s+/g, " ").trim();
  }

  function escapeHtml(value) {
    return String(value == null ? "" : value).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;" }[c];
    });
  }

  function pageTitle() {
    var el = document.querySelector(CONFIG.titleSelector);
    var text = el ? cleanText(el.textContent) : "";
    if (text) return text;
    var match = document.title.match(/^(.+?)\s*[-–—]/);
    if (match) return match[1];
    return cleanText(document.title.replace(/\s*[-–—].*$/, "")) || location.href;
  }

  function pageType() {
    var path = location.pathname;
    if (CONFIG.playRegex.test(path)) return "play";
    if (CONFIG.detailRegex.test(path)) return "detail";
    if (CONFIG.listRegex.test(path) || path === "/") return "list";
    return "other";
  }

  function absoluteUrl(url) {
    if (!url || url === "#" || /^javascript:/i.test(url)) return "";
    if (/^(magnet:|ed2k:|thunder:)/i.test(url)) return url;
    if (/^\/\//i.test(url)) {
      try { return new URL(url, location.href).href; } catch (e) { return "https:" + url; }
    }
    try { return new URL(url, location.href).href; } catch (e) { return url; }
  }

  function classify(url) {
    if (/^magnet:/i.test(url)) return { type: "magnet", group: "magnet", label: "磁力" };
    if (/^ed2k:/i.test(url)) return { type: "ed2k", group: "magnet", label: "电驴" };
    if (/^thunder:/i.test(url)) return { type: "thunder", group: "magnet", label: "迅雷" };
    if (/pan\.quark\.cn/i.test(url)) return { type: "quark", group: "pan", label: "夸克" };
    if (/aliyundrive\.com|alipan\.com/i.test(url)) return { type: "aliyun", group: "pan", label: "阿里" };
    if (/pan\.baidu\.com/i.test(url)) return { type: "baidu", group: "pan", label: "百度" };
    if (/drive\.uc\.cn/i.test(url)) return { type: "uc", group: "pan", label: "UC" };
    if (/pan\.xunlei\.com/i.test(url)) return { type: "xunlei", group: "pan", label: "迅雷盘" };
    if (/cloud\.189\.cn/i.test(url)) return { type: "tianyi", group: "pan", label: "天翼" };
    if (/123pan\.|123684\.|123685\.|123912\.|123592\.|123865\./i.test(url)) return { type: "123", group: "pan", label: "123" };
    if (/115\.com|115cdn\.com/i.test(url)) return { type: "115", group: "pan", label: "115" };
    if (/yun\.139\.com|caiyun\.139\.com/i.test(url)) return { type: "mobile", group: "pan", label: "移动云" };
    if (/\.(m3u8|mp4|mkv|flv|mov|avi|webm)(\?|#|$)/i.test(url)) return { type: "media", group: "online", label: "在线" };
    return { type: "http", group: "online", label: "链接" };
  }

  function addItem(group, item) {
    if (!item || !item.url) return;
    var list = state.items[group];
    for (var i = 0; i < list.length; i++) {
      if (list[i].url === item.url) return;
    }
    item.index = list.length + 1;
    list.push(item);
  }

  function hostName(url) {
    try { return new URL(url, location.href).hostname.replace(/^www\./, ""); } catch (e) { return ""; }
  }

  // ---------- Image proxy via fm.res() ----------

  function proxyImages() {
    if (state.imagesProxied) return;
    state.imagesProxied = true;
    if (!window.fm || typeof window.fm.res !== "function") return;

    // Proxy lazyload images (data-original attribute)
    var images = document.querySelectorAll("img[data-original], .lazyload[data-original]");
    for (var i = 0; i < images.length; i++) {
      var img = images[i];
      if (img.dataset.fmProxied === "1") continue;
      var src = img.getAttribute("data-original") || img.getAttribute("src") || "";
      if (!src) continue;
      if (!/^https?:\/\//i.test(src)) continue;

      img.dataset.fmProxied = "1";
      var proxiedUrl = "";
      try {
        proxiedUrl = window.fm.res(absoluteUrl(src), {
          headers: { Referer: location.href }
        });
      } catch (e) { continue; }
      if (proxiedUrl) {
        img.setAttribute("data-original", proxiedUrl);
        img.setAttribute("src", proxiedUrl);
        // Also update background-image for lazyload divs
        if (img.style && img.style.backgroundImage) {
          img.style.backgroundImage = "url('" + proxiedUrl + "')";
        }
      }
    }

    // Proxy background-image lazyload elements (a.stui-vodlist__thumb)
    var thumbs = document.querySelectorAll(".stui-vodlist__thumb.lazyload[data-original]");
    for (var j = 0; j < thumbs.length; j++) {
      var thumb = thumbs[j];
      if (thumb.dataset.fmProxied === "1") continue;
      var bgSrc = thumb.getAttribute("data-original") || "";
      if (!bgSrc) continue;
      if (!/^https?:\/\//i.test(bgSrc)) continue;

      thumb.dataset.fmProxied = "1";
      var bgProxied = "";
      try {
        bgProxied = window.fm.res(absoluteUrl(bgSrc), {
          headers: { Referer: location.href }
        });
      } catch (e) { continue; }
      if (bgProxied) {
        thumb.setAttribute("data-original", bgProxied);
        thumb.style.backgroundImage = "url('" + bgProxied + "')";
      }
    }
  }

  // ---------- Parse player_aaaa variable from play page ----------

  function parsePlayerData() {
    if (state.parsed) return;
    state.parsed = true;

    // Try window.player_aaaa first
    if (window.player_aaaa && window.player_aaaa.url) {
      state.playerData = window.player_aaaa;
      log("player_aaaa from window, url:", window.player_aaaa.url);
      return;
    }

    // Fallback: extract from <script> tags inside .stui-player__video
    var container = document.querySelector(CONFIG.playerContainerSelector);
    var scope = container || document;
    var scripts = scope.querySelectorAll("script");
    for (var i = 0; i < scripts.length; i++) {
      var text = scripts[i].textContent || "";
      var startIdx = text.indexOf("var player_aaaa=");
      if (startIdx < 0) continue;
      startIdx = text.indexOf("{", startIdx);
      if (startIdx < 0) continue;

      // Find matching closing brace by counting depth
      var depth = 0;
      var endIdx = -1;
      for (var j = startIdx; j < text.length; j++) {
        if (text.charAt(j) === "{") depth++;
        else if (text.charAt(j) === "}") {
          depth--;
          if (depth === 0) { endIdx = j; break; }
        }
      }
      if (endIdx < 0) continue;

      var ppStr = text.substring(startIdx, endIdx + 1);
      try {
        state.playerData = JSON.parse(ppStr);
        log("player_aaaa extracted (JSON), url:", state.playerData.url);
        return;
      } catch (e) {
        try {
          state.playerData = Function("return " + ppStr)();
          log("player_aaaa extracted (eval), url:", state.playerData.url);
          return;
        } catch (e2) {
          log("player_aaaa parse failed");
        }
      }
    }
    log("player_aaaa not found");
  }

  // ---------- Collect online items ----------

  function collectOnlineItems() {
    state.items.online = [];

    if (state.playerData && state.playerData.url) {
      var url = state.playerData.url;
      // The URL may be escaped with \/ - unescape it
      url = url.replace(/\\\//g, "/");
      var from = state.playerData.from || "";
      var vodName = state.playerData.vod_data && state.playerData.vod_data.vod_name || pageTitle();

      addItem("online", {
        url: absoluteUrl(url),
        type: "media",
        badge: "当前",
        title: from ? ("线路: " + from) : "在线播放",
        subtitle: vodName + " · " + hostName(url),
        source: "player-data"
      });

      // Also add next episode if available
      if (state.playerData.url_next) {
        var urlNext = state.playerData.url_next.replace(/\\\//g, "/");
        if (urlNext) {
          addItem("online", {
            url: absoluteUrl(urlNext),
            type: "media",
            badge: "下一集",
            title: "下一集",
            subtitle: hostName(urlNext),
            source: "player-data-next"
          });
        }
      }
    }

    // Fallback: get URL from iframe src if it contains a parse URL
    if (state.items.online.length === 0) {
      var iframe = document.querySelector(CONFIG.playerIframeSelector);
      if (iframe) {
        var iframeSrc = iframe.getAttribute("src") || "";
        // Parse URL format: https://jx.xxx.com/dplayer/?url=https://cdn.xxx/video.m3u8
        var urlMatch = iframeSrc.match(/[?&]url=([^&]+)/);
        if (urlMatch) {
          var extractedUrl = decodeURIComponent(urlMatch[1]);
          addItem("online", {
            url: absoluteUrl(extractedUrl),
            type: "media",
            badge: "当前",
            title: "在线播放",
            subtitle: hostName(extractedUrl),
            source: "iframe-parse"
          });
        }
      }
    }
  }

  // ---------- Play item ----------

  async function playItem(group, index) {
    var item = state.items[group] && state.items[group][index];
    if (!item) return;

    var sdk = await whenFm();
    var title = pageTitle() + " · " + item.title;
    setBusy(item, true);

    try {
      log("play", group, item.type, item.title, item.url);

      if (item.type === "media") {
        return sdk.play(item.url, title, {
          headers: { Referer: location.href },
          credentials: "include"
        });
      }

      return sdk.pan.play({
        type: item.type,
        url: item.url,
        title: title
      });
    } catch (error) {
      log("play failed", error && (error.stack || error.message) || error);
      toast("调用原生播放失败");
    } finally {
      setBusy(item, false);
    }
  }

  function setBusy(item, busy) {
    item.busy = busy;
    render();
  }

  // ---------- Render panel ----------

  function render() {
    var panel = document.getElementById(CONFIG.panelId);
    if (!panel) {
      panel = document.createElement("section");
      panel.id = CONFIG.panelId;
      panel.setAttribute("aria-label", "BDTV 播放列表");

      var playerContainer = document.querySelector(CONFIG.playerContainerSelector);
      if (playerContainer && playerContainer.parentNode) {
        playerContainer.parentNode.insertBefore(panel, playerContainer.nextSibling);
      } else {
        var main = document.querySelector(".stui-content") || document.querySelector(".stui-main") || document.querySelector("main");
        if (main) main.insertBefore(panel, main.firstChild);
        else document.body.insertBefore(panel, document.body.firstChild);
      }
    }

    var activeItems = state.items[state.activeTab] || [];
    var total = state.items.online.length;

    panel.innerHTML = ""
      + "<div class='fm-bdtv-head'>"
      + "  <div>"
      + "    <div class='fm-bdtv-kicker'>BDTV</div>"
      + "    <div class='fm-bdtv-title'>" + escapeHtml(pageTitle()) + "</div>"
      + "  </div>"
      + "  <div class='fm-bdtv-count'>" + total + " 条线路</div>"
      + "</div>"
      + "<div class='fm-bdtv-list'>"
      + (activeItems.length ? activeItems.map(rowHtml).join("") : emptyHtml())
      + "</div>";
  }

  function rowHtml(item, index) {
    var busy = item.busy ? " is-busy" : "";
    var subtitle = item.subtitle ? "<span class='fm-bdtv-sub'>" + escapeHtml(item.subtitle) + "</span>" : "";
    return "<button type='button' class='fm-bdtv-row" + busy + "' data-fm-group='" + (state.activeTab) + "' data-fm-index='" + index + "'>"
      + "<span class='fm-bdtv-badge'>" + escapeHtml(item.badge || "") + "</span>"
      + "<span class='fm-bdtv-main'><span class='fm-bdtv-name'>" + escapeHtml(item.title) + "</span>" + subtitle + "</span>"
      + "<span class='fm-bdtv-action'>" + (item.busy ? "..." : "播放") + "</span>"
      + "</button>";
  }

  function emptyHtml() {
    return "<div class='fm-bdtv-empty'>暂无可播放线路</div>";
  }

  // ---------- Panel click handler ----------

  function onPanelClick(event) {
    var row = event.target.closest("[data-fm-group][data-fm-index]");
    if (!row) return;
    event.preventDefault();
    event.stopPropagation();
    playItem(row.getAttribute("data-fm-group"), Number(row.getAttribute("data-fm-index")));
  }

  // ---------- Intercept episode clicks on detail page ----------

  function interceptClicks(event) {
    // On detail page: intercept episode clicks to navigate to play page
    // (we handle play on the play page itself)
    // On play page: no need to intercept, our panel handles it

    // On play page: intercept any remaining play links
    if (pageType() === "play") {
      var epLink = event.target.closest(CONFIG.episodeSelector);
      if (epLink) {
        var href = epLink.getAttribute("href") || "";
        if (!href) return;
        // Let the navigation happen - we'll parse the new page
        return;
      }
    }
  }

  // ---------- Page enhancement ----------

  function enhancePage() {
    document.documentElement.classList.add("fm-bdtv-enhanced");
    enhanceHeader();
    var type = pageType();
    if (type === "list") {
      enhanceListPage();
    } else if (type === "detail") {
      enhanceDetailPage();
    } else if (type === "play") {
      enhancePlayPage();
    }
    enhanceFocusable();
  }

  function enhanceHeader() {
    var header = document.querySelector(".stui-header");
    if (header) header.classList.add("fm-bdtv-head-bar");
  }

  function enhanceListPage() {
    ensureSearchBar();
    enhanceMovieCards();
    proxyImages();
  }

  function ensureSearchBar() {
    if (document.getElementById(CONFIG.searchId)) return;

    // The site already has a search bar, just enhance it
    var searchForm = document.querySelector("form#search");
    if (searchForm) {
      searchForm.classList.add("fm-bdtv-search-form");
      var input = searchForm.querySelector("input.mac_wd");
      if (input) input.classList.add("fm-bdtv-search-input");
    }
  }

  function enhanceMovieCards() {
    var items = document.querySelectorAll(CONFIG.itemSelector);
    for (var i = 0; i < items.length; i++) {
      var item = items[i];
      if (item.dataset.fmEnhanced === "1") continue;
      item.dataset.fmEnhanced = "1";
      item.classList.add("fm-bdtv-item");

      var thumb = item.querySelector(CONFIG.itemThumbSelector);
      if (thumb) {
        thumb.classList.add("fm-bdtv-thumb");
        thumb.setAttribute("tabindex", "0");
      }

      var title = item.querySelector(CONFIG.itemTitleSelector);
      if (title) title.classList.add("fm-bdtv-item-title");
    }
  }

  function enhanceDetailPage() {
    proxyImages();

    // Style the playlist area
    var playlist = document.querySelector(CONFIG.playlistContainerSelector);
    if (playlist) playlist.classList.add("fm-bdtv-playlist");

    // Style detail info
    var detailInfo = document.querySelector(CONFIG.detailInfoSelector);
    if (detailInfo) detailInfo.classList.add("fm-bdtv-detail-info");

    // Hide the "立即播放" button (we intercept episode clicks instead)
    var playBtn = document.querySelector(".play-btn");
    if (playBtn) playBtn.classList.add("fm-bdtv-hide");
  }

  function enhancePlayPage() {
    // Hide original iframe player (we replace with our panel)
    var playerContainer = document.querySelector(CONFIG.playerContainerSelector);
    if (playerContainer) playerContainer.classList.add("fm-bdtv-hide");

    // Keep episode list visible but style it
    var playlist = document.querySelector(CONFIG.playlistContainerSelector);
    if (playlist) playlist.classList.add("fm-bdtv-playlist");

    // Parse player data and build panel
    parsePlayerData();
    collectOnlineItems();
    render();
  }

  function enhanceFocusable() {
    var selectors = [
      CONFIG.itemThumbSelector,
      CONFIG.episodeSelector,
      "button",
      "input",
      "select",
      "a[href]"
    ];
    var nodes = document.querySelectorAll(selectors.join(","));
    for (var i = 0; i < nodes.length; i++) {
      var node = nodes[i];
      if (node.closest(".fm-bdtv-hide")) continue;
      if (!node.hasAttribute("tabindex") && !/^(A|BUTTON|INPUT|SELECT|TEXTAREA)$/i.test(node.tagName)) {
        node.setAttribute("tabindex", "0");
      }
    }
  }

  function onKeyboardActivate(event) {
    if (event.key !== "Enter" && event.key !== " " && event.keyCode !== 13 && event.keyCode !== 23) return;
    var target = event.target;
    if (target.closest(".stui-content__playlist") || target.closest(".stui-vodlist")) {
      event.preventDefault();
      target.click();
    }
  }

  // ---------- Scan loop ----------

  function scan() {
    enhancePage();
  }

  function scheduleScan() {
    clearTimeout(scheduleScan.timer);
    scheduleScan.timer = setTimeout(scan, CONFIG.scanDelay);
  }

  function installObserver() {
    new MutationObserver(function (mutations) {
      for (var i = 0; i < mutations.length; i++) {
        if (!isOwnMutation(mutations[i])) {
          scheduleScan();
          return;
        }
      }
    }).observe(document.documentElement, { childList: true, subtree: true });
  }

  function isOwnMutation(mutation) {
    var panel = document.getElementById(CONFIG.panelId);
    if (!panel) return false;
    if (panel.contains(mutation.target)) return true;
    var nodes = Array.prototype.slice.call(mutation.addedNodes || []).concat(Array.prototype.slice.call(mutation.removedNodes || []));
    for (var i = 0; i < nodes.length; i++) {
      var node = nodes[i];
      if (node === panel || (node.nodeType === 1 && panel.contains(node))) return true;
    }
    return false;
  }

  // ---------- Style injection ----------

  function installStyle() {
    var css = ""
      // Base
      + ".fm-bdtv-enhanced { -webkit-tap-highlight-color: transparent; }"
      + ".fm-bdtv-hide { display: none !important; }"

      // Header
      + ".fm-bdtv-head-bar {"
      + "  position: sticky !important;"
      + "  top: 0;"
      + "  z-index: 80;"
      + "}"

      // Search bar enhancement
      + ".fm-bdtv-search-form input.mac_wd, .fm-bdtv-search-input {"
      + "  min-height: 40px;"
      + "  border: 1px solid #0f766e;"
      + "  border-radius: 6px;"
      + "  background: #f8fafc;"
      + "  color: #111827;"
      + "  padding: 0 12px;"
      + "  font-size: 14px;"
      + "  outline: none;"
      + "  box-sizing: border-box;"
      + "}"

      // Movie cards
      + ".fm-bdtv-item {"
      + "  min-width: 0;"
      + "}"
      + ".fm-bdtv-thumb {"
      + "  position: relative;"
      + "  display: block;"
      + "  overflow: hidden;"
      + "  border-radius: 6px;"
      + "  border: 1px solid #e5e7eb;"
      + "  background: #dbe3ec;"
      + "  transition: transform .15s ease, border-color .15s ease;"
      + "  text-decoration: none !important;"
      + "}"
      // 3:4 aspect ratio via padding-top hack
      + ".fm-bdtv-thumb::before {"
      + "  content: '';"
      + "  display: block;"
      + "  padding-top: 133%;"
      + "}"
      + ".fm-bdtv-thumb img, .fm-bdtv-thumb.lazyload {"
      + "  position: absolute;"
      + "  top: 0; left: 0;"
      + "  width: 100% !important;"
      + "  height: 100% !important;"
      + "  object-fit: cover;"
      + "}"
      + ".fm-bdtv-thumb .pic-text {"
      + "  position: absolute;"
      + "  bottom: 0; left: 0; right: 0;"
      + "  padding: 4px 8px;"
      + "  background: linear-gradient(transparent, rgba(0,0,0,.7));"
      + "  color: #fff;"
      + "  font-size: 11px;"
      + "  z-index: 2;"
      + "}"
      + ".fm-bdtv-thumb .play {"
      + "  display: none !important;"
      + "}"
      + ".fm-bdtv-item-title {"
      + "  font-size: 14px;"
      + "  font-weight: 700;"
      + "  line-height: 1.35;"
      + "  white-space: nowrap;"
      + "  overflow: hidden;"
      + "  text-overflow: ellipsis;"
      + "  color: #111827 !important;"
      + "  text-decoration: none !important;"
      + "}"

      // Detail page
      + ".fm-bdtv-detail-info {"
      + "  max-width: 800px;"
      + "}"
      + ".fm-bdtv-detail-info h1.title {"
      + "  font-size: 22px;"
      + "  font-weight: 800;"
      + "}"

      // Playlist / episode buttons
      + ".fm-bdtv-playlist {"
      + "  max-width: 800px;"
      + "  margin: 0 auto 16px;"
      + "}"
      + ".fm-bdtv-playlist .stui-content__playlist a.btn {"
      + "  min-width: 44px;"
      + "  min-height: 44px;"
      + "  display: inline-flex;"
      + "  align-items: center;"
      + "  justify-content: center;"
      + "  border: 1px solid #e2e8f0;"
      + "  border-radius: 6px;"
      + "  margin: 3px;"
      + "  padding: 0 10px;"
      + "  font-size: 13px;"
      + "  color: #334155;"
      + "  text-decoration: none;"
      + "  background: #fff;"
      + "}"
      + ".fm-bdtv-playlist .stui-content__playlist a.btn:hover, "
      + ".fm-bdtv-playlist .stui-content__playlist a.btn.active {"
      + "  border-color: #0f766e;"
      + "  background: #0f766e;"
      + "  color: #fff;"
      + "}"

      // Playback panel
      + "#" + CONFIG.panelId + " {"
      + "  max-width: 800px;"
      + "  margin: 0 auto 16px;"
      + "  padding: 14px;"
      + "  border: 1px solid rgba(15, 118, 110, .22);"
      + "  border-radius: 8px;"
      + "  background: #fff;"
      + "  color: #111827;"
      + "  box-shadow: 0 8px 22px rgba(15, 23, 42, .08);"
      + "}"
      + "#" + CONFIG.panelId + " * { box-sizing: border-box; }"
      + ".fm-bdtv-head {"
      + "  display: flex;"
      + "  align-items: flex-start;"
      + "  justify-content: space-between;"
      + "  margin-bottom: 12px;"
      + "}"
      + ".fm-bdtv-kicker {"
      + "  color: #0f766e;"
      + "  font-size: 12px;"
      + "  font-weight: 800;"
      + "  letter-spacing: .08em;"
      + "  text-transform: uppercase;"
      + "}"
      + ".fm-bdtv-title {"
      + "  margin-top: 2px;"
      + "  font-size: 17px;"
      + "  line-height: 1.35;"
      + "  font-weight: 800;"
      + "}"
      + ".fm-bdtv-count {"
      + "  min-width: 34px;"
      + "  height: 30px;"
      + "  padding: 0 10px;"
      + "  border-radius: 999px;"
      + "  background: #eef2ff;"
      + "  color: #4338ca;"
      + "  display: inline-flex;"
      + "  align-items: center;"
      + "  justify-content: center;"
      + "  font-size: 13px;"
      + "  font-weight: 800;"
      + "  white-space: nowrap;"
      + "}"
      + ".fm-bdtv-list {"
      + "  display: flex;"
      + "  flex-direction: column;"
      + "}"
      + ".fm-bdtv-row {"
      + "  width: 100%;"
      + "  min-height: 54px;"
      + "  border: 1px solid #e2e8f0;"
      + "  border-radius: 8px;"
      + "  background: #fff;"
      + "  color: #111827;"
      + "  display: grid;"
      + "  grid-template-columns: auto minmax(0, 1fr) auto;"
      + "  align-items: center;"
      + "  margin-top: 8px;"
      + "  padding: 9px 10px;"
      + "  text-align: left;"
      + "  cursor: pointer;"
      + "}"
      + ".fm-bdtv-row:active { transform: translateY(1px); }"
      + ".fm-bdtv-row.is-busy { opacity: .68; }"
      + ".fm-bdtv-badge {"
      + "  min-width: 42px;"
      + "  height: 28px;"
      + "  padding: 0 8px;"
      + "  border-radius: 999px;"
      + "  background: #ecfeff;"
      + "  color: #0e7490;"
      + "  display: inline-flex;"
      + "  align-items: center;"
      + "  justify-content: center;"
      + "  font-size: 12px;"
      + "  font-weight: 800;"
      + "  white-space: nowrap;"
      + "}"
      + ".fm-bdtv-main {"
      + "  min-width: 0;"
      + "  display: flex;"
      + "  flex-direction: column;"
      + "  margin: 0 10px;"
      + "}"
      + ".fm-bdtv-name {"
      + "  overflow: hidden;"
      + "  text-overflow: ellipsis;"
      + "  white-space: nowrap;"
      + "  font-size: 14px;"
      + "  line-height: 1.35;"
      + "  font-weight: 800;"
      + "}"
      + ".fm-bdtv-sub {"
      + "  overflow: hidden;"
      + "  text-overflow: ellipsis;"
      + "  white-space: nowrap;"
      + "  color: #64748b;"
      + "  font-size: 12px;"
      + "  line-height: 1.3;"
      + "}"
      + ".fm-bdtv-action {"
      + "  min-width: 42px;"
      + "  color: #be123c;"
      + "  font-size: 13px;"
      + "  font-weight: 900;"
      + "  text-align: right;"
      + "}"
      + ".fm-bdtv-empty {"
      + "  min-height: 56px;"
      + "  border: 1px dashed #cbd5e1;"
      + "  border-radius: 8px;"
      + "  color: #64748b;"
      + "  display: flex;"
      + "  align-items: center;"
      + "  justify-content: center;"
      + "  font-size: 14px;"
      + "  font-weight: 700;"
      + "  margin-top: 8px;"
      + "}"

      // Focus styles (TV compatible, no :focus-visible)
      + ".fm-bdtv-enhanced a:focus,"
      + ".fm-bdtv-enhanced button:focus,"
      + ".fm-bdtv-enhanced [tabindex]:focus {"
      + "  outline: 3px solid #14b8a6 !important;"
      + "  outline-offset: 2px !important;"
      + "}"
      + ".fm-bdtv-thumb:focus {"
      + "  border-color: #14b8a6 !important;"
      + "  transform: translateY(-2px);"
      + "  box-shadow: 0 10px 28px rgba(15, 118, 110, .20) !important;"
      + "}"
      + ".fm-bdtv-row:focus {"
      + "  border-color: #14b8a6 !important;"
      + "  background: #f0fdfa !important;"
      + "}"

      // Responsive
      + "@media (max-width: 640px) {"
      + "  #" + CONFIG.panelId + " {"
      + "    margin-left: -2px;"
      + "    margin-right: -2px;"
      + "    border-radius: 0;"
      + "    box-shadow: none;"
      + "  }"
      + "  .fm-bdtv-row {"
      + "    grid-template-columns: auto minmax(0, 1fr);"
      + "  }"
      + "  .fm-bdtv-action {"
      + "    grid-column: 2;"
      + "    text-align: left;"
      + "    margin-top: -2px;"
      + "  }"
      + "}"

      // Dark mode support
      + ".dark .fm-bdtv-thumb {"
      + "  border-color: #26313c;"
      + "  background: #121820;"
      + "}"
      + ".dark .fm-bdtv-item-title { color: #f8fafc !important; }"
      + ".dark #" + CONFIG.panelId + " {"
      + "  border-color: rgba(20, 184, 166, .28);"
      + "  background: #101214;"
      + "  color: #f8fafc;"
      + "}"
      + ".dark .fm-bdtv-kicker { color: #2dd4bf; }"
      + ".dark .fm-bdtv-row {"
      + "  border-color: #2a343f;"
      + "  background: #15191e;"
      + "  color: #f8fafc;"
      + "}"
      + ".dark .fm-bdtv-badge {"
      + "  background: rgba(45, 212, 191, .13);"
      + "  color: #5eead4;"
      + "}"
      + ".dark .fm-bdtv-sub { color: #94a3b8; }"
      + ".dark .fm-bdtv-action { color: #fb7185; }"
      + ".dark .fm-bdtv-empty {"
      + "  border-color: #334155;"
      + "  color: #94a3b8;"
      + "}"
      + ".dark .fm-bdtv-row:focus { background: #0f1a1a !important; }"
      + ".dark .fm-bdtv-playlist .stui-content__playlist a.btn {"
      + "  border-color: #334155;"
      + "  color: #d1d5db;"
      + "  background: #15191e;"
      + "}"
      + ".dark .fm-bdtv-playlist .stui-content__playlist a.btn:hover, "
      + ".dark .fm-bdtv-playlist .stui-content__playlist a.btn.active {"
      + "  border-color: #14b8a6;"
      + "  background: #0f766e;"
      + "  color: #fff;"
      + "}";

    if (typeof GM_addStyle === "function") GM_addStyle(css);
    else {
      var style = document.createElement("style");
      style.textContent = css;
      (document.head || document.documentElement).appendChild(style);
    }
  }

  // ---------- Boot ----------

  ready(function () {
    installStyle();
    document.addEventListener("click", interceptClicks, true);
    document.addEventListener("click", onPanelClick, true);
    document.addEventListener("keydown", onKeyboardActivate, true);
    installObserver();
    scan();
    log("ready", location.href, "type:", pageType());
  });

  window.addEventListener("fmurlchange", function () {
    state.parsed = false;
    state.playerData = null;
    state.items.online = [];
    state.imagesProxied = false;
    scheduleScan();
  });
})();
