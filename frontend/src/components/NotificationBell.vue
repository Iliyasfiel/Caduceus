<!--
Caduceus 通知铃铛组件
展示未读通知数量，点击展开通知列表，支持实时 WebSocket 通知
-->
<template>
  <div class="notification-bell" ref="bellRef">
    <button class="bell-button" @click="toggleNotifications">
      <span class="bell-icon">🔔</span>
      <span v-if="unreadCount > 0" class="badge">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
    </button>
    <div v-if="showNotifications" class="notification-dropdown" @click.stop>
      <div class="dropdown-header">
        <span>通知</span>
        <button class="mark-all-btn" @click="markAllRead">全部标记已读</button>
      </div>
      <div class="notification-list">
        <p v-if="notifications.length === 0" class="empty-tip">暂无通知</p>
        <div
          v-for="notification in notifications"
          :key="notification.id"
          class="notification-item"
          :class="{ unread: !notification.is_read }"
          @click="handleNotificationClick(notification)"
        >
          <div class="notification-title">{{ notification.title }}</div>
          <div class="notification-time">{{ formatRelativeTime(notification.created_at) }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 通知铃铛组件
 * 提供通知下拉菜单、已读标记、时间格式化等功能
 */
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useNotificationsStore } from '@/stores/notifications'
import router from '@/router'

const notificationsStore = useNotificationsStore()

const unreadCount = computed(() => notificationsStore.unreadCount)
const notifications = computed(() => notificationsStore.notifications)

const showNotifications = ref(false)
const bellRef = ref(null)

function toggleNotifications() {
  showNotifications.value = !showNotifications.value
}

// 点击通知项：标记已读 + 跳转
async function handleNotificationClick(notification) {
  if (!notification.is_read) {
    await notificationsStore.markNotificationAsRead(notification.id)
  }
  showNotifications.value = false
  if (notification.link) {
    router.push(notification.link)
  }
}

// 全部标记已读
function markAllRead() {
  notificationsStore.markAllNotificationsAsRead()
}

// 点击外部区域关闭下拉菜单
function handleClickOutside(event) {
  if (bellRef.value && !bellRef.value.contains(event.target)) {
    showNotifications.value = false
  }
}

// 相对时间格式化：刚刚 / n分钟前 / n小时前 / n天前
function formatRelativeTime(time) {
  if (!time) return ''
  const now = Date.now()
  const past = new Date(time).getTime()
  const diff = Math.floor((now - past) / 1000)

  if (diff < 60) return '刚刚'
  if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`
  if (diff < 2592000) return `${Math.floor(diff / 86400)}天前`
  return new Date(time).toLocaleString('zh-CN')
}

onMounted(() => {
  notificationsStore.fetchUnreadCount()
  notificationsStore.fetchNotifications()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
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
  padding: 4px;
}

.badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: #e74c3c;
  color: white;
  font-size: 11px;
  min-width: 18px;
  height: 18px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
  line-height: 1;
}

.notification-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  width: 320px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 110;
  margin-top: 8px;
}

.dropdown-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
  font-weight: 600;
  color: #333;
}

.mark-all-btn {
  background: none;
  border: none;
  color: #667eea;
  cursor: pointer;
  font-size: 13px;
}

.mark-all-btn:hover {
  color: #5a6fd6;
}

.notification-list {
  max-height: 360px;
  overflow-y: auto;
  padding: 8px;
}

.empty-tip {
  text-align: center;
  color: #999;
  padding: 24px;
  margin: 0;
}

.notification-item {
  padding: 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.notification-item:hover {
  background: #f5f7fa;
}

.notification-item.unread {
  background: #f0f4ff;
}

.notification-item.unread:hover {
  background: #e6edff;
}

.notification-title {
  font-weight: 500;
  color: #333;
  font-size: 14px;
}

.notification-time {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}
</style>
