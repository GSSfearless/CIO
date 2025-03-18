import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useTheme } from 'react-native-paper';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

// 导入屏幕组件
import HomeScreen from '../screens/HomeScreen';
import SourcesScreen from '../screens/SourcesScreen';
import FocusPointsScreen from '../screens/FocusPointsScreen';
import InfoScreen from '../screens/InfoScreen';
import QueryScreen from '../screens/QueryScreen';
import SettingsScreen from '../screens/SettingsScreen';
import LoginScreen from '../screens/LoginScreen';
import RegisterScreen from '../screens/RegisterScreen';

// 定义堆栈导航类型
export type RootStackParamList = {
  Main: undefined;
  Login: undefined;
  Register: undefined;
  Settings: undefined;
};

// 定义底部标签导航类型
export type MainTabParamList = {
  Home: undefined;
  Sources: undefined;
  FocusPoints: undefined;
  Info: undefined;
  Query: undefined;
};

// 创建导航器
const Stack = createNativeStackNavigator<RootStackParamList>();
const Tab = createBottomTabNavigator<MainTabParamList>();

// 主标签导航
const MainNavigator = () => {
  const theme = useTheme();
  
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName = 'home';
          
          if (route.name === 'Home') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === 'Sources') {
            iconName = focused ? 'database' : 'database-outline';
          } else if (route.name === 'FocusPoints') {
            iconName = focused ? 'target' : 'target-outline';
          } else if (route.name === 'Info') {
            iconName = focused ? 'information' : 'information-outline';
          } else if (route.name === 'Query') {
            iconName = focused ? 'comment-question' : 'comment-question-outline';
          }
          
          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: theme.colors.primary,
        tabBarInactiveTintColor: 'gray',
      })}
    >
      <Tab.Screen name="Home" component={HomeScreen} options={{ title: '首页' }} />
      <Tab.Screen name="Sources" component={SourcesScreen} options={{ title: '信息源' }} />
      <Tab.Screen name="FocusPoints" component={FocusPointsScreen} options={{ title: '关注点' }} />
      <Tab.Screen name="Info" component={InfoScreen} options={{ title: '浏览' }} />
      <Tab.Screen name="Query" component={QueryScreen} options={{ title: '查询' }} />
    </Tab.Navigator>
  );
};

// 根导航器
const AppNavigator = () => {
  return (
    <Stack.Navigator initialRouteName="Main">
      <Stack.Screen
        name="Main"
        component={MainNavigator}
        options={{ headerShown: false }}
      />
      <Stack.Screen
        name="Login"
        component={LoginScreen}
        options={{ title: '登录' }}
      />
      <Stack.Screen
        name="Register"
        component={RegisterScreen}
        options={{ title: '注册' }}
      />
      <Stack.Screen
        name="Settings"
        component={SettingsScreen}
        options={{ title: '设置' }}
      />
    </Stack.Navigator>
  );
};

export default AppNavigator; 