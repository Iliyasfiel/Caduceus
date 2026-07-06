/**
 * Caduceus 前端入口文件
 * 初始化 Vue 应用、路由和状态管理
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
// 设计令牌与全局基础样式（必须早于 App.vue 引入，保证组件 mounted 时令牌已生效）
import './styles/tokens.css'
import './styles/base.css'
// 响应式断点 + 工具类（mobile-first，按需启用）
import './styles/breakpoints.css'
import App from './App.vue'
import router from './router'
import { useThemeStore } from './stores/theme'

// 创建 Vue 应用实例
const app = createApp(App)

// 注册 Pinia 状态管理
const pinia = createPinia()
app.use(pinia)

// 在 Pinia 可用后立刻初始化主题（避免首屏闪白）
useThemeStore().init()

// 注册路由
app.use(router)

// 挂载应用
app.mount('#app')