/**
 * Caduceus 任务 API
 * 提供任务的 CRUD 操作接口
 */
import client from './client'

// 获取任务列表
export function getTasks(params = {}) {
  return client.get('/tasks/tasks/', { params })
}

// 获取单个任务详情
export function getTask(id) {
  return client.get(`/tasks/tasks/${id}/`)
}

// 创建任务
export function createTask(data) {
  return client.post('/tasks/tasks/', data)
}

// 更新任务
export function updateTask(id, data) {
  return client.patch(`/tasks/tasks/${id}/`, data)
}

// 删除任务
export function deleteTask(id) {
  return client.delete(`/tasks/tasks/${id}/`)
}

// 获取任务的执行人分配
export function getTaskAssignments(taskId) {
  return client.get(`/tasks/tasks/${taskId}/assignments/`)
}

// 添加任务评论
export function addTaskComment(taskId, content) {
  return client.post(`/tasks/tasks/${taskId}/add_comment/`, { content })
}

// 关联其他任务
export function relateTask(taskId, relatedTaskId) {
  return client.post(`/tasks/tasks/${taskId}/relate/`, { related_task_id: relatedTaskId })
}

// 获取任务变更日志
export function getTaskLogs(taskId) {
  return client.get(`/tasks/tasks/${taskId}/logs/`)
}

// 更新任务分享配置（设置过期时间等）
export function updateTaskShare(id, data) {
  return client.patch(`/tasks/tasks/${id}/share/`, data)
}

// 取消任务分享
export function cancelTaskShare(id) {
  return client.post(`/tasks/tasks/${id}/cancel_share/`)
}

export default {
  getTasks,
  getTask,
  createTask,
  updateTask,
  deleteTask,
  getTaskAssignments,
  addTaskComment,
  relateTask,
  getTaskLogs,
  updateTaskShare,
  cancelTaskShare
}
