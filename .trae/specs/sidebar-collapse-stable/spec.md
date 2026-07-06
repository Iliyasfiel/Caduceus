# 侧边栏收起不影响主内容布局 Spec

## Why

侧边栏展开/收起时让主内容区 `margin-left` / `width` 同步变化，会导致右上角用户标签抖动、管线编辑器画布弹跳，破坏 UX 稳定感。

主流做法（GitHub / Linear / Notion 等）：**侧边栏以 drawer 形式从左侧弹出**，不参与主内容布局：
- 默认收起，不占任何空间
- 汉堡按钮触发浮层弹出
- 弹出时背景加遮罩 + 降低主页面对比度
- 点击遮罩 / 外部 / ESC 键 收起
- 主内容始终 `width: 100%`，零重排

此方案一统全部页面（含 PipelineEditor），不再需要"分页面区分处理"的复杂度。

## What Changes

- 全部页面统一为 drawer 模式（移除之前 PipelineEditor 走 push 让位的逻辑）
- AppLayout 默认收起 sidebar；汉堡按钮触发 drawer 浮层
- drawer 弹出时：
  - sidebar fixed + `transform: translateX(0)` 显示
  - 全屏遮罩 `<div class="sidebar-overlay">` 使用 `rgba(0, 0, 0, 0.5)` 统一深色半透明背景（light / dark 主题都用同一颜色，依靠透明度营造对比度反馈）
  - 主内容区视觉上被遮罩压低对比度，无需给 main 自身加 filter
- 关闭方式：点击遮罩、点击 sidebar 外部、ESC 键、按汉堡按钮再次
- 移动端 / 桌面端统一行为

### Breaking Changes
- 桌面端侧边栏默认收起（与之前"默认展开"不同）— 这是预期行为调整

## Impact

- Affected specs：Phase 7 UI 重设计（布局层）
- Affected code：
  - `frontend/src/components/AppLayout.vue`（核心改造：drawer + overlay）
  - 不影响其它页面/组件/store/api

## ADDED Requirements

### Requirement: Sidebar 默认收起，所有页面统一 drawer 模式

AppLayout 移除路由感知的多模式判断，所有页面（包括 PipelineEditor）统一走 drawer 模式：
- sidebar 默认收起（`transform: translateX(-100%)`）
- main 始终 `width: 100%`、`margin-left: 0`，与 sidebar 状态完全无关
- 移除 `.layout-push` 相关 CSS

#### Scenario: 默认状态（任意路由、桌面/移动）
- **WHEN** 用户进入任何路由
- **THEN** sidebar 默认收起（隐藏在屏幕左侧外）
- **AND** main 占满视口全宽
- **AND** header 内所有元素位置稳定

#### Scenario: 点击汉堡按钮打开 drawer
- **WHEN** 用户点击 header 上的汉堡按钮
- **THEN** sidebar 以 drawer 形式从左侧滑入（transform 过渡）
- **AND** 全屏遮罩 `<div class="sidebar-overlay">` 淡入显示，颜色为 `rgba(0, 0, 0, 0.5)`（深色半透明，统一 light / dark 主题）
- **AND** 视觉上主页面被遮罩压低对比度
- **AND** 汉堡按钮变为 ✕ 图标（可选，提供关闭入口）

#### Scenario: 点击遮罩关闭 drawer
- **WHEN** drawer 打开状态下用户点击遮罩区域
- **THEN** drawer 平滑滑出收起
- **AND** 遮罩淡出消失
- **AND** 主页面恢复完整对比度

#### Scenario: 再次点击汉堡按钮关闭
- **WHEN** drawer 打开状态下用户再次点击汉堡按钮
- **THEN** drawer 收起（同上）

#### Scenario: ESC 键关闭
- **WHEN** drawer 打开状态下用户按 ESC 键
- **THEN** drawer 收起

## MODIFIED Requirements

### Requirement: AppLayout 主内容区布局策略

**Before**（策略 B：双模式）：
- `.app-layout` 是 `display: block`
- 默认 overlay：main `width: 100%`、`margin-left: 0`
- `.layout-push`（管线编辑器）：main 让位 240px
- 桌面端 sidebar 默认展开，移动端默认收起

**After**（GitHub drawer）：
- `.app-layout` 是 `display: block`
- main 永远 `width: 100%`、`margin-left: 0`，**与 sidebar 状态完全无关**
- sidebar fixed + transform 滑出/滑入，永远浮层
- **桌面端 + 移动端默认收起**（不再按视口宽度区分）
- 新增 `<div class="sidebar-overlay">` 全屏遮罩元素，仅在 sidebar 打开时渲染（`v-if`）

## REMOVED Requirements

### 移除：路由感知双模式
- 移除 `useRoute()` 与 `isPipelineEditor` 计算属性
- 移除根元素 `:class="{ 'layout-push': ... }"`
- 移除 `.layout-push .main-content` 与 `.layout-push .sidebar` 全部规则

### 移除：移动端默认收起逻辑
- 移除 `window.innerWidth < 768px` 判定
- 移除 `isMobile` ref
- 移除 `@media (max-width: 768px)` 内 `.main-content` 让位规则

### 移除：默认展开行为
- `sidebarCollapsed` 默认值改为 `true`（默认收起）