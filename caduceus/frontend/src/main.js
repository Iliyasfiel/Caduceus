/**
 * Caduceus 前端入口文件
 * 初始化 Vue 应用、路由和状态管理
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// 创建 Vue 应用实例
const app = createApp(App)

// 注册 Pinia 状态管理
app.use(createPinia())

// 注册路由
app.use(router)

// 挂载应用
app.mount('#app')