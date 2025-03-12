"""
Agent基类
为所有智能代理提供基础功能
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

from app.llm import LLMService, Message
from app.utils import logger


class BaseAgent(ABC):
    """智能代理基类"""
    
    def __init__(self, llm_service: Optional[LLMService] = None, **kwargs):
        """
        初始化
        
        Args:
            llm_service: LLM服务实例，如果为None则使用默认服务
            **kwargs: 其他参数
        """
        self.llm_service = llm_service or LLMService()
        self.temperature = kwargs.get("temperature", 0.0)
        self.system_message = kwargs.get("system_message", "")
    
    async def _prepare_messages(
        self, 
        messages: List[Dict[str, Any]] = None, 
        system_message: Optional[str] = None
    ) -> List[Message]:
        """
        准备消息列表
        
        Args:
            messages: 消息列表
            system_message: 系统消息
            
        Returns:
            List[Message]: 格式化后的消息列表
        """
        result = []
        
        # 添加系统消息
        if system_message or self.system_message:
            result.append(Message.system_message(system_message or self.system_message))
        
        # 添加其他消息
        if messages:
            for msg in messages:
                if msg.get("role") == "system":
                    result.append(Message.system_message(msg.get("content", "")))
                elif msg.get("role") == "user":
                    result.append(Message.user_message(msg.get("content", "")))
                elif msg.get("role") == "assistant":
                    result.append(Message.assistant_message(msg.get("content", "")))
                elif msg.get("role") == "tool" and "content" in msg and "tool_call_id" in msg:
                    result.append(Message.tool_message(msg["content"], msg["tool_call_id"]))
        
        return result
    
    @abstractmethod
    async def process(self, *args, **kwargs) -> Any:
        """
        处理输入数据
        
        Args:
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            Any: 处理结果
        """
        pass 