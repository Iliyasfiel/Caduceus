/**
 * Caduceus Dashboard API 模块
 * 提供仪表盘统计数据的 API 调用封装
 */
import client from './client'

export function getDashboardStats() {
  return client.get('/dashboard/stats/')
}
