/**
 * Caduceus 路由配置
 * 定义页面路由和导航守卫
 */
import { createRouter, createWebHistory } from 'vue-router'

// 路由表（页面待后续创建）
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: '仪表盘', requiresAuth: true }
  },
  {
    path: '/tasks',
    name: 'TaskList',
    component: () => import('@/views/TaskList.vue'),
    meta: { title: '任务列表', requiresAuth: true }
  },
  {
    path: '/tasks/:id',
    name: 'TaskDetail',
    component: () => import('@/views/TaskDetail.vue'),
    meta: { title: '任务详情', requiresAuth: true }
  },
  {
    path: '/pipeline',
    name: 'PipelineEditor',
    component: () => import('@/views/PipelineEditor.vue'),
    meta: { title: '管线编辑器', requiresAuth: true }
  },
  {
    path: '/resources',
    name: 'ResourceList',
    component: () => import('@/views/ResourceList.vue'),
    meta: { title: '资源库', requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'AdminPanel',
    component: () => import('@/views/AdminPanel.vue'),
    meta: { title: '管理面板', requiresAuth: true }
  },
  {
    path: '/share/:token',
    name: 'SharePage',
    component: () => import('@/views/SharePage.vue'),
    meta: { title: '分享页面' }
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局前置守卫：检查认证状态
router.beforeEach((to, from, next) => {
  // 更新页面标题
  document.title = to.meta.title ? `${to.meta.title} - Caduceus` : 'Caduceus'

  // 检查是否需要认证
  if (to.meta.requiresAuth) {
    // 从 localStorage 检查登录状态（后续改为从 Pinia store 检查）
    const isLoggedIn = localStorage.getItem('isLoggedIn')
    if (!isLoggedIn) {
      // 未登录则跳转到登录页
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
  }

  next()
})

export default router