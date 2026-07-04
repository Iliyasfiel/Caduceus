<!--
Caduceus 任务详情页面
展示任务完整信息：基本信息、管线阶段进度、角色感知字段排序、评论、日志、执行人
-->
<template>
  <AppLayout>
    <div class="task-detail-page" v-if="task">
      <!-- 顶部工具栏 -->
      <div class="toolbar">
        <button class="btn-back" @click="$router.push('/tasks')">← 返回列表</button>
        <button class="btn-share" @click="handleShare">分享</button>
        <div class="toolbar-center" v-if="task.pipeline_name">
          <span class="pipeline-badge">📋 {{ task.pipeline_name }}</span>
        </div>
        <div class="toolbar-right">
          <select v-model="task.status" class="status-select" :class="'status-' + task.status" @change="handleStatusChange">
            <option value="draft">草稿</option>
            <option value="pending">待处理</option>
            <option value="in_progress">进行中</option>
            <option value="completed">已完成</option>
            <option value="cancelled">已取消</option>
          </select>
          <button class="btn-save" :disabled="saving" @click="handleSave">
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>

      <div class="detail-body">
        <!-- 左侧主内容 -->
        <div class="main-content">
          <!-- 管线阶段进度 -->
          <section class="section" v-if="pipelineNodes.length > 0">
            <h2 class="section-title">阶段进度</h2>
            <div class="pipeline-timeline">
              <div
                v-for="(node, idx) in pipelineNodes"
                :key="node.id"
                class="timeline-step"
                :class="{ active: currentStageIndex >= idx, last: idx === pipelineNodes.length - 1 }"
              >
                <div class="step-dot" :class="{ active: currentStageIndex >= idx }"></div>
                <div class="step-label">{{ node.label }}</div>
                <div v-if="idx < pipelineNodes.length - 1" class="step-line" :class="{ active: currentStageIndex > idx }"></div>
              </div>
            </div>
          </section>

          <!-- 基本信息 -->
          <section class="section">
            <h2 class="section-title">基本信息</h2>
            <div class="info-grid">
              <div class="info-item">
                <label>标题</label>
                <input v-model="task.title" type="text" class="info-input" />
              </div>
              <div class="info-item">
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
          </section>

          <!-- 自定义字段（按用户角色优先级排序） -->
          <section class="section" v-if="sortedFields.length > 0">
            <h2 class="section-title">任务字段</h2>
            <div class="info-grid">
              <div class="info-item" v-for="f in sortedFields" :key="f.key">
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
          </section>

          <!-- 评论区域 -->
          <section class="section">
            <h2 class="section-title">评论 ({{ comments.length }})</h2>
            <div class="comment-list">
              <div v-if="comments.length === 0" class="empty-comments">暂无评论</div>
              <div v-for="c in comments" :key="c.id" class="comment-item">
                <div class="comment-header">
                  <strong>{{ c.author_name || '用户' }}</strong>
                  <span class="comment-time">{{ formatDate(c.created_at) }}</span>
                </div>
                <p class="comment-content">{{ c.content }}</p>
              </div>
            </div>
            <div class="comment-form">
              <textarea v-model="newComment" class="comment-input" placeholder="输入评论..." rows="2"></textarea>
              <button class="btn-comment" :disabled="!newComment.trim() || commenting" @click="handleAddComment">
                {{ commenting ? '发送中...' : '发送' }}
              </button>
            </div>
          </section>

          <!-- 变更日志 -->
          <section class="section">
            <h2 class="section-title">变更日志 ({{ logs.length }})</h2>
            <div class="log-list">
              <div v-if="logs.length === 0" class="empty-logs">暂无变更记录</div>
              <div v-for="l in logs" :key="l.id" class="log-item">
                <div class="log-header">
                  <strong>{{ l.operator_name || '系统' }}</strong>
                  <span class="log-badge">{{ l.action }}</span>
                  <span class="log-time">{{ formatDate(l.created_at) }}</span>
                </div>
                <p class="log-changes" v-if="l.changes && Object.keys(l.changes).length">
                  {{ formatChanges(l.changes) }}
                </p>
              </div>
            </div>
          </section>
        </div>

        <!-- 右侧面板：执行人 + 管线节点摘要 -->
        <aside class="side-panel">
          <section class="side-section">
            <h3>执行人</h3>
            <div v-if="assignments.length === 0" class="empty-assign">暂无执行人</div>
            <div v-for="a in assignments" :key="a.id" class="assign-item">
              <div class="assign-info">
                <strong>{{ a.user_name || '用户 #' + a.user }}</strong>
                <span class="assign-role">{{ a.role_name || '无角色' }}</span>
              </div>
              <span class="assign-status" :class="a.status">
                {{ a.status_display || a.status }}
              </span>
            </div>
          </section>

          <section class="side-section" v-if="pipelineNodes.length > 0">
            <h3>阶段节点</h3>
            <div v-for="(node, idx) in pipelineNodes" :key="node.id" class="node-summary" :class="{ active: currentStageIndex >= idx }">
              <div class="node-summary-header">
                <span class="node-dot" :class="{ active: currentStageIndex >= idx }"></span>
                <strong>{{ node.label }}</strong>
              </div>
              <div class="node-summary-roles" v-if="node.roles && node.roles.length > 0">
                角色: {{ node.roles.map(r => r.role_id).join(', ') }}
              </div>
            </div>
          </section>

          <!-- 关联资源 -->
          <section class="side-section">
            <div class="side-section-header">
              <h3>关联资源</h3>
              <button class="btn-add-resource" @click="showResourceSelector = true">+ 关联资源</button>
            </div>
            <div v-if="linkedResources.length === 0" class="empty-assign">暂无关联资源</div>
            <div v-for="r in linkedResources" :key="r.id" class="assign-item">
              <div class="assign-info">
                <strong>{{ r.name || r.resource_type_name }}</strong>
                <span class="assign-role">{{ r.resource_type_name || '资源' }}</span>
              </div>
              <span class="assign-status" :class="r.status || 'available'">
                {{ statusMap[r.status] || r.status || '可用' }}
              </span>
            </div>
          </section>
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
      <div v-if="showShareModal" class="modal-overlay" @click.self="showShareModal = false">
        <div class="modal share-modal">
          <div class="modal-header">
            <h2>分享任务</h2>
            <button class="modal-close" @click="showShareModal = false">&times;</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>分享链接</label>
              <div class="share-link-row">
                <input :value="shareUrl" readonly class="info-input" />
                <button class="btn-copy" @click="copyShareUrl">复制</button>
              </div>
            </div>
            <div class="form-group">
              <label>过期时间（可选）</label>
              <input type="date" v-model="shareExpiresAt" class="form-input" />
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-cancel-share" @click="handleCancelShare">取消分享</button>
            <button class="btn-submit" @click="handleSetExpiry">设置过期</button>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="loading" class="loading-page">加载中...</div>
    <div v-else class="loading-page">任务不存在或已删除</div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import ResourceSelector from '@/components/ResourceSelector.vue'
import { useTasksStore } from '@/stores/tasks'
import { useAuthStore } from '@/stores/auth'
import { getTaskAssignments } from '@/api/tasks'

const route = useRoute()
const tasksStore = useTasksStore()
const authStore = useAuthStore()

const task = ref(null)
const loading = ref(true)
const saving = ref(false)
const assignments = ref([])
const comments = ref([])
const logs = ref([])
const newComment = ref('')
const commenting = ref(false)
const pipelineNodes = ref([])
const currentStageIndex = ref(0)
const showResourceSelector = ref(false)
const linkedResources = ref([])
const showShareModal = ref(false)
const shareExpiresAt = ref('')

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
    if (pipelineNodes.value.length > 0) {
      // 默认当前阶段为第一个节点
      const instanceNode = task.value.current_node
      if (instanceNode) {
        const idx = pipelineNodes.value.findIndex(n => n.id === instanceNode)
        currentStageIndex.value = idx >= 0 ? idx : 0
      }
    }

    comments.value = task.value.recent_comments || []
    // 加载已关联资源
    if (task.value.resources && task.value.resources.length > 0) {
      loadLinkedResources(task.value.resources)
    }
    loadAssignments(id)
    loadLogs(id)
  } catch (err) {
    console.error('加载任务失败:', err)
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
    alert('保存成功')
  } catch (err) {
    console.error('保存失败:', err)
    alert('保存失败: ' + (err.response?.data?.detail || err.message))
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
      alert('生成分享链接失败')
      return
    }
  }
  showShareModal.value = true
}

// 复制分享链接
function copyShareUrl() {
  if (shareUrl.value) {
    navigator.clipboard.writeText(shareUrl.value)
    alert('已复制')
  }
}

// 设置分享过期时间
async function handleSetExpiry() {
  try {
    const { updateTaskShare } = await import('@/api/tasks')
    await updateTaskShare(task.value.id, {
      share_expires_at: shareExpiresAt.value || null
    })
    alert('过期时间已更新')
    showShareModal.value = false
    shareExpiresAt.value = ''
  } catch (err) {
    alert('设置过期时间失败')
  }
}

// 取消分享
async function handleCancelShare() {
  if (!confirm('确定取消分享？取消后分享链接将失效。')) return
  try {
    const { cancelTaskShare } = await import('@/api/tasks')
    await cancelTaskShare(task.value.id)
    task.value.share_token = null
    showShareModal.value = false
    shareExpiresAt.value = ''
    alert('已取消分享')
  } catch (err) {
    alert('取消分享失败')
  }
}

async function handleStatusChange() {
  await handleSave()
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
    alert('评论失败')
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

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 20px;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
}

.toolbar-center { flex: 1; text-align: center; }
.pipeline-badge { font-size: 13px; color: #7c3aed; }

.toolbar-right { display: flex; align-items: center; gap: 12px; }
.btn-back { padding: 6px 14px; background: #f3f4f6; border: 1px solid #d1d5db; border-radius: 6px; font-size: 13px; cursor: pointer; color: #374151; }
.btn-share { padding: 6px 14px; background: #fff; border: 1px solid #667eea; border-radius: 6px; font-size: 13px; cursor: pointer; color: #667eea; margin-left: 8px; }
.btn-share:hover { background: #ede9fe; }
.status-select { padding: 6px 12px; border-radius: 6px; font-size: 13px; border: 1px solid #d1d5db; outline: none; font-weight: 500; }
.status-draft { background: #f3f4f6; color: #6b7280; }
.status-pending { background: #fef3c7; color: #92400e; }
.status-in_progress { background: #dbeafe; color: #1e40af; }
.status-completed { background: #d1fae5; color: #065f46; }
.status-cancelled { background: #fee2e2; color: #991b1b; }
.btn-save { padding: 6px 20px; background: #667eea; color: #fff; border: none; border-radius: 6px; font-size: 13px; cursor: pointer; }
.btn-save:disabled { opacity: 0.6; cursor: not-allowed; }

.detail-body { display: flex; flex: 1; overflow: hidden; }
.main-content { flex: 1; overflow-y: auto; padding: 20px; }

.section { background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; margin-bottom: 16px; }
.section-title { margin: 0 0 12px 0; font-size: 15px; color: #1f2937; }

/* 管线阶段时间轴 */
.pipeline-timeline {
  display: flex;
  align-items: flex-start;
  overflow-x: auto;
  padding: 8px 0 16px;
}
.timeline-step { display: flex; flex-direction: column; align-items: center; position: relative; min-width: 80px; flex: 1; }
.step-dot { width: 20px; height: 20px; border-radius: 50%; background: #e5e7eb; border: 3px solid #d1d5db; z-index: 1; transition: all 0.3s; }
.step-dot.active { background: #667eea; border-color: #667eea; }
.step-label { font-size: 12px; color: #6b7280; text-align: center; margin-top: 6px; max-width: 80px; word-break: break-all; }
.timeline-step.active .step-label { color: #667eea; font-weight: 500; }
.step-line { position: absolute; top: 10px; left: 50%; width: 100%; height: 3px; background: #e5e7eb; z-index: 0; }
.step-line.active { background: #667eea; }

/* 基本信息 */
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.info-item { display: flex; flex-direction: column; gap: 4px; }
.info-item label { font-size: 12px; color: #9ca3af; font-weight: 500; }
.field-badge { display: inline-block; font-size: 10px; background: #ede9fe; color: #7c3aed; padding: 1px 6px; border-radius: 4px; margin-left: 4px; }
.info-input, .info-textarea { padding: 8px 12px; border: 1px solid #e5e7eb; border-radius: 6px; font-size: 14px; outline: none; font-family: inherit; }
.info-input:focus, .info-textarea:focus { border-color: #667eea; }
.info-textarea { resize: vertical; }
.info-value { font-size: 14px; color: #374151; }
.switch-label { display: flex; align-items: center; gap: 8px; font-size: 13px; color: #374151; }
.switch-input { accent-color: #667eea; }

/* 评论 */
.comment-list { max-height: 300px; overflow-y: auto; }
.comment-item { padding: 10px 0; border-bottom: 1px solid #f3f4f6; }
.comment-header { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
.comment-header strong { font-size: 13px; color: #1f2937; }
.comment-time { font-size: 11px; color: #9ca3af; }
.comment-content { margin: 0; font-size: 13px; color: #374151; line-height: 1.5; }
.comment-form { display: flex; gap: 8px; margin-top: 12px; }
.comment-input { flex: 1; padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 13px; outline: none; resize: none; font-family: inherit; }
.comment-input:focus { border-color: #667eea; }
.btn-comment { padding: 8px 16px; background: #667eea; color: #fff; border: none; border-radius: 6px; font-size: 13px; cursor: pointer; align-self: flex-end; }
.btn-comment:disabled { opacity: 0.6; cursor: not-allowed; }
.empty-comments, .empty-logs { text-align: center; padding: 16px; color: #9ca3af; font-size: 13px; }

/* 日志 */
.log-list { max-height: 300px; overflow-y: auto; }
.log-item { padding: 8px 0; border-bottom: 1px solid #f3f4f6; }
.log-header { display: flex; align-items: center; gap: 8px; font-size: 12px; }
.log-badge { padding: 1px 6px; background: #f3f4f6; border-radius: 4px; color: #6b7280; font-size: 11px; }
.log-time { color: #9ca3af; margin-left: auto; }
.log-changes { margin: 4px 0 0 0; font-size: 12px; color: #6b7280; }

/* 右侧面板 */
.side-panel { width: 260px; min-width: 260px; border-left: 1px solid #e5e7eb; background: #fafbfc; padding: 16px; overflow-y: auto; }
.side-section { margin-bottom: 24px; }
.side-section h3 { margin: 0 0 12px 0; font-size: 14px; color: #1f2937; }
.side-section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.side-section-header h3 { margin: 0; font-size: 14px; color: #1f2937; }
.btn-add-resource { padding: 2px 10px; background: #667eea; color: #fff; border: none; border-radius: 4px; font-size: 12px; cursor: pointer; }
.btn-add-resource:hover { background: #5a6fd6; }
.assign-item, .node-summary { display: flex; align-items: center; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #e5e7eb; }
.node-summary { flex-direction: column; align-items: flex-start; gap: 4px; }
.node-summary-header { display: flex; align-items: center; gap: 8px; }
.node-dot { width: 10px; height: 10px; border-radius: 50%; background: #e5e7eb; display: inline-block; }
.node-dot.active { background: #667eea; }
.node-summary-roles { font-size: 11px; color: #9ca3af; padding-left: 18px; }
.assign-info { display: flex; flex-direction: column; gap: 2px; }
.assign-info strong { font-size: 13px; color: #1f2937; }
.assign-role { font-size: 11px; color: #9ca3af; }
.assign-status { font-size: 11px; padding: 2px 8px; border-radius: 10px; }
.assign-status.pending { background: #fef3c7; color: #92400e; }
.assign-status.accepted { background: #dbeafe; color: #1e40af; }
.assign-status.completed { background: #d1fae5; color: #065f46; }
.empty-assign { text-align: center; padding: 16px; color: #9ca3af; font-size: 13px; }
.loading-page { text-align: center; padding: 48px; color: #9ca3af; }

/* 分享弹窗 */
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.4);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000;
}
.share-modal {
  background: #fff;
  border-radius: 12px;
  width: 480px;
  max-width: 90vw;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}
.modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 20px; border-bottom: 1px solid #e5e7eb;
}
.modal-header h2 { margin: 0; font-size: 16px; color: #1f2937; }
.modal-close { background: none; border: none; font-size: 20px; cursor: pointer; color: #9ca3af; padding: 0; line-height: 1; }
.modal-close:hover { color: #374151; }
.modal-body { padding: 20px; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 12px; color: #6b7280; margin-bottom: 6px; font-weight: 500; }
.share-link-row { display: flex; gap: 8px; }
.share-link-row .info-input { flex: 1; }
.btn-copy { padding: 8px 16px; background: #667eea; color: #fff; border: none; border-radius: 6px; font-size: 13px; cursor: pointer; white-space: nowrap; }
.btn-copy:hover { background: #5a6fd6; }
.form-input { width: 100%; padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 14px; outline: none; box-sizing: border-box; }
.form-input:focus { border-color: #667eea; }
.modal-footer { display: flex; justify-content: flex-end; gap: 8px; padding: 12px 20px; border-top: 1px solid #e5e7eb; }
.btn-cancel-share { padding: 8px 16px; background: #fee2e2; color: #991b1b; border: none; border-radius: 6px; font-size: 13px; cursor: pointer; }
.btn-cancel-share:hover { background: #fecaca; }
.btn-submit { padding: 8px 16px; background: #667eea; color: #fff; border: none; border-radius: 6px; font-size: 13px; cursor: pointer; }
.btn-submit:hover { background: #5a6fd6; }
</style>
