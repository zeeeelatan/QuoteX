<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-form-wrapper">
        <div class="auth-content">
          <div class="branding">
            <div class="logo-wrapper">
              <span class="material-symbols-outlined">smart_toy</span>
            </div>
            <span class="brand-name">AI 智能报价</span>
          </div>
          <h1 class="page-title">用户注册</h1>
          <p class="page-subtitle">注册后可使用历史记录与个人设置</p>

          <form class="auth-form" @submit.prevent="handleRegister">
            <div class="form-group">
              <label for="username">用户名</label>
              <div class="input-wrapper">
                <span class="material-symbols-outlined input-icon">person</span>
                <input
                  id="username"
                  v-model="username"
                  type="text"
                  placeholder="2-64 个字符"
                  autocomplete="username"
                  required
                />
              </div>
            </div>
            <div class="form-group">
              <label for="password">密码</label>
              <div class="input-wrapper">
                <span class="material-symbols-outlined input-icon">lock</span>
                <input
                  id="password"
                  v-model="password"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="至少 6 位"
                  autocomplete="new-password"
                  required
                />
                <span class="material-symbols-outlined toggle-password" @click="showPassword = !showPassword">
                  {{ showPassword ? 'visibility_off' : 'visibility' }}
                </span>
              </div>
            </div>
            <div class="form-group">
              <label for="name">姓名</label>
              <div class="input-wrapper">
                <span class="material-symbols-outlined input-icon">badge</span>
                <input
                  id="name"
                  v-model="name"
                  type="text"
                  placeholder="您的姓名"
                  required
                />
              </div>
            </div>
            <div class="form-group">
              <label for="email">邮箱（选填）</label>
              <div class="input-wrapper">
                <span class="material-symbols-outlined input-icon">email</span>
                <input
                  id="email"
                  v-model="email"
                  type="email"
                  placeholder="your@email.com"
                />
              </div>
            </div>

            <button type="submit" class="submit-btn" :disabled="loading">
              <span v-if="loading" class="loading-spinner"></span>
              {{ loading ? '注册中...' : '注册' }}
            </button>
            <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
          </form>

          <p class="footer-link">
            已有账号？
            <router-link to="/login">去登录</router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { setAuth } from '../stores/authStore'

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'

const router = useRouter()
const username = ref('')
const password = ref('')
const name = ref('')
const email = ref('')
const showPassword = ref(false)
const loading = ref(false)
const errorMessage = ref('')

async function handleRegister() {
  errorMessage.value = ''
  if (password.value.length < 6) {
    errorMessage.value = '密码至少 6 位'
    return
  }
  loading.value = true
  try {
    const res = await axios.post(`${API_URL}/auth/register`, {
      username: username.value.trim(),
      password: password.value,
      name: name.value.trim(),
      email: email.value.trim() || undefined,
    })
    const data = res.data
    setAuth(data.access_token, {
      user_id: data.user_id,
      username: data.username,
      name: data.name,
    })
    router.replace('/')
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || '注册失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #101622;
}
.auth-container {
  width: 100%;
  max-width: 420px;
  padding: 2rem;
}
.auth-form-wrapper {
  background-color: #1a2332;
  border: 1px solid #232f48;
  border-radius: 1rem;
  padding: 2.5rem;
}
.branding {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}
.logo-wrapper {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.5rem;
  background-color: #135bec;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}
.logo-wrapper .material-symbols-outlined { font-size: 1.5rem; }
.brand-name { font-size: 1.25rem; font-weight: 700; color: #e2e8f0; }
.page-title { font-size: 1.75rem; font-weight: 700; color: #f1f5f9; margin-bottom: 0.25rem; }
.page-subtitle { font-size: 0.875rem; color: #94a3b8; margin-bottom: 1.5rem; }
.auth-form { display: flex; flex-direction: column; gap: 1.25rem; }
.form-group { display: flex; flex-direction: column; gap: 0.5rem; }
.form-group label { font-size: 0.875rem; font-weight: 500; color: #cbd5e1; }
.input-wrapper { position: relative; display: flex; align-items: center; }
.input-icon { position: absolute; left: 1rem; color: #94a3b8; font-size: 1.25rem; }
.input-wrapper input {
  width: 100%;
  padding: 0.875rem 1rem 0.875rem 2.75rem;
  border-radius: 0.5rem;
  border: 1px solid #334155;
  background-color: #0f172a;
  color: #e2e8f0;
  font-size: 0.875rem;
}
.input-wrapper input:focus {
  outline: none;
  border-color: #135bec;
}
.toggle-password { position: absolute; right: 1rem; color: #94a3b8; cursor: pointer; }
.submit-btn {
  width: 100%;
  padding: 0.875rem;
  background-color: #135bec;
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
.submit-btn:hover:not(:disabled) { background-color: #1d64f2; }
.submit-btn:disabled { opacity: 0.7; cursor: not-allowed; }
.loading-spinner {
  width: 1rem; height: 1rem;
  border: 2px solid transparent;
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.error-message { color: #ef4444; font-size: 0.875rem; text-align: center; }
.footer-link { margin-top: 1.5rem; text-align: center; font-size: 0.875rem; color: #94a3b8; }
.footer-link a { color: #135bec; text-decoration: none; }
.footer-link a:hover { text-decoration: underline; }
</style>
