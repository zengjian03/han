// ============================================
// Web 高效去广告脚本 (Web Efficient Ad Blocker)
// 功能: 屏蔽常见广告元素、弹窗、跟踪脚本
// 用法: 在浏览器控制台运行，或作为浏览器扩展/用户脚本使用
// ============================================

(function() {
    'use strict';

    // ==================== 配置 ====================
    const CONFIG = {
        debug: false,                    // 调试模式
        interval: 500,                   // 轮询间隔(ms)
        maxAttempts: 50,                 // 最大轮询次数
        hideStyle: 'display:none !important;visibility:hidden !important;width:0 !important;height:0 !important;opacity:0 !important;pointer-events:none !important;',
        blockTrackers: true,             // 是否屏蔽跟踪器
        blockPopups: true,               // 是否屏蔽弹窗
        blockIframes: true               // 是否屏蔽广告iframe
    };

    // ==================== 广告选择器库 ====================
    const AD_SELECTORS = [
        // --- 通用广告容器 ---
        '[id*="ad" i]', '[class*="ad" i]',
        '[id*="ads" i]', '[class*="ads" i]',
        '[id*="advert" i]', '[class*="advert" i]',
        '[id*="sponsor" i]', '[class*="sponsor" i]',
        '[id*="banner" i]', '[class*="banner" i]',
        '[id*="popup" i]', '[class*="popup" i]',
        '[id*="modal" i][class*="ad" i]',
        '[id*="overlay" i][class*="ad" i]',

        // --- 国内常见广告 ---
        '.ad-wrapper', '.ad-container', '.ad-box',
        '.ad-banner', '.ad-slot', '.ad-unit',
        '.adsbygoogle', '.adsense',
        '#ad_header', '#ad_footer', '#ad_sidebar',
        '.cpro', '.bdad', '.ggbox', '.gg_area',
        '[class*="guanggao" i]', '[id*="guanggao" i]',
        '[class*="gg" i][class*="ad" i]',

        // --- 国外常见广告 ---
        '.google-ad', '.googleads', '.google-ads',
        '.facebook-ad', '.twitter-ad',
        '.amazon-ad', '.affiliate-ad',
        '.outbrain', '.taboola',
        '.mgbox', '.revcontent',

        // --- 视频广告 ---
        '.video-ad', '.pre-roll-ad', '.mid-roll-ad',
        '[class*="video_ads" i]', '[id*="video_ads" i]',
        '.ytp-ad-module', '.ytp-ad-overlay',
        '.html5-video-player .ad-container',

        // --- 弹窗/浮层 ---
        '.modal-backdrop', '.popup-overlay',
        '.fancybox-overlay', '.lightbox-overlay',
        '[class*="modal" i][class*="promo" i]',
        '[class*="dialog" i][class*="ad" i]',
        '.subscribe-box', '.newsletter-popup',
        '.cookie-consent:not([class*="simple" i])',
        '.gdpr-popup', '.privacy-popup',

        // --- 悬浮按钮/横幅 ---
        '.fixed-ad', '.sticky-ad', '.floating-ad',
        '.bottom-bar-ad', '.top-bar-ad',
        '.sidebar-ad', '.right-ad', '.left-ad',

        // --- 社交媒体嵌入广告 ---
        '.fb_ad', '.twitter_ad', '.instagram_ad',
        '.sponsored-content', '.promoted-content',
        '.promoted-tweet', '.sponsored-story'
    ];

    // ==================== 跟踪器/分析脚本域名 ====================
    const TRACKER_DOMAINS = [
        'google-analytics.com', 'googletagmanager.com',
        'googleadservices.com', 'googlesyndication.com',
        'doubleclick.net', 'googleusercontent.com',
        'facebook.com/tr', 'facebook.net',
        'connect.facebook.net', 'analytics.facebook.com',
        'twitter.com/i/ads', 'analytics.twitter.com',
        'amazon-adsystem.com', 'amazon.com/gp/advertising',
        'outbrain.com', 'taboola.com', 'revcontent.com',
        'scorecardresearch.com', 'quantserve.com',
        'moatads.com', 'adsrvr.org',
        'hotjar.com', 'optimizely.com',
        'segment.io', 'mixpanel.com',
        'kissmetrics.com', 'heapanalytics.com',
        'chartbeat.com', 'parsely.com',
        'newrelic.com', 'fullstory.com',
        'luckyorange.com', 'crazyegg.com',
        'mouseflow.com', 'sessioncam.com',
        'clicktale.net', 'tealeaf.com',
        'bizographics.com', 'linkedin.com/li/track',
        'ads.linkedin.com', 'analytics.yahoo.com',
        'advertising.yahoo.com', 'gemini.yahoo.com',
        'bing.com/bat', 'bat.bing.com',
        'clarity.ms', 'microsoft.com/clarity',
        'tiqcdn.com', 'tealiumiq.com',
        'adobedtm.com', 'omtrdc.net',
        'demdex.net', 'everesttech.net',
        'adsystem.com', 'advertising.com',
        'adnxs.com', 'appnexus.com',
        'openx.net', 'rubiconproject.com',
        'pubmatic.com', 'indexexchange.com',
        'casalemedia.com', 'contextweb.com',
        'criteo.com', 'criteo.net',
        'adform.net', 'smartadserver.com',
        'yieldmanager.com', 'yieldmo.com'
    ];

    // ==================== 广告 iframe 域名 ====================
    const AD_IFRAME_DOMAINS = [
        'googleads', 'doubleclick', 'googlesyndication',
        'googleusercontent', 'facebook.com/plugins',
        'twitter.com/widgets', 'adsystem',
        'amazon-adsystem', 'outbrain.com',
        'taboola.com', 'revcontent.com',
        'mgid.com', 'popads.net',
        'propellerads.com', 'onclickads.net',
        'adsterra.com', 'ad-maven.com',
        'exoclick.com', 'juicyads.com',
        'eroadvertising.com', 'adnxs.com',
        'adsrvr.org', 'advertising.com'
    ];

    // ==================== 日志工具 ====================
    const Logger = {
        log: function(...args) {
            if (CONFIG.debug) {
                console.log('[AdBlocker]', ...args);
            }
        },
        info: function(...args) {
            console.info('[AdBlocker]', ...args);
        },
        warn: function(...args) {
            console.warn('[AdBlocker]', ...args);
        },
        blocked: function(type, element) {
            this.log('已屏蔽', type + ':', element);
        }
    };

    // ==================== 核心功能 ====================

    /**
     * 隐藏元素
     */
    function hideElement(el) {
        if (!el || el._adblocked) return;
        el.style.cssText = CONFIG.hideStyle;
        el._adblocked = true;
        Logger.blocked('元素', el.tagName + (el.id ? '#' + el.id : '') + (el.className ? '.' + el.className.split(' ').join('.') : ''));
    }

    /**
     * 移除元素
     */
    function removeElement(el) {
        if (!el || el._adremoved) return;
        try {
            el.parentNode.removeChild(el);
            el._adremoved = true;
            Logger.blocked('移除', el.tagName);
        } catch(e) {}
    }

    /**
     * 基于选择器隐藏广告元素
     */
    function blockBySelectors() {
        AD_SELECTORS.forEach(selector => {
            try {
                document.querySelectorAll(selector).forEach(el => {
                    // 排除非广告元素（如 address, admin 等）
                    if (isProbablyAd(el)) {
                        hideElement(el);
                    }
                });
            } catch(e) {
                // 无效选择器，跳过
            }
        });
    }

    /**
     * 判断元素是否可能是广告
     */
    function isProbablyAd(el) {
        const tag = el.tagName.toLowerCase();
        const id = (el.id || '').toLowerCase();
        const cls = (el.className || '').toLowerCase();
        const text = (el.textContent || '').toLowerCase();

        // 排除常见误伤
        const falsePositives = [
            'address', 'admin', 'add', 'advanced',
            'adapt', 'adobe', 'android', 'load'
        ];
        for (let fp of falsePositives) {
            if (id === fp || cls === fp) return false;
        }

        // 检查尺寸（广告通常有固定尺寸）
        const rect = el.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) return false;

        // 常见广告尺寸
        const adSizes = [
            [300, 250], [728, 90], [160, 600], [320, 50],
            [468, 60], [970, 90], [336, 280], [300, 600],
            [250, 250], [200, 200], [180, 150], [125, 125],
            [120, 600], [120, 240], [234, 60], [120, 90]
        ];
        for (let size of adSizes) {
            if (Math.abs(rect.width - size[0]) < 5 && Math.abs(rect.height - size[1]) < 5) {
                return true;
            }
        }

        // 检查文本内容
        const adKeywords = ['广告', '推广', '赞助商', 'sponsored', 'advertisement', 'ad by', 'ads by'];
        for (let kw of adKeywords) {
            if (text.includes(kw)) return true;
        }

        // 检查子元素是否包含广告相关图片
        const imgs = el.querySelectorAll('img');
        for (let img of imgs) {
            const src = (img.src || '').toLowerCase();
            if (src.includes('ad') || src.includes('ads') || src.includes('banner')) {
                return true;
            }
        }

        return true; // 默认屏蔽
    }

    /**
     * 拦截 iframe 广告
     */
    function blockIframes() {
        if (!CONFIG.blockIframes) return;

        document.querySelectorAll('iframe').forEach(iframe => {
            const src = (iframe.src || '').toLowerCase();
            for (let domain of AD_IFRAME_DOMAINS) {
                if (src.includes(domain)) {
                    hideElement(iframe);
                    return;
                }
            }

            // 检查 iframe 内容
            try {
                const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                if (iframeDoc) {
                    const bodyText = (iframeDoc.body && iframeDoc.body.textContent) || '';
                    if (/ads?\s*by|advertisement|sponsored|推广|广告/i.test(bodyText)) {
                        hideElement(iframe);
                    }
                }
            } catch(e) {
                // 跨域 iframe，无法访问
            }
        });
    }

    /**
     * 拦截外部脚本
     */
    function blockExternalScripts() {
        if (!CONFIG.blockTrackers) return;

        document.querySelectorAll('script[src]').forEach(script => {
            const src = script.src.toLowerCase();
            for (let domain of TRACKER_DOMAINS) {
                if (src.includes(domain)) {
                    script.remove();
                    Logger.blocked('跟踪脚本', src);
                    return;
                }
            }
        });
    }

    /**
     * 拦截 XMLHttpRequest
     */
    function interceptXHR() {
        if (!window.XMLHttpRequest) return;

        const originalOpen = XMLHttpRequest.prototype.open;
        XMLHttpRequest.prototype.open = function(method, url) {
            const lowerUrl = (url || '').toLowerCase();
            for (let domain of TRACKER_DOMAINS) {
                if (lowerUrl.includes(domain)) {
                    Logger.blocked('XHR 请求', url);
                    // 阻止请求
                    this._blocked = true;
                    return;
                }
            }
            return originalOpen.apply(this, arguments);
        };

        const originalSend = XMLHttpRequest.prototype.send;
        XMLHttpRequest.prototype.send = function() {
            if (this._blocked) {
                // 模拟成功响应
                Object.defineProperty(this, 'readyState', { value: 4, writable: false });
                Object.defineProperty(this, 'status', { value: 200, writable: false });
                Object.defineProperty(this, 'responseText', { value: '', writable: false });
                if (this.onreadystatechange) this.onreadystatechange();
                return;
            }
            return originalSend.apply(this, arguments);
        };
    }

    /**
     * 拦截 Fetch 请求
     */
    function interceptFetch() {
        if (!window.fetch) return;

        const originalFetch = window.fetch;
        window.fetch = function(url, options) {
            const urlStr = (typeof url === 'string' ? url : url.url || '').toLowerCase();
            for (let domain of TRACKER_DOMAINS) {
                if (urlStr.includes(domain)) {
                    Logger.blocked('Fetch 请求', urlStr);
                    return Promise.resolve(new Response('', { status: 200 }));
                }
            }
            return originalFetch.apply(this, arguments);
        };
    }

    /**
     * 拦截图片请求
     */
    function blockTrackingImages() {
        document.querySelectorAll('img').forEach(img => {
            const src = (img.src || '').toLowerCase();
            for (let domain of TRACKER_DOMAINS) {
                if (src.includes(domain)) {
                    img.remove();
                    Logger.blocked('跟踪像素', src);
                    return;
                }
            }

            // 1x1 像素跟踪图
            if (img.width === 1 && img.height === 1) {
                img.remove();
                Logger.blocked('1x1 跟踪像素', src);
            }
        });
    }

    /**
     * 屏蔽弹窗
     */
    function blockPopups() {
        if (!CONFIG.blockPopups) return;

        // 拦截 window.open
        const originalOpen = window.open;
        window.open = function(url, target, features) {
            Logger.blocked('弹窗', url || '未知');
            return null;
        };

        // 拦截 alert/confirm/prompt
        window.alert = function(msg) {
            Logger.blocked('Alert 弹窗', msg);
        };
        window.confirm = function(msg) {
            Logger.blocked('Confirm 弹窗', msg);
            return true;
        };
        window.prompt = function(msg, defaultVal) {
            Logger.blocked('Prompt 弹窗', msg);
            return defaultVal || null;
        };
    }

    /**
     * 清理 Cookie 中的广告相关数据
     */
    function cleanAdCookies() {
        const cookies = document.cookie.split(';');
        const adPatterns = ['ad', 'ads', 'track', 'pixel', 'utm', 'campaign'];

        cookies.forEach(cookie => {
            const name = cookie.split('=')[0].trim().toLowerCase();
            for (let pattern of adPatterns) {
                if (name.includes(pattern)) {
                    document.cookie = name + '=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
                    Logger.blocked('广告 Cookie', name);
                    break;
                }
            }
        });
    }

    /**
     * 使用 MutationObserver 动态屏蔽
     */
    function observeMutations() {
        if (!window.MutationObserver) return;

        const observer = new MutationObserver(mutations => {
            let shouldCheck = false;
            mutations.forEach(mutation => {
                if (mutation.addedNodes.length > 0) {
                    shouldCheck = true;
                }
            });

            if (shouldCheck) {
                blockBySelectors();
                blockIframes();
                blockExternalScripts();
                blockTrackingImages();
            }
        });

        observer.observe(document.documentElement, {
            childList: true,
            subtree: true
        });

        return observer;
    }

    /**
     * 轮询检查（备用方案）
     */
    function startPolling() {
        let attempts = 0;
        const timer = setInterval(() => {
            blockBySelectors();
            blockIframes();
            blockExternalScripts();
            blockTrackingImages();

            attempts++;
            if (attempts >= CONFIG.maxAttempts) {
                clearInterval(timer);
                Logger.info('轮询结束，共执行', attempts, '次');
            }
        }, CONFIG.interval);
    }

    /**
     * 清理页面中的广告相关元素
     */
    function cleanPage() {
        // 移除空的广告容器
        document.querySelectorAll('[class*="ad" i], [id*="ad" i]').forEach(el => {
            if (el.children.length === 0 && !el.textContent.trim()) {
                removeElement(el);
            }
        });

        // 移除内联广告样式
        document.querySelectorAll('style').forEach(style => {
            const text = style.textContent || '';
            if (/\[class\*=["']ad["']\]/i.test(text) || /google-ad/i.test(text)) {
                style.remove();
                Logger.blocked('广告样式', '内联样式表');
            }
        });
    }

    // ==================== 初始化 ====================
    function init() {
        Logger.info('广告拦截器启动...');

        // 立即执行一次
        blockBySelectors();
        blockIframes();
        blockExternalScripts();
        blockTrackingImages();
        cleanAdCookies();

        // 拦截网络请求
        interceptXHR();
        interceptFetch();

        // 屏蔽弹窗
        blockPopups();

        // 监听 DOM 变化
        const observer = observeMutations();

        // 备用轮询
        startPolling();

        // 页面加载完成后清理
        if (document.readyState === 'complete') {
            cleanPage();
        } else {
            window.addEventListener('load', cleanPage);
        }

        Logger.info('广告拦截器初始化完成');
        console.log('%c🛡️ 广告拦截器已激活', 'color: #4CAF50; font-size: 14px; font-weight: bold;');
    }

    // ==================== 启动 ====================
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // 暴露 API
    window.AdBlocker = {
        config: CONFIG,
        blockNow: function() {
            blockBySelectors();
            blockIframes();
            blockExternalScripts();
            blockTrackingImages();
            cleanPage();
        },
        addSelector: function(selector) {
            AD_SELECTORS.push(selector);
        },
        addTrackerDomain: function(domain) {
            TRACKER_DOMAINS.push(domain);
        },
        stats: function() {
            return {
                selectors: AD_SELECTORS.length,
                trackers: TRACKER_DOMAINS.length,
                adIframes: AD_IFRAME_DOMAINS.length
            };
        }
    };

})();
