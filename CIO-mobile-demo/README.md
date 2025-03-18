# CIO情报管家移动应用

这是CIO情报管家的移动应用客户端，基于React Native和Expo开发。

## 项目概述

CIO情报管家是一个智能情报助手应用，帮助用户获取、分析和管理重要信息。用户可以设置关注点，提交查询，并获取智能分析结果。

## 技术栈

- React Native
- Expo
- TypeScript
- React Navigation
- React Query
- React Native Paper
- Axios

## 项目结构

```
src/
  ├── api/            # API服务
  ├── assets/         # 静态资源
  ├── components/     # 可复用组件
  ├── config/         # 配置文件
  ├── navigation/     # 导航配置
  ├── screens/        # 屏幕组件
  ├── services/       # 业务服务
  ├── store/          # 状态管理
  ├── styles/         # 样式
  ├── types/          # 类型定义
  └── utils/          # 工具函数
```

## 功能特性

- 用户认证（登录/注册）
- 智能查询
- 关注点管理
- 信息源管理
- 查询历史

## 开发环境设置

### 前提条件

- Node.js (v14+)
- npm 或 yarn
- Expo CLI
- Android Studio (Android开发) 或 Xcode (iOS开发)

### 安装依赖

```bash
npm install
# 或
yarn install
```

### 运行开发服务器

```bash
npm start
# 或
yarn start
# 或
npx expo start
```

### 在设备上测试

1. 在手机上安装Expo Go应用
2. 扫描终端中显示的QR码
3. 或者使用模拟器/真机通过USB连接

## 构建生产版本

### Android

```bash
expo build:android
```

### iOS

```bash
expo build:ios
```

## 贡献指南

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

[MIT](LICENSE) 