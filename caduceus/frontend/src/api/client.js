/**
 * Caduceus HTTP 客户端
 * 基于 Axios 创建统一的 API 调用实例
 * 包含请求拦截器和响应拦截器
 */
import axios from 'axios'
import router from '@/router'

// 创建 Axios 实例
const client = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器：可在此添加认证 token 等
client.interceptors.request.use(
  (config) => {
    // 后续添加 CSRF token 或 JWT token
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器：处理错误响应
client.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // 401 未认证：跳转到登录页
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('isLoggedIn')
      router.push({ name: 'Login' })
    }
    return Promise.reject(error)
  }
)

export default client