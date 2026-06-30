/**
 * Caduceus 认证 API
 * 提供登录、登出、获取用户信息等接口
 */
import client from './client'

// 登录
export function login(username, password) {
  // Django 使用 Session 认证，这里发送 POST 到登录接口
  // 实际实现时需要配合 Django 的 authentication views
  return client.post('/auth/login/', { username, password })
}

// 登出
export function logout() {
  return client.post('/auth/logout/')
}

// 获取当前用户信息
export function getCurrentUser() {
  return client.get('/accounts/me/')
}

export default {
  login,
  logout,
  getCurrentUser
}