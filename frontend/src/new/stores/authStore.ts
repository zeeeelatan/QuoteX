/**
 * 用户认证状态：token、当前用户信息，与 localStorage 同步
 * 用于请求头鉴权、路由守卫、按用户隔离缓存 key
 */
import { ref, computed } from 'vue'
import axios from 'axios'

const TOKEN_KEY = 'quotation_access_token'
const USER_KEY = 'quotation_user'

export interface AuthUser {
  user_id: number
  username: string
  name: string
}

export interface UserProfile {
  name: string
  position: string
  avatar: string
}

function loadStored(): { token: string | null; user: AuthUser | null } {
  try {
    const token = localStorage.getItem(TOKEN_KEY)
    const raw = localStorage.getItem(USER_KEY)
    const user = raw ? (JSON.parse(raw) as AuthUser) : null
    return { token, user }
  } catch {
    return { token: null, user: null }
  }
}

const token = ref<string | null>(loadStored().token)
const user = ref<AuthUser | null>(loadStored().user)

/** 用户资料（全局缓存，避免组件重建时闪烁） */
const userProfile = ref<UserProfile>({ name: '', position: '', avatar: '' })
let profileLoaded = false

export function getUserProfile(): UserProfile {
  return userProfile.value
}

export const userProfileRef = computed(() => userProfile.value)

export async function loadUserProfile(): Promise<void> {
  if (!isLoggedIn()) return
  if (profileLoaded) return
  try {
    const API_URL = import.meta.env.VITE_API_BASE_URL || '/api'
    const res = await axios.get(`${API_URL}/user-profile/`)
    if (res.data && res.data.id && res.data.id !== 0) {
      userProfile.value = {
        name: res.data.name || '',
        position: res.data.position || '',
        avatar: res.data.avatar || '',
      }
      profileLoaded = true
    }
  } catch (err) {
    console.error('加载用户资料失败', err)
  }
}

export function refreshUserProfile(): void {
  profileLoaded = false
  loadUserProfile()
}

export function getToken(): string | null {
  return token.value
}

export function getUserId(): number | null {
  return user.value?.user_id ?? null
}

export function getUserName(): string {
  return user.value?.name ?? ''
}

export function isLoggedIn(): boolean {
  return !!token.value
}

/** 供模板用：登录态变化时视图会更新 */
export const isLoggedInRef = computed(() => !!token.value)

/** 登录/注册成功后调用，持久化 token 与用户信息 */
export function setAuth(accessToken: string, authUser: AuthUser): void {
  token.value = accessToken
  user.value = authUser
  localStorage.setItem(TOKEN_KEY, accessToken)
  localStorage.setItem(USER_KEY, JSON.stringify(authUser))
  axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`
}

/** 登出：清除 token 与用户 */
export function clearAuth(): void {
  token.value = null
  user.value = null
  userProfile.value = { name: '', position: '', avatar: '' }
  profileLoaded = false
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
  delete axios.defaults.headers.common['Authorization']
}

/** 应用启动时从 localStorage 恢复请求头 */
export function initAxiosAuth(): void {
  const t = getToken()
  if (t) axios.defaults.headers.common['Authorization'] = `Bearer ${t}`
  else delete axios.defaults.headers.common['Authorization']
}

// 登录/注册弹窗（右上角点击时打开，不强制整页登录）
export const showLoginModal = ref(false)
export const showRegisterModal = ref(false)

export function openLoginModal(): void {
  showRegisterModal.value = false
  showLoginModal.value = true
}

export function openRegisterModal(): void {
  showLoginModal.value = false
  showRegisterModal.value = true
}

export function closeLoginModal(): void {
  showLoginModal.value = false
}

export function closeRegisterModal(): void {
  showRegisterModal.value = false
}

export function useAuthModals() {
  return {
    showLoginModal,
    showRegisterModal,
    openLoginModal,
    openRegisterModal,
    closeLoginModal,
    closeRegisterModal,
  }
}

/** 用于按用户隔离的 localStorage/sessionStorage key 前缀（未登录为 guest） */
export function getStorageKeyPrefix(): string {
  const id = getUserId()
  return id != null ? `user_${id}_` : 'guest_'
}

export function useAuth() {
  return {
    token: computed(() => token.value),
    user: computed(() => user.value),
    isLoggedIn: computed(() => isLoggedIn()),
    getToken,
    getUserId,
    getUserName,
    setAuth,
    clearAuth,
    getStorageKeyPrefix,
  }
}
