# UI 设计原则 · Polish 记录 · Drawer 改造 · 文件清单

> 📦 **临时文档**（位于 [`dev-tmp/design/`](./)）。从原 `caduceus-ui-redesign.md` §5 / §6 / §8 / §10 / §13 / §15 拆分而来。
>
> 引用方：[`caduceus-design.md` §十二、基础组件清单](../../designingDocument/caduceus-design.md)
>
> 清理规则：按 `.trae/rules/project_rules.md` “临时文件（dev-tmp）” 一节，删除前须先向用户确认。

---

## 1. 设计原则（Design Principles）

后续开发应遵循以下原则，违反需在 PR 说明理由。

### 1.1 视觉原则

1. **同色语义不变量**：成功/错误色跨主题保持一致，不因主题变化
2. **圆角统一**：90% 元素使用 `--radius-md`，不要在小元素上用大圆角
3. **阴影克制**：阴影仅用于层级区分，不用于装饰
4. **间距 4 倍数**：所有间距值必须是 `--space-*` 之一，不写裸 px
5. **token 化**：所有颜色 / 字号 / 间距 / 圆角 / 阴影必须引用 token，**严禁硬编码**
6. **类型克制**：只用 7 级字号阶梯，不引入额外档位
7. **图表色专用**：5 个蓝色 `--color-chart-*` 仅用于数据可视化，不用作 UI 强调

### 1.2 组件原则

1. **状态色映射**：业务状态 → Badge tone 必须遵循 [caduceus-design.md §11.2](../caduceus-design.md) 映射表
2. **弹窗统一用 UiModal**：禁止自写 modal（特殊情况需说明）
3. **通知统一用 useToast()**：禁止 alert() / console.log() 作为用户反馈
4. **确认操作统一用 useConfirm()**：禁止 confirm() / 自写确认弹窗
5. **导入统一从 index.js**：禁止 import 单个组件文件路径
6. **Props 透传**：基础组件 props 透传原生属性，避免 API 漂移
7. **图标统一走 UiIcon**：禁止散落内联 SVG 或 emoji 字符

### 1.3 代码组织原则

1. **业务逻辑零改动承诺**：UI 重构只动 `<template>` 和 `<style>`，不动 `<script setup>` 的 state / API / 事件
2. **脚本逻辑完整保留**：所有 `ref` / `computed` / `onMounted` / `store` 调用 / API 调用必须保留
3. **感知层替换等价**：alert → toast 是用户感知等价；confirm → useConfirm 是 Promise 包装，调用方接收 true/false
4. **错误修复归 polish**：发现白屏 / 报错应作为 polish 的一部分修复，单独 commit

### 1.4 可访问性原则

1. **对比度**：所有文字/背景组合通过 WCAG AA（4.5:1 正文，3:1 大字）
2. **键盘导航**：所有可点击元素可通过 Tab 聚焦，ESC 关闭弹窗（UiModal 内置）
3. **Focus 环**：使用 `--color-ring` 作为聚焦环，不去除浏览器默认聚焦
4. **触摸目标**：按钮和链接的点击区域 ≥ 44×44px（移动端适配前置）
5. **语义化 HTML**：按钮用 `<button>`，链接用 `<a>`，不滥用 `<div @click>`

### 1.5 国际化原则

- 当前仅支持中文。预留 i18n 接口（`t()` 函数）但未集成 vue-i18n
- 文案集中在页面 template 中，不硬编码到组件 prop
- Badge tone 等枚举值国际化时需提供映射表

---

## 2. 关键页面 Polish — v2.0 实际完成

按"用户最高频路径"排序。✅ = 已完成；🟡 = 部分完成；⏳ = 待办。

| 顺序 | 页面 | v2.0 状态 | 关键改进 |
|------|------|-----------|----------|
| 1 | `Login.vue` | ✅ 已 polish | token 化 + UiInput/UiButton；右上角主题切换 |
| 2 | `Dashboard.vue` | ✅ 已 polish | token 化 + UiCard/UiBadge/UiEmptyState；不再用渐变数字 |
| 3 | `TaskList.vue` | ✅ 已 polish | UiCard 列表 + UiBadge 状态色 + 创建 UiModal + UiSelect 筛选；alert→toast |
| 4 | `TaskDetail.vue` | ✅ 已 polish | 时间线 UiCard 化 + UiInput 字段 + UiModal 分享；UiConfirm 替代 confirm |
| 5 | `PipelineEditor.vue` | 🟡 部分 polish | 工具栏 token 化 + 全局 toast；节点视觉保留（Vue Flow 自定义成本高） |
| 6 | `ResourceList.vue` | ✅ 已 polish | UiTabs + UiCard + UiModal + UiConfirm；操作日志折叠 |
| 7 | `AdminPanel.vue` | ✅ 已 polish | UiTabs + 3 个 UiModal + UiConfirm；warning/success 配色 token 化 |
| 8 | `SharePage.vue` | ✅ 已 polish | token 化 + UiCard + UiSpinner |
| 9 | `AppLayout.vue` | ✅ 已 polish | 顶栏 + 侧栏 Vercel 风格重构；UiButton 统一；UiIcon 全部图标 |
| 10 | `NotificationBell.vue` | ✅ 已 polish | token 化（11 处硬编码）；UiIcon 替换 🔔 |

**额外完成**：

- 子组件 token 化：`ResourceSelector.vue`（12 处硬编码）/ `TaskMergeGroup.vue`（11 处）/ `PipelineCanvas.vue`（67 处，布局层）
- 全局 `<UiToast />` 和 `<UiConfirm />` 挂在 `App.vue`
- 全 5 处 emoji / 特殊符号（🔔/☰/✕/☀/☾/◐/✓/📋）替换为 UiIcon

---

## 3. 体验细节

- ✅ **全局通知系统**：`useToast()` 替代 alert()，3 秒自动消失
- ✅ **全局确认弹窗**：`useConfirm()` 替代 confirm()，移动端友好
- ✅ **三态主题切换**：light / dark / system，localStorage 持久化
- ✅ **App.vue 挂载全局组件**：`<UiToast />` + `<UiConfirm />` 各一份
- ✅ **UiIcon 集中管理**：11 个图标集中在 `UiIcon.vue`，新增图标只需在 PATHS 注册
- 🟡 **Loading 骨架**：UiSpinner 已实现，但页面级骨架尚未统一（优先级 P2）
- ⏳ **EmptyState 全站统一**：组件已实现，但各页面空态文案/图标风格未统一（优先级 P2）
- ⏳ **错误边界**：未实现（优先级 P2）
- ⏳ **移动端响应式**：PipelineEditor 需桌面专属占位，breakpoints 工具类待添加（优先级 P1，详见 [ui-roadmap-p1.md](./ui-roadmap-p1.md)）

---

## 4. AppLayout 侧边栏 Drawer 改造（Phase 5-2）

> 完整 Spec 见 `.trae/specs/sidebar-collapse-stable/`，本节汇总设计决策与最终实现。

### 4.1 决策：GitHub 风格 Drawer（统一桌面 + 移动端）

**问题演进**：

1. 旧版：桌面默认展开 + 移动默认收起，main 用 `margin-left: 240px` 让位 → 侧栏收起时 main 抖动
2. 中间版（策略 B）：管线编辑器走 push 让位、其它路由走 overlay → 管线画布仍弹跳，复杂度增加
3. **最终方案：GitHub 风格 drawer** — 桌面 + 移动统一：默认收起，汉堡按钮触发浮层 + 全屏遮罩

**核心设计原则**：

- **零重排**：侧边栏 `position: fixed + transform: translateX(-100%/0)`，与 main 布局完全解耦
- **main 始终 `width: 100%` + `margin-left: 0`**，与侧边栏状态零耦合 → header 用户标签零抖动
- **统一遮罩**：`rgba(0, 0, 0, 0.5)`，light / dark 主题都用同一颜色（与 `UiModal` 视觉统一，不引入新 token）
- **多种关闭方式**：再点汉堡 ✕ / 点击遮罩 / 点击菜单项 / 按 ESC 键
- **图标切换**：汉堡按钮 `☰ ↔ ✕` 随状态切换（已统一为 `UiIcon name="menu"/"close"`）
- **无障碍**：汉堡按钮带 `aria-label` / `aria-expanded` 属性

### 4.2 z-index 层级

| 元素 | z-index | 说明 |
|------|---------|------|
| `<header>` | 100 | 顶栏，固定在最上 |
| `<aside class="sidebar">` | 95 | drawer 浮层（打开时在 header 下方） |
| `<div class="sidebar-overlay">` | 90 | 全屏遮罩（在 drawer 与 main 之间） |
| `<main>` | auto | 主内容，受遮罩压低视觉对比度 |

### 4.3 关闭方式矩阵

| 触发 | 实现位置 | 说明 |
|------|---------|------|
| 点击遮罩 | `sidebar-overlay @click="closeSidebar"` | 最直观的关闭方式 |
| 再点汉堡 ✕ | `menu-toggle @click="toggleSidebar"` | 切回 ☰ |
| 点击菜单项 | `<router-link @click="closeSidebar">` | 导航时关闭 |
| ESC 键 | `window.addEventListener('keydown', handleKeydown)` | 键盘用户友好 |
| 点击 sidebar 链接 | `nav-item` 装饰的 hover/active 行为 | 复用菜单项关闭 |

### 4.4 与 `UiModal` 视觉一致性

- 同款遮罩色 `rgba(0, 0, 0, 0.5)` —— 视觉语言统一
- 同款过渡时长 `var(--transition-normal)`（250ms ease）—— 用户感知一致
- sidebar drawer 与 `UiModal variant="drawer"` 在概念上一致（侧边浮层），可考虑未来用 `UiModal` 统一重构（当前业务量小，未做）

### 4.5 已解决的历史 bug

✅ **AppLayout 主内容宽度收缩 bug** — 已通过 drawer 改造彻底解决：

- 移除 flex 列布局对 main 的 shrink 干扰
- main 永远 `width: 100%`，不再依赖父容器让位
- 详见 `.trae/specs/sidebar-collapse-stable/checklist.md`

---

## 5. 风险与回滚（历史，已闭环）

- **风险**：UI 大改可能引入未发现的视觉 bug
- **缓解**：
  - 所有改动仅在 `ui-redesign` 分支进行
  - 每个阶段独立可回滚
  - 关键页面（Login / Dashboard / TaskDetail）合并前需用户确认
- **回滚**：`git revert` PR 即可，main 不受影响
- **已发现并修复的 bug**：
  - AdminPanel.vue 中间 `import { watch }` 导致白屏 → 移到顶部
  - PipelineEditor.vue 缺失 `useToast` import 导致白屏 → 补 import

> 状态更新：v2.0 全部 Polish 已合入 main，ui-redesign 分支关闭，main 稳定。后续视觉改动按 [caduceus-design.md §十一](../../designingDocument/caduceus-design.md) 风格基线进行。

---

## 6. 文件清单（v2.0 落地态）

### 6.1 新增文件

```
frontend/src/styles/
├── tokens.css             # 设计令牌（颜色 / 字号 / 间距 / 圆角 / 阴影 / 动效 / 语义色 / dark mode）
├── base.css               # reset + body 基础样式
└── breakpoints.css        # Phase 5 响应式断点 + 工具类

frontend/src/components/ui/
├── UiButton.vue
├── UiInput.vue
├── UiSelect.vue
├── UiCard.vue
├── UiBadge.vue
├── UiModal.vue
├── UiTabs.vue
├── UiEmptyState.vue
├── UiToast.vue
├── UiConfirm.vue
├── UiSpinner.vue
├── UiThemeToggle.vue
├── UiIcon.vue             # v2.0 新增
└── index.js               # 统一导出

frontend/src/stores/
├── theme.js               # 三态主题
├── toast.js               # 全局通知
└── confirm.js             # 全局确认弹窗
```

### 6.2 修改文件

- `frontend/src/main.js` — 引入 tokens.css + base.css + breakpoints.css + theme store init
- `frontend/src/App.vue` — 挂载 `<UiToast />` + `<UiConfirm />`
- `frontend/src/components/AppLayout.vue` — token 化 + UiButton + UiThemeToggle + UiIcon
- `frontend/src/components/NotificationBell.vue` — token 化 + UiIcon 替换 🔔
- `frontend/src/components/ResourceSelector.vue` — token 化 + UiBadge + 移动端 CSS
- `frontend/src/components/TaskMergeGroup.vue` — token 化 + UiBadge + UiIcon 替换 📋
- `frontend/src/components/PipelineCanvas.vue` — 布局层 token 化
- 8 个 view 文件：`Login.vue` / `Dashboard.vue` / `TaskList.vue` / `TaskDetail.vue` / `ResourceList.vue` / `AdminPanel.vue` / `SharePage.vue` / `PipelineEditor.vue`

### 6.3 验证记录

- `npm run build`：0 错误 0 警告（每次阶段完成后验证）
- 所有页面 `alert()` / `confirm()` 残留：0
- 所有 emoji / 特殊字符（`✓ ✕ ◐ ☰ ☾ ☀ 📋 ✗ ⏵ ⏴` + Emoji 区段）残留：0（全部走 `UiIcon`）
- 主题三态切换：light / dark / system 均正常
- dark mode：所有 token 化的页面自动跟随
- 移动端 UiModal 自动全屏：手动 dev tools 验证 OK

---

## 7. 业务逻辑契约对照

每个 polish 页面提交前，逐项检查 `<script setup>` 与 main 的 diff：

- 所有 `ref()` / `computed()` / `onMounted()` / `onUnmounted()` 数量与命名一致
- 所有 API 调用（`client.get(...)` / `client.post(...)` 等）路径与参数一致
- 所有 store 调用（`useAuthStore()` 等）一致
- 所有 emits 一致
- 所有路由跳转一致

**已通过验证**：8 个业务页面 + 5 个子组件 + AppLayout