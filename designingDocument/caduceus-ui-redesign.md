# Caduceus UI 重新设计规划

> **状态**：规划文档（基线） | **版本**：v1.0 | **适用分支**：`ui-redesign`
> **创建日期**：2026-07-04 | **关联 Spec**：`.trae/specs/phase-7-repo-governance-and-ui-plan/`

## 0. 背景与目标

经过 Phase 0-6 迭代，Caduceus 前端已具备完整功能（认证 / Dashboard / 任务流 / 资源 / 管线 / 通知 / 分享 / 管理）。但视觉层呈"工程师风"：所有样式散落在每个 .vue 的 `<style>` 里，没有统一的设计令牌，没有可复用的基础组件库。

本次 UI 重新设计的目标：

1. **建立轻量级设计系统**：颜色 / 间距 / 字号 / 圆角 / 阴影 等令牌 + 12 个基础组件
2. **关键页面 Polish**：按用户最高频路径，对 3-5 个页面做视觉重做
3. **不破坏现有功能**：所有改动都在 `ui-redesign` 隔离分支进行，不直接 commit 到 main
4. **可持续**：剩余页面可在后续 Sprint 用同一套系统批量替换

**明确不做**：
- ❌ 不引入重型 UI 组件库（Element Plus / Ant Design Vue 等），保持轻量
- ❌ 不做完整主题切换（暗色模式），仅预留令牌空间
- ❌ 不重做业务逻辑

---

## 1. 设计令牌（Design Tokens）— P0

新建 `frontend/src/styles/tokens.css`（CSS 变量）+ `frontend/src/styles/base.css`（reset + body 基础样式），在 `main.js` 引入。**所有组件只能引用令牌，不写裸值。**

| 令牌类别 | 具体内容 | 用途 |
|---|---|---|
| 颜色（语义） | `primary` / `success` / `warning` / `danger` / `info` | 按钮、徽章、强调 |
| 颜色（灰阶） | `gray-50` / `gray-100` / `gray-200` / `gray-400` / `gray-600` / `gray-900` | 文字、背景、分割 |
| 颜色（场景） | `bg-canvas` / `bg-surface` / `bg-elevated` / `border-subtle` / `text-primary` / `text-secondary` / `text-muted` | 卡片层级、文字层级 |
| 字号 | `text-xs(12) / sm(14) / base(16) / lg(18) / xl(20) / 2xl(24) / 3xl(30)` | 全局文字 |
| 间距 | `space-1(4) / 2(8) / 3(12) / 4(16) / 6(24) / 8(32) / 12(48)` | padding / margin / gap |
| 圆角 | `radius-sm(4) / md(8) / lg(12) / xl(16) / full(9999)` | 按钮、卡片、徽章、头像 |
| 阴影 | `shadow-sm / shadow-md / shadow-lg` | 卡片、弹窗 |
| 动效 | `transition-fast(150ms) / normal(250ms) / slow(400ms)` | hover / 展开 / 路由 |

**默认值建议**（现代简约商务风）：
- `primary`: `#2563EB`（蓝）
- `bg-canvas`: `#F9FAFB`（极浅灰）
- `bg-surface`: `#FFFFFF`
- `text-primary`: `#111827`
- 圆角偏大：8-16px
- 阴影克制：单层、模糊半径 8-16

---

## 2. 基础组件（Base Components）— P0

放在 `frontend/src/components/ui/`。**强制只用令牌，不写硬编码值。**

| 组件 | 关键变体 | 涉及页面 |
|---|---|---|
| `Button` | primary / secondary / ghost / danger × sm/md/lg × loading / icon-only | 全部 |
| `Input` | text / textarea / number / 带前缀图标 / 错误态 | Login, Admin, TaskDetail, Pipeline |
| `Select` | 单选 / 多选 / 搜索 | Admin, TaskDetail, ResourceSelector |
| `Card` | 基础 / 可悬浮 / 带 header-actions | Dashboard, TaskList, TaskDetail, TaskMergeGroup |
| `Badge` | 状态色（pending/in_progress/done/...） + 角色色 | TaskList, TaskDetail, ResourceList |
| `Table` | 表头排序 / 空状态 / loading 骨架 / 行 hover | TaskList, ResourceList, Admin |
| `Modal` | 居中 / 右侧抽屉 / 销毁确认 | ResourceSelector, Admin, TaskDetail 资源选择 |
| `Tabs` | 基础 / 胶囊 | ResourceList, Admin |
| `EmptyState` | 图标 + 标题 + 副标题 + CTA | 所有列表空态 |
| `Toast` | success / error / info | 全局通知 |
| `Avatar` | 图片 / 首字母 / 角色色块 | NotificationBell, Admin |
| `Dropdown` | 触发器 + 菜单 | NotificationBell, 顶栏用户菜单 |

---

## 3. 复合组件（Composite Components）— P1

由基础组件组合而成，供业务页面直接使用。

| 组件 | 组成 | 涉及位置 |
|---|---|---|
| `StatCard` | Card + 大数字 + 趋势/对比文案 | Dashboard 统计区 |
| `TimelineStep` | Badge + 连接线 + 时间 + 操作按钮 | TaskDetail 阶段时间线 |
| `FieldRow` | Label + Input + 角色可见性开关 | TaskDetail 字段表单 |
| `ResourceCard` | Card + Badge(type) + Badge(status) + 数量/单位 | ResourceList / TaskDetail 资源选择 |
| `CommentItem` | Avatar + 内容 + 时间 + 操作 | TaskDetail 评论区 |
| `NodePropertyPanel` | Tabs(Basic/Fields/Roles) + Form | PipelineEditor 右侧 |
| `MergeGroup` | Card + 子任务列表 + 折叠 | TaskList 合并组 |

---

## 4. 关键页面 Polish 顺序 — P0~P1

按"用户最高频路径"排序。每页挑 1-2 个最有视觉冲击的位置先做。

| 顺序 | 页面 | 重点优化 |
|---|---|---|
| 1 | `Login.vue` | 居中品牌区 + 渐变背景 + 卡片化表单（第一印象） |
| 2 | `Dashboard.vue` | StatCard 重做 + 渐变色数字 + 任务列表卡片化 |
| 3 | `TaskList.vue` | Table 替换列表式 + 状态 Badge 统一 + 合并组视觉化 |
| 4 | `TaskDetail.vue` | TimelineStep 三态可视 + 字段区卡片化 + 资源区紧凑 |
| 5 | `PipelineEditor.vue` | 节点配色统一 + 右侧属性面板改 Tabs |
| 6 | `ResourceList.vue` | 顶部筛选 + ResourceCard 网格 + 日志折叠 |
| 7 | `AdminPanel.vue` | Tabs 胶囊化 + 表格统一 |
| 8 | `SharePage.vue` | 只读风格的简化版，公开访问要"有质感" |
| 9 | `AppLayout.vue` | 顶栏 / 侧栏对齐 + 通知铃 Badge |
| 10 | `NotificationBell.vue` | 下拉卡片化 + 已读未读视觉区分 |

---

## 5. 体验细节 — P2（按需）

- 全局 Loading 骨架（替代裸 spinner）
- EmptyState 统一插画/图标
- 错误边界（页面崩溃兜底）
- 暗色模式（基于令牌直接反色）
- 移动端响应式（先做任务详情和列表）

---

## 6. 给 TRAE Design 的输入建议

将本规划直接喂给 TRAE Design 时，明确以下输入：

1. **风格基调**（三选一）：
   - **现代简约商务风**（推荐，灰白底 + 蓝色强调）
   - **Linear/Notion 风格**（高密度信息、留白克制）
   - **暖色协作风**（Figma / Slack 风格，适合多人协作产品）
2. **设计令牌**：6 个语义色 + 5 级灰阶，圆角偏大（8-16px），阴影克制
3. **参考产品**：Linear（任务流） + Figma（编辑器） + Vercel（Dashboard 卡片）

---

## 7. 任务拆分（待办基线）

在 `ui-redesign` 分支上，按以下顺序分阶段交付。每个 Task 都应是**可独立验证**的（小步快跑）。

### 阶段 A：设计令牌与全局样式

- [ ] **A1** 新建 `frontend/src/styles/tokens.css` 定义所有 CSS 变量
- [ ] **A2** 新建 `frontend/src/styles/base.css` 定义 reset + body 基础样式
- [ ] **A3** 在 `main.js` 引入 `tokens.css` 与 `base.css`
- [ ] **A4** 验证：浏览器 DevTools 中 `:root` 暴露所有令牌
- **依赖**：无

### 阶段 B：基础组件（核心 7 个）— 立即可看到第一波效果

- [ ] **B1** 实现 `Button.vue`（4 种 variant × 3 种 size）
- [ ] **B2** 实现 `Input.vue`（含错误态）
- [ ] **B3** 实现 `Card.vue`（基础 + 悬浮 + header-actions）
- [ ] **B4** 实现 `Badge.vue`（状态色 + 角色色）
- [ ] **B5** 实现 `Modal.vue`（居中 + 右侧抽屉）
- [ ] **B6** 实现 `EmptyState.vue`
- [ ] **B7** 实现 `Toast.vue` + 全局 `useToast()` composable
- **依赖**：A

### 阶段 C：基础组件（剩余 5 个）

- [ ] **C1** 实现 `Select.vue`（单选 + 多选 + 搜索）
- [ ] **C2** 实现 `Table.vue`（表头排序 / 空状态 / loading / 行 hover）
- [ ] **C3** 实现 `Tabs.vue`（基础 + 胶囊）
- [ ] **C4** 实现 `Avatar.vue`
- [ ] **C5** 实现 `Dropdown.vue`
- **依赖**：B

### 阶段 D：复合组件

- [ ] **D1** `StatCard.vue`
- [ ] **D2** `TimelineStep.vue`
- [ ] **D3** `FieldRow.vue`
- [ ] **D4** `ResourceCard.vue`
- [ ] **D5** `CommentItem.vue`
- [ ] **D6** `NodePropertyPanel.vue`
- [ ] **D7** `MergeGroup.vue`
- **依赖**：B、C

### 阶段 E：关键页面 Polish（按用户高频路径）

- [ ] **E1** 重做 `Login.vue`
- [ ] **E2** 重做 `Dashboard.vue`
- [ ] **E3** 重做 `TaskList.vue`
- [ ] **E4** 重做 `TaskDetail.vue`（复用 D2 TimelineStep、D3 FieldRow）
- [ ] **E5** 重做 `PipelineEditor.vue`（复用 D6 NodePropertyPanel）
- [ ] **E6** 重做 `ResourceList.vue`（复用 D4 ResourceCard）
- [ ] **E7** 重做 `AdminPanel.vue`
- [ ] **E8** 重做 `SharePage.vue`
- **依赖**：D

### 阶段 F：剩余页面与细节

- [ ] **F1** 重做 `AppLayout.vue` 与 `NotificationBell.vue`
- [ ] **F2** Loading 骨架统一
- [ ] **F3** EmptyState 全站统一
- [ ] **F4** 错误边界
- **依赖**：E

### 阶段 G：测试与回归

- [ ] **G1** 视觉回归（手动截图对比）
- [ ] **G2** 响应式验证（任务详情 + 任务列表）
- [ ] **G3** 浏览器兼容（Chrome / Safari / Firefox）
- [ ] **G4** 合并到 main（PR review）
- **依赖**：F

---

## 8. 风险与回滚

- **风险**：UI 大改可能引入未发现的视觉 bug
- **缓解**：
  - 所有改动仅在 `ui-redesign` 分支进行
  - 每个阶段（E1-E8）独立可回滚
  - 关键页面（Login / Dashboard / TaskDetail）合并前需用户确认
- **回滚**：`git revert` PR 即可，main 不受影响

---

## 9. 后续 Spec

- 每个阶段（A-G）建议独立建 Spec（`.trae/specs/ui-redesign-phase-X/`），以便追踪进度
- TRAE Design 生成的视觉稿可放 `designingDocument/caduceus-ui-redesign-designs/`（届时另起小节）
