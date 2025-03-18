import api from './client';
import { 
  CreateFocusPointRequest, 
  FocusPoint, 
  UpdateFocusPointRequest 
} from '../types/api';

// 关注点相关API
const focusPointApi = {
  // 获取所有关注点
  getFocusPoints: (page = 1, limit = 10) => 
    api.get<FocusPoint[]>('/focus-points', { page, limit }),
  
  // 获取活跃的关注点
  getActiveFocusPoints: () => 
    api.get<FocusPoint[]>('/focus-points/active'),
  
  // 获取单个关注点详情
  getFocusPoint: (id: string) => 
    api.get<FocusPoint>(`/focus-points/${id}`),
  
  // 创建新关注点
  createFocusPoint: (data: CreateFocusPointRequest) => 
    api.post<FocusPoint>('/focus-points', data),
  
  // 更新关注点
  updateFocusPoint: (id: string, data: UpdateFocusPointRequest) => 
    api.put<FocusPoint>(`/focus-points/${id}`, data),
  
  // 删除关注点
  deleteFocusPoint: (id: string) => 
    api.delete(`/focus-points/${id}`),
};

export default focusPointApi; 