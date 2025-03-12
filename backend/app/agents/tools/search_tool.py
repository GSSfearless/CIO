"""
搜索工具
通过搜索引擎API搜索信息
"""
from typing import List, Optional
from pydantic import BaseModel, Field

from app.agents.tools.base_tool import BaseTool, ToolInput, ToolOutput
from app.scrapers.search_engine import create_search_engine, SearchResult
from app.utils import logger


class SearchToolInput(ToolInput):
    """搜索工具输入参数"""
    query: str = Field(..., description="搜索查询")
    engine: str = Field(default="zhipu", description="搜索引擎类型（zhipu）")
    max_results: int = Field(default=5, description="返回的最大结果数量")


class SearchToolOutput(ToolOutput):
    """搜索工具输出结果"""
    results: List[SearchResult] = Field(default_factory=list, description="搜索结果列表")
    total_found: int = Field(default=0, description="找到的结果总数")
    query: str = Field(..., description="执行的搜索查询")
    message: Optional[str] = Field(default=None, description="额外信息或错误消息")
    success: bool = Field(default=True, description="搜索是否成功")


class SearchTool(BaseTool):
    """搜索工具实现"""
    
    name: str = "search"
    description: str = "通过搜索引擎搜索网络上的信息"
    input_schema = SearchToolInput
    output_schema = SearchToolOutput
    
    async def _run(self, input_data: SearchToolInput) -> SearchToolOutput:
        """
        运行搜索工具
        
        Args:
            input_data: 搜索工具输入参数
            
        Returns:
            SearchToolOutput: 搜索工具输出结果
        """
        try:
            # 创建搜索引擎实例
            search_engine = create_search_engine(input_data.engine)
            
            # 执行搜索
            results = await search_engine.search(input_data.query, force_update=True)
            
            # 限制结果数量
            limited_results = results[:input_data.max_results]
            
            # 返回结果
            return SearchToolOutput(
                results=limited_results,
                total_found=len(results),
                query=input_data.query,
                success=True
            )
        
        except Exception as e:
            logger.error(f"搜索工具执行失败: {e}")
            return SearchToolOutput(
                results=[],
                total_found=0,
                query=input_data.query,
                message=f"搜索失败: {str(e)}",
                success=False
            ) 