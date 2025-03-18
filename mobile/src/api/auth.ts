import api from './index';

// 登录接口
export const login = (credentials: { email: string; password: string }) => {
  return api.post('/auth/login', credentials);
};

// 注册接口
export const register = (userData: { email: string; password: string; name: string }) => {
  return api.post('/auth/register', userData);
};

// 登出接口
export const logout = () => {
  return api.post('/auth/logout');
};

// 重置密码接口
export const resetPassword = (email: string) => {
  return api.post('/auth/reset-password', { email });
};

// 更新密码接口
export const updatePassword = (data: { token: string; password: string }) => {
  return api.post('/auth/update-password', data);
};

// 获取当前用户信息
export const getCurrentUser = () => {
  return api.get('/auth/me');
};

// 更新用户资料
export const updateProfile = (data: { name?: string; avatar?: string }) => {
  return api.put('/auth/profile', data);
}; 