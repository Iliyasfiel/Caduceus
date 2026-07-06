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
        <div
          class="user-menu"
          ref="userMenuRef"
          @mouseenter="handleMenuEnter"
          @mouseleave="handleMenuLeave"
        >
          <button
            type="button"
            class="user-trigger"
            :aria-expanded="userMenuOpen"
            aria-haspopup="true"
            @click="toggleUserMenu"
            @focus="openUserMenu"
            @blur="scheduleCloseUserMenu"
          >
            <span class="user-avatar" :title="user?.username || '用户'">
              {{ avatarText }}
            </span>
            <span class="user-name">{{ user?.username || '用户' }}</span>
            <UiIcon name="chevron-down" :size="14" class="user-caret" />
          </button>

          <Transition name="popover-fade">
            <div v-if="userMenuOpen" class="user-popover" @click.stop>
              <div class="popover-header">
                <div class="popover-avatar">{{ avatarText }}</div>
                <div class="popover-identity">
                  <div class="popover-name">{{ user?.username || '未登录用户' }}</div>
                  <div class="popover-email" v-if="user?.email">{{ user.email }}</div>
                  <div class="popover-email muted" v-else>未设置邮箱</div>
                </div>
              </div>

              <div class="popover-meta">
                <div class="popover-row">
                  <span class="popover-label">角色</span>
                  <span class="popover-value">{{ roleLabel }}</span>
                </div>
                <div class="popover-row" v-if="user?.last_login">
                  <span class="popover-label">最近登录</span>
                  <span class="popover-value">{{ formatLastLogin(user.last_login) }}</span>
                </div>
                <div class="popover-row" v-else>
                  <span class="popover-label">最近登录</span>
                  <span class="popover-value muted">首次登录</span>
                </div>
              </div>

              <div class="popover-footer">
                <button type="button" class="logout-btn" @click="handleLogout">
                  <UiIcon name="logout" :size="16" class="logout-icon" />
                  <span>退出登录</span>
                </button>
              </div>
            </div>
          </Transition>
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
 *
 * 顶部用户区改造：
 * - 移除原独立的「退出」按钮
 * - 用户名按钮作为气泡触发器，hover 弹出 / 点击也能切换
 * - 气泡内展示头像、用户名、邮箱、角色、最近登录时间
 * - 退出按钮下移到气泡底部 footer
 */
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import NotificationBell from '@/components/NotificationBell.vue'
import { UiThemeToggle, UiIcon } from '@/components/ui'

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

// ========== 用户气泡状态 ==========
const userMenuOpen = ref(false)
const userMenuRef = ref(null)
// 鼠标在触发器和气泡之间移动时不让气泡闪烁关闭
let closeTimer = null

function openUserMenu() {
  if (closeTimer) {
    clearTimeout(closeTimer)
    closeTimer = null
  }
  userMenuOpen.value = true
}

function closeUserMenu() {
  userMenuOpen.value = false
}

function toggleUserMenu() {
  if (userMenuOpen.value) {
    closeUserMenu()
  } else {
    openUserMenu()
  }
}

// hover 触发：鼠标进入立刻打开，离开用 setTimeout 延迟关闭，
// 方便鼠标从触发器移动到气泡内部时不会瞬间消失
function handleMenuEnter() {
  openUserMenu()
}

function handleMenuLeave() {
  if (closeTimer) clearTimeout(closeTimer)
  closeTimer = setTimeout(() => {
    closeUserMenu()
  }, 120)
}

// 触发器失焦时延迟关闭，确保点击气泡内按钮时能拿到事件
function scheduleCloseUserMenu(event) {
  // 相关目标是气泡内元素时，不关闭
  const next = event?.relatedTarget
  if (next && userMenuRef.value && userMenuRef.value.contains(next)) {
    return
  }
  if (closeTimer) clearTimeout(closeTimer)
  closeTimer = setTimeout(() => {
    closeUserMenu()
  }, 120)
}

// 点击页面其他区域时关闭气泡
function handleDocumentClick(event) {
  if (!userMenuOpen.value) return
  if (userMenuRef.value && !userMenuRef.value.contains(event.target)) {
    closeUserMenu()
  }
}

// 头像文字：取用户名首字符；未登录时显示 '?'
const avatarText = computed(() => {
  const name = user.value?.username
  if (!name) return '?'
  return name.trim().charAt(0).toUpperCase()
})

// 角色显示文案：兼容多种字段命名（role / is_staff / is_superuser）
const roleLabel = computed(() => {
  if (!user.value) return '访客'
  if (user.value.is_superuser) return '超级管理员'
  if (user.value.is_staff) return '管理员'
  if (user.value.role) return user.value.role
  return '普通用户'
})

// 最近登录时间格式化（容错：无效日期返回「未知」）
function formatLastLogin(value) {
  if (!value) return '未知'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '未知'
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// ESC 键关闭：drawer / 气泡同时支持
function handleKeydown(e) {
  if (e.key !== 'Escape') return
  if (!sidebarCollapsed.value) {
    closeSidebar()
  }
  if (userMenuOpen.value) {
    closeUserMenu()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
  document.addEventListener('click', handleDocumentClick)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  document.removeEventListener('click', handleDocumentClick)
  if (closeTimer) clearTimeout(closeTimer)
})

// 登出
function handleLogout() {
  closeUserMenu()
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
  position: relative;
  display: flex;
  align-items: center;
}

/* 用户气泡触发器：头像 + 用户名 + 箭头，hover 时高亮 */
.user-trigger {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: 4px 10px 4px 4px;
  border-radius: var(--radius-full);
  background: transparent;
  border: 1px solid transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: var(--text-sm);
  font-weight: 500;
  line-height: 1;
  transition:
    background-color var(--transition-fast),
    color var(--transition-fast),
    border-color var(--transition-fast);
}

.user-trigger:hover,
.user-trigger:focus-visible,
.user-trigger[aria-expanded='true'] {
  background-color: var(--color-muted);
  color: var(--text-primary);
  border-color: var(--border-subtle);
  outline: none;
}

.user-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: var(--radius-full);
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  color: var(--color-primary-foreground);
  font-size: var(--text-xs);
  font-weight: 600;
  letter-spacing: 0.02em;
  flex-shrink: 0;
}

.user-name {
  font-size: var(--text-sm);
  color: inherit;
  font-weight: 500;
  max-width: 120px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-caret {
  color: inherit;
  transition: transform var(--transition-fast);
}

.user-trigger[aria-expanded='true'] .user-caret {
  transform: rotate(180deg);
}

/* 气泡本体
 *
 * 定位：与触发器右侧对齐，顶部留出 6px 间隙（看起来像挂在 trigger 下方）
 * 尺寸：260px 宽，内部用 flex-column 自然撑开
 * 阴影：与 NotificationBell 同档 token，保证视觉一致
 */
.user-popover {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 260px;
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  z-index: 110;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 气泡顶端小三角，朝向触发器 */
.user-popover::before {
  content: '';
  position: absolute;
  top: -6px;
  right: 18px;
  width: 12px;
  height: 12px;
  background: var(--bg-surface);
  border-top: 1px solid var(--border-subtle);
  border-left: 1px solid var(--border-subtle);
  transform: rotate(45deg);
}

.popover-header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4);
  background: var(--color-muted);
}

.popover-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: var(--radius-full);
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  color: var(--color-primary-foreground);
  font-size: var(--text-base);
  font-weight: 600;
  flex-shrink: 0;
}

.popover-identity {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.popover-name {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.3;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.popover-email {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  line-height: 1.3;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.popover-email.muted {
  color: var(--text-muted);
}

.popover-meta {
  padding: var(--space-3) var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  border-bottom: 1px solid var(--border-subtle);
}

.popover-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-3);
  font-size: var(--text-xs);
}

.popover-label {
  color: var(--text-muted);
}

.popover-value {
  color: var(--text-primary);
  font-weight: 500;
  text-align: right;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.popover-value.muted {
  color: var(--text-muted);
  font-weight: 400;
}

.popover-footer {
  padding: var(--space-2);
  background: var(--bg-surface);
}

.logout-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  width: 100%;
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  background: transparent;
  border: 1px solid var(--border-subtle);
  color: var(--text-primary);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  transition:
    background-color var(--transition-fast),
    color var(--transition-fast),
    border-color var(--transition-fast);
}

.logout-btn:hover {
  background-color: var(--color-destructive);
  border-color: var(--color-destructive);
  color: var(--color-primary-foreground);
}

.logout-btn:focus-visible {
  outline: 2px solid var(--color-destructive);
  outline-offset: 1px;
}

.logout-icon {
  color: inherit;
}

/* 气泡淡入淡出 */
.popover-fade-enter-active,
.popover-fade-leave-active {
  transition:
    opacity var(--transition-fast),
    transform var(--transition-fast);
}

.popover-fade-enter-from,
.popover-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
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