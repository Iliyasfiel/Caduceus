<!--
UiSelect：原生 select 包装
v-model 行为与原生一致；可选 label。
为复用 status 枚举选项，提供 options 数组 prop 简化调用。
-->
<template>
  <div :class="['ui-select', { 'ui-select--error': !!error }]">
    <label v-if="label" :for="selectId" class="ui-select__label">{{ label }}</label>
    <div class="ui-select__control">
      <select
        :id="selectId"
        :value="modelValue"
        :disabled="disabled"
        :required="required"
        class="ui-select__field"
        @change="onChange"
      >
        <option v-if="placeholder" value="">{{ placeholder }}</option>
        <option
          v-for="opt in normalizedOptions"
          :key="String(opt.value)"
          :value="opt.value"
          :disabled="opt.disabled"
        >
          {{ opt.label }}
        </option>
      </select>
      <span class="ui-select__chevron" aria-hidden="true">▾</span>
    </div>
    <p v-if="error" class="ui-select__error">{{ error }}</p>
  </div>
</template>

<script setup>
/**
 * UiSelect 脚本：透传 v-model；options 支持 [{label, value}] 或 [['label', value]] 两种格式。
 */
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: [String, Number, null], default: '' },
  label: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
  required: { type: Boolean, default: false },
  error: { type: String, default: '' },
  options: {
    type: Array,
    default: () => [],
    // 接受 ['label', value] 形式 或 {label, value} 形式
    validator: (val) => Array.isArray(val)
  }
})

const emit = defineEmits(['update:modelValue'])

const selectId = computed(
  () => `ui-select-${Math.random().toString(36).slice(2, 9)}`
)

const normalizedOptions = computed(() =>
  props.options.map((opt) => {
    if (Array.isArray(opt)) return { label: String(opt[0]), value: opt[1], disabled: false }
    return { label: opt.label, value: opt.value, disabled: !!opt.disabled }
  })
)

function onChange(e) {
  emit('update:modelValue', e.target.value)
}
</script>

<style scoped>
.ui-select {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.ui-select__label {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--text-primary);
}

.ui-select__control {
  position: relative;
  display: flex;
  align-items: center;
  border: 1px solid var(--color-input);
  border-radius: var(--radius-md);
  background-color: var(--color-card);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.ui-select__control:focus-within {
  border-color: var(--color-ring);
  box-shadow: 0 0 0 3px rgba(13, 13, 13, 0.08);
}

.ui-select__field {
  flex: 1;
  appearance: none;
  -webkit-appearance: none;
  padding: var(--space-3) var(--space-8) var(--space-3) var(--space-3);
  border: 0;
  outline: none;
  background: transparent;
  font-size: var(--text-sm);
  color: var(--text-primary);
  cursor: pointer;
}

.ui-select__chevron {
  position: absolute;
  right: var(--space-3);
  pointer-events: none;
  color: var(--text-muted);
  font-size: var(--text-xs);
}

.ui-select--error .ui-select__control {
  border-color: var(--color-destructive);
}

.ui-select__error {
  font-size: var(--text-xs);
  color: var(--color-destructive);
}
</style>