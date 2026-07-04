/**
 * Caduceus 管线 API
 * 提供管线的 CRUD 操作接口
 */
import client from './client'

// 获取管线列表
export function getPipelines() {
  return client.get('/pipeline/pipelines/')
}

// 获取单个管线详情
export function getPipeline(id) {
  return client.get(`/pipeline/pipelines/${id}/`)
}

// 创建管线
export function createPipeline(data) {
  return client.post('/pipeline/pipelines/', data)
}

// 更新管线
export function updatePipeline(id, data) {
  return client.patch(`/pipeline/pipelines/${id}/`, data)
}

// 删除管线
export function deletePipeline(id) {
  return client.delete(`/pipeline/pipelines/${id}/`)
}

export default {
  getPipelines,
  getPipeline,
  createPipeline,
  updatePipeline,
  deletePipeline
}
