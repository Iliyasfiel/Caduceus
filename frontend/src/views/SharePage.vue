<!--
Caduceus 公开分享页面
通过分享令牌访问任务信息，无需登录
样式 polish：全部 token 化；状态用 UiBadge 统一呈现；区段用 UiCard 包装。
业务逻辑（axios / 状态映射 / 公开字段 / 错误处理）零改动。
-->
<template>
  <div class="share-page">
    <!-- 加载中 -->
    <div v-if="loading" class="share-loading">
      <UiSpinner label="加载中…" />
    </div>

    <!-- 错误 -->
    <UiCard v-else-if="error" class="share-error">
      <div class="error-icon">⚠</div>
      <h2>分享已过期或不存在</h2>
      <p>{{ error }}</p>
    </UiCard>

    <!-- 成功加载 -->
    <div v-else-if="task" class="share-content">
      <!-- 顶部标题 -->
      <div class="share-header">
        <h1 v-if="task.pipeline_name">{{ task.pipeline_name }} 任务进度</h1>
        <h1 v-else>任务进度</h1>
      </div>

      <!-- 管线阶段进度 -->
      <UiCard v-if="pipelineNodes.length > 0" class="share-section">
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
      </UiCard>

      <!-- 任务基本信息 -->
      <UiCard class="share-section">
        <h2 class="section-title">任务信息</h2>
        <div class="task-header-row">
          <h3 class="task-title">{{ task.title }}</h3>
          <UiBadge :tone="statusTone(task.status)">
            {{ statusMap[task.status] || task.status_display || task.status }}
          </UiBadge>
        </div>
      </UiCard>

      <!-- 公开字段 -->
      <UiCard v-if="publicFields.length > 0" class="share-section">
        <h2 class="section-title">公开字段</h2>
        <div class="fields-grid">
          <div class="field-item" v-for="f in publicFields" :key="f.key">
            <span class="field-label">{{ f.label }}</span>
            <span class="field-value">{{ f.value || '暂无' }}</span>
          </div>
        </div>
      </UiCard>

      <!-- 时间信息 -->
      <UiCard class="share-section">
        <h2 class="section-title">时间</h2>
        <div class="time-row">
          <span class="time-item">创建时间：{{ formatDate(task.created_at) }}</span>
          <span class="time-item">更新时间：{{ formatDate(task.updated_at) }}</span>
        </div>
      </UiCard>
    </div>
  </div>
</template>

<script setup>
/**
 * Caduceus 公开分享页面脚本
 * 业务逻辑零改动：axios / status 映射 / 公开字段过滤 / 错误捕获全部保留。
 */
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { UiCard, UiBadge, UiSpinner } from '@/components/ui'

const route = useRoute()
const task = ref(null)
const loading = ref(true)
const error = ref('')
const pipelineNodes = ref([])
const currentStageIndex = ref(0)
const publicFields = ref([])

const statusMap = {
  draft: '草稿',
  pending: '待处理',
  in_progress: '进行中',
  completed: '已完成',
  cancelled: '已取消'
}

function statusTone(status) {
  switch (status) {
    case 'draft':       return 'neutral'
    case 'pending':     return 'warning'
    case 'in_progress': return 'info'
    case 'completed':   return 'success'
    case 'cancelled':   return 'danger'
    default:            return 'neutral'
  }
}

async function loadShareData() {
  loading.value = true
  error.value = ''
  try {
    const token = route.params.token
    const res = await axios.get(`/api/tasks/tasks/share/${token}/`)
    task.value = res.data

    pipelineNodes.value = task.value.pipeline_nodes || []
    if (pipelineNodes.value.length > 0 && task.value.current_node) {
      const idx = pipelineNodes.value.findIndex(n => n.id === task.value.current_node)
      currentStageIndex.value = idx >= 0 ? idx : 0
    }

    publicFields.value = task.value.fields || []
  } catch (err) {
    if (err.response?.status === 410) {
      error.value = '该分享链接已过期'
    } else if (err.response?.status === 404) {
      error.value = '分享链接不存在'
    } else {
      error.value = '加载失败，请检查链接是否正确'
    }
  }
  loading.value = false
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}`
}

onMounted(() => {
  loadShareData()
})
</script>

<style scoped>
.share-page {
  min-height: 100vh;
  background-color: var(--bg-canvas);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: var(--space-10) var(--space-5);
}

.share-loading {
  text-align: center;
  padding: var(--space-20) 0;
  color: var(--text-muted);
  font-size: var(--text-base);
}

.share-error {
  max-width: 420px;
  text-align: center;
  padding: var(--space-10) var(--space-6);
}

.error-icon {
  font-size: 48px;
  margin-bottom: var(--space-4);
  color: var(--color-destructive);
}

.share-error h2 {
  margin: 0 0 var(--space-2);
  font-size: var(--text-lg);
  color: var(--text-primary);
}

.share-error p {
  margin: 0;
  font-size: var(--text-sm);
  color: var(--text-muted);
}

.share-content {
  width: 100%;
  max-width: 700px;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.share-header {
  text-align: center;
  margin-bottom: var(--space-2);
}

.share-header h1 {
  margin: 0;
  font-size: var(--text-xl);
  color: var(--text-primary);
  font-weight: 600;
}

.share-section :deep(.ui-card__body) {
  padding: var(--space-5) var(--space-6);
}

.section-title {
  margin: 0 0 var(--space-4) 0;
  font-size: var(--text-sm);
  color: var(--text-muted);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* 管线阶段时间轴 */
.pipeline-timeline {
  display: flex;
  align-items: flex-start;
  overflow-x: auto;
  padding: var(--space-2) 0 var(--space-3);
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
  background-color: var(--color-muted);
  border: 3px solid var(--border-subtle);
  z-index: 1;
  transition: var(--transition-normal);
}

.step-dot.active {
  background-color: var(--text-primary);
  border-color: var(--text-primary);
}

.step-label {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  text-align: center;
  margin-top: var(--space-2);
  max-width: 80px;
  word-break: break-all;
}

.timeline-step.active .step-label {
  color: var(--text-primary);
  font-weight: 500;
}

.step-line {
  position: absolute;
  top: 10px;
  left: 50%;
  width: 100%;
  height: 3px;
  background-color: var(--border-subtle);
  z-index: 0;
}

.step-line.active {
  background-color: var(--text-primary);
}

/* 任务标题行 */
.task-header-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex-wrap: wrap;
}

.task-title {
  margin: 0;
  font-size: var(--text-lg);
  color: var(--text-primary);
  font-weight: 600;
}

/* 公开字段 */
.fields-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-3);
}

.field-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.field-label {
  font-size: var(--text-xs);
  color: var(--text-muted);
  font-weight: 500;
}

.field-value {
  font-size: var(--text-sm);
  color: var(--text-primary);
}

/* 时间 */
.time-row {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.time-item {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}
</style>