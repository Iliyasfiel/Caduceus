<!--
Caduceus 根组件
作为整个应用的容器，渲染路由视图 + 全局 Toast 容器
样式一律由 tokens.css / base.css 提供，本文件不写硬编码值。
-->
<template>
  <router-view />
  <UiToast />
</template>

<script setup>
/**
 * 根组件脚本：Toast 容器常驻，业务侧通过 useToast() 调用。
 */
import { UiToast, UiConfirm } from '@/components/ui'
</script>

<style>
/* 全局基础样式已迁移到 src/styles/base.css，本文件留空 */
</style>