// WebHome extension for https://a123tv.com/
// Optimized behavior:
// - Build one clean native playback panel on the detail/play page.
// - Parse embedded pp.la[] data to extract all route m3u8 URLs.
// - Group resources into 在线播放 (all routes are online m3u8).
// - Click any row to call fm.play() directly with the resolved m3u8 URL.
// - Proxy images via fm.res() for WebView compatibility.
// - Simplify mobile pages into a search-first movie UI with TV focus states.
// - Hide original player and route list, replace with clean App-play panel.
(function () {
  var CONFIG = {
    panelId: "fm-a123tv-panel",
    searchId: "fm-a123tv-search",
    name: "fm-a123tv",
    titleSelector: ".w4-bread li.on h1, .w4-bread li.on",
    detailSelector: ".w4-video, .w4-episode, .w4-line",
    itemWrapSelector: ".w4-item-wrap",
    itemSelector: "a.w4-item",
    episodeSelector: ".w4-episode-list a",
    lineSelector: "a.w4-line-item",
    playerSelector: ".awp",
    imgSelector: "a.w4-item img[data-src], .w4-line-cover img[data-src]",
    scanDelay: 200
  };

  var state = {
    activeTab: "online",
    items: {
      online: []
    },
    parsed: false,
    ppData: null,
    imagesProxied: false
  };

  function log() {
    var args = Array.prototype.slice.call(arguments);
    if (typeof GM_log === "function") GM_log.apply(null, args);
    else console.log.apply(console, ["[fm-a123tv]"].concat(args));
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
    var match = document.title.match(/《(.+?)》/);
    if (match) return match[1];
    return cleanText(document.title.replace(/\s*[-–—].*$/, "")) || location.href;
  }

  function isDetailPage() {
    return !!document.querySelector(CONFIG.detailSelector);
  }

  function absoluteUrl(url) {
    if (!url || url === "#" || /^javascript:/i.test(url)) return "";
    if (/^(magnet:|ed2k:|thunder:)/i.test(url)) return url;
    // Handle protocol-relative URLs
    if (/^\/\//i.test(url)) {
      try {
        return new URL(url, location.href).href;
      } catch (e) {
        return "https:" + url;
      }
    }
    try {
      return new URL(url, location.href).href;
    } catch (e) {
      return url;
    }
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

  // ---------- Image proxy via fm.res() ----------

  function proxyImages() {
    if (state.imagesProxied) return;
    state.imagesProxied = true;

    // Only proxy if fm.res is available (runs in WebHome WebView)
    if (!window.fm || typeof window.fm.res !== "function") return;

    var images = document.querySelectorAll("img[data-src]");
    for (var i = 0; i < images.length; i++) {
      var img = images[i];
      if (img.dataset.fmProxied === "1") continue;
      var src = img.getAttribute("data-src") || img.getAttribute("src") || "";
      if (!src) continue;
      // Only proxy external images (protocol-relative or full URL)
      if (!/^\/\//i.test(src) && /^https?:\/\//i.test(src) && /^https?:\/\/(i1\.)?a123tv\.com/i.test(src)) {
        // Same-origin images, no need to proxy
        continue;
      }
      if (!/^\/\//i.test(src) && !/^https?:\/\//i.test(src)) continue;

      img.dataset.fmProxied = "1";
      var proxiedUrl = "";
      try {
        proxiedUrl = window.fm.res(absoluteUrl(src));
      } catch (e) {
        // fm.res failed, skip
        continue;
      }
      if (proxiedUrl) {
        img.setAttribute("data-src", proxiedUrl);
        img.setAttribute("src", proxiedUrl);
        img.removeAttribute("data-loaded");
      }
    }
  }

  // ---------- Parse pp variable from page scripts ----------

  function parsePpData() {
    if (state.parsed) return;
    state.parsed = true;

    // Try to read window.pp first (set by site's inline script)
    if (window.pp && window.pp.la && Array.isArray(window.pp.la)) {
      state.ppData = window.pp;
      log("pp from window, routes:", window.pp.la.length);
      return;
    }

    // Fallback: extract from <script> tags
    // pp is defined as: var pp={...}; inside an inline <script>
    // Use greedy match to handle nested objects/arrays
    var scripts = document.querySelectorAll("script:not([src])");
    for (var i = 0; i < scripts.length; i++) {
      var text = scripts[i].textContent || "";
      // Find "var pp=" and match to the last "};"
      var startIdx = text.indexOf("var pp=");
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
          if (depth === 0) {
            endIdx = j;
            break;
          }
        }
      }
      if (endIdx < 0) continue;

      var ppStr = text.substring(startIdx, endIdx + 1);
      try {
        state.ppData = JSON.parse(ppStr);
        log("pp extracted from script (JSON), routes:", state.ppData.la ? state.ppData.la.length : 0);
        return;
      } catch (e) {
        try {
          state.ppData = Function("return " + ppStr)();
          log("pp extracted from script (eval), routes:", state.ppData.la ? state.ppData.la.length : 0);
          return;
        } catch (e2) {
          log("pp parse failed, trying next script");
        }
      }
    }
    log("pp not found in any script");
  }

  // ---------- Collect online items from pp.la ----------

  function collectOnlineItems() {
    state.items.online = [];

    // Method 1: From pp.la data
    if (state.ppData && state.ppData.la) {
      var la = state.ppData.la;
      var title = pageTitle();
      for (var i = 0; i < la.length; i++) {
        var route = la[i];
        if (!Array.isArray(route) || route.length < 5) continue;
        var routeId = String(route[0] || "");
        var routeName = String(route[1] || ("线路" + (i + 1)));
        var episodeCount = Number(route[2]) || 1;
        var m3u8Url = String(route[4] || "");
        if (!m3u8Url) continue;

        // Mark current active route
        var badge = "在线";
        var player = document.querySelector(CONFIG.playerSelector);
        if (player) {
          var playerSrc = player.getAttribute("data-src") || "";
          if (playerSrc === m3u8Url || (routeId && playerSrc.indexOf(routeId) >= 0)) {
            badge = "当前";
          }
        }

        addItem("online", {
          url: absoluteUrl(m3u8Url),
          type: "media",
          badge: badge,
          title: routeName,
          subtitle: episodeCount > 1 ? (episodeCount + "集") : ("单集 · " + hostName(m3u8Url)),
          source: "pp-data",
          routeId: routeId
        });
      }
    }

    // Method 2: Fallback - collect from line items in DOM
    if (state.items.online.length === 0) {
      var lineItems = document.querySelectorAll(CONFIG.lineSelector);
      for (var j = 0; j < lineItems.length; j++) {
        var item = lineItems[j];
        var href = item.getAttribute("href") || "";
        var lineTitle = item.getAttribute("title") || cleanText(item.textContent);
        if (!href) continue;
        addItem("online", {
          url: absoluteUrl(href),
          type: "http",
          badge: "线路",
          title: lineTitle || ("线路" + (j + 1)),
          subtitle: "点击进入线路页",
          source: "line-dom"
        });
      }
    }

    // Method 3: Fallback - get current player m3u8
    if (state.items.online.length === 0) {
      var playerEl = document.querySelector(CONFIG.playerSelector);
      if (playerEl) {
        var src = playerEl.getAttribute("data-src") || "";
        if (src) {
          addItem("online", {
            url: absoluteUrl(src),
            type: "media",
            badge: "当前",
            title: "当前线路",
            subtitle: hostName(src),
            source: "player-data"
          });
        }
      }
    }
  }

  function hostName(url) {
    try {
      return new URL(url, location.href).hostname.replace(/^www\./, "");
    } catch (e) {
      return "";
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
        // Direct m3u8 playback with Referer header
        return sdk.play(item.url, title, {
          headers: { Referer: location.href },
          credentials: "include"
        });
      }

      if (item.type === "http" && item.source === "line-dom") {
        // Navigate to the line page and let the extension re-parse
        location.href = item.url;
        return;
      }

      // Generic fallback
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
      panel.setAttribute("aria-label", "A123TV 播放列表");
      var anchor = document.querySelector(".w4-video");
      if (anchor && anchor.parentNode) {
        anchor.parentNode.insertBefore(panel, anchor.nextSibling);
      } else {
        var main = document.querySelector(".w4-main") || document.querySelector("main");
        if (main) main.insertBefore(panel, main.firstChild);
        else document.body.insertBefore(panel, document.body.firstChild);
      }
    }

    var activeItems = state.items[state.activeTab] || [];
    var total = state.items.online.length;

    panel.innerHTML = ""
      + "<div class='fm-a123tv-head'>"
      + "  <div>"
      + "    <div class='fm-a123tv-kicker'>A123TV</div>"
      + "    <div class='fm-a123tv-title'>" + escapeHtml(pageTitle()) + "</div>"
      + "  </div>"
      + "  <div class='fm-a123tv-count'>" + total + " 条线路</div>"
      + "</div>"
      + "<div class='fm-a123tv-list'>"
      + (activeItems.length ? activeItems.map(rowHtml).join("") : emptyHtml())
      + "</div>";
  }

  function rowHtml(item, index) {
    var busy = item.busy ? " is-busy" : "";
    var subtitle = item.subtitle ? "<span class='fm-a123tv-sub'>" + escapeHtml(item.subtitle) + "</span>" : "";
    return "<button type='button' class='fm-a123tv-row" + busy + "' data-fm-group='" + (state.activeTab) + "' data-fm-index='" + index + "'>"
      + "<span class='fm-a123tv-badge'>" + escapeHtml(item.badge || "") + "</span>"
      + "<span class='fm-a123tv-main'><span class='fm-a123tv-name'>" + escapeHtml(item.title) + "</span>" + subtitle + "</span>"
      + "<span class='fm-a123tv-action'>" + (item.busy ? "..." : "播放") + "</span>"
      + "</button>";
  }

  function emptyHtml() {
    return "<div class='fm-a123tv-empty'>暂无可播放线路</div>";
  }

  // ---------- Panel click handler ----------

  function onPanelClick(event) {
    var row = event.target.closest("[data-fm-group][data-fm-index]");
    if (!row) return;
    event.preventDefault();
    event.stopPropagation();
    playItem(row.getAttribute("data-fm-group"), Number(row.getAttribute("data-fm-index")));
  }

  // ---------- Intercept original play clicks ----------

  function interceptClicks(event) {
    // Intercept line item clicks - route to native playback instead
    var lineItem = event.target.closest(CONFIG.lineSelector);
    if (lineItem) {
      var href = lineItem.getAttribute("href") || "";
      if (!href) return;
      // Only intercept if we have pp data with m3u8 URLs
      if (state.ppData && state.ppData.la) {
        var routeId = extractRouteId(href);
        if (routeId) {
          var m3u8 = findM3u8ByRouteId(routeId);
          if (m3u8) {
            event.preventDefault();
            event.stopPropagation();
            event.stopImmediatePropagation();
            var title = pageTitle() + " · " + (lineItem.getAttribute("title") || "线路");
            whenFm().then(function (sdk) {
              return sdk.play(m3u8, title, {
                headers: { Referer: location.href },
                credentials: "include"
              });
            }).catch(function (err) {
              log("line click play failed", err);
              toast("播放失败");
            });
            return;
          }
        }
      }
      // No m3u8 found, let original navigation happen
      return;
    }

    // Intercept episode clicks - try to find matching m3u8
    var epLink = event.target.closest(CONFIG.episodeSelector);
    if (epLink && state.ppData && state.ppData.la) {
      var epHref = epLink.getAttribute("href") || "";
      var epRouteId = extractRouteId(epHref);
      if (epRouteId) {
        var epM3u8 = findM3u8ByRouteId(epRouteId);
        if (epM3u8) {
          event.preventDefault();
          event.stopPropagation();
          event.stopImmediatePropagation();
          var epTitle = pageTitle() + " · " + (epLink.getAttribute("title") || "播放");
          whenFm().then(function (sdk) {
            return sdk.play(epM3u8, epTitle, {
              headers: { Referer: location.href },
              credentials: "include"
            });
          }).catch(function (err) {
            log("episode click play failed", err);
            toast("播放失败");
          });
          return;
        }
      }
    }
  }

  function extractRouteId(url) {
    // URL format: /v/{slug}/{routeId}.html
    var match = url.match(/\/v\/[^\/]+\/([a-z0-9]+)\.html$/i);
    return match ? match[1] : "";
  }

  function findM3u8ByRouteId(routeId) {
    if (!state.ppData || !state.ppData.la || !routeId) return "";
    var la = state.ppData.la;
    for (var i = 0; i < la.length; i++) {
      if (Array.isArray(la[i]) && String(la[i][0]) === routeId && la[i][4]) {
        return String(la[i][4]);
      }
    }
    return "";
  }

  // ---------- Page enhancement ----------

  function enhancePage() {
    document.documentElement.classList.add("fm-a123tv-enhanced");
    enhanceHeader();
    if (!isDetailPage()) {
      enhanceListPage();
    } else {
      enhanceDetailPage();
    }
    enhanceFocusable();
  }

  function enhanceHeader() {
    var header = document.querySelector(".w4-head");
    if (header) header.classList.add("fm-a123tv-head-bar");
  }

  function enhanceListPage() {
    ensureSearchBar();
    enhanceMovieCards();
    proxyImages();
  }

  function ensureSearchBar() {
    if (document.getElementById(CONFIG.searchId)) {
      syncSearchMeta();
      return;
    }

    var host = document.createElement("section");
    host.id = CONFIG.searchId;
    host.innerHTML = ""
      + "<form class='fm-a123tv-search-form' action='" + escapeHtml(location.origin + "/s/") + "' method='get'>"
      + "  <div class='fm-a123tv-search-label'>A123TV</div>"
      + "  <div class='fm-a123tv-search-row'>"
      + "    <input class='fm-a123tv-search-input' type='search' name='wd' placeholder='搜索电影、剧集、动漫' autocomplete='off' maxlength='10'>"
      + "    <button class='fm-a123tv-search-button' type='submit'>搜索</button>"
      + "  </div>"
      + "  <div class='fm-a123tv-search-meta'></div>"
      + "</form>";

    var main = document.querySelector(".w4-main") || document.querySelector("main");
    if (main) main.insertBefore(host, main.firstChild);
    else document.body.insertBefore(host, document.body.firstChild);

    host.addEventListener("submit", function (event) {
      var input = host.querySelector("input[name='wd']");
      var keyword = cleanText(input && input.value);
      if (!keyword) {
        event.preventDefault();
        if (input) input.focus();
        return;
      }
      event.preventDefault();
      location.href = location.origin + "/s/" + encodeURIComponent(keyword) + ".html";
    });

    syncSearchMeta();
  }

  function syncSearchMeta() {
    var host = document.getElementById(CONFIG.searchId);
    if (!host) return;
    var meta = host.querySelector(".fm-a123tv-search-meta");
    var path = location.pathname;
    var searchMatch = path.match(/^\/s\/(.+?)(?:\/p(\d+))?\.html$/);
    if (meta) {
      if (searchMatch) {
        var kw = decodeURIComponent(searchMatch[1]);
        var page = searchMatch[2] ? (" 第" + searchMatch[2] + "页") : "";
        meta.textContent = "搜索 \"" + kw + "\" 的结果" + page;
      } else {
        meta.textContent = "最新影视资源";
      }
    }
  }

  function enhanceMovieCards() {
    // Target .w4-item-wrap containers (the actual grid children)
    var wraps = document.querySelectorAll(CONFIG.itemWrapSelector);
    for (var i = 0; i < wraps.length; i++) {
      var wrap = wraps[i];
      if (wrap.dataset.fmEnhanced === "1") continue;
      wrap.dataset.fmEnhanced = "1";
      wrap.classList.add("fm-a123tv-item-wrap");

      var card = wrap.querySelector(CONFIG.itemSelector);
      if (card) {
        card.classList.add("fm-a123tv-card");
        card.setAttribute("tabindex", "0");

        var poster = card.querySelector(".w4-item-cover");
        if (poster) poster.classList.add("fm-a123tv-card-poster");

        var info = card.querySelector(".w4-item-info");
        if (info) info.classList.add("fm-a123tv-card-info");
      }
    }
  }

  function enhanceDetailPage() {
    // Hide original player area (we replace it with our panel)
    var video = document.querySelector(".w4-video");
    if (video) video.classList.add("fm-a123tv-hide");

    // Hide original line list (we show routes in our panel)
    var lineSection = document.querySelector(".w4-line");
    if (lineSection && lineSection.previousElementSibling) {
      var lineHeading = lineSection.previousElementSibling;
      if (lineHeading && /切换线路/.test(cleanText(lineHeading.textContent))) {
        lineHeading.classList.add("fm-a123tv-hide");
      }
    }
    if (lineSection) lineSection.classList.add("fm-a123tv-hide");

    // Keep episode list visible but style it
    var episode = document.querySelector(".w4-episode");
    if (episode) episode.classList.add("fm-a123tv-episode");

    // Style related recommendation heading
    var meta2s = document.querySelectorAll(".w4-meta2");
    for (var i = 0; i < meta2s.length; i++) {
      var text = cleanText(meta2s[i].textContent);
      if (/相关推荐/.test(text)) {
        meta2s[i].classList.add("fm-a123tv-meta2");
      }
    }
  }

  function enhanceFocusable() {
    var selectors = [
      CONFIG.itemSelector,
      CONFIG.episodeSelector,
      CONFIG.lineSelector,
      "button",
      "input",
      "select",
      "a[href]"
    ];
    var nodes = document.querySelectorAll(selectors.join(","));
    for (var i = 0; i < nodes.length; i++) {
      var node = nodes[i];
      if (node.closest(".fm-a123tv-hide")) continue;
      if (!node.hasAttribute("tabindex") && !/^(A|BUTTON|INPUT|SELECT|TEXTAREA)$/i.test(node.tagName)) {
        node.setAttribute("tabindex", "0");
      }
    }
  }

  function onKeyboardActivate(event) {
    if (event.key !== "Enter" && event.key !== " " && event.keyCode !== 13 && event.keyCode !== 23) return;
    var target = event.target;
    if (target.closest(".w4-episode-list") || target.closest(".w4-line")) {
      event.preventDefault();
      target.click();
    }
  }

  // ---------- Scan loop ----------

  function scan() {
    enhancePage();
    if (!isDetailPage()) return;
    parsePpData();
    collectOnlineItems();
    render();
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
      + ".fm-a123tv-enhanced { -webkit-tap-highlight-color: transparent; }"
      + ".fm-a123tv-hide { display: none !important; }"

      // Header
      + ".fm-a123tv-head-bar {"
      + "  max-width: 1228px !important;"
      + "  margin: 0 auto !important;"
      + "  position: sticky !important;"
      + "  top: 0;"
      + "  z-index: 80;"
      + "}"

      // Search bar
      + "#" + CONFIG.searchId + " {"
      + "  max-width: 1228px;"
      + "  margin: 12px auto 14px;"
      + "  padding: 0 14px;"
      + "}"
      + ".fm-a123tv-search-form {"
      + "  padding: 12px;"
      + "  border: 1px solid #e2e8f0;"
      + "  border-radius: 8px;"
      + "  background: #fff;"
      + "  box-shadow: 0 8px 24px rgba(15, 23, 42, .07);"
      + "}"
      + ".fm-a123tv-search-label {"
      + "  color: #0f766e;"
      + "  font-size: 13px;"
      + "  font-weight: 900;"
      + "  letter-spacing: .08em;"
      + "}"
      + ".fm-a123tv-search-row {"
      + "  display: grid;"
      + "  grid-template-columns: minmax(0, 1fr) auto;"
      + "  margin-top: 9px;"
      + "}"
      + ".fm-a123tv-search-input {"
      + "  width: 100%;"
      + "  min-width: 0;"
      + "  min-height: 48px;"
      + "  border: 1px solid #cbd5e1;"
      + "  border-radius: 8px;"
      + "  background: #f8fafc;"
      + "  color: #111827;"
      + "  padding: 0 13px;"
      + "  font-size: 15px;"
      + "  outline: none;"
      + "  box-sizing: border-box;"
      + "}"
      + ".fm-a123tv-search-button {"
      + "  min-width: 72px;"
      + "  min-height: 48px;"
      + "  border: 1px solid #0f766e;"
      + "  border-radius: 8px;"
      + "  background: #0f766e;"
      + "  color: #fff;"
      + "  padding: 0 14px;"
      + "  font-size: 15px;"
      + "  font-weight: 900;"
      + "  margin-left: 8px;"
      + "}"
      + ".fm-a123tv-search-meta {"
      + "  min-height: 18px;"
      + "  margin-top: 8px;"
      + "  color: #64748b;"
      + "  font-size: 12px;"
      + "  line-height: 1.45;"
      + "}"

      // Movie cards grid - target .w4-item-wrap as grid items
      + ".fm-a123tv-enhanced .w4-list {"
      + "  display: grid !important;"
      + "  grid-template-columns: repeat(2, minmax(0, 1fr)) !important;"
      + "  margin: 0 auto 20px !important;"
      + "  max-width: 1228px;"
      + "  padding: 0 14px;"
      + "}"
      + ".fm-a123tv-item-wrap {"
      + "  min-width: 0;"
      + "}"
      + ".fm-a123tv-card {"
      + "  position: relative;"
      + "  min-width: 0;"
      + "  border: 1px solid #e5e7eb;"
      + "  border-radius: 8px;"
      + "  background: #fff;"
      + "  overflow: hidden;"
      + "  transition: transform .15s ease, border-color .15s ease;"
      + "  text-decoration: none !important;"
      + "  color: inherit !important;"
      + "  display: block;"
      + "}"
      + ".fm-a123tv-card-poster {"
      + "  position: relative;"
      + "  overflow: hidden;"
      + "  background: #dbe3ec;"
      + "}"
      // Use padding-top hack for 3:2 aspect ratio (old WebView safe)
      + ".fm-a123tv-card-poster::before {"
      + "  content: '';"
      + "  display: block;"
      + "  padding-top: 133%;"
      + "}"
      + ".fm-a123tv-card-poster img {"
      + "  position: absolute;"
      + "  top: 0; left: 0;"
      + "  width: 100% !important;"
      + "  height: 100% !important;"
      + "  object-fit: cover;"
      + "}"
      + ".fm-a123tv-card-poster .r {"
      + "  position: absolute;"
      + "  top: 6px; right: 6px;"
      + "  z-index: 2;"
      + "  padding: 2px 6px;"
      + "  border-radius: 4px;"
      + "  background: rgba(0,0,0,.7);"
      + "  color: #fff;"
      + "  font-size: 11px;"
      + "  font-weight: 700;"
      + "}"
      + ".fm-a123tv-card-poster .s {"
      + "  position: absolute;"
      + "  bottom: 0; left: 0; right: 0;"
      + "  padding: 4px 8px;"
      + "  background: linear-gradient(transparent, rgba(0,0,0,.7));"
      + "  color: #fff;"
      + "  font-size: 11px;"
      + "}"
      + ".fm-a123tv-card-info {"
      + "  padding: 8px;"
      + "}"
      + ".fm-a123tv-card-info .t {"
      + "  font-size: 14px;"
      + "  font-weight: 700;"
      + "  line-height: 1.35;"
      + "  white-space: nowrap;"
      + "  overflow: hidden;"
      + "  text-overflow: ellipsis;"
      + "  color: #111827 !important;"
      + "}"
      + ".fm-a123tv-card-info .i {"
      + "  font-size: 12px;"
      + "  color: #64748b !important;"
      + "  margin-top: 3px;"
      + "}"

      // Episode section
      + ".fm-a123tv-episode {"
      + "  max-width: 1228px;"
      + "  margin: 0 auto 16px;"
      + "  padding: 0 14px;"
      + "}"
      + ".fm-a123tv-episode .w4-episode-list a {"
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
      + "}"
      + ".fm-a123tv-episode .w4-episode-list a.on {"
      + "  border-color: #0f766e;"
      + "  background: #0f766e;"
      + "  color: #fff;"
      + "}"

      // Related section
      + ".fm-a123tv-meta2 {"
      + "  max-width: 1228px;"
      + "  margin: 16px auto 8px;"
      + "  padding: 0 14px;"
      + "}"

      // Playback panel
      + "#" + CONFIG.panelId + " {"
      + "  max-width: 1228px;"
      + "  margin: 0 auto 16px;"
      + "  padding: 14px;"
      + "  border: 1px solid rgba(15, 118, 110, .22);"
      + "  border-radius: 8px;"
      + "  background: #fff;"
      + "  color: #111827;"
      + "  box-shadow: 0 8px 22px rgba(15, 23, 42, .08);"
      + "}"
      + "#" + CONFIG.panelId + " * { box-sizing: border-box; }"
      + ".fm-a123tv-head {"
      + "  display: flex;"
      + "  align-items: flex-start;"
      + "  justify-content: space-between;"
      + "  margin-bottom: 12px;"
      + "}"
      + ".fm-a123tv-kicker {"
      + "  color: #0f766e;"
      + "  font-size: 12px;"
      + "  font-weight: 800;"
      + "  letter-spacing: .08em;"
      + "  text-transform: uppercase;"
      + "}"
      + ".fm-a123tv-title {"
      + "  margin-top: 2px;"
      + "  font-size: 17px;"
      + "  line-height: 1.35;"
      + "  font-weight: 800;"
      + "}"
      + ".fm-a123tv-count {"
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
      + ".fm-a123tv-list {"
      + "  display: flex;"
      + "  flex-direction: column;"
      + "}"
      + ".fm-a123tv-row {"
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
      + ".fm-a123tv-row:active { transform: translateY(1px); }"
      + ".fm-a123tv-row.is-busy { opacity: .68; }"
      + ".fm-a123tv-badge {"
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
      + ".fm-a123tv-main {"
      + "  min-width: 0;"
      + "  display: flex;"
      + "  flex-direction: column;"
      + "  margin: 0 10px;"
      + "}"
      + ".fm-a123tv-name {"
      + "  overflow: hidden;"
      + "  text-overflow: ellipsis;"
      + "  white-space: nowrap;"
      + "  font-size: 14px;"
      + "  line-height: 1.35;"
      + "  font-weight: 800;"
      + "}"
      + ".fm-a123tv-sub {"
      + "  overflow: hidden;"
      + "  text-overflow: ellipsis;"
      + "  white-space: nowrap;"
      + "  color: #64748b;"
      + "  font-size: 12px;"
      + "  line-height: 1.3;"
      + "}"
      + ".fm-a123tv-action {"
      + "  min-width: 42px;"
      + "  color: #be123c;"
      + "  font-size: 13px;"
      + "  font-weight: 900;"
      + "  text-align: right;"
      + "}"
      + ".fm-a123tv-empty {"
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
      + ".fm-a123tv-enhanced a:focus,"
      + ".fm-a123tv-enhanced button:focus,"
      + ".fm-a123tv-enhanced [tabindex]:focus {"
      + "  outline: 3px solid #14b8a6 !important;"
      + "  outline-offset: 2px !important;"
      + "}"
      + ".fm-a123tv-card:focus-within {"
      + "  border-color: #14b8a6 !important;"
      + "  transform: translateY(-2px);"
      + "  box-shadow: 0 10px 28px rgba(15, 118, 110, .20) !important;"
      + "}"
      + ".fm-a123tv-row:focus {"
      + "  border-color: #14b8a6 !important;"
      + "  background: #f0fdfa !important;"
      + "}"

      // Responsive
      + "@media (min-width: 700px) {"
      + "  .fm-a123tv-enhanced .w4-list {"
      + "    grid-template-columns: repeat(4, minmax(0, 1fr)) !important;"
      + "    margin-left: auto !important;"
      + "    margin-right: auto !important;"
      + "  }"
      + "}"
      + "@media (min-width: 1100px) {"
      + "  .fm-a123tv-enhanced .w4-list {"
      + "    grid-template-columns: repeat(6, minmax(0, 1fr)) !important;"
      + "  }"
      + "}"
      + "@media (max-width: 640px) {"
      + "  #" + CONFIG.panelId + " {"
      + "    margin-left: -2px;"
      + "    margin-right: -2px;"
      + "    border-radius: 0;"
      + "    box-shadow: none;"
      + "  }"
      + "  .fm-a123tv-row {"
      + "    grid-template-columns: auto minmax(0, 1fr);"
      + "  }"
      + "  .fm-a123tv-action {"
      + "    grid-column: 2;"
      + "    text-align: left;"
      + "    margin-top: -2px;"
      + "  }"
      + "}"

      // Dark mode support (site uses .dark class)
      + ".dark #" + CONFIG.searchId + " .fm-a123tv-search-form {"
      + "  border-color: #26313c;"
      + "  background: #121820;"
      + "}"
      + ".dark .fm-a123tv-search-label { color: #5eead4; }"
      + ".dark .fm-a123tv-search-input {"
      + "  border-color: #334155;"
      + "  background: #0f141b;"
      + "  color: #f8fafc;"
      + "}"
      + ".dark .fm-a123tv-item-wrap .fm-a123tv-card {"
      + "  border-color: #26313c;"
      + "  background: #121820;"
      + "}"
      + ".dark .fm-a123tv-card-info .t { color: #f8fafc !important; }"
      + ".dark .fm-a123tv-card-info .i { color: #94a3b8 !important; }"
      + ".dark #" + CONFIG.panelId + " {"
      + "  border-color: rgba(20, 184, 166, .28);"
      + "  background: #101214;"
      + "  color: #f8fafc;"
      + "}"
      + ".dark .fm-a123tv-kicker { color: #2dd4bf; }"
      + ".dark .fm-a123tv-row {"
      + "  border-color: #2a343f;"
      + "  background: #15191e;"
      + "  color: #f8fafc;"
      + "}"
      + ".dark .fm-a123tv-badge {"
      + "  background: rgba(45, 212, 191, .13);"
      + "  color: #5eead4;"
      + "}"
      + ".dark .fm-a123tv-sub { color: #94a3b8; }"
      + ".dark .fm-a123tv-action { color: #fb7185; }"
      + ".dark .fm-a123tv-empty {"
      + "  border-color: #334155;"
      + "  color: #94a3b8;"
      + "}"
      + ".dark .fm-a123tv-row:focus { background: #0f1a1a !important; }"
      + ".dark .fm-a123tv-episode .w4-episode-list a {"
      + "  border-color: #334155;"
      + "  color: #d1d5db;"
      + "}"
      + ".dark .fm-a123tv-episode .w4-episode-list a.on {"
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
    log("ready", location.href);
  });

  window.addEventListener("fmurlchange", function () {
    state.parsed = false;
    state.ppData = null;
    state.items.online = [];
    state.imagesProxied = false;
    scheduleScan();
  });
})();
