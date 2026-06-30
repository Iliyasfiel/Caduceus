/**
 * Caduceus 资源 API
 * 提供资源类型、资源条目和预约的接口
 */
import client from './client'

// 获取资源类型列表
export function getResourceTypes() {
  return client.get('/resources/types/')
}

// 获取资源条目列表
export function getResourceItems(params = {}) {
  return client.get('/resources/items/', { params })
}

// 获取单个资源条目详情
export function getResourceItem(id) {
  return client.get(`/resources/items/${id}/`)
}

// 创建资源预约
export function createBooking(data) {
  return client.post('/resources/bookings/', data)
}

// 更新预约状态
export function updateBookingStatus(id, status) {
  return client.patch(`/resources/bookings/${id}/`, { status })
}

export default {
  getResourceTypes,
  getResourceItems,
  getResourceItem,
  createBooking,
  updateBookingStatus
}