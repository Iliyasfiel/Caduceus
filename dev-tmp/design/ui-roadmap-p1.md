# UI 后续路线图（P1/P2 待办 · 复合组件决策 · Phase 5 断点工具类）

> 📦 **临时文档**（位于 [`dev-tmp/design/`](./)）。从原 `caduceus-ui-redesign.md` §4 / §9 拆分而来。
>
> 引用方：[`caduceus-design.md` §十二、基础组件清单](../../designingDocument/caduceus-design.md)
>
> 清理规则：按 `.trae/rules/project_rules.md` “临时文件（dev-tmp）” 一节，删除前须先向用户确认。

---

## 1. 复合组件（Composite Components）— P1

v2.0 **未引入独立的复合组件**，业务页面直接组合基础组件实现：

| 原规划组件 | 实际替代方案 | 是否需要独立组件化 |
|-----------|--------------|------------------|
| `StatCard` | 直接用 `UiCard` + 内联大数字（`--text-3xl`）+ 变化文案 | ⏳ P2 评估 |
| `TimelineStep` | 直接用 `UiBadge`（状态色）+ `UiCard`（容器）+ 时间轴 div | ⏳ P2 评估 |
| `FieldRow` | 直接用 `UiInput` + label prop | ⏳ P2 评估 |
| `ResourceCard` | 直接用 `UiCard` + `UiBadge`（type + status tone） | ⏳ P2 评估 |
| `CommentItem` | 直接用 `UiCard`（基础） + 评论样式 | ⏳ P2 评估 |
| `NodePropertyPanel` | 用 `UiTabs` + `UiInput` 组合 | ⏳ P2 评估 |
| `MergeGroup` | 直接用 `UiCard` + 折叠 CSS | ⏳ P2 评估 |

**判断标准**：当同一组合模式在 3 个以上页面重复出现且 Props/Emits 稳定时，提取为独立组件。现状下业务页面数不足以触发此条件。

---

## 2. Phase 5 断点与工具类基线（已落地）

> 落地于 `frontend/src/styles/breakpoints.css`，在 `main.js` 中引入。

**断点（mobile-first，min-width 媒体查询）**：

| Token | 值 | 典型设备 |
|-------|-----|----------|
| `--bp-sm` | `640px` | 手机横屏 / 小平板 |
| `--bp-md` | `768px` | 平板竖屏 / 手机大屏 |
| `--bp-lg` | `1024px` | 桌面 / 平板横屏 |
| `--bp-xl` | `1280px` | 桌面宽屏 |

**10 个通用工具类**：

| 类名 | 作用 | 媒体行为 |
|------|------|----------|
| `hide-on-mobile` | 移动端隐藏 | 默认隐藏；≥ md 才显示 |
| `hide-on-tablet` | 仅平板隐藏 | 仅在 md-lg 显示 |
| `hide-on-desktop` | 桌面隐藏 | 默认显示；≥ lg 才隐藏 |
| `stack-on-mobile` | 移动栈式 / 桌面横向 | 默认 flex-col；≥ md 改 flex-row |
| `stack-on-mobile-reverse` | 同上但反向 | mobile 用 column-reverse |
| `touch-target` | 触摸目标 ≥ 44×44px | 始终 |
| `full-bleed-mobile` | 移动端去 padding | 默认 0；≥ md 恢复 `--space-6` |
| `scroll-x-mobile` | 表格横向滚动 | 始终；触发 `-webkit-overflow-scrolling: touch` |
| `safe-bottom-mobile` | iOS 底部安全区 | 用 `env(safe-area-inset-bottom)` |
| `text-truncate` / `text-truncate-2` | 单/双行省略 | 始终 |

**使用规约**：

- 工具类只在**布局外层**用，业务组件内部仍按需写 `@media (min-width: 768px)`
- 组件内部 @media 用 token（`var(--bp-md)` 等），不要写裸 px
- 工具类不写进 `Ui*.vue` 内部（避免组件 API 污染），仅供业务页面使用
- iOS notch 安全区只在移动端滚动容器底部考虑，桌面端不需要

---

## 3. 后续 Spec 与路线图（未启动）

- **Phase 6（待评估）**：Table / Avatar / Dropdown 组件化（当前业务量小，未必必要）
- **Phase 7（待评估）**：错误边界 + 页面级 Loading 骨架 + EmptyState 文案统一
- **移动端策略（Web-only / GitHub 风格）**：
  - 阶段基线：V1.x 阶段**不做独立 H5 移动应用**（推迟到 V2.0，见 PRD §7.2）；PipelineEditor 的移动端体验问题同步推迟，未来小版本再议
  - 同一套交互逻辑：桌面端与移动端共享同一套页面 / 同一套表单 / 同一套数据流
  - 只做响应式排版优化：自适应密度、列折叠、容器方向调整
  - SharePage：保持公开分享页同一布局，仅做响应式 polish（不做"移动端独立布局"）
  - UiModal 自动全屏（< 640px）✅ 已实现

---

## 4. 变更记录

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-07-04 | 初始规划文档（任务拆分 / 风险 / 后续 Spec） |
| v2.0 | 2026-07-04 | 实际落地后重写：新增第 2 节设计风格基线、第 5-7 节实际完成状态、第 10-13 节设计原则与 API 参考 |
| v2.1 | 2026-07-05 | 新增第 15 节「AppLayout Drawer 改造」：记录 GitHub 风格 drawer 决策、z-index 层级、关闭方式矩阵、视觉一致性 |
| v3.0 | 2026-07-06 | **重构**：原文件拆分。设计令牌 / 组件清单迁入 [`caduceus-design.md`](../../designingDocument/caduceus-design.md) §11 / §12 作为正式设计章节；API 参考 / 设计原则 / Polish 记录 / Drawer 改造 / 文件清单 / 验证记录 拆分为 [ui-design-principles-and-polish.md](./ui-design-principles-and-polish.md)；复合组件 / Phase 5 工具类 / 后续 Spec 拆分为本文档。原文件 `caduceus-ui-redesign.md` 删除 |
| v3.1 | 2026-07-06 | 重写 §3 移动端边界 → "移动端策略（Web-only / GitHub 风格）"。同步在 [`caduceus-design.md`](../../designingDocument/caduceus-design.md) §十三新增「跨平台策略」正式章节，明确 V1.x 不做独立 H5、不做"请用桌面访问"占位、不做 JS 视口判断 |