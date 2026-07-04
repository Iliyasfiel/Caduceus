<!--
Caduceus 任务列表页面
展示所有任务，支持筛选、搜索、创建新任务
-->
<template>
  <AppLayout>
    <div class="task-list-page">
      <div class="page-header">
        <h1>任务列表</h1>
        <button class="btn-create" @click="showCreateModal = true">+ 创建任务</button>
      </div>

      <div class="filters-bar">
        <input
          v-model="searchQuery"
          type="text"
          class="search-input"
          placeholder="搜索任务标题..."
          @keydown.enter="applySearch"
        />
        <select v-model="statusFilter" class="filter-select" @change="applySearch">
          <option value="">全部状态</option>
          <option value="draft">草稿</option>
          <option value="pending">待处理</option>
          <option value="in_progress">进行中</option>
          <option value="completed">已完成</option>
          <option value="cancelled">已取消</option>
        </select>
        <label class="filter-checkbox">
          <input type="checkbox" v-model="showMineOnly" @change="applySearch" />
          只看与我相关
        </label>
        <label class="filter-checkbox" v-if="hasMergeableGroups">
          <input type="checkbox" v-model="mergeMode" @change="applySearch" />
          合并展示
        </label>
        <span class="task-count">共 {{ tasks.length }} 个任务</span>
      </div>

      <div v-if="loading" class="loading">加载中...</div>

      <!-- 正常列表视图 -->
      <div v-else-if="!mergeMode" class="task-grid">
        <div
          v-for="task in tasks"
          :key="task.id"
          class="task-card"
          @click="goToDetail(task.id)"
        >
          <div class="card-header">
            <span class="card-status" :class="'status-' + task.status">
              {{ statusMap[task.status] || task.status }}
            </span>
            <span class="card-date">{{ formatDate(task.created_at) }}</span>
          </div>
          <h3 class="card-title">{{ task.title }}</h3>
          <p class="card-desc">{{ task.description?.substring(0, 100) || '暂无描述' }}</p>
          <div class="card-footer">
            <span class="card-creator">发起人: {{ task.creator_name || task.creator || '未知' }}</span>
            <span class="card-assignees" v-if="task.assignments?.length">
              {{ task.assignments.length }} 个执行人
            </span>
          </div>
        </div>
        <div v-if="tasks.length === 0 && !loading" class="empty">暂无任务，点击右上角创建第一个任务</div>
      </div>

      <!-- 合并展示视图 -->
      <div v-else-if="!loading" class="merge-view">
        <div v-if="groupedTasks.groups.length === 0 && groupedTasks.singles.length === 0" class="empty">
          暂无任务，点击右上角创建第一个任务
        </div>
        <template v-else>
          <TaskMergeGroup
            v-for="group in groupedTasks.groups"
            :key="'group-' + group.pipelineId"
            :groupTitle="group.title"
            :tasks="group.tasks"
          />
          <div v-if="groupedTasks.singles.length > 0" class="task-grid">
            <div
              v-for="task in groupedTasks.singles"
              :key="task.id"
              class="task-card"
              @click="goToDetail(task.id)"
            >
              <div class="card-header">
                <span class="card-status" :class="'status-' + task.status">
                  {{ statusMap[task.status] || task.status }}
                </span>
                <span class="card-date">{{ formatDate(task.created_at) }}</span>
              </div>
              <h3 class="card-title">{{ task.title }}</h3>
              <p class="card-desc">{{ task.description?.substring(0, 100) || '暂无描述' }}</p>
              <div class="card-footer">
                <span class="card-creator">发起人: {{ task.creator_name || task.creator || '未知' }}</span>
                <span class="card-assignees" v-if="task.assignments?.length">
                  {{ task.assignments.length }} 个执行人
                </span>
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- 创建任务弹窗 -->
      <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
        <div class="modal">
          <div class="modal-header">
            <h2>创建任务</h2>
            <button class="modal-close" @click="showCreateModal = false">×</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>任务标题 *</label>
              <input v-model="newTask.title" type="text" class="form-input" placeholder="输入任务标题" />
            </div>
            <div class="form-group">
              <label>任务描述</label>
              <textarea v-model="newTask.description" class="form-textarea" placeholder="输入任务描述（可选）" rows="4"></textarea>
            </div>
            <div class="form-group">
              <label>管线模板（可选）</label>
              <select v-model="newTask.pipeline_id" class="form-input">
                <option :value="null">无</option>
                <option v-for="p in pipelines" :key="p.id" :value="p.id">{{ p.name }}</option>
              </select>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-cancel" @click="showCreateModal = false">取消</button>
            <button class="btn-submit" :disabled="creating || !newTask.title.trim()" @click="handleCreate">
              {{ creating ? '创建中...' : '创建' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import TaskMergeGroup from '@/components/TaskMergeGroup.vue'
import { useTasksStore } from '@/stores/tasks'
import { getPipelines } from '@/api/pipeline'

const router = useRouter()
const tasksStore = useTasksStore()

const tasks = ref([])
const loading = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')
const showMineOnly = ref(false)
const mergeMode = ref(false)
const showCreateModal = ref(false)
const creating = ref(false)
const pipelines = ref([])

const newTask = ref({
  title: '',
  description: '',
  pipeline_id: null
})

const statusMap = {
  draft: '草稿',
  pending: '待处理',
  in_progress: '进行中',
  completed: '已完成',
  cancelled: '已取消'
}

// 是否存在可合并的任务（任一任务有非空的 related_tasks）
const hasMergeableGroups = computed(() => {
  return tasks.value.some(t => t.related_tasks && t.related_tasks.length > 0)
})

// 将任务列表按管线分组，用于合并展示
const groupedTasks = computed(() => {
  const groups = []
  const groupedIds = new Set()

  tasks.value.forEach(task => {
    if (groupedIds.has(task.id)) return

    const hasRelated = task.related_tasks && task.related_tasks.length > 0
    const pipelineId = task.pipeline

    if (hasRelated && pipelineId) {
      // 找出同一管线下的所有关联任务（包含自身及其关联任务中同管线的）
      const pipelineTasks = tasks.value.filter(t => {
        if (groupedIds.has(t.id)) return false
        const tHasRelated = t.related_tasks && t.related_tasks.length > 0
        const tPipeline = t.pipeline
        if (!tHasRelated || tPipeline !== pipelineId) return false
        // 检查与当前 task 是否在同一关联网络中
        const taskRelatedSet = new Set(task.related_tasks)
        taskRelatedSet.add(task.id)
        const tRelatedSet = new Set(t.related_tasks)
        tRelatedSet.add(t.id)
        // 两者有关联交集或同一管线
        return [...taskRelatedSet].some(id => tRelatedSet.has(id))
      })

      if (pipelineTasks.length > 1) {
        pipelineTasks.forEach(t => groupedIds.add(t.id))
        const pipelineName = task.pipeline_name || '管线 #' + pipelineId
        groups.push({
          pipelineId: pipelineId,
          title: pipelineName + '（' + pipelineTasks.length + '个任务）',
          tasks: pipelineTasks
        })
      }
    }
  })

  // 未归入任何分组的单独任务
  const singles = tasks.value.filter(t => !groupedIds.has(t.id))

  return { groups, singles }
})

// 加载任务列表
async function loadTasks() {
  loading.value = true
  try {
    const params = {}
    if (searchQuery.value) params.search = searchQuery.value
    if (statusFilter.value) params.status = statusFilter.value
    if (showMineOnly.value) {
      // "只看与我相关" 使用 assignee 参数过滤
      const { useAuthStore } = await import('@/stores/auth')
      const authStore = useAuthStore()
      if (authStore.user?.id) params.assignee = authStore.user.id
    }
    await tasksStore.fetchTasks(params)
    tasks.value = tasksStore.tasks
  } catch (err) {
    console.error('加载任务列表失败:', err)
  }
  loading.value = false
}

// 应用搜索筛选
function applySearch() {
  loadTasks()
}

// 跳转到任务详情
function goToDetail(id) {
  router.push({ name: 'TaskDetail', params: { id } })
}

// 创建任务
async function handleCreate() {
  if (!newTask.value.title.trim()) return
  creating.value = true
  try {
    const data = {
      title: newTask.value.title.trim(),
      description: newTask.value.description.trim(),
    }
    if (newTask.value.pipeline_id) {
      data.pipeline = newTask.value.pipeline_id
    }
    await tasksStore.createNewTask(data)
    showCreateModal.value = false
    newTask.value = { title: '', description: '', pipeline_id: null }
    loadTasks()
  } catch (err) {
    console.error('创建任务失败:', err)
    alert('创建失败: ' + (err.response?.data?.detail || err.message))
  }
  creating.value = false
}

// 格式化日期
function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  return `${month}-${day} ${hours}:${minutes}`
}

// 加载管线列表
async function loadPipelines() {
  try {
    const res = await getPipelines()
    pipelines.value = Array.isArray(res.data) ? res.data : (res.data?.results || [])
  } catch (err) {
    // 管线 API 可能尚未就绪，静默忽略
  }
}

onMounted(() => {
  loadTasks()
  loadPipelines()
})
</script>

<style scoped>
.task-list-page {
  padding: 24px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.page-header h1 {
  margin: 0;
  font-size: 22px;
  color: #1f2937;
}

.btn-create {
  padding: 8px 20px;
  background: #667eea;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-create:hover {
  background: #5a6fd6;
}

.filters-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.search-input {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 13px;
  width: 200px;
  outline: none;
}

.search-input:focus {
  border-color: #667eea;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 13px;
  background: #fff;
  outline: none;
}

.filter-checkbox {
  font-size: 13px;
  color: #374151;
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
}

.task-count {
  font-size: 12px;
  color: #9ca3af;
  margin-left: auto;
}

.loading {
  text-align: center;
  padding: 48px;
  color: #9ca3af;
}

.task-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.task-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: box-shadow 0.15s, transform 0.15s;
}

.task-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-1px);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.card-status {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 500;
}

.status-draft { background: #f3f4f6; color: #6b7280; }
.status-pending { background: #fef3c7; color: #92400e; }
.status-in_progress { background: #dbeafe; color: #1e40af; }
.status-completed { background: #d1fae5; color: #065f46; }
.status-cancelled { background: #fee2e2; color: #991b1b; }

.card-date {
  font-size: 11px;
  color: #9ca3af;
}

.card-title {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #1f2937;
}

.card-desc {
  margin: 0 0 12px 0;
  font-size: 13px;
  color: #6b7280;
  line-height: 1.5;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  color: #9ca3af;
}

.empty {
  text-align: center;
  padding: 48px;
  color: #9ca3af;
  grid-column: 1 / -1;
}

/* 弹窗 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal {
  background: #fff;
  border-radius: 12px;
  width: 480px;
  max-width: 90vw;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  margin: 0;
  font-size: 16px;
}

.modal-close {
  background: none;
  border: none;
  font-size: 22px;
  color: #9ca3af;
  cursor: pointer;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 6px;
}

.form-input, .form-textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  outline: none;
  box-sizing: border-box;
}

.form-input:focus, .form-textarea:focus {
  border-color: #667eea;
}

.form-textarea {
  resize: vertical;
  font-family: inherit;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 12px 20px;
  border-top: 1px solid #e5e7eb;
}

.btn-cancel {
  padding: 8px 20px;
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
}

.btn-submit {
  padding: 8px 20px;
  background: #667eea;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
