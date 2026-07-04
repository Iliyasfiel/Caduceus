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
        <select
          v-model="selectedTypeId"
          class="type-select"
          @change="handleTypeChange"
        >
          <option :value="null" disabled>请选择资源类型</option>
          <option
            v-for="type in resourceTypes"
            :key="type.id"
            :value="type.id"
          >
            {{ type.name }}
          </option>
        </select>
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
          <span class="status-badge" :class="'status-' + item.status">
            {{ statusLabel(item.status) }}
          </span>
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
import { ref, watch } from 'vue'
import { getResourceTypes, getResourceItems } from '@/api/resources'

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
  background: #fff;
  border-radius: 10px;
  width: 560px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
}

.modal-title {
  margin: 0;
  padding: 20px 24px 16px;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  border-bottom: 1px solid #eee;
}

.filter-area {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 24px;
  border-bottom: 1px solid #f0f0f0;
}

.filter-label {
  font-size: 14px;
  color: #555;
  white-space: nowrap;
}

.type-select {
  flex: 1;
  padding: 7px 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  color: #333;
  outline: none;
  background: #fff;
  cursor: pointer;
}

.type-select:focus {
  border-color: #667eea;
}

.items-area {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
  min-height: 120px;
  max-height: 360px;
}

.empty-hint {
  text-align: center;
  color: #999;
  padding: 32px 24px;
  font-size: 14px;
}

.item-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 24px;
  cursor: pointer;
  transition: background 0.15s;
}

.item-row:hover {
  background: #f5f7fa;
}

.item-row.item-linked {
  background: #f9f9f9;
}

.item-row.item-linked:hover {
  background: #f0f0f0;
}

.item-checkbox {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: #667eea;
  flex-shrink: 0;
}

.item-name {
  flex: 1;
  font-size: 14px;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-type {
  font-size: 12px;
  color: #999;
  white-space: nowrap;
}

/* 状态彩色 badge */
.status-badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 10px;
  font-size: 12px;
  color: #fff;
  white-space: nowrap;
  flex-shrink: 0;
}

.status-available {
  background: #27ae60;
}

.status-reserved {
  background: #e67e22;
}

.status-in_use {
  background: #3498db;
}

.status-maintenance {
  background: #95a5a6;
}

.status-unavailable {
  background: #e74c3c;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 14px 24px;
  border-top: 1px solid #eee;
}

.btn-cancel {
  padding: 8px 20px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: #fff;
  color: #666;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-cancel:hover {
  background: #f5f5f5;
}

.btn-confirm {
  padding: 8px 20px;
  border: none;
  border-radius: 6px;
  background: #667eea;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-confirm:hover {
  background: #5a6fd6;
}
</style>
