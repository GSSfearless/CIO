import api from './index';

// 创建关注点
export const createFocusPoint = (data: {
  title: string;
  description: string;
  tags?: string[];
  active?: boolean;
}) => {
  return api.post('/focus-points', data);
};

// 获取关注点列表
export const getFocusPoints = (params?: {
  page?: number;
  limit?: number;
  tag?: string;
  active?: boolean;
}) => {
  return api.get('/focus-points', { params });
};

// 获取单个关注点详情
export const getFocusPoint = (id: string) => {
  return api.get(`/focus-points/${id}`);
};

// 更新关注点
export const updateFocusPoint = (id: string, data: {
  title?: string;
  description?: string;
  tags?: string[];
  active?: boolean;
}) => {
  return api.put(`/focus-points/${id}`, data);
};

// 删除关注点
export const deleteFocusPoint = (id: string) => {
  return api.delete(`/focus-points/${id}`);
};

// 获取关注点相关信息
export const getFocusPointInfo = (id: string, params?: {
  page?: number;
  limit?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}) => {
  return api.get(`/focus-points/${id}/info`, { params });
}; 