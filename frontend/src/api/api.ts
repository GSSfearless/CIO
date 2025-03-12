import axios, { AxiosRequestConfig } from 'axios';
import { 
  Source, SourceCreate, SourceUpdate,
  FocusPoint, FocusPointCreate, FocusPointUpdate,
  Info, InfoCreate, InfoUpdate,
  Query, QueryRequest, QueryResponse
} from '../types';

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证令牌等
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // 处理错误响应
    return Promise.reject(error);
  }
);

// 通用API请求函数
const apiRequest = async <T>(config: AxiosRequestConfig): Promise<T> => {
  try {
    const response = await api(config);
    return response.data;
  } catch (error) {
    console.error('API请求错误:', error);
    throw error;
  }
};

// 信息源API
export const sourcesApi = {
  getAll: (params?: any) => apiRequest<Source[]>({ 
    method: 'GET', 
    url: '/sources',
    params 
  }),
  
  getById: (id: string) => apiRequest<Source>({ 
    method: 'GET', 
    url: `/sources/${id}` 
  }),
  
  create: (data: SourceCreate) => apiRequest<Source>({ 
    method: 'POST', 
    url: '/sources', 
    data 
  }),
  
  update: (id: string, data: SourceUpdate) => apiRequest<Source>({ 
    method: 'PATCH', 
    url: `/sources/${id}`, 
    data 
  }),
  
  delete: (id: string) => apiRequest<void>({ 
    method: 'DELETE', 
    url: `/sources/${id}` 
  }),
};

// 关注点API
export const focusPointsApi = {
  getAll: (params?: any) => apiRequest<FocusPoint[]>({ 
    method: 'GET', 
    url: '/focus-points',
    params 
  }),
  
  getById: (id: string) => apiRequest<FocusPoint>({ 
    method: 'GET', 
    url: `/focus-points/${id}` 
  }),
  
  create: (data: FocusPointCreate) => apiRequest<FocusPoint>({ 
    method: 'POST', 
    url: '/focus-points', 
    data 
  }),
  
  update: (id: string, data: FocusPointUpdate) => apiRequest<FocusPoint>({ 
    method: 'PATCH', 
    url: `/focus-points/${id}`, 
    data 
  }),
  
  delete: (id: string) => apiRequest<void>({ 
    method: 'DELETE', 
    url: `/focus-points/${id}` 
  }),
};

// 信息API
export const infoApi = {
  getAll: (params?: any) => apiRequest<Info[]>({ 
    method: 'GET', 
    url: '/info',
    params 
  }),
  
  getById: (id: string) => apiRequest<Info>({ 
    method: 'GET', 
    url: `/info/${id}` 
  }),
  
  create: (data: InfoCreate) => apiRequest<Info>({ 
    method: 'POST', 
    url: '/info', 
    data 
  }),
  
  update: (id: string, data: InfoUpdate) => apiRequest<Info>({ 
    method: 'PATCH', 
    url: `/info/${id}`, 
    data 
  }),
  
  delete: (id: string) => apiRequest<void>({ 
    method: 'DELETE', 
    url: `/info/${id}` 
  }),
  
  getLatestByFocus: (focusId: string, limit?: number) => apiRequest<Info[]>({ 
    method: 'GET', 
    url: `/info/focus/${focusId}/latest`,
    params: { limit } 
  }),
  
  search: (query: string, focusId?: string, params?: any) => apiRequest<Info[]>({ 
    method: 'GET', 
    url: '/info/search',
    params: { query, focus_id: focusId, ...params } 
  }),
};

// 查询API
export const queryApi = {
  create: (data: QueryRequest) => apiRequest<QueryResponse>({ 
    method: 'POST', 
    url: '/query', 
    data 
  }),
  
  getAll: (params?: any) => apiRequest<Query[]>({ 
    method: 'GET', 
    url: '/query',
    params 
  }),
  
  getById: (id: string) => apiRequest<Query>({ 
    method: 'GET', 
    url: `/query/${id}` 
  }),
  
  delete: (id: string) => apiRequest<void>({ 
    method: 'DELETE', 
    url: `/query/${id}` 
  }),
};

export default api; 