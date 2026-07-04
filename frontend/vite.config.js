/**
 * Caduceus 前端 Vite 配置
 * 配置 Vue 插件、API 代理和构建选项
 */
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      // 设置 @ 别名指向 src 目录，方便导入
      '@': path.resolve(__dirname, 'src')
    }
  },
  server: {
    port: 3000,
    // 开发环境代理配置，将 API 和 WebSocket 请求转发到后端
    proxy: {
      // REST API 代理
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      // WebSocket 代理
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false
  }
})