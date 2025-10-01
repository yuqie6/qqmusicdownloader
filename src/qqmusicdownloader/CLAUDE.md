[根目录](../../CLAUDE.md) > **src** > **qqmusicdownloader**

# qqmusicdownloader 包

## 分层结构

- `ui/`：Textual 终端界面与交互逻辑，依赖服务层暴露的接口。
- `services/`：应用服务，协调下载流程与状态控制，依赖领域层与基础设施层。
- `domain/`：核心实体、值对象与配置，保持纯逻辑、无副作用。
- `infrastructure/`：对接 QQ 音乐 API、加密脚本、文件系统与下载实现细节。

## 关键模块

### `ui/app.py`
- Textual `QQMusicApp` 主入口。
- 负责用户输入、状态展示、进度控制。
- 通过 `DownloadService` 访问业务逻辑。

### `services/download_service.py`
- 封装下载流程、搜索缓存与全局暂停控制。
- 提供 `from_cookie()` 工厂方法，简化 UI 初始化。
- 负责协调基础设施层下载接口。

### `domain/config.py`
- 定义 `DownloadConfig`，集中管理并发度与默认音质。

### `domain/models.py`
- 描述 `SongRecord`、`FileSizeMap` 类型结构，保证数据契约一致。

### `domain/ports.py`
- 定义 `DownloadAPI` 协议，约束基础设施层需提供的最小下载能力。
- 服务层依赖该抽象以满足依赖倒置原则，可插拔不同实现或 Mock。

### `infrastructure/qq_music_api.py`
- 实现 QQ 音乐 API 调用、Cookie 校验、歌曲搜索与下载。
- 提供 `configure_download_dirs()` 以在服务层/界面层动态调整下载目录。

### `infrastructure/crypto/bridge.py`
- 封装 Node.js 加密脚本的进程生命周期管理。
- 提供 `encrypt_payload()` / `decrypt_response()` 供 API 客户端复用。

## 扩展指南

1. 新增业务流程：
   - 在 `services/` 中建新模块，依赖 `domain` 与 `infrastructure` 的抽象。
   - UI 通过注入服务层接口使用。

2. 新增基础设施实现：
   - 在 `infrastructure/` 下创建模块，并提供抽象协议给服务层。
   - 必要时在 `domain` 内扩充实体描述。

3. 新增 UI 组件：
   - 在 `ui/` 内分离 Widgets/Screen，确保仅通过服务层交互。

## 入口说明

- CLI：`uv run qqmusicdownloader` 或 `python -m qqmusicdownloader`
- 包导入：`from qqmusicdownloader.services import DownloadService`

## 测试建议

- 对 `services/`、`domain/` 编写单元测试，利用异步测试工具。
- 对 `infrastructure/` 关注网络请求的 stub/mocking。
- UI 层可使用 Textual 的 `Pilot` 工具进行交互测试。

---

*最后更新：2025-10-03*
