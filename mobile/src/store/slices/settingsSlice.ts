import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../index';

// 主题类型
export type ThemeType = 'light' | 'dark' | 'system';

// 设置状态接口
interface SettingsState {
  theme: ThemeType;
  language: string;
  notificationsEnabled: boolean;
  autoRefresh: boolean;
  refreshInterval: number; // 分钟
  fontSize: 'small' | 'medium' | 'large';
}

// 初始状态
const initialState: SettingsState = {
  theme: 'system',
  language: 'zh-CN',
  notificationsEnabled: true,
  autoRefresh: true,
  refreshInterval: 30,
  fontSize: 'medium',
};

// 创建设置切片
const settingsSlice = createSlice({
  name: 'settings',
  initialState,
  reducers: {
    setTheme: (state, action: PayloadAction<ThemeType>) => {
      state.theme = action.payload;
    },
    setLanguage: (state, action: PayloadAction<string>) => {
      state.language = action.payload;
    },
    toggleNotifications: (state) => {
      state.notificationsEnabled = !state.notificationsEnabled;
    },
    toggleAutoRefresh: (state) => {
      state.autoRefresh = !state.autoRefresh;
    },
    setRefreshInterval: (state, action: PayloadAction<number>) => {
      state.refreshInterval = action.payload;
    },
    setFontSize: (state, action: PayloadAction<'small' | 'medium' | 'large'>) => {
      state.fontSize = action.payload;
    },
    resetSettings: () => initialState,
  },
});

// 导出操作
export const {
  setTheme,
  setLanguage,
  toggleNotifications,
  toggleAutoRefresh,
  setRefreshInterval,
  setFontSize,
  resetSettings,
} = settingsSlice.actions;

// 导出选择器
export const selectTheme = (state: RootState) => state.settings.theme;
export const selectLanguage = (state: RootState) => state.settings.language;
export const selectNotificationsEnabled = (state: RootState) => state.settings.notificationsEnabled;
export const selectAutoRefresh = (state: RootState) => state.settings.autoRefresh;
export const selectRefreshInterval = (state: RootState) => state.settings.refreshInterval;
export const selectFontSize = (state: RootState) => state.settings.fontSize;
export const selectSettings = (state: RootState) => state.settings;

// 导出reducer
export default settingsSlice.reducer; 