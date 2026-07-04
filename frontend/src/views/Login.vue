<!--
Caduceus 登录页面
表单结构改用 UiInput / UiButton；视觉风格与 Vercel 设计令牌一致。
业务逻辑（auth 调用 / 跳转）保持不变。
-->
<template>
  <div class="login-page">
    <div class="login-page__topbar">
      <UiThemeToggle />
    </div>
    <div class="login-card">
      <header class="login-card__brand">
        <div class="login-card__logo" aria-hidden="true">C</div>
        <h1 class="login-card__title">Caduceus</h1>
        <p class="login-card__subtitle">协同工作平台</p>
      </header>

      <form class="login-card__form" @submit.prevent="handleLogin">
        <UiInput
          v-model="username"
          label="用户名"
          placeholder="请输入用户名"
          autocomplete="username"
          required
        />
        <UiInput
          v-model="password"
          label="密码"
          type="password"
          placeholder="请输入密码"
          autocomplete="current-password"
          required
        />

        <UiButton
          type="submit"
          variant="primary"
          size="lg"
          :loading="loading"
          block
        >
          {{ loading ? '登录中…' : '登录' }}
        </UiButton>

        <p v-if="error" class="login-card__error">{{ error }}</p>
      </form>
    </div>
  </div>
</template>

<script setup>
/**
 * Caduceus 登录页面脚本
 * 业务逻辑零改动：表单状态、auth 调用、登录后跳转逻辑保持原状。
 */
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { UiButton, UiInput } from '@/components/ui'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// 表单数据（双向绑定到 UiInput，modelValue / update:modelValue 行为与原生 input 一致）
const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

// 处理登录
async function handleLogin() {
  loading.value = true
  error.value = ''

  const success = await authStore.performLogin(username.value, password.value)

  if (success) {
    // 登录成功，跳转到目标页面
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } else {
    error.value = '登录失败，请检查用户名和密码'
  }

  loading.value = false
}
</script>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: var(--bg-canvas);
  padding: var(--space-6);
}

.login-card {
  width: 100%;
  max-width: 400px;
  background-color: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  padding: var(--space-12) var(--space-8);
  box-shadow: var(--shadow-md);
}

.login-card__brand {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-8);
}

.login-card__logo {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  background-color: var(--color-primary);
  color: var(--color-primary-foreground);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: var(--text-lg);
}

.login-card__title {
  font-size: var(--text-2xl);
  font-weight: 600;
  color: var(--text-primary);
}

.login-card__subtitle {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.login-card__form {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.login-card__error {
  margin-top: var(--space-2);
  font-size: var(--text-sm);
  color: var(--color-destructive);
  text-align: center;
}
</style>