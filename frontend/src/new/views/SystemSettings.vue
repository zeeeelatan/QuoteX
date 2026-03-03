<template>
  <div class="system-settings-page">
    <div class="page-header">
      <div class="header-left">
        <button class="back-btn" @click="emit('go-home')">
          <span class="material-symbols-outlined">arrow_back</span>
        </button>
        <div class="title-section">
          <h1 class="page-title">个人配置</h1>
          <p class="page-subtitle">管理您的个人档案、联系方式及安全设置</p>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn-primary" @click="saveChanges">
          <span class="material-symbols-outlined">save</span>
          保存更改
        </button>
      </div>
    </div>

    <!-- Content Cards -->
    <div class="content-cards">
      <!-- Avatar Section -->
      <div class="content-card">
        <div class="avatar-section">
          <div class="avatar-preview-group">
            <div class="avatar-preview-wrapper" @click="triggerAvatarUpload">
              <div class="avatar-preview" :style="{ backgroundImage: userAvatar }"></div>
              <div class="avatar-overlay">
                <span class="material-symbols-outlined">photo_camera</span>
              </div>
            </div>
            <div class="avatar-info">
              <p class="avatar-title">当前头像</p>
              <p class="avatar-hint">支持 JPG, PNG 格式，最大 2MB</p>
            </div>
          </div>
          <input type="file" ref="avatarInputRef" accept="image/jpeg,image/png" @change="handleAvatarUpload" style="display: none" />
          <button class="btn-secondary" @click="triggerAvatarUpload">更换头像</button>
        </div>
      </div>

      <!-- Basic Info Form -->
      <div class="content-card">
        <h3 class="card-title">
          <span class="material-symbols-outlined card-icon">badge</span>
          基本信息
        </h3>
        <div class="form-grid">
          <div class="form-field">
            <label class="form-label">昵称</label>
            <input class="form-input" type="text" v-model="userSettings.nickname" placeholder="请输入昵称" />
          </div>
          <div class="form-field">
            <label class="form-label">职位头衔</label>
            <div class="input-readonly-wrapper">
              <input class="form-input readonly" type="text" v-model="userSettings.position" readonly />
              <span class="material-symbols-outlined lock-icon">lock</span>
            </div>
            <p class="form-hint">职位信息由管理员同步，不可自行修改</p>
          </div>
          <div class="form-field full-width">
            <label class="form-label">个人简介</label>
            <textarea class="form-textarea" v-model="userSettings.bio" placeholder="介绍一下你自己..." rows="3"></textarea>
          </div>
        </div>
      </div>

      <!-- Contact & Security -->
      <div class="form-row">
        <!-- Contact Info -->
        <div class="content-card">
          <h3 class="card-title">
            <span class="material-symbols-outlined card-icon">contact_mail</span>
            联系方式
          </h3>
          <div class="form-fields-compact">
            <div class="form-field">
              <label class="form-label">邮箱地址</label>
              <div class="input-group">
                <input class="form-input" type="email" v-model="userSettings.email" />
                <button class="btn-small">验证</button>
              </div>
            </div>
            <div class="form-field">
              <label class="form-label">手机号码</label>
              <div class="input-group">
                <input class="form-input readonly" type="tel" :value="maskedPhone" readonly />
                <button class="btn-small" @click="showPhoneEdit = true">修改</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Security Settings -->
        <div class="content-card">
          <h3 class="card-title">
            <span class="material-symbols-outlined card-icon">shield</span>
            安全设置
          </h3>
          <div class="security-settings">
            <div class="security-item">
              <div class="security-info">
                <span class="security-label">登录密码</span>
                <span class="security-hint">上次修改：3个月前</span>
              </div>
              <button class="text-btn">修改</button>
            </div>
            <div class="security-item">
              <div class="security-info">
                <span class="security-label">两步验证 (2FA)</span>
                <span class="security-hint">保护账号安全</span>
              </div>
              <label class="toggle-switch">
                <input class="toggle-input" type="checkbox" v-model="userSettings.twoFactorEnabled" />
                <div class="toggle-slider"></div>
              </label>
            </div>
          </div>
          <div class="security-footer">
            <button class="danger-btn" @click="logoutAllDevices">
              <span class="material-symbols-outlined">logout</span>
              退出登录所有设备
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast Notification -->
    <div v-if="toast.show" class="toast" :class="toast.type">
      <span class="material-symbols-outlined">{{ toast.icon }}</span>
      <span>{{ toast.message }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const emit = defineEmits<{
  'go-home': []
}>()

// Default avatar
const defaultAvatar = 'https://lh3.googleusercontent.com/aida-public/AB6AXuDseCis7eFPMlDsQTxa4UJDQM0NaKbsbzofX_Mi6TN-2xaKyvlZNIdhkEFOwDBGB-i9nyiKt_NQD_35zysXqWHkzZ1g_Oa3kEvGx2sb3ejxv6cNjGMZy4lnRDsdxNPUiWc_prmCaIHLfF4Z4uWq6Aua_NaQNnlZcaRLwtmBA_DCPh4w-3ZlGOxjmYBBeAOUTKU7GMGNP_LP6ZNHsJ-RUTNwKT09JUOkVgy_JtGHYy5R-69NvRGPNBF7wSBzFWbiltzFmwPA-IUJ34Y'

// State
const avatarInputRef = ref<HTMLInputElement | null>(null)
const showPhoneEdit = ref(false)

const userSettings = ref({
  nickname: 'Alex Zhang',
  position: '销售经理',
  bio: '',
  email: 'alex.zhang@example.com',
  phone: '138****8888',
  twoFactorEnabled: false
})

const toast = ref({
  show: false,
  message: '',
  type: 'success',
  icon: 'check_circle'
})

// Computed
const userAvatar = computed(() => {
  const savedAvatar = localStorage.getItem('user_avatar')
  return `url("${savedAvatar || defaultAvatar}")`
})

const maskedPhone = computed(() => {
  return userSettings.value.phone
})

// Functions
function triggerAvatarUpload() {
  avatarInputRef.value?.click()
}

function handleAvatarUpload(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return

  // Validate file size (2MB)
  if (file.size > 2 * 1024 * 1024) {
    showToast('图片大小不能超过 2MB', 'error')
    return
  }

  // Validate file type
  if (!['image/jpeg', 'image/png'].includes(file.type)) {
    showToast('只支持 JPG、PNG 格式', 'error')
    return
  }

  // Read and save avatar
  const reader = new FileReader()
  reader.onload = (e) => {
    const result = e.target?.result as string
    localStorage.setItem('user_avatar', result)
    showToast('头像更新成功')
  }
  reader.readAsDataURL(file)
}

function cancelChanges() {
  // Reload from storage
  loadUserSettings()
  showToast('已取消更改', 'success')
}

function saveChanges() {
  // Save to localStorage
  localStorage.setItem('user_settings', JSON.stringify(userSettings.value))
  showToast('保存成功', 'success')
}

function logoutAllDevices() {
  if (confirm('确定要退出登录所有设备吗？')) {
    localStorage.clear()
    sessionStorage.clear()
    showToast('已退出所有设备', 'success')
    setTimeout(() => {
      emit('go-home')
    }, 1500)
  }
}

function showToast(message: string, type: 'success' | 'error' = 'success') {
  toast.value = {
    show: true,
    message,
    type,
    icon: type === 'success' ? 'check_circle' : 'error'
  }
  setTimeout(() => {
    toast.value.show = false
  }, 3000)
}

function loadUserSettings() {
  const saved = localStorage.getItem('user_settings')
  if (saved) {
    try {
      userSettings.value = { ...userSettings.value, ...JSON.parse(saved) }
    } catch (e) {
      console.error('Failed to load user settings:', e)
    }
  }
}

onMounted(() => {
  loadUserSettings()
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+SC:wght@300;400;500;700;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

.system-settings-page {
  font-family: "Inter", "Noto Sans SC", sans-serif;
  background-color: #0B1120;
  color: #ffffff;
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 1.5rem 2rem;
  overflow-y: auto;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.back-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.5rem;
  background-color: #151e32;
  border: 1px solid #232f48;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s;
}

.back-btn:hover {
  background-color: #232f48;
  color: white;
}

.back-btn .material-symbols-outlined {
  font-size: 1.25rem;
}

.title-section {
  display: flex;
  flex-direction: column;
}

.page-title {
  font-size: 1.875rem;
  font-weight: 700;
  color: white;
}

.page-subtitle {
  font-size: 0.875rem;
  color: #92a4c9;
  margin-top: 0.125rem;
}

/* Content Cards */
.content-cards {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.content-card {
  background-color: #232f48;
  border-radius: 0.75rem;
  padding: 1.5rem;
  border: 1px solid #2d3b59;
}

.card-title {
  color: #ffffff;
  font-size: 1.125rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.card-icon {
  color: #135bec;
  font-size: 1.25rem;
}

/* Avatar Section */
.avatar-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

@media (min-width: 768px) {
  .avatar-section {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
}

.avatar-preview-group {
  display: flex;
  gap: 1.25rem;
  align-items: center;
}

.avatar-preview-wrapper {
  position: relative;
  cursor: pointer;
}

.avatar-preview {
  width: 6rem;
  height: 6rem;
  border-radius: 9999px;
  background-position: center;
  background-repeat: no-repeat;
  background-size: cover;
  border: 4px solid #0B1120;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
}

.avatar-overlay {
  position: absolute;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}

.avatar-preview-wrapper:hover .avatar-overlay {
  opacity: 1;
}

.avatar-overlay .material-symbols-outlined {
  color: #ffffff;
  font-size: 1.5rem;
}

.avatar-info {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.avatar-title {
  color: #ffffff;
  font-size: 1.125rem;
  font-weight: 700;
  line-height: normal;
}

.avatar-hint {
  color: #92a4c9;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

/* Buttons */
.btn-secondary {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
  height: 2.5rem;
  padding: 0 1.5rem;
  background-color: #111722;
  border: 1px solid #3e4c6b;
  color: #ffffff;
  font-size: 0.875rem;
  font-weight: 700;
  transition: all 0.2s;
  width: 100%;
}

@media (min-width: 768px) {
  .btn-secondary {
    width: auto;
  }
}

.btn-secondary:hover {
  background-color: #1c263a;
}

.btn-primary {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  border-radius: 0.5rem;
  height: 2.75rem;
  padding: 0 2rem;
  background-color: #135bec;
  border: none;
  color: #ffffff;
  font-size: 0.875rem;
  font-weight: 700;
  transition: all 0.2s;
  box-shadow: 0 0 15px rgba(19, 91, 236, 0.3);
}

.btn-primary:hover {
  background-color: #1e40af;
}

.btn-small {
  padding: 0 1rem;
  height: 2.75rem;
  border-radius: 0.5rem;
  background-color: #2d3b59;
  color: #ffffff;
  font-size: 0.875rem;
  font-weight: 500;
  transition: background-color 0.2s;
  white-space: nowrap;
}

.btn-small:hover {
  background-color: #3e4c6b;
}

.text-btn {
  background: none;
  border: none;
  color: #135bec;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: color 0.2s;
}

.text-btn:hover {
  color: #60a5fa;
}

/* Form */
.form-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

@media (min-width: 768px) {
  .form-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-field.full-width {
  grid-column: 1 / -1;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #92a4c9;
}

.form-input {
  width: 100%;
  background-color: #111722;
  border: 1px solid #3e4c6b;
  border-radius: 0.5rem;
  height: 2.75rem;
  padding: 0 1rem;
  color: #ffffff;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #135bec;
  box-shadow: 0 0 0 1px rgba(19, 91, 236, 0.5);
}

.form-input::placeholder {
  color: #5e6e8c;
}

.form-input.readonly {
  background-color: rgba(17, 23, 34, 0.5);
  color: #92a4c9;
  cursor: not-allowed;
}

.form-textarea {
  width: 100%;
  background-color: #111722;
  border: 1px solid #3e4c6b;
  border-radius: 0.5rem;
  padding: 1rem;
  color: #ffffff;
  font-size: 0.875rem;
  resize: none;
  transition: all 0.2s;
}

.form-textarea:focus {
  outline: none;
  border-color: #135bec;
  box-shadow: 0 0 0 1px rgba(19, 91, 236, 0.5);
}

.form-textarea::placeholder {
  color: #5e6e8c;
}

.form-hint {
  font-size: 0.75rem;
  color: #5e6e8c;
  margin-top: 0.25rem;
}

.input-readonly-wrapper {
  position: relative;
}

.input-readonly-wrapper .lock-icon {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #5e6e8c;
  font-size: 0.875rem;
}

.input-readonly-wrapper .form-input {
  padding-right: 2.5rem;
}

.input-group {
  display: flex;
  gap: 0.5rem;
}

.input-group .form-input {
  flex: 1;
}

.form-fields-compact {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Form Row */
.form-row {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

@media (min-width: 768px) {
  .form-row {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Security Settings */
.security-settings {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.security-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem;
  border-radius: 0.5rem;
  background-color: #111722;
  border: 1px solid #2d3b59;
}

.security-info {
  display: flex;
  flex-direction: column;
}

.security-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #ffffff;
}

.security-hint {
  font-size: 0.75rem;
  color: #5e6e8c;
}

/* Toggle Switch */
.toggle-switch {
  position: relative;
  display: inline-block;
  width: 2.25rem;
  height: 1.25rem;
  cursor: pointer;
}

.toggle-input {
  position: absolute;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.toggle-slider {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #3e4c6b;
  border-radius: 9999px;
  transition: 0.3s;
}

.toggle-slider::before {
  position: absolute;
  content: '';
  height: 1rem;
  width: 1rem;
  left: 0.125rem;
  bottom: 0.125rem;
  background-color: #ffffff;
  border-radius: 9999px;
  transition: 0.3s;
}

.toggle-input:checked + .toggle-slider {
  background-color: #135bec;
}

.toggle-input:checked + .toggle-slider::before {
  transform: translateX(1rem);
}

/* Security Footer */
.security-footer {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #2d3b59;
}

.danger-btn {
  width: 100%;
  padding: 0.5rem;
  color: #ef4444;
  background: transparent;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.danger-btn:hover {
  background-color: rgba(239, 68, 68, 0.1);
}

/* Toast Notification */
.toast {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  background-color: #1e293b;
  border-radius: 0.5rem;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
  z-index: 100;
  animation: slideIn 0.3s ease-out;
}

.toast.success {
  border-left: 4px solid #22c55e;
}

.toast.error {
  border-left: 4px solid #ef4444;
}

.toast .material-symbols-outlined {
  font-size: 1.25rem;
}

.toast.success .material-symbols-outlined {
  color: #22c55e;
}

.toast.error .material-symbols-outlined {
  color: #ef4444;
}

@keyframes slideIn {
  from {
    transform: translateY(100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* Custom Scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #111722;
}

::-webkit-scrollbar-thumb {
  background: #232f48;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #3e4c6b;
}
</style>
