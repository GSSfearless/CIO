# MCP协议集成指南

## 概述

Model Context Protocol (MCP) 是一个标准化协议，旨在帮助大型语言模型 (LLM) 与外部服务和工具进行有效通信，从而扩展其能力。本文档详细说明如何将MCP协议集成到CIO项目中，替换当前的自定义工具代理框架，以提高系统的标准化和可扩展性。

## MCP协议简介

MCP提供了一种结构化的方式，让LLM能够以标准化的方式：
- 调用外部API和服务
- 处理请求与响应
- 维护上下文状态
- 进行双向通信和流数据交换

相比我们现有的自定义工具代理框架，MCP具有以下优势：
- **标准化**: 采用统一标准，与更多工具和服务兼容
- **双向通信**: 支持复杂的交互模式和流式数据处理
- **生态系统**: 可以利用已有的MCP工具生态
- **可扩展性**: 更容易添加和管理新工具

## 集成路线图

### 1. 环境准备

**安装MCP SDK**
```bash
pip install mcp-sdk-python
```

**添加依赖到requirements.txt**
```
mcp-sdk-python==0.3.0
```

### 2. 核心组件改造

#### 2.1 创建MCP服务管理器

在`app/llm/mcp_manager.py`中实现MCP服务管理器:

```python
from typing import Dict, List, Optional
import os
import logging
from mcp_sdk.server import MCPServer
from mcp_sdk.models import ServerConfig

class MCPManager:
    """管理MCP服务器和工具的管理器"""
    
    def __init__(self):
        self.servers: Dict[str, MCPServer] = {}
        self.logger = logging.getLogger("mcp_manager")
    
    def start_server(self, server_name: str, port: int, tools: List[str] = None) -> bool:
        """启动一个MCP服务器"""
        try:
            config = ServerConfig(
                name=server_name,
                host="0.0.0.0",
                port=port,
                plugins=tools or []
            )
            server = MCPServer(config)
            self.servers[server_name] = server
            server.start(background=True)
            self.logger.info(f"启动MCP服务器 {server_name} 在端口 {port}")
            return True
        except Exception as e:
            self.logger.error(f"启动MCP服务器失败: {str(e)}")
            return False
    
    def stop_server(self, server_name: str) -> bool:
        """停止一个MCP服务器"""
        if server_name in self.servers:
            try:
                self.servers[server_name].stop()
                del self.servers[server_name]
                self.logger.info(f"停止MCP服务器 {server_name}")
                return True
            except Exception as e:
                self.logger.error(f"停止MCP服务器失败: {str(e)}")
                return False
        return False
    
    def get_server_info(self, server_name: str) -> Optional[dict]:
        """获取服务器信息"""
        if server_name in self.servers:
            server = self.servers[server_name]
            return {
                "name": server.config.name,
                "port": server.config.port,
                "tools": server.config.plugins,
                "status": "running"
            }
        return None
    
    def list_servers(self) -> List[dict]:
        """列出所有运行中的服务器"""
        return [self.get_server_info(name) for name in self.servers]
    
    def stop_all(self):
        """停止所有服务器"""
        for server_name in list(self.servers.keys()):
            self.stop_server(server_name)
            
# 单例模式实现
mcp_manager = MCPManager()
```

#### 2.2 MCP工具基类

在`app/agents/tools/mcp_tool.py`中创建MCP工具基类:

```python
from typing import Any, Dict, List, Optional
from mcp_sdk.plugin import Plugin, PluginConfig
import logging

class MCPTool(Plugin):
    """MCP工具基类，所有工具继承自此类"""
    
    def __init__(self, name: str, description: str, version: str = "0.1.0"):
        config = PluginConfig(
            name=name,
            description=description,
            version=version
        )
        super().__init__(config)
        self.logger = logging.getLogger(f"mcp_tool.{name}")
        
    async def setup(self) -> None:
        """工具初始化时调用"""
        self.logger.info(f"设置MCP工具: {self.config.name}")
        
    async def teardown(self) -> None:
        """工具卸载时调用"""
        self.logger.info(f"卸载MCP工具: {self.config.name}")
        
    def get_info(self) -> Dict[str, Any]:
        """获取工具信息"""
        return {
            "name": self.config.name,
            "description": self.config.description,
            "version": self.config.version,
            "endpoints": [e.name for e in self.endpoints]
        }
```

#### 2.3 LLM适配器更新

更新`app/llm/llm_adapters.py`以支持MCP工具:

```python
# 添加到现有的LLMAdapter基类
class LLMAdapter(ABC):
    # ... 现有代码 ...
    
    async def chat_with_mcp(self, 
                          prompt: str, 
                          mcp_endpoints: List[str],
                          system_prompt: str = None,
                          max_tokens: int = 1000) -> str:
        """
        使用MCP协议与LLM进行对话
        
        Args:
            prompt: 用户提示
            mcp_endpoints: MCP端点列表，格式为['http://localhost:8000', ...]
            system_prompt: 系统提示
            max_tokens: 最大输出令牌数
            
        Returns:
            LLM的响应文本
        """
        raise NotImplementedError("子类必须实现chat_with_mcp方法")
```

#### 2.4 工具代理更新

更新`app/agents/tool_agent.py`以支持MCP工具:

```python
# 在现有的ToolAgent类中添加MCP支持

from app.llm.mcp_manager import mcp_manager

class ToolAgent:
    # ... 现有代码 ...
    
    async def initialize_mcp_tools(self, tools: List[str], port: int = 8000) -> bool:
        """
        初始化MCP工具服务器
        
        Args:
            tools: 要加载的工具列表
            port: 服务器端口
            
        Returns:
            是否成功初始化
        """
        self.mcp_server_name = f"cio_tools_{id(self)}"
        return mcp_manager.start_server(self.mcp_server_name, port, tools)
    
    async def execute_with_mcp(self, 
                             query: str, 
                             system_prompt: str = None,
                             show_reasoning: bool = False) -> Dict[str, Any]:
        """
        使用MCP工具执行查询
        
        Args:
            query: 用户查询
            system_prompt: 系统提示
            show_reasoning: 是否显示推理过程
            
        Returns:
            包含结果和元数据的字典
        """
        if not hasattr(self, 'mcp_server_name'):
            raise ValueError("MCP工具服务器未初始化")
            
        server_info = mcp_manager.get_server_info(self.mcp_server_name)
        if not server_info:
            raise ValueError("MCP工具服务器不存在")
            
        mcp_endpoint = f"http://localhost:{server_info['port']}"
        
        start_time = time.time()
        
        # 构建系统提示
        if not system_prompt:
            system_prompt = (
                "你是一个智能助手，可以使用外部工具来回答用户的问题。"
                "分析用户的查询，确定需要使用哪些工具，并按照合适的顺序使用它们。"
                "如果需要，可以多次使用工具，直到获得完整的答案。"
            )
            
        # 使用LLM适配器与MCP交互
        response = await self.llm_service.chat_with_mcp(
            prompt=query,
            mcp_endpoints=[mcp_endpoint],
            system_prompt=system_prompt,
            max_tokens=2000
        )
        
        elapsed_time = time.time() - start_time
        
        # 返回结果
        return {
            "response": response,
            "elapsed_time": elapsed_time,
            "tools_used": server_info["tools"],
            "reasoning": None if not show_reasoning else "MCP协议当前不支持直接提取推理过程"
        }
        
    def cleanup(self):
        """清理资源"""
        if hasattr(self, 'mcp_server_name'):
            mcp_manager.stop_server(self.mcp_server_name)
        # ... 其他清理代码 ...
```

### 3. 示例工具实现

#### 3.1 网页工具

在`app/agents/tools/web_tool_mcp.py`中实现:

```python
from app.agents.tools.mcp_tool import MCPTool
from mcp_sdk.plugin import endpoint
import aiohttp
from bs4 import BeautifulSoup
import logging

class WebToolMCP(MCPTool):
    """MCP兼容的网页工具"""
    
    def __init__(self):
        super().__init__(
            name="web_tool",
            description="用于从网页获取信息的工具"
        )
        self.logger = logging.getLogger("mcp_tool.web")
        
    async def setup(self):
        await super().setup()
        self.session = aiohttp.ClientSession()
        
    async def teardown(self):
        await self.session.close()
        await super().teardown()
        
    @endpoint("fetch_url")
    async def fetch_url(self, url: str) -> dict:
        """
        从URL获取网页内容
        
        Args:
            url: 要获取的URL
            
        Returns:
            包含网页内容和元数据的字典
        """
        try:
            self.logger.info(f"正在获取URL: {url}")
            async with self.session.get(url) as response:
                if response.status != 200:
                    return {
                        "success": False,
                        "error": f"HTTP错误: {response.status}",
                        "content": None
                    }
                    
                html = await response.text()
                
                # 使用BeautifulSoup解析HTML
                soup = BeautifulSoup(html, 'html.parser')
                
                # 提取标题
                title = soup.title.string if soup.title else "无标题"
                
                # 提取正文内容
                # 移除脚本、样式和导航元素
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                    
                text = soup.get_text(separator='\n', strip=True)
                
                # 如果内容过长，进行简单摘要
                if len(text) > 5000:
                    text = text[:5000] + "... (内容已截断)"
                    
                return {
                    "success": True,
                    "url": url,
                    "title": title,
                    "content": text,
                    "status_code": response.status
                }
                
        except Exception as e:
            self.logger.error(f"获取URL失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "content": None
            }
```

#### 3.2 搜索工具

在`app/agents/tools/search_tool_mcp.py`中实现:

```python
from app.agents.tools.mcp_tool import MCPTool
from mcp_sdk.plugin import endpoint
import aiohttp
import os
import logging
from typing import List, Dict, Any

class SearchToolMCP(MCPTool):
    """MCP兼容的搜索工具"""
    
    def __init__(self):
        super().__init__(
            name="search_tool",
            description="用于在互联网上搜索信息的工具"
        )
        self.logger = logging.getLogger("mcp_tool.search")
        self.api_key = os.getenv("SEARCH_API_KEY")
        self.search_engine_id = os.getenv("SEARCH_ENGINE_ID")
        
    async def setup(self):
        await super().setup()
        self.session = aiohttp.ClientSession()
        if not self.api_key or not self.search_engine_id:
            self.logger.warning("搜索API密钥或引擎ID未设置，搜索功能可能无法正常工作")
        
    async def teardown(self):
        await self.session.close()
        await super().teardown()
        
    @endpoint("search")
    async def search(self, query: str, limit: int = 5) -> dict:
        """
        执行互联网搜索
        
        Args:
            query: 搜索查询
            limit: 返回的结果数量
            
        Returns:
            包含搜索结果的字典
        """
        try:
            self.logger.info(f"正在搜索: {query}")
            
            if not self.api_key or not self.search_engine_id:
                return {
                    "success": False,
                    "error": "搜索API未配置",
                    "results": []
                }
                
            # 使用Google自定义搜索API
            search_url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": self.api_key,
                "cx": self.search_engine_id,
                "q": query,
                "num": min(limit, 10)  # API限制最多10个结果
            }
            
            async with self.session.get(search_url, params=params) as response:
                if response.status != 200:
                    return {
                        "success": False,
                        "error": f"搜索API错误: {response.status}",
                        "results": []
                    }
                    
                data = await response.json()
                
                # 解析搜索结果
                results = []
                if "items" in data:
                    for item in data["items"]:
                        results.append({
                            "title": item.get("title", ""),
                            "link": item.get("link", ""),
                            "snippet": item.get("snippet", ""),
                            "displayLink": item.get("displayLink", "")
                        })
                
                return {
                    "success": True,
                    "query": query,
                    "results": results,
                    "total_results": data.get("searchInformation", {}).get("totalResults", "0")
                }
                
        except Exception as e:
            self.logger.error(f"搜索失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "results": []
            }
```

### 4. API集成

更新查询API以支持MCP工具:

```python
# 更新app/api/query.py

from app.llm.mcp_manager import mcp_manager
from app.agents.tools.mcp_tool import MCPTool
import importlib
import inspect
import os
import pkgutil

# 动态发现并注册MCP工具
def discover_mcp_tools():
    """发现项目中所有MCP工具"""
    tools = []
    package_dir = os.path.dirname(os.path.abspath(__file__))
    tools_dir = os.path.join(package_dir, "..", "agents", "tools")
    
    for (_, name, _) in pkgutil.iter_modules([tools_dir]):
        if name.endswith("_mcp"):
            try:
                module = importlib.import_module(f"app.agents.tools.{name}")
                for _, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, MCPTool) and 
                        obj is not MCPTool):
                        tools.append(obj.__name__)
            except ImportError as e:
                logging.error(f"导入工具模块失败: {name}, 错误: {str(e)}")
                
    return tools

# 更新查询API端点
@router.post("/query", response_model=QueryResponse)
async def create_query(query_request: QueryRequest, db = Depends(get_db)):
    """
    创建新的查询
    """
    # ... 现有代码 ...
    
    # 使用MCP工具代理
    tool_agent = ToolAgent(llm_service)
    
    # 初始化MCP工具
    mcp_tools = discover_mcp_tools()
    await tool_agent.initialize_mcp_tools(mcp_tools)
    
    try:
        # 执行查询
        result = await tool_agent.execute_with_mcp(
            query=query_request.query,
            show_reasoning=query_request.show_reasoning
        )
        
        # ... 保存查询结果到数据库等其他现有代码 ...
        
        return query_response
    finally:
        # 清理资源
        tool_agent.cleanup()
```

## 示例: 使用MCP工具

```python
from app.agents.tool_agent import ToolAgent
from app.llm.llm_service import llm_service

async def example_usage():
    # 创建工具代理
    agent = ToolAgent(llm_service)
    
    # 初始化MCP工具
    tools = ["WebToolMCP", "SearchToolMCP"]
    await agent.initialize_mcp_tools(tools)
    
    try:
        # 执行查询
        result = await agent.execute_with_mcp(
            query="查找关于人工智能最新发展的信息并总结要点",
            show_reasoning=True
        )
        
        print(f"响应: {result['response']}")
        print(f"用时: {result['elapsed_time']:.2f}秒")
        print(f"使用的工具: {result['tools_used']}")
    finally:
        # 清理资源
        agent.cleanup()
```

## 集成测试

创建一个测试脚本`tests/test_mcp.py`:

```python
import asyncio
import pytest
from app.llm.mcp_manager import mcp_manager
from app.agents.tools.web_tool_mcp import WebToolMCP
from app.agents.tool_agent import ToolAgent
from app.llm.llm_service import llm_service

@pytest.mark.asyncio
async def test_mcp_manager():
    """测试MCP管理器"""
    # 启动服务器
    result = mcp_manager.start_server("test_server", 8765, ["WebToolMCP"])
    assert result is True
    
    # 列出服务器
    servers = mcp_manager.list_servers()
    assert len(servers) > 0
    assert any(s["name"] == "test_server" for s in servers)
    
    # 获取服务器信息
    info = mcp_manager.get_server_info("test_server")
    assert info is not None
    assert info["port"] == 8765
    
    # 停止服务器
    result = mcp_manager.stop_server("test_server")
    assert result is True
    
    # 验证服务器已停止
    servers = mcp_manager.list_servers()
    assert not any(s["name"] == "test_server" for s in servers)

@pytest.mark.asyncio
async def test_web_tool():
    """测试MCP网页工具"""
    tool = WebToolMCP()
    await tool.setup()
    
    try:
        # 测试获取网页
        result = await tool.fetch_url("https://www.baidu.com")
        assert result["success"] is True
        assert "百度" in result["title"]
        assert len(result["content"]) > 0
    finally:
        await tool.teardown()

@pytest.mark.asyncio
async def test_tool_agent_with_mcp():
    """测试使用MCP的工具代理"""
    agent = ToolAgent(llm_service)
    
    # 初始化MCP工具
    result = await agent.initialize_mcp_tools(["WebToolMCP"])
    assert result is True
    
    try:
        # 执行简单查询
        query = "百度的首页有什么内容?"
        result = await agent.execute_with_mcp(query)
        
        assert "response" in result
        assert len(result["response"]) > 0
        assert "tools_used" in result
        assert "WebToolMCP" in result["tools_used"]
    finally:
        agent.cleanup()
```

## 注意事项

1. **配置管理**:
   - 确保在环境变量或配置文件中设置所需的API密钥。
   - 考虑为不同的MCP服务器使用不同的端口。

2. **错误处理**:
   - 实现全面的错误处理，以防工具执行失败。
   - 确保资源正确清理，特别是在出现异常时。

3. **性能考虑**:
   - MCP服务器启动需要时间，考虑实现服务器池以提高性能。
   - 对于频繁使用的工具，可以保持服务器长时间运行。

4. **安全性**:
   - 限制MCP服务器只接受本地连接，除非有特殊需求。
   - 实现访问控制和身份验证机制，特别是对于生产环境。

## 未来扩展

1. **工具市场**:
   - 创建一个工具仓库，允许轻松添加和管理MCP工具。
   - 实现工具版本控制和依赖管理。

2. **高级功能**:
   - 实现工具组合和工作流，自动调度一系列MCP工具。
   - 添加工具使用监控和分析功能。

3. **分布式部署**:
   - 允许在多个服务器上运行MCP服务，实现负载均衡。
   - 实现云原生部署支持。 