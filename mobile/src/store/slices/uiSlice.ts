import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '..';

// UI状态接口
interface UIState {
  darkMode: boolean;
  language: string;
  notificationsEnabled: boolean;
  loading: {
    global: boolean;
    [key: string]: boolean;
  };
}

// 初始状态
const initialState: UIState = {
  darkMode: false,
  language: 'zh_CN',
  notificationsEnabled: true,
  loading: {
    global: false,
  },
};

// 创建UI切片
const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    toggleDarkMode: (state) => {
      state.darkMode = !state.darkMode;
    },
    setLanguage: (state, action: PayloadAction<string>) => {
      state.language = action.payload;
    },
    toggleNotifications: (state) => {
      state.notificationsEnabled = !state.notificationsEnabled;
    },
    setLoading: (state, action: PayloadAction<{ key: string; value: boolean }>) => {
      const { key, value } = action.payload;
      state.loading[key] = value;
    },
    setGlobalLoading: (state, action: PayloadAction<boolean>) => {
      state.loading.global = action.payload;
    },
  },
});

// 导出操作
export const {
  toggleDarkMode,
  setLanguage,
  toggleNotifications,
  setLoading,
  setGlobalLoading,
} = uiSlice.actions;

// 导出选择器
export const selectDarkMode = (state: RootState) => state.ui.darkMode;
export const selectLanguage = (state: RootState) => state.ui.language;
export const selectNotificationsEnabled = (state: RootState) => state.ui.notificationsEnabled;
export const selectLoading = (state: RootState, key: string) => state.ui.loading[key];
export const selectGlobalLoading = (state: RootState) => state.ui.loading.global;

export default uiSlice.reducer; 