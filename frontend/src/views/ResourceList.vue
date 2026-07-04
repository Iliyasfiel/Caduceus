<!--
Caduceus 资源库管理页面
提供资源条目管理和资源类型管理两大功能模块
支持资源条目的增删改查、动态表单、操作日志查看
-->
<template>
  <AppLayout>
    <div class="resource-list">
      <div class="page-header">
        <h1>资源库</h1>
      </div>

      <!-- Tab 切换 -->
      <div class="tabs">
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'items' }"
          @click="activeTab = 'items'"
        >
          资源条目管理
        </button>
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'types' }"
          @click="activeTab = 'types'"
        >
          资源类型管理
        </button>
      </div>

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
              <input
                v-model="itemSearchQuery"
                type="text"
                placeholder="搜索资源名称..."
                class="search-input"
              />
            </div>
            <button class="btn-primary" @click="openItemCreateDialog">+ 新建条目</button>
          </div>

          <div v-if="store.loading" class="loading">加载中...</div>

          <table v-else class="data-table">
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
                  <span class="status-badge" :class="statusClass(item.status)">
                    {{ statusLabel(item.status) }}
                  </span>
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
              <tr v-if="filteredItems.length === 0">
                <td colspan="6" class="empty-tip">暂无资源条目</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ==================== 资源类型管理 Tab ==================== -->
      <div v-if="activeTab === 'types'" class="types-layout">
        <div class="types-toolbar">
          <h3 class="section-title">资源类型列表</h3>
          <button class="btn-primary" @click="openTypeCreateDialog">+ 新建类型</button>
        </div>

        <div v-if="store.loading" class="loading">加载中...</div>

        <table v-else class="data-table">
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
                <span class="status-badge" :class="type.is_active ? 'status-green' : 'status-gray'">
                  {{ type.is_active ? '启用' : '禁用' }}
                </span>
              </td>
              <td class="cell-actions">
                <button class="btn-action" @click="openTypeEditDialog(type)">编辑</button>
              </td>
            </tr>
            <tr v-if="store.resourceTypes.length === 0">
              <td colspan="5" class="empty-tip">暂无资源类型</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- ==================== 新建/编辑资源条目弹窗 ==================== -->
      <div v-if="itemDialogVisible" class="dialog-overlay" @click.self="itemDialogVisible = false">
        <div class="dialog">
          <div class="dialog-header">
            <h2>{{ editingItem ? '编辑资源条目' : '新建资源条目' }}</h2>
            <button class="dialog-close" @click="itemDialogVisible = false">✕</button>
          </div>
          <div class="dialog-body">
            <!-- 资源类型选择（仅新建时） -->
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
              <input
                v-model="itemForm.name"
                type="text"
                class="form-input"
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
                <input
                  v-model="itemForm.location"
                  type="text"
                  class="form-input"
                  placeholder="如：A栋3楼机房"
                />
              </div>
              <div class="form-group form-group-half">
                <label>状态</label>
                <select v-model="itemForm.status" class="form-input">
                  <option
                    v-for="opt in statusOptions"
                    :key="opt.value"
                    :value="opt.value"
                  >
                    {{ opt.label }}
                  </option>
                </select>
              </div>
            </div>

            <!-- 根据 field_schema 动态生成字段 -->
            <div v-for="field in itemFormFields" :key="field.key" class="form-group">
              <label>{{ field.label || field.key }}</label>
              <!-- text 类型 -->
              <input
                v-if="field.type === 'text' || !field.type"
                v-model="itemForm.field_values[field.key]"
                type="text"
                class="form-input"
              />
              <!-- textarea 类型 -->
              <textarea
                v-else-if="field.type === 'textarea'"
                v-model="itemForm.field_values[field.key]"
                class="form-input form-textarea"
                rows="3"
              ></textarea>
              <!-- number 类型 -->
              <input
                v-else-if="field.type === 'number'"
                v-model.number="itemForm.field_values[field.key]"
                type="number"
                class="form-input"
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

            <div class="form-actions">
              <button class="btn-secondary" @click="itemDialogVisible = false">取消</button>
              <button class="btn-primary" @click="submitItem" :disabled="itemSubmitting">
                {{ itemSubmitting ? '提交中...' : '确认' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- ==================== 新建/编辑资源类型弹窗 ==================== -->
      <div v-if="typeDialogVisible" class="dialog-overlay" @click.self="typeDialogVisible = false">
        <div class="dialog">
          <div class="dialog-header">
            <h2>{{ editingType ? '编辑资源类型' : '新建资源类型' }}</h2>
            <button class="dialog-close" @click="typeDialogVisible = false">✕</button>
          </div>
          <div class="dialog-body">
            <div class="form-group">
              <label>名称 <span class="required">*</span></label>
              <input
                v-model="typeForm.name"
                type="text"
                class="form-input"
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
                <input
                  v-model="typeForm.icon"
                  type="text"
                  class="form-input"
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

            <div class="form-actions">
              <button class="btn-secondary" @click="typeDialogVisible = false">取消</button>
              <button class="btn-primary" @click="submitType" :disabled="typeSubmitting">
                {{ typeSubmitting ? '提交中...' : '确认' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- ==================== 操作日志弹窗 ==================== -->
      <div v-if="logDialogVisible" class="dialog-overlay" @click.self="logDialogVisible = false">
        <div class="dialog">
          <div class="dialog-header">
            <h2>操作日志 - {{ logItem?.name }}</h2>
            <button class="dialog-close" @click="logDialogVisible = false">✕</button>
          </div>
          <div class="dialog-body">
            <div v-if="logLoading" class="loading">加载中...</div>
            <div v-else-if="logs.length === 0" class="empty-tip">暂无操作日志</div>
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
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
/**
 * Caduceus 资源库管理页面
 * 包含资源条目管理和资源类型管理两个Tab
 * 支持动态表单、操作日志查看等功能
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

const store = useResourcesStore()

// 当前激活的 Tab
const activeTab = ref('items')

// 资源条目搜索
const itemSearchQuery = ref('')

// 选中的资源类型 ID（null 表示全部）
const selectedTypeId = ref(null)

// 状态选项列表
const statusOptions = [
  { value: 'available', label: '可用' },
  { value: 'reserved', label: '已预约' },
  { value: 'in_use', label: '使用中' },
  { value: 'maintenance', label: '维修中' },
  { value: 'unavailable', label: '不可用' }
]

// 状态映射配置
const statusMap = {
  available: { label: '可用', class: 'status-green' },
  reserved: { label: '已预约', class: 'status-blue' },
  in_use: { label: '使用中', class: 'status-orange' },
  maintenance: { label: '维修中', class: 'status-yellow' },
  unavailable: { label: '不可用', class: 'status-gray' }
}

// 获取状态中文标签
function statusLabel(status) {
  return statusMap[status]?.label || status || '-'
}

// 获取状态样式类
function statusClass(status) {
  return statusMap[status]?.class || ''
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
    alert('请填写名称和资源类型')
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
    await store.fetchResourceItems()
  } catch (error) {
    console.error('保存资源条目失败:', error)
    alert('保存失败：' + (error.response?.data?.detail || error.message))
  }
  itemSubmitting.value = false
}

// 删除资源条目
async function handleDeleteItem(item) {
  const confirmed = confirm(`确定要删除资源条目「${item.name}」吗？此操作不可撤销。`)
  if (!confirmed) return
  try {
    await deleteResourceItem(item.id)
    await store.fetchResourceItems()
  } catch (error) {
    console.error('删除资源条目失败:', error)
    alert('删除失败：' + (error.response?.data?.detail || error.message))
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
    alert('请填写类型名称')
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
    await store.fetchResourceTypes()
  } catch (error) {
    console.error('保存资源类型失败:', error)
    alert('保存失败：' + (error.response?.data?.detail || error.message))
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
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0;
  font-size: 22px;
  color: #1a1a1a;
}

/* Tab 切换 */
.tabs {
  display: flex;
  gap: 0;
  border-bottom: 2px solid #eee;
  margin-bottom: 20px;
}

.tab-btn {
  padding: 10px 24px;
  border: none;
  background: none;
  color: #666;
  font-size: 15px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: #333;
}

.tab-btn.active {
  color: #667eea;
  border-bottom-color: #667eea;
  font-weight: 600;
}

/* ===== 资源条目管理布局 ===== */
.items-layout {
  display: flex;
  gap: 24px;
}

/* 左侧类型侧边栏 */
.types-sidebar {
  width: 220px;
  min-width: 220px;
  background: #fafafa;
  border-radius: 8px;
  border: 1px solid #eee;
  padding: 12px 0;
}

.sidebar-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  padding: 0 16px 10px;
  border-bottom: 1px solid #eee;
}

.sidebar-loading {
  padding: 20px 16px;
  color: #999;
  text-align: center;
  font-size: 13px;
}

.type-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  cursor: pointer;
  transition: background 0.15s;
}

.type-item:hover {
  background: #f0f4ff;
}

.type-item.active {
  background: #e8edff;
  color: #667eea;
  font-weight: 500;
}

.type-name {
  font-size: 14px;
}

.type-badge {
  background: #e0e0e0;
  color: #666;
  padding: 1px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
}

.type-item.active .type-badge {
  background: #667eea;
  color: #fff;
}

/* 右侧主区域 */
.items-main {
  flex: 1;
  min-width: 0;
}

.items-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  gap: 12px;
}

.items-toolbar .search-bar {
  flex: 1;
  max-width: 320px;
}

/* 搜索框 */
.search-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  outline: none;
  box-sizing: border-box;
}

.search-input:focus {
  border-color: #667eea;
}

/* 通用数据表格 */
.data-table {
  width: 100%;
  border-collapse: collapse;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #eee;
}

.data-table th {
  background: #f8f9fa;
  padding: 10px 14px;
  text-align: left;
  font-size: 13px;
  font-weight: 600;
  color: #555;
  border-bottom: 1px solid #eee;
  white-space: nowrap;
}

.data-table td {
  padding: 12px 14px;
  font-size: 14px;
  color: #333;
  border-bottom: 1px solid #f0f0f0;
  vertical-align: middle;
}

.data-table tbody tr:hover {
  background: #fafbff;
}

.data-table tbody tr:last-child td {
  border-bottom: none;
}

.cell-name {
  font-weight: 500;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cell-fields {
  font-size: 13px;
  color: #666;
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
  color: #666;
}

.cell-desc {
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #888;
  font-size: 13px;
}

.cell-actions {
  white-space: nowrap;
}

.btn-action {
  padding: 4px 12px;
  border: 1px solid #ddd;
  background: #fff;
  color: #555;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  margin-right: 6px;
  transition: all 0.15s;
}

.btn-action:hover {
  border-color: #667eea;
  color: #667eea;
}

.btn-danger-text {
  color: #e74c3c;
  border-color: #fdd;
}

.btn-danger-text:hover {
  background: #fff5f5;
  color: #c0392b;
  border-color: #e74c3c;
}

/* ===== 资源类型管理 ===== */
.types-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title {
  margin: 0;
  font-size: 16px;
  color: #333;
}

/* 状态标签 */
.status-badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.status-green {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-blue {
  background: #e3f2fd;
  color: #1565c0;
}

.status-orange {
  background: #fff3e0;
  color: #e65100;
}

.status-yellow {
  background: #fffde7;
  color: #f9a825;
}

.status-gray {
  background: #f5f5f5;
  color: #888;
}

/* 通用按钮 */
.btn-primary {
  padding: 8px 20px;
  background: #667eea;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
  white-space: nowrap;
}

.btn-primary:hover {
  background: #5a6fd6;
}

.btn-primary:disabled {
  background: #b0b0b0;
  cursor: not-allowed;
}

.btn-secondary {
  padding: 8px 20px;
  background: #f0f0f0;
  color: #333;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.btn-secondary:hover {
  background: #e0e0e0;
}

/* 对话框 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.dialog {
  background: #fff;
  border-radius: 10px;
  width: 90%;
  max-width: 620px;
  max-height: 80vh;
  overflow-y: auto;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
}

.dialog-header h2 {
  margin: 0;
  font-size: 18px;
}

.dialog-close {
  background: none;
  border: none;
  font-size: 20px;
  color: #999;
  cursor: pointer;
}

.dialog-close:hover {
  color: #333;
}

.dialog-body {
  padding: 20px;
}

/* 表单 */
.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-group-half {
  flex: 1;
}

.required {
  color: #e74c3c;
}

.form-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  outline: none;
  box-sizing: border-box;
}

.form-input:focus {
  border-color: #667eea;
}

.form-input:disabled {
  background: #f5f5f5;
  color: #999;
}

.form-textarea {
  resize: vertical;
}

.form-textarea-json {
  font-family: 'SF Mono', 'Menlo', 'Monaco', monospace;
  font-size: 13px;
  line-height: 1.5;
}

.form-hint {
  font-size: 12px;
  color: #999;
  margin-top: -4px;
  margin-bottom: 8px;
  line-height: 1.5;
}

.form-error {
  font-size: 12px;
  color: #e74c3c;
  margin-top: 4px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
}

/* Switch 开关 */
.switch-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  padding-top: 4px;
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
  background: #ccc;
  border-radius: 24px;
  transition: 0.3s;
}

.switch-slider::before {
  content: '';
  position: absolute;
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background: #fff;
  border-radius: 50%;
  transition: 0.3s;
}

.switch input:checked + .switch-slider {
  background: #667eea;
}

.switch input:checked + .switch-slider::before {
  transform: translateX(18px);
}

.switch-label {
  font-size: 13px;
  color: #666;
}

/* 时间线 */
.timeline {
  position: relative;
  padding-left: 24px;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 7px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #e0e0e0;
}

.timeline-item {
  position: relative;
  margin-bottom: 18px;
}

.timeline-dot {
  position: absolute;
  left: -20px;
  top: 4px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #667eea;
}

.timeline-content {
  font-size: 14px;
}

.timeline-event {
  font-weight: 600;
  color: #333;
}

.timeline-summary {
  color: #555;
  margin-top: 2px;
}

.timeline-details {
  color: #888;
  font-size: 12px;
  font-family: monospace;
  background: #f5f5f5;
  padding: 4px 8px;
  border-radius: 4px;
  margin-top: 4px;
  white-space: pre-wrap;
  word-break: break-all;
}

.timeline-operator {
  color: #aaa;
  font-size: 12px;
  margin-top: 2px;
}

/* 其他 */
.loading {
  text-align: center;
  padding: 40px;
  color: #999;
}

.empty-tip {
  text-align: center;
  padding: 40px;
  color: #ccc;
}
</style>
