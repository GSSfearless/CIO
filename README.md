# CIO: 您的 AI 首席情报官 🤖✨

CIO (Chief Intelligence Officer) 是一个由 AI 驱动的个性化智能系统，旨在扮演您专属的"首席情报官"角色。它能帮助您自动收集、智能处理、深度分析并便捷查询您所关注领域的海量信息，为您提供及时、精准的情报支持。

## 项目愿景 🚀

想象一下拥有一位全天候待命、能力超群的首席情报官，能够：

- 🔭 **主动监控与收集**: 7x24小时不间断地从互联网、数据库等多种渠道为您搜集最新的相关信息。
- 🧠 **智能分析与提炼**: 利用先进的 AI 技术，对繁杂的信息进行分类、摘要、关联分析，去伪存真，提炼核心情报。
- 💬 **交互式情报获取**: 通过自然语言对话，快速响应您的查询需求，提供精准、深入的分析结果。
- 💡 **自主决策与行动**: 智能判断任务需求，自主选择并调度最优工具（如网络搜索、数据查询、内容抓取等）来完成情报任务。

CIO 项目致力于将这一愿景变为现实，为您打造一个强大的个人情报中枢。

## 核心功能 🎯

- 📥 **自动化情报收集**: 支持从 RSS、网页、搜索引擎等多种信息源自动获取与您关注点相关的信息。
- 📊 **智能化信息处理**: 运用大语言模型对收集的信息进行分类、打标签、生成摘要、建立关联，形成结构化的情报知识库。
- 🗣️ **交互式自然语言查询**: 允许用户通过自然语言提问，系统能够理解意图并返回精准的答案或分析报告。
- ⚙️ **自主工具调度引擎**: 强大的 AI 代理能够根据任务需求，自主决策并执行最合适的工具组合，完成复杂的信息获取和分析任务。

## 项目特点 ⭐

### 🇨🇳 国内大模型深度适配

系统优先适配国内主流大语言模型，确保在中国大陆地区的最佳性能和合规性：

- <0xF0><0x9F><0xA7><0xA9> 智谱AI (GLM 系列) (默认)
- <0xF0><0x9F><0x90><0xBC> 百度文心一言 (ERNIE-Bot 系列)
- 🔥 讯飞星火认知大模型

用户可以通过简单的配置（环境变量或配置文件）在不同模型服务间无缝切换。

### 🧠 增强的自主工具代理 (AI Agent)

CIO 的核心是其高度自主的 AI 代理系统，具备类人智能的特征：

1.  **深度意图理解**: 精准分析用户查询的深层意图和信息需求。
2.  **智能工具决策**: 基于任务复杂度、信息可用性和工具能力，自主选择最优的单一或组合工具。
3.  **多轮迭代推理**: 支持"规划-执行-反思-调整"的复杂工作流，例如"搜索信息 -> 阅读关键内容 -> 总结要点 -> 基于总结进行下一步决策"。
4.  **自主终止判断**: AI 代理能根据当前已获取信息的充分性和质量，自主判断何时结束任务，避免冗余操作。
5.  **过程透明可追溯**: 可选择性地展示 AI 代理的完整思考链条、工具选择逻辑和执行过程，方便理解和调试。

## 项目结构 📁

```
CIO/
├── backend/              # 后端服务 (FastAPI, Python)
│   ├── app/              # 应用核心代码
│   │   ├── agents/       # AI 代理核心逻辑 (工具选择、任务规划、执行控制)
│   │   │   └── tools/    # 可供代理调度的工具集 (搜索, 网页抓取, 数据库查询等)
│   │   ├── api/          # RESTful API 接口定义
│   │   ├── llm/          # 大语言模型适配层 (支持多厂商)
│   │   ├── models/       # 数据模型 (Pydantic)
│   │   ├── scrapers/     # 网页内容抓取与解析模块
│   │   └── utils/        # 通用工具函数
│   ├── main.py           # 应用入口
│   └── requirements.txt  # Python 依赖
├── frontend/             # 前端应用 (React, TypeScript)
│   ├── public/           # 静态资源
│   ├── src/              # 源代码
│   │   ├── api/          # 前后端 API 交互层
│   │   ├── components/   # 可复用 UI 组件
│   │   ├── pages/        # 页面级组件
│   │   ├── types/        # TypeScript 类型定义
│   │   ├── App.tsx       # React 应用根组件
│   │   └── main.tsx      # 前端入口点
│   └── package.json      # Node.js 依赖与脚本
├── mobile/               # 移动端应用 (React Native, 规划中)
│   └── ...
├── docs/                 # 项目文档
├── CIO-mobile-demo/      # 移动端 Demo (可选)
├── .env.example          # 环境变量示例文件
├── .gitignore            # Git 忽略配置
├── README.md             # 项目说明 (本文档)
└── PROGRESS.md           # 项目详细进展与规划
```

## AI 代理与工具系统详解 🛠️

CIO的核心特色是自主工具选择代理系统，该系统能够：

1. **智能理解查询**：分析用户问题，理解查询意图
2. **自主选择工具**：根据问题类型决定使用何种工具
3. **多工具协作**：串联多个工具完成复杂任务
4. **结果整合**：综合多个工具的输出生成连贯回答
5. **状态跟踪**：记录工具使用情况、收集的信息和信心水平
6. **自主决策**：根据收集的信息质量和数量自主决定何时停止工具使用

### 可用工具 🔧

- 🔍 **搜索工具**：通过搜索引擎实时获取网络信息
- 💾 **数据库查询工具**：查询系统内已收集的信息
- 🌐 **网页抓取工具**：获取特定网页的详细内容

## API 结构 🔌

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

## 项目进展 📈

参考 `PROGRESS.md` 获取最新的详细进展和未来规划。

## 技术栈 💻

### 后端 ☁️
- Python 3.9+
- FastAPI
- Pydantic
- PocketBase（云数据库服务）
- 多种大语言模型服务（智谱AI、百度文心、讯飞星火等）

### 前端 🎨
- React 18
- TypeScript
- React Router
- React Query
- Axios
- Tailwind CSS

## 环境变量配置 ⚙️

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

## 运行项目 ▶️

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

然后编辑`.env`