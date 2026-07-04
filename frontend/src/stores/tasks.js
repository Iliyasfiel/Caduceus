/**
 * Caduceus 任务状态管理
 * 管理任务列表、当前任务详情等状态
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getTasks, getTask, createTask, updateTask, deleteTask, addTaskComment } from '@/api/tasks'

export const useTasksStore = defineStore('tasks', () => {
  // 任务列表
  const tasks = ref([])
  // 当前任务详情
  const currentTask = ref(null)
  // 加载状态
  const loading = ref(false)

  // 获取任务列表
  async function fetchTasks(params = {}) {
    loading.value = true
    try {
      const response = await getTasks(params)
      tasks.value = response.data.results || response.data
    } catch (error) {
      console.error('获取任务列表失败:', error)
    }
    loading.value = false
  }

  // 获取任务详情
  async function fetchTask(id) {
    loading.value = true
    try {
      const response = await getTask(id)
      currentTask.value = response.data
    } catch (error) {
      console.error('获取任务详情失败:', error)
    }
    loading.value = false
  }

  // 创建任务
  async function createNewTask(data) {
    loading.value = true
    try {
      const response = await createTask(data)
      tasks.value.unshift(response.data)
      return response.data
    } catch (error) {
      console.error('创建任务失败:', error)
      throw error
    }
    loading.value = false
  }

  // 更新任务
  async function updateExistingTask(id, data) {
    loading.value = true
    try {
      const response = await updateTask(id, data)
      // 更新列表中的任务
      const index = tasks.value.findIndex(t => t.id === id)
      if (index !== -1) {
        tasks.value[index] = response.data
      }
      // 更新当前任务详情
      if (currentTask.value && currentTask.value.id === id) {
        currentTask.value = response.data
      }
      return response.data
    } catch (error) {
      console.error('更新任务失败:', error)
      throw error
    }
    loading.value = false
  }

  // 删除任务
  async function deleteExistingTask(id) {
    loading.value = true
    try {
      await deleteTask(id)
      tasks.value = tasks.value.filter(t => t.id !== id)
      if (currentTask.value && currentTask.value.id === id) {
        currentTask.value = null
      }
    } catch (error) {
      console.error('删除任务失败:', error)
      throw error
    }
    loading.value = false
  }

  // 添加评论
  async function addComment(taskId, content) {
    try {
      const response = await addTaskComment(taskId, content)
      // 更新当前任务的评论列表
      if (currentTask.value && currentTask.value.id === taskId) {
        currentTask.value.comments.push(response.data)
      }
      return response.data
    } catch (error) {
      console.error('添加评论失败:', error)
      throw error
    }
  }

  return {
    tasks,
    currentTask,
    loading,
    fetchTasks,
    fetchTask,
    createNewTask,
    updateExistingTask,
    deleteExistingTask,
    addComment
  }
})