/**
 * Caduceus 管线 API
 * 提供管线的 CRUD 操作接口
 */
import client from './client'

// 获取管线列表
export function getPipelines() {
  return client.get('/pipeline/')
}

// 获取单个管线详情
export function getPipeline(id) {
  return client.get(`/pipeline/${id}/`)
}

// 创建管线
export function createPipeline(data) {
  return client.post('/pipeline/', data)
}

// 更新管线
export function updatePipeline(id, data) {
  return client.patch(`/pipeline/${id}/`, data)
}

// 删除管线
export function deletePipeline(id) {
  return client.delete(`/pipeline/${id}/`)
}

export default {
  getPipelines,
  getPipeline,
  createPipeline,
  updatePipeline,
  deletePipeline
}