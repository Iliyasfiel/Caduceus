<!--
Caduceus 资源选择器组件（模态版）
用于任务详情页中关联资源：弹窗中按资源类型筛选、多选资源条目
已关联的资源条目复选框默认选中
-->
<template>
  <div v-if="visible" class="modal-overlay" @click.self="handleCancel">
    <div class="modal-card">
      <h3 class="modal-title">关联资源</h3>

      <!-- 资源类型筛选 -->
      <div class="filter-area">
        <label class="filter-label">资源类型：</label>
        <UiSelect
          v-model="selectedTypeId"
          :options="resourceTypeOptions"
          placeholder="请选择资源类型"
          @change="handleTypeChange"
        />
      </div>

      <!-- 资源条目列表 -->
      <div class="items-area">
        <div v-if="!selectedTypeId" class="empty-hint">请先选择资源类型</div>
        <div v-else-if="loading" class="empty-hint">加载中...</div>
        <div v-else-if="resourceItems.length === 0" class="empty-hint">该类型下暂无资源条目</div>
        <div
          v-for="item in resourceItems"
          :key="item.id"
          class="item-row"
          :class="{ 'item-linked': isItemLinked(item.id) }"
        >
          <input
            type="checkbox"
            :checked="selectedIds.has(item.id)"
            class="item-checkbox"
            @change="toggleItem(item)"
          />
          <span class="item-name">{{ item.name }}</span>
          <span class="item-type">{{ item.resource_type_name }}</span>
          <UiBadge :tone="statusTone(item.status)">
            {{ statusLabel(item.status) }}
          </UiBadge>
        </div>
      </div>

      <!-- 底部操作栏 -->
      <div class="modal-footer">
        <button class="btn-cancel" @click="handleCancel">取消</button>
        <button class="btn-confirm" @click="handleConfirm">确认</button>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 资源选择器组件（模态版）
 * 弹出模态框，按资源类型筛选并多选资源条目
 * 已关联的条目默认选中，确认后 emit 选中结果
 */
import { ref, watch, computed } from 'vue'
import { getResourceTypes, getResourceItems } from '@/api/resources'
import UiSelect from '@/components/ui/UiSelect.vue'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  visible: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'update:visible', 'confirm'])

// 资源类型列表
const resourceTypes = ref([])
// 当前选中的资源类型 ID
const selectedTypeId = ref(null)
// 资源类型选项（UiSelect 用）
const resourceTypeOptions = computed(() =>
  resourceTypes.value.map((t) => ({ label: t.name, value: t.id }))
)
// 当前类型下的资源条目
const resourceItems = ref([])
// 用户勾选的条目 ID 集合(初始化时从 modelValue 中读取)
const selectedIds = ref(new Set())
// 加载状态
const loading = ref(false)

// 状态中文标签映射
const statusLabelMap = {
  available: '可用',
  reserved: '已预约',
  in_use: '使用中',
  maintenance: '维护中',
  unavailable: '不可用'
}

// 获取状态中文标签
function statusLabel(status) {
  return statusLabelMap[status] || status
}

// item.id 是否在 modelValue 中(已关联标记)
function isItemLinked(itemId) {
  return props.modelValue.some((item) => item.id === itemId)
}

// 加载资源类型列表
async function fetchResourceTypes() {
  try {
    const response = await getResourceTypes()
    resourceTypes.value = response.data.results || response.data
  } catch (error) {
    console.error('加载资源类型失败:', error)
  }
}

// 资源类型变更：加载对应条目
async function handleTypeChange() {
  if (!selectedTypeId.value) {
    resourceItems.value = []
    return
  }
  loading.value = true
  try {
    const response = await getResourceItems({ resource_type: selectedTypeId.value })
    resourceItems.value = response.data.results || response.data
  } catch (error) {
    console.error('加载资源条目失败:', error)
  }
  loading.value = false
}

// 切换条目选中状态
function toggleItem(item) {
  const newSet = new Set(selectedIds.value)
  if (newSet.has(item.id)) {
    newSet.delete(item.id)
  } else {
    newSet.add(item.id)
  }
  selectedIds.value = newSet
}

// 取消：关闭弹窗
function handleCancel() {
  emit('update:visible', false)
}

// 确认：emit 选中结果并关闭弹窗
function handleConfirm() {
  // 组装选中的条目对象列表（从当前加载的 resourceItems 中筛选）
  const selectedItems = resourceItems.value.filter(
    (item) => selectedIds.value.has(item.id)
  )
  // 精简输出字段
  const result = selectedItems.map((item) => ({
    id: item.id,
    name: item.name,
    resource_type_name: item.resource_type_name,
    status: item.status
  }))
  const resultIds = result.map((item) => item.id)

  emit('update:modelValue', result)
  emit('confirm', resultIds)
  emit('update:visible', false)
}

// 弹窗打开时：初始化 selectedIds 为 modelValue 中的条目 ID
watch(
  () => props.visible,
  (isVisible) => {
    if (isVisible) {
      const ids = new Set(props.modelValue.map((item) => item.id))
      selectedIds.value = ids
      selectedTypeId.value = null
      resourceItems.value = []
      fetchResourceTypes()
    }
  }
)
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}

.modal-card {
  background-color: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  width: 560px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-xl);
}

.modal-title {
  margin: 0;
  padding: var(--space-5) var(--space-6) var(--space-4);
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-subtle);
}

.filter-area {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-6);
  border-bottom: 1px solid var(--border-subtle);
}

.filter-label {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  white-space: nowrap;
}

.type-select {
  flex: 1;
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--color-input);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  color: var(--text-primary);
  outline: none;
  background-color: var(--bg-surface);
  cursor: pointer;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.type-select:focus {
  border-color: var(--color-ring);
  box-shadow: 0 0 0 3px rgba(13, 13, 13, 0.08);
}

.items-area {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-2) 0;
  min-height: 120px;
  max-height: 360px;
}

.empty-hint {
  text-align: center;
  color: var(--text-muted);
  padding: var(--space-8) var(--space-6);
  font-size: var(--text-sm);
}

.item-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-6);
  cursor: pointer;
  transition: background-color var(--transition-fast);
}

.item-row:hover {
  background-color: var(--color-muted);
}

.item-row.item-linked {
  background-color: var(--bg-canvas);
}

.item-row.item-linked:hover {
  background-color: var(--color-muted);
}

.item-checkbox {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: var(--text-primary);
  flex-shrink: 0;
}

.item-name {
  flex: 1;
  font-size: var(--text-sm);
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-type {
  font-size: var(--text-xs);
  color: var(--text-muted);
  white-space: nowrap;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-6);
  border-top: 1px solid var(--border-subtle);
}

.btn-cancel {
  padding: var(--space-2) var(--space-5);
  border: 1px solid var(--color-input);
  border-radius: var(--radius-md);
  background-color: var(--bg-surface);
  color: var(--text-secondary);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: border-color var(--transition-fast), color var(--transition-fast), background-color var(--transition-fast);
}

.btn-cancel:hover {
  border-color: var(--text-primary);
  color: var(--text-primary);
  background-color: var(--color-muted);
}

.btn-confirm {
  padding: var(--space-2) var(--space-5);
  border: none;
  border-radius: var(--radius-md);
  background-color: var(--text-primary);
  color: var(--bg-surface);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.btn-confirm:hover {
  opacity: 0.85;
}

/* 移动端全屏化（路径 A 的 5 行 CSS） */
@media (max-width: 640px) {
  .modal-card {
    width: 100vw !important;
    height: 100vh !important;
    max-height: 100vh !important;
    border-radius: 0 !important;
  }
}
</style>
