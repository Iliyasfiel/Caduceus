# dev-tmp/design — 设计文档相关临时草稿

> 配合正式设计文档 [`designingDocument/caduceus-design.md`](../../../designingDocument/caduceus-design.md) §十一、§十二 使用。
>
> 顶层索引：[`dev-tmp/README.md`](../README.md)

## 当前内容

| 文件 | 来源 | 用途 | 状态 |
|------|------|------|------|
| [`ui-component-api-reference.md`](./ui-component-api-reference.md) | 原 `caduceus-ui-redesign.md` §11 | 13 个基础组件的 Props / Emits / Slots 详细参考；全局 Store API | 长期保留（与正式设计文档互补） |
| [`ui-design-principles-and-polish.md`](./ui-design-principles-and-polish.md) | 原 `caduceus-ui-redesign.md` §5 / §6 / §8 / §10 / §13 / §15 | UI 设计原则 / Polish 记录 / Drawer 改造 / 文件清单 / 验证记录 | 长期保留（实施回顾与审计追踪） |
| [`ui-roadmap-p1.md`](./ui-roadmap-p1.md) | 原 `caduceus-ui-redesign.md` §4 / §9 | 复合组件决策 / Phase 5 工具类 / 后续 Spec | 长期保留（路线图参考） |
| [`resource-v2-lifecycle-discussion.md`](./resource-v2-lifecycle-discussion.md) | 客户场景「舞台灯光全生命周期管理」讨论 | 资源库 v2 方向草案：事件流载体定位 / 资源模板独立画布 / 任务 ↔ 资源双向耦合 | 等待客户反馈后再决定要不要沉淀进正式设计文档 |
| [`uiselect-v2-plan.md`](./uiselect-v2-plan.md) | 2026-07-06 在 `feature/task-list-ui-optimize` 分支讨论 | UiSelect 重构为自渲染 popper 计划：修复暗色模式 bug + 键盘导航 + 暴露 3 个可选能力（搜索 / 多选 / 异步） | 待用户确认后实施 |

## 清理规则

按 [`.trae/rules/project_rules.md`](../../../.trae/rules/project_rules.md) “临时文件（dev-tmp）” 一节，删除本目录内任何文件 / 子目录前，必须**先向用户确认**该临时内容是否需要同步沉淀到项目正式文档。