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

## 11.3 UiSelect

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