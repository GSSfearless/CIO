# CIO (Customized Information Organizer)

CIO是一个个性化信息管理和查询系统，旨在帮助用户自动收集、组织和查询与其关注点相关的信息。

## 项目概述

- 自动收集：从多种信息源（RSS、网页、搜索引擎等）收集与用户关注点相关的信息
- 智能组织：使用AI对收集的信息进行分类、摘要和关联
- 交互式查询：允许用户通过自然语言查询相关信息

## 项目结构

```
CIO/
├── backend/              # 后端服务
│   ├── app/              # 应用代码
│   │   ├── agents/       # 智能代理模块
│   │   ├── api/          # API接口
│   │   ├── llm/          # 大语言模型服务
│   │   ├── models/       # 数据模型
│   │   ├── scrapers/     # 信息采集器
│   │   └── utils/        # 工具函数
│   ├── main.py           # 应用入口点
│   └── requirements.txt  # 依赖管理
└── frontend/             # 前端代码
    ├── public/           # 静态资源
    ├── src/              # 源代码
    │   ├── api/          # API调用
    │   ├── components/   # 可复用组件
    │   ├── pages/        # 页面组件
    │   ├── types/        # 类型定义
    │   ├── App.tsx       # 应用入口组件
    │   └── main.tsx      # 应用入口点
    └── package.json      # 项目配置
```

## API结构

CIO提供了REST风格的API，所有API端点都以`/api/v1`为前缀。

### 信息源管理（/api/v1/sources）

- `GET /sources` - 获取信息源列表
- `GET /sources/{source_id}` - 获取特定信息源详情
- `POST /sources` - 创建新的信息源
- `PATCH /sources/{source_id}` - 更新信息源
- `DELETE /sources/{source_id}` - 删除信息源

### 关注点管理（/api/v1/focus-points）

- `GET /focus-points` - 获取关注点列表
- `GET /focus-points/{focus_id}` - 获取特定关注点详情
- `POST /focus-points` - 创建新的关注点
- `PATCH /focus-points/{focus_id}` - 更新关注点
- `DELETE /focus-points/{focus_id}` - 删除关注点

### 信息查询（/api/v1/info）

- `GET /info` - 获取信息列表
- `GET /info/{info_id}` - 获取特定信息详情
- `POST /info` - 创建新的信息
- `PATCH /info/{info_id}` - 更新信息
- `DELETE /info/{info_id}` - 删除信息
- `GET /info/focus/{focus_id}/latest` - 获取特定关注点的最新信息
- `GET /info/search` - 搜索信息内容

### 交互式查询（/api/v1/query）

- `POST /query` - 创建新的查询并获取响应
- `GET /query` - 获取查询历史记录
- `GET /query/{query_id}` - 获取特定查询详情
- `DELETE /query/{query_id}` - 删除查询记录

## 项目进展

当前已完成：
- 后端基础架构搭建
- 数据模型设计
- API接口实现（信息源、关注点、信息查询、交互式查询）
- 前端基础框架搭建
- 前端API服务层实现
- 前端基本布局和首页

下一步计划：
- 完成前端界面各功能页面
- 实现信息处理代理（分类和摘要）
- 实现调度系统

## 技术栈

### 后端
- Python 3.9+
- FastAPI
- Pydantic
- PocketBase（云数据库服务）
- OpenAI API（LLM服务）

### 前端
- React 18
- TypeScript
- React Router
- React Query
- Axios
- Tailwind CSS

## 运行项目

### 后端

1. 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

2. 复制环境变量配置文件
```bash
cp .env.example .env
```
然后编辑`.env`文件，填入必要的配置信息

3. 运行开发服务器
```bash
uvicorn main:app --reload
```

4. 访问API文档
打开浏览器访问 http://localhost:8000/docs

### 前端

1. 安装依赖
```bash
cd frontend
npm install
```

2. 复制环境变量配置文件
```bash
cp .env.example .env
```

3. 运行开发服务器
```bash
npm run dev
```

4. 访问前端应用
打开浏览器访问 http://localhost:5173 