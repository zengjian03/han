# 📺 OK影视 / 影视最新版 使用指南

推荐使用 **OK影视** 或 **影视最新版壳** 以获得最佳体验。

## 📱 系统要求 & 兼容性
* **最低兼容安卓版本**：Android 6.0
* **故障排除**：如果播放时出现闪退等情况，请尝试在设置中切换为 **ijk** 播放核心。

---

## ⚠️ 重要声明 (必读)

> ❣️ **注意**：本项目仅供交流学习，**请勿用于商业用途**。视频源中出现的任何广告，请勿轻信！
>
> ❣️ **注意**：请切勿在网盘 `tv_temp_saved` 目录存放重要文件。此目录仅作为视频播放服务临时转存目录，**系统会不定期清除该目录内容**！

---

## 🔗 接口配置 (点播地址)

### 🌐 在线接口
您可以选择以下任一接口填入配置：

- **接口 1**: `https://chigua.eu.org`
- **接口 2**: `https://16151.kstore.space`

### 📂 本地包入口
如果您使用本地包，请参考以下路径格式：

* **主入口**: `file://包名/api.json`
* **Py 爬虫入口**: `file://包名/py.json`
* **Js 爬虫入口**: `file://包名/js.json`

> **注意**：以上 `file://` 开头的路径仅为配置示例，**在浏览器中无法直接点击打开**，请手动复制到 APP 配置中。

---

## 🛠️ 本地包详细说明

### 基础配置
* ✔️ **自定义包名**：支持更改包文件夹名称，例如：`file://dongli/api.json`
* ✔️ **任意路径**：支持将本地包放置在任意路径。
* ✔️ **推荐根目录**：
    ```text
    /storage/emulated/0/dp/
    ```

### 📁 固定存储目录
系统相关文件将固定存储在以下目录：

| 文件类型 | 存储路径 |
| :--- | :--- |
| **Cookie** | `/storage/emulated/0/TVData/cookie` |
| **数据库** | `/storage/emulated/0/TVData/db` |
| **配置文件** | `/storage/emulated/0/TVData/config` |
| **APK/本地包下载** | `/storage/emulated/0/Download/` |
| **凯速 Token** | `/storage/emulated/0/TVData/kstore_token.txt` |

### ⚙️ 高级功能
* **本地数据库映射**：需指定自定义映射配置文件。
    * [查看示例配置](https://v6.gh-proxy.org/https://raw.githubusercontent.com/chitue/dongliTV/refs/heads/main/config/local_database_mapping.json)
    * *注意：网络数据库下载后需**重启 APP**生效。目前本地数据库仅支持直链播放。*
* **网盘播放**：此类播放需要配置中心提前设置 Cookie。

### ☁️ Cookie 云备份与恢复
支持通过配置 **凯速 Access Token** 将本地 Cookie 存储到凯速直链云存储中，实现多设备一键恢复。

1.  **获取 Token**: [点击此处获取凯速 Access Token](https://my.ksust.com/kstore.htm?aff=16151) (页面底部)
2.  **默认保存**: Token 默认保存在 `/storage/emulated/0/TVData/kstore_token.txt`

---

## 💾 资源下载与推荐

### 网盘推荐顺序
个人推荐顺序如下：
1. 百度网盘
2. 夸克网盘
3. UC 网盘
4. 阿里网盘
5. 天翼云盘
6. 123 网盘 (每月 10G 流量限制)

### 📥 东篱影视专用资源下载 
包含 APK 和本地包资源：

* **UC 网盘**: [点击下载](https://drive.uc.cn/s/084710ec4dc04?public=1)
* **夸克网盘**: [点击下载](https://pan.quark.cn/s/514a56ac6d23)
* **百度网盘**: [点击下载](https://pan.baidu.com/s/13JGvmZlFIqJblaDFRGthVQ?pwd=2026) *(提取码: 2026)*
* **迅雷网盘**: [点击下载](https://pan.xunlei.com/s/VOoL5NPJCrDfWdYq2l6S4s52A1?pwd=74bm)

### 📖 详细使用说明

* **详细说明**: [点击阅读](https://chigua.eu.org/docs/USAGE.md)