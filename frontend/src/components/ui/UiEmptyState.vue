<!--
UiEmptyState：空状态占位
图标 + 标题 + 副标题 + 可选 CTA
供所有列表页使用，统一空态视觉。
-->
<template>
  <div class="ui-empty">
    <div v-if="$slots.icon || icon" class="ui-empty__icon">
      <slot name="icon">{{ icon }}</slot>
    </div>
    <h4 v-if="title" class="ui-empty__title">{{ title }}</h4>
    <p v-if="description" class="ui-empty__desc">{{ description }}</p>
    <div v-if="$slots.action" class="ui-empty__action">
      <slot name="action" />
    </div>
  </div>
</template>

<script setup>
/**
 * UiEmptyState 脚本：无业务逻辑。
 */
defineProps({
  icon: { type: String, default: '' },
  title: { type: String, default: '' },
  description: { type: String, default: '' }
})
</script>

<style scoped>
.ui-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-12) var(--space-6);
  text-align: center;
  color: var(--text-muted);
}

.ui-empty__icon {
  font-size: var(--text-3xl);
  opacity: 0.5;
}

.ui-empty__title {
  font-size: var(--text-base);
  color: var(--text-primary);
}

.ui-empty__desc {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.ui-empty__action {
  margin-top: var(--space-4);
}
</style>