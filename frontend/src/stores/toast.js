/**
 * Toast Store
 *
 * 全局轻量通知队列。
 * - toast.success/error/info/warning(msg, opts?)
 * - duration: 自动消失毫秒数（0 = 不自动消失）
 * - 不持久化到 localStorage
 */
import { defineStore } from 'pinia'

let _seq = 0

export const useToastStore = defineStore('toast', {
  state: () => ({
    list: []
  }),

  actions: {
    push(message, tone = 'info', opts = {}) {
      const id = ++_seq
      const { duration = 3000, dismissible = true } = opts
      this.list.push({ id, message, tone, dismissible })
      if (duration > 0) {
        setTimeout(() => this.remove(id), duration)
      }
      return id
    },

    remove(id) {
      this.list = this.list.filter((t) => t.id !== id)
    },

    success(msg, opts) { return this.push(msg, 'success', opts) },
    error(msg, opts)   { return this.push(msg, 'error', opts) },
    info(msg, opts)    { return this.push(msg, 'info', opts) },
    warning(msg, opts) { return this.push(msg, 'warning', opts) }
  }
})

/**
 * useToast composable：便捷写法，业务侧 import 后直接 toast.success(...)。
 */
export function useToast() {
  const store = useToastStore()
  return {
    success: (msg, opts) => store.success(msg, opts),
    error:   (msg, opts) => store.error(msg, opts),
    info:    (msg, opts) => store.info(msg, opts),
    warning: (msg, opts) => store.warning(msg, opts)
  }
}