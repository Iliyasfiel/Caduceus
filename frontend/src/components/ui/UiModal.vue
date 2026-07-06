<!--
UiModal：通用弹窗组件
变体：center（居中弹窗）| drawer（右侧抽屉）
v-model 控制显隐；title / footer / size 可选。
ESC 键关闭、点击遮罩关闭、关闭时释放焦点。
-->
<template>
  <Teleport to="body">
    <Transition name="ui-modal">
      <div v-if="modelValue" class="ui-modal" :class="`ui-modal--${variant}`" @keydown.esc.stop="close">
        <div class="ui-modal__overlay" @click="closeOnOverlay && close()" />
        <div
          ref="panelRef"
          class="ui-modal__panel"
          :style="panelStyle"
          role="dialog"
          aria-modal="true"
        >
          <header v-if="title || $slots.header || closeable" class="ui-modal__header">
            <slot name="header">
              <h3 class="ui-modal__title">{{ title }}</h3>
            </slot>
            <button
              v-if="closeable"
              type="button"
              class="ui-modal__close"
              aria-label="关闭"
              @click="close"
            >×</button>
          </header>

          <div class="ui-modal__body">
            <slot />
          </div>

          <footer v-if="$slots.footer" class="ui-modal__footer">
            <slot name="footer" />
          </footer>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
/**
 * UiModal 脚本：v-model 双向绑定；关闭时通知父级。
 */
import { computed, watch, ref, nextTick, onUnmounted } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: '' },
  variant: { type: String, default: 'center' }, // center | drawer
  size: { type: String, default: 'md' },         // sm (360) | md (480) | lg (640)
  closeable: { type: Boolean, default: true },
  closeOnOverlay: { type: Boolean, default: true }
})

const emit = defineEmits(['update:modelValue', 'close'])

const panelRef = ref(null)

const panelStyle = computed(() => {
  if (props.variant === 'drawer') {
    return { width: '420px', maxWidth: '90vw', height: '100vh' }
  }
  const sizes = { sm: '360px', md: '480px', lg: '640px' }
  return { width: sizes[props.size] || sizes.md, maxWidth: '90vw' }
})

function close() {
  emit('update:modelValue', false)
  emit('close')
}

// 打开时锁滚动 + 挂载全局 ESC 监听
watch(() => props.modelValue, async (open) => {
  if (open) {
    document.body.style.overflow = 'hidden'
    await nextTick()
    panelRef.value?.focus()
  } else {
    document.body.style.overflow = ''
  }
})

function onKeydown(e) {
  if (e.key === 'Escape' && props.modelValue && props.closeable) close()
}
if (typeof window !== 'undefined') window.addEventListener('keydown', onKeydown)
onUnmounted(() => {
  if (typeof window !== 'undefined') window.removeEventListener('keydown', onKeydown)
  document.body.style.overflow = ''
})
</script>

<style scoped>
.ui-modal {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
}

.ui-modal--center {
  align-items: center;
  justify-content: center;
}

.ui-modal--drawer {
  justify-content: flex-end;
}

.ui-modal__overlay {
  position: absolute;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
}

.ui-modal__panel {
  position: relative;
  background-color: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  display: flex;
  flex-direction: column;
  max-height: 90vh;
  overflow: hidden;
}

.ui-modal--drawer .ui-modal__panel {
  border-radius: 0;
  height: 100vh;
  max-height: 100vh;
}

.ui-modal__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-6);
  border-bottom: 1px solid var(--border-subtle);
}

.ui-modal__title {
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.ui-modal__close {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  padding: 0;
  border: 0;
  border-radius: var(--radius-md);
  background-color: transparent;
  color: var(--text-secondary);
  font-size: var(--text-xl);
  line-height: 1;
  cursor: pointer;
  transition: background-color var(--transition-fast), color var(--transition-fast);
}

.ui-modal__close:hover {
  background-color: var(--color-muted);
  color: var(--text-primary);
}

.ui-modal__body {
  padding: var(--space-6);
  overflow-y: auto;
  flex: 1;
}

.ui-modal__footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: var(--space-2);
  padding: var(--space-4) var(--space-6);
  border-top: 1px solid var(--border-subtle);
}

/* 过渡动画 */
.ui-modal-enter-active,
.ui-modal-leave-active {
  transition: opacity var(--transition-fast);
}
.ui-modal-enter-from,
.ui-modal-leave-to {
  opacity: 0;
}

.ui-modal-enter-active .ui-modal__panel,
.ui-modal-leave-active .ui-modal__panel {
  transition: transform var(--transition-normal), opacity var(--transition-normal);
}

.ui-modal--center .ui-modal-enter-from .ui-modal__panel,
.ui-modal--center .ui-modal-leave-to .ui-modal__panel {
  transform: scale(0.96);
  opacity: 0;
}

.ui-modal--drawer .ui-modal-enter-from .ui-modal__panel,
.ui-modal--drawer .ui-modal-leave-to .ui-modal__panel {
  transform: translateX(100%);
}
</style>