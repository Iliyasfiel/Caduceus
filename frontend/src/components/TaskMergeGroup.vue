<!--
Caduceus 任务合并组组件
可折叠的任务合并展示组，将同一管线下的关联任务聚合显示
支持展开/折叠，子任务卡片点击跳转 TaskDetail
-->
<template>
  <div class="merge-group">
    <div class="group-header" @click="toggleExpand">
      <span class="group-arrow">{{ expanded ? '▼' : '▶' }}</span>
      <span class="group-title">{{ groupTitle }}</span>
      <span class="group-badge">{{ tasks.length }} 个任务</span>
    </div>
    <div v-if="expanded" class="group-body">
      <div
        v-for="task in tasks"
        :key="task.id"
        class="sub-task-card"
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
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * TaskMergeGroup - 可折叠的任务合并组组件
 * Props:
 *   groupTitle      - 合并组标题（如"测试管线（3个任务）"）
 *   tasks           - 子任务列表
 *   defaultExpanded - 默认是否展开
 */
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  groupTitle: { type: String, required: true },
  tasks: { type: Array, required: true },
  defaultExpanded: { type: Boolean, default: false }
})

const router = useRouter()

// 展开/折叠状态
const expanded = ref(props.defaultExpanded)

const statusMap = {
  draft: '草稿',
  pending: '待处理',
  in_progress: '进行中',
  completed: '已完成',
  cancelled: '已取消'
}

// 切换展开/折叠
function toggleExpand() {
  expanded.value = !expanded.value
}

// 跳转到任务详情
function goToDetail(id) {
  router.push({ name: 'TaskDetail', params: { id } })
}

// 格式化日期为 MM-DD HH:mm
function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  return `${month}-${day} ${hours}:${minutes}`
}
</script>

<style scoped>
.merge-group {
  margin-bottom: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.group-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #f9fafb;
  cursor: pointer;
  user-select: none;
  border-bottom: 1px solid #e5e7eb;
  transition: background 0.15s;
}

.group-header:hover {
  background: #f3f4f6;
}

.group-arrow {
  font-size: 12px;
  color: #6b7280;
  width: 16px;
  text-align: center;
}

.group-title {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
  flex: 1;
}

.group-badge {
  font-size: 11px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 10px;
  background: #ede9fe;
  color: #7c3aed;
}

.group-body {
  padding: 8px 12px 8px 28px;
  background: #fff;
}

.sub-task-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: box-shadow 0.15s, transform 0.15s;
}

.sub-task-card:last-child {
  margin-bottom: 4px;
}

.sub-task-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transform: translateY(-1px);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
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
  margin: 0 0 6px 0;
  font-size: 14px;
  color: #1f2937;
}

.card-desc {
  margin: 0 0 10px 0;
  font-size: 12px;
  color: #6b7280;
  line-height: 1.4;
}

.card-footer {
  font-size: 12px;
  color: #9ca3af;
}
</style>
