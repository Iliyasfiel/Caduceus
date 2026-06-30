<!--
Caduceus 任务列表页面
展示所有任务，支持"只看与我相关"筛选
-->
<template>
  <AppLayout>
    <div class="task-list">
      <h1>任务列表</h1>
      <div class="filters">
        <label>
          <input type="checkbox" v-model="showMineOnly" />
          只看与我相关
        </label>
      </div>
      <div class="task-grid">
        <p>任务列表功能待 Phase 1 实现</p>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref } from 'vue'
import AppLayout from '@/components/AppLayout.vue'

const showMineOnly = ref(false)
</script>

<style scoped>
.task-list {
  padding: 24px;
}

.filters {
  margin-bottom: 24px;
}

.task-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}
</style>