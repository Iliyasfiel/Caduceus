/**
 * Theme Store
 *
 * 管理三态主题：light / dark / system
 * - mode='system'：跟随 OS 的 prefers-color-scheme，不写 data-theme
 * - mode='light'  ：写 data-theme='light'，强制亮色
 * - mode='dark'   ：写 data-theme='dark'，强制暗色
 *
 * 选择持久化在 localStorage（key: caduceus.theme）。
 */
import { defineStore } from 'pinia'

const STORAGE_KEY = 'caduceus.theme'

function readStored() {
  try {
    const v = localStorage.getItem(STORAGE_KEY)
    return v === 'light' || v === 'dark' || v === 'system' ? v : 'system'
  } catch {
    return 'system'
  }
}

/**
 * 把 store 中的 mode 同步到 <html data-theme="...">。
 * 'system' 模式移除属性，让 CSS @media (prefers-color-scheme: dark) 自然生效。
 */
function applyToDom(mode) {
  const root = document.documentElement
  if (mode === 'system') {
    root.removeAttribute('data-theme')
  } else {
    root.setAttribute('data-theme', mode)
  }
}

export const useThemeStore = defineStore('theme', {
  state: () => ({
    /** 'light' | 'dark' | 'system' */
    mode: 'system'
  }),

  getters: {
    /** 当前实际生效的明暗，用于按钮图标判断 */
    resolved(state) {
      if (state.mode !== 'system') return state.mode
      if (typeof window === 'undefined') return 'light'
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    }
  },

  actions: {
    /**
     * 应用启动时调用一次：从 localStorage 恢复 + 监听系统偏好变化。
     */
    init() {
      this.mode = readStored()
      applyToDom(this.mode)

      // system 模式下，OS 切换深浅色时实时跟随
      const mq = window.matchMedia('(prefers-color-scheme: dark)')
      const onSystemChange = () => {
        if (this.mode === 'system') applyToDom('system')
      }
      // Safari < 14 用 addListener；现代浏览器用 addEventListener
      if (mq.addEventListener) mq.addEventListener('change', onSystemChange)
      else if (mq.addListener) mq.addListener(onSystemChange)
    },

    /**
     * 切换三态：light → dark → system → light …
     */
    cycle() {
      const next = this.mode === 'light' ? 'dark' : this.mode === 'dark' ? 'system' : 'light'
      this.setMode(next)
    },

    /**
     * 直接设置模式
     */
    setMode(mode) {
      if (mode !== 'light' && mode !== 'dark' && mode !== 'system') return
      this.mode = mode
      try { localStorage.setItem(STORAGE_KEY, mode) } catch { /* 隐私模式可能写失败，忽略 */ }
      applyToDom(mode)
    }
  }
})