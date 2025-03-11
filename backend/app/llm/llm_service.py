"""
LLM服务模块，集成OpenAI等LLM服务
"""
import json
from typing import Dict, List, Literal, Optional, Union, Any

from openai import AsyncOpenAI
from pydantic import BaseModel

from app.config import config
from app.utils import logger


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


class LLMService:
    """LLM服务类"""
    
    _instances: Dict[str, "LLMService"] = {}
    
    def __new__(cls, config_name: str = "default"):
        """单例模式"""
        if config_name not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[config_name] = instance
            return instance
        return cls._instances[config_name]
    
    def __init__(self, config_name: str = "default"):
        """初始化"""
        if not hasattr(self, "client"):
            llm_config = config.llm.get(config_name)
            if not llm_config:
                raise ValueError(f"LLM配置 '{config_name}' 不存在")
            
            self.model = llm_config.model
            self.max_tokens = llm_config.max_tokens
            self.temperature = llm_config.temperature
            self.api_key = llm_config.api_key
            self.api_base_url = llm_config.api_base_url
            
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.api_base_url
            )
    
    @staticmethod
    def format_messages(messages: List[Union[dict, Message]]) -> List[dict]:
        """
        格式化消息列表
        """
        formatted_messages = []
        
        for message in messages:
            if isinstance(message, dict):
                if "role" not in message:
                    raise ValueError("消息字典必须包含'role'字段")
                formatted_messages.append(message)
            elif isinstance(message, Message):
                formatted_messages.append(message.to_dict())
            else:
                raise TypeError(f"不支持的消息类型: {type(message)}")
        
        # 验证所有消息都有必要的字段
        for msg in formatted_messages:
            if msg["role"] not in ["system", "user", "assistant", "tool"]:
                raise ValueError(f"无效的角色: {msg['role']}")
            if "content" not in msg and "tool_calls" not in msg:
                raise ValueError("消息必须包含'content'或'tool_calls'")
        
        return formatted_messages
    
    async def chat(
        self,
        messages: List[Union[dict, Message]],
        system_msgs: Optional[List[Union[dict, Message]]] = None,
        stream: bool = False,
        temperature: Optional[float] = None,
    ) -> str:
        """
        发送聊天请求并获取响应
        """
        try:
            # 格式化系统和用户消息
            if system_msgs:
                system_msgs = self.format_messages(system_msgs)
                messages = system_msgs + self.format_messages(messages)
            else:
                messages = self.format_messages(messages)
            
            if not stream:
                # 非流式请求
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=self.max_tokens,
                    temperature=temperature or self.temperature,
                    stream=False,
                )
                
                if not response.choices or not response.choices[0].message.content:
                    raise ValueError("LLM响应为空或无效")
                
                return response.choices[0].message.content
            
            # 流式请求
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=temperature or self.temperature,
                stream=True,
            )
            
            collected_messages = []
            async for chunk in response:
                chunk_message = chunk.choices[0].delta.content or ""
                collected_messages.append(chunk_message)
            
            full_response = "".join(collected_messages).strip()
            if not full_response:
                raise ValueError("LLM流式响应为空")
            
            return full_response
        
        except Exception as e:
            logger.error(f"LLM请求错误: {e}")
            raise
    
    async def chat_with_tools(
        self,
        messages: List[Union[dict, Message]],
        system_msgs: Optional[List[Union[dict, Message]]] = None,
        tools: Optional[List[dict]] = None,
        tool_choice: Optional[str] = None,
        temperature: Optional[float] = None,
    ):
        """
        使用工具功能与LLM交互
        """
        try:
            # 格式化消息
            if system_msgs:
                system_msgs = self.format_messages(system_msgs)
                messages = system_msgs + self.format_messages(messages)
            else:
                messages = self.format_messages(messages)
            
            # 设置工具调用请求
            kwargs = {}
            if tools:
                kwargs["tools"] = tools
            if tool_choice:
                kwargs["tool_choice"] = tool_choice
            
            # 发送请求
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=self.max_tokens,
                **kwargs,
            )
            
            # 检查响应是否有效
            if not response.choices or not response.choices[0].message:
                logger.error(f"无效或空的LLM响应: {response}")
                raise ValueError("LLM响应无效或为空")
            
            return response.choices[0].message
        
        except Exception as e:
            logger.error(f"LLM工具调用错误: {e}")
            raise 