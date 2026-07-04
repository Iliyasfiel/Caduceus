<!--
UiButton：按钮基础组件
变体：primary / secondary / ghost / danger
尺寸：sm / md / lg
状态：default / loading / disabled
所有视觉走 token，不写硬编码值。
-->
<template>
  <button
    :class="[
      'ui-btn',
      `ui-btn--${variant}`,
      `ui-btn--${size}`,
      { 'ui-btn--loading': loading, 'ui-btn--block': block }
    ]"
    :type="type"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <span v-if="loading" class="ui-btn__spinner" aria-hidden="true" />
    <span class="ui-btn__label"><slot /></span>
  </button>
</template>

<script setup>
/**
 * UiButton 脚本：透传 props，原生 button 行为保持不变。
 * 业务侧只需关心 variant / size / loading / block，事件按原生 button 一致触发。
 */
import { computed } from 'vue'

const props = defineProps({
  variant: { type: String, default: 'primary' }, // primary | secondary | ghost | danger
  size: { type: String, default: 'md' },          // sm | md | lg
  type: { type: String, default: 'button' },      // button | submit | reset
  loading: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  block: { type: Boolean, default: false }
})

const emit = defineEmits(['click'])

const _ = computed(() => props.variant) // 占位：保留响应式引用，便于未来扩展

function handleClick(e) {
  // loading / disabled 状态不再冒泡，避免父级误判提交成功
  if (props.disabled || props.loading) {
    e.preventDefault()
    return
  }
  emit('click', e)
}
</script>

<style scoped>
.ui-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  font-weight: 500;
  cursor: pointer;
  transition: background-color var(--transition-fast),
              border-color var(--transition-fast),
              color var(--transition-fast),
              box-shadow var(--transition-fast);
  user-select: none;
}

.ui-btn:focus-visible {
  outline: 2px solid var(--color-ring);
  outline-offset: 2px;
}

.ui-btn--block { width: 100%; }

/* 尺寸 */
.ui-btn--sm { padding: var(--space-1) var(--space-3); font-size: var(--text-xs); height: 28px; }
.ui-btn--md { padding: var(--space-2) var(--space-4); font-size: var(--text-sm); height: 36px; }
.ui-btn--lg { padding: var(--space-3) var(--space-5); font-size: var(--text-base); height: 44px; }

/* 变体 */
.ui-btn--primary {
  background-color: var(--color-primary);
  color: var(--color-primary-foreground);
  border-color: var(--color-primary);
}
.ui-btn--primary:hover:not(:disabled) { opacity: 0.9; }

.ui-btn--secondary {
  background-color: var(--color-secondary);
  color: var(--color-secondary-foreground);
  border-color: var(--color-border);
}
.ui-btn--secondary:hover:not(:disabled) { background-color: var(--color-accent); }

.ui-btn--ghost {
  background-color: transparent;
  color: var(--color-foreground);
  border-color: transparent;
}
.ui-btn--ghost:hover:not(:disabled) { background-color: var(--color-muted); }

.ui-btn--danger {
  background-color: var(--color-destructive);
  color: var(--color-destructive-foreground);
  border-color: var(--color-destructive);
}
.ui-btn--danger:hover:not(:disabled) { opacity: 0.9; }

.ui-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.ui-btn--loading .ui-btn__label { opacity: 0.7; }

.ui-btn__spinner {
  width: 12px;
  height: 12px;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: var(--radius-full);
  animation: ui-btn-spin 0.6s linear infinite;
}

@keyframes ui-btn-spin {
  to { transform: rotate(360deg); }
}
</style>