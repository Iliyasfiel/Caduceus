<!--
UiIcon：图标基础组件
集中管理项目内全部线性 outline 图标（Lucide 风格 24×24 viewBox）
- 通过 name 传入图标名；size / stroke-width / aria-label 可覆盖
- 默认 currentColor 跟父级文字色，自动适配 light / dark 主题
- 默认 aria-hidden="true"，由父级按钮等提供语义
-->
<template>
  <span class="ui-icon" :style="iconStyle" aria-hidden="true">
    <svg
      xmlns="http://www.w3.org/2000/svg"
      :width="size"
      :height="size"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      :stroke-width="strokeWidth"
      stroke-linecap="round"
      stroke-linejoin="round"
      v-html="path"
    />
  </span>
</template>

<script setup>
/**
 * UiIcon 脚本：内部维护一个图标名注册表（path 数组）。
 * - 添加新图标：在 PATHS 中新增条目即可，无需新增文件
 * - 体积控制：图标数量在几十个以内，build 时会被 tree-shaking + gzip 压缩
 */
import { computed } from 'vue'

const props = defineProps({
  name: { type: String, required: true },          // 图标名，对应 PATHS 中的 key
  size: { type: [Number, String], default: 20 },   // 像素或数字（不带单位）
  strokeWidth: { type: [Number, String], default: 1.75 }
})

/**
 * 全部线性 outline 图标（Lucide 同款 path data，24×24 viewBox）
 * 单一来源：新增图标只在这里加；如需扩展（如 logo 等复杂图形）请单独建组件。
 */
const PATHS = {
  bell: '<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/>',
  menu: '<line x1="4" y1="6" x2="20" y2="6"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="18" x2="20" y2="18"/>',
  close: '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
  sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/>',
  moon: '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>',
  system: '<rect x="3" y="4" width="18" height="12" rx="2" ry="2"/><line x1="8" y1="20" x2="16" y2="20"/><line x1="12" y1="16" x2="12" y2="20"/>',
  check: '<polyline points="20 6 9 17 4 12"/>',
  x: '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
  info: '<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>',
  warning: '<path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
  clipboard: '<path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/>'
}

const path = computed(() => PATHS[props.name] || '')

const iconStyle = computed(() => ({
  // 行内块避免父级基线导致 SVG 下方多 1~2px 空隙
  display: 'inline-flex',
  alignItems: 'center',
  justifyContent: 'center',
  lineHeight: 0
}))
</script>

<style scoped>
.ui-icon {
  /* 容器只负责布局，颜色由 currentColor 透传给 svg */
  color: inherit;
}

.ui-icon :deep(svg) {
  display: block;
}
</style>