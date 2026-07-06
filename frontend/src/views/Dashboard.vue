<!--
Caduceus 仪表盘页面
统计卡片 / 最近任务列表改用 UiCard + UiBadge。
业务逻辑（数据加载 / 跳转）保持不变。
-->
<template>
  <AppLayout>
    <div class="dashboard">
      <header class="dashboard__header">
        <h1 class="dashboard__title">仪表盘</h1>
        <p class="dashboard__subtitle">本月任务概览与最近动态</p>
      </header>

      <!-- 统计卡片网格 -->
      <div class="dashboard__stats">
        <UiCard v-for="card in statCards" :key="card.key" class="stat-card">
          <div class="stat-card__head">
            <span class="stat-card__label">{{ card.label }}</span>
            <span class="stat-card__dot" :style="{ background: card.color }" aria-hidden="true" />
          </div>
          <p v-if="!loading" class="stat-card__value">{{ card.value }}</p>
          <p v-else class="stat-card__value stat-card__value--placeholder">加载中…</p>
        </UiCard>
      </div>

      <!-- 最近任务区域 -->
      <section class="dashboard__section">
        <h2 class="dashboard__section-title">最近任务</h2>
        <UiCard class="dashboard__list-card">
          <UiEmptyState
            v-if="!loading && stats.recent_tasks.length === 0"
            title="暂无任务"
            description="还没有创建任何任务，去新建一个吧。"
          />
          <div v-else-if="!loading" class="recent-list">
            <div
              v-for="task in stats.recent_tasks"
              :key="task.id"
              class="recent-task"
              @click="goToTask(task.id)"
            >
              <div class="recent-task__info">
                <span class="recent-task__title">{{ task.title }}</span>
                <span class="recent-task__meta">
                  {{ task.creator_name }} · {{ formatTime(task.created_at) }}
                </span>
              </div>
              <UiBadge :tone="statusToTone(task.status)">
                {{ task.status_display }}
              </UiBadge>
            </div>
          </div>
          <div v-else class="recent-list__loading">加载中…</div>
        </UiCard>
      </section>
    </div>
  </AppLayout>
</template>

<script setup>
/**
 * Caduceus Dashboard 页面脚本
 * 业务逻辑零改动：数据加载、跳转、状态映射保持原状。
 */
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import { getDashboardStats } from '@/api/dashboard'
import { UiCard, UiBadge, UiEmptyState } from '@/components/ui'

const router = useRouter()

const loading = ref(true)

const stats = reactive({
  total_tasks: 0,
  completed_tasks: 0,
  in_progress_tasks: 0,
  completion_rate: 0,
  resource_usage_count: 0,
  recent_tasks: []
})

// 统计卡片数据（视图层配置，业务字段不变）
const statCards = ref([])

function refreshStatCards() {
  statCards.value = [
    { key: 'total',    label: '本月任务总数', value: stats.total_tasks,         color: 'var(--color-chart-3)' },
    { key: 'done',     label: '已完成',       value: stats.completed_tasks,     color: 'var(--color-success)' },
    { key: 'rate',     label: '完成率',       value: stats.completion_rate + '%', color: 'var(--color-chart-2)' },
    { key: 'progress', label: '进行中',       value: stats.in_progress_tasks,   color: 'var(--color-chart-4)' }
  ]
}

// 状态 → Badge tone 映射（与原 status-* CSS 类保持一致语义）
function statusToTone(status) {
  switch (status) {
    case 'draft':        return 'neutral'
    case 'pending':      return 'warning'
    case 'in_progress':  return 'info'
    case 'completed':    return 'success'
    case 'cancelled':    return 'danger'
    default:             return 'neutral'
  }
}

// 页面挂载时加载统计数据
onMounted(async () => {
  try {
    const res = await getDashboardStats()
    Object.assign(stats, res.data)
    refreshStatCards()
  } catch (e) {
    console.error('加载仪表盘数据失败:', e)
  } finally {
    loading.value = false
  }
})

// 格式化时间显示
function formatTime(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${month}-${day} ${hours}:${minutes}`
}

// 跳转到任务详情页
function goToTask(id) {
  router.push({ name: 'TaskDetail', params: { id } })
}
</script>

<style scoped>
.dashboard {
  padding: var(--space-6);
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.dashboard__header {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.dashboard__title {
  font-size: var(--text-2xl);
  font-weight: 600;
}

.dashboard__subtitle {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

/* 统计区 */
.dashboard__stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-4);
}

.stat-card__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-3);
}

.stat-card__label {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.stat-card__dot {
  width: 8px;
  height: 8px;
  border-radius: var(--radius-full);
}

.stat-card__value {
  font-size: var(--text-3xl);
  font-weight: 600;
  line-height: var(--leading-tight);
  color: var(--text-primary);
}

.stat-card__value--placeholder {
  font-size: var(--text-base);
  color: var(--text-muted);
  font-weight: 400;
}

/* 最近任务区 */
.dashboard__section {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.dashboard__section-title {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--text-primary);
}

.dashboard__list-card :deep(.ui-card__body) {
  padding: 0;
}

.recent-list {
  display: flex;
  flex-direction: column;
}

.recent-task {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  padding: var(--space-4) var(--space-6);
  cursor: pointer;
  transition: background-color var(--transition-fast);
}

.recent-task + .recent-task {
  border-top: 1px solid var(--border-subtle);
}

.recent-task:hover {
  background-color: var(--color-muted);
}

.recent-task__info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.recent-task__title {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--text-primary);
}

.recent-task__meta {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.recent-list__loading {
  padding: var(--space-6);
  font-size: var(--text-sm);
  color: var(--text-muted);
  text-align: center;
}
</style>