/**
 * Caduceus 任务 API
 * 提供任务的 CRUD 操作接口
 */
import client from './client'

// 获取任务列表
export function getTasks(params = {}) {
  return client.get('/tasks/', { params })
}

// 获取单个任务详情
export function getTask(id) {
  return client.get(`/tasks/${id}/`)
}

// 创建任务
export function createTask(data) {
  return client.post('/tasks/', data)
}

// 更新任务
export function updateTask(id, data) {
  return client.patch(`/tasks/${id}/`, data)
}

// 删除任务
export function deleteTask(id) {
  return client.delete(`/tasks/${id}/`)
}

// 获取任务的执行人分配
export function getTaskAssignments(taskId) {
  return client.get(`/tasks/${taskId}/assignments/`)
}

// 添加任务评论
export function addTaskComment(taskId, content) {
  return client.post(`/tasks/${taskId}/add_comment/`, { content })
}

// 关联其他任务
export function relateTask(taskId, relatedTaskId) {
  return client.post(`/tasks/${taskId}/relate/`, { related_task_id: relatedTaskId })
}

export default {
  getTasks,
  getTask,
  createTask,
  updateTask,
  deleteTask,
  getTaskAssignments,
  addTaskComment,
  relateTask
}