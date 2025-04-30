# CIO

CIO是一个个性化信息管理和查询系统，旨在帮助用户自动收集、组织和查询与其关注点相关的信息。

## 项目概述

- 自动收集：从多种信息源（RSS、网页、搜索引擎等）收集与用户关注点相关的信息
- 智能组织：使用AI对收集的信息进行分类、摘要和关联
- 交互式查询：允许用户通过自然语言查询相关信息
- 自主工具选择：AI代理能自主决定使用何种工具（网络搜索、数据库查询等）回答用户问题

## 项目特点

### 国内大模型支持

系统默认使用智谱AI作为大模型服务，同时支持：

- 智谱AI（默认）
- 百度文心一言
- 讯飞星火认知大模型

可通过环境变量或配置文件轻松切换不同的模型服务。

### 增强的工具代理系统

CIO的核心是自主工具使用代理，它能够：

1. **智能理解查询**：深入分析用户问题，理解查询意图
2. **自主选择工具**：根据问题类型决定使用何种工具
3. **多轮工具使用**：支持"搜索-阅读-总结-决策"的完整循环
4. **自主退出判断**：根据信息收集状态自动决定是否继续使用工具
5. **推理过程可视化**：可选显示完整的推理和工具使用过程

## 项目结构

```
CIO/
├── backend/              # 后端服务
│   ├── app/              # 应用代码
│   │   ├── agents/       # 智能代理模块
│   │   │   └── tools/    # 代理工具集
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

## AI代理与工具系统

CIO的核心特色是自主工具选择代理系统，该系统能够：

1. **智能理解查询**：分析用户问题，理解查询意图
2. **自主选择工具**：根据问题类型决定使用何种工具
3. **多工具协作**：串联多个工具完成复杂任务
4. **结果整合**：综合多个工具的输出生成连贯回答
5. **状态跟踪**：记录工具使用情况、收集的信息和信心水平
6. **自主决策**：根据收集的信息质量和数量自主决定何时停止工具使用

### 可用工具

- **搜索工具**：通过搜索引擎实时获取网络信息
- **数据库查询工具**：查询系统内已收集的信息
- **网页抓取工具**：获取特定网页的详细内容

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
  - 参数：
    - `query`: 查询内容
    - `focus_id`: (可选) 关注点ID
    - `context_info_ids`: (可选) 上下文信息ID列表
    - `show_reasoning`: (可选) 是否显示推理过程，默认为false
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
- 自主工具选择代理系统实现
- 增强的工具代理系统（支持多轮迭代和自主决策）
- 国内大模型支持（智谱AI、百度文心、讯飞星火）

下一步计划：
- 完成前端界面各功能页面
- 实现信息分类和摘要代理
- 实现调度系统

## 技术栈

### 后端
- Python 3.9+
- FastAPI
- Pydantic
- PocketBase（云数据库服务）
- 多种大语言模型服务（智谱AI、百度文心、讯飞星火等）

### 前端
- React 18
- TypeScript
- React Router
- React Query
- Axios
- Tailwind CSS

## 环境变量配置

### LLM服务配置

```
# LLM提供商，可选：zhipu（智谱AI）, baidu（百度文心）, xunfei（讯飞星火）
LLM_PROVIDER="zhipu"

# 智谱AI配置
ZHIPU_API_KEY="你的智谱AI API密钥"
ZHIPU_MODEL="glm-4"

# 百度文心一言配置
BAIDU_API_KEY="你的百度API密钥"
BAIDU_SECRET_KEY="你的百度密钥"
BAIDU_MODEL="ernie-bot-4"

# 讯飞星火配置
XUNFEI_APP_ID="你的讯飞应用ID"
XUNFEI_API_KEY="你的讯飞API密钥"
XUNFEI_API_SECRET="你的讯飞密钥"
XUNFEI_MODEL="general"
```

### 数据库配置

```
# PocketBase数据库配置
PB_API_BASE="http://127.0.0.1:8090"
PB_API_AUTH="admin@example.com|password123"
```

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
