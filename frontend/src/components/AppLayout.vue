<!--
Caduceus 应用布局组件
提供响应式侧边栏导航和顶部栏（Vercel 风格 token 化）
移动端侧边栏可折叠为汉堡菜单
-->
<template>
  <div class="app-layout">
    <!-- 顶部栏 -->
    <header class="header">
      <button class="menu-toggle" @click="toggleSidebar" aria-label="切换菜单">
        <span class="menu-icon">☰</span>
      </button>
      <div class="logo">Caduceus</div>
      <div class="header-right">
        <UiThemeToggle />
        <NotificationBell />
        <div class="user-menu">
          <span class="user-name">{{ user?.username || '用户' }}</span>
          <UiButton variant="secondary" size="sm" @click="handleLogout">
            退出
          </UiButton>
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
/**
 * AppLayout 脚本：业务逻辑零改动（auth store / 登出 / 响应式折叠全部保留）。
 */
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import NotificationBell from '@/components/NotificationBell.vue'
import { UiButton, UiThemeToggle } from '@/components/ui'

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
  background-color: var(--bg-canvas);
}

/* 顶部栏 */
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
  background-color: var(--bg-surface);
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-subtle);
  padding: 0 var(--space-4);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
}

.menu-toggle {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: var(--text-lg);
  cursor: pointer;
  padding: var(--space-2);
  border-radius: var(--radius-md);
  transition: color var(--transition-fast), background-color var(--transition-fast);
}

.menu-toggle:hover {
  color: var(--text-primary);
  background-color: var(--color-muted);
}

.logo {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.user-menu {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.user-name {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  font-weight: 500;
}

/* 侧边栏 */
.sidebar {
  position: fixed;
  top: 60px;
  left: 0;
  bottom: 0;
  width: 240px;
  background-color: var(--bg-surface);
  border-right: 1px solid var(--border-subtle);
  transition: transform var(--transition-normal);
  z-index: 90;
}

.sidebar-collapsed {
  transform: translateX(-240px);
}

.nav-menu {
  padding: var(--space-3) 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-item {
  display: block;
  padding: var(--space-3) var(--space-5);
  color: var(--text-secondary);
  text-decoration: none;
  font-size: var(--text-sm);
  font-weight: 500;
  border-radius: 0;
  margin: 0 var(--space-2);
  border-radius: var(--radius-md);
  transition: background-color var(--transition-fast), color var(--transition-fast);
}

.nav-item:hover {
  background-color: var(--color-muted);
  color: var(--text-primary);
}

.nav-item.router-link-active {
  background-color: var(--color-muted);
  color: var(--text-primary);
  font-weight: 600;
}

/* 主内容区 */
.main-content {
  margin-top: 60px;
  margin-left: 240px;
  padding: var(--space-5);
  flex: 1;
  background-color: var(--bg-canvas);
  transition: margin-left var(--transition-normal);
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

  .user-name {
    display: none;
  }
}
</style>