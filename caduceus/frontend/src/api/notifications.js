/**
 * Caduceus 通知 API
 * 提供获取通知、标记已读等接口
 */
import client from './client'

// 获取通知列表
export function getNotifications(params = {}) {
  return client.get('/notifications/', { params })
}

// 获取未读通知数量
export function getUnreadCount() {
  return client.get('/notifications/unread_count/')
}

// 标记单个通知为已读
export function markAsRead(id) {
  return client.patch(`/notifications/${id}/`, { is_read: true })
}

// 标记所有通知为已读
export function markAllAsRead() {
  return client.post('/notifications/mark_all_read/')
}

export default {
  getNotifications,
  getUnreadCount,
  markAsRead,
  markAllAsRead
}