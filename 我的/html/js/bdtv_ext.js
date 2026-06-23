(function() {
    'use strict';

    // 等待页面加载完成
    function waitForElement(selector, timeout = 5000) {
        return new Promise((resolve) => {
            const start = Date.now();
            const check = () => {
                const el = document.querySelector(selector);
                if (el) return resolve(el);
                if (Date.now() - start >= timeout) return resolve(null);
                setTimeout(check, 200);
            };
            check();
        });
    }

    // 解析播放源：从页面 script 或 video 标签中提取真实视频地址
    function extractVideoSource() {
        const video = document.querySelector('video');
        if (video && video.src) {
            return { type: 'direct', url: video.src };
        }
        // 尝试从配置变量中读取
        if (window.playerConfig && window.playerConfig.url) {
            return { type: 'config', url: window.playerConfig.url };
        }
        // 寻找 m3u8 链接
        const scripts = Array.from(document.querySelectorAll('script'));
        for (let script of scripts) {
            const content = script.textContent || script.innerText;
            if (content && (content.includes('.m3u8') || content.includes('.mp4'))) {
                const match = content.match(/(https?:[^"'\s]+\.(m3u8|mp4)[^"'\s]*)/i);
                if (match) return { type: 'script', url: match[1] };
            }
        }
        return null;
    }

    // 添加浮动工具栏
    function addFloatingToolbar() {
        if (document.getElementById('bdtv-toolbar')) return;
        const toolbar = document.createElement('div');
        toolbar.id = 'bdtv-toolbar';
        toolbar.innerHTML = `
            <style>
                #bdtv-toolbar {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    z-index: 9999;
                    background: rgba(0,0,0,0.8);
                    backdrop-filter: blur(8px);
                    border-radius: 40px;
                    padding: 8px 16px;
                    display: flex;
                    gap: 12px;
                    font-family: system-ui, sans-serif;
                    font-size: 14px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                    border: 1px solid rgba(255,255,255,0.2);
                }
                #bdtv-toolbar button {
                    background: #ff6b6b;
                    border: none;
                    color: white;
                    padding: 6px 12px;
                    border-radius: 30px;
                    cursor: pointer;
                    font-weight: bold;
                    transition: 0.2s;
                }
                #bdtv-toolbar button:hover {
                    background: #ff4757;
                    transform: scale(1.02);
                }
                #bdtv-toolbar .info {
                    color: #ccc;
                    line-height: 32px;
                    margin-left: 8px;
                }
            </style>
            <button id="bdtv-extract">🎬 解析源</button>
            <button id="bdtv-fullscreen">⛶ 全屏</button>
            <span class="info" id="bdtv-status">就绪</span>
        `;
        document.body.appendChild(toolbar);

        document.getElementById('bdtv-extract').addEventListener('click', () => {
            const source = extractVideoSource();
            const statusSpan = document.getElementById('bdtv-status');
            if (source) {
                statusSpan.innerHTML = `✅ 获取到: ${source.url.substring(0, 60)}...`;
                // 可以弹窗或直接播放
                const video = document.querySelector('video');
                if (video && source.url !== video.src) {
                    video.src = source.url;
                    video.load();
                    video.play();
                    statusSpan.innerHTML = '🎉 已切换播放源';
                } else if (!video) {
                    statusSpan.innerHTML = '⚠️ 未找到 video 标签，可复制链接手动播放';
                    navigator.clipboard.writeText(source.url);
                    alert('视频链接已复制到剪贴板');
                }
            } else {
                statusSpan.innerHTML = '❌ 未检测到播放源';
            }
        });

        document.getElementById('bdtv-fullscreen').addEventListener('click', () => {
            const video = document.querySelector('video');
            if (video) {
                if (video.requestFullscreen) video.requestFullscreen();
                else if (video.webkitRequestFullscreen) video.webkitRequestFullscreen();
                else alert('当前浏览器不支持全屏');
            } else {
                alert('未找到视频元素');
            }
        });
    }

    // 自动运行：检测播放页才显示工具栏
    function init() {
        if (window.location.pathname.includes('/play/') || window.location.pathname.includes('/vod/')) {
            addFloatingToolbar();
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();