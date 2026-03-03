<template>
  <nav class="shared-nav">
    <router-link to="/" class="nav-item" :class="{ active: isActive('/') }">
      <span class="material-symbols-outlined">home</span>
      <span class="nav-text">首页概览</span>
    </router-link>
    <a href="#" class="nav-item" :class="{ active: isActive('/product-database') }" @click.prevent="openProductDatabase">
      <span class="material-symbols-outlined">inventory_2</span>
      <span class="nav-text">产品数据库</span>
    </a>
    <router-link to="/quote-history" class="nav-item" :class="{ active: isActive('/quote-history') }">
      <span class="material-symbols-outlined">history</span>
      <span class="nav-text">历史记录</span>
    </router-link>
    <a href="#" class="nav-item" @click.prevent="handleOpenSystemSettings">
      <span class="material-symbols-outlined">settings</span>
      <span class="nav-text">系统设置</span>
    </a>
  </nav>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { openSystemSettings } from '../stores/settingsDialogStore'

const emit = defineEmits<{
  openProductDatabase: []
}>()

const route = useRoute()

function isActive(path: string): boolean {
  // 移除末尾斜杠进行比较
  const currentPath = route.path.endsWith('/') && route.path !== '/'
    ? route.path.slice(0, -1)
    : route.path
  const targetPath = path.endsWith('/') && path !== '/'
    ? path.slice(0, -1)
    : path
  return currentPath === targetPath
}

function openProductDatabase() {
  emit('openProductDatabase')
}

function handleOpenSystemSettings() {
  openSystemSettings()
}
</script>

<style scoped>
.shared-nav {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.875rem;
  border-radius: 0.5rem;
  color: #94a3b8;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s;
  white-space: nowrap;
  cursor: pointer;
}

.nav-item:hover {
  color: #ffffff;
  background-color: rgba(255, 255, 255, 0.05);
}

.nav-item.active {
  color: #135bec;
  background-color: rgba(19, 91, 236, 0.1);
}

.nav-item .material-symbols-outlined {
  font-size: 1.125rem;
}

.nav-text {
  font-size: 0.875rem;
}

@media (max-width: 768px) {
  .shared-nav {
    display: none;
  }

  .nav-text {
    display: none;
  }

  .nav-item .material-symbols-outlined {
    font-size: 1.25rem;
  }
}
</style>
