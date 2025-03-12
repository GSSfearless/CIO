// 基础类型
export interface BaseModel {
  id?: string;
  created?: string;
  updated?: string;
}

// 信息源类型
export interface Source extends BaseModel {
  url: string;
  type: string;
  name: string;
  description?: string;
  category?: string;
  activated: boolean;
}

export interface SourceCreate {
  url: string;
  type: string;
  name: string;
  description?: string;
  category?: string;
  activated?: boolean;
}

export interface SourceUpdate {
  url?: string;
  type?: string;
  name?: string;
  description?: string;
  category?: string;
  activated?: boolean;
}

// 关注点类型
export interface FocusPoint extends BaseModel {
  focuspoint: string;
  explanation?: string;
  activated: boolean;
  per_hour: number;
  search_engine: boolean;
  source_ids: string[];
  owner?: string;
}

export interface FocusPointCreate {
  focuspoint: string;
  explanation?: string;
  activated?: boolean;
  per_hour?: number;
  search_engine?: boolean;
  source_ids?: string[];
  owner?: string;
}

export interface FocusPointUpdate {
  focuspoint?: string;
  explanation?: string;
  activated?: boolean;
  per_hour?: number;
  search_engine?: boolean;
  source_ids?: string[];
  owner?: string;
}

// 信息类型
export interface Info extends BaseModel {
  title: string;
  content: string;
  summary?: string;
  url?: string;
  url_title?: string;
  published?: string;
  author?: string;
  source?: string;
  tags: string[];
  relevance_score?: number;
  focus_id: string;
}

export interface InfoCreate {
  title: string;
  content: string;
  summary?: string;
  url?: string;
  url_title?: string;
  published?: string;
  author?: string;
  source?: string;
  tags?: string[];
  relevance_score?: number;
  focus_id: string;
}

export interface InfoUpdate {
  title?: string;
  content?: string;
  summary?: string;
  url?: string;
  url_title?: string;
  published?: string;
  author?: string;
  source?: string;
  tags?: string[];
  relevance_score?: number;
  focus_id?: string;
}

// 查询类型
export interface Query extends BaseModel {
  query: string;
  focus_id?: string;
  response: string;
  timestamp: string;
}

export interface QueryRequest {
  query: string;
  focus_id?: string;
  context_info_ids?: string[];
}

export interface QueryResponse {
  query_id: string;
  query: string;
  response: string;
  focus_id?: string;
  timestamp: string;
}

// API响应类型
export interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
} 