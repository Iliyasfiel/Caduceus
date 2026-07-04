# Caduceus UI 重新设计规划

> **状态**：v2.0（已实现 + 风格规范基线） | **版本**：v2.0 | **适用分支**：`ui-redesign`
> **创建日期**：2026-07-04 | **最后更新**：2026-07-04 | **关联 Spec**：`.trae/specs/phase-7-ui-redesign-foundation/`

## 0. 文档说明

本文档是 Caduceus 前端 UI 重设计的**唯一权威文档**，包含三个层次：

1. **第 1-9 节** — 规划与现状（v1.0 时期的规划 + v2.0 实际落地后的状态）
2. **第 10 节** — **设计风格基线（Style Guide）**：所有视觉决策的真相来源，供后续开发者遵循
3. **第 11-12 节** — 组件 / Store API 参考 + 设计原则与禁忌

任何后续 UI 改动**必须**先查阅本风格基线。改动令牌值、新增组件、调整组件 API 都需要在本文档同步更新。

---

## 1. 背景与目标

经过 Phase 0-6 迭代，Caduceus 前端已具备完整功能（认证 / Dashboard / 任务流 / 资源 / 管线 / 通知 / 分享 / 管理）。但视觉层呈"工程师风"：所有样式散落在每个 .vue 的 `<style>` 里，没有统一的设计令牌，没有可复用的基础组件库。

本次 UI 重新设计的目标：

1. **建立轻量级设计系统**：颜色 / 间距 / 字号 / 圆角 / 阴影 等令牌 + 12 个基础组件
2. **关键页面 Polish**：按用户最高频路径，对 8 个业务页面做视觉重做
3. **不破坏现有功能**：所有改动都在 `ui-redesign` 隔离分支进行，不直接 commit 到 main
4. **可持续**：剩余页面可在后续 Sprint 用同一套系统批量替换

**v2.0 新增目标**（已落地）：

5. **三态主题系统**：light / dark / system 切换，localStorage 持久化
6. **全局通知 + 确认弹窗**：替代浏览器原生 `alert()` / `confirm()`
7. **业务逻辑零改动承诺**：通过契约对照验证（详见第 13 节）

---

## 2. 设计风格基线（Style Guide）

> **本节是 v2.0 新增的核心规范**。所有 UI 改动的视觉决策必须与本节一致。如需偏离，需在 PR 描述中说明理由。

### 2.1 设计语言定位

**Vercel 风格 · 现代简约商务 · 工程师友好**

| 维度 | 取向 | 反例 |
|------|------|------|
| 整体氛围 | 克制 / 干净 / 信息密度高 | 不要 Material 浮夸阴影 / 不要 Tailwind 粉彩 |
| 颜色基调 | 中性灰 + 黑白 + 单点强调色 | 不要大面积彩色 / 不要彩色渐变 |
| 圆角 | 中等 8-12px（柔和但有结构感） | 不要完全方角 / 不要 24px 大圆角（儿童化） |
| 阴影 | 极轻，单层，0.04-0.06 透明度 | 不要立体感强的多层阴影 |
| 字体 | Geist Sans（Vercel 主字体）+ Geist Mono（代码） | 不要用系统字体外的装饰字体 |
| 数字 | Geist Mono 等宽（仪表盘） | 不要用衬线字体显示数字 |
| 图标 | 线性图标，1.5px 描边 | 不要用 emoji 代替功能图标（除非是 EmptyState 的情绪点缀） |

### 2.2 颜色系统

#### 主色板（基础 21 色，全部直接复用 Vercel token）

| Token | Light 值 | Dark 值 | 用途 |
|-------|---------|---------|------|
| `--color-background` | `#ffffff` | `#0a0a0a` | 页面主背景 |
| `--color-foreground` | `#0a0a0a` | `#fafafa` | 主文字 |
| `--color-card` | `#ffffff` | `#171717` | 卡片背景 |
| `--color-card-foreground` | `#0a0a0a` | `#fafafa` | 卡片内文字 |
| `--color-popover` | `#ffffff` | `#262626` | 弹窗 / 下拉背景 |
| `--color-popover-foreground` | `#0a0a0a` | `#fafafa` | 弹窗内文字 |
| `--color-primary` | `#121212` | `#e5e5e5` | 主操作按钮（Vercel 用黑白为主色） |
| `--color-primary-foreground` | `#fafafa` | `#171717` | 主按钮文字 |
| `--color-secondary` | `#f5f5f5` | — | 次要按钮背景 |
| `--color-secondary-foreground` | `#171717` | — | 次要按钮文字 |
| `--color-muted` | `#f5f5f5` | `#262626` | 静默背景（tag 灰底） |
| `--color-muted-foreground` | `#858585` | `#a1a1a1` | 静默文字 |
| `--color-accent` | `#f5f5f5` | `#404040` | 悬浮背景 |
| `--color-accent-foreground` | `#171717` | `#fafafa` | 悬浮文字 |
| `--color-destructive` | `#e7000b` | `#ff6467` | 危险操作（红色） |
| `--color-destructive-foreground` | `#ffffff` | — | 危险操作文字 |
| `--color-border` | `#e8e8e8` | `#282828` | 边框 |
| `--color-input` | `#e5e5e5` | `#343434` | 输入框边框 |
| `--color-ring` | `#0d0d0d` | `#737373` | 聚焦环 |
| `--color-success` | `#62d178` | `#62d178` | 成功色（light/dark 同色） |
| `--color-error` | `#ff6166` | `#ff6166` | 错误色（light/dark 同色） |

**关键决策**：

- **主按钮 = 黑白**，不用品牌蓝。Vercel 风格强调"反品牌化"，让用户的注意力集中在内容本身
- **成功/错误色跨主题同色**：因为这两个语义要"一眼识别"，不能因主题变化改变含义
- **Chart 色仅用于数据可视化**：5 个蓝色梯度（`#91c5ff` → `#1f3fad`），不用于 UI 强调

#### 语义色（Badge / Status 共 5 组 × 2 色 = 10 个 token）

| Token | Light bg | Light fg | Dark bg | Dark fg | 用途 |
|-------|---------|---------|---------|---------|------|
| `--badge-neutral-bg/-fg` | `#f5f5f5` | `#525252` | `#262626` | `#d4d4d4` | 默认 / draft / 静默状态 |
| `--badge-info-bg/-fg` | `#dbeafe` | `#1e3a8a` | `#1e3a8a` | `#dbeafe` | in_progress / 进行中 / 提示 |
| `--badge-success-bg/-fg` | `#d1fae5` | `#065f46` | `#14532d` | `#bbf7d0` | completed / success / 已完成 |
| `--badge-warning-bg/-fg` | `#fef3c7` | `#92400e` | `#78350f` | `#fde68a` | pending / warning / 待处理 |
| `--badge-danger-bg/-fg` | `#fee2e2` | `#991b1b` | `#7f1d1d` | `#fecaca` | cancelled / failed / error |

**业务状态色映射规则**（Caduceus 任务流）：

| 任务状态 | Badge tone | 说明 |
|---------|-----------|------|
| `draft` | neutral | 草稿，未发布 |
| `pending` | warning | 待开始 |
| `in_progress` | info | 进行中 |
| `completed` | success | 已完成 |
| `cancelled` | danger | 已取消 |

#### 场景语义别名

为让业务页面用更直观的语义 token，定义以下别名（指向基础 token）：

```css
--bg-canvas:     var(--color-background);  /* 页面底色 */
--bg-surface:    var(--color-card);        /* 卡片 */
--bg-elevated:   var(--color-popover);     /* 浮层（弹窗） */
--bg-muted:      var(--color-muted);       /* 静默区 */

--text-primary:   var(--color-foreground);          /* 主文字 */
--text-secondary: var(--color-muted-foreground);    /* 次文字 */
--text-muted:     var(--color-muted-foreground);    /* 弱化文字 */
--text-inverse:   var(--color-primary-foreground);  /* 反色文字 */

--border-subtle: var(--color-border);  /* 默认边框 */
--border-strong: var(--color-foreground);  /* 强调边框 */
```

### 2.3 字号阶梯

| Token | 值 | 像素 | 典型用途 |
|-------|-----|------|----------|
| `--text-xs` | `0.75rem` | 12px | 辅助信息 / 标签 / badge |
| `--text-sm` | `0.875rem` | 14px | 表格内容 / 表单 label |
| `--text-base` | `1rem` | 16px | 正文 / 按钮 |
| `--text-lg` | `1.125rem` | 18px | 卡片标题 / 强调文字 |
| `--text-xl` | `1.25rem` | 20px | 二级页面标题 |
| `--text-2xl` | `1.5rem` | 24px | 一级页面标题 |
| `--text-3xl` | `1.875rem` | 30px | Dashboard 大数字 |

行高：`--leading-tight: 1.2`（标题）/ `--leading-normal: 1.5`（正文）/ `--leading-relaxed: 1.7`（长文）

**决策**：7 级阶梯够用，不引入 9-10 级（Element Plus 那样的）。字号过大（>30px）仅在 Dashboard 数字使用，不在普通文本出现。

### 2.4 间距系统（4 倍数）

| Token | 值 | 像素 | 典型用途 |
|-------|-----|------|----------|
| `--space-1` | `0.25rem` | 4px | 图标与文字间距 |
| `--space-2` | `0.5rem` | 8px | badge 内边距 / 表单内边距 |
| `--space-3` | `0.75rem` | 12px | 卡片内边距（紧凑） |
| `--space-4` | `1rem` | 16px | 卡片内边距（标准）/ 列表项间距 |
| `--space-5` | `1.25rem` | 20px | 表单字段间距 |
| `--space-6` | `1.5rem` | 24px | 区块内边距 |
| `--space-8` | `2rem` | 32px | 区块间距 / 弹窗内边距 |
| `--space-10` | `2.5rem` | 40px | 大区块间距 |
| `--space-12` | `3rem` | 48px | 页面主区域间距 |

**决策**：4 倍数（Tailwind 风格），但只暴露 9 档而非完整 16+ 档。避免设计师在"13px / 17px / 22px"这种无系统值上选。

### 2.5 圆角

| Token | 值 | 像素 | 典型用途 |
|-------|-----|------|----------|
| `--radius-sm` | `0.25rem` | 4px | badge / 标签 |
| `--radius-md` | `0.5rem` | 8px | **默认**，按钮 / 输入框 / 卡片 |
| `--radius-lg` | `0.75rem` | 12px | 大卡片 / 弹窗 |
| `--radius-xl` | `1rem` | 16px | 头像大圆角 |
| `--radius-full` | `9999px` | 9999px | 头像 / 圆形按钮 |

**决策**：8px 是 Vercel 默认，全系统 90% 元素使用 `--radius-md`。不要在小元素上用 12px+，也不要在大卡片上用 4px。

### 2.6 阴影

| Token | 值 | 用途 |
|-------|-----|------|
| `--shadow-sm` | `0 1px 2px rgba(0,0,0,0.04)` | hover 抬起 |
| `--shadow-md` | `0 2px 4px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.04)` | 卡片默认 |
| `--shadow-lg` | `0 4px 8px rgba(0,0,0,0.06), 0 2px 4px rgba(0,0,0,0.04)` | 弹窗 |

**决策**：Vercel 原版阴影极弱（0.04 alpha），Dashboard 等信息密集场景略增强（叠加层 0.05）。**不要**使用 Element Plus 的 `0 12px 32px rgba(0,0,0,0.14)` 这种立体阴影。

### 2.7 动效

| Token | 值 | 用途 |
|-------|-----|------|
| `--transition-fast` | `150ms ease` | hover / 颜色变化 |
| `--transition-normal` | `250ms ease` | 弹窗 / 抽屉 / Tab 切换 |
| `--transition-slow` | `400ms ease` | 路由切换 / 大块内容淡入 |

### 2.8 字体

```css
--font-sans: "Geist", ui-sans-serif, sans-serif, system-ui;
--font-mono: "Geist Mono", ui-monospace, monospace;
```

**决策**：Geist 是 Vercel 自研字体，Caduceus 通过 Vercel 模板引入。如果加载失败，回退到系统字体（`-apple-system, BlinkMacSystemFont` 等）。**不引入额外字体**（避免性能开销）。

### 2.9 主题切换策略

**三态**：light / dark / system

- **system**（默认）：不写 `data-theme`，跟随 OS `prefers-color-scheme`
- **light / dark**：写 `data-theme="light"` 或 `data-theme="dark"`，强制覆盖

实现位置：`frontend/src/stores/theme.js` 的 `useThemeStore`，通过 `data-theme` 属性挂载到 `<html>`。`main.js` 启动时立即调用 `useThemeStore().init()` 避免首屏闪白。

切换按钮：`UiThemeToggle.vue`，三态循环（☀ → ☾ → ◐ → ☀），位置在顶栏右上角和 Login 页右上角。

### 2.10 暗色模式特殊处理

**跨主题同色**：成功色 / 错误色（语义不能因主题变化）

**色阶反转**：背景从白系 → 黑系；前景从黑系 → 白系；不是简单 `invert()`

**Badge 配色反转策略**：浅色背景 + 深色前景（白天）↔ 深色背景 + 浅色前景（黑夜），保持 WCAG AA 对比度

---

## 3. 基础组件（Base Components）— v2.0 实际产出

放在 `frontend/src/components/ui/`。**强制只用令牌，不写硬编码值。**

| 组件 | 关键变体 / Props | v1.0 规划 | v2.0 实际 | 偏差说明 |
|------|----------------|-----------|-----------|---------|
| `UiButton` | variant: primary/secondary/ghost/danger × size: sm/md/lg × loading / block / disabled | ✅ Button | ✅ | 与规划一致 |
| `UiInput` | v-model / label / type(text/number/textarea) / error / hint / required / disabled | ✅ Input | ✅ | 与规划一致 |
| `UiSelect` | v-model / options: `[{label, value}]` 或 `[['label', value]]` / label / error / disabled / required | ✅ Select | ✅ | 与规划一致 |
| `UiCard` | title / hoverable / 默认插槽 / header / footer 插槽 | ✅ Card | ✅ | 与规划一致 |
| `UiBadge` | tone: neutral/info/success/warning/danger × size: sm/md | ✅ Badge | ✅ | 与规划一致 |
| `UiModal` | v-model / title / variant: center/drawer / size: sm/md/lg / closeable / closeOnOverlay / 自定义 footer 插槽 | ✅ Modal | ✅ | 与规划一致；ESC + body lock 内置 |
| `UiTabs` | activeKey(v-model) / tabs: `[{key, label, count?}]` | ✅ Tabs | ✅ | 与规划一致 |
| `UiEmptyState` | icon / title / description / 默认 CTA 插槽 | ✅ EmptyState | ✅ | 与规划一致 |
| `UiToast` | 消费 `useToastStore()`，无 props；tone 自动来自 toast 实例 | ✅ Toast | ✅ | 与规划一致；通过 store 调用 |
| `UiConfirm` | 消费 `useConfirmStore()`，无 props；通过 `useConfirm()(opts) → Promise<boolean>` 调用 | ⚠️ 未规划 | ✅ **新增** | 业务侧确认类操作统一入口 |
| `UiSpinner` | size: sm/md/lg × tone: primary/inverse × label 可选 | ⚠️ 未规划 | ✅ **新增** | 替代页面内裸 spinner |
| `UiThemeToggle` | 三态切换按钮，无 props | ⚠️ 未规划 | ✅ **新增** | 顶栏主题切换 |
| ~~UiTable~~ | — | ✅ Table | ❌ **未实现** | v2.0 用原生 table + UiCard 包装替代（业务量小，不必引入） |
| ~~UiAvatar~~ | — | ✅ Avatar | ❌ **未实现** | v2.0 用 UI 直接渲染首字母，业务量小 |
| ~~UiDropdown~~ | — | ✅ Dropdown | ❌ **未实现** | v2.0 用原生 `<details>` 或 Popover.js 替代（仅 NotificationBell 用到） |

**统一入口**：`frontend/src/components/ui/index.js`，业务代码用：

```js
import { UiButton, UiCard, UiBadge } from '@/components/ui'
```

---

## 4. 复合组件（Composite Components）— P1

v2.0 **未引入独立的复合组件**，业务页面直接组合基础组件实现：

| 原规划组件 | 实际替代方案 |
|-----------|--------------|
| `StatCard` | 直接用 `UiCard` + 内联大数字（`--text-3xl`）+ 变化文案 |
| `TimelineStep` | 直接用 `UiBadge`（状态色）+ `UiCard`（容器）+ 时间轴 div |
| `FieldRow` | 直接用 `UiInput` + label prop |
| `ResourceCard` | 直接用 `UiCard` + `UiBadge`（type + status tone） |
| `CommentItem` | 直接用 `UiCard`（基础） + 评论样式 |
| `NodePropertyPanel` | 用 `UiTabs` + `UiInput` 组合 |
| `MergeGroup` | 直接用 `UiCard` + 折叠 CSS |

**决策理由**：当前业务量下，复合组件的复用价值低于抽象成本。后续若出现 ≥3 个页面的同类复合需求，再回看本节补齐。

---

## 5. 关键页面 Polish — v2.0 实际完成

按"用户最高频路径"排序。✅ = 已完成；🟡 = 部分完成；⏳ = 待办。

| 顺序 | 页面 | v1.0 规划 | v2.0 状态 | 关键改进 |
|------|------|-----------|-----------|----------|
| 1 | `Login.vue` | ✅ 居中品牌区 + 卡片化表单 | ✅ 已 polish | token 化 + UiInput/UiButton；右上角主题切换 |
| 2 | `Dashboard.vue` | ✅ StatCard + 任务列表卡片化 | ✅ 已 polish | token 化 + UiCard/UiBadge/UiEmptyState；不再用渐变数字 |
| 3 | `TaskList.vue` | ✅ Table + 状态 Badge 统一 | ✅ 已 polish | UiCard 列表 + UiBadge 状态色 + 创建 UiModal + UiSelect 筛选；alert→toast |
| 4 | `TaskDetail.vue` | ✅ TimelineStep + 字段区卡片化 | ✅ 已 polish | 时间线 UiCard 化 + UiInput 字段 + UiModal 分享；UiConfirm 替代 confirm |
| 5 | `PipelineEditor.vue` | ✅ 节点配色统一 + Tabs 面板 | 🟡 部分 polish | 工具栏 token 化 + 全局 toast；节点视觉保留（Vue Flow 自定义成本高） |
| 6 | `ResourceList.vue` | ✅ 顶部筛选 + ResourceCard | ✅ 已 polish | UiTabs + UiCard + UiModal + UiConfirm；操作日志折叠 |
| 7 | `AdminPanel.vue` | ✅ Tabs 胶囊化 + 表格统一 | ✅ 已 polish | UiTabs + 3 个 UiModal + UiConfirm；warning/success 配色 token 化 |
| 8 | `SharePage.vue` | ✅ 公开页简化 | ✅ 已 polish | token 化 + UiCard + UiSpinner |
| 9 | `AppLayout.vue` | ✅ 顶栏侧栏对齐 + 通知铃 | ✅ 已 polish | 顶栏 + 侧栏 Vercel 风格重构；UiButton 统一 |
| 10 | `NotificationBell.vue` | ✅ 下拉卡片化 | ✅ 已 polish | token 化（11 处硬编码） |

**额外完成**：

- 子组件 token 化：`ResourceSelector.vue`（12 处硬编码）/ `TaskMergeGroup.vue`（11 处）/ `PipelineCanvas.vue`（67 处，布局层）
- 全局 `<UiToast />` 和 `<UiConfirm />` 挂在 `App.vue`

---

## 6. 体验细节

- ✅ **全局通知系统**：`useToast()` 替代 alert()，3 秒自动消失
- ✅ **全局确认弹窗**：`useConfirm()` 替代 confirm()，移动端友好
- ✅ **三态主题切换**：light / dark / system，localStorage 持久化
- ✅ **App.vue 挂载全局组件**：`<UiToast />` + `<UiConfirm />` 各一份
- 🟡 **Loading 骨架**：UiSpinner 已实现，但页面级骨架尚未统一（优先级 P2）
- ⏳ **EmptyState 全站统一**：组件已实现，但各页面空态文案/图标风格未统一（优先级 P2）
- ⏳ **错误边界**：未实现（优先级 P2）
- ⏳ **移动端响应式**：PipelineEditor 需桌面专属占位，breakpoints 工具类待添加（优先级 P1，详见第 9 节后续）

---

## 7. 全局 Store

| Store | 用途 | API |
|-------|------|-----|
| `useThemeStore` | 三态主题 + 持久化 | `mode` / `setMode(m)` / `init()` |
| `useToastStore` | 全局通知 | `push(msg, tone, opts)` / `remove(id)` / `success/error/info/warning(msg, opts?)` |
| `useConfirmStore` | 全局确认弹窗 | `open(opts) → Promise<boolean>` |

**Toast 使用示例**：

```js
const toast = useToast()
toast.success('保存成功')
toast.error('保存失败', { duration: 5000 })
toast.info('提示信息', { duration: 0, dismissible: true })
```

**Confirm 使用示例**：

```js
const confirm = useConfirm()
const ok = await confirm({
  title: '删除任务',
  message: '此操作不可撤销，确认删除？',
  tone: 'danger',
  confirmText: '删除',
  cancelText: '取消'
})
if (ok) {
  await api.deleteTask(taskId)
}
```

---

## 8. 风险与回滚

- **风险**：UI 大改可能引入未发现的视觉 bug
- **缓解**：
  - 所有改动仅在 `ui-redesign` 分支进行
  - 每个阶段独立可回滚
  - 关键页面（Login / Dashboard / TaskDetail）合并前需用户确认
- **回滚**：`git revert` PR 即可，main 不受影响
- **已发现并修复的 bug**：
  - AdminPanel.vue 中间 `import { watch }` 导致白屏 → 移到顶部
  - PipelineEditor.vue 缺失 `useToast` import 导致白屏 → 补 import

---

## 9. 后续 Spec 与路线图

- **Phase 5（响应式适配）**：基于现有 token 层扩展 breakpoints（640 / 768 / 1024 / 1280）+ 通用工具类
- **移动端边界**：PipelineEditor 桌面专属（"请用桌面访问"占位）；SharePage 完整移动端适配；UiModal 自动全屏
- **Phase 6（待评估）**：Table / Avatar / Dropdown 组件化（当前业务量小，未必必要）
- **Phase 7（待评估）**：错误边界 + 页面级 Loading 骨架 + EmptyState 文案统一

---

## 10. 设计原则（Design Principles）

后续开发应遵循以下原则，违反需在 PR 说明理由。

### 10.1 视觉原则

1. **同色语义不变量**：成功/错误色跨主题保持一致，不因主题变化
2. **圆角统一**：90% 元素使用 `--radius-md`，不要在小元素上用大圆角
3. **阴影克制**：阴影仅用于层级区分，不用于装饰
4. **间距 4 倍数**：所有间距值必须是 `--space-*` 之一，不写裸 px
5. **token 化**：所有颜色 / 字号 / 间距 / 圆角 / 阴影必须引用 token，**严禁硬编码**
6. **类型克制**：只用 7 级字号阶梯，不引入额外档位
7. **图表色专用**：5 个蓝色 `--color-chart-*` 仅用于数据可视化，不用作 UI 强调

### 10.2 组件原则

1. **状态色映射**：业务状态 → Badge tone 必须遵循第 2.2 节映射表
2. **弹窗统一用 UiModal**：禁止自写 modal（特殊情况需说明）
3. **通知统一用 useToast()**：禁止 alert() / console.log() 作为用户反馈
4. **确认操作统一用 useConfirm()**：禁止 confirm() / 自写确认弹窗
5. **导入统一从 index.js**：禁止 import 单个组件文件路径
6. **Props 透传**：基础组件 props 透传原生属性，避免 API 漂移

### 10.3 代码组织原则

1. **业务逻辑零改动承诺**：UI 重构只动 `<template>` 和 `<style>`，不动 `<script setup>` 的 state / API / 事件
2. **脚本逻辑完整保留**：所有 `ref` / `computed` / `onMounted` / `store` 调用 / API 调用必须保留
3. **感知层替换等价**：alert → toast 是用户感知等价；confirm → useConfirm 是 Promise 包装，调用方接收 true/false
4. **错误修复归 polish**：发现白屏 / 报错应作为 polish 的一部分修复，单独 commit

### 10.4 可访问性原则

1. **对比度**：所有文字/背景组合通过 WCAG AA（4.5:1 正文，3:1 大字）
2. **键盘导航**：所有可点击元素可通过 Tab 聚焦，ESC 关闭弹窗（UiModal 内置）
3. **Focus 环**：使用 `--color-ring` 作为聚焦环，不去除浏览器默认聚焦
4. **触摸目标**：按钮和链接的点击区域 ≥ 44×44px（移动端适配前置）
5. **语义化 HTML**：按钮用 `<button>`，链接用 `<a>`，不滥用 `<div @click>`

### 10.5 国际化原则

- 当前仅支持中文。预留 i18n 接口（`t()` 函数）但未集成 vue-i18n
- 文案集中在页面 template 中，不硬编码到组件 prop
- Badge tone 等枚举值国际化时需提供映射表

---

## 11. 组件 API 参考（Props / Emits）

详细列出每个基础组件的 API，供业务开发查阅。

### 11.1 UiButton

| Prop | 类型 | 默认值 | 说明 |
|------|------|-------|------|
| `variant` | `'primary' \| 'secondary' \| 'ghost' \| 'danger'` | `'primary'` | 视觉变体 |
| `size` | `'sm' \| 'md' \| 'lg'` | `'md'` | 尺寸 |
| `type` | `'button' \| 'submit' \| 'reset'` | `'button'` | 原生 button type |
| `loading` | `boolean` | `false` | 加载态（不可点击 + spinner） |
| `disabled` | `boolean` | `false` | 禁用态 |
| `block` | `boolean` | `false` | 块级（width: 100%） |

Emits: `click`（原生 click 事件透传）

### 11.2 UiInput

| Prop | 类型 | 默认值 | 说明 |
|------|------|-------|------|
| `modelValue` | `string \| number` | `''` | v-model |
| `label` | `string` | `''` | 顶部 label |
| `type` | `'text' \| 'number' \| 'textarea' \| 'password' \| 'email'` | `'text'` | 输入类型 |
| `placeholder` | `string` | `''` | 占位符 |
| `disabled` | `boolean` | `false` | 禁用 |
| `required` | `boolean` | `false` | 必填标识（红星） |
| `autocomplete` | `string` | `'off'` | 自动填充 |
| `error` | `string` | `''` | 错误提示（非空时输入框红边） |
| `hint` | `string` | `''` | 帮助提示 |

Emits: `update:modelValue` / `blur`

**特殊**：type='number' 自动 `Number()` 转换（无需 v-model.number）

### 11.3 UiSelect

| Prop | 类型 | 默认值 | 说明 |
|------|------|-------|------|
| `modelValue` | `string \| number \| null` | `''` | v-model |
| `label` | `string` | `''` | label |
| `placeholder` | `string` | `''` | 占位符 |
| `disabled` | `boolean` | `false` | 禁用 |
| `required` | `boolean` | `false` | 必填 |
| `error` | `string` | `''` | 错误提示 |
| `options` | `Array` | `[]` | 选项，支持 `[{label, value}]` 或 `['label', value]` |

Emits: `update:modelValue`

### 11.4 UiCard

| Prop | 类型 | 默认值 | 说明 |
|------|------|-------|------|
| `title` | `string` | `''` | 卡片标题（自动渲染 header） |
| `hoverable` | `boolean` | `false` | 悬浮抬起效果 |

Slots: `default`（内容）/ `header`（自定义头部，覆写 title）/ `footer`（底部操作区）

### 11.5 UiBadge

| Prop | 类型 | 默认值 | 说明 |
|------|------|-------|------|
| `tone` | `'neutral' \| 'info' \| 'success' \| 'warning' \| 'danger'` | `'neutral'` | 语义色 |
| `size` | `'sm' \| 'md'` | `'md'` | 尺寸 |

### 11.6 UiModal

| Prop | 类型 | 默认值 | 说明 |
|------|------|-------|------|
| `modelValue` | `boolean` | `false` | v-model（显示/隐藏） |
| `title` | `string` | `''` | 弹窗标题 |
| `variant` | `'center' \| 'drawer'` | `'center'` | 居中弹窗 / 右侧抽屉 |
| `size` | `'sm' \| 'md' \| 'lg'` | `'md'` | 居中弹窗宽度（360 / 480 / 640） |
| `closeable` | `boolean` | `true` | 是否可关闭（ESC / overlay） |
| `closeOnOverlay` | `boolean` | `true` | 点击 overlay 是否关闭 |

Emits: `update:modelValue` / `close`

Slots: `default`（主体）/ `footer`（底部按钮）

**特殊**：

- 打开时自动锁 body 滚动，关闭时恢复
- ESC 关闭（closeable=true 时）
- 移动端（<640px）自动全屏

### 11.7 UiTabs

| Prop | 类型 | 默认值 | 说明 |
|------|------|-------|------|
| `activeKey` | `string \| number` | 必填 | 当前激活 tab key |
| `tabs` | `Array<{key, label, count?}>` | 必填 | tab 列表 |

Emits: `update:activeKey`

### 11.8 UiEmptyState

| Prop | 类型 | 默认值 | 说明 |
|------|------|-------|------|
| `icon` | `string` | `''` | 图标 emoji 或文字 |
| `title` | `string` | `''` | 标题 |
| `description` | `string` | `''` | 副标题 |

Slots: `default`（CTA 按钮区）

### 11.9 UiToast / UiConfirm / UiSpinner / UiThemeToggle

无 props，通过 store 或内部状态管理。详见第 7 节。

---

## 12. 验证记录

### 12.1 构建验证

- `npm run build`：0 错误 0 警告（每次阶段完成后验证）

### 12.2 运行时验证

- 所有页面 `alert()` / `confirm()` 残留：0
- 主题三态切换：light / dark / system 均正常
- dark mode：所有 token 化的页面自动跟随
- 移动端 UiModal 自动全屏：手动 dev tools 验证 OK

### 12.3 业务逻辑契约对照

每个 polish 页面提交前，逐项检查 `<script setup>` 与 main 的 diff：

- 所有 `ref()` / `computed()` / `onMounted()` / `onUnmounted()` 数量与命名一致
- 所有 API 调用（`client.get(...)` / `client.post(...)` 等）路径与参数一致
- 所有 store 调用（`useAuthStore()` 等）一致
- 所有 emits 一致
- 所有路由跳转一致

**已通过验证**：8 个业务页面 + 5 个子组件 + AppLayout

---

## 13. 文件清单

### 13.1 新增文件（v2.0）

```
frontend/src/styles/
├── tokens.css             # 设计令牌（颜色 / 字号 / 间距 / 圆角 / 阴影 / 动效 / 语义色 / dark mode）
└── base.css               # reset + body 基础样式

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
└── index.js               # 统一导出

frontend/src/stores/
├── theme.js               # 三态主题
├── toast.js               # 全局通知
└── confirm.js             # 全局确认弹窗
```

### 13.2 修改文件（v2.0）

- `frontend/src/main.js` — 引入 tokens.css + base.css + theme store init
- `frontend/src/App.vue` — 挂载 `<UiToast />` + `<UiConfirm />`
- `frontend/src/components/AppLayout.vue` — token 化 + UiButton + UiThemeToggle
- `frontend/src/components/NotificationBell.vue` — token 化
- `frontend/src/components/ResourceSelector.vue` — token 化 + UiBadge + 移动端 CSS
- `frontend/src/components/TaskMergeGroup.vue` — token 化 + UiBadge
- `frontend/src/components/PipelineCanvas.vue` — 布局层 token 化
- 8 个 view 文件：`Login.vue` / `Dashboard.vue` / `TaskList.vue` / `TaskDetail.vue` / `ResourceList.vue` / `AdminPanel.vue` / `SharePage.vue` / `PipelineEditor.vue`

---

## 14. 变更记录

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-07-04 | 初始规划文档（任务拆分 / 风险 / 后续 Spec） |
| v2.0 | 2026-07-04 | 实际落地后重写：新增第 2 节设计风格基线、第 5-7 节实际完成状态、第 10-13 节设计原则与 API 参考 |