"""
工具基类
所有工具都应继承此基类，并实现相应的方法
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, Type

from pydantic import BaseModel, Field


class ToolInput(BaseModel):
    """工具输入参数基类"""
    pass


class ToolOutput(BaseModel):
    """工具输出结果基类"""
    pass


class BaseTool(ABC):
    """工具基类"""
    
    name: str = ""
    description: str = ""
    input_schema: Type[ToolInput] = ToolInput
    output_schema: Type[ToolOutput] = ToolOutput
    
    def __init__(self, **kwargs):
        """
        初始化工具
        
        Args:
            **kwargs: 其他参数
        """
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @abstractmethod
    async def _run(self, input_data: ToolInput) -> ToolOutput:
        """
        运行工具的具体实现
        
        Args:
            input_data: 工具输入参数
            
        Returns:
            ToolOutput: 工具输出结果
        """
        pass
    
    async def run(self, input_data: Union[Dict[str, Any], ToolInput]) -> ToolOutput:
        """
        运行工具
        
        Args:
            input_data: 工具输入参数，可以是字典或ToolInput实例
            
        Returns:
            ToolOutput: 工具输出结果
        """
        # 如果输入是字典，转换为ToolInput实例
        if isinstance(input_data, dict):
            input_data = self.input_schema(**input_data)
        
        # 运行工具
        return await self._run(input_data)
    
    def get_schema(self) -> Dict[str, Any]:
        """
        获取工具的模式定义
        
        Returns:
            Dict[str, Any]: 工具的模式定义
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.input_schema.schema(),
            "returns": self.output_schema.schema()
        }
    
    @classmethod
    def available_tools(cls) -> List[Type["BaseTool"]]:
        """
        获取所有可用的工具类型
        
        Returns:
            List[Type["BaseTool"]]: 所有可用的工具类型
        """
        return cls.__subclasses__() 