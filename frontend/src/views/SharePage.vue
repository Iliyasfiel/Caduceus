<!--
Caduceus 公开分享页面
通过分享令牌访问任务信息，无需登录
-->
<template>
  <div class="share-page">
    <!-- 加载中 -->
    <div v-if="loading" class="share-loading">加载中...</div>

    <!-- 错误 -->
    <div v-else-if="error" class="share-error">
      <div class="error-icon">⚠</div>
      <h2>分享已过期或不存在</h2>
      <p>{{ error }}</p>
    </div>

    <!-- 成功加载 -->
    <div v-else-if="task" class="share-content">
      <!-- 顶部标题 -->
      <div class="share-header">
        <h1 v-if="task.pipeline_name">{{ task.pipeline_name }} 任务进度</h1>
        <h1 v-else>任务进度</h1>
      </div>

      <!-- 管线阶段进度 -->
      <section class="share-section" v-if="pipelineNodes.length > 0">
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

      <!-- 任务基本信息 -->
      <section class="share-section">
        <h2 class="section-title">任务信息</h2>
        <div class="task-header-row">
          <h3 class="task-title">{{ task.title }}</h3>
          <span class="status-tag" :class="'status-' + task.status">{{ statusMap[task.status] || task.status_display || task.status }}</span>
        </div>
      </section>

      <!-- 公开字段 -->
      <section class="share-section" v-if="publicFields.length > 0">
        <h2 class="section-title">公开字段</h2>
        <div class="fields-grid">
          <div class="field-item" v-for="f in publicFields" :key="f.key">
            <span class="field-label">{{ f.label }}</span>
            <span class="field-value">{{ f.value || '暂无' }}</span>
          </div>
        </div>
      </section>

      <!-- 时间信息 -->
      <section class="share-section">
        <h2 class="section-title">时间</h2>
        <div class="time-row">
          <span class="time-item">创建时间：{{ formatDate(task.created_at) }}</span>
          <span class="time-item">更新时间：{{ formatDate(task.updated_at) }}</span>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
/**
 * Caduceus 公开分享页面
 * 无需登录即可查看任务基本信息、管线进度和公开字段
 */
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

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
  background: #f5f7fa;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 40px 20px;
}

.share-loading {
  text-align: center;
  padding: 80px 0;
  color: #9ca3af;
  font-size: 16px;
}

.share-error {
  text-align: center;
  padding: 80px 20px;
  color: #6b7280;
}
.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}
.share-error h2 {
  margin: 0 0 8px 0;
  font-size: 20px;
  color: #374151;
}
.share-error p {
  margin: 0;
  font-size: 14px;
  color: #9ca3af;
}

.share-content {
  width: 100%;
  max-width: 700px;
}

.share-header {
  text-align: center;
  margin-bottom: 24px;
}
.share-header h1 {
  margin: 0;
  font-size: 22px;
  color: #1f2937;
}

.share-section {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 20px 24px;
  margin-bottom: 16px;
}
.section-title {
  margin: 0 0 14px 0;
  font-size: 14px;
  color: #9ca3af;
  font-weight: 500;
}

/* 管线阶段时间轴 */
.pipeline-timeline {
  display: flex;
  align-items: flex-start;
  overflow-x: auto;
  padding: 8px 0 12px;
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
  border-radius: 50%;
  background: #e5e7eb;
  border: 3px solid #d1d5db;
  z-index: 1;
  transition: all 0.3s;
}
.step-dot.active {
  background: #667eea;
  border-color: #667eea;
}
.step-label {
  font-size: 12px;
  color: #6b7280;
  text-align: center;
  margin-top: 6px;
  max-width: 80px;
  word-break: break-all;
}
.timeline-step.active .step-label {
  color: #667eea;
  font-weight: 500;
}
.step-line {
  position: absolute;
  top: 10px;
  left: 50%;
  width: 100%;
  height: 3px;
  background: #e5e7eb;
  z-index: 0;
}
.step-line.active {
  background: #667eea;
}

/* 任务标题行 */
.task-header-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.task-title {
  margin: 0;
  font-size: 18px;
  color: #1f2937;
}
.status-tag {
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}
.status-draft { background: #f3f4f6; color: #6b7280; }
.status-pending { background: #fef3c7; color: #92400e; }
.status-in_progress { background: #dbeafe; color: #1e40af; }
.status-completed { background: #d1fae5; color: #065f46; }
.status-cancelled { background: #fee2e2; color: #991b1b; }

/* 公开字段 */
.fields-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.field-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.field-label {
  font-size: 12px;
  color: #9ca3af;
  font-weight: 500;
}
.field-value {
  font-size: 14px;
  color: #374151;
}

/* 时间 */
.time-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.time-item {
  font-size: 13px;
  color: #6b7280;
}
</style>
