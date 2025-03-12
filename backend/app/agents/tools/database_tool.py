"""
数据库查询工具
用于查询系统数据库中的信息
"""
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field

from app.agents.tools.base_tool import BaseTool, ToolInput, ToolOutput
from app.models.pocketbase import PocketBase
from app.models.schemas import Info, FocusPoint, Source
from app.utils import logger


class DatabaseToolInput(ToolInput):
    """数据库查询工具输入参数"""
    collection: str = Field(..., description="要查询的集合名称（info, focus_points, sources等）")
    filter_params: Optional[Dict[str, Any]] = Field(default={}, description="过滤参数")
    limit: int = Field(default=10, description="返回的最大结果数量")
    sort: Optional[List[str]] = Field(default=None, description="排序条件，例如['-created']")
    skip: int = Field(default=0, description="跳过的结果数量")


class DatabaseToolOutput(ToolOutput):
    """数据库查询工具输出结果"""
    results: List[Dict[str, Any]] = Field(default_factory=list, description="查询结果列表")
    total: int = Field(default=0, description="结果总数")
    collection: str = Field(..., description="查询的集合名称")
    message: Optional[str] = Field(default=None, description="额外信息或错误消息")
    success: bool = Field(default=True, description="查询是否成功")


class DatabaseTool(BaseTool):
    """数据库查询工具实现"""
    
    name: str = "database_query"
    description: str = "查询系统数据库中的信息"
    input_schema = DatabaseToolInput
    output_schema = DatabaseToolOutput
    
    async def _run(self, input_data: DatabaseToolInput) -> DatabaseToolOutput:
        """
        运行数据库查询工具
        
        Args:
            input_data: 数据库查询工具输入参数
            
        Returns:
            DatabaseToolOutput: 数据库查询工具输出结果
        """
        try:
            # 创建数据库连接
            db = PocketBase()
            
            # 执行查询
            response = await db.get_collection_list(
                input_data.collection,
                filter_params=input_data.filter_params,
                skip=input_data.skip,
                limit=input_data.limit,
                sort=input_data.sort
            )
            
            # 将结果转换为适当的模型
            processed_results = []
            if input_data.collection == "info":
                processed_results = [Info.from_dict(item).dict() for item in response]
            elif input_data.collection == "focus_points":
                processed_results = [FocusPoint.from_dict(item).dict() for item in response]
            elif input_data.collection == "sources":
                processed_results = [Source.from_dict(item).dict() for item in response]
            else:
                processed_results = response
            
            # 返回结果
            return DatabaseToolOutput(
                results=processed_results,
                total=len(processed_results),
                collection=input_data.collection,
                success=True
            )
        
        except Exception as e:
            logger.error(f"数据库查询工具执行失败: {e}")
            return DatabaseToolOutput(
                results=[],
                total=0,
                collection=input_data.collection,
                message=f"查询失败: {str(e)}",
                success=False
            ) 