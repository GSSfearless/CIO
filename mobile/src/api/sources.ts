import api from './index';

// 创建信息源
export const createSource = (data: {
  name: string;
  type: string;
  url: string;
  description?: string;
  refresh_interval?: number;
  tags?: string[];
}) => {
  return api.post('/sources', data);
};

// 获取信息源列表
export const getSources = (params?: {
  page?: number;
  limit?: number;
  type?: string;
  tag?: string;
}) => {
  return api.get('/sources', { params });
};

// 获取单个信息源详情
export const getSource = (id: string) => {
  return api.get(`/sources/${id}`);
};

// 更新信息源
export const updateSource = (id: string, data: {
  name?: string;
  url?: string;
  description?: string;
  refresh_interval?: number;
  tags?: string[];
  active?: boolean;
}) => {
  return api.put(`/sources/${id}`, data);
};

// 删除信息源
export const deleteSource = (id: string) => {
  return api.delete(`/sources/${id}`);
};

// 手动刷新信息源
export const refreshSource = (id: string) => {
  return api.post(`/sources/${id}/refresh`);
};

// 获取信息源类型
export const getSourceTypes = () => {
  return api.get('/sources/types');
}; 