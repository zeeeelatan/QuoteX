<template>
  <header class="branch-page-header">
    <div class="header-left">
      <router-link to="/" class="logo-link">
        <div class="logo-wrapper">
          <span class="material-symbols-outlined">smart_toy</span>
        </div>
        <h2 class="header-title">AI 智能报价系统</h2>
      </router-link>
    </div>
    <SharedNavigation @open-product-database="$emit('openProductDatabase')" />
    <div class="header-right">
      <button class="icon-btn notification-btn">
        <span class="material-symbols-outlined">notifications</span>
        <span class="notification-dot"></span>
      </button>
      <div class="divider"></div>
      <template v-if="isLoggedInRef">
        <div class="user-info" ref="userInfoRef" @click="toggleUserMenu">
          <div
            class="user-avatar"
            :style="userProfile.avatar ? { backgroundImage: `url(${userProfile.avatar})`, backgroundSize: 'cover' } : {}"
          ></div>
          <div class="user-details">
            <span class="user-name">{{ userProfile.name || '用户' }}</span>
            <span class="user-role">{{ userProfile.position || '高级销售经理' }}</span>
          </div>
          <span class="material-symbols-outlined dropdown-arrow" :class="{ expanded: isUserMenuOpen }">expand_more</span>
        </div>
        <Teleport to="body">
          <div v-if="isUserMenuOpen" class="user-dropdown-menu" :style="userDropdownStyle">
            <div class="dropdown-header">
              <div
                class="dropdown-avatar"
                :style="userProfile.avatar ? { backgroundImage: `url(${userProfile.avatar})`, backgroundSize: 'cover' } : {}"
              ></div>
              <div class="dropdown-info">
                <span class="dropdown-name">{{ userProfile.name || '用户' }}</span>
                <span class="dropdown-role">{{ userProfile.position || '高级销售经理' }}</span>
              </div>
            </div>
            <div class="dropdown-divider"></div>
            <a href="#" class="dropdown-item" @click.prevent="navigateToSystemSettings">
              <span class="material-symbols-outlined">settings</span>
              <span>系统设置</span>
            </a>
            <a href="#" class="dropdown-item" @click.prevent="navigateToPersonalSettings">
              <span class="material-symbols-outlined">person</span>
              <span>个人设置</span>
            </a>
            <div class="dropdown-divider"></div>
            <a href="#" class="dropdown-item logout-item" @click.prevent="handleLogout">
              <span class="material-symbols-outlined">logout</span>
              <span>退出登录</span>
            </a>
          </div>
        </Teleport>
      </template>
      <template v-else>
        <div class="auth-buttons">
          <button type="button" class="auth-btn register" @click="openRegisterModal">注册</button>
          <button type="button" class="auth-btn login" @click="openLoginModal">登录</button>
        </div>
      </template>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import axios from 'axios'
import SharedNavigation from './SharedNavigation.vue'
import { clearAuth, isLoggedIn, isLoggedInRef, openLoginModal, openRegisterModal } from '../stores/authStore'
import { openSystemSettings, openPersonalSettings } from '../stores/settingsDialogStore'

defineEmits<{
  openProductDatabase: []
}>()

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'

const userProfile = ref({
  name: '',
  position: '',
  avatar: ''
})

async function loadUserProfile() {
  if (!isLoggedIn()) return
  try {
    const res = await axios.get(`${API_URL}/user-profile/`)
    if (res.data) {
      userProfile.value.name = res.data.name || '用户'
      userProfile.value.position = res.data.position || '高级销售经理'
      userProfile.value.avatar = res.data.avatar || ''
    }
  } catch (err) {
    console.error('加载用户资料失败', err)
  }
}

const isUserMenuOpen = ref(false)
const userInfoRef = ref<HTMLElement | null>(null)
const userDropdownPosition = ref({ top: 0, right: 0 })

function updateUserDropdownPosition() {
  if (userInfoRef.value) {
    const rect = userInfoRef.value.getBoundingClientRect()
    userDropdownPosition.value = {
      top: rect.bottom + window.scrollY + 8,
      right: window.innerWidth - rect.right
    }
  }
}

const userDropdownStyle = computed(() => ({
  position: 'fixed',
  top: `${userDropdownPosition.value.top}px`,
  right: `${userDropdownPosition.value.right}px`
}))

function toggleUserMenu() {
  isUserMenuOpen.value = !isUserMenuOpen.value
  if (isUserMenuOpen.value) {
    nextTick(updateUserDropdownPosition)
  }
}

function navigateToSystemSettings() {
  openSystemSettings()
  isUserMenuOpen.value = false
}

function navigateToPersonalSettings() {
  openPersonalSettings()
  isUserMenuOpen.value = false
}

function handleLogout() {
  isUserMenuOpen.value = false
  clearAuth()
}

function handleClickOutsideUserMenu(event: MouseEvent) {
  const target = event.target as Node
  const isClickInsideUserInfo = userInfoRef.value?.contains(target)
  const isClickInsideDropdown = (target as HTMLElement).closest?.('.user-dropdown-menu')
  if (!isClickInsideUserInfo && !isClickInsideDropdown) {
    isUserMenuOpen.value = false
  }
}

onMounted(() => {
  if (isLoggedIn()) loadUserProfile()
  document.addEventListener('click', handleClickOutsideUserMenu)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutsideUserMenu)
})
</script>

<style scoped>
.branch-page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #232f48;
  background-color: #101622;
  padding: 1rem 1.5rem;
  position: sticky;
  top: 0;
  z-index: 50;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
  color: inherit;
  transition: opacity 0.2s;
}

.logo-link:hover {
  opacity: 0.8;
}

.logo-wrapper {
  width: 2rem;
  height: 2rem;
  color: #135bec;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(19, 91, 236, 0.1);
  border-radius: 0.5rem;
}

.header-title {
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: -0.015em;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.icon-btn {
  position: relative;
  color: #94a3b8;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  transition: color 0.2s;
}

.icon-btn:hover {
  color: #135bec;
}

.notification-dot {
  position: absolute;
  top: 0;
  right: 0;
  width: 0.5rem;
  height: 0.5rem;
  background-color: #ef4444;
  border-radius: 9999px;
}

.divider {
  height: 2rem;
  width: 1px;
  background-color: #232f48;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 0.5rem;
  transition: background-color 0.2s;
}

.user-info:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

.user-avatar {
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 9999px;
  background-color: #1e293b;
  background-repeat: no-repeat;
  background-position: center;
}

.user-details {
  display: none;
  flex-direction: column;
}

@media (min-width: 1024px) {
  .user-details {
    display: flex;
  }
}

.user-name {
  font-size: 0.875rem;
  font-weight: 500;
  line-height: 1;
  color: white;
}

.user-role {
  font-size: 0.75rem;
  color: #94a3b8;
  margin-top: 0.25rem;
}

.dropdown-arrow {
  font-size: 1.25rem;
  color: #94a3b8;
  transition: transform 0.2s;
}

.dropdown-arrow.expanded {
  transform: rotate(180deg);
}

/* 用户下拉菜单 - Teleport 到 body，需确保选择器能命中 */
.user-dropdown-menu {
  min-width: 16rem;
  background-color: #151e32;
  border: 1px solid #232f48;
  border-radius: 0.75rem;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
  z-index: 99999;
  overflow: hidden;
  animation: branchHeaderDropdownFadeIn 0.2s ease-out;
}

@keyframes branchHeaderDropdownFadeIn {
  from {
    opacity: 0;
    transform: translateY(-0.5rem);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dropdown-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  border-bottom: 1px solid #232f48;
}

.dropdown-avatar {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 9999px;
  background-color: #1e293b;
  background-repeat: no-repeat;
  background-position: center;
}

.dropdown-info {
  display: flex;
  flex-direction: column;
}

.dropdown-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: white;
}

.dropdown-role {
  font-size: 0.75rem;
  color: #94a3b8;
}

.dropdown-divider {
  height: 1px;
  background-color: #232f48;
  margin: 0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  color: #cbd5e1;
  text-decoration: none;
  font-size: 0.875rem;
  transition: all 0.2s;
  cursor: pointer;
}

.dropdown-item:hover {
  background-color: rgba(19, 91, 236, 0.1);
  color: #135bec;
}

.dropdown-item .material-symbols-outlined {
  font-size: 1.125rem;
}

.dropdown-item.logout-item {
  color: #ef4444;
}

.dropdown-item.logout-item:hover {
  background-color: rgba(239, 68, 68, 0.1);
  color: #f87171;
}

.auth-buttons {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.auth-btn {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}
.auth-btn.register {
  color: #94a3b8;
  background: transparent;
}
.auth-btn.register:hover {
  color: #e2e8f0;
  background: rgba(255, 255, 255, 0.05);
}
.auth-btn.login {
  color: white;
  background: #135bec;
}
.auth-btn.login:hover {
  background: #1d64f2;
}
</style>
