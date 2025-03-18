import api from './index';

// 创建查询接口
export const createQuery = (data: {
  query: string;
  focus_id?: string;
  context_info_ids?: string[];
  show_reasoning?: boolean;
}) => {
  return api.post('/query', data);
};

// 获取查询历史列表
export const getQueries = (params?: {
  page?: number;
  limit?: number;
  focus_id?: string;
}) => {
  return api.get('/query', { params });
};

// 获取单个查询详情
export const getQuery = (id: string) => {
  return api.get(`/query/${id}`);
};

// 删除查询
export const deleteQuery = (id: string) => {
  return api.delete(`/query/${id}`);
};

// 获取推荐查询
export const getRecommendedQueries = (focusId?: string) => {
  const params = focusId ? { focus_id: focusId } : {};
  return api.get('/query/recommended', { params });
}; 