<template>
  <Teleport to="body">
    <div v-if="showLoginModal || showRegisterModal" class="auth-modal-overlay" @click.self="closeCurrent">
      <div class="auth-modal-card">
        <button class="auth-modal-close" @click="closeCurrent" aria-label="关闭">
          <span class="material-symbols-outlined">close</span>
        </button>

        <!-- 登录 -->
        <template v-if="showLoginModal">
          <div class="auth-modal-header">
            <span class="material-symbols-outlined auth-modal-logo">smart_toy</span>
            <h2 class="auth-modal-title">登录</h2>
            <p class="auth-modal-subtitle">登录后可使用历史记录与个人设置</p>
          </div>
          <form class="auth-form" @submit.prevent="handleLogin">
            <div class="form-group">
              <label>用户名</label>
              <div class="input-wrapper">
                <span class="material-symbols-outlined input-icon">person</span>
                <input v-model="loginUsername" type="text" placeholder="请输入用户名" required />
              </div>
            </div>
            <div class="form-group">
              <label>密码</label>
              <div class="input-wrapper">
                <span class="material-symbols-outlined input-icon">lock</span>
                <input
                  v-model="loginPassword"
                  :type="showLoginPw ? 'text' : 'password'"
                  placeholder="请输入密码"
                  required
                />
                <span class="material-symbols-outlined toggle-pw" @click="showLoginPw = !showLoginPw">
                  {{ showLoginPw ? 'visibility_off' : 'visibility' }}
                </span>
              </div>
            </div>
            <button type="submit" class="submit-btn" :disabled="loginLoading">
              <span v-if="loginLoading" class="spinner"></span>
              {{ loginLoading ? '登录中...' : '登录' }}
            </button>
            <p v-if="loginError" class="error-msg">{{ loginError }}</p>
          </form>
          <p class="auth-switch">
            还没有账号？
            <a href="#" @click.prevent="openRegisterModal">立即注册</a>
          </p>
        </template>

        <!-- 注册 -->
        <template v-else-if="showRegisterModal">
          <div class="auth-modal-header">
            <span class="material-symbols-outlined auth-modal-logo">smart_toy</span>
            <h2 class="auth-modal-title">注册</h2>
            <p class="auth-modal-subtitle">注册后可使用历史记录与个人设置</p>
          </div>
          <form class="auth-form" @submit.prevent="handleRegister">
            <div class="form-group">
              <label>用户名</label>
              <div class="input-wrapper">
                <span class="material-symbols-outlined input-icon">person</span>
                <input v-model="regUsername" type="text" placeholder="2-64 个字符" required />
              </div>
            </div>
            <div class="form-group">
              <label>密码</label>
              <div class="input-wrapper">
                <span class="material-symbols-outlined input-icon">lock</span>
                <input
                  v-model="regPassword"
                  :type="showRegPw ? 'text' : 'password'"
                  placeholder="至少 6 位"
                  required
                />
                <span class="material-symbols-outlined toggle-pw" @click="showRegPw = !showRegPw">
                  {{ showRegPw ? 'visibility_off' : 'visibility' }}
                </span>
              </div>
            </div>
            <div class="form-group">
              <label>姓名</label>
              <div class="input-wrapper">
                <span class="material-symbols-outlined input-icon">badge</span>
                <input v-model="regName" type="text" placeholder="您的姓名" required />
              </div>
            </div>
            <div class="form-group">
              <label>邮箱（选填）</label>
              <div class="input-wrapper">
                <span class="material-symbols-outlined input-icon">email</span>
                <input v-model="regEmail" type="email" placeholder="your@email.com" />
              </div>
            </div>
            <button type="submit" class="submit-btn" :disabled="regLoading">
              <span v-if="regLoading" class="spinner"></span>
              {{ regLoading ? '注册中...' : '注册' }}
            </button>
            <p v-if="regError" class="error-msg">{{ regError }}</p>
          </form>
          <p class="auth-switch">
            已有账号？
            <a href="#" @click.prevent="openLoginModal">去登录</a>
          </p>
        </template>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import axios from 'axios'
import {
  setAuth,
  showLoginModal,
  showRegisterModal,
  closeLoginModal,
  closeRegisterModal,
  openLoginModal,
  openRegisterModal,
} from '../stores/authStore'

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'

function closeCurrent() {
  closeLoginModal()
  closeRegisterModal()
}

const loginUsername = ref('')
const loginPassword = ref('')
const showLoginPw = ref(false)
const loginLoading = ref(false)
const loginError = ref('')

const regUsername = ref('')
const regPassword = ref('')
const regName = ref('')
const regEmail = ref('')
const showRegPw = ref(false)
const regLoading = ref(false)
const regError = ref('')

watch([showLoginModal, showRegisterModal], () => {
  loginError.value = ''
  regError.value = ''
})

function normalizeApiErrorDetail(detail: unknown): string {
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail.length > 0) {
    const first = detail[0]
    if (first && typeof first === 'object' && 'msg' in first) return String((first as { msg: string }).msg)
    return String(detail[0])
  }
  if (detail && typeof detail === 'object' && 'msg' in detail) return String((detail as { msg: string }).msg)
  return '登录失败，请检查用户名和密码'
}

async function handleLogin() {
  loginError.value = ''
  loginLoading.value = true
  try {
    const res = await axios.post(`${API_URL}/auth/login`, {
      username: loginUsername.value.trim(),
      password: loginPassword.value,
    })
    const data = res.data
    const token = data?.access_token
    const userId = data?.user_id != null ? Number(data.user_id) : null
    if (token && userId != null) {
      setAuth(token, {
        user_id: userId,
        username: (data.username ?? '').toString(),
        name: (data.name ?? '用户').toString(),
      })
      closeCurrent()
    } else {
      loginError.value = '登录返回数据异常，请重试'
    }
  } catch (err: any) {
    const detail = err.response?.data?.detail
    loginError.value = detail != null ? normalizeApiErrorDetail(detail) : (err.message || '网络异常，请检查后端是否启动')
  } finally {
    loginLoading.value = false
  }
}

async function handleRegister() {
  regError.value = ''
  if (regPassword.value.length < 6) {
    regError.value = '密码至少 6 位'
    return
  }
  regLoading.value = true
  try {
    const res = await axios.post(`${API_URL}/auth/register`, {
      username: regUsername.value.trim(),
      password: regPassword.value,
      name: regName.value.trim(),
      email: regEmail.value.trim() || undefined,
    })
    const data = res.data
    const token = data?.access_token
    const userId = data?.user_id != null ? Number(data.user_id) : null
    if (token && userId != null) {
      setAuth(token, {
        user_id: userId,
        username: (data.username ?? '').toString(),
        name: (data.name ?? '用户').toString(),
      })
      closeCurrent()
    } else {
      regError.value = '注册返回数据异常，请重试'
    }
  } catch (err: any) {
    const detail = err.response?.data?.detail
    regError.value = detail != null ? normalizeApiErrorDetail(detail) : (err.message || '网络异常，请检查后端是否启动')
  } finally {
    regLoading.value = false
  }
}
</script>

<style scoped>
.auth-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100000;
}
.auth-modal-card {
  position: relative;
  width: 100%;
  max-width: 400px;
  margin: 1rem;
  padding: 2rem;
  background: #1a2332;
  border: 1px solid #232f48;
  border-radius: 1rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}
.auth-modal-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  padding: 0.25rem;
  color: #94a3b8;
  background: none;
  border: none;
  cursor: pointer;
}
.auth-modal-close:hover {
  color: #e2e8f0;
}
.auth-modal-header {
  margin-bottom: 1.5rem;
}
.auth-modal-logo {
  font-size: 2rem;
  color: #135bec;
  display: block;
  margin-bottom: 0.5rem;
}
.auth-modal-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 0.25rem 0;
}
.auth-modal-subtitle {
  font-size: 0.875rem;
  color: #94a3b8;
  margin: 0;
}
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}
.form-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #cbd5e1;
}
.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}
.input-icon {
  position: absolute;
  left: 0.75rem;
  color: #94a3b8;
  font-size: 1.125rem;
}
.input-wrapper input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border-radius: 0.5rem;
  border: 1px solid #334155;
  background: #0f172a;
  color: #e2e8f0;
  font-size: 0.875rem;
}
.input-wrapper input:focus {
  outline: none;
  border-color: #135bec;
}
.toggle-pw {
  position: absolute;
  right: 0.75rem;
  color: #94a3b8;
  cursor: pointer;
}
.submit-btn {
  width: 100%;
  padding: 0.75rem;
  background: #135bec;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}
.submit-btn:hover:not(:disabled) {
  background: #1d64f2;
}
.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
.spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid transparent;
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
.error-msg {
  color: #ef4444;
  font-size: 0.875rem;
  margin: 0;
  text-align: center;
}
.auth-switch {
  margin-top: 1rem;
  text-align: center;
  font-size: 0.875rem;
  color: #94a3b8;
}
.auth-switch a {
  color: #135bec;
  text-decoration: none;
}
.auth-switch a:hover {
  text-decoration: underline;
}
</style>
