import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { useSelector } from 'react-redux';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from 'react-native-paper';

// 导入屏幕
import HomeScreen from '../screens/HomeScreen';
import QueryScreen from '../screens/QueryScreen';
import FocusPointsScreen from '../screens/FocusPointsScreen';
import SourcesScreen from '../screens/SourcesScreen';
import ProfileScreen from '../screens/ProfileScreen';
import LoginScreen from '../screens/LoginScreen';
import RegisterScreen from '../screens/RegisterScreen';
import FocusPointDetailScreen from '../screens/FocusPointDetailScreen';
import SourceDetailScreen from '../screens/SourceDetailScreen';
import InfoDetailScreen from '../screens/InfoDetailScreen';

// 导入状态选择器
import { selectIsAuthenticated } from '../store/slices/authSlice';

// 定义导航参数类型
export type RootStackParamList = {
  Main: undefined;
  Login: undefined;
  Register: undefined;
  FocusPointDetail: { id: string };
  SourceDetail: { id: string };
  InfoDetail: { id: string };
};

export type MainTabParamList = {
  Home: undefined;
  Query: { focusId?: string; queryId?: string };
  FocusPoints: undefined;
  Sources: undefined;
  Profile: undefined;
};

// 创建导航器
const Stack = createNativeStackNavigator<RootStackParamList>();
const Tab = createBottomTabNavigator<MainTabParamList>();

// 主标签导航
function MainTabNavigator() {
  const theme = useTheme();

  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: string;

          if (route.name === 'Home') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === 'Query') {
            iconName = focused ? 'chatbubble' : 'chatbubble-outline';
          } else if (route.name === 'FocusPoints') {
            iconName = focused ? 'list' : 'list-outline';
          } else if (route.name === 'Sources') {
            iconName = focused ? 'layers' : 'layers-outline';
          } else if (route.name === 'Profile') {
            iconName = focused ? 'person' : 'person-outline';
          } else {
            iconName = 'help-outline';
          }

          return <Ionicons name={iconName as any} size={size} color={color} />;
        },
        tabBarActiveTintColor: theme.colors.primary,
        tabBarInactiveTintColor: 'gray',
        headerShown: true,
      })}
    >
      <Tab.Screen 
        name="Home" 
        component={HomeScreen} 
        options={{ 
          title: '首页',
          headerTitle: 'CIO情报管家'
        }} 
      />
      <Tab.Screen 
        name="Query" 
        component={QueryScreen} 
        options={{ 
          title: '查询',
          headerTitle: '智能查询'
        }} 
      />
      <Tab.Screen 
        name="FocusPoints" 
        component={FocusPointsScreen} 
        options={{ 
          title: '关注点',
          headerTitle: '我的关注点'
        }} 
      />
      <Tab.Screen 
        name="Sources" 
        component={SourcesScreen} 
        options={{ 
          title: '信息源',
          headerTitle: '信息源管理'
        }} 
      />
      <Tab.Screen 
        name="Profile" 
        component={ProfileScreen} 
        options={{ 
          title: '我的',
          headerTitle: '个人中心'
        }} 
      />
    </Tab.Navigator>
  );
}

// 根导航
export default function Navigation() {
  const isAuthenticated = useSelector(selectIsAuthenticated);

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {isAuthenticated ? (
          <>
            <Stack.Screen name="Main" component={MainTabNavigator} />
            <Stack.Screen 
              name="FocusPointDetail" 
              component={FocusPointDetailScreen} 
              options={{ headerShown: true, title: '关注点详情' }}
            />
            <Stack.Screen 
              name="SourceDetail" 
              component={SourceDetailScreen} 
              options={{ headerShown: true, title: '信息源详情' }}
            />
            <Stack.Screen 
              name="InfoDetail" 
              component={InfoDetailScreen} 
              options={{ headerShown: true, title: '信息详情' }}
            />
          </>
        ) : (
          <>
            <Stack.Screen name="Login" component={LoginScreen} />
            <Stack.Screen name="Register" component={RegisterScreen} />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
} 