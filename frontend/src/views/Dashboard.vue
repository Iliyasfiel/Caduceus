<!--
Caduceus 仪表盘页面
展示统计卡片、任务概览和最近任务列表
-->
<template>
  <AppLayout>
    <div class="dashboard">
      <h1>仪表盘</h1>

      <!-- 统计卡片网格 -->
      <div class="stats-grid">
        <div class="stat-card" style="--card-color: #667eea">
          <h3>本月任务总数</h3>
          <p class="stat-value" v-if="!loading">{{ stats.total_tasks }}</p>
          <p class="stat-value placeholder" v-else>加载中...</p>
        </div>
        <div class="stat-card" style="--card-color: #10b981">
          <h3>已完成</h3>
          <p class="stat-value" v-if="!loading">{{ stats.completed_tasks }}</p>
          <p class="stat-value placeholder" v-else>加载中...</p>
        </div>
        <div class="stat-card" style="--card-color: #f59e0b">
          <h3>完成率</h3>
          <p class="stat-value" v-if="!loading">{{ stats.completion_rate }}%</p>
          <p class="stat-value placeholder" v-else>加载中...</p>
        </div>
        <div class="stat-card" style="--card-color: #3b82f6">
          <h3>进行中</h3>
          <p class="stat-value" v-if="!loading">{{ stats.in_progress_tasks }}</p>
          <p class="stat-value placeholder" v-else>加载中...</p>
        </div>
      </div>

      <!-- 最近任务区域 -->
      <div class="recent-section">
        <h2>最近任务</h2>
        <div v-if="loading" class="loading-text">加载中...</div>
        <div v-else-if="stats.recent_tasks.length === 0" class="empty-text">
          暂无任务
        </div>
        <div v-else class="recent-list">
          <div
            v-for="task in stats.recent_tasks"
            :key="task.id"
            class="recent-task-card"
            @click="goToTask(task.id)"
          >
            <div class="task-info">
              <span class="task-title">{{ task.title }}</span>
              <span class="task-meta">{{ task.creator_name }} · {{ formatTime(task.created_at) }}</span>
            </div>
            <span class="task-status-tag" :class="'status-' + task.status">
              {{ task.status_display }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
/**
 * Caduceus Dashboard 页面脚本
 * 加载仪表盘聚合统计数据并展示
 */
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import { getDashboardStats } from '@/api/dashboard'

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

// 页面挂载时加载统计数据
onMounted(async () => {
  try {
    const res = await getDashboardStats()
    Object.assign(stats, res.data)
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
  padding: 24px;
}

h1 {
  margin-bottom: 24px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.stat-card {
  background: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stat-card h3 {
  margin-bottom: 8px;
  color: #666;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: var(--card-color, #667eea);
}

.stat-value.placeholder {
  font-size: 20px;
  color: #999;
  font-weight: normal;
}

/* 最近任务区域 */
.recent-section {
  margin-top: 32px;
}

.recent-section h2 {
  margin-bottom: 16px;
  font-size: 20px;
  color: #333;
}

.loading-text,
.empty-text {
  color: #999;
  font-size: 14px;
  padding: 16px 0;
}

.recent-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recent-task-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: white;
  padding: 16px 20px;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  cursor: pointer;
  transition: box-shadow 0.2s;
}

.recent-task-card:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
}

.task-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.task-title {
  font-size: 15px;
  font-weight: 600;
  color: #333;
}

.task-meta {
  font-size: 12px;
  color: #999;
}

.task-status-tag {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.status-draft {
  background: #f3f4f6;
  color: #6b7280;
}

.status-pending {
  background: #fef3c7;
  color: #92400e;
}

.status-in_progress {
  background: #dbeafe;
  color: #1e40af;
}

.status-completed {
  background: #d1fae5;
  color: #065f46;
}

.status-cancelled {
  background: #fee2e2;
  color: #991b1b;
}
</style>
