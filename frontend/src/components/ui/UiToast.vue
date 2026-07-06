<!--
UiToast：全局轻量通知
通过 useToast() composable 调用 toast.success/error/info，3 秒自动消失。
本组件自身订阅 store 渲染，页面不需要直接使用。
-->
<template>
  <Teleport to="body">
    <div class="ui-toast-container" aria-live="polite" aria-atomic="true">
      <TransitionGroup name="ui-toast">
        <div
          v-for="t in toasts"
          :key="t.id"
          :class="['ui-toast', `ui-toast--${t.tone}`]"
        >
          <UiIcon :name="iconFor(t.tone)" :size="14" class="ui-toast__icon" />
          <span class="ui-toast__msg">{{ t.message }}</span>
          <button
            v-if="t.dismissible !== false"
            type="button"
            class="ui-toast__close"
            aria-label="关闭"
            @click="remove(t.id)"
          >
            <UiIcon name="x" :size="14" />
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
/**
 * UiToast 脚本：仅消费 useToastStore。
 */
import { computed } from 'vue'
import { useToastStore } from '@/stores/toast'
import UiIcon from './UiIcon.vue'

const store = useToastStore()
const toasts = computed(() => store.list)

function iconFor(tone) {
  return { success: 'check', error: 'x', info: 'info', warning: 'warning' }[tone] || 'info'
}

function remove(id) {
  store.remove(id)
}
</script>

<style scoped>
.ui-toast-container {
  position: fixed;
  top: var(--space-6);
  right: var(--space-6);
  z-index: 2000;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  pointer-events: none;
}

.ui-toast {
  pointer-events: auto;
  display: flex;
  align-items: center;
  gap: var(--space-3);
  min-width: 260px;
  max-width: 360px;
  padding: var(--space-3) var(--space-4);
  background-color: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-left-width: 3px;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  font-size: var(--text-sm);
  color: var(--text-primary);
}

.ui-toast--success { border-left-color: var(--color-success); }
.ui-toast--error   { border-left-color: var(--color-destructive); }
.ui-toast--info    { border-left-color: var(--color-chart-3); }
.ui-toast--warning { border-left-color: #f59e0b; }

.ui-toast__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: var(--radius-full);
  flex-shrink: 0;
}

/* tone 决定图标底色与前景色，遵循 token 语义 */
.ui-toast--success .ui-toast__icon { background-color: var(--color-success); color: var(--color-success-foreground); }
.ui-toast--error   .ui-toast__icon { background-color: var(--color-destructive); color: var(--color-destructive-foreground); }
.ui-toast--info    .ui-toast__icon { background-color: var(--color-chart-3); color: var(--color-primary-foreground); }
.ui-toast--warning .ui-toast__icon { background-color: #f59e0b; color: var(--color-primary-foreground); }

.ui-toast__msg {
  flex: 1;
  line-height: var(--leading-normal);
}

.ui-toast__close {
  background: none;
  border: 0;
  color: var(--text-muted);
  line-height: 0;
  cursor: pointer;
  padding: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.ui-toast__close:hover {
  color: var(--text-primary);
}

.ui-toast-enter-active,
.ui-toast-leave-active {
  transition: transform var(--transition-normal), opacity var(--transition-normal);
}
.ui-toast-enter-from,
.ui-toast-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
</style>