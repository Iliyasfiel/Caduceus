<!--
Caduceus 任务详情页面
工具栏 / 信息区 / 时间线 / 评论 / 日志 / 右侧面板 / 分享弹窗 全部 polish。
业务逻辑（store / API / 字段排序 / 阶段流转 / 资源选择 / 分享）零改动。
-->
<template>
  <AppLayout>
    <div class="task-detail-page" v-if="task">
      <!-- 顶部工具栏 -->
      <header class="toolbar">
        <div class="toolbar__left">
          <UiButton variant="secondary" size="sm" @click="$router.push('/tasks')">
            ← 返回列表
          </UiButton>
          <UiButton variant="ghost" size="sm" @click="handleShare">分享</UiButton>
        </div>
        <div class="toolbar__center" v-if="task.pipeline_name">
          <UiBadge tone="info">
            <UiIcon name="clipboard" :size="12" class="badge-icon" />
            {{ task.pipeline_name }}
          </UiBadge>
        </div>
        <div class="toolbar__right">
          <div :class="['status-select', 'status-' + task.status]">
            <UiSelect
              v-model="task.status"
              :options="statusOptions"
              size="sm"
              @change="handleStatusChange"
            />
          </div>
          <UiButton
            variant="primary"
            size="sm"
            :loading="saving"
            @click="handleSave"
          >
            保存
          </UiButton>
        </div>
      </header>

      <div class="detail-body">
        <!-- 左侧主内容 -->
        <div class="main-content">
          <!-- 管线阶段进度 -->
          <UiCard v-if="pipelineNodes.length > 0" class="section">
            <template #header>
              <h2 class="section-title">阶段进度</h2>
            </template>
            <div class="pipeline-timeline">
              <div
                v-for="(node, idx) in pipelineNodes"
                :key="node.id"
                class="timeline-step"
                :class="{ last: idx === pipelineNodes.length - 1 }"
              >
                <div
                  class="step-dot"
                  :class="{
                    completed: currentStageIndex > idx,
                    current: currentStageIndex === idx
                  }"
                ></div>
                <div class="step-label" :class="{ current: currentStageIndex === idx }">{{ node.label }}</div>
                <div v-if="currentStageIndex > idx" class="step-label-done">已完成</div>
                <div
                  v-if="idx < pipelineNodes.length - 1"
                  class="step-line"
                  :class="{ completed: currentStageIndex > idx, active: currentStageIndex === idx }"
                ></div>
                <div
                  v-if="currentStageIndex === idx && idx < pipelineNodes.length - 1"
                  class="step-next-btn"
                  @click="handleMarkStageComplete(idx)"
                >
                  <span class="next-arrow">▶</span>
                </div>
                <div
                  v-if="currentStageIndex === idx && idx === pipelineNodes.length - 1"
                  class="step-complete-btn"
                  @click="handleCompleteTask"
                >
                  <UiIcon name="check" :size="14" class="step-complete-btn__icon" />
                  <span>完成任务</span>
                </div>
              </div>
            </div>
          </UiCard>

          <!-- 基本信息 -->
          <UiCard class="section">
            <template #header>
              <h2 class="section-title">基本信息</h2>
            </template>
            <div class="info-grid">
              <div class="info-item info-item--full">
                <label>标题</label>
                <input v-model="task.title" type="text" class="info-input" />
              </div>
              <div class="info-item info-item--full">
                <label>描述</label>
                <textarea v-model="task.description" class="info-textarea" rows="4" placeholder="暂无描述"></textarea>
              </div>
              <div class="info-item">
                <label>创建者</label>
                <span class="info-value">{{ task.creator_name || task.creator || '未知' }}</span>
              </div>
              <div class="info-item" v-if="task.pipeline">
                <label>绑定管线</label>
                <span class="info-value">{{ task.pipeline_name || '管线 #' + task.pipeline }}</span>
              </div>
              <div class="info-item">
                <label>创建时间</label>
                <span class="info-value">{{ formatDate(task.created_at) }}</span>
              </div>
              <div class="info-item">
                <label>更新时间</label>
                <span class="info-value">{{ formatDate(task.updated_at) }}</span>
              </div>
            </div>
          </UiCard>

          <!-- 自定义字段（按用户角色优先级排序） -->
          <UiCard v-if="sortedFields.length > 0" class="section">
            <template #header>
              <h2 class="section-title">任务字段</h2>
            </template>
            <div class="info-grid">
              <div
                v-for="f in sortedFields"
                :key="f.key"
                class="info-item"
                :class="{ 'info-item--full': f.type === 'textarea' }"
              >
                <label>
                  {{ f.label }}
                  <span v-if="f.is_public" class="field-badge">公开</span>
                </label>
                <input v-if="f.type === 'text'" v-model="f.value" type="text" class="info-input" :placeholder="'输入' + f.label" />
                <textarea v-else-if="f.type === 'textarea'" v-model="f.value" class="info-textarea" rows="2" :placeholder="'输入' + f.label"></textarea>
                <input v-else-if="f.type === 'number'" v-model.number="f.value" type="number" class="info-input" :placeholder="'输入' + f.label" />
                <select v-else-if="f.type === 'select'" v-model="f.value" class="info-input">
                  <option value="">请选择</option>
                </select>
                <input v-else-if="f.type === 'date'" v-model="f.value" type="date" class="info-input" />
                <label v-else-if="f.type === 'boolean'" class="switch-label">
                  <input type="checkbox" v-model="f.value" class="switch-input" />
                  <span>{{ f.value ? '是' : '否' }}</span>
                </label>
                <input v-else v-model="f.value" type="text" class="info-input" :placeholder="'输入' + f.label" />
              </div>
            </div>
          </UiCard>

          <!-- 评论区域 -->
          <UiCard class="section">
            <template #header>
              <h2 class="section-title">评论 ({{ comments.length }})</h2>
            </template>
            <div class="comment-list">
              <UiEmptyState v-if="comments.length === 0" title="暂无评论" />
              <div v-for="c in comments" :key="c.id" class="comment-item">
                <div class="comment-header">
                  <strong>{{ c.author_name || '用户' }}</strong>
                  <span class="comment-time">{{ formatDate(c.created_at) }}</span>
                </div>
                <p class="comment-content">{{ c.content }}</p>
              </div>
            </div>
            <div class="comment-form">
              <textarea
                v-model="newComment"
                class="comment-input"
                placeholder="输入评论..."
                rows="2"
              />
              <UiButton
                variant="primary"
                size="sm"
                :disabled="!newComment.trim()"
                :loading="commenting"
                @click="handleAddComment"
              >
                发送
              </UiButton>
            </div>
          </UiCard>

          <!-- 变更日志 -->
          <UiCard class="section">
            <template #header>
              <h2 class="section-title">变更日志 ({{ logs.length }})</h2>
            </template>
            <div class="log-list">
              <UiEmptyState v-if="logs.length === 0" title="暂无变更记录" />
              <div v-for="l in logs" :key="l.id" class="log-item">
                <div class="log-header">
                  <strong>{{ l.operator_name || '系统' }}</strong>
                  <span class="log-badge">{{ l.action }}</span>
                  <span class="log-time">{{ formatDate(l.created_at) }}</span>
                </div>
                <p v-if="l.changes && Object.keys(l.changes).length" class="log-changes">
                  {{ formatChanges(l.changes) }}
                </p>
              </div>
            </div>
          </UiCard>
        </div>

        <!-- 右侧面板：执行人 + 管线节点摘要 -->
        <aside class="side-panel">
          <UiCard class="side-section">
            <template #header>
              <h3 class="side-section__title">执行人</h3>
            </template>
            <UiEmptyState v-if="assignments.length === 0" title="暂无执行人" />
            <div v-for="a in assignments" :key="a.id" class="assign-item">
              <div class="assign-info">
                <strong>{{ a.user_name || '用户 #' + a.user }}</strong>
                <span class="assign-role">{{ a.role_name || '无角色' }}</span>
              </div>
              <UiBadge :tone="assignmentTone(a.status)">
                {{ a.status_display || a.status }}
              </UiBadge>
            </div>
          </UiCard>

          <UiCard v-if="pipelineNodes.length > 0" class="side-section">
            <template #header>
              <h3 class="side-section__title">阶段节点</h3>
            </template>
            <div
              v-for="(node, idx) in pipelineNodes"
              :key="node.id"
              class="node-summary"
              :class="{ completed: currentStageIndex > idx, current: currentStageIndex === idx }"
            >
              <div class="node-summary-header">
                <span
                  class="node-dot"
                  :class="{ completed: currentStageIndex > idx, current: currentStageIndex === idx }"
                ></span>
                <strong>{{ node.label }}</strong>
              </div>
              <div v-if="node.roles && node.roles.length > 0" class="node-summary-roles">
                角色: {{ node.roles.map(r => r.role_id).join(', ') }}
              </div>
            </div>
          </UiCard>

          <!-- 关联资源 -->
          <UiCard class="side-section">
            <template #header>
              <div class="side-section__head-row">
                <h3 class="side-section__title">关联资源</h3>
                <UiButton variant="ghost" size="sm" @click="showResourceSelector = true">
                  + 关联资源
                </UiButton>
              </div>
            </template>
            <UiEmptyState v-if="linkedResources.length === 0" title="暂无关联资源" />
            <div v-for="r in linkedResources" :key="r.id" class="assign-item">
              <div class="assign-info">
                <strong>{{ r.name || r.resource_type_name }}</strong>
                <span class="assign-role">{{ r.resource_type_name || '资源' }}</span>
              </div>
              <UiBadge :tone="resourceTone(r.status)">
                {{ statusMap[r.status] || r.status || '可用' }}
              </UiBadge>
            </div>
          </UiCard>
        </aside>
      </div>

      <!-- ResourceSelector 弹窗 -->
      <ResourceSelector
        v-model="linkedResources"
        :visible="showResourceSelector"
        @update:visible="showResourceSelector = $event"
        @confirm="handleResourceConfirm"
      />

      <!-- 分享弹窗 -->
      <UiModal v-model="showShareModal" title="分享任务" size="md">
        <div class="form-stack">
          <div class="form-field">
            <label class="form-field__label">分享链接</label>
            <div class="share-link-row">
              <input :value="shareUrl" readonly class="info-input" />
              <UiButton variant="secondary" size="sm" @click="copyShareUrl">复制</UiButton>
            </div>
          </div>
          <div class="form-field">
            <label class="form-field__label">过期时间（可选）</label>
            <input type="date" v-model="shareExpiresAt" class="info-input" />
          </div>
        </div>
        <template #footer>
          <UiButton variant="danger" size="sm" @click="handleCancelShare">取消分享</UiButton>
          <UiButton variant="primary" size="sm" @click="handleSetExpiry">设置过期</UiButton>
        </template>
      </UiModal>
    </div>

    <UiEmptyState v-else-if="loading" title="加载中…" class="loading-page" />
    <UiEmptyState v-else title="任务不存在或已删除" class="loading-page" />
  </AppLayout>
</template>

<script setup>
/**
 * Caduceus TaskDetail 页面脚本
 * 业务逻辑零改动：store / API / 字段排序 / 阶段流转 / 资源 / 分享 全部保留。
 * 仅 alert() 替换为 useToast()，confirm() 替换为原生 confirm（保持业务行为一致）。
 */
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import ResourceSelector from '@/components/ResourceSelector.vue'
import { useTasksStore } from '@/stores/tasks'
import { useAuthStore } from '@/stores/auth'
import { getTaskAssignments } from '@/api/tasks'
import { useToast } from '@/stores/toast'
import { useConfirm } from '@/stores/confirm'
import {
  UiButton, UiCard, UiBadge, UiEmptyState, UiModal, UiIcon, UiSelect
} from '@/components/ui'

// 状态选项（UiSelect 用）：与后端 choices 保持一致
const statusOptions = [
  { label: '草稿', value: 'draft' },
  { label: '待处理', value: 'pending' },
  { label: '进行中', value: 'in_progress' },
  { label: '已完成', value: 'completed' },
  { label: '已取消', value: 'cancelled' }
]

const route = useRoute()
const tasksStore = useTasksStore()
const authStore = useAuthStore()
const toast = useToast()

const task = ref(null)
const loading = ref(true)
const saving = ref(false)
const assignments = ref([])
const comments = ref([])
const logs = ref([])
const newComment = ref('')
const commenting = ref(false)
const pipelineNodes = ref([])
const showResourceSelector = ref(false)
const linkedResources = ref([])
const showShareModal = ref(false)
const shareExpiresAt = ref('')

const currentStageIndex = computed(() => {
  if (!task.value?.current_node || !pipelineNodes.value.length) return 0
  if (task.value.current_node === 'completed') return pipelineNodes.value.length
  const idx = pipelineNodes.value.findIndex(n => n.id === task.value.current_node)
  return idx >= 0 ? idx : 0
})

const shareUrl = computed(() => {
  return task.value?.share_token ? `http://localhost:3000/share/${task.value.share_token}` : ''
})

const statusMap = {
  available: '可用',
  reserved: '已预约',
  in_use: '使用中',
  maintenance: '维护中',
  unavailable: '不可用'
}

// 状态色映射（与 TaskList / Dashboard 保持一致）
function statusToTone(status) {
  switch (status) {
    case 'draft':       return 'neutral'
    case 'pending':     return 'warning'
    case 'in_progress': return 'info'
    case 'completed':   return 'success'
    case 'cancelled':   return 'danger'
    default:            return 'neutral'
  }
}

function assignmentTone(status) {
  switch (status) {
    case 'pending':   return 'warning'
    case 'accepted':  return 'info'
    case 'completed': return 'success'
    default:          return 'neutral'
  }
}

function resourceTone(status) {
  switch (status) {
    case 'available':   return 'success'
    case 'reserved':    return 'warning'
    case 'in_use':      return 'info'
    case 'maintenance': return 'warning'
    case 'unavailable': return 'danger'
    default:            return 'neutral'
  }
}

// 按当前用户角色优先级排序的字段列表
const sortedFields = computed(() => {
  if (!task.value?.fields || !Array.isArray(task.value.fields)) return []
  const fields = [...task.value.fields]
  const currentRoleIds = (authStore.user?.role_assignments || []).map(a => a.role)

  fields.sort((a, b) => {
    const aPriority = (a.priority_roles || []).some(r => currentRoleIds.includes(r))
    const bPriority = (b.priority_roles || []).some(r => currentRoleIds.includes(r))
    if (aPriority && !bPriority) return -1
    if (!aPriority && bPriority) return 1
    return 0
  })

  return fields
})

// 加载任务详情
async function loadTask() {
  loading.value = true
  try {
    const id = route.params.id
    await tasksStore.fetchTask(id)
    task.value = { ...tasksStore.currentTask }

    // 管线信息
    pipelineNodes.value = task.value.pipeline_nodes || []

    comments.value = task.value.recent_comments || []
    // 加载已关联资源
    if (task.value.resources && task.value.resources.length > 0) {
      loadLinkedResources(task.value.resources)
    }
    loadAssignments(id)
    loadLogs(id)
  } catch (err) {
    console.error('加载任务失败:', err)
    toast.error('加载任务失败')
  }
  loading.value = false
}

async function loadAssignments(taskId) {
  try {
    const res = await getTaskAssignments(taskId)
    assignments.value = Array.isArray(res.data) ? res.data : (res.data?.results || [])
  } catch (err) {
    console.error('加载分配信息失败:', err)
  }
}

// 加载已关联资源详情
async function loadLinkedResources(resourceIds) {
  try {
    // resourceIds 可能是 ID 数组或对象数组
    const ids = Array.isArray(resourceIds) ? resourceIds.map(r => typeof r === 'object' ? r.id : r) : []
    if (ids.length === 0) return
    const { getResourceItems } = await import('@/api/resources')
    const res = await getResourceItems({ ids: ids.join(',') })
    linkedResources.value = Array.isArray(res.data) ? res.data : (res.data?.results || [])
    // 如果 API 不支持 ids 参数，则逐个加载
    if (linkedResources.value.length === 0) {
      const items = []
      for (const id of ids) {
        try {
          const r = await getResourceItems({ id })
          const data = Array.isArray(r.data) ? r.data : (r.data?.results || [])
          items.push(...data)
        } catch (e) { /* skip */ }
      }
      linkedResources.value = items
    }
  } catch (err) {
    console.error('加载关联资源失败:', err)
  }
}

async function loadLogs(taskId) {
  try {
    const { getTaskLogs } = await import('@/api/tasks')
    const res = await getTaskLogs(taskId)
    logs.value = Array.isArray(res.data) ? res.data : (res.data?.results || [])
  } catch (err) {
    // 静默忽略
  }
}

async function handleSave() {
  saving.value = true
  try {
    await tasksStore.updateExistingTask(task.value.id, {
      title: task.value.title,
      description: task.value.description,
      status: task.value.status,
      fields: task.value.fields,
      resources: linkedResources.value.map(r => r.id)
    })
    toast.success('保存成功')
  } catch (err) {
    console.error('保存失败:', err)
    toast.error('保存失败: ' + (err.response?.data?.detail || err.message))
  }
  saving.value = false
}

// 资源选择确认回调
async function handleResourceConfirm(resourceIds) {
  showResourceSelector.value = false
  // 将关联的资源 ID 合并到任务数据中
  task.value.resources = resourceIds
  await handleSave()
}

// 打开分享弹窗（如果没有 share_token 则自动触发后端生成）
async function handleShare() {
  if (!task.value.share_token) {
    try {
      const { updateTaskShare } = await import('@/api/tasks')
      const res = await updateTaskShare(task.value.id, {})
      task.value.share_token = res.data.share_token
    } catch (err) {
      toast.error('生成分享链接失败')
      return
    }
  }
  showShareModal.value = true
}

// 复制分享链接
function copyShareUrl() {
  if (shareUrl.value) {
    navigator.clipboard.writeText(shareUrl.value)
    toast.success('已复制分享链接')
  }
}

// 设置分享过期时间
async function handleSetExpiry() {
  try {
    const { updateTaskShare } = await import('@/api/tasks')
    await updateTaskShare(task.value.id, {
      share_expires_at: shareExpiresAt.value || null
    })
    toast.success('过期时间已更新')
    showShareModal.value = false
    shareExpiresAt.value = ''
  } catch (err) {
    toast.error('设置过期时间失败')
  }
}

// 取消分享
async function handleCancelShare() {
  const ok = await confirm({
    title: '取消分享',
    message: '取消后分享链接将失效，无法通过该链接访问任务。',
    tone: 'danger',
    confirmText: '取消分享'
  })
  if (!ok) return
  try {
    const { cancelTaskShare } = await import('@/api/tasks')
    await cancelTaskShare(task.value.id)
    task.value.share_token = null
    showShareModal.value = false
    shareExpiresAt.value = ''
    toast.success('已取消分享')
  } catch (err) {
    toast.error('取消分享失败')
  }
}

async function handleStatusChange() {
  await handleSave()
}

async function handleMarkStageComplete(idx) {
  if (idx >= pipelineNodes.value.length - 1) return
  const nextNode = pipelineNodes.value[idx + 1]
  try {
    await tasksStore.updateExistingTask(task.value.id, { current_node: nextNode.id })
    task.value.current_node = nextNode.id
  } catch (err) {
    console.error('标记阶段失败:', err)
    toast.error('标记失败: ' + (err.response?.data?.detail || err.message))
  }
}

async function handleCompleteTask() {
  try {
    await tasksStore.updateExistingTask(task.value.id, { current_node: 'completed', status: 'completed' })
    task.value.current_node = 'completed'
    task.value.status = 'completed'
  } catch (err) {
    console.error('完成任务失败:', err)
    toast.error('操作失败: ' + (err.response?.data?.detail || err.message))
  }
}

async function handleAddComment() {
  if (!newComment.value.trim()) return
  commenting.value = true
  try {
    await tasksStore.addComment(task.value.id, newComment.value.trim())
    await tasksStore.fetchTask(task.value.id)
    task.value = { ...tasksStore.currentTask }
    comments.value = task.value.recent_comments || []
    newComment.value = ''
  } catch (err) {
    console.error('评论失败:', err)
    toast.error('评论失败')
  }
  commenting.value = false
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  return `${month}-${day} ${hours}:${minutes}`
}

function formatChanges(changes) {
  if (!changes || typeof changes !== 'object') return ''
  return Object.entries(changes)
    .map(([k, v]) => `${k}: ${typeof v === 'object' ? JSON.stringify(v) : v}`)
    .join('; ')
}

onMounted(() => {
  loadTask()
})
</script>

<style scoped>
.task-detail-page {
  padding: 0;
  margin: -24px;
  height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 顶部工具栏 */
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3) var(--space-6);
  background-color: var(--bg-surface);
  border-bottom: 1px solid var(--border-subtle);
  flex-shrink: 0;
}

.toolbar__left {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.toolbar__center {
  flex: 1;
  text-align: center;
}

.toolbar__right {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.status-select {
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  border: 1px solid var(--color-input);
  background-color: var(--bg-surface);
  color: var(--text-primary);
  font-weight: 500;
  outline: none;
  cursor: pointer;
}

.status-select:focus {
  border-color: var(--color-ring);
}

.detail-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-5);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

/* Section 卡片：让 UiCard 默认 body padding 收紧一些，更紧凑 */
.section :deep(.ui-card__body) {
  padding: var(--space-4) var(--space-5);
}

.section-title {
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

/* 管线阶段时间轴 */
.pipeline-timeline {
  display: flex;
  align-items: flex-start;
  overflow-x: auto;
  padding: var(--space-2) 0 var(--space-4);
}

.timeline-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  min-width: 80px;
  flex: 1;
}

.step-dot {
  width: 20px;
  height: 20px;
  border-radius: var(--radius-full);
  background: var(--color-muted);
  border: 3px solid var(--color-border);
  z-index: 1;
  transition: all var(--transition-normal);
}

.step-dot.completed {
  background: var(--color-success);
  border-color: var(--color-success);
}

.step-dot.current {
  background: var(--color-primary);
  border-color: var(--color-primary);
  box-shadow: 0 0 0 6px rgba(18, 18, 18, 0.12);
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.25); }
}

.step-label {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  text-align: center;
  margin-top: var(--space-2);
  max-width: 80px;
  word-break: break-all;
}

.step-label.current {
  color: var(--color-primary);
  font-weight: 600;
}

.step-label-done {
  font-size: 10px;
  color: var(--color-success);
  margin-top: 2px;
}

.step-line {
  position: absolute;
  top: 10px;
  left: 50%;
  width: 100%;
  height: 3px;
  background: var(--color-border);
  z-index: 0;
}

.step-line.completed { background: var(--color-success); }
.step-line.active { background: var(--color-primary); }

.step-next-btn {
  position: absolute;
  top: -2px;
  right: -8px;
  width: 22px;
  height: 22px;
  border-radius: var(--radius-full);
  background: var(--color-primary);
  color: var(--color-primary-foreground);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 2;
  font-size: 11px;
  transition: transform var(--transition-fast);
}

.step-next-btn:hover { transform: scale(1.2); }

.step-complete-btn {
  position: absolute;
  top: -8px;
  right: -30px;
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: 2px 10px;
  border-radius: var(--radius-full);
  background: var(--color-success);
  color: var(--color-primary-foreground);
  cursor: pointer;
  font-size: 11px;
  white-space: nowrap;
}

.step-complete-btn__icon {
  color: inherit;
}

/* 基本信息 */
.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-3);
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.info-item--full {
  grid-column: 1 / -1;
}

.info-item label {
  font-size: var(--text-xs);
  color: var(--text-muted);
  font-weight: 500;
}

.field-badge {
  display: inline-block;
  font-size: 10px;
  background-color: var(--color-muted);
  color: var(--text-secondary);
  padding: 1px 6px;
  border-radius: var(--radius-sm);
  margin-left: var(--space-2);
}

.info-input,
.info-textarea {
  padding: var(--space-3);
  border: 1px solid var(--color-input);
  border-radius: var(--radius-md);
  background-color: var(--color-card);
  font-size: var(--text-sm);
  color: var(--text-primary);
  outline: none;
  font-family: inherit;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.info-input:focus,
.info-textarea:focus {
  border-color: var(--color-ring);
  box-shadow: 0 0 0 3px rgba(13, 13, 13, 0.08);
}

.info-textarea { resize: vertical; }

.info-value {
  font-size: var(--text-sm);
  color: var(--text-primary);
}

.switch-label {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-sm);
  color: var(--text-primary);
}

.switch-input { accent-color: var(--color-primary); }

/* 评论 */
.comment-list {
  max-height: 300px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.comment-item {
  padding: var(--space-3) 0;
  border-bottom: 1px solid var(--border-subtle);
}

.comment-item:last-child {
  border-bottom: 0;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-1);
}

.comment-header strong {
  font-size: var(--text-sm);
  color: var(--text-primary);
}

.comment-time {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.comment-content {
  margin: 0;
  font-size: var(--text-sm);
  color: var(--text-primary);
  line-height: var(--leading-normal);
}

.comment-form {
  display: flex;
  gap: var(--space-2);
  margin-top: var(--space-3);
}

.comment-input {
  flex: 1;
  padding: var(--space-3);
  border: 1px solid var(--color-input);
  border-radius: var(--radius-md);
  background-color: var(--color-card);
  font-size: var(--text-sm);
  color: var(--text-primary);
  outline: none;
  resize: none;
  font-family: inherit;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.comment-input:focus {
  border-color: var(--color-ring);
  box-shadow: 0 0 0 3px rgba(13, 13, 13, 0.08);
}

/* 日志 */
.log-list {
  max-height: 300px;
  overflow-y: auto;
}

.log-item {
  padding: var(--space-2) 0;
  border-bottom: 1px solid var(--border-subtle);
}

.log-item:last-child {
  border-bottom: 0;
}

.log-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-xs);
}

.log-badge {
  padding: 2px 6px;
  background-color: var(--color-muted);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: 11px;
}

.log-time {
  color: var(--text-muted);
  margin-left: auto;
}

.log-changes {
  margin: var(--space-1) 0 0 0;
  font-size: var(--text-xs);
  color: var(--text-secondary);
}

/* 右侧面板 */
.side-panel {
  width: 280px;
  min-width: 280px;
  border-left: 1px solid var(--border-subtle);
  background-color: var(--bg-canvas);
  padding: var(--space-4);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.side-section :deep(.ui-card__body) {
  padding: var(--space-3) var(--space-4);
}

.side-section__title {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.side-section__head-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
  width: 100%;
}

.assign-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-2) 0;
  border-bottom: 1px solid var(--border-subtle);
  gap: var(--space-2);
}

.assign-item:last-child {
  border-bottom: 0;
}

.node-summary {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: var(--space-1);
  padding: var(--space-2) var(--space-2);
  border-left: 3px solid transparent;
}

.node-summary.completed {
  border-left-color: var(--color-success);
}

.node-summary.current {
  border-left-color: var(--color-primary);
}

.node-summary-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.node-dot {
  width: 10px;
  height: 10px;
  border-radius: var(--radius-full);
  background: var(--color-muted);
  display: inline-block;
}

.node-dot.completed { background: var(--color-success); }
.node-dot.current { background: var(--color-primary); }

.node-summary-roles {
  font-size: var(--text-xs);
  color: var(--text-muted);
  padding-left: 18px;
}

.assign-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.assign-info strong {
  font-size: var(--text-sm);
  color: var(--text-primary);
}

.assign-role {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.loading-page {
  margin-top: var(--space-12);
}

/* 分享弹窗表单 */
.form-stack {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.form-field__label {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--text-primary);
}

.share-link-row {
  display: flex;
  gap: var(--space-2);
}

.share-link-row .info-input {
  flex: 1;
}
</style>