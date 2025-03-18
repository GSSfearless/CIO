# CIO情报管家移动应用

CIO情报管家移动应用是一个基于React Native和Expo构建的跨平台移动应用，旨在为用户提供随时随地访问和管理情报信息的能力。

## 功能特点

- **智能查询**：通过自然语言与AI助手交互，获取精准信息
- **关注点管理**：创建和管理您关注的主题，自动收集相关信息
- **信息源管理**：添加、编辑和管理各类信息源
- **信息聚合**：自动整合来自不同渠道的信息，形成知识库
- **个性化推荐**：基于您的关注点和历史查询，推荐相关信息
- **离线访问**：支持关键信息的离线访问和阅读

## 技术栈

- **React Native**：跨平台移动应用开发框架
- **Expo**：简化React Native开发的工具和服务
- **TypeScript**：提供类型安全的JavaScript超集
- **React Navigation**：应用导航解决方案
- **React Native Paper**：Material Design组件库
- **React Query**：数据获取和缓存管理
- **Redux Toolkit**：状态管理
- **Axios**：HTTP客户端

## 项目结构

```
mobile/
├── assets/              # 图片、字体等静态资源
├── src/
│   ├── api/             # API服务和接口定义
│   ├── components/      # 可复用UI组件
│   ├── config/          # 应用配置
│   ├── hooks/           # 自定义React Hooks
│   ├── navigation/      # 导航配置
│   ├── screens/         # 应用屏幕组件
│   ├── store/           # Redux状态管理
│   │   └── slices/      # Redux切片
│   ├── types/           # TypeScript类型定义
│   └── utils/           # 工具函数
├── App.tsx              # 应用入口
├── app.json             # Expo配置
├── babel.config.js      # Babel配置
├── package.json         # 依赖管理
└── tsconfig.json        # TypeScript配置
```

## 开始使用

### 前提条件

- Node.js (>= 14.0.0)
- npm 或 yarn
- Expo CLI (`npm install -g expo-cli`)

### 安装

1. 克隆仓库
```bash
git clone https://github.com/yourusername/cio.git
cd cio/mobile
```

2. 安装依赖
```bash
npm install
# 或
yarn install
```

3. 启动开发服务器
```bash
npm start
# 或
yarn start
```

4. 使用Expo Go应用扫描二维码在真机上运行，或使用模拟器/模拟机运行

### 构建应用

```bash
expo build:android  # 构建Android应用
expo build:ios      # 构建iOS应用
```

## 主要屏幕

- **首页**：显示关注点摘要、最新信息和推荐查询
- **查询**：与AI助手进行自然语言交互
- **关注点**：管理您关注的主题
- **信息源**：管理和配置信息来源
- **个人中心**：用户设置和偏好

## 后端API

移动应用通过RESTful API与后端服务通信，API基础URL可在`src/config/index.ts`中配置。

## 贡献

欢迎提交问题报告和拉取请求。对于重大更改，请先开issue讨论您想要更改的内容。

## 许可证

[MIT](https://choosealicense.com/licenses/mit/) 