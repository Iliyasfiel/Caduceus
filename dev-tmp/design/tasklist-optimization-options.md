# TaskList 优化方向 — 10 项技术债 + 建议

> **来源**：2026-07-06 在 `feature/task-list-ui-optimize` 分支讨论。
> **状态**：草稿，未决定哪几项要做。**待用户（开发者）勾选 / 排序 / 增删后，再进入正式设计阶段**。
> **关联**：[TaskList.vue](../../../frontend/src/views/TaskList.vue) · [TaskMergeGroup.vue](../../../frontend/src/components/TaskMergeGroup.vue) · [stores/tasks.js](../../../frontend/src/stores/tasks.js)

---

## 概念说明

"技术债"指 **从代码层面读出的可改进点**（不一定等于"用户视角的痛点"，但很多都是先写出来一起看、再决定）。
"建议"是 **如果某项要做，推荐怎么做的初步思路**，具体方案待选定后再细化。

每项用统一结构：
- **现状**：代码层面观察到的具体问题（带行号 / 链接）
- **影响**：不修会带来什么后果（用户 / 开发 / 设计一致性）
- **建议**：推荐方案 + 备选 + 工作量预估
- **优先级**：🔴 高 / 🟡 中 / 🟢 低 / ⚪ 不动

---

## 🚨 类别 A：真 bug / 设计系统一致性

### A-1. TaskMergeGroup 没接设计系统

- **现状**：见 [TaskMergeGroup.vue:89-202](../../../frontend/src/components/TaskMergeGroup.vue#L89-L202)。全部样式硬编码：
  - `border: 1px solid #e5e7eb` / `background: #f9fafb` 等浅色 hex
  - 状态标签自行实现 `<span class="card-status status-X">`（[TaskMergeGroup.vue:167-178](../../../frontend/src/components/TaskMergeGroup.vue#L167-L178)），**没用 UiBadge**
  - 任务列表主视图已经用 UiBadge / UiCard / UiEmptyState，**合并组组件完全脱节**
- **影响**：
  - 🔴 **暗色模式完全不工作**（同 UiSelect 原 bug）
  - 主题切换时合并组样式不变
  - 新增状态枚举需要手动改两套样式（UiBadge + 硬编码）
- **建议**：
  1. 用 `UiBadge` 替换自写 `<span class="card-status">`，复用 tone 映射（[caduceus-design.md §11.2 状态色映射](../../designingDocument/caduceus-design.md)）
  2. 全部硬编码颜色换成 `var(--bg-surface)` / `var(--border-subtle)` / `var(--bg-hover)` 等 token
  3. 把 `.merge-group` 整个用 `UiCard` 包一层，去掉自写结构
- **工作量**：~30 分钟
- **优先级**：🔴 高（暗色模式 bug 必须修）

### A-2. TaskMergeGroup 仍在用 emoji 字符作为箭头

- **现状**：[TaskMergeGroup.vue:9](../../../frontend/src/components/TaskMergeGroup.vue#L9) `{{ expanded ? '▼' : '▶' }}`
- **影响**：违反 [ui-design-principles-and-polish.md §1.2 第 7 条](../../../dev-tmp/design/ui-design-principles-and-polish.md)（图标统一走 UiIcon）
- **建议**：替换为 `<UiIcon name="chevron-down" />` + `is-open` 类控制旋转
- **工作量**：5 分钟（含 A-1 一起做）
- **优先级**：🟡 中（顺手做即可）

---

## 🎨 类别 B：视觉 / 信息密度

### B-1. 任务卡片信息密度可优化

- **现状**：[TaskList.vue:62-87](../../../frontend/src/views/TaskList.vue#L62-L87) 卡片只展示：
  - `status` · `priority` · `created_at` · `title` · `description`（100 字截断）· `creator_name`
  - **没展示**：`pipeline_name` / `current_node`（管线当前阶段）· `assignments.length`（执行人数）· `due_date`（如果有）· `tags`
- **影响**：用户需要点进详情才能看到管线进度，**列表页信息密度低**，反复点开浪费操作
- **建议**：
  - 卡片增加**管线名 + 当前节点**两行（如果任务绑定了 pipeline）
  - 卡片 footer 增加**执行人头像组**（assignments 前 3 个 + "+N"）
  - 后端列表 API 已经返回这些字段，[stores/tasks.js:7-10](../../../frontend/src/stores/tasks.js#L7-L10) `loadTasks()` 直接拿到
- **备选**：不动卡片密度，提供**紧凑视图 / 详情视图切换**，详情视图允许鼠标 hover 显示完整字段
- **工作量**：~40 分钟（视觉调整 + 后端字段未返回的话加 API）
- **优先级**：🟡 中（信息密度是 TaskList 优化的核心议题之一）

### B-2. 卡片 hover 反馈弱

- **现状**：[UiCard.vue:43-44](../../../frontend/src/components/ui/UiCard.vue#L43-L44) `hoverable` 时只 `box-shadow` 微变，没有边框强调
- **影响**：整个卡片可点击（`@click="goToDetail"`），但**没有视觉提示**告诉用户"这是个 link"
- **建议**：增加 `border-color: var(--color-primary)` 在 hover 时轻微透出，或左边缘加 4px 色条
- **工作量**：10 分钟
- **优先级**：🟢 低（属于 polish）

---

## 📱 类别 C：响应式

### C-1. 卡片网格断点策略欠优化

- **现状**：[TaskList.vue:56](../../../frontend/src/views/TaskList.vue#L56) `grid-template-columns: repeat(auto-fill, minmax(320px, 1fr))`
- **影响**：
  - 手机上：320px 卡片在 375px 屏宽下最多 1 列，但有大量空白
  - 平板（768px）：2 列，但卡片 320px 显得窄
  - 桌面（1280px+）：3-4 列
- **建议**：显式断点 + 列数
  ```css
  .grid {
    display: grid;
    gap: var(--space-4);
    /* mobile: 1 列；tablet: 2 列；desktop: 3 列；wide: 4 列 */
    grid-template-columns: 1fr;
  }
  @media (min-width: 768px) { grid-template-columns: repeat(2, 1fr); }
  @media (min-width: 1280px) { grid-template-columns: repeat(3, 1fr); }
  @media (min-width: 1920px) { grid-template-columns: repeat(4, 1fr); }
  ```
- **备选**：保持 auto-fill 但 minmax 调整（`minmax(min(100%, 320px), 1fr)`）
- **工作量**：10 分钟
- **优先级**：🟡 中（响应式在 §13 政策里是 Web-only 风格的体现）

---

## 🔍 类别 D：筛选 / 搜索

### D-1. 筛选条缺少"已应用筛选条件可视化"

- **现状**：[TaskList.vue:16-44](../../../frontend/src/views/TaskList.vue#L16-L44) 顶栏只展示一个"全部状态"select + 搜索框 + 切换按钮；筛选条件**没有任何 chip 提示**
- **影响**：
  - 用户选了"待处理"过滤后，看不出来当前在过滤什么
  - 刷新页面筛选就丢（URL 不反映）
- **建议**：
  - 筛选条下方加一行 `applied-filters`，每个 chip 可单独移除（×）
  - 关键筛选条件同步到 URL query（如 `?status=pending`），刷新保留
- **工作量**：~30 分钟（chip UI + URL 同步）
- **优先级**：🟢 低（属于 polish，但能显著提体验）

### D-2. 搜索框没有 debounce / 必须按 Enter

- **现状**：[TaskList.vue:27](../../../frontend/src/views/TaskList.vue#L27) `@keydown.enter="applySearch"`，输字符不刷新结果
- **影响**：用户输完得按 Enter 才生效，**不像 GitHub / Linear 的"边输边搜"体验**
- **建议**：输入时 `debounce 250ms` 自动触发搜索（不需要按 Enter）；Enter 仍可作为显式触发（顺手）
- **工作量**：10 分钟
- **优先级**：🟢 低（微优化）

---

## ⚙️ 类别 E：交互 / 行为 / 缺能力

### E-1. 加载态 / 错误态缺失

- **现状**：[TaskList.vue:48-50](../../../frontend/src/views/TaskList.vue#L48-L50) 只有 `<div v-if="loading">加载中...</div>` 一行文字，**没有骨架屏**；错误完全没处理
- **影响**：
  - 网络慢时只看到"加载中..."文字，体验差
  - API 失败时空白页（store.loadTasks 抛错时没有任何 capture）
- **建议**：
  - 用 `UiSkeleton`（如果存在）或自写骨架卡片 3-4 个，列表区布局稳定
  - `try/catch` 包裹 `store.loadTasks`，失败时 `useToast().error('加载失败：xxx')` + 显示 UiEmptyState 错误版本
- **工作量**：~30 分钟
- **优先级**：🟡 中（基础健壮性）

### E-2. 空态缺少 CTA

- **现状**：[TaskList.vue:110-114](../../../frontend/src/views/TaskList.vue#L110-L114) `<UiEmptyState title="暂无任务" description="点击右上角创建第一个任务">` — 但**没有按钮**
- **影响**：用户得自己去找"创建任务"按钮，路径不直观
- **建议**：UiEmptyState 增加 `action` slot + "新建第一个任务"按钮（如果用户有创建权限；权限来自 auth store）
- **工作量**：10 分钟
- **优先级**：🟢 低（细节但显著）

### E-3. 批次操作（多选 + 批量）

- **现状**：所有卡片只能单独点击，没有 checkbox；没有批量操作工具栏
- **影响**：任务多了以后（≥ 50 个），批量删 / 批量改状态 / 批量分配极度刚需
- **建议**：
  - 增加"进入批量模式"开关（顶栏 toggle）
  - 批量模式下每张卡左上出现 checkbox + 全选
  - 底栏出现"已选 N 项 - [操作：改状态/分配/删除/取消]"
- **备选（轻量版）**：保持单选点击，卡片右上加三个 icon 按钮（编辑 / 删除 / 分配）— 工作量小很多
- **工作量**：~2 小时（完整批量）/ 30 分钟（轻量版）
- **优先级**：🟢 低（属于新能力，V1.x 不是强刚需）

### E-4. 创建任务后定位 / URL 反映

- **现状**：[TaskList.vue:160-167](../../../frontend/src/views/TaskList.vue#L160-L167) `onTaskCreated()` 关闭 modal + `loadTasks()` 重拉，**没滚到新任务 / 不更新 URL**
- **影响**：用户创建后看到的是第一页，没有"我创建了任务就在这里"的反馈
- **建议**：
  - 创建成功后 `loadTasks()` 然后**滚到列表顶** + 用 UiToast "已创建任务 XXX"
  - 后续增强：highlight 新任务卡片 2 秒
- **工作量**：10 分钟
- **优先级**：🟢 低（细节）

---

## 📊 类别 F：性能 / 数据流

### F-1. TaskMergeGroup 内的子卡片没有用 UiCard

- **现状**：[TaskMergeGroup.vue:15-31](../../../frontend/src/components/TaskMergeGroup.vue#L15-L31) `<div class="sub-task-card">` — 自写结构硬编码样式
- **影响**：和 TaskList 主视图卡片**视觉不统一**（合并组内的任务卡看起来跟外面的不一样）
- **建议**：复用 TaskList 里的卡片段，提取成 `<TaskListItem :task="t" />` 子组件
- **工作量**：~1 小时（提取 + 重构 + 关联调整）
- **优先级**：🟡 中（一致性是当前问题域核心）

---

## ✂️ 不在本期优化范围 / 可暂缓

| 项 | 原因 |
|---|---|
| TaskDetail / TaskCreate 弹窗的二次打磨 | 本次只动 TaskList 页本身 |
| TaskManager.vue (如果存在) 重写 | 与本期主题无关 |
| 搜索后端（如果有）的全文搜索能力 | 性能 / 后端能力问题，超出"界面优化"范围 |
| 数据导出 / CSV | 新能力，未提需求 |

---

## 📋 待用户决策

请基于这份清单告知我：

1. **要做哪些**（勾选 / 直接打字）
2. **哪些不做 / 哪些暂缓**
3. **优先顺序**（哪些必须先做 / 哪些可以放最后）
4. **有没有补充**（你看到的我没看到的痛点）

然后我会：
- 把选中项按依赖关系排成实施批次
- 写一份正式的 `tasklist-polish-design.md`（含 scope / out-of-scope / 验收标准）
- 再写 `tasklist-polish-plan.md` 进入 dev-tmp
- 然后才动代码

---

## 相关文档

- [uiselect-v2-plan.md](./uiselect-v2-plan.md) — 之前完成的 UiSelect 重构计划，参考格式
- [ui-design-principles-and-polish.md](./ui-design-principles-and-polish.md) — 设计原则与 polish 历史
- [caduceus-design.md](../../designingDocument/caduceus-design.md) §11 / §12 / §13 — 设计语言 / 基础组件 / 跨平台策略
- [project_rules.md](../../.trae/rules/project_rules.md) §设计文档驱动开发 — 任何改动先写设计再写代码