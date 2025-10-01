# 极简音乐下载器 🎵

一个专注命令行体验的 QQ 音乐下载工具！基于 [Textual](https://www.textualize.io/) 构建现代化 TUI，跨平台运行自如，把搜索、选择、下载、进度展示全部装进一个终端窗口。

当你找到喜欢的歌曲，只要在终端里敲几下键盘，就能把音乐整洁地保存到本地。

## ✨ 功能特点

- 🔍 智能搜索：快速定位 QQ 音乐曲库中的歌曲
- ✅ Cookie 管理：内置校验流程，避免无效凭证浪费时间
- 🧾 多选下载：支持批量勾选歌曲并自由选择音质
- 📊 即时反馈：进度条与状态提示让下载过程一目了然

## 📦 安装与运行

### 使用 uv（推荐）

1. 安装 [uv](https://github.com/astral-sh/uv)（一次性操作）
2. 克隆代码仓库并进入目录：
   ```bash
   git clone https://github.com/yuqie6/qqmusicdownloader.git
   cd qqmusicdownloader
   ```
3. 直接启动 TUI：
   ```bash
   uv run qqmusicdownloader
   ```

`uv run` 会自动解析 `pyproject.toml` 中的依赖，创建隔离环境并启动应用。

### pip 备选方案

如果暂时无法使用 uv，可以手动创建虚拟环境：

```bash
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell
./.venv/Scripts/Activate.ps1
# Windows CMD
./.venv/Scripts/activate.bat
pip install textual aiohttp aiofiles
python -m qqmusicdownloader
```

> 建议优先使用 uv，以获得更快的依赖解析速度与更加可重复的环境。

## 🎮 使用指南

1. 运行 `uv run qqmusicdownloader`（或 `python -m qqmusicdownloader`）打开终端界面
2. 粘贴 QQ 音乐 VIP 账号 Cookie，按 Enter 或点击“保存 Cookie”完成验证
3. 如需更改下载目录，在路径输入框中填写并“应用路径”
4. 输入关键词进行搜索，等待结果出现在列表中
5. 使用空格或回车勾选想要下载的歌曲，可一次选择多首
6. 通过音质下拉框选择目标格式，确认后点击“开始下载”
7. 如需暂停/恢复，可使用“暂停/恢复”按钮

## 🎯 功能演进

### Unreleased
- 🆕 全面切换至 Textual TUI，告别桌面 GUI 依赖
- ♻️ 移除 Briefcase 打包脚手架，运行流程更轻量

### 1.2.0 (2024-12-03)
- 新增路径选择与批量下载提示
- 优化视觉样式与按钮布局
- 修复重复下载与 About 信息问题

### 1.1.0 (2024-12-02)
- 引入批量下载与暂停/继续控制
- 改善界面操作体验

### 1.0.0 (2024-12-01)
- 支持搜索、单曲下载等核心功能

## ⚠️ 温馨提示

- 软件仅供学习与研究使用，请勿用于商业目的
- 下载的音乐请只作为个人收藏与欣赏
- 支持正版音乐，为创作者的付出买单

## 🔧 技术栈

- [Python](https://www.python.org/)
- [Textual](https://www.textualize.io/)
- [aiohttp](https://docs.aiohttp.org/)
- [aiofiles](https://github.com/Tinche/aiofiles)

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 `git checkout -b feature/awesome-feature`
3. 完成开发并提交 `git commit -m "feat: 描述你的改动"`
4. 推送分支并发起 Pull Request

欢迎通过 Issue 分享想法或反馈 Bug，一起让工具更好用！

## 📄 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE)。

## 🙏 鸣谢

- [Textual](https://www.textualize.io/) 带来的优雅终端 UI
- 所有测试、反馈与 Star 的朋友
