<template>
  <div class="admin-login">
    <div class="login-container">
      <!-- Left Column: Login Form -->
      <div class="login-form-wrapper">
        <div class="login-content">
          <!-- Branding -->
          <div class="branding">
            <div class="logo-wrapper">
              <span class="material-symbols-outlined">smart_toy</span>
            </div>
            <span class="brand-name">AI Quoting Sys</span>
          </div>
          <h1 class="page-title">智能AI报价系统</h1>
          <p class="page-subtitle">后台管理登录</p>

          <!-- Login Form -->
          <form class="login-form" @submit.prevent="handleLogin">
            <div class="form-group">
              <label for="username">用户名</label>
              <div class="input-wrapper">
                <span class="material-symbols-outlined input-icon">person</span>
                <input
                  id="username"
                  v-model="username"
                  type="text"
                  placeholder="请输入用户名"
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
                  placeholder="请输入密码"
                  autocomplete="current-password"
                  required
                />
                <span class="material-symbols-outlined toggle-password" @click="showPassword = !showPassword">
                  {{ showPassword ? 'visibility_off' : 'visibility' }}
                </span>
              </div>
            </div>

            <div class="form-actions">
              <label class="remember-me">
                <input type="checkbox" v-model="rememberMe" />
                <span>记住密码</span>
              </label>
              <a href="#" class="forgot-link">忘记密码?</a>
            </div>

            <button type="submit" class="login-btn" :disabled="loading">
              <span v-if="loading" class="loading-spinner"></span>
              {{ loading ? '登录中...' : '立即登录' }}
            </button>

            <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
          </form>

          <p class="copyright">
            © 2024 AI Quoting System. All rights reserved.<br />
            Powered by Intelligent Neural Networks
          </p>
        </div>
      </div>

      <!-- Right Column: Visual -->
      <div class="visual-side">
        <div class="overlay"></div>
        <img
          src="https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop"
          alt="AI Background"
          class="bg-image"
        />
        <div class="quote-overlay">
          <blockquote>
            <p>"智能化算法驱动，让商业报价从未如此精准高效。"</p>
            <footer>—— 系统管理员公告</footer>
          </blockquote>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const username = ref('')
const password = ref('')
const showPassword = ref(false)
const rememberMe = ref(false)
const loading = ref(false)
const errorMessage = ref('')

// Load saved credentials
onMounted(() => {
  const savedUsername = localStorage.getItem('admin_username')
  const savedPassword = localStorage.getItem('admin_password')
  if (savedUsername) username.value = savedUsername
  if (savedPassword) {
    password.value = savedPassword
    rememberMe.value = true
  }
})

async function handleLogin() {
  errorMessage.value = ''
  loading.value = true

  // Simple validation (in production, this should call an API)
  if (username.value && password.value) {
    // Simulate API call
    setTimeout(() => {
      // For demo, accept any username/password
      // In production, validate against backend
      if (password.value.length >= 4) {
        // Save credentials if remember me is checked
        if (rememberMe.value) {
          localStorage.setItem('admin_username', username.value)
          localStorage.setItem('admin_password', password.value)
        } else {
          localStorage.removeItem('admin_username')
          localStorage.removeItem('admin_password')
        }

        // Set login state
        localStorage.setItem('admin_logged_in', 'true')
        localStorage.setItem('admin_username_display', username.value)

        // Redirect to dashboard
        router.push('/admin/dashboard')
      } else {
        errorMessage.value = '用户名或密码错误'
      }
      loading.value = false
    }, 500)
  } else {
    errorMessage.value = '请输入用户名和密码'
    loading.value = false
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+SC:wght@300;400;500;700;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

.admin-login {
  font-family: "Inter", "Noto Sans SC", sans-serif;
  background-color: #101622;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.admin-login :deep(body) {
  background-color: #101622;
}

.login-container {
  display: flex;
  width: 100%;
  min-height: 100vh;
}

/* Left Side - Form */
.login-form-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 3rem 2rem;
  max-width: 600px;
}

.login-content {
  width: 100%;
  max-width: 400px;
  display: flex;
  flex-direction: column;
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
  box-shadow: 0 10px 15px -3px rgba(19, 91, 236, 0.3);
}

.logo-wrapper .material-symbols-outlined {
  font-size: 1.5rem;
}

.brand-name {
  font-size: 1.25rem;
  font-weight: 700;
  color: #e2e8f0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: #f1f5f9;
  margin-bottom: 0.5rem;
}

.page-subtitle {
  font-size: 1.125rem;
  color: #94a3b8;
  margin-bottom: 2rem;
}

/* Form */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
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
  left: 1rem;
  color: #94a3b8;
  font-size: 1.25rem;
  pointer-events: none;
}

.input-wrapper input {
  width: 100%;
  padding: 1rem 1rem 1rem 3rem;
  border-radius: 0.5rem;
  border: 1px solid #334155;
  background-color: #1e293b;
  color: #e2e8f0;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.input-wrapper input:focus {
  outline: none;
  border-color: #135bec;
  box-shadow: 0 0 0 3px rgba(19, 91, 236, 0.1);
}

.input-wrapper input::placeholder {
  color: #64748b;
}

.toggle-password {
  position: absolute;
  right: 1rem;
  color: #94a3b8;
  cursor: pointer;
  transition: color 0.2s;
}

.toggle-password:hover {
  color: #475569;
}

.form-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #94a3b8;
  cursor: pointer;
}

.remember-me input {
  width: 1rem;
  height: 1rem;
  cursor: pointer;
}

.forgot-link {
  font-size: 0.875rem;
  color: #135bec;
  text-decoration: none;
  transition: color 0.2s;
}

.forgot-link:hover {
  color: #1d64f2;
}

.login-btn {
  width: 100%;
  padding: 1rem;
  background-color: #135bec;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.login-btn:hover:not(:disabled) {
  background-color: #1d64f2;
  box-shadow: 0 10px 15px -3px rgba(19, 91, 236, 0.25);
}

.login-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loading-spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid transparent;
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-message {
  color: #ef4444;
  font-size: 0.875rem;
  text-align: center;
  padding: 0.5rem;
}

.copyright {
  margin-top: 2.5rem;
  text-align: center;
  font-size: 0.75rem;
  color: #64748b;
  line-height: 1.5;
}

/* Right Side - Visual */
.visual-side {
  display: none;
  position: relative;
  flex: 1;
  background-color: #192233;
}

@media (min-width: 1024px) {
  .visual-side {
    display: block;
  }
}

.overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom right, rgba(19, 91, 236, 0.2), transparent, rgba(16, 22, 34, 0.8));
  z-index: 10;
}

.bg-image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0.9;
}

.quote-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 3rem;
  z-index: 20;
  background: linear-gradient(to top, #101622, #101622 80%, transparent);
}

.quote-overlay blockquote {
  max-width: 400px;
}

.quote-overlay p {
  font-size: 1.125rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 0.5rem;
}

.quote-overlay footer {
  font-size: 0.875rem;
  color: #135bec;
  font-weight: 600;
}

</style>
