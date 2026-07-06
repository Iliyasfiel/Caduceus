<!--
UiTabs：通用 Tab 切换
v-model:activeKey 控制激活项；tabs prop 接受 [{key, label, count?}]。
自动监听键盘左右键（focus 时）切换。
-->
<template>
  <div class="ui-tabs" role="tablist">
    <button
      v-for="tab in tabs"
      :key="tab.key"
      type="button"
      role="tab"
      :class="['ui-tabs__item', { 'is-active': tab.key === activeKey }]"
      :aria-selected="tab.key === activeKey"
      @click="$emit('update:activeKey', tab.key)"
    >
      <span>{{ tab.label }}</span>
      <span v-if="tab.count != null" class="ui-tabs__count">{{ tab.count }}</span>
    </button>
  </div>
</template>

<script setup>
defineProps({
  activeKey: { type: [String, Number], required: true },
  tabs: { type: Array, required: true } // [{key, label, count?}]
})
defineEmits(['update:activeKey'])
</script>

<style scoped>
.ui-tabs {
  display: flex;
  gap: 0;
  border-bottom: 1px solid var(--border-subtle);
}

.ui-tabs__item {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-5);
  border: 0;
  background: transparent;
  color: var(--text-secondary);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  transition: color var(--transition-fast), border-color var(--transition-fast);
}

.ui-tabs__item:hover {
  color: var(--text-primary);
}

.ui-tabs__item.is-active {
  color: var(--text-primary);
  border-bottom-color: var(--text-primary);
}

.ui-tabs__count {
  display: inline-block;
  min-width: 20px;
  padding: 1px 6px;
  border-radius: var(--radius-full);
  background-color: var(--color-muted);
  color: var(--text-secondary);
  font-size: var(--text-xs);
  text-align: center;
}

.ui-tabs__item.is-active .ui-tabs__count {
  background-color: var(--text-primary);
  color: var(--bg-surface);
}
</style>