<!--
Caduceus 任务列表页面
筛选条 / 任务卡片 / 创建弹窗 改用 UiInput / UiSelect / UiButton / UiBadge / UiCard / UiEmptyState / UiModal。
业务逻辑（store / API / 合并分组）零改动。
-->
<template>
  <AppLayout>
    <div class="task-list-page">
      <!-- 页面头部 -->
      <header class="page-header">
        <div>
          <h1 class="page-header__title">任务列表</h1>
          <p class="page-header__subtitle">共 {{ tasks.length }} 个任务</p>
        </div>
        <UiButton variant="primary" size="md" @click="showCreateModal = true">
          + 创建任务
        </UiButton>
      </header>

      <!-- 筛选条 -->
      <UiCard class="filters">
        <div class="filters__row">
          <div class="filters__search">
            <UiInput
              v-model="searchQuery"
              placeholder="搜索任务标题..."
              @keydown.enter="applySearch"
            />
          </div>
          <UiSelect
            v-model="statusFilter"
            :options="statusOptions"
            @change="applySearch"
          />
          <label class="filters__check">
            <input type="checkbox" v-model="showMineOnly" @change="applySearch" />
            <span>只看与我相关</span>
          </label>
          <label v-if="hasMergeableGroups" class="filters__check">
            <input type="checkbox" v-model="mergeMode" @change="applySearch" />
            <span>合并展示</span>
          </label>
        </div>
      </UiCard>

      <!-- 加载中 -->
      <div v-if="loading" class="loading">加载中…</div>

      <!-- 正常列表视图 -->
      <div v-else-if="!mergeMode" class="task-grid">
        <UiCard
          v-for="task in tasks"
          :key="task.id"
          hoverable
          class="task-card"
          @click="goToDetail(task.id)"
        >
          <div class="task-card__head">
            <UiBadge :tone="statusToTone(task.status)">
              {{ statusMap[task.status] || task.status }}
            </UiBadge>
            <span class="task-card__date">{{ formatDate(task.created_at) }}</span>
          </div>
          <h3 class="task-card__title">{{ task.title }}</h3>
          <p class="task-card__desc">{{ task.description?.substring(0, 100) || '暂无描述' }}</p>
          <div class="task-card__foot">
            <span>发起人: {{ task.creator_name || task.creator || '未知' }}</span>
            <span v-if="task.assignments?.length">{{ task.assignments.length }} 个执行人</span>
          </div>
        </UiCard>

        <UiEmptyState
          v-if="tasks.length === 0"
          class="task-grid__empty"
          title="暂无任务"
          description="点击右上角创建第一个任务"
        />
      </div>

      <!-- 合并展示视图 -->
      <div v-else class="merge-view">
        <template v-if="groupedTasks.groups.length === 0 && groupedTasks.singles.length === 0">
          <UiEmptyState
            title="暂无任务"
            description="点击右上角创建第一个任务"
          />
        </template>
        <template v-else>
          <TaskMergeGroup
            v-for="group in groupedTasks.groups"
            :key="'group-' + group.pipelineId"
            :groupTitle="group.title"
            :tasks="group.tasks"
          />
          <div v-if="groupedTasks.singles.length > 0" class="task-grid">
            <UiCard
              v-for="task in groupedTasks.singles"
              :key="task.id"
              hoverable
              class="task-card"
              @click="goToDetail(task.id)"
            >
              <div class="task-card__head">
                <UiBadge :tone="statusToTone(task.status)">
                  {{ statusMap[task.status] || task.status }}
                </UiBadge>
                <span class="task-card__date">{{ formatDate(task.created_at) }}</span>
              </div>
              <h3 class="task-card__title">{{ task.title }}</h3>
              <p class="task-card__desc">{{ task.description?.substring(0, 100) || '暂无描述' }}</p>
              <div class="task-card__foot">
                <span>发起人: {{ task.creator_name || task.creator || '未知' }}</span>
                <span v-if="task.assignments?.length">{{ task.assignments.length }} 个执行人</span>
              </div>
            </UiCard>
          </div>
        </template>
      </div>

      <!-- 创建任务弹窗 -->
      <UiModal
        v-model="showCreateModal"
        title="创建任务"
        size="md"
      >
        <div class="form-stack">
          <UiInput
            v-model="newTask.title"
            label="任务标题 *"
            placeholder="输入任务标题"
            required
          />
          <div class="form-field">
            <label class="form-field__label">任务描述</label>
            <textarea
              v-model="newTask.description"
              class="form-field__textarea"
              placeholder="输入任务描述（可选）"
              rows="4"
            />
          </div>
          <UiSelect
            v-model="newTask.pipeline_id"
            label="管线模板（可选）"
            placeholder="无"
            :options="pipelineOptions"
          />
        </div>
        <template #footer>
          <UiButton variant="ghost" @click="showCreateModal = false">取消</UiButton>
          <UiButton
            variant="primary"
            :loading="creating"
            :disabled="!newTask.title.trim()"
            @click="handleCreate"
          >
            创建
          </UiButton>
        </template>
      </UiModal>
    </div>
  </AppLayout>
</template>

<script setup>
/**
 * Caduceus TaskList 页面脚本
 * 业务逻辑零改动：store 调用、API、合并分组、筛选过滤、创建流程保持原状。
 * 仅将 alert() 替换为 useToast()，保持用户感知一致。
 */
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import TaskMergeGroup from '@/components/TaskMergeGroup.vue'
import { useTasksStore } from '@/stores/tasks'
import { getPipelines } from '@/api/pipeline'
import { useToast } from '@/stores/toast'
import {
  UiButton, UiInput, UiSelect, UiCard, UiBadge, UiEmptyState, UiModal
} from '@/components/ui'

const router = useRouter()
const tasksStore = useTasksStore()
const toast = useToast()

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

// 状态 → Badge tone 映射
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

const statusOptions = [
  ['全部状态', ''],
  ['草稿',     'draft'],
  ['待处理',   'pending'],
  ['进行中',   'in_progress'],
  ['已完成',   'completed'],
  ['已取消',   'cancelled']
]

const pipelineOptions = computed(() =>
  pipelines.value.map((p) => [p.name, p.id])
)

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
    toast.error('加载任务失败')
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
    toast.success('任务创建成功')
    loadTasks()
  } catch (err) {
    console.error('创建任务失败:', err)
    toast.error('创建失败: ' + (err.response?.data?.detail || err.message))
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
  padding: var(--space-6);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--space-4);
}

.page-header__title {
  font-size: var(--text-2xl);
  font-weight: 600;
  color: var(--text-primary);
}

.page-header__subtitle {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin-top: var(--space-1);
}

/* 筛选条 */
.filters :deep(.ui-card__body) {
  padding: var(--space-3) var(--space-4);
}

.filters__row {
  display: flex;
  align-items: flex-end;
  gap: var(--space-3);
  flex-wrap: wrap;
}

.filters__search {
  flex: 1;
  min-width: 200px;
}

.filters__check {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  padding-bottom: var(--space-3);
  cursor: pointer;
}

.filters__check input {
  accent-color: var(--color-primary);
}

.loading {
  text-align: center;
  padding: var(--space-12);
  color: var(--text-muted);
  font-size: var(--text-sm);
}

/* 任务卡片 */
.task-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--space-4);
}

.task-card :deep(.ui-card__body) {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.task-card__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.task-card__date {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.task-card__title {
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.task-card__desc {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  line-height: var(--leading-normal);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin: 0;
}

.task-card__foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: var(--text-xs);
  color: var(--text-muted);
  margin-top: var(--space-2);
}

.task-grid__empty {
  grid-column: 1 / -1;
}

/* 创建任务表单 */
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

.form-field__textarea {
  padding: var(--space-3);
  border: 1px solid var(--color-input);
  border-radius: var(--radius-md);
  background-color: var(--color-card);
  font-size: var(--text-sm);
  color: var(--text-primary);
  resize: vertical;
  font-family: inherit;
  outline: none;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.form-field__textarea:focus {
  border-color: var(--color-ring);
  box-shadow: 0 0 0 3px rgba(13, 13, 13, 0.08);
}
</style>