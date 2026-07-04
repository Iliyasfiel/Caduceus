/**
 * Caduceus 通知状态管理
 * 管理通知列表、未读计数、WebSocket 实时连接等
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getNotifications, getUnreadCount, markAsRead, markAllAsRead } from '@/api/notifications'

const MAX_RETRY_COUNT = 3
const RETRY_INTERVAL = 2000

export const useNotificationsStore = defineStore('notifications', () => {
  const notifications = ref([])
  const unreadCount = ref(0)
  let wsConnection = null
  let retryCount = 0
  let retryTimer = null

  async function fetchNotifications() {
    try {
      const response = await getNotifications()
      notifications.value = response.data.results || response.data
    } catch (error) {
      console.error('获取通知列表失败:', error)
    }
  }

  async function fetchUnreadCount() {
    try {
      const response = await getUnreadCount()
      unreadCount.value = response.data.count || 0
    } catch (error) {
      console.error('获取未读计数失败:', error)
    }
  }

  async function markNotificationAsRead(id) {
    try {
      await markAsRead(id)
      const notification = notifications.value.find(n => n.id === id)
      if (notification) {
        notification.is_read = true
      }
      unreadCount.value = Math.max(0, unreadCount.value - 1)
      sendMarkRead(id)
    } catch (error) {
      console.error('标记已读失败:', error)
    }
  }

  async function markAllNotificationsAsRead() {
    try {
      await markAllAsRead()
      notifications.value.forEach(n => n.is_read = true)
      unreadCount.value = 0
    } catch (error) {
      console.error('标记全部已读失败:', error)
    }
  }

  /**
   * 发送标记已读消息给 WebSocket 服务端
   * @param {number} id - 通知 ID
   */
  function sendMarkRead(id) {
    if (wsConnection && wsConnection.readyState === WebSocket.OPEN) {
      wsConnection.send(JSON.stringify({
        action: 'mark_read',
        notification_id: id
      }))
    }
  }

  /**
   * 建立 WebSocket 连接，实现实时通知推送
   * 连接失败时自动重试，最多重试 MAX_RETRY_COUNT 次
   */
  function connectWebSocket() {
    if (wsConnection && wsConnection.readyState === WebSocket.OPEN) return

    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${location.host}/ws/notifications/`

    wsConnection = new WebSocket(wsUrl)

    wsConnection.onopen = () => {
      retryCount = 0
      wsConnection.send(JSON.stringify({ action: 'join' }))
    }

    wsConnection.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        const notification = data.notification || data
        if (notification) {
          notifications.value.unshift(notification)
          unreadCount.value += 1
        }
      } catch (error) {
        console.error('解析 WebSocket 消息失败:', error)
      }
    }

    wsConnection.onerror = (error) => {
      console.error('WebSocket 连接错误:', error)
    }

    wsConnection.onclose = (event) => {
      if (!event.wasClean && retryCount < MAX_RETRY_COUNT) {
        retryCount += 1
        // 延迟重试
        retryTimer = setTimeout(() => {
          connectWebSocket()
        }, RETRY_INTERVAL)
      }
    }
  }

  /**
   * 断开 WebSocket 连接并清理重试定时器
   */
  function disconnectWebSocket() {
    if (retryTimer) {
      clearTimeout(retryTimer)
      retryTimer = null
    }
    retryCount = MAX_RETRY_COUNT
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
    sendMarkRead,
    connectWebSocket,
    disconnectWebSocket
  }
})
