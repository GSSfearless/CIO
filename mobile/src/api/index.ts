import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Sentry from 'sentry-expo';

// API基础URL
// 开发环境下使用localhost，生产环境使用实际域名
const API_BASE_URL = __DEV__ 
  ? 'http://localhost:3000/api/v1'
  : 'https://your-production-domain.com/api/v1';

// 创建axios实例
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 添加认证token
api.interceptors.request.use(
  async (config) => {
    try {
      const token = await AsyncStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (error) {
      console.error('获取token失败:', error);
    }
    return config;
  },
  (error) => {
    Sentry.captureException(error);
    return Promise.reject(error);
  }
);

// 响应拦截器 - 处理错误和刷新token
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    // 处理401错误 - token过期
    if (error.response && error.response.status === 401) {
      try {
        // 尝试刷新token
        const refreshToken = await AsyncStorage.getItem('refreshToken');
        if (!refreshToken) {
          // 没有刷新token，需要重新登录
          await AsyncStorage.removeItem('token');
          return Promise.reject(error);
        }

        // 使用刷新token获取新token
        const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refreshToken,
        });

        if (response.data.token) {
          await AsyncStorage.setItem('token', response.data.token);
          
          // 使用新token重试之前的请求
          error.config.headers.Authorization = `Bearer ${response.data.token}`;
          return axios(error.config);
        }
      } catch (refreshError) {
        // 刷新token失败，需要重新登录
        await AsyncStorage.removeItem('token');
        await AsyncStorage.removeItem('refreshToken');
        Sentry.captureException(refreshError);
      }
    }

    // 捕获其他API错误
    if (error.response) {
      Sentry.captureException(error);
    }

    return Promise.reject(error);
  }
);

export default api; 