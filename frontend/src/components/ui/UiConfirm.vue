<!--
UiConfirm：全局确认弹窗
通过 useConfirm() composable 调用 showConfirm({ title, message, tone }) → Promise<boolean>
本组件订阅 useConfirmStore 渲染，页面不需要直接使用。
-->
<template>
  <Teleport to="body">
    <Transition name="ui-confirm">
      <div v-if="state.visible" class="ui-confirm">
        <div class="ui-confirm__overlay" @click="onCancel" />
        <div class="ui-confirm__panel" role="alertdialog" aria-modal="true">
          <div class="ui-confirm__header">
            <span class="ui-confirm__icon" :class="`ui-confirm__icon--${state.tone}`">
              {{ iconFor(state.tone) }}
            </span>
            <h3 class="ui-confirm__title">{{ state.title }}</h3>
          </div>
          <div class="ui-confirm__body">
            <p class="ui-confirm__message">{{ state.message }}</p>
          </div>
          <div class="ui-confirm__footer">
            <UiButton variant="secondary" size="sm" @click="onCancel">
              {{ state.cancelText }}
            </UiButton>
            <UiButton
              :variant="state.tone === 'danger' ? 'danger' : 'primary'"
              size="sm"
              :loading="state.loading"
              @click="onConfirm"
            >
              {{ state.confirmText }}
            </UiButton>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
/**
 * UiConfirm 脚本：消费 useConfirmStore。
 */
import { computed } from 'vue'
import { useConfirmStore } from '@/stores/confirm'
import { UiButton } from '@/components/ui'

const store = useConfirmStore()
const state = computed(() => store.state)

function iconFor(tone) {
  return { danger: '!', warning: '?', info: 'i' }[tone] || '?'
}

function onCancel() {
  store.resolve(false)
}

function onConfirm() {
  store.resolve(true)
}
</script>

<style scoped>
.ui-confirm {
  position: fixed;
  inset: 0;
  z-index: 1500;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ui-confirm__overlay {
  position: absolute;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
}

.ui-confirm__panel {
  position: relative;
  background-color: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
  width: 420px;
  max-width: 90vw;
  display: flex;
  flex-direction: column;
}

.ui-confirm__header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-5) var(--space-5) var(--space-3);
}

.ui-confirm__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-full);
  font-size: var(--text-base);
  font-weight: 700;
  flex-shrink: 0;
}

.ui-confirm__icon--danger {
  background-color: var(--badge-danger-bg);
  color: var(--badge-danger-fg);
}

.ui-confirm__icon--warning {
  background-color: var(--badge-warning-bg);
  color: var(--badge-warning-fg);
}

.ui-confirm__icon--info {
  background-color: var(--badge-info-bg);
  color: var(--badge-info-fg);
}

.ui-confirm__title {
  margin: 0;
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--text-primary);
  line-height: var(--leading-tight);
}

.ui-confirm__body {
  padding: 0 var(--space-5) var(--space-5);
}

.ui-confirm__message {
  margin: 0;
  font-size: var(--text-sm);
  color: var(--text-secondary);
  line-height: var(--leading-normal);
  white-space: pre-line;
}

.ui-confirm__footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-5) var(--space-5);
}

.ui-confirm-enter-active,
.ui-confirm-leave-active {
  transition: opacity var(--transition-fast);
}
.ui-confirm-enter-from,
.ui-confirm-leave-to {
  opacity: 0;
}

.ui-confirm-enter-active .ui-confirm__panel,
.ui-confirm-leave-active .ui-confirm__panel {
  transition: transform var(--transition-normal);
}

.ui-confirm-enter-from .ui-confirm__panel,
.ui-confirm-leave-to .ui-confirm__panel {
  transform: scale(0.96);
}
</style>