import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { Provider as PaperProvider, DefaultTheme } from 'react-native-paper';
import { Provider as ReduxProvider } from 'react-redux';
import { QueryClient, QueryClientProvider } from 'react-query';
import * as Sentry from 'sentry-expo';

import Navigation from './src/navigation';
import { store } from './src/store';

// 初始化Sentry
Sentry.init({
  dsn: 'YOUR_SENTRY_DSN', // 替换为您的Sentry DSN
  enableInExpoDevelopment: false,
  debug: __DEV__,
});

// 创建React Query客户端
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

// 自定义主题
const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: '#3F51B5',
    accent: '#FF4081',
  },
};

export default function App() {
  return (
    <SafeAreaProvider>
      <ReduxProvider store={store}>
        <QueryClientProvider client={queryClient}>
          <PaperProvider theme={theme}>
            <Navigation />
            <StatusBar style="auto" />
          </PaperProvider>
        </QueryClientProvider>
      </ReduxProvider>
    </SafeAreaProvider>
  );
} 