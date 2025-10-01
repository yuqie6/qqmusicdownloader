[根目录](../../../CLAUDE.md) > [src](../../) > **qq_music_downloader**

# 核心下载模块

## 模块职责

负责 QQ 音乐的搜索、下载、加密解密等核心功能。提供完整的 TUI 用户界面和 API 接口。

## 入口与启动

### 主入口：`app.py`
- **启动命令**：`uv run qqmusicdownloader` 或 `python -m qq_music_downloader`
- **主要类**：`QQMusicApp` (基于 Textual)
- **入口函数**：`main()`

### 核心流程
1. Cookie 验证与配置
2. 歌曲 API 搜索
3. 音质选择与批量下载
4. 进度展示与状态管理

## 对外接口

### QQMusicAPI 类
主要 API 接口封装：
- `validate_cookie()` - Cookie 验证
- `search_song(keyword)` - 歌曲搜索
- `get_song_url(songmid, media_mid, quality)` - 获取下载链接
- `download_with_lyrics()` - 带歌词下载

### QQMusicDownloader 类
简化的下载器接口：
- `validate_cookie()` - 验证 Cookie
- `search(keyword)` - 搜索歌曲
- 支持暂停/恢复功能

## 关键依赖与配置

### Python 依赖
```python
# pyproject.toml
dependencies = [
    "aiofiles>=24.1.0",
    "aiohttp>=3.12.15",
    "textual>=0.58.1",
    "pytest>=8.4.2",
    "ruff>=0.13.1",
]
```

### Node.js 依赖
- QQ 音乐加密算法需要 Node.js 运行时
- 关键文件位于 `node_tools/` 目录
- 自动复制到临时目录执行

### 配置类
- `APIConfig` - API 超时、重试等配置
- `DownloadConfig` - 下载并发、默认音质配置

## 数据模型

### 歌曲数据结构
```python
{
    "name": "歌曲名称",
    "singer": "歌手",
    "album": "专辑",
    "songmid": "歌曲ID",
    "media_mid": "媒体ID"
}
```

### 音质选项
- 1: M4A (128kbps)
- 2: MP3 (320kbps)
- 3: FLAC (无损)

## 测试与质量

### 测试覆盖
- 单元测试：基础测试框架已建立
- 集成测试：API 接口测试
- UI 测试：Textual 界面测试

### 代码质量工具
- **ruff**：代码检查和格式化
- **pytest**：单元测试框架
- **mypy**：类型检查（建议启用）

## 常见问题 (FAQ)

### Q: Cookie 如何获取？
A: 登录 QQ 音乐网页版，在开发者工具中复制 Cookie。

### Q: 下载失败怎么办？
A: 检查 Cookie 有效性、网络连接、音质支持情况。

### Q: Node.js 环境问题？
A: 确保系统安装了 Node.js，crypto_bridge 模块会自动处理。

## 相关文件清单

### 核心文件
- `app.py` - TUI 应用主入口 (489行)
- `qq_music_api.py` - QQ 音乐 API 接口
- `downloader.py` - 下载器封装
- `crypto_bridge.py` - Node.js 加密桥接

### Node.js 工具
- `node_tools/qq_api_crypto.js` - 加密算法核心
- `node_tools/vendor.js` - 依赖库
- `node_tools/runtime.js` - 运行时支持

### 配置文件
- `__init__.py` - 模块初始化
- `__main__.py` - Python 模块入口

## 变更记录 (Changelog)

### 2025-10-02
- 🆕 创建模块文档
- 📝 补充接口说明和使用指南
- 🔧 整理文件结构和依赖关系

---

*最后更新：2025-10-02*