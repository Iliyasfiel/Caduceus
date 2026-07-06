# UiSelect v2 重构计划（自渲染 popper + 暗色修复）

> 来源：2026-07-06 在 `feature/task-list-ui-optimize` 分支上讨论。
> 触发问题：TaskList 创建任务弹窗 → 管线模板下拉 [frontend/src/views/TaskList.vue:142](../../../frontend/src/views/TaskList.vue#L142) 在暗色模式下的显示问题。
>
> 状态：**计划已确定，等待用户（开发者）确认后实施**。
> 关联：与 [ui-design-principles-and-polish.md](./ui-design-principles-and-polish.md) 互补；完成时会在该文件追加 v2 重构记录。

---

## 🎯 目标（Goals）

修复 UiSelect 暗色模式显示问题 + 提供自渲染 popper 的标准下拉面板 + 暴露 3 个可选能力（搜索 / 多选 / 异步）作为未来扩展，但**本次不绑定到现有 3 个调用点**。

## 🚫 非目标（Non-Goals）

- 不引入 floating-ui / tippy.js 等外部依赖
- 不重写其他 UI 组件（UiInput / UiButton / UiBadge 等不动）
- 不动 TaskList.vue / ResourceList.vue 的现有调用（保持向后兼容）
- 不实现 optgroup 分组、虚拟滚动、trigger 自定义 slot
- 不解决原生 `<select>` 在 PipelineCanvas / TaskDetail / AdminPanel 等地方"也暗色不对"的问题（本次范围只在 UiSelect 组件）

## 📦 当前分支

`feature/task-list-ui-optimize`（已上游推送到 GitHub，含 `94c0b02` doc commit）

---

## 🔧 实施步骤

### 步骤 1：改写 [frontend/src/components/ui/UiSelect.vue](../../../frontend/src/components/ui/UiSelect.vue)

**模板部分**（约 80 行）：

```html
<div class="ui-select" :class="cssClass">
  <button class="ui-select__trigger" type="button"
          :id="triggerId" :aria-haspopup="'listbox'"
          :aria-expanded="open" :aria-controls="listboxId"
          :aria-disabled="disabled" :aria-invalid="!!error"
          @click="toggleOpen" @keydown="onTriggerKeydown">
    <span class="ui-select__value" :class="{'is-placeholder': isPlaceholder}">
      {{ displayText }}
    </span>
    <span class="ui-select__chevron" :class="{'is-open': open}">▾</span>
  </button>

  <Teleport to="body">
    <Transition name="ui-select-pop">
      <ul v-if="open && !disabled"
          ref="listboxEl"
          class="ui-select__popper"
          :class="popperCssClass"
          :style="popperStyle"
          :id="listboxId"
          role="listbox"
          :aria-multiselectable="multiple || undefined"
          @keydown="onListboxKeydown"
          tabindex="-1">
        <li v-if="searchable" class="ui-select__search">
          <input ref="searchInputEl" v-model="searchQuery"
                 type="text" :placeholder="searchPlaceholder || '搜索...'"
                 class="ui-select__search-input"
                 @keydown.stop />
        </li>
        <li v-if="multiple && modelValue.length > 0" class="ui-select__chips">
          <span v-for="chip in displayChips" class="ui-select__chip">
            {{ chip.label }}
            <button type="button" class="ui-select__chip-remove"
                    @click.stop="removeValue(chip.value)"
                    :aria-label="`移除 ${chip.label}`">×</button>
          </span>
          <span v-if="extraChipCount > 0" class="ui-select__chip is-extra">+{{ extraChipCount }}</span>
        </li>
        <li v-if="filteredOptions.length === 0" class="ui-select__empty">
          {{ emptyText || '无匹配项' }}
        </li>
        <li v-for="(opt, idx) in filteredOptions" :key="opt.value"
            class="ui-select__option"
            :class="{
              'is-highlighted': idx === highlightIndex,
              'is-selected': isSelected(opt.value),
              'is-disabled': opt.disabled
            }"
            role="option"
            :aria-selected="isSelected(opt.value)"
            :aria-disabled="opt.disabled || undefined"
            @mouseenter="highlightIndex = idx"
            @mousedown.prevent="selectOption(opt)">
          <span v-if="multiple" class="ui-select__checkbox"
                :class="{'is-checked': isSelected(opt.value)}">
            {{ isSelected(opt.value) ? '✓' : '' }}
          </span>
          <span class="ui-select__option-label">{{ opt.label }}</span>
        </li>
      </ul>
    </Transition>
  </Teleport>

  <!-- 表单兜底：隐藏的原生 select，用于表单序列化 / 无障碍 fallback -->
  <select v-show="false" :value="serializedValue"
          @change="onNativeChange" tabindex="-1" aria-hidden="true">
    <option v-for="opt in options" :key="String(opt.value)" :value="opt.value">{{ opt.label }}</option>
  </select>

  <p v-if="error" class="ui-field__error">{{ error }}</p>
  <p v-else-if="hint" class="ui-field__hint">{{ hint }}</p>
</div>
```

**script setup 部分**（约 120 行）：

```js
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick, useId } from 'vue'

const props = defineProps({
  modelValue: { type: [String, Number, Array, null], default: '' },
  options: { type: Array, default: () => [] },
  label: String, placeholder: String, disabled: Boolean, required: Boolean,
  error: String, hint: String,
  // 新能力（默认关闭，老代码零行为变化）
  searchable: { type: Boolean, default: false },
  multiple: { type: Boolean, default: false },
  asyncLoader: { type: Function, default: null },
  searchPlaceholder: { type: String, default: '' },
  emptyText: { type: String, default: '' },
  maxDisplayChips: { type: Number, default: 3 }
})

const emit = defineEmits(['update:modelValue', 'change', 'blur'])

const open = ref(false)
const highlightIndex = ref(0)
const searchQuery = ref('')
const triggerEl = ref(null)
const listboxEl = ref(null)
const searchInputEl = ref(null)
const popperPos = ref({ top: 0, left: 0, width: 0, placement: 'bottom' })
const localOptions = ref([])
const debounceTimer = ref(null)

const id = useId()
const triggerId = `ui-select-trigger-${id}`
const listboxId = `ui-select-listbox-${id}`

const isMultiple = computed(() => props.multiple || Array.isArray(props.modelValue))
const sourceOptions = computed(() => props.asyncLoader ? localOptions.value : props.options)
const filteredOptions = computed(() => {
  const opts = sourceOptions.value
  if (!props.searchable || !searchQuery.value) return opts
  const q = searchQuery.value.toLowerCase()
  return opts.filter(o => String(o.label).toLowerCase().includes(q))
})
const isPlaceholder = computed(() => isMultiple.value
  ? !(props.modelValue && props.modelValue.length)
  : !props.modelValue)
const displayText = computed(() => isMultiple.value
  ? (props.modelValue?.length ? `${props.modelValue.length} 项已选` : (props.placeholder || ''))
  : (props.options.find(o => o.value === props.modelValue)?.label || props.placeholder || ''))
const displayChips = computed(() => {
  const sel = props.modelValue || []
  const max = props.maxDisplayChips
  return sel.slice(0, max).map(v => {
    const opt = props.options.find(o => o.value === v)
    return { value: v, label: opt?.label || String(v) }
  })
})
const extraChipCount = computed(() =>
  Math.max(0, (props.modelValue?.length || 0) - props.maxDisplayChips))
const isSelected = (v) => isMultiple.value
  ? (props.modelValue || []).includes(v)
  : props.modelValue === v
const serializedValue = computed(() => isMultiple.value ? '' : (props.modelValue ?? ''))
const cssClass = computed(() => ({
  'ui-select--open': open.value,
  'ui-select--disabled': props.disabled,
  'ui-select--multiple': isMultiple.value,
  'ui-select--error': !!props.error
}))
const popperCssClass = computed(() => `ui-select__popper--${popperPos.value.placement}`)
const popperStyle = computed(() => ({
  position: 'fixed',
  top: popperPos.value.top + 'px',
  left: popperPos.value.left + 'px',
  width: popperPos.value.width + 'px',
  zIndex: 1001
}))

function toggleOpen() { if (!props.disabled) open.value ? closePopper() : openPopper() }
async function openPopper() {
  if (open.value) return
  open.value = true
  await nextTick()
  computePopperPosition()
  searchInputEl.value?.focus()
  highlightIndex.value = Math.max(0, filteredOptions.value.findIndex(o => isSelected(o.value)))
}
function closePopper() { open.value = false; searchQuery.value = ''; highlightIndex.value = 0 }
function selectOption(opt) {
  if (opt.disabled) return
  if (isMultiple.value) {
    const cur = props.modelValue || []
    const next = cur.includes(opt.value)
      ? cur.filter(v => v !== opt.value)
      : [...cur, opt.value]
    emit('update:modelValue', next)
    emit('change', next)
  } else {
    emit('update:modelValue', opt.value)
    emit('change', opt.value)
    closePopper()
  }
}
function removeValue(v) {
  if (!isMultiple.value) return
  emit('update:modelValue', (props.modelValue || []).filter(x => x !== v))
}
function onTriggerKeydown(e) {
  if (props.disabled) return
  if (['ArrowDown', 'ArrowUp', 'Enter', ' '].includes(e.key)) {
    e.preventDefault()
    openPopper()
  }
}
function onListboxKeydown(e) {
  if (e.key === 'Escape') { e.preventDefault(); closePopper(); triggerEl.value?.focus() }
  else if (e.key === 'Tab') { closePopper() }
  else if (e.key === 'ArrowDown') { e.preventDefault(); moveHighlight(1) }
  else if (e.key === 'ArrowUp') { e.preventDefault(); moveHighlight(-1) }
  else if (e.key === 'Enter') {
    e.preventDefault()
    const o = filteredOptions.value[highlightIndex.value]
    if (o) selectOption(o)
  }
}
function moveHighlight(delta) {
  const opts = filteredOptions.value
  if (opts.length === 0) return
  let i = highlightIndex.value
  for (let step = 0; step < opts.length; step++) {
    i = (i + delta + opts.length) % opts.length
    if (!opts[i].disabled) { highlightIndex.value = i; return }
  }
}
function onClickOutside(e) {
  if (!open.value) return
  if (triggerEl.value?.contains(e.target)) return
  if (listboxEl.value?.contains(e.target)) return
  closePopper()
}
function computePopperPosition() {
  if (!triggerEl.value) return
  const r = triggerEl.value.getBoundingClientRect()
  const vh = window.innerHeight
  const ph = 280
  const placement = (vh - r.bottom) < ph && r.top > ph ? 'top' : 'bottom'
  popperPos.value = {
    top: placement === 'bottom' ? r.bottom + 4 : r.top - 4,
    left: r.left,
    width: r.width,
    placement
  }
}

watch(searchQuery, (q) => {
  if (!props.asyncLoader) return
  clearTimeout(debounceTimer.value)
  debounceTimer.value = setTimeout(async () => {
    try { localOptions.value = await props.asyncLoader(q) }
    catch (e) { localOptions.value = [] }
  }, 250)
})

onMounted(() => document.addEventListener('mousedown', onClickOutside))
onBeforeUnmount(() => document.removeEventListener('mousedown', onClickOutside))
```

**scoped style 部分**（约 100 行）：

- trigger：复用 UiInput 视觉（`--color-input` border / `--color-card` 背景 / `--radius-md`）
- popper：Teleport 到 body，`position: fixed` + z-index 1001（比 UiModal 1000 高一层）
- 暗色正确：用 `var(--bg-surface)` + `var(--text-primary)`，**彻底解决原生 `<option>` 不可控问题**
- 选项高亮：`var(--color-muted)`
- 选项选中：左边出现 ✓ 标记（多选）/ 文字色 `var(--color-primary)`
- 响应式：`max-width: 95vw`（移动端）、自动 flip
- 动画：与 UiModal 节奏一致（fade + scale）

---

### 步骤 2：手测 3 个现有调用点（**验收通过才进 commit**）

| # | 调用点 | 测试场景 |
|---|---|---|
| 1 | [TaskList.vue:30](../../../frontend/src/views/TaskList.vue#L30) 顶部状态筛选 | 桌面亮色 / 桌面暗色 / 手机亮色 / 手机暗色；鼠标点击 / 键盘 ↑↓Enter / 点击外部关闭 / Esc 关闭 |
| 2 | [TaskList.vue:142](../../../frontend/src/views/TaskList.vue#L142) 创建任务 → 管线模板下拉 | **关键**：暗色模式下拉展开，确认背景/文字颜色都正确（**这是要修的核心 bug**） |
| 3 | [ResourceList.vue:204](../../../frontend/src/views/ResourceList.vue#L204) 资源类型筛选 | 同 #1 |

**Pass 标准**：
- ✅ 暗色模式下拉展开后，**背景 + 文字都是设计的暗色色板**
- ✅ 鼠标点击、键盘 ↑↓Enter、Esc、Tab、点击外部 — 6 种交互全部正常
- ✅ 选中后 modelValue 正确更新（v-model 双向绑定有效）
- ✅ 移动端视口（375x667）下拉不会溢出屏幕

---

### 步骤 3：补 dev-tmp 重构记录

在 [ui-design-principles-and-polish.md](./ui-design-principles-and-polish.md) 加一条 UiSelect v2 改造记录（详见该文件末尾的 v2 章节草稿）。

---

### 步骤 4：commit + push

```bash
git add frontend/src/components/ui/UiSelect.vue
git add dev-tmp/design/ui-design-principles-and-polish.md   # 视情况

git commit -m "fix(ui): UiSelect 自渲染 popper，修复暗色模式下拉面板不跟随主题"
git push
```

> 按 [`git-workflow.md`](../../../.trae/rules/git-workflow.md) 第 4 条：完工前如果主线上有更新，先 `git fetch origin main && git rebase origin/main` 再推送。本次不动 main，所以无需 rebase。

---

## ⏱️ 工作量预估

- 步骤 1（写代码）：30-50 分钟
- 步骤 2（手测）：10-15 分钟
- 步骤 3（补记录）：5 分钟
- 步骤 4（commit + push）：2 分钟

---

## 📌 完成定义（Definition of Done）

- ✅ UiSelect.vue 重写完成，~250 行
- ✅ 现有 3 个调用点（TaskList×2 + ResourceList×1）零改动
- ✅ 暗色模式下拉面板背景 + 文字**完全**跟设计令牌走（**核心修复目标**）
- ✅ 键盘交互 6 项（点击 / ↑↓ / Enter / Esc / Tab / 点外部）全部可用
- ✅ 移动端（375px）下拉不溢出
- ✅ dev-tmp 改造记录已补
- ✅ 已 commit + push 到 GitHub 远端

---

## ⚠️ 不在本计划范围

- PipelineCanvas / TaskDetail / AdminPanel 里的原生 `<select>`（另一个话题）
- Task.status 语义重构（今天只做 UiSelect）
- 任务列表界面本身的优化（这是后面才做的）

---

## 🤔 待办

- [ ] 用户（开发者）确认计划
- [ ] 实施步骤 1-4
- [ ] 完成后更新本文件，标记 ✅