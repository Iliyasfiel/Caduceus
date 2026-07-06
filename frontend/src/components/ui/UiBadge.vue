<!--
UiBadge：徽章基础组件
tone 语义：neutral / info / success / warning / danger
业务侧只需选择 tone + 文本即可，避免重复写颜色。
-->
<template>
  <span :class="['ui-badge', `ui-badge--${tone}`, `ui-badge--${size}`]">
    <slot />
  </span>
</template>

<script setup>
/**
 * UiBadge 脚本：无业务逻辑。
 */
defineProps({
  tone: { type: String, default: 'neutral' }, // neutral | info | success | warning | danger
  size: { type: String, default: 'md' }       // sm | md
})
</script>

<style scoped>
.ui-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  border-radius: var(--radius-full);
  font-weight: 500;
  line-height: 1;
  white-space: nowrap;
}

.ui-badge--sm { padding: 2px 8px; font-size: var(--text-xs); }
.ui-badge--md { padding: 4px 10px; font-size: var(--text-xs); }

.ui-badge--neutral {
  background-color: var(--badge-neutral-bg);
  color: var(--badge-neutral-fg);
}

.ui-badge--info {
  background-color: var(--badge-info-bg);
  color: var(--badge-info-fg);
}

.ui-badge--success {
  background-color: var(--badge-success-bg);
  color: var(--badge-success-fg);
}

.ui-badge--warning {
  background-color: var(--badge-warning-bg);
  color: var(--badge-warning-fg);
}

.ui-badge--danger {
  background-color: var(--badge-danger-bg);
  color: var(--badge-danger-fg);
}
</style>