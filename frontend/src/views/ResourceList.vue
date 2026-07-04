<!--
Caduceus 资源库管理页面
提供资源条目管理和资源类型管理两大功能模块
支持资源条目的增删改查、动态表单、操作日志查看
模板 / 样式 polish：使用 UiTabs / UiCard / UiBadge / UiButton / UiInput / UiSelect / UiModal / UiEmptyState。
业务逻辑（store / API / 表单 / 校验）零改动。
-->
<template>
  <AppLayout>
    <div class="resource-list">
      <div class="page-header">
        <h1 class="page-header__title">资源库</h1>
      </div>

      <!-- Tab 切换 -->
      <UiTabs
        v-model:activeKey="activeTab"
        :tabs="[
          { key: 'items', label: '资源条目管理' },
          { key: 'types', label: '资源类型管理' }
        ]"
      />

      <!-- ==================== 资源条目管理 Tab ==================== -->
      <div v-if="activeTab === 'items'" class="items-layout">
        <!-- 左侧：资源类型列表 -->
        <div class="types-sidebar">
          <div class="sidebar-title">资源类型</div>
          <div v-if="store.loading" class="sidebar-loading">加载中...</div>
          <div
            v-else
            class="type-item"
            :class="{ active: selectedTypeId === null }"
            @click="selectType(null)"
          >
            <span class="type-name">全部</span>
            <span class="type-badge">{{ totalItemCount }}</span>
          </div>
          <div
            v-for="type in store.resourceTypes"
            :key="type.id"
            class="type-item"
            :class="{ active: selectedTypeId === type.id }"
            @click="selectType(type.id)"
          >
            <span class="type-name">{{ type.name }}</span>
            <span class="type-badge">{{ getTypeItemCount(type.id) }}</span>
          </div>
        </div>

        <!-- 右侧：资源条目表格 -->
        <div class="items-main">
          <div class="items-toolbar">
            <div class="search-bar">
              <UiInput
                v-model="itemSearchQuery"
                placeholder="搜索资源名称..."
              />
            </div>
            <UiButton variant="primary" size="md" @click="openItemCreateDialog">
              + 新建条目
            </UiButton>
          </div>

          <div v-if="store.loading" class="loading">加载中...</div>

          <UiCard v-else class="table-card">
            <table class="data-table">
              <thead>
                <tr>
                  <th>名称</th>
                  <th>状态</th>
                  <th>字段值</th>
                  <th>位置</th>
                  <th>描述</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in filteredItems" :key="item.id">
                  <td class="cell-name">{{ item.name }}</td>
                  <td>
                    <UiBadge :tone="statusTone(item.status)">
                      {{ statusLabel(item.status) }}
                    </UiBadge>
                  </td>
                  <td class="cell-fields">{{ formatFieldSummary(item) }}</td>
                  <td class="cell-location">{{ item.location || '-' }}</td>
                  <td class="cell-desc">{{ truncate(item.description, 30) }}</td>
                  <td class="cell-actions">
                    <button class="btn-action" @click="openItemEditDialog(item)">编辑</button>
                    <button class="btn-action btn-danger-text" @click="handleDeleteItem(item)">删除</button>
                    <button class="btn-action" @click="openLogDialog(item)">日志</button>
                  </td>
                </tr>
              </tbody>
            </table>
            <UiEmptyState
              v-if="filteredItems.length === 0"
              class="table-empty"
              title="暂无资源条目"
            />
          </UiCard>
        </div>
      </div>

      <!-- ==================== 资源类型管理 Tab ==================== -->
      <div v-if="activeTab === 'types'" class="types-layout">
        <div class="types-toolbar">
          <h3 class="section-title">资源类型列表</h3>
          <UiButton variant="primary" size="md" @click="openTypeCreateDialog">
            + 新建类型
          </UiButton>
        </div>

        <div v-if="store.loading" class="loading">加载中...</div>

        <UiCard v-else class="table-card">
          <table class="data-table">
            <thead>
              <tr>
                <th>名称</th>
                <th>描述</th>
                <th>图标</th>
                <th>是否启用</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="type in store.resourceTypes" :key="type.id">
                <td class="cell-name">{{ type.name }}</td>
                <td class="cell-desc">{{ truncate(type.description, 40) }}</td>
                <td>{{ type.icon || '-' }}</td>
                <td>
                  <UiBadge :tone="type.is_active ? 'success' : 'neutral'">
                    {{ type.is_active ? '启用' : '禁用' }}
                  </UiBadge>
                </td>
                <td class="cell-actions">
                  <button class="btn-action" @click="openTypeEditDialog(type)">编辑</button>
                </td>
              </tr>
            </tbody>
          </table>
          <UiEmptyState
            v-if="store.resourceTypes.length === 0"
            class="table-empty"
            title="暂无资源类型"
          />
        </UiCard>
      </div>

      <!-- ==================== 新建/编辑资源条目弹窗 ==================== -->
      <UiModal
        v-model="itemDialogVisible"
        :title="editingItem ? '编辑资源条目' : '新建资源条目'"
        size="md"
      >
        <div class="form-stack">
          <div class="form-group">
            <label>资源类型 <span class="required">*</span></label>
            <select
              v-model="itemForm.resource_type"
              class="form-input"
              :disabled="!!editingItem"
              @change="onItemTypeChange"
            >
              <option :value="null" disabled>请选择资源类型</option>
              <option
                v-for="type in store.resourceTypes"
                :key="type.id"
                :value="type.id"
              >
                {{ type.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>名称 <span class="required">*</span></label>
            <UiInput
              v-model="itemForm.name"
              placeholder="请输入资源名称"
            />
          </div>
          <div class="form-group">
            <label>描述</label>
            <textarea
              v-model="itemForm.description"
              class="form-input form-textarea"
              rows="2"
              placeholder="请输入资源描述"
            ></textarea>
          </div>
          <div class="form-row">
            <div class="form-group form-group-half">
              <label>位置</label>
              <UiInput
                v-model="itemForm.location"
                placeholder="如：A栋3楼机房"
              />
            </div>
            <div class="form-group form-group-half">
              <label>状态</label>
              <UiSelect
                v-model="itemForm.status"
                :options="statusOptions"
              />
            </div>
          </div>

          <!-- 根据 field_schema 动态生成字段 -->
          <div v-for="field in itemFormFields" :key="field.key" class="form-group">
            <label>{{ field.label || field.key }}</label>
            <!-- text 类型 -->
            <UiInput
              v-if="field.type === 'text' || !field.type"
              v-model="itemForm.field_values[field.key]"
            />
            <!-- textarea 类型 -->
            <textarea
              v-else-if="field.type === 'textarea'"
              v-model="itemForm.field_values[field.key]"
              class="form-input form-textarea"
              rows="3"
            ></textarea>
            <!-- number 类型 -->
            <UiInput
              v-else-if="field.type === 'number'"
              v-model.number="itemForm.field_values[field.key]"
              type="number"
            />
            <!-- select 类型 -->
            <select
              v-else-if="field.type === 'select'"
              v-model="itemForm.field_values[field.key]"
              class="form-input"
            >
              <option value="">请选择</option>
              <option
                v-for="opt in (field.options || [])"
                :key="opt"
                :value="opt"
              >
                {{ opt }}
              </option>
            </select>
          </div>
        </div>
        <template #footer>
          <UiButton variant="secondary" @click="itemDialogVisible = false">取消</UiButton>
          <UiButton
            variant="primary"
            :loading="itemSubmitting"
            @click="submitItem"
          >
            确认
          </UiButton>
        </template>
      </UiModal>

      <!-- ==================== 新建/编辑资源类型弹窗 ==================== -->
      <UiModal
        v-model="typeDialogVisible"
        :title="editingType ? '编辑资源类型' : '新建资源类型'"
        size="md"
      >
        <div class="form-stack">
          <div class="form-group">
            <label>名称 <span class="required">*</span></label>
            <UiInput
              v-model="typeForm.name"
              placeholder="如：服务器"
            />
          </div>
          <div class="form-group">
            <label>描述</label>
            <textarea
              v-model="typeForm.description"
              class="form-input form-textarea"
              rows="2"
              placeholder="请输入资源类型描述"
            ></textarea>
          </div>
          <div class="form-row">
            <div class="form-group form-group-half">
              <label>图标</label>
              <UiInput
                v-model="typeForm.icon"
                placeholder="如：server"
              />
            </div>
            <div class="form-group form-group-half">
              <label>是否启用</label>
              <div class="switch-wrapper">
                <label class="switch">
                  <input
                    v-model="typeForm.is_active"
                    type="checkbox"
                  />
                  <span class="switch-slider"></span>
                </label>
                <span class="switch-label">{{ typeForm.is_active ? '已启用' : '已禁用' }}</span>
              </div>
            </div>
          </div>
          <div class="form-group">
            <label>字段定义（field_schema）</label>
            <p class="form-hint">
              JSON 数组格式，每项含 key、label、type（text/textarea/number/select），select 类型需含 options
            </p>
            <textarea
              v-model="typeForm.field_schema_text"
              class="form-input form-textarea form-textarea-json"
              rows="6"
              placeholder='[{"key": "ip", "label": "IP地址", "type": "text"}, {"key": "os", "label": "操作系统", "type": "select", "options": ["Ubuntu", "CentOS"]}]'
            ></textarea>
            <p v-if="typeForm.field_schema_error" class="form-error">
              {{ typeForm.field_schema_error }}
            </p>
          </div>
        </div>
        <template #footer>
          <UiButton variant="secondary" @click="typeDialogVisible = false">取消</UiButton>
          <UiButton
            variant="primary"
            :loading="typeSubmitting"
            @click="submitType"
          >
            确认
          </UiButton>
        </template>
      </UiModal>

      <!-- ==================== 操作日志弹窗 ==================== -->
      <UiModal
        v-model="logDialogVisible"
        :title="`操作日志 - ${logItem?.name || ''}`"
        size="md"
      >
        <div v-if="logLoading" class="loading">加载中...</div>
        <UiEmptyState v-else-if="logs.length === 0" title="暂无操作日志" />
        <div v-else class="timeline">
          <div
            v-for="log in logs"
            :key="log.id"
            class="timeline-item"
          >
            <div class="timeline-dot"></div>
            <div class="timeline-content">
              <div class="timeline-event">{{ log.event_key || log.action || '-' }}</div>
              <div class="timeline-summary" v-if="log.summary">{{ log.summary }}</div>
              <div class="timeline-details" v-if="log.details">{{ log.details }}</div>
              <div class="timeline-operator">
                {{ log.operator_name || '-' }} · {{ formatTime(log.created_at) }}
              </div>
            </div>
          </div>
        </div>
      </UiModal>
    </div>
  </AppLayout>
</template>

<script setup>
/**
 * Caduceus ResourceList 页面脚本
 * 业务逻辑零改动：store / API / 表单校验 / 动态字段 / 日志加载 全部保留。
 * 仅 alert() 替换为 useToast()；confirm() 保留原生（业务行为一致）。
 */
import { ref, reactive, computed, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { useResourcesStore } from '@/stores/resources'
import {
  createResourceItem,
  updateResourceItem,
  deleteResourceItem,
  getResourceLogs,
  createResourceType,
  updateResourceType
} from '@/api/resources'
import { useToast } from '@/stores/toast'
import {
  UiButton, UiInput, UiSelect, UiCard, UiBadge, UiModal, UiEmptyState, UiTabs
} from '@/components/ui'

const store = useResourcesStore()
const toast = useToast()

// 当前激活的 Tab
const activeTab = ref('items')

// 资源条目搜索
const itemSearchQuery = ref('')

// 选中的资源类型 ID（null 表示全部）
const selectedTypeId = ref(null)

// 状态选项列表
const statusOptions = [
  ['可用',     'available'],
  ['已预约',   'reserved'],
  ['使用中',   'in_use'],
  ['维修中',   'maintenance'],
  ['不可用',   'unavailable']
]

// 状态映射配置
const statusMap = {
  available:   { label: '可用',   tone: 'success' },
  reserved:    { label: '已预约', tone: 'warning' },
  in_use:      { label: '使用中', tone: 'info' },
  maintenance: { label: '维修中', tone: 'warning' },
  unavailable: { label: '不可用', tone: 'neutral' }
}

// 获取状态中文标签
function statusLabel(status) {
  return statusMap[status]?.label || status || '-'
}

// 获取状态 tone
function statusTone(status) {
  return statusMap[status]?.tone || 'neutral'
}

// 格式化时间
function formatTime(isoStr) {
  if (!isoStr) return '-'
  const d = new Date(isoStr)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

// 截断文本
function truncate(text, maxLen) {
  if (!text) return '-'
  return text.length > maxLen ? text.slice(0, maxLen) + '...' : text
}

// 获取某类型下的资源条目数量
function getTypeItemCount(typeId) {
  return store.resourceItems.filter((item) => item.resource_type === typeId).length
}

// 全部条目总数
const totalItemCount = computed(() => store.resourceItems.length)

// 按类型和搜索词过滤资源条目
const filteredItems = computed(() => {
  let items = store.resourceItems
  if (selectedTypeId.value !== null) {
    items = items.filter((item) => item.resource_type === selectedTypeId.value)
  }
  if (itemSearchQuery.value.trim()) {
    const q = itemSearchQuery.value.trim().toLowerCase()
    items = items.filter((item) => item.name.toLowerCase().includes(q))
  }
  return items
})

// 选中资源类型
function selectType(typeId) {
  selectedTypeId.value = typeId
}

// 获取资源类型的 field_schema
function getTypeFieldSchema(typeId) {
  if (!typeId) return []
  const type = store.resourceTypes.find((t) => t.id === typeId)
  if (!type || !type.field_schema) return []
  // 兼容数组和对象格式
  if (Array.isArray(type.field_schema)) return type.field_schema
  return type.field_schema.fields || []
}

// 格式化字段值摘要
function formatFieldSummary(item) {
  const schema = getTypeFieldSchema(item.resource_type)
  if (!schema.length) return '-'
  // 取前两个有值的字段展示
  const values = item.field_values || item.field_data || {}
  const keys = schema.map((f) => f.key).filter((k) => values[k] != null && values[k] !== '')
  const shown = keys.slice(0, 2)
  if (!shown.length) return '-'
  return shown.map((k) => values[k]).join(' / ')
}

// ==================== 资源条目弹窗 ====================
const itemDialogVisible = ref(false)
const itemSubmitting = ref(false)
const editingItem = ref(null)

const itemForm = reactive({
  name: '',
  resource_type: null,
  description: '',
  location: '',
  status: 'available',
  field_values: {}
})

// 当前正在编辑/新建时的动态字段列表
const itemFormFields = computed(() => {
  if (!itemForm.resource_type) return []
  return getTypeFieldSchema(itemForm.resource_type)
})

// 切换资源类型时重置 field_values
function onItemTypeChange() {
  itemForm.field_values = {}
}

// 打开新建条目弹窗
function openItemCreateDialog() {
  editingItem.value = null
  itemForm.name = ''
  itemForm.resource_type = null
  itemForm.description = ''
  itemForm.location = ''
  itemForm.status = 'available'
  itemForm.field_values = {}
  itemDialogVisible.value = true
}

// 打开编辑条目弹窗
function openItemEditDialog(item) {
  editingItem.value = item
  itemForm.name = item.name
  itemForm.resource_type = item.resource_type
  itemForm.description = item.description || ''
  itemForm.location = item.location || ''
  itemForm.status = item.status || 'available'
  // 兼容 field_values 和 field_data 字段名
  const fv = item.field_values || item.field_data || {}
  itemForm.field_values = { ...fv }
  itemDialogVisible.value = true
}

// 提交资源条目（新建或编辑）
async function submitItem() {
  if (!itemForm.name || !itemForm.resource_type) {
    toast.error('请填写名称和资源类型')
    return
  }
  itemSubmitting.value = true
  try {
    const payload = {
      name: itemForm.name,
      description: itemForm.description,
      location: itemForm.location,
      status: itemForm.status,
      field_values: itemForm.field_values
    }
    if (editingItem.value) {
      await updateResourceItem(editingItem.value.id, payload)
    } else {
      await createResourceItem({
        ...payload,
        resource_type: itemForm.resource_type
      })
    }
    itemDialogVisible.value = false
    toast.success(editingItem.value ? '条目更新成功' : '条目创建成功')
    await store.fetchResourceItems()
  } catch (error) {
    console.error('保存资源条目失败:', error)
    toast.error('保存失败：' + (error.response?.data?.detail || error.message))
  }
  itemSubmitting.value = false
}

// 删除资源条目
async function handleDeleteItem(item) {
  const ok = await confirm({
    title: '删除资源条目',
    message: `确定要删除资源条目「${item.name}」吗？此操作不可撤销。`,
    tone: 'danger',
    confirmText: '删除'
  })
  if (!ok) return
  try {
    await deleteResourceItem(item.id)
    toast.success('条目已删除')
    await store.fetchResourceItems()
  } catch (error) {
    console.error('删除资源条目失败:', error)
    toast.error('删除失败：' + (error.response?.data?.detail || error.message))
  }
}

// ==================== 资源类型弹窗 ====================
const typeDialogVisible = ref(false)
const typeSubmitting = ref(false)
const editingType = ref(null)

const typeForm = reactive({
  name: '',
  description: '',
  icon: '',
  is_active: true,
  field_schema_text: '[]',
  field_schema_error: ''
})

// 打开新建类型弹窗
function openTypeCreateDialog() {
  editingType.value = null
  typeForm.name = ''
  typeForm.description = ''
  typeForm.icon = ''
  typeForm.is_active = true
  typeForm.field_schema_text = '[]'
  typeForm.field_schema_error = ''
  typeDialogVisible.value = true
}

// 打开编辑类型弹窗
function openTypeEditDialog(type) {
  editingType.value = type
  typeForm.name = type.name
  typeForm.description = type.description || ''
  typeForm.icon = type.icon || ''
  typeForm.is_active = type.is_active
  const schema = type.field_schema
  if (typeof schema === 'string') {
    typeForm.field_schema_text = schema
  } else if (schema) {
    typeForm.field_schema_text = JSON.stringify(schema, null, 2)
  } else {
    typeForm.field_schema_text = '[]'
  }
  typeForm.field_schema_error = ''
  typeDialogVisible.value = true
}

// 提交资源类型（新建或编辑）
async function submitType() {
  if (!typeForm.name.trim()) {
    toast.error('请填写类型名称')
    return
  }
  // 校验 field_schema JSON 格式
  let fieldSchema
  try {
    fieldSchema = JSON.parse(typeForm.field_schema_text)
    if (!Array.isArray(fieldSchema)) {
      typeForm.field_schema_error = 'field_schema 必须是一个 JSON 数组'
      return
    }
  } catch {
    typeForm.field_schema_error = 'JSON 格式不合法，请检查'
    return
  }
  typeForm.field_schema_error = ''

  typeSubmitting.value = true
  try {
    const payload = {
      name: typeForm.name,
      description: typeForm.description,
      icon: typeForm.icon,
      is_active: typeForm.is_active,
      field_schema: fieldSchema
    }
    if (editingType.value) {
      await updateResourceType(editingType.value.id, payload)
    } else {
      await createResourceType(payload)
    }
    typeDialogVisible.value = false
    toast.success(editingType.value ? '类型更新成功' : '类型创建成功')
    await store.fetchResourceTypes()
  } catch (error) {
    console.error('保存资源类型失败:', error)
    toast.error('保存失败：' + (error.response?.data?.detail || error.message))
  }
  typeSubmitting.value = false
}

// ==================== 操作日志弹窗 ====================
const logDialogVisible = ref(false)
const logLoading = ref(false)
const logItem = ref(null)
const logs = ref([])

// 打开操作日志弹窗
async function openLogDialog(item) {
  logItem.value = item
  logDialogVisible.value = true
  logLoading.value = true
  logs.value = []
  try {
    const res = await getResourceLogs(item.id)
    logs.value = res.data.results || res.data || []
  } catch (error) {
    console.error('获取操作日志失败:', error)
  }
  logLoading.value = false
}

// 初始化：加载数据
onMounted(async () => {
  await store.fetchResourceTypes()
  await store.fetchResourceItems()
})
</script>

<style scoped>
.resource-list {
  padding: var(--space-6);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.page-header__title {
  font-size: var(--text-2xl);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

/* ===== 资源条目管理布局 ===== */
.items-layout {
  display: flex;
  gap: var(--space-5);
}

/* 左侧类型侧边栏 */
.types-sidebar {
  width: 220px;
  min-width: 220px;
  background-color: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: var(--space-3) 0;
  align-self: flex-start;
}

.sidebar-title {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--text-primary);
  padding: 0 var(--space-4) var(--space-2);
  border-bottom: 1px solid var(--border-subtle);
}

.sidebar-loading {
  padding: var(--space-4);
  color: var(--text-muted);
  text-align: center;
  font-size: var(--text-xs);
}

.type-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-2) var(--space-4);
  cursor: pointer;
  transition: background-color var(--transition-fast);
}

.type-item:hover {
  background-color: var(--color-muted);
}

.type-item.active {
  background-color: var(--color-muted);
  color: var(--text-primary);
  font-weight: 600;
}

.type-name {
  font-size: var(--text-sm);
}

.type-badge {
  background-color: var(--color-muted);
  color: var(--text-secondary);
  padding: 1px 8px;
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: 500;
}

.type-item.active .type-badge {
  background-color: var(--text-primary);
  color: var(--bg-surface);
}

/* 右侧主区域 */
.items-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.items-toolbar {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--space-3);
}

.items-toolbar .search-bar {
  flex: 1;
  max-width: 320px;
}

/* 通用数据表格 */
.table-card :deep(.ui-card__body) {
  padding: 0;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-sm);
}

.data-table th {
  background-color: var(--bg-canvas);
  padding: var(--space-3) var(--space-4);
  text-align: left;
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border-subtle);
  white-space: nowrap;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.data-table td {
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-sm);
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-subtle);
  vertical-align: middle;
}

.data-table tbody tr:hover {
  background-color: var(--bg-canvas);
}

.data-table tbody tr:last-child td {
  border-bottom: 0;
}

.table-empty {
  padding: var(--space-8);
}

.cell-name {
  font-weight: 500;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text-primary);
}

.cell-fields {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cell-location {
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text-secondary);
}

.cell-desc {
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text-muted);
  font-size: var(--text-xs);
}

.cell-actions {
  white-space: nowrap;
}

.btn-action {
  padding: 4px 12px;
  border: 1px solid var(--color-input);
  background-color: var(--bg-surface);
  color: var(--text-secondary);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: var(--text-xs);
  margin-right: var(--space-1);
  transition: border-color var(--transition-fast), color var(--transition-fast);
}

.btn-action:hover {
  border-color: var(--text-primary);
  color: var(--text-primary);
}

.btn-danger-text {
  color: var(--color-destructive);
  border-color: var(--color-destructive);
}

.btn-danger-text:hover {
  background-color: var(--badge-danger-bg);
  color: var(--color-destructive);
  border-color: var(--color-destructive);
}

/* ===== 资源类型管理 ===== */
.types-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  margin: 0;
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--text-primary);
}

/* 表单 */
.form-stack {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.form-group label {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--text-primary);
}

.form-row {
  display: flex;
  gap: var(--space-3);
}

.form-group-half {
  flex: 1;
}

.required {
  color: var(--color-destructive);
}

.form-input {
  width: 100%;
  padding: var(--space-3);
  border: 1px solid var(--color-input);
  border-radius: var(--radius-md);
  background-color: var(--bg-surface);
  font-size: var(--text-sm);
  color: var(--text-primary);
  outline: none;
  box-sizing: border-box;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.form-input:focus {
  border-color: var(--color-ring);
  box-shadow: 0 0 0 3px rgba(13, 13, 13, 0.08);
}

.form-input:disabled {
  background-color: var(--color-muted);
  color: var(--text-muted);
}

.form-textarea {
  resize: vertical;
  font-family: inherit;
}

.form-textarea-json {
  font-family: 'SF Mono', 'Menlo', 'Monaco', monospace;
  font-size: var(--text-xs);
  line-height: 1.5;
}

.form-hint {
  font-size: var(--text-xs);
  color: var(--text-muted);
  line-height: 1.5;
  margin: -4px 0 var(--space-2);
}

.form-error {
  font-size: var(--text-xs);
  color: var(--color-destructive);
  margin-top: var(--space-1);
}

/* Switch 开关 */
.switch-wrapper {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding-top: var(--space-1);
}

.switch {
  position: relative;
  display: inline-block;
  width: 42px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.switch-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--color-muted);
  border-radius: var(--radius-full);
  transition: var(--transition-fast);
}

.switch-slider::before {
  content: '';
  position: absolute;
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: var(--bg-surface);
  border-radius: var(--radius-full);
  transition: var(--transition-fast);
}

.switch input:checked + .switch-slider {
  background-color: var(--text-primary);
}

.switch input:checked + .switch-slider::before {
  transform: translateX(18px);
}

.switch-label {
  font-size: var(--text-xs);
  color: var(--text-secondary);
}

/* 时间线 */
.timeline {
  position: relative;
  padding-left: var(--space-6);
}

.timeline::before {
  content: '';
  position: absolute;
  left: 7px;
  top: 0;
  bottom: 0;
  width: 2px;
  background-color: var(--border-subtle);
}

.timeline-item {
  position: relative;
  margin-bottom: var(--space-4);
}

.timeline-dot {
  position: absolute;
  left: -20px;
  top: 4px;
  width: 10px;
  height: 10px;
  border-radius: var(--radius-full);
  background-color: var(--text-primary);
}

.timeline-content {
  font-size: var(--text-sm);
}

.timeline-event {
  font-weight: 600;
  color: var(--text-primary);
}

.timeline-summary {
  color: var(--text-secondary);
  margin-top: 2px;
}

.timeline-details {
  color: var(--text-muted);
  font-size: var(--text-xs);
  font-family: monospace;
  background-color: var(--color-muted);
  padding: var(--space-2);
  border-radius: var(--radius-sm);
  margin-top: var(--space-1);
  white-space: pre-wrap;
  word-break: break-all;
}

.timeline-operator {
  color: var(--text-muted);
  font-size: var(--text-xs);
  margin-top: 2px;
}

.loading {
  text-align: center;
  padding: var(--space-12);
  color: var(--text-muted);
  font-size: var(--text-sm);
}
</style>