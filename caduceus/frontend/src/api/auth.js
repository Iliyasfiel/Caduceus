/**
 * Caduceus 认证 API
 * 提供登录、登出、获取用户信息等接口
 */
import client from './client'

// 登录
export function login(username, password) {
  return client.post('/accounts/auth/login/', { username, password })
}

// 登出
export function logout() {
  return client.post('/accounts/auth/logout/')
}

// 获取当前用户信息
export function getCurrentUser() {
  return client.get('/accounts/users/me/')
}

export default {
  login,
  logout,
  getCurrentUser
}