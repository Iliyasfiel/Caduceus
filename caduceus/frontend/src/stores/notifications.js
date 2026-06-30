/**
 * Caduceus 通知状态管理
 * 管理通知列表、未读计数、WebSocket 连接等
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getNotifications, getUnreadCount, markAsRead, markAllAsRead } from '@/api/notifications'

export const useNotificationsStore = defineStore('notifications', () => {
  // 通知列表
  const notifications = ref([])
  // 未读计数
  const unreadCount = ref(0)
  // WebSocket 连接
  let wsConnection = null

  // 获取通知列表
  async function fetchNotifications() {
    try {
      const response = await getNotifications()
      notifications.value = response.data.results || response.data
    } catch (error) {
      console.error('获取通知列表失败:', error)
    }
  }

  // 获取未读计数
  async function fetchUnreadCount() {
    try {
      const response = await getUnreadCount()
      unreadCount.value = response.data.count || 0
    } catch (error) {
      console.error('获取未读计数失败:', error)
    }
  }

  // 标记已读
  async function markNotificationAsRead(id) {
    try {
      await markAsRead(id)
      // 更新本地状态
      const notification = notifications.value.find(n => n.id === id)
      if (notification) {
        notification.is_read = true
      }
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    } catch (error) {
      console.error('标记已读失败:', error)
    }
  }

  // 标记全部已读
  async function markAllNotificationsAsRead() {
    try {
      await markAllAsRead()
      notifications.value.forEach(n => n.is_read = true)
      unreadCount.value = 0
    } catch (error) {
      console.error('标记全部已读失败:', error)
    }
  }

  // 建立 WebSocket 连接（待实现）
  function connectWebSocket() {
    // WebSocket 连接逻辑待 Phase 3 实现
    // wsConnection = new WebSocket(`${location.protocol === 'https:' ? 'wss:' : 'ws:'}//${location.host}/ws/notifications/`)
  }

  // 断开 WebSocket 连接
  function disconnectWebSocket() {
    if (wsConnection) {
      wsConnection.close()
      wsConnection = null
    }
  }

  return {
    notifications,
    unreadCount,
    fetchNotifications,
    fetchUnreadCount,
    markNotificationAsRead,
    markAllNotificationsAsRead,
    connectWebSocket,
    disconnectWebSocket
  }
})