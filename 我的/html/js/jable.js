// WebHome extension for https://jable.tv/
// 最终稳定版：通过 pan.play 触发 App 本地嗅探规则

(function () {
  const CONFIG = { buttonClass: "fm-jable-play" };

  async function play(url, title) {
    const sdk = await new Promise(resolve => {
      if (window.fm) resolve(window.fm);
      else window.addEventListener("fmsdk", () => resolve(window.fm), { once: true });
    });
    try {
      // 强制触发解析流程
      return sdk.pan.play({ type: "jable", url: url, title: title });
    } catch (error) {
      console.error("[fm-jable] 调用失败:", error);
    }
  }

  function enhance() {
    document.querySelectorAll(".video-img-box").forEach(box => {
      if (box.dataset.fmReady) return;
      box.dataset.fmReady = "1";
      const link = box.querySelector("a");
      if (!link) return;
      const btn = document.createElement("button");
      btn.textContent = "嗅探播放";
      btn.style.cssText = "position:absolute; bottom:5px; right:5px; z-index:99; background:#e91e63; color:#fff; border:none; padding:4px; font-size:12px;";
      btn.onclick = (e) => {
        e.preventDefault();
        e.stopPropagation();
        const title = box.querySelector(".title")?.textContent.trim() || document.title;
        play(link.href, title);
      };
      box.style.position = "relative";
      box.appendChild(btn);
    });
  }

  new MutationObserver(enhance).observe(document.body, { childList: true, subtree: true });
  enhance();
})();
