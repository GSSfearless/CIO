import api from './client';
import { 
  CreateSourceRequest, 
  Source, 
  UpdateSourceRequest 
} from '../types/api';

// 信息源相关API
const sourceApi = {
  // 获取所有信息源
  getSources: (page = 1, limit = 10) => 
    api.get<Source[]>('/sources', { page, limit }),
  
  // 获取活跃的信息源
  getActiveSources: () => 
    api.get<Source[]>('/sources/active'),
  
  // 获取单个信息源详情
  getSource: (id: string) => 
    api.get<Source>(`/sources/${id}`),
  
  // 创建新信息源
  createSource: (data: CreateSourceRequest) => 
    api.post<Source>('/sources', data),
  
  // 更新信息源
  updateSource: (id: string, data: UpdateSourceRequest) => 
    api.put<Source>(`/sources/${id}`, data),
  
  // 删除信息源
  deleteSource: (id: string) => 
    api.delete(`/sources/${id}`),
};

export default sourceApi; 