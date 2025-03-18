import api from './client';
import { CreateQueryRequest, Query } from '../types/api';

// 查询相关API
const queryApi = {
  // 获取查询历史
  getQueries: (page = 1, limit = 10) => 
    api.get<Query[]>('/queries', { page, limit }),
  
  // 获取单个查询详情
  getQuery: (id: string) => 
    api.get<Query>(`/queries/${id}`),
  
  // 创建新查询
  createQuery: (data: CreateQueryRequest) => 
    api.post<Query>('/queries', data),
  
  // 删除查询
  deleteQuery: (id: string) => 
    api.delete(`/queries/${id}`),
};

export default queryApi; 