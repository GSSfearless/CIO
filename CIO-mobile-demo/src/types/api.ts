// 用户相关接口
export interface User {
  id: string;
  username: string;
  email: string;
  avatar?: string;
  createdAt: string;
  updatedAt: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface AuthResponse {
  user: User;
  token: string;
}

// 查询相关接口
export interface Query {
  id: string;
  userId: string;
  content: string;
  response?: string;
  reasoning?: string;
  createdAt: string;
  updatedAt: string;
  focusPointIds?: string[];
}

export interface CreateQueryRequest {
  content: string;
  focusPointIds?: string[];
  showReasoning?: boolean;
}

// 关注点相关接口
export interface FocusPoint {
  id: string;
  userId: string;
  title: string;
  description?: string;
  tags?: string[];
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface CreateFocusPointRequest {
  title: string;
  description?: string;
  tags?: string[];
}

export interface UpdateFocusPointRequest {
  title?: string;
  description?: string;
  tags?: string[];
  isActive?: boolean;
}

// 信息源相关接口
export interface Source {
  id: string;
  userId: string;
  name: string;
  type: 'rss' | 'web' | 'api';
  url: string;
  refreshInterval?: number;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface CreateSourceRequest {
  name: string;
  type: 'rss' | 'web' | 'api';
  url: string;
  refreshInterval?: number;
}

export interface UpdateSourceRequest {
  name?: string;
  url?: string;
  refreshInterval?: number;
  isActive?: boolean;
}

// 通用响应接口
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
} 