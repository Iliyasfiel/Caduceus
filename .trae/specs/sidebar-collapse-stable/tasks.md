# Tasks

- [x] Task 1: 移除路由感知双模式
  - [x] SubTask 1.1: 移除 `<script setup>` 中 `useRoute` 与 `isPipelineEditor`
  - [x] SubTask 1.2: 移除模板根元素 `:class="{ 'layout-push': isPipelineEditor }"`
  - [x] SubTask 1.3: 移除 `.layout-push` 相关 CSS

- [x] Task 2: 改为默认收起
  - [x] SubTask 2.1: `sidebarCollapsed` 默认值改为 `true`
  - [x] SubTask 2.2: 移除 `window.innerWidth < 768px` 判定
  - [x] SubTask 2.3: 移除 `isMobile` ref 与 `checkMobile` 函数
  - [x] SubTask 2.4: 移除 `@media (max-width: 768px)` 内让位规则
  - [x] SubTask 2.5: 移除 `onMounted` / `onUnmounted` 中 resize 监听

- [x] Task 3: 增加 sidebar-overlay 遮罩元素
  - [x] SubTask 3.1: 模板中增加 `<div v-if="!sidebarCollapsed" class="sidebar-overlay" @click="closeSidebar">`
  - [x] SubTask 3.2: 样式：position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 90; opacity transition
  - [x] SubTask 3.3: 遮罩颜色统一使用 `rgba(0, 0, 0, 0.5)`（深色半透明），light / dark 主题都用同一颜色，不引入新 token

- [x] Task 4: 增加 drawer 关闭逻辑
  - [x] SubTask 4.1: 增加 `closeSidebar()` 函数（设置 sidebarCollapsed = true）
  - [x] SubTask 4.2: 监听键盘 ESC 键：drawer 打开时按 ESC 关闭
  - [x] SubTask 4.3: 汉堡按钮图标切换：☰（收起） ↔ ✕（打开）

- [x] Task 5: 构建与场景验证
  - [x] SubTask 5.1: `npm run build` 0 错误 0 警告
  - [ ] SubTask 5.2: 默认状态（任意路由）：sidebar 收起、main 满宽（需浏览器手动验证）
  - [ ] SubTask 5.3: 点击汉堡：drawer 从左侧滑入 + 遮罩淡入 + 主页面降低对比度（需浏览器手动验证）
  - [ ] SubTask 5.4: 点击遮罩 / 再点汉堡 / ESC 键：drawer 关闭（需浏览器手动验证）
  - [ ] SubTask 5.5: 任意页面（含 PipelineEditor）：sidebar 收起/打开时 header 不抖动、main 无重排（需浏览器手动验证）

# Task Dependencies
- Task 1 / Task 2 是改造前置（先移除旧逻辑）— ✅
- Task 3 / Task 4 在 Task 1 / Task 2 基础上增加 drawer 行为 — ✅
- Task 5 在所有 Task 完成后验证（构建已通过，浏览器场景验证待用户确认）