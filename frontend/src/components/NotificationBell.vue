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
  background: var(--color-destructive);
  color: var(--color-primary-foreground);
  font-size: var(--text-xs);
  min-width: 18px;
  height: 18px;
  border-radius: var(--radius-full);
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
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  z-index: 110;
  margin-top: var(--space-2);
}

.dropdown-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--border-subtle);
  font-weight: 600;
  color: var(--text-primary);
  font-size: var(--text-sm);
}

.mark-all-btn {
  background: none;
  border: none;
  color: var(--text-primary);
  cursor: pointer;
  font-size: var(--text-xs);
  transition: color var(--transition-fast);
}

.mark-all-btn:hover {
  color: var(--text-secondary);
}

.notification-list {
  max-height: 360px;
  overflow-y: auto;
  padding: var(--space-2);
}

.empty-tip {
  text-align: center;
  color: var(--text-muted);
  padding: var(--space-6);
  margin: 0;
  font-size: var(--text-sm);
}

.notification-item {
  padding: var(--space-3);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background-color var(--transition-fast);
}

.notification-item:hover {
  background: var(--color-muted);
}

.notification-item.unread {
  background: var(--badge-info-bg);
}

.notification-item.unread:hover {
  background: var(--badge-info-bg);
  filter: brightness(0.95);
}

.notification-title {
  font-weight: 500;
  color: var(--text-primary);
  font-size: var(--text-sm);
}

.notification-time {
  font-size: var(--text-xs);
  color: var(--text-muted);
  margin-top: var(--space-1);
}
</style>
