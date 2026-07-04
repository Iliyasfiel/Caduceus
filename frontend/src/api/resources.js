/**
 * Caduceus 资源 API
 * 提供资源类型、资源条目和预约的接口
 */
import client from './client'

// 获取资源类型列表
export function getResourceTypes() {
  return client.get('/resources/resource-types/')
}

// 获取资源条目列表
export function getResourceItems(params = {}) {
  return client.get('/resources/resource-items/', { params })
}

// 获取单个资源条目详情
export function getResourceItem(id) {
  return client.get(`/resources/resource-items/${id}/`)
}

// 创建资源条目
export function createResourceItem(data) {
  return client.post('/resources/resource-items/', data)
}

// 更新资源条目
export function updateResourceItem(id, data) {
  return client.patch(`/resources/resource-items/${id}/`, data)
}

// 删除资源条目
export function deleteResourceItem(id) {
  return client.delete(`/resources/resource-items/${id}/`)
}

// 获取资源操作日志列表
export function getResourceLogs(resourceId) {
  return client.get('/resources/resource-logs/', {
    params: { resource: resourceId }
  })
}

// 创建资源操作日志
export function createResourceLog(data) {
  return client.post('/resources/resource-logs/', data)
}

// 创建资源类型
export function createResourceType(data) {
  return client.post('/resources/resource-types/', data)
}

// 更新资源类型
export function updateResourceType(id, data) {
  return client.patch(`/resources/resource-types/${id}/`, data)
}

export default {
  getResourceTypes,
  getResourceItems,
  getResourceItem,
  createResourceItem,
  updateResourceItem,
  deleteResourceItem,
  getResourceLogs,
  createResourceLog,
  createResourceType,
  updateResourceType
}
