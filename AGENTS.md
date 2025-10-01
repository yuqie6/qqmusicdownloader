# Repository Guidelines

## Project Structure & Module Organization
核心 TUI 实现在 `src/qqmusicdownloader/`，按分层结构划分：`ui/` 负责 Textual 布局与交互，`services/` 编排下载流程，`domain/` 保存实体与配置，`infrastructure/` 对接 QQ 音乐 API、加密脚本与文件系统。静态资源放在 `resources/`。终端示例与额外资料位于 `docs/`。回归测试集中在 `tests/`，务必与业务模块一一对应。`music-downloader-site/` 为站点素材，修改前确认不会破坏 TUI 主流程。

## Build, Test, and Development Commands
使用 uv 简化环境：`uv run qqmusicdownloader` 启动 TUI 并加载依赖。首次贡献请执行 `uv sync` 以安装项目锁定的依赖。校验异步逻辑前运行 `uv run pytest`。静态检查使用 `uv run ruff check .`；格式化则用 `uv run ruff format .`。如需调试单个模块，可调用 `uv run python -m qqmusicdownloader`。

## Coding Style & Naming Conventions
代码遵循 Python 3.11 标准，统一使用 4 空格缩进与 Unix 换行。模块、包、函数与变量采 snake_case，类名使用 PascalCase。保留类型注解以提升异步边界的可维护性；公开函数应声明返回类型。避免在 UI 层进行网络请求，保持单一职责。配置值（下载目录、API 常量）集中在模块顶部，便于复用。

## Testing Guidelines
采用 pytest，测试文件命名 `test_*.py` 并放置在 `tests/`。针对异步协程使用 `pytest.mark.asyncio` 或 `asyncio.run` 包装，确保下载与解析逻辑均覆盖正常及错误分支。新增功能前先编写最小断言，检验完成后执行整套测试，目标是保证关键路径覆盖率不下降。

## Commit & Pull Request Guidelines
遵循类似 Conventional Commits 的前缀：`feat`, `fix`, `refactor`, `docs`, `ci` 等，例如 `feat: 支持批量选择音质`。确保单次提交聚焦单一改动，并在正文说明行为变化与破坏性风险。提交 PR 时附上：需求背景、解决方案概述、测试命令输出与补充截图（如 UI 有改动）。链接相关 Issue，同时声明是否引入新的依赖或环境变量，便于回顾与审核。

## Security & Configuration Tips
Cookie 含敏感凭证，只能存储在本机配置目录，严禁提交到版本库。修改 `resources/` 下的 Textual 主题时，确认不泄露账号信息。异步请求默认指向 QQ 音乐公开接口，任何生产环境 URL 需在讨论后再合并。
