<!--
Caduceus 应用布局组件
提供响应式侧边栏导航和顶部栏
移动端侧边栏可折叠为汉堡菜单
-->
<template>
  <div class="app-layout">
    <!-- 顶部栏 -->
    <header class="header">
      <button class="menu-toggle" @click="toggleSidebar">
        <span class="menu-icon">☰</span>
      </button>
      <div class="logo">Caduceus</div>
      <div class="header-right">
        <NotificationBell />
        <div class="user-menu">
          <span>{{ user?.username || '用户' }}</span>
          <button @click="handleLogout">退出</button>
        </div>
      </div>
    </header>

    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <nav class="nav-menu">
        <router-link to="/" class="nav-item">仪表盘</router-link>
        <router-link to="/tasks" class="nav-item">任务列表</router-link>
        <router-link to="/pipeline" class="nav-item">管线编辑器</router-link>
        <router-link to="/resources" class="nav-item">资源库</router-link>
        <router-link to="/admin" class="nav-item">管理面板</router-link>
      </nav>
    </aside>

    <!-- 主内容区 -->
    <main class="main-content" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <slot />
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import NotificationBell from '@/components/NotificationBell.vue'

const authStore = useAuthStore()
const user = computed(() => authStore.user)

// 侧边栏折叠状态
const sidebarCollapsed = ref(false)

// 响应式：移动端默认折叠侧边栏
function checkMobile() {
  if (window.innerWidth < 768) {
    sidebarCollapsed.value = true
  }
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})

// 切换侧边栏
function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

// 登出
function handleLogout() {
  authStore.performLogout()
}
</script>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* 顶部栏 */
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
  background: #667eea;
  color: white;
  padding: 0 16px;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
}

.menu-toggle {
  background: none;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  padding: 8px;
}

.logo {
  font-size: 20px;
  font-weight: bold;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-menu button {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
}

/* 侧边栏 */
.sidebar {
  position: fixed;
  top: 60px;
  left: 0;
  bottom: 0;
  width: 240px;
  background: #f5f5f5;
  transition: transform 0.3s;
  z-index: 90;
}

.sidebar-collapsed {
  transform: translateX(-240px);
}

.nav-menu {
  padding: 16px 0;
}

.nav-item {
  display: block;
  padding: 12px 24px;
  color: #333;
  text-decoration: none;
}

.nav-item:hover {
  background: #e0e0e0;
}

.nav-item.router-link-active {
  background: #667eea;
  color: white;
}

/* 主内容区 */
.main-content {
  margin-top: 60px;
  margin-left: 240px;
  padding: 24px;
  flex: 1;
  background: #fff;
  transition: margin-left 0.3s;
}

.main-content.sidebar-collapsed {
  margin-left: 0;
}

/* 移动端样式 */
@media (max-width: 768px) {
  .sidebar {
    width: 240px;
  }

  .main-content {
    margin-left: 0;
  }

  .sidebar:not(.sidebar-collapsed) {
    transform: translateX(0);
  }
}
</style>