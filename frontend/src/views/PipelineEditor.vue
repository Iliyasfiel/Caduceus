<!--
Caduceus 管线编辑器页面
提供管线的可视化创建、编辑和保存功能
包裹 PipelineCanvas 画布组件，左侧展示管线列表，顶部工具栏提供保存/返回等操作
-->
<template>
  <AppLayout>
    <div class="pipeline-editor-page">
      <!-- 顶部工具栏：管线名称输入、保存按钮、返回按钮 -->
      <div class="toolbar">
        <div class="toolbar-left">
          <button class="btn-back" @click="goBack">
            ← 返回列表
          </button>
          <input
            ref="nameInputRef"
            v-model="pipelineName"
            type="text"
            class="name-input"
            placeholder="输入管线名称..."
          />
        </div>
        <div class="toolbar-right">
          <span v-if="currentPipelineId" class="pipeline-id">ID: {{ currentPipelineId }}</span>
          <button
            class="btn-save"
            :disabled="saving || !pipelineName.trim()"
            @click="savePipeline"
          >
            <span v-if="saving" class="btn-spinner"></span>
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>

      <div class="editor-body">
        <!-- 左侧管线列表（可折叠） -->
        <aside class="pipeline-list-panel" :class="{ collapsed: listCollapsed }">
          <div class="list-header">
            <h3>管线列表</h3>
            <button class="btn-collapse" @click="listCollapsed = !listCollapsed">
              {{ listCollapsed ? '▶' : '◀' }}
            </button>
          </div>
          <div v-if="!listCollapsed" class="list-body">
            <button class="btn-new" @click="createNewPipeline">
              + 新建管线
            </button>
            <div v-if="loadingList" class="list-loading">加载中...</div>
            <div v-else-if="pipelines.length === 0" class="list-empty">暂无管线</div>
            <div
              v-for="p in pipelines"
              :key="p.id"
              class="list-item"
              :class="{ active: currentPipelineId === p.id }"
              @click="loadPipelineById(p.id)"
            >
              <span class="list-item-name">{{ p.name }}</span>
              <span class="list-item-time">{{ formatDate(p.updated_at) }}</span>
            </div>
          </div>
        </aside>

        <!-- 主体画布区域 -->
        <div class="canvas-wrapper">
          <PipelineCanvas
            v-model="pipelineData"
            :availableRoles="availableRoles"
            :availableResourceTypes="availableResourceTypes"
          />
        </div>
      </div>

      <!-- 操作提示 Toast 消息 -->
      <Transition name="fade">
        <div v-if="showToast" class="toast" :class="toastType">
          {{ toastMessage }}
        </div>
      </Transition>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import PipelineCanvas from '@/components/PipelineCanvas.vue'
import { getPipelines, getPipeline, createPipeline, updatePipeline } from '@/api/pipeline'
import { getResourceTypes } from '@/api/resources'

const router = useRouter()

// ===================== 状态 =====================

// 当前编辑的管线 ID（新建时为 null）
const currentPipelineId = ref(null)

// 管线名称
const pipelineName = ref('')

// 名称输入框引用
const nameInputRef = ref(null)

// 画布 v-model 数据 { nodes: [], edges: [] }
const pipelineData = ref({
  nodes: [],
  edges: []
})

// 管线列表
const pipelines = ref([])

// 列表加载状态
const loadingList = ref(false)

// 保存按钮 loading 状态
const saving = ref(false)

// 左侧列表折叠状态
const listCollapsed = ref(false)

// ===================== 外部数据 =====================

// 可用角色列表（暂无可用的 accounts API，使用空数组占位）
const availableRoles = ref([])

// 可用资源类型列表
const availableResourceTypes = ref([])

// ===================== Toast 提示 =====================

const showToast = ref(false)
const toastMessage = ref('')
const toastType = ref('success') // 'success' | 'error'
let toastTimer = null

// 显示 Toast 提示
function showToastMessage(message, type = 'success') {
  toastMessage.value = message
  toastType.value = type
  showToast.value = true
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => {
    showToast.value = false
  }, 3000)
}

// ===================== 管线列表加载 =====================

// 从 API 获取管线列表
async function loadPipelineList() {
  loadingList.value = true
  try {
    const res = await getPipelines()
    // 兼容分页响应和直接数组响应
    pipelines.value = Array.isArray(res.data) ? res.data : (res.data.results || [])
  } catch (err) {
    console.error('加载管线列表失败:', err)
    showToastMessage('加载管线列表失败', 'error')
  } finally {
    loadingList.value = false
  }
}

// ===================== 管线操作 =====================

// 创建新管线：清空画布数据，焦点移到名称输入框
async function createNewPipeline() {
  // 如果有未保存的更改，这里可以加确认提示（后续迭代）
  currentPipelineId.value = null
  pipelineName.value = ''
  pipelineData.value = { nodes: [], edges: [] }
  await nextTick()
  nameInputRef.value?.focus()
}

// 点击列表项加载已有管线到编辑器
async function loadPipelineById(id) {
  loadingList.value = true
  try {
    const res = await getPipeline(id)
    const pipeline = res.data

    currentPipelineId.value = pipeline.id
    pipelineName.value = pipeline.name || ''

    // 反序列化 nodes 和 edges 数据到画布
    pipelineData.value = {
      nodes: pipeline.nodes || [],
      edges: pipeline.edges || []
    }
  } catch (err) {
    console.error('加载管线详情失败:', err)
    showToastMessage('加载管线详情失败', 'error')
  } finally {
    loadingList.value = false
  }
}

// 保存管线：新建时 POST 创建，编辑已有管线时 PATCH 更新
async function savePipeline() {
  if (!pipelineName.value.trim()) {
    showToastMessage('请输入管线名称', 'error')
    return
  }

  saving.value = true
  try {
    // 构造请求体
    const payload = {
      name: pipelineName.value.trim(),
      nodes: pipelineData.value.nodes,
      edges: pipelineData.value.edges
    }

    if (currentPipelineId.value) {
      // 编辑已有管线：PATCH 更新
      const res = await updatePipeline(currentPipelineId.value, payload)
      showToastMessage('管线更新成功')
    } else {
      // 新建管线：POST 创建
      const res = await createPipeline(payload)
      // 保存成功后记录新管线 ID
      currentPipelineId.value = res.data.id
      showToastMessage('管线创建成功')
    }

    // 刷新管线列表
    await loadPipelineList()
  } catch (err) {
    console.error('保存管线失败:', err)
    const detail = err.response?.data?.detail || err.message || '保存失败'
    showToastMessage(detail, 'error')
  } finally {
    saving.value = false
  }
}

// ===================== 导航 =====================

// 返回到仪表盘页面
function goBack() {
  router.push('/')
}

// ===================== 工具函数 =====================

// 格式化日期显示
function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  return `${month}-${day} ${hours}:${minutes}`
}

// ===================== 生命周期 =====================

onMounted(async () => {
  // 页面挂载时加载管线列表和资源类型
  await loadPipelineList()

  // 加载可用资源类型列表
  try {
    const res = await getResourceTypes()
    availableResourceTypes.value = Array.isArray(res.data)
      ? res.data
      : (res.data.results || [])
  } catch (err) {
    console.error('加载资源类型失败:', err)
  }
})
</script>

<style scoped>
.pipeline-editor-page {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 60px);
  margin: -24px;
  overflow: hidden;
}

/* ==================== 顶部工具栏 ==================== */

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
  min-height: 48px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-back {
  padding: 6px 14px;
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 13px;
  color: #374151;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.15s;
}

.btn-back:hover {
  background: #e5e7eb;
}

.name-input {
  flex: 1;
  max-width: 400px;
  padding: 6px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 15px;
  color: #1f2937;
  outline: none;
  transition: border-color 0.15s;
}

.name-input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.15);
}

.name-input::placeholder {
  color: #9ca3af;
}

.pipeline-id {
  font-size: 12px;
  color: #9ca3af;
  font-family: monospace;
}

/* 保存按钮 */
.btn-save {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 20px;
  background: #667eea;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.15s;
}

.btn-save:hover:not(:disabled) {
  background: #5a6fd6;
}

.btn-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* ==================== 编辑器主体 ==================== */

.editor-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* ==================== 左侧管线列表 ==================== */

.pipeline-list-panel {
  width: 240px;
  min-width: 240px;
  background: #fafbfc;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  transition: width 0.25s, min-width 0.25s;
}

.pipeline-list-panel.collapsed {
  width: 44px;
  min-width: 44px;
}

.list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
}

.list-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
  white-space: nowrap;
  overflow: hidden;
}

.pipeline-list-panel.collapsed .list-header h3 {
  display: none;
}

.btn-collapse {
  background: none;
  border: none;
  font-size: 12px;
  color: #6b7280;
  cursor: pointer;
  padding: 4px;
  flex-shrink: 0;
  transition: color 0.15s;
}

.btn-collapse:hover {
  color: #374151;
}

.list-body {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  padding: 8px;
}

/* 新建管线按钮 */
.btn-new {
  padding: 8px 14px;
  background: #667eea;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  width: 100%;
  margin-bottom: 8px;
  transition: background 0.15s;
}

.btn-new:hover {
  background: #5a6fd6;
}

/* 列表加载 / 空状态 */
.list-loading,
.list-empty {
  text-align: center;
  padding: 24px 12px;
  font-size: 13px;
  color: #9ca3af;
}

/* 列表项 */
.list-item {
  display: flex;
  flex-direction: column;
  padding: 10px 12px;
  margin-bottom: 4px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s;
  background: #fff;
  border: 1px solid #e5e7eb;
}

.list-item:hover {
  background: #f3f4f6;
}

.list-item.active {
  background: #ede9fe;
  border-color: #a78bfa;
}

.list-item-name {
  font-size: 13px;
  font-weight: 500;
  color: #374151;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.list-item-time {
  font-size: 11px;
  color: #9ca3af;
  margin-top: 2px;
}

/* ==================== 画布容器 ==================== */

.canvas-wrapper {
  flex: 1;
  overflow: hidden;
  position: relative;
}

/* 覆盖 PipelineCanvas 内部的 100vh 高度，使其适配父容器 */
.canvas-wrapper :deep(.pipeline-canvas) {
  height: 100%;
}

/* ==================== Toast 消息 ==================== */

.toast {
  position: fixed;
  top: 76px;
  right: 24px;
  z-index: 200;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  color: #fff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  pointer-events: none;
}

.toast.success {
  background: #10b981;
}

.toast.error {
  background: #ef4444;
}

/* Toast 淡入淡出过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
