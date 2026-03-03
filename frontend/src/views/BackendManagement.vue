<template>
  <div class="backend-management">
    <div class="menu-container">
      <el-menu mode="horizontal" :default-active="activeMenu" @select="handleMenuSelect" class="backend-menu">
        <el-menu-item index="rate-management">费率管理</el-menu-item>
        <el-menu-item index="service-level">服务级别管理</el-menu-item>
        <el-menu-item index="gpu-price">GPU价格管理</el-menu-item>
      </el-menu>
    </div>
    <div class="content-container">
      <router-view v-slot="{ Component }">
        <keep-alive>
          <component :is="Component" />
        </keep-alive>
      </router-view>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const activeMenu = ref('rate-management')

// 处理菜单选择
const handleMenuSelect = (key) => {
  router.push(`/backend-management/${key}`)
}

// 根据当前路由设置活动菜单
onMounted(() => {
  const path = route.path.split('/')
  const currentPath = path[path.length - 1]
  activeMenu.value = currentPath || 'rate-management'
  
  // 如果是根路径，重定向到费率管理
  if (path.length <= 2) {
    router.push('/backend-management/rate-management')
  }
})
</script>

<style scoped>
.backend-management {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.menu-container {
  padding: 0 24px;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.content-container {
  flex: 1;
  padding: 24px;
  overflow: auto;
}

.backend-menu {
  border-bottom: none;
}
</style> 