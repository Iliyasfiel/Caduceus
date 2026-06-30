/**
 * Caduceus 认证状态管理
 * 管理用户登录状态、用户信息等
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login, logout, getCurrentUser } from '@/api/auth'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  // 用户信息
  const user = ref(null)
  // 登录状态
  const isLoggedIn = computed(() => !!user.value)

  // 登录操作
  async function performLogin(username, password) {
    try {
      await login(username, password)
      // 登录成功后获取用户信息
      const response = await getCurrentUser()
      user.value = response.data
      localStorage.setItem('isLoggedIn', 'true')
      return true
    } catch (error) {
      console.error('登录失败:', error)
      return false
    }
  }

  // 登出操作
  async function performLogout() {
    try {
      await logout()
    } catch (error) {
      console.error('登出失败:', error)
    }
    user.value = null
    localStorage.removeItem('isLoggedIn')
    router.push({ name: 'Login' })
  }

  // 初始化：获取当前用户信息
  async function init() {
    if (localStorage.getItem('isLoggedIn')) {
      try {
        const response = await getCurrentUser()
        user.value = response.data
      } catch (error) {
        // 获取用户信息失败，清除登录状态
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