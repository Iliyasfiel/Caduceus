# UI 组件 API 参考（Props / Emits / Slots）

> 📦 **临时文档**（位于 [`dev-tmp/design/`](./)）。从原 `caduceus-ui-redesign.md` §11 拆分而来。
>
> 引用方：[`caduceus-design.md` §十二、基础组件清单](../../designingDocument/caduceus-design.md)
>
> 清理规则：按 `.trae/rules/project_rules.md` “临时文件（dev-tmp）” 一节，删除前须先向用户确认是否需要将组件 API 沉淀到正式设计文档或自动生成到代码注释里。

## 11.1 UiButton

| Prop | 类型 | 默认值 | 说明 |
|------|------|-------|------|
| `variant` | `'primary' \| 'secondary' \| 'ghost' \| 'danger'` | `'primary'` | 视觉变体 |
| `size` | `'sm' \| 'md' \| 'lg'` | `'md'` | 尺寸 |
| `type` | `'button' \| 'submit' \| 'reset'` | `'button'` | 原生 button type |
| `loading` | `boolean` | `false` | 加载态（不可点击 + spinner） |
| `disabled` | `boolean` | `false` | 禁用态 |
| `block` | `boolean` | `false` | 块级（width: 100%） |

Emits: `click`（原生 click 事件透传）

## 11.2 UiInput

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

## 11.3 UiSelect（v2 — 自渲染 popper）

> 自 v2 起为前端**标准下拉组件**。禁止使用原生 `<select>` 元素。
>
> 改造原因（2026-07-06）：原实现用原生 `<select>` + `appearance: none`，下拉 `<option>` 由浏览器接管渲染，**暗色模式下背景/文字无法跟随设计令牌**。v2 完全自渲染 popper（Teleport 到 body），暗色模式天然正确，并新增多选 / 搜索 / 异步能力。
>
> 完整改造记录：[ui-design-principles-and-polish.md §5.5](./ui-design-principles-and-polish.md)

### Props

| Prop | 类型 | 默认值 | 说明 |
|------|------|-------|------|
| `modelValue` | `string \| number \| Array \| null` | `''` | v-model。单选时为标量；多选时为 Array |
| `options` | `Array` | `[]` | 选项。两种格式：`[{label, value, disabled?}]` 或 `[['label', value], ...]`（兼容 tuple）|
| `label` | `string` | `''` | 顶部 label |
| `placeholder` | `string` | `''` | 占位符 |
| `size` | `'sm' \| 'md'` | `'md'` | 尺寸。`sm` 用于 toolbar / 表格内嵌等紧凑场景 |
| `disabled` | `boolean` | `false` | 禁用 |
| `required` | `boolean` | `false` | 必填标识（红星）|
| `error` | `string` | `''` | 错误提示（非空时输入框红边）|
| `hint` | `string` | `''` | 帮助提示 |
| `searchable` | `boolean` | `false` | 启用搜索框过滤（选项较多时）|
| `multiple` | `boolean` | `false` | 启用多选模式（modelValue 改为 Array）|
| `asyncLoader` | `(query: string) => Promise<Array>` | `null` | 异步加载。启用后 `options` prop 失效，由 asyncLoader 返回值决定 |
| `searchPlaceholder` | `string` | `''` | 搜索框 placeholder（默认"搜索..."）|
| `emptyText` | `string` | `''` | 无匹配项时的提示（默认"无匹配项"）|
| `maxDisplayChips` | `number` | `3` | 多选 trigger 显示上限；超出部分显示 `+N` |

### Emits

| 事件 | 参数 | 说明 |
|------|------|------|
| `update:modelValue` | `value` | v-model 双向绑定 |
| `change` | `value` | 选中值变更（与 update 同步触发）|
| `blur` | - | popper 关闭时触发 |

### 行为规范

| 交互 | 行为 |
|------|------|
| 点击 trigger | 打开 / 关闭 popper |
| 鼠标 hover option | 高亮该 option |
| 鼠标点击 option | 单选：选中 + 关闭；多选：切换选中状态，**不关闭** |
| ↑ / ↓ | 移动高亮（自动跳过 disabled）|
| Enter | 选中当前高亮项（单选关闭 / 多选不关闭）|
| Esc | 关闭（不动 modelValue，焦点回到 trigger）|
| Tab | 关闭（保留选中）|
| 点击 popper 外部 | 关闭（保留选中）|

### 选项格式规范

**对象格式**（推荐）：
```js
[{ label: '草稿', value: 'draft' }, { label: '待处理', value: 'pending' }]
```

**Tuple 格式**（兼容老代码）：
```js
[['草稿', 'draft'], ['待处理', 'pending']]
```

**带 disabled**（仅对象格式支持）：
```js
[{ label: '发起人', value: 'initiator' },
 { label: '执行人', value: 'executor', disabled: true }]
```

### 异步加载示例

```vue
<UiSelect
  v-model="pipelineId"
  :asyncLoader="searchPipelines"
  searchable
  placeholder="搜索管线"
/>
```
```js
async function searchPipelines(query) {
  const { data } = await api.get('/pipelines/', { params: { search: query } })
  return data.results.map(p => ({ label: p.name, value: p.id }))
}
```

### 设计要点

- **零外部依赖**：手写定位 + 键盘导航 + ARIA
- **完全跟设计令牌走**：背景/文字/边框/阴影全部用 `var(--bg-elevated)` / `var(--text-primary)` / `var(--border-default)` / `var(--shadow-lg)` 等
- **Teleport 到 body**：避免被父级 `overflow: hidden` / `transform` 裁剪
- **z-index 1001**：比 UiModal（1000）高一层
- **自动 flip**：视口下方放不下时自动向上展开
- **响应式**：移动端 `max-width: 95vw`，不溢出
- **可访问性**：完整 ARIA（`role="listbox"` / `role="option"` / `aria-selected` / `aria-expanded` / `aria-multiselectable`）；表单兜底保留隐藏的原生 `<select>`

### Vercel 风格视觉

- 触发器：扁平、极轻量边框、紧凑 padding（md 6px 10px / sm 3px 8px）、font-size 13/12、line-height 1.2
- popper：纯色面板 + 微圆角（8px）+ 极轻双层阴影、暗色加深
- 选项：紧凑 padding（7px 8px）、高亮是中性灰（`--bg-hover`，**不是 primary 蓝**）
- 选中态：仅 `font-weight: 500` 字重加重，无彩色
- 多选 checkbox：14×14，黑白反转（Vercel 风）
- 过渡：120ms cubic-bezier(0.16, 1, 0.3, 1) 极简 fade + 微 scale
- 滚动条：8px 细滚动条 + padding 容器

## 11.4 UiCard

| Prop | 类型 | 默认值 | 说明 |
|------|------|-------|------|
| `title` | `string` | `''` | 卡片标题（自动渲染 header） |
| `hoverable` | `boolean` | `false` | 悬浮抬起效果 |

Slots: `default`（内容）/ `header`（自定义头部，覆写 title）/ `footer`（底部操作区）

## 11.5 UiBadge

| Prop | 类型 | 默认值 | 说明 |
|------|------|-------|------|
| `tone` | `'neutral' \| 'info' \| 'success' \| 'warning' \| 'danger'` | `'neutral'` | 语义色 |
| `size` | `'sm' \| 'md'` | `'md'` | 尺寸 |

## 11.6 UiModal

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

## 11.7 UiTabs

| Prop | 类型 | 默认值 | 说明 |
|------|------|-------|------|
| `activeKey` | `string \| number` | 必填 | 当前激活 tab key |
| `tabs` | `Array<{key, label, count?}>` | 必填 | tab 列表 |

Emits: `update:activeKey`

## 11.8 UiEmptyState

| Prop | 类型 | 默认值 | 说明 |
|------|------|-------|------|
| `icon` | `string` | `''` | 图标 emoji 或文字 |
| `title` | `string` | `''` | 标题 |
| `description` | `string` | `''` | 副标题 |

Slots: `default`（CTA 按钮区）

## 11.9 UiToast / UiConfirm / UiSpinner / UiThemeToggle / UiIcon

无 props（UiIcon 除外），通过 store 或内部状态管理。详见 [ui-design-principles-and-polish.md §2 全局 Store](./ui-design-principles-and-polish.md)。

**UiIcon 专属 Props**：

| Prop | 类型 | 默认值 | 说明 |
|------|------|-------|------|
| `name` | `string` | 必填 | 图标名，对应 PATHS 中的 key（bell / menu / close / sun / moon / system / check / x / info / warning / clipboard） |
| `size` | `number \| string` | `20` | 像素 |
| `strokeWidth` | `number \| string` | `1.75` | 描边宽度 |

## 11.10 全局 Store API

**useThemeStore**

| API | 说明 |
|-----|------|
| `mode` | 当前模式：`'light' \| 'dark' \| 'system'` |
| `setMode(m)` | 设置模式并持久化到 localStorage |
| `init()` | 启动时调用：读取 localStorage → 设置 `<html data-theme>` |

**useToastStore**

```js
const toast = useToast()
toast.success('保存成功')
toast.error('保存失败', { duration: 5000 })
toast.info('提示信息', { duration: 0, dismissible: true })
toast.warning('请检查输入')
```

**useConfirmStore**

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

**useNotificationsStore**

| API | 说明 |
|-----|------|
| `list` | 通知列表（ref） |
| `unreadCount` | 未读数（computed） |
| `fetchList()` | 拉取最新通知 |
| `markAsRead(id)` | 单条标记已读 |
| `markAllAsRead()` | 全部标记已读 |

**useAuthStore**

| API | 说明 |
|-----|------|
| `user` | 当前用户对象 |
| `isAuthenticated` | 是否已登录 |
| `login(username, password)` | 登录 |
| `logout()` | 登出 |
| `checkAuth()` | 启动时验证 token 有效性 |