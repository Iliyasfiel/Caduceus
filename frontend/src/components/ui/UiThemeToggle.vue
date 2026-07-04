<!--
UiThemeToggle：顶栏主题切换按钮
点击循环切换：light → dark → system → light
图标根据当前 resolved 状态显示（太阳 / 月亮 / 自动）。
-->
<template>
  <button
    type="button"
    class="ui-theme-toggle"
    :title="title"
    :aria-label="title"
    @click="onClick"
  >
    <span class="ui-theme-toggle__icon" aria-hidden="true">{{ icon }}</span>
  </button>
</template>

<script setup>
/**
 * UiThemeToggle 脚本：无业务逻辑，仅消费 useThemeStore。
 */
import { computed } from 'vue'
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()

const icon = computed(() => {
  if (themeStore.mode === 'system') return '◐'
  return themeStore.resolved === 'dark' ? '☾' : '☀'
})

const title = computed(() => {
  const map = { light: '当前：亮色，点击切到暗色', dark: '当前：暗色，点击切到跟随系统', system: '当前：跟随系统，点击切到亮色' }
  return map[themeStore.mode]
})

function onClick() {
  themeStore.cycle()
}
</script>

<style scoped>
.ui-theme-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  padding: 0;
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  background-color: transparent;
  color: var(--text-secondary);
  font-size: var(--text-base);
  line-height: 1;
  cursor: pointer;
  transition: background-color var(--transition-fast), color var(--transition-fast), border-color var(--transition-fast);
}

.ui-theme-toggle:hover {
  background-color: var(--color-muted);
  color: var(--text-primary);
}

.ui-theme-toggle:focus-visible {
  outline: 2px solid var(--color-ring);
  outline-offset: 2px;
}

.ui-theme-toggle__icon {
  font-size: var(--text-base);
}
</style>