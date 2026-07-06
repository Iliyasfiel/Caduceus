<!--
Caduceus 应用布局组件
提供响应式侧边栏导航和顶部栏（Vercel 风格 token 化）
侧边栏采用 GitHub 风格 drawer：默认收起，汉堡按钮触发浮层弹出 + 全屏遮罩
-->
<template>
  <div class="app-layout">
    <!-- 顶部栏 -->
    <header class="header">
      <button
        class="menu-toggle"
        @click="toggleSidebar"
        :aria-label="sidebarCollapsed ? '打开菜单' : '关闭菜单'"
        :aria-expanded="!sidebarCollapsed"
      >
        <UiIcon :name="sidebarCollapsed ? 'menu' : 'close'" :size="20" class="menu-icon" />
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

    <!-- 全屏遮罩（drawer 打开时显示，点击关闭） -->
    <Transition name="overlay-fade">
      <div
        v-if="!sidebarCollapsed"
        class="sidebar-overlay"
        @click="closeSidebar"
        aria-hidden="true"
      />
    </Transition>

    <!-- 侧边栏 drawer：默认 translateX(-100%) 隐藏在屏幕外，展开时回到 0 -->
    <aside class="sidebar" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <nav class="nav-menu">
        <router-link to="/" class="nav-item" @click="closeSidebar">仪表盘</router-link>
        <router-link to="/tasks" class="nav-item" @click="closeSidebar">任务列表</router-link>
        <router-link to="/pipeline" class="nav-item" @click="closeSidebar">管线编辑器</router-link>
        <router-link to="/resources" class="nav-item" @click="closeSidebar">资源库</router-link>
        <router-link to="/admin" class="nav-item" @click="closeSidebar">管理面板</router-link>
      </nav>
    </aside>

    <!-- 主内容区：始终 width: 100%，与 sidebar 状态完全无关，零重排 -->
    <main class="main-content">
      <slot />
    </main>
  </div>
</template>

<script setup>
/**
 * AppLayout 脚本：业务逻辑零改动（auth store / 登出全部保留）。
 * 侧边栏改为 GitHub 风格 drawer：
 * - 默认收起（hidden offscreen），不参与主内容布局
 * - 汉堡按钮 / ESC / 点击遮罩 / 点击菜单项 触发关闭
 * - main 始终 width: 100%，header 内元素零抖动
 */
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import NotificationBell from '@/components/NotificationBell.vue'
import { UiButton, UiThemeToggle, UiIcon } from '@/components/ui'

const authStore = useAuthStore()
const user = computed(() => authStore.user)

// 侧边栏状态：默认收起（true = collapsed）
const sidebarCollapsed = ref(true)

// 切换 / 关闭侧边栏
function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

function closeSidebar() {
  sidebarCollapsed.value = true
}

// ESC 键关闭：drawer 打开时按下 ESC 收起
function handleKeydown(e) {
  if (e.key === 'Escape' && !sidebarCollapsed.value) {
    closeSidebar()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})

// 登出
function handleLogout() {
  authStore.performLogout()
}
</script>

<style scoped>
.app-layout {
  display: block;
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

/* 侧边栏 drawer
 *
 * fixed 浮层，始终在屏幕左侧：
 * - 默认 sidebar-collapsed → transform: translateX(-100%) 隐藏在屏幕外
 * - 展开 → transform: translateX(0) 显示
 * 不参与 main 布局，main 始终 width: 100%
 */
.sidebar {
  position: fixed;
  top: 60px;
  left: 0;
  bottom: 0;
  width: 240px;
  background-color: var(--bg-surface);
  border-right: 1px solid var(--border-subtle);
  box-shadow: var(--shadow-lg);
  transition: transform var(--transition-normal);
  z-index: 95;
}

.sidebar.sidebar-collapsed {
  transform: translateX(-100%);
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

/* 全屏遮罩
 *
 * 统一深色半透明 rgba(0, 0, 0, 0.5)，light / dark 主题都用同一颜色。
 * 通过 opacity + Transition 实现淡入淡出（v-if 控制元素存在）。
 * z-index 介于 header(100) 与 sidebar(95) 之间，但点击优先级高于 sidebar 链接（因为它绝对定位覆盖全屏）。
 */
.sidebar-overlay {
  position: fixed;
  top: 60px;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 90;
}

/* 遮罩淡入淡出 */
.overlay-fade-enter-active,
.overlay-fade-leave-active {
  transition: opacity var(--transition-normal);
}

.overlay-fade-enter-from,
.overlay-fade-leave-to {
  opacity: 0;
}

/* 主内容区
 *
 * 始终 width: 100%，margin-left: 0，**与 sidebar 状态完全无关**。
 * sidebar 是 drawer 浮层，不占空间，因此 main 不会因为 sidebar 状态变化而重排。
 * header 内 logo / 通知铃铛 / 用户菜单位置稳定。
 */
.main-content {
  margin-top: 60px;
  margin-left: 0;
  padding: var(--space-5);
  width: 100%;
  box-sizing: border-box;
  background-color: var(--bg-canvas);
}
</style>