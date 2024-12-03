


# 极简音乐下载器 🎵

一款让音乐下载变得轻松愉快的 QQ 音乐下载工具！基于 [BeeWare](https://beeware.org/) 框架开发，力求带给你简单纯粹的下载体验。

想象一下，当你找到心仪的音乐时，只需轻点几下，音乐就会从云端悄然降落到你的设备中 - 就是这么简单！

**This cross-platform app was generated by [Briefcase](https://briefcase.readthedocs.io/) - part of [The BeeWare Project](https://beeware.org/). If you want to see more tools like Briefcase, please consider [becoming a financial member of BeeWare](https://beeware.org/contributing/membership).**

## ✨ 功能特点

- 🔍 智能搜索：快速定位 QQ 音乐曲库中的音乐
- 🌈 界面简洁：告别繁琐，享受清爽的操作体验
- 🚀 下载便捷：只需几步，让音乐陪伴左右

## 🌐 官方网站
- https://yuqie6.github.io/qqmusicdownloader

## 📦 安装说明

### 系统要求
- Windows 11 （作者正在努力支持更多平台！）

### 下载安装
1. 从 [Releases](https://github.com/YOUR_USERNAME/qq-music-downloader/releases) 页面获取最新版本
2. 双击安装程序，轻松搞定！


### 源码安装
#### 环境要求

在开始之前，请确保您的系统满足以下要求：

- Python 3.8 或更高版本
- pip（Python 包管理器）
- Git（用于克隆代码仓库）

您可以通过在终端运行以下命令检查 Python 版本：
```bash
python --version
```

#### 安装步骤

#### 1. 克隆代码仓库

首先，克隆项目代码到本地：

```bash
git clone https://github.com/yuqie6/qqmusicdownloader.git
cd qqmusicdownloader
```

### 2. 设置开发环境

建议使用虚拟环境来管理项目依赖。创建并激活虚拟环境：

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

#### 3. 安装 Briefcase

安装 Briefcase 工具，它将帮助我们管理项目依赖和运行应用：

```bash
python -m pip install --upgrade pip
python -m pip install briefcase
```

#### 4. 运行应用

在开发模式下运行应用：

```bash
briefcase dev
```

这个命令会自动完成以下工作：
- 安装所有必要的依赖包
- 配置开发环境
- 启动应用程序

### 常见问题解决

#### 如果遇到依赖安装问题

有时可能会遇到某些依赖包安装失败的情况。这种情况下，您可以尝试：

1. 确保您的 pip 是最新版本：
```bash
python -m pip install --upgrade pip
```

2. 如果某个包安装失败，可以尝试单独安装：
```bash
python -m pip install 包名
```

#### 如果应用无法启动

1. 检查是否已正确激活虚拟环境
2. 确认 Python 版本是否满足要求
3. 查看 `briefcase dev` 命令的错误输出

### 开发者说明

本项目使用 `pyproject.toml` 进行依赖管理，而不是传统的 requirements.txt。如果您需要添加新的依赖，请编辑 `pyproject.toml` 文件。



## 🎯 版本历史

### 1.2.0 (03 Dec 2024)

#### ✨ 新增功能
* 新增了路径选择，方便用户自定义下载位置
* 在选择格式时新增温馨提示，方便用户使用

#### 💄 界面优化
* 重新设计了界面布局，采用现代化的卡片式设计
* 优化了按钮和控件的视觉效果
* 新增了路径选择按钮，方便用户自定义下载位置
* 把音质选择改为了文件格式选择，更加准确
* 设计了单独的程序图标

#### 🐛 修复问题
* 修复了文件已存在时仍会下载
* 修改了about信息
#### ⚠️ 已知问题
* 进度条还是有问题，作者能力有限
* 多次搜索，搜索栏会遗留歌名，点击即可看见真实歌名
### 1.1.0 - 2024年12月2日
- ✨ 重磅更新：支持批量下载功能
- 🎮 新增下载暂停/继续控制
- 🐛 修复了一些已知问题（但还在加班修复其他bug）
- 💄 界面小优化，让操作更顺手

### 1.0.0 - 2024年12月1日
- 🎉 首个正式版本闪亮登场！
- 🔍 支持基本搜索功能
- ⬇️ 实现单曲下载
- 🎨 简洁的界面

## 🎮 使用方法

1. 启动应用，就像打开一个音乐百宝箱
2. 输入你的 QQ音乐 VIP 账号 cookie（别担心，本地开源，作者也看不见）
3. 在搜索框输入你想找的歌曲或歌手
4. 点击搜索，让音乐来找你
5. 选择心仪的歌曲
6. 一键下载，就这么简单！

## ⚠️ 温馨提示

- 本软件是学习研究的小伙伴，请勿用于商业用途
- 下载的音乐请仅供个人欣赏
- 让我们一起支持正版音乐，给创作者应有的尊重

## 🔧 技术栈

- [Python](https://www.python.org/) - 最好的朋友
- [BeeWare](https://beeware.org/) - 跨平台的神奇魔法
- [Briefcase](https://briefcase.readthedocs.io/) - 打包分发的得力助手

## 🤝 贡献指南

欢迎加入我们的开源大家庭！以下是参与的简单步骤：

1. Fork 本仓库（为项目增添一份力量）
2. 创建特性分支 (`git checkout -b feature/YourAmazingFeature`)
3. 提交改动 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/YourAmazingFeature`)
5. 发起 Pull Request（让我们看看你的精彩创意！）

## 👨‍💻 作者

[@yuqie6](https://github.com/yuqie6) - 一个热爱音乐与代码的追梦人

## 📄 许可证

本项目采用 MIT 许可证 - 详情请见 [LICENSE](LICENSE) 文件

## 🙏 鸣谢

- [BeeWare](https://beeware.org/) - 让跨平台开发不再是梦
- [Briefcase](https://briefcase.readthedocs.io/) - 打包分发的得力助手
- 所有关注和支持这个项目的朋友们

---

*温馨提示：这是一个独立项目，与 QQ音乐官方无关，仅供学习交流使用。*