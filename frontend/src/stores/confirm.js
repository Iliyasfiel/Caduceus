/**
 * Confirm Store
 *
 * 全局确认弹窗队列（同一时刻只支持一个 confirm）。
 * 用法：
 *   const ok = await useConfirm()({ title, message, tone, confirmText, cancelText })
 *
 * tone: danger（默认，红色） | warning | info
 */
import { defineStore } from 'pinia'
import { reactive } from 'vue'

export const useConfirmStore = defineStore('confirm', {
  state: () => ({
    state: reactive({
      visible: false,
      title: '',
      message: '',
      tone: 'danger',
      confirmText: '确定',
      cancelText: '取消',
      loading: false
    }),
    _resolver: null
  }),

  actions: {
    resolve(result) {
      if (this._resolver) {
        this._resolver(result)
        this._resolver = null
      }
      this.state.visible = false
    },

    open(opts) {
      // 如果已经有一个 confirm 在显示，先 reject 它（异常保护）
      if (this._resolver) {
        this._resolver(false)
        this._resolver = null
      }
      Object.assign(this.state, {
        visible: true,
        title: opts.title || '确认操作',
        message: opts.message || '',
        tone: opts.tone || 'danger',
        confirmText: opts.confirmText || '确定',
        cancelText: opts.cancelText || '取消',
        loading: false
      })
      return new Promise((resolve) => {
        this._resolver = resolve
      })
    }
  }
})

/**
 * useConfirm composable：业务侧便捷调用。
 * 返回函数直接调用，返回 Promise<boolean>。
 */
export function useConfirm() {
  const store = useConfirmStore()
  return (opts) => store.open(opts)
}