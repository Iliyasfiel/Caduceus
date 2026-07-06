/**
 * Caduceus 认证状态管理
 * 管理用户登录状态、用户信息，登录成功时自动建立 WebSocket 通知连接
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login, logout, getCurrentUser } from '@/api/auth'
import { useNotificationsStore } from '@/stores/notifications'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isLoggedIn = computed(() => !!user.value)

  async function performLogin(username, password) {
    try {
      await login(username, password)
      const response = await getCurrentUser()
      user.value = response.data
      localStorage.setItem('isLoggedIn', 'true')
      // 登录成功后建立 WebSocket 通知连接
      const notificationsStore = useNotificationsStore()
      notificationsStore.connectWebSocket()
      return true
    } catch (error) {
      console.error('登录失败:', error)
      return false
    }
  }

  async function performLogout() {
    try {
      await logout()
    } catch (error) {
      console.error('登出失败:', error)
    }
    // 登出时断开 WebSocket 通知连接
    const notificationsStore = useNotificationsStore()
    notificationsStore.disconnectWebSocket()
    user.value = null
    localStorage.removeItem('isLoggedIn')
    router.push({ name: 'Login' })
  }

  // 初始化：获取当前用户信息，已登录时恢复 WebSocket 连接
  async function init() {
    if (localStorage.getItem('isLoggedIn')) {
      try {
        const response = await getCurrentUser()
        user.value = response.data
        // 已登录状态恢复 WebSocket 连接
        const notificationsStore = useNotificationsStore()
        notificationsStore.connectWebSocket()
      } catch (error) {
        localStorage.removeItem('isLoggedIn')
        user.value = null
      }
    }
  }

  return {
    user,
    isLoggedIn,
    performLogin,
    performLogout,
    init
  }
})
