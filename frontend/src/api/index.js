import axios from 'axios'
import { ElMessage } from 'element-plus'

// 动态检测后端 API 地址
function detectApiBaseUrl() {
  const envUrl = import.meta.env?.VITE_API_BASE_URL
  // 构建时注入的环境变量优先（生产环境为 /api，走 nginx 代理）
  if (envUrl) return envUrl
  // 本地开发：通过 IP 访问时直连后端，localhost 走 Vite 代理
  const hostname = window.location.hostname
  if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
    return `${window.location.protocol}//${hostname}:5002`
  }
  return '/api'
}

// 创建 axios 实例
const api = axios.create({
  baseURL: detectApiBaseUrl(),
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 从 localStorage 读取 token 并附加到请求头
    const token = localStorage.getItem('quotation_access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    // 如果请求标记了 silentError，不弹出错误提示（由调用方自行处理）
    if (!error.config?.silentError) {
      console.error('响应错误:', error)
      ElMessage.error(error.response?.data?.detail || error.response?.data?.message || '请求失败')
    }
    return Promise.reject(error)
  }
)

export default api 