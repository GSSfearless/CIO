import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { API_BASE_URL } from '../config';
import { ApiResponse } from '../types/api';

// 创建axios实例
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 从本地存储获取token
    const token = localStorage.getItem('token');
    
    // 如果有token，添加到请求头
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // 处理401错误（未授权）
    if (error.response && error.response.status === 401) {
      // 清除本地存储的token
      localStorage.removeItem('token');
      
      // 重定向到登录页面
      // 在实际应用中，这里可能需要使用导航库进行重定向
    }
    
    return Promise.reject(error);
  }
);

// 通用请求方法
export const request = async <T>(
  config: AxiosRequestConfig
): Promise<ApiResponse<T>> => {
  try {
    const response: AxiosResponse = await apiClient(config);
    
    return {
      success: true,
      data: response.data,
    };
  } catch (error: any) {
    return {
      success: false,
      error: error.response?.data?.message || error.message || '未知错误',
    };
  }
};

// 导出常用请求方法
export const api = {
  get: <T>(url: string, params?: any) => 
    request<T>({ method: 'GET', url, params }),
  
  post: <T>(url: string, data?: any) => 
    request<T>({ method: 'POST', url, data }),
  
  put: <T>(url: string, data?: any) => 
    request<T>({ method: 'PUT', url, data }),
  
  delete: <T>(url: string) => 
    request<T>({ method: 'DELETE', url }),
};

export default api; 