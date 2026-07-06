<!--
UiInput：表单输入基础组件
支持 v-model；可选 label / error / hint
业务侧与原生 input 行为一致；error 态自动应用 destructive 色。
-->
<template>
  <div :class="['ui-field', { 'ui-field--error': !!error }]">
    <label v-if="label" :for="inputId" class="ui-field__label">{{ label }}</label>
    <div class="ui-field__control">
      <span v-if="$slots.prefix" class="ui-field__prefix"><slot name="prefix" /></span>
      <input
        :id="inputId"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :required="required"
        :autocomplete="autocomplete"
        class="ui-field__input"
        @input="onInput"
        @blur="$emit('blur', $event)"
      />
    </div>
    <p v-if="error" class="ui-field__error">{{ error }}</p>
    <p v-else-if="hint" class="ui-field__hint">{{ hint }}</p>
  </div>
</template>

<script setup>
/**
 * UiInput 脚本：透传 modelValue / update:modelValue 事件，行为等价原生 input。
 */
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: [String, Number], default: '' },
  label: { type: String, default: '' },
  type: { type: String, default: 'text' },
  placeholder: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
  required: { type: Boolean, default: false },
  autocomplete: { type: String, default: 'off' },
  error: { type: String, default: '' },
  hint: { type: String, default: '' }
})

const emit = defineEmits(['update:modelValue', 'blur'])

const inputId = computed(
  () => `ui-input-${Math.random().toString(36).slice(2, 9)}`
)

function onInput(e) {
  // number 类型自动转换；与 v-model.number 行为一致
  if (props.type === 'number') {
    const raw = e.target.value
    emit('update:modelValue', raw === '' ? '' : Number(raw))
  } else {
    emit('update:modelValue', e.target.value)
  }
}
</script>

<style scoped>
.ui-field {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.ui-field__label {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--text-primary);
}

.ui-field__control {
  display: flex;
  align-items: center;
  border: 1px solid var(--color-input);
  border-radius: var(--radius-md);
  background-color: var(--color-card);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.ui-field__control:focus-within {
  border-color: var(--color-ring);
  box-shadow: 0 0 0 3px rgba(13, 13, 13, 0.08);
}

.ui-field__prefix {
  padding-left: var(--space-3);
  color: var(--text-muted);
}

.ui-field__input {
  flex: 1;
  padding: var(--space-3) var(--space-3);
  border: 0;
  outline: none;
  background: transparent;
  font-size: var(--text-sm);
  color: var(--text-primary);
}

.ui-field__input::placeholder {
  color: var(--text-muted);
}

.ui-field--error .ui-field__control {
  border-color: var(--color-destructive);
}

.ui-field__error {
  font-size: var(--text-xs);
  color: var(--color-destructive);
}

.ui-field__hint {
  font-size: var(--text-xs);
  color: var(--text-muted);
}
</style>