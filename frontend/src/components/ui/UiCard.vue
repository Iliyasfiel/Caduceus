<!--
UiCard：基础卡片容器
可选 header / footer 插槽；hoverable 用于列表项交互反馈。
-->
<template>
  <div :class="['ui-card', { 'ui-card--hoverable': hoverable }]">
    <header v-if="$slots.header || title" class="ui-card__header">
      <slot name="header">
        <h3 class="ui-card__title">{{ title }}</h3>
      </slot>
      <div v-if="$slots.actions" class="ui-card__actions">
        <slot name="actions" />
      </div>
    </header>
    <div class="ui-card__body">
      <slot />
    </div>
    <footer v-if="$slots.footer" class="ui-card__footer">
      <slot name="footer" />
    </footer>
  </div>
</template>

<script setup>
/**
 * UiCard 脚本：无业务逻辑，仅做布局容器。
 */
defineProps({
  title: { type: String, default: '' },
  hoverable: { type: Boolean, default: false }
})
</script>

<style scoped>
.ui-card {
  background-color: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  transition: box-shadow var(--transition-normal), border-color var(--transition-normal);
}

.ui-card--hoverable { cursor: pointer; }
.ui-card--hoverable:hover { box-shadow: var(--shadow-md); }

.ui-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-6);
  border-bottom: 1px solid var(--border-subtle);
}

.ui-card__title {
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--text-primary);
}

.ui-card__actions {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.ui-card__body {
  padding: var(--space-6);
}

.ui-card__footer {
  padding: var(--space-4) var(--space-6);
  border-top: 1px solid var(--border-subtle);
  color: var(--text-secondary);
}
</style>