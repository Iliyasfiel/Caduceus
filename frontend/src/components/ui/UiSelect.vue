<!--
  UiSelect v2：自渲染 popper 下拉面板

  v2 改造原因（2026-07-06）：
  原实现使用原生 <select> + appearance: none 隐藏默认箭头，
  但展开后的 <option> 列表由浏览器接管渲染，**暗色模式下拉背景/文字无法跟随设计令牌**，
  触发于 TaskList 创建任务弹窗的管线模板下拉暗色模式显示问题。
  改造方案：完全自渲染 listbox popper（Teleport 到 body），用 var(--bg-surface) / var(--text-primary) 等设计令牌渲染。
  键盘导航：↑↓/Enter/Esc/Tab + 点击外部关闭 + 移动端自适应。

  向后兼容：保持原有 props 100% 不变（modelValue / options / label / placeholder /
  disabled / required / error / hint）。现有 3 个调用点零改动即可享受暗色修复 + 键盘导航。

  新增可选能力（不传 = 老行为）：
  - searchable：下拉顶部启用搜索框过滤
  - multiple：多选模式（v-model 用 Array）
  - asyncLoader(q) -> Promise<options[]>：异步加载，启用后 options prop 失效
  - maxDisplayChips：多选 trigger 显示上限（默认 3）
-->
<template>
  <div :class="['ui-field', 'ui-select', cssClass]">
    <label v-if="label" :for="triggerId" class="ui-field__label">{{ label }}</label>

    <div ref="triggerEl" class="ui-field__control ui-select__control"
         @click.stop="toggleOpen">
      <button
        :id="triggerId"
        type="button"
        class="ui-select__trigger"
        :aria-haspopup="'listbox'"
        :aria-expanded="open"
        :aria-controls="listboxId"
        :aria-disabled="disabled || undefined"
        :aria-invalid="!!error || undefined"
        :disabled="disabled"
        @keydown="onTriggerKeydown"
      >
        <span class="ui-select__value" :class="{ 'is-placeholder': isPlaceholder }">
          {{ displayText }}
        </span>
        <svg class="ui-select__chevron" :class="{ 'is-open': open }" viewBox="0 0 16 16"
             width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.5"
             stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M4 6l4 4 4-4" />
        </svg>
      </button>
    </div>

    <Teleport to="body">
      <Transition name="ui-select-pop">
        <ul
          v-if="open && !disabled"
          ref="listboxEl"
          :id="listboxId"
          class="ui-select__popper"
          :class="popperCssClass"
          :style="popperStyle"
          role="listbox"
          :aria-multiselectable="multiple || undefined"
          tabindex="-1"
          @keydown="onListboxKeydown"
        >
          <li v-if="searchable" class="ui-select__search" @click.stop>
            <input
              ref="searchInputEl"
              v-model="searchQuery"
              type="text"
              class="ui-select__search-input"
              :placeholder="searchPlaceholder || '搜索...'"
              @keydown.stop
            />
          </li>
          <li
            v-if="multiple && Array.isArray(modelValue) && modelValue.length > 0"
            class="ui-select__chips"
            @click.stop
          >
            <span v-for="chip in displayChips" :key="String(chip.value)" class="ui-select__chip">
              {{ chip.label }}
              <button
                type="button"
                class="ui-select__chip-remove"
                :aria-label="`移除 ${chip.label}`"
                @click.stop="removeValue(chip.value)"
              >×</button>
            </span>
            <span v-if="extraChipCount > 0" class="ui-select__chip is-extra">+{{ extraChipCount }}</span>
          </li>
          <li v-if="filteredOptions.length === 0" class="ui-select__empty">
            {{ emptyText || '无匹配项' }}
          </li>
          <li
            v-for="(opt, idx) in filteredOptions"
            :key="String(opt.value)"
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
            @mousedown.prevent="selectOption(opt)"
          >
            <span
              v-if="multiple"
              class="ui-select__checkbox"
              :class="{ 'is-checked': isSelected(opt.value) }"
              aria-hidden="true"
            >
              {{ isSelected(opt.value) ? '✓' : '' }}
            </span>
            <span class="ui-select__option-label">{{ opt.label }}</span>
          </li>
        </ul>
      </Transition>
    </Teleport>

    <!-- 表单兜底：隐藏的原生 select，用于无障碍 / 表单序列化；永远不会有真实交互 -->
    <select
      v-show="false"
      :value="serializedValue"
      :multiple="multiple || undefined"
      tabindex="-1"
      aria-hidden="true"
      @change="onNativeChange"
    >
      <option v-for="opt in options" :key="String(opt.value)" :value="opt.value">{{ opt.label }}</option>
    </select>

    <p v-if="error" class="ui-field__error">{{ error }}</p>
    <p v-else-if="hint" class="ui-field__hint">{{ hint }}</p>
  </div>
</template>

<script setup>
/**
 * UiSelect v2 脚本：自渲染 popper、键盘导航、v-model 双向绑定。
 * 单选 / 多选 / 搜索 / 异步加载四种能力通过 props 可选启用。
 */
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick, useId } from 'vue'

const props = defineProps({
  // 向后兼容：原 8 个 prop
  modelValue: { type: [String, Number, Array, null], default: '' },
  options: { type: Array, default: () => [] },
  label: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
  required: { type: Boolean, default: false },
  error: { type: String, default: '' },
  hint: { type: String, default: '' },

  // v2 新增（默认关闭，老代码零行为变化）
  searchable: { type: Boolean, default: false },
  multiple: { type: Boolean, default: false },
  asyncLoader: { type: Function, default: null },
  searchPlaceholder: { type: String, default: '' },
  emptyText: { type: String, default: '' },
  maxDisplayChips: { type: Number, default: 3 },

  // v2 新增：尺寸（Vercel 风格只有两种：默认 / sm）
  size: { type: String, default: 'md' }   // 'sm' | 'md'
})

const emit = defineEmits(['update:modelValue', 'change', 'blur'])

// 状态
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
const triggerId = computed(() => `ui-select-trigger-${id}`)
const listboxId = computed(() => `ui-select-listbox-${id}`)

// 派生
const isMultiple = computed(() => props.multiple || Array.isArray(props.modelValue))
const sourceOptions = computed(() => (props.asyncLoader ? localOptions.value : props.options) || [])

/**
 * 标准化 options：支持两种入参格式
 * 1. [{label, value, disabled?}]
 * 2. [['label', value], ...]  // tuple 格式（兼容老代码）
 * 统一输出 [{label, value, disabled}]，模板与逻辑层不必关心入参格式
 */
const normalizedOptions = computed(() =>
  sourceOptions.value.map((o) => {
    if (Array.isArray(o)) return { label: o[0], value: o[1], disabled: false }
    return {
      label: o.label ?? String(o.value ?? ''),
      value: o.value,
      disabled: !!o.disabled
    }
  })
)
const filteredOptions = computed(() => {
  const opts = normalizedOptions.value
  if (!props.searchable || !searchQuery.value) return opts
  const q = searchQuery.value.toLowerCase()
  return opts.filter((o) => String(o.label).toLowerCase().includes(q))
})
const isPlaceholder = computed(() =>
  isMultiple.value ? !(props.modelValue && props.modelValue.length) : !props.modelValue
)
const displayText = computed(() => {
  if (isMultiple.value) {
    return props.modelValue && props.modelValue.length
      ? `已选 ${props.modelValue.length} 项`
      : props.placeholder || ''
  }
  const found = normalizedOptions.value.find((o) => o.value === props.modelValue)
  return found ? found.label : props.placeholder || ''
})
const displayChips = computed(() => {
  const sel = props.modelValue || []
  const max = props.maxDisplayChips
  return sel.slice(0, max).map((v) => {
    const opt = normalizedOptions.value.find((o) => o.value === v)
    return { value: v, label: opt ? opt.label : String(v) }
  })
})
const extraChipCount = computed(() =>
  Math.max(0, (props.modelValue?.length || 0) - props.maxDisplayChips)
)
const serializedValue = computed(() => (isMultiple.value ? '' : props.modelValue ?? ''))
const cssClass = computed(() => ({
  'ui-select--open': open.value,
  'ui-select--disabled': props.disabled,
  'ui-select--multiple': isMultiple.value,
  'ui-select--sm': props.size === 'sm',
  'ui-field--error': !!props.error
}))
const popperCssClass = computed(() => `ui-select__popper--${popperPos.value.placement}`)
const popperStyle = computed(() => ({
  position: 'fixed',
  top: `${popperPos.value.top}px`,
  left: `${popperPos.value.left}px`,
  width: `${popperPos.value.width}px`,
  zIndex: 1001
}))

// 选中判断
function isSelected(v) {
  return isMultiple.value
    ? !!(props.modelValue && props.modelValue.includes(v))
    : props.modelValue === v
}

// 开关
function toggleOpen() {
  if (props.disabled) return
  if (open.value) closePopper()
  else openPopper()
}
async function openPopper() {
  if (open.value) return
  open.value = true
  await nextTick()
  computePopperPosition()
  if (props.searchable) searchInputEl.value?.focus()
  // 默认高亮当前已选项
  const idx = filteredOptions.value.findIndex((o) => isSelected(o.value))
  highlightIndex.value = idx >= 0 ? idx : 0
}
function closePopper() {
  open.value = false
  searchQuery.value = ''
  highlightIndex.value = 0
}

// 选择
function selectOption(opt) {
  if (opt.disabled) return
  if (isMultiple.value) {
    const cur = props.modelValue || []
    const next = cur.includes(opt.value)
      ? cur.filter((v) => v !== opt.value)
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
  emit('update:modelValue', (props.modelValue || []).filter((x) => x !== v))
}

// 键盘
function onTriggerKeydown(e) {
  if (props.disabled) return
  if (['ArrowDown', 'ArrowUp', 'Enter', ' '].includes(e.key)) {
    e.preventDefault()
    openPopper()
  }
}
function onListboxKeydown(e) {
  if (e.key === 'Escape') {
    e.preventDefault()
    closePopper()
    triggerEl.value?.querySelector('button')?.focus()
  } else if (e.key === 'Tab') {
    closePopper()
  } else if (e.key === 'ArrowDown') {
    e.preventDefault()
    moveHighlight(1)
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    moveHighlight(-1)
  } else if (e.key === 'Enter') {
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
    if (!opts[i].disabled) {
      highlightIndex.value = i
      // 滚动到可视区
      nextTick(() => {
        const el = listboxEl.value?.querySelectorAll('.ui-select__option')[i]
        el?.scrollIntoView({ block: 'nearest' })
      })
      return
    }
  }
}

// 定位
function computePopperPosition() {
  if (!triggerEl.value) return
  const r = triggerEl.value.getBoundingClientRect()
  const vh = window.innerHeight
  const ph = 280
  const placement = vh - r.bottom < ph && r.top > ph ? 'top' : 'bottom'
  popperPos.value = {
    top: placement === 'bottom' ? r.bottom + 4 : r.top - 4,
    left: r.left,
    width: r.width,
    placement
  }
}

// 点击外部关闭
function onClickOutside(e) {
  if (!open.value) return
  if (triggerEl.value?.contains(e.target)) return
  if (listboxEl.value?.contains(e.target)) return
  closePopper()
}

// 异步加载
watch(searchQuery, (q) => {
  if (!props.asyncLoader) return
  clearTimeout(debounceTimer.value)
  debounceTimer.value = setTimeout(async () => {
    try {
      localOptions.value = (await props.asyncLoader(q)) || []
    } catch (e) {
      localOptions.value = []
    }
  }, 250)
})

// 表单兜底：原生 select 变化（防御性，正常不会触发）
function onNativeChange(e) {
  emit('update:modelValue', e.target.value)
}

onMounted(() => document.addEventListener('mousedown', onClickOutside))
onBeforeUnmount(() => {
  document.removeEventListener('mousedown', onClickOutside)
  clearTimeout(debounceTimer.value)
})
</script>

<style scoped>
/*
 * UiSelect v2 样式：Vercel 风格
 *
 * 设计要点：
 * 1. 触发器：扁平 + 极轻量边框 + focus ring 极细 + 行高紧凑
 * 2. popper：纯色面板 + 微圆角 + 极轻阴影 / 暗色加深边框
 * 3. 选项：紧凑 padding + 高亮是中性灰（不是 primary 蓝）
 * 4. 选中态：仅用 ✓ icon（多选）或 ✓ 强调字重（单选），无彩色背景
 * 5. 排版：text-sm、行高 1.2、字重中性
 * 6. 暗色模式：背景用 bg-elevated（更暗）+ 边框更亮
 */
.ui-select {
  position: relative;
}

/* sm 尺寸：紧凑模式，给 toolbar / 表格内嵌场景 */
.ui-select--sm .ui-select__control {
  min-height: 26px;
}
.ui-select--sm .ui-select__trigger {
  padding: 3px 8px;
  font-size: 12px;
}

/* 触发器容器：继承 UiInput 视觉 */
.ui-select__control {
  cursor: pointer;
  padding: 0;
  min-height: 32px;
}

/* trigger 按钮 */
.ui-select__trigger {
  flex: 1;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
  padding: 6px 10px;
  border: 0;
  outline: none;
  background: transparent;
  font-size: 13px;
  font-weight: 400;
  line-height: 1.2;
  color: var(--text-primary);
  cursor: pointer;
  text-align: left;
  transition: color var(--transition-fast);
}

.ui-select__trigger:hover:not(:disabled) {
  color: var(--text-primary);
}

.ui-select__trigger:disabled {
  cursor: not-allowed;
  color: var(--text-muted);
}

.ui-select__value {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 0;
}

.ui-select__value.is-placeholder {
  color: var(--text-muted);
}

.ui-select__chevron {
  color: var(--text-muted);
  transition: transform 150ms cubic-bezier(0.4, 0, 0.2, 1);
  flex-shrink: 0;
  opacity: 0.7;
}

.ui-select__chevron.is-open {
  transform: rotate(180deg);
  opacity: 1;
}

/* popper 浮层 */
.ui-select__popper {
  margin: 0;
  padding: 4px;
  list-style: none;
  background-color: var(--bg-elevated, var(--bg-surface));
  border: 1px solid var(--border-default, var(--border-subtle));
  border-radius: 8px;
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.04),
    0 4px 12px rgba(0, 0, 0, 0.06);
  max-height: 320px;
  overflow-y: auto;
  overflow-x: hidden;
  color: var(--text-primary);
  font-size: 13px;
  font-weight: 400;
  line-height: 1.2;
}

/* 暗色模式：阴影更深、边框更亮 */
:root[data-theme='dark'] .ui-select__popper {
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.3),
    0 8px 24px rgba(0, 0, 0, 0.4);
}

.ui-select__popper--top {
  transform: translateY(-100%);
}

/* 搜索框：极轻量 */
.ui-select__search {
  padding: 4px;
  position: sticky;
  top: 0;
  background-color: var(--bg-elevated, var(--bg-surface));
  border-bottom: 1px solid var(--border-subtle);
  z-index: 1;
}

.ui-select__search-input {
  width: 100%;
  padding: 6px 10px;
  border: 1px solid transparent;
  border-radius: 6px;
  background-color: var(--bg-surface);
  color: var(--text-primary);
  font-size: 13px;
  outline: none;
  transition: border-color 100ms, background-color 100ms;
}

.ui-select__search-input:focus {
  border-color: var(--border-default);
  background-color: var(--bg-elevated, var(--bg-surface));
}

.ui-select__search-input::placeholder {
  color: var(--text-muted);
}

/* 多选筹码：极简 chip 风格 */
.ui-select__chips {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  padding: 6px 8px;
  border-bottom: 1px solid var(--border-subtle);
}

.ui-select__chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 4px 2px 8px;
  background-color: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: 4px;
  font-size: 12px;
  font-weight: 400;
  color: var(--text-primary);
  line-height: 1.2;
}

.ui-select__chip.is-extra {
  font-weight: 500;
  color: var(--text-muted);
  border-color: transparent;
  background-color: transparent;
}

.ui-select__chip-remove {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 14px;
  height: 14px;
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 14px;
  line-height: 1;
  border-radius: 3px;
  transition: background-color 100ms, color 100ms;
}

.ui-select__chip-remove:hover {
  background-color: var(--color-destructive);
  color: #fff;
}

/* 选项：紧凑 */
.ui-select__option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 8px;
  border-radius: 4px;
  cursor: pointer;
  user-select: none;
  font-size: 13px;
  font-weight: 400;
  line-height: 1.2;
  color: var(--text-primary);
  transition: background-color 80ms;
}

.ui-select__option.is-highlighted {
  background-color: var(--bg-hover, rgba(127, 127, 127, 0.08));
}

.ui-select__option.is-selected {
  font-weight: 500;
}

.ui-select__option.is-disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.ui-select__checkbox {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 14px;
  height: 14px;
  border: 1px solid var(--border-default, var(--text-muted));
  border-radius: 3px;
  font-size: 10px;
  color: transparent;
  flex-shrink: 0;
  background-color: transparent;
  transition: background-color 80ms, border-color 80ms, color 80ms;
}

.ui-select__checkbox.is-checked {
  background-color: var(--text-primary);
  border-color: var(--text-primary);
  color: var(--bg-elevated, var(--bg-surface));
}

.ui-select__option-label {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ui-select__empty {
  padding: 12px 8px;
  text-align: center;
  color: var(--text-muted);
  font-size: 12px;
}

/* 滚动条：细 */
.ui-select__popper::-webkit-scrollbar {
  width: 8px;
}
.ui-select__popper::-webkit-scrollbar-thumb {
  background-color: var(--border-subtle);
  border-radius: 4px;
  border: 2px solid var(--bg-elevated, var(--bg-surface));
}
.ui-select__popper::-webkit-scrollbar-thumb:hover {
  background-color: var(--text-muted);
}

/* 移动端 */
@media (max-width: 640px) {
  .ui-select__popper {
    max-width: 95vw;
  }
}

/* 过渡：极简 fade + 微 scale */
.ui-select-pop-enter-active,
.ui-select-pop-leave-active {
  transition: opacity 120ms cubic-bezier(0.16, 1, 0.3, 1),
              transform 120ms cubic-bezier(0.16, 1, 0.3, 1);
}
.ui-select-pop-enter-from,
.ui-select-pop-leave-to {
  opacity: 0;
  transform: translateY(-4px) scale(0.98);
}
.ui-select__popper--top.ui-select-pop-enter-from,
.ui-select__popper--top.ui-select-pop-leave-to {
  transform: translateY(4px) scale(0.98);
}
</style>