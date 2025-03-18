import api from './client';
import { AuthResponse, LoginRequest, RegisterRequest, User } from '../types/api';

// 认证相关API
const authApi = {
  // 用户登录
  login: (data: LoginRequest) => 
    api.post<AuthResponse>('/auth/login', data),
  
  // 用户注册
  register: (data: RegisterRequest) => 
    api.post<AuthResponse>('/auth/register', data),
  
  // 获取当前用户信息
  getCurrentUser: () => 
    api.get<User>('/auth/me'),
  
  // 退出登录
  logout: () => {
    // 清除本地存储的token
    localStorage.removeItem('token');
    return Promise.resolve({ success: true });
  },
  
  // 保存token到本地存储
  saveToken: (token: string) => {
    localStorage.setItem('token', token);
  },
  
  // 获取token
  getToken: () => {
    return localStorage.getItem('token');
  },
  
  // 检查是否已登录
  isAuthenticated: () => {
    return !!localStorage.getItem('token');
  },
};

export default authApi; 