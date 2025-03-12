"""
消息模型模块
用于表示与LLM交互的消息
"""
from typing import Dict, List, Literal, Optional, Any

from pydantic import BaseModel, Field


class Message(BaseModel):
    """消息模型"""
    role: Literal["system", "user", "assistant", "tool"] = "user"
    content: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None
    
    @classmethod
    def system_message(cls, content: str) -> "Message":
        """创建系统消息"""
        return cls(role="system", content=content)
    
    @classmethod
    def user_message(cls, content: str) -> "Message":
        """创建用户消息"""
        return cls(role="user", content=content)
    
    @classmethod
    def assistant_message(cls, content: str) -> "Message":
        """创建助手消息"""
        return cls(role="assistant", content=content)
    
    @classmethod
    def tool_message(cls, content: str, tool_call_id: str) -> "Message":
        """创建工具消息"""
        return cls(role="tool", content=content, tool_call_id=tool_call_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {"role": self.role}
        
        if self.content is not None:
            result["content"] = self.content
        
        if self.tool_calls is not None:
            result["tool_calls"] = self.tool_calls
        
        if self.tool_call_id is not None:
            result["tool_call_id"] = self.tool_call_id
            
        if self.name is not None:
            result["name"] = self.name
            
        return result 