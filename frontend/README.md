# CIO 前端

这是CIO项目的前端部分，使用React构建。

## 功能

- 信息源管理界面
- 关注点管理界面
- 信息浏览和搜索界面
- 交互式查询界面

## 技术栈

- React
- TypeScript
- Tailwind CSS
- Axios (API请求)

## 开发环境设置

1. 安装依赖
```bash
npm install
```

2. 启动开发服务器
```bash
npm run dev
```

3. 构建生产版本
```bash
npm run build
```

## 项目结构

```
frontend/
├── public/           # 静态资源
├── src/              # 源代码
│   ├── api/          # API调用
│   ├── components/   # 可复用组件
│   ├── contexts/     # React上下文
│   ├── hooks/        # 自定义钩子
│   ├── pages/        # 页面组件
│   ├── types/        # TypeScript类型定义
│   ├── utils/        # 工具函数
│   ├── App.tsx       # 应用入口组件
│   └── main.tsx      # 应用入口点
├── .env.example      # 环境变量示例
├── package.json      # 项目配置
└── tsconfig.json     # TypeScript配置
```

## 与后端集成

前端通过RESTful API与后端通信，API基础URL可在环境变量中配置：

```
VITE_API_BASE_URL=http://localhost:8000/api/v1
``` 