import { configureStore } from '@reduxjs/toolkit';
import { persistStore, persistReducer } from 'redux-persist';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { combineReducers } from 'redux';
import { setupListeners } from '@reduxjs/toolkit/query';

import authReducer from './slices/authSlice';
import uiReducer from './slices/uiSlice';
import sourcesReducer from './slices/sourcesSlice';
import focusPointsReducer from './slices/focusPointsSlice';
import settingsReducer from './slices/settingsSlice';

// 持久化配置
const persistConfig = {
  key: 'root',
  storage: AsyncStorage,
  whitelist: ['auth'], // 只持久化auth状态
};

// 合并所有reducers
const rootReducer = combineReducers({
  auth: authReducer,
  ui: uiReducer,
  sources: sourcesReducer,
  focusPoints: focusPointsReducer,
  settings: settingsReducer,
});

// 创建持久化reducer
const persistedReducer = persistReducer(persistConfig, rootReducer);

// 配置store
export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
});

// 创建持久化store
export const persistor = persistStore(store);

// 启用监听器
setupListeners(store.dispatch);

// 导出RootState和AppDispatch类型
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch; 