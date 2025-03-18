import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { Provider as PaperProvider, DefaultTheme } from 'react-native-paper';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Ionicons } from '@expo/vector-icons';
import { View, Text } from 'react-native';

// 导入配置
import { APP_CONFIG } from './src/config';

// 创建React Query客户端
const queryClient = new QueryClient();

// 创建导航堆栈
const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

// 导入屏幕组件
import HomeScreen from './src/screens/HomeScreen';
import QueryScreen from './src/screens/QueryScreen';

// 稍后创建的屏幕 - 目前使用占位符组件
const TrackingScreen = () => (
  <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
    <Text>我的跟踪</Text>
  </View>
);

const HistoryScreen = () => (
  <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
    <Text>历史记录</Text>
  </View>
);

const ProfileScreen = () => (
  <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
    <Text>我的</Text>
  </View>
);

// 自定义主题
const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: '#1976D2',
    accent: '#2196F3',
    background: '#FFFFFF',
    surface: '#FFFFFF',
  },
};

// 主页标签导航
function HomeTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: any;
          if (route.name === '首页') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === '跟踪') {
            iconName = focused ? 'radar' : 'radar-outline';
          } else if (route.name === '历史') {
            iconName = focused ? 'time' : 'time-outline';
          } else if (route.name === '我的') {
            iconName = focused ? 'person' : 'person-outline';
          }
          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: theme.colors.primary,
        tabBarInactiveTintColor: 'gray',
        headerShown: false,
      })}
    >
      <Tab.Screen name="首页" component={HomeScreen} />
      <Tab.Screen name="跟踪" component={TrackingScreen} />
      <Tab.Screen name="历史" component={HistoryScreen} />
      <Tab.Screen name="我的" component={ProfileScreen} />
    </Tab.Navigator>
  );
}

export default function App() {
  return (
    <SafeAreaProvider>
      <PaperProvider theme={theme}>
        <QueryClientProvider client={queryClient}>
          <NavigationContainer>
            <Stack.Navigator initialRouteName="Home">
              <Stack.Screen 
                name="Home" 
                component={HomeTabs} 
                options={{ headerShown: false }}
              />
              <Stack.Screen 
                name="Query" 
                component={QueryScreen} 
                options={{ 
                  headerTitle: '查询结果',
                  headerTitleAlign: 'center',
                  headerShadowVisible: false,
                }}
              />
            </Stack.Navigator>
          </NavigationContainer>
          <StatusBar style="auto" />
        </QueryClientProvider>
      </PaperProvider>
    </SafeAreaProvider>
  );
}
