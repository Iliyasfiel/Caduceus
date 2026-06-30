<!--
Caduceus 仪表盘页面
展示基础统计卡片和任务概览
-->
<template>
  <AppLayout>
    <div class="dashboard">
      <h1>仪表盘</h1>
      <p>仪表盘功能待 Phase 6 实现</p>
      <div class="stats-grid">
        <div class="stat-card">
          <h3>本月任务总数</h3>
          <p class="stat-value">--</p>
        </div>
        <div class="stat-card">
          <h3>已完成</h3>
          <p class="stat-value">--</p>
        </div>
        <div class="stat-card">
          <h3>进行中</h3>
          <p class="stat-value">--</p>
        </div>
        <div class="stat-card">
          <h3>资源调用</h3>
          <p class="stat-value">--</p>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import AppLayout from '@/components/AppLayout.vue'
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
  color: #667eea;
}
</style>