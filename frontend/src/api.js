import axios from 'axios';

// 简化API配置，仅支持本地开发场景
let API_URL;

// 优先使用 Vite 环境变量配置（例如 http://localhost:5002）
const ENV_API_URL = import.meta.env?.VITE_API_BASE_URL;

// 先尝试自动获取当前访问地址的主机名和协议
const currentProtocol = window.location.protocol;
const currentHostname = window.location.hostname;

// 如果是通过IP访问，则使用当前IP作为API地址
if (currentHostname !== 'localhost' && currentHostname !== '127.0.0.1') {
  // 使用当前主机名，但端口跟随环境变量（未配置则默认5001）
  const envPort = (() => {
    try {
      if (!ENV_API_URL) return null
      return new URL(ENV_API_URL).port || null
    } catch {
      return null
    }
  })()
  API_URL = `${currentProtocol}//${currentHostname}:${envPort || '5001'}`;
} else {
  // 本地环境
  API_URL = ENV_API_URL || 'http://localhost:5002';
}

console.log('当前使用的API地址:', API_URL);

// 创建axios实例
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  // 禁用凭证，避免CORS问题
  withCredentials: false,
  // 增加超时时间以支持批量匹配大量数据
  timeout: 60000,
});

// 简单的响应拦截器
api.interceptors.response.use(
  response => response,
  error => {
    if (error.message.includes('timeout')) {
      console.error('API请求超时，请检查后端服务是否正常运行');
    } else if (error.response) {
      console.error(`API错误: ${error.response.status} - ${JSON.stringify(error.response.data)}`);
    } else {
      console.error('API请求失败:', error.message);
    }
    return Promise.reject(error);
  }
);

export const matchDevices = async (devices) => {
  try {
    const response = await api.post('/bulk-match/', { items: devices });
    return response.data;
  } catch (error) {
    console.error('匹配设备错误:', error);
    throw error;
  }
};

export const searchDevice = async (model) => {
  try {
    const response = await api.get(`/devices/search/?model=${encodeURIComponent(model)}`);
    return response.data;
  } catch (error) {
    console.error('搜索设备错误:', error);
    throw error;
  }
};

export default api;