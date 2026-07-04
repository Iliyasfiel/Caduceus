<!--
Caduceus 根组件
作为整个应用的容器，渲染路由视图
-->
<template>
  <router-view />
</template>

<script setup>
// 根组件无需额外逻辑，路由视图会根据当前路由渲染对应页面
</script>

<style>
/* 全局样式 */
:root {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  font-size: 16px;
  line-height: 1.5;
  color: #213547;
  background-color: #ffffff;
}

body {
  margin: 0;
  min-height: 100vh;
}

#app {
  width: 100%;
  min-height: 100vh;
}
</style>