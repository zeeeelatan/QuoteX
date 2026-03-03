<template>
  <router-view />
  <AuthModal />
  <SettingsDialog />
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import AuthModal from './components/AuthModal.vue'
import SettingsDialog from './components/SettingsDialog.vue'
import { initAxiosAuth, clearAuth, getToken, openLoginModal } from './stores/authStore'

onMounted(() => {
  initAxiosAuth()
  axios.interceptors.response.use(
    (res) => res,
    (err) => {
      if (err.response?.status === 401) {
        if (getToken()) clearAuth()
        ElMessage.warning(err.response?.data?.detail || '此功能需要登录，请点击右上角登录')
        openLoginModal()
      }
      return Promise.reject(err)
    }
  )
})
</script>

<style scoped></style>
