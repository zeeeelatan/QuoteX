import axios from 'axios';

// API 地址配置
const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002';

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