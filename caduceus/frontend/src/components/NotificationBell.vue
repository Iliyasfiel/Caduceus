<!--
Caduceus 通知铃铛组件
展示未读通知数量，点击展开通知列表
-->
<template>
  <div class="notification-bell">
    <button class="bell-button" @click="toggleNotifications">
      <span class="bell-icon">🔔</span>
      <span v-if="unreadCount > 0" class="badge">{{ unreadCount }}</span>
    </button>
    <div v-if="showNotifications" class="notification-dropdown">
      <div class="dropdown-header">
        <span>通知</span>
        <button @click="markAllRead">全部标记已读</button>
      </div>
      <div class="notification-list">
        <p v-if="notifications.length === 0">暂无通知</p>
        <div v-for="notification in notifications" :key="notification.id" class="notification-item" :class="{ unread: !notification.is_read }">
          <div class="notification-title">{{ notification.title }}</div>
          <div class="notification-time">{{ formatTime(notification.created_at) }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useNotificationsStore } from '@/stores/notifications'

const notificationsStore = useNotificationsStore()

// 未读计数
const unreadCount = computed(() => notificationsStore.unreadCount)
// 通知列表
const notifications = computed(() => notificationsStore.notifications)

// 下拉菜单显示状态
const showNotifications = ref(false)

// 切换下拉菜单
function toggleNotifications() {
  showNotifications.value = !showNotifications.value
}

// 全部标记已读
function markAllRead() {
  notificationsStore.markAllNotificationsAsRead()
}

// 格式化时间
function formatTime(time) {
  if (!time) return ''
  const date = new Date(time)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  // 获取未读计数和通知列表
  notificationsStore.fetchUnreadCount()
  notificationsStore.fetchNotifications()
})
</script>

<style scoped>
.notification-bell {
  position: relative;
}

.bell-button {
  background: none;
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
  position: relative;
}

.badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: #e74c3c;
  color: white;
  font-size: 12px;
  min-width: 16px;
  height: 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.notification-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  width: 300px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 110;
}

.dropdown-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-bottom: 1px solid #eee;
}

.dropdown-header button {
  background: none;
  border: none;
  color: #667eea;
  cursor: pointer;
}

.notification-list {
  max-height: 300px;
  overflow-y: auto;
  padding: 8px;
}

.notification-item {
  padding: 12px;
  border-radius: 4px;
}

.notification-item.unread {
  background: #f0f4ff;
}

.notification-title {
  font-weight: 500;
  color: #333;
}

.notification-time {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}
</style>