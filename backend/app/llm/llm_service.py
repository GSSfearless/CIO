"""
LLM服务模块，集成多种LLM服务
"""
import os
from typing import Dict, List, Optional, Union, Any

from app.config import config
from app.utils import logger
from app.llm.message import Message
from app.llm.llm_adapters import create_llm_adapter, LLMAdapter


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
        if not hasattr(self, "adapter"):
            llm_config = config.llm.get(config_name)
            if not llm_config:
                raise ValueError(f"LLM配置 '{config_name}' 不存在")
            
            self.model = llm_config.model
            self.max_tokens = llm_config.max_tokens
            self.temperature = llm_config.temperature
            
            # 创建适配器
            provider = llm_config.provider or os.environ.get("LLM_PROVIDER", "zhipu")
            
            # 根据provider创建适配器
            self.adapter = create_llm_adapter(
                provider=provider,
                api_key=llm_config.api_key,
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            logger.info(f"已初始化LLM服务，使用提供商: {provider}，模型: {self.model}")
    
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
            
            # 使用适配器进行聊天
            if stream:
                logger.warning("当前版本不支持流式请求，将使用普通请求")
            
            response = await self.adapter.chat(
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response
            
        except Exception as e:
            logger.error(f"LLM请求错误: {e}")
            return f"LLM请求错误: {str(e)}"
    
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
        
        注意：此功能目前仅OpenAI和部分模型支持
        """
        logger.warning("chat_with_tools功能可能不被所有模型支持")
        
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
            
            # 使用适配器进行工具调用
            # 注意: 并非所有适配器都支持此功能
            response = await self.adapter.chat(
                messages=messages,
                temperature=temperature or self.temperature,
                **kwargs
            )
            
            return response
        
        except Exception as e:
            logger.error(f"LLM工具调用错误: {e}")
            raise


async def process_query(
    query: str,
    focus_id: Optional[str] = None,
    context_info: Optional[List[Dict[str, Any]]] = None,
    show_reasoning: bool = False
) -> str:
    """
    处理用户查询
    
    Args:
        query: 用户查询内容
        focus_id: 关注点ID
        context_info: 上下文信息列表
        show_reasoning: 是否显示推理过程
        
    Returns:
        str: 处理结果
    """
    # 导入工具代理
    from app.agents.tool_agent import ToolAgent
    
    try:
        # 创建工具代理
        agent = ToolAgent()
        
        # 准备上下文信息
        context = ""
        if context_info:
            context = "相关上下文信息:\n"
            for i, info in enumerate(context_info, 1):
                context += f"{i}. {info.get('title', '无标题')}: {info.get('content', '无内容')[:200]}...\n"
        
        # 如果有关注点，添加到上下文
        if focus_id:
            try:
                from app.models.pocketbase import PocketBase
                
                db = PocketBase()
                focus_point = await db.get_record("focus_points", focus_id)
                
                if focus_point:
                    if context:
                        context += "\n"
                    context += f"当前关注点: {focus_point.get('focuspoint', '')}\n"
                    explanation = focus_point.get('explanation')
                    if explanation:
                        context += f"关注点说明: {explanation}\n"
            except Exception as e:
                logger.error(f"获取关注点信息失败: {e}")
        
        # 处理查询，显示或隐藏推理过程
        response = await agent.process(
            query, 
            context=context if context else None,
            show_reasoning=show_reasoning
        )
        
        # 清理资源
        await agent.cleanup()
        
        return response
        
    except Exception as e:
        logger.error(f"处理查询失败: {e}")
        return f"处理查询时出现错误: {str(e)}" 