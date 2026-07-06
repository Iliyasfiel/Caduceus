<!--
UiSpinner：基础 loading 指示器
size: sm | md | lg
label: 可选加载文字
tone: primary | muted（默认 muted）
-->
<template>
  <span class="ui-spinner" :class="[`ui-spinner--${size}`, `ui-spinner--${tone}`]" role="status" :aria-label="label || '加载中'">
    <span class="ui-spinner__circle"></span>
    <span v-if="label" class="ui-spinner__label">{{ label }}</span>
  </span>
</template>

<script setup>
defineProps({
  size: { type: String, default: 'md' },     // sm=16 / md=24 / lg=32
  tone: { type: String, default: 'muted' },   // primary | muted
  label: { type: String, default: '' }
})
</script>

<style scoped>
.ui-spinner {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
}

.ui-spinner__circle {
  display: inline-block;
  border-style: solid;
  border-color: var(--border-subtle);
  border-top-color: currentColor;
  border-radius: var(--radius-full);
  animation: ui-spinner-rotate 0.8s linear infinite;
}

.ui-spinner--sm .ui-spinner__circle { width: 14px; height: 14px; border-width: 2px; }
.ui-spinner--md .ui-spinner__circle { width: 20px; height: 20px; border-width: 2px; }
.ui-spinner--lg .ui-spinner__circle { width: 28px; height: 28px; border-width: 3px; }

.ui-spinner--primary { color: var(--text-primary); }
.ui-spinner--muted   { color: var(--text-muted); }

.ui-spinner__label {
  font-size: var(--text-sm);
  color: inherit;
}

@keyframes ui-spinner-rotate {
  to { transform: rotate(360deg); }
}
</style>