/**
 * Caduceus 资源状态管理
 * 管理资源类型、资源条目等状态
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getResourceTypes, getResourceItems } from '@/api/resources'

export const useResourcesStore = defineStore('resources', () => {
  // 资源类型列表
  const resourceTypes = ref([])
  // 资源条目列表
  const resourceItems = ref([])
  // 加载状态
  const loading = ref(false)

  // 获取资源类型
  async function fetchResourceTypes() {
    loading.value = true
    try {
      const response = await getResourceTypes()
      resourceTypes.value = response.data.results || response.data
    } catch (error) {
      console.error('获取资源类型失败:', error)
    }
    loading.value = false
  }

  // 获取资源条目
  async function fetchResourceItems(params = {}) {
    loading.value = true
    try {
      const response = await getResourceItems(params)
      resourceItems.value = response.data.results || response.data
    } catch (error) {
      console.error('获取资源条目失败:', error)
    }
    loading.value = false
  }

  return {
    resourceTypes,
    resourceItems,
    loading,
    fetchResourceTypes,
    fetchResourceItems
  }
})