# UI 拆分执行计划

## 背景
现有 `src/qqmusicdownloader/ui/app.py` 将布局、样式、交互集中于单文件，难以维护。需按 Textual 最佳实践拆分为独立 Widgets，外部化 CSS。

## 目标
- 将 UI 区块拆分为独立 Widget 类，落实单一职责。
- 提取内联 CSS 至 `ui/themes/default.css`。
- 保持现有功能与交互逻辑不变。

## 步骤
1. 提取内联 CSS 至 `ui/themes/default.css`。
2. 为认证、路径、搜索、结果、动作、状态等区块创建独立 Widgets。
3. 更新 `ui/widgets/__init__.py` 导出新组件。
4. 重构 `ui/app.py` 使用新组件并维持原有行为。
5. 运行必要检查，确保无回归。

