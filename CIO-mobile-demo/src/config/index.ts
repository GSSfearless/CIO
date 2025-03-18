// API配置
export const API_BASE_URL = 'http://localhost:8000/api';

// 应用配置
export const APP_CONFIG = {
  // 应用名称
  appName: 'CIO情报管家',
  
  // 版本信息
  version: '1.0.0',
  
  // 缓存配置
  cache: {
    // 缓存过期时间（毫秒）
    expireTime: 1000 * 60 * 60, // 1小时
    
    // 最大缓存条目数
    maxEntries: 100,
  },
  
  // 查询配置
  query: {
    // 最大查询历史记录数
    maxHistoryItems: 50,
    
    // 默认显示推理过程
    defaultShowReasoning: false,
  },
  
  // 关注点配置
  focusPoints: {
    // 最大标签数
    maxTags: 5,
    
    // 标签最大长度
    maxTagLength: 20,
  },
  
  // 信息源配置
  sources: {
    // 支持的信息源类型
    supportedTypes: ['rss', 'web', 'api'],
    
    // 默认刷新间隔（分钟）
    defaultRefreshInterval: 60,
  },
  
  // 主题配置
  theme: {
    // 主色调
    primaryColor: '#3F51B5',
    
    // 强调色
    accentColor: '#FF4081',
    
    // 背景色
    backgroundColor: '#F5F5F5',
  },
};

// 错误消息
export const ERROR_MESSAGES = {
  // 网络错误
  networkError: '网络连接失败，请检查您的网络设置',
  
  // 服务器错误
  serverError: '服务器错误，请稍后再试',
  
  // 认证错误
  authError: '认证失败，请重新登录',
  
  // 权限错误
  permissionError: '您没有权限执行此操作',
  
  // 表单验证错误
  validationError: '表单验证失败，请检查输入',
  
  // 查询错误
  queryError: '查询处理失败，请重试',
};

// 正则表达式
export const REGEX = {
  // 电子邮件
  email: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
  
  // URL
  url: /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*\/?$/,
  
  // 密码（至少8个字符，包含字母和数字）
  password: /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/,
}; 