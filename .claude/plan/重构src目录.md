# 重构 src 目录计划

## 上下文
- 旧版实现集中于 `src/qq_music_downloader/`，UI、业务、基础设施耦合，文件体量大。
- 目标构建分层包 `src/qqmusicdownloader/`，拆分 UI、服务、领域、基础设施职责。
- 需确保 Node 加密桥接可用、清理旧结构与资源，并补充测试覆盖。

## 已执行步骤
1. 建立新包骨架：`domain`、`services`、`infrastructure`、`ui`，同步入口指向。
2. 迁移并重构下载 API、下载服务与 Textual UI，落实依赖倒置与职责拆分。
3. 搬迁 Node 加密脚本，清理旧目录与无用资源，更新文档与脚本说明。
4. 验证加密桥接功能，新增下载服务单元测试，引入 `pytest-asyncio`。

## 后续建议
- 持续补充基础设施与 UI 层测试。
- 评估是否需要继续维护 `music-downloader-site` 并制定部署策略。
