"""
大语言模型适配器模块
为不同的LLM服务提供统一的接口
"""
from abc import ABC, abstractmethod
import os
import json
import asyncio
from typing import List, Dict, Any, Optional, Union
import httpx

from app.utils import logger
from app.llm.message import Message


class LLMAdapter(ABC):
    """
    LLM适配器基类
    为不同的LLM服务提供统一的接口
    """
    
    @abstractmethod
    async def chat(
        self,
        messages: List[Union[Dict[str, Any], Message]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """
        与LLM交互的通用方法
        
        Args:
            messages: 消息列表
            temperature: 温度参数，控制随机性
            max_tokens: 最大生成token数
            **kwargs: 其他参数
            
        Returns:
            str: LLM的响应
        """
        pass
    
    @staticmethod
    def format_messages(messages: List[Union[Dict[str, Any], Message]]) -> List[Dict[str, Any]]:
        """
        格式化消息列表为标准格式
        
        Args:
            messages: 消息列表
            
        Returns:
            List[Dict[str, Any]]: 格式化后的消息列表
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
        
        return formatted_messages
    
    @staticmethod
    def _mock_response(messages: List[Union[Dict[str, Any], Message]]) -> str:
        """
        生成模拟响应（当API未配置时使用）
        
        Args:
            messages: 消息列表
            
        Returns:
            str: 模拟的响应文本
        """
        logger.warning("使用模拟模式生成响应")
        
        # 找出最后一条用户消息
        user_message = ""
        formatted_messages = LLMAdapter.format_messages(messages)
        for msg in reversed(formatted_messages):
            if msg["role"] == "user":
                user_message = msg["content"]
                break
        
        if not user_message:
            return "我没有收到任何问题，请问有什么可以帮助您的？"
        
        # 根据问题类型返回简单回答
        if "天气" in user_message:
            return "我无法获取实时天气信息，请查看天气预报应用或网站了解最新天气情况。"
        elif "时间" in user_message:
            return "我无法获取当前时间，请查看您的设备时钟。"
        elif "名字" in user_message:
            return "我是CIO的AI助手，很高兴能帮助您。"
        else:
            return "很抱歉，由于我正在模拟模式下运行，无法提供准确的回答。请确保正确配置API密钥以获取更好的体验。"


class OpenAIAdapter(LLMAdapter):
    """
    OpenAI API适配器
    支持OpenAI API及兼容接口
    """
    
    def __init__(
        self,
        api_key: str = "",
        api_base_url: str = "https://api.openai.com/v1",
        model: str = "gpt-3.5-turbo",
        max_tokens: int = 2000,
        temperature: float = 0.7
    ):
        """
        初始化OpenAI适配器
        
        Args:
            api_key: API密钥
            api_base_url: API基础URL
            model: 模型名称
            max_tokens: 最大生成token数
            temperature: 温度参数
        """
        self.api_key = api_key
        self.api_base_url = api_base_url
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # 用于限制并发请求的信号量
        self.semaphore = asyncio.Semaphore(1)
        
        # 检查API密钥是否配置
        self.mock_mode = not bool(self.api_key)
        if self.mock_mode:
            logger.warning("OpenAI API密钥未设置，将使用模拟模式")
    
    async def chat(
        self,
        messages: List[Union[Dict[str, Any], Message]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        调用OpenAI API进行聊天生成
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大生成token数
            **kwargs: 其他参数
            
        Returns:
            str: 生成的响应文本
        """
        if self.mock_mode:
            return self._mock_response(messages)
        
        # 格式化消息
        formatted_messages = self.format_messages(messages)
        
        # 设置参数
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens
        
        try:
            # 获取信号量，限制并发请求
            async with self.semaphore:
                # 构建API请求参数
                url = f"{self.api_base_url}/chat/completions"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                }
                payload = {
                    "model": self.model,
                    "messages": formatted_messages,
                    "temperature": temp,
                    "max_tokens": tokens,
                    **kwargs,
                }
                
                # 发送请求
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        url=url,
                        headers=headers,
                        json=payload,
                        timeout=120,  # 较长的超时时间
                    )
                    
                    # 解析响应
                    if response.status_code != 200:
                        logger.error(f"OpenAI API错误: {response.status_code}, {response.text}")
                        return f"OpenAI API调用失败: HTTP {response.status_code}"
                    
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    return content
        
        except Exception as e:
            logger.error(f"OpenAI调用出错: {str(e)}")
            return f"API调用出错: {str(e)}"


class ZhipuAdapter(LLMAdapter):
    """
    智谱AI适配器
    支持智谱AI的API
    """
    
    def __init__(
        self,
        api_key: str = "",
        model: str = "glm-4",
        max_tokens: int = 2000,
        temperature: float = 0.7
    ):
        """
        初始化智谱AI适配器
        
        Args:
            api_key: API密钥
            model: 模型名称
            max_tokens: 最大生成token数
            temperature: 温度参数
        """
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # 检查API密钥是否配置
        self.mock_mode = not bool(self.api_key)
        if self.mock_mode:
            logger.warning("智谱AI API密钥未设置，将使用模拟模式")
    
    async def chat(
        self,
        messages: List[Union[Dict[str, Any], Message]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        调用智谱AI API进行聊天生成
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大生成token数
            **kwargs: 其他参数
            
        Returns:
            str: 生成的响应文本
        """
        if self.mock_mode:
            return self._mock_response(messages)
        
        # 格式化消息
        formatted_messages = self.format_messages(messages)
        
        # 设置参数
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens
        
        try:
            # 构建API请求参数
            url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": self.api_key,
            }
            payload = {
                "model": self.model,
                "messages": formatted_messages,
                "temperature": temp,
                "max_tokens": tokens,
                **kwargs,
            }
            
            # 发送请求
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url=url,
                    headers=headers,
                    json=payload,
                    timeout=120,  # 较长的超时时间
                )
                
                # 解析响应
                if response.status_code != 200:
                    logger.error(f"智谱AI API错误: {response.status_code}, {response.text}")
                    return f"智谱AI API调用失败: HTTP {response.status_code}"
                
                data = response.json()
                
                # 智谱AI的响应格式
                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0]["message"]["content"]
                    return content
                else:
                    logger.error(f"智谱AI响应格式错误: {data}")
                    return "智谱AI响应格式错误"
        
        except Exception as e:
            logger.error(f"智谱AI调用出错: {str(e)}")
            return f"API调用出错: {str(e)}"


class BaiduAdapter(LLMAdapter):
    """
    百度文心一言适配器
    支持百度文心一言的API
    """
    
    def __init__(
        self,
        api_key: str = "",
        secret_key: str = "",
        model: str = "ernie-bot-4",
        max_tokens: int = 2000,
        temperature: float = 0.7
    ):
        """
        初始化百度文心一言适配器
        
        Args:
            api_key: API密钥
            secret_key: 密钥
            model: 模型名称
            max_tokens: 最大生成token数
            temperature: 温度参数
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.access_token = None
        
        # 检查API密钥是否配置
        self.mock_mode = not (bool(self.api_key) and bool(self.secret_key))
        if self.mock_mode:
            logger.warning("百度API密钥未设置，将使用模拟模式")
    
    async def _get_access_token(self) -> str:
        """
        获取百度API访问令牌
        
        Returns:
            str: 访问令牌
        """
        url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={self.api_key}&client_secret={self.secret_key}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url)
            result = response.json()
            if "access_token" in result:
                return result["access_token"]
            else:
                logger.error(f"获取百度访问令牌失败: {result}")
                raise Exception("获取百度访问令牌失败")
    
    async def chat(
        self,
        messages: List[Union[Dict[str, Any], Message]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        调用百度文心一言API进行聊天生成
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大生成token数
            **kwargs: 其他参数
            
        Returns:
            str: 生成的响应文本
        """
        if self.mock_mode:
            return self._mock_response(messages)
        
        # 格式化消息
        formatted_messages = self.format_messages(messages)
        
        # 设置参数
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens
        
        try:
            # 获取访问令牌
            if not self.access_token:
                self.access_token = await self._get_access_token()
            
            # 构建API请求参数
            url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/{self.model}?access_token={self.access_token}"
            headers = {
                "Content-Type": "application/json",
            }
            
            # 百度API需要特殊处理消息格式
            payload = {
                "messages": formatted_messages,
                "temperature": temp,
                "top_p": 0.8,
                "stream": False,
            }
            
            # 发送请求
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url=url,
                    headers=headers,
                    json=payload,
                    timeout=120,  # 较长的超时时间
                )
                
                # 解析响应
                if response.status_code != 200:
                    logger.error(f"百度API错误: {response.status_code}, {response.text}")
                    return f"百度API调用失败: HTTP {response.status_code}"
                
                data = response.json()
                
                # 百度的响应格式
                if "result" in data:
                    return data["result"]
                else:
                    logger.error(f"百度响应格式错误: {data}")
                    return "百度响应格式错误"
        
        except Exception as e:
            logger.error(f"百度API调用出错: {str(e)}")
            return f"API调用出错: {str(e)}"


class XunfeiAdapter(LLMAdapter):
    """
    讯飞星火认知大模型适配器
    支持讯飞星火认知大模型的API
    """
    
    def __init__(
        self,
        app_id: str = "",
        api_key: str = "",
        api_secret: str = "",
        model: str = "general",
        max_tokens: int = 2000,
        temperature: float = 0.7
    ):
        """
        初始化讯飞星火认知大模型适配器
        
        Args:
            app_id: 应用ID
            api_key: API密钥
            api_secret: API密钥
            model: 模型名称
            max_tokens: 最大生成token数
            temperature: 温度参数
        """
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # 检查API密钥是否配置
        self.mock_mode = not (bool(self.app_id) and bool(self.api_key) and bool(self.api_secret))
        if self.mock_mode:
            logger.warning("讯飞API密钥未设置，将使用模拟模式")
    
    async def chat(
        self,
        messages: List[Union[Dict[str, Any], Message]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        调用讯飞星火认知大模型API进行聊天生成
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大生成token数
            **kwargs: 其他参数
            
        Returns:
            str: 生成的响应文本
        """
        if self.mock_mode:
            return self._mock_response(messages)
        
        # 格式化消息
        formatted_messages = self.format_messages(messages)
        
        # 设置参数
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens
        
        # 讯飞API需要特殊处理消息格式
        xunfei_messages = []
        for msg in formatted_messages:
            xunfei_messages.append({
                "role": msg["role"],
                "content": msg["content"],
            })
        
        try:
            # 导入讯飞SDK
            import hmac
            import base64
            import hashlib
            import time
            from datetime import datetime
            from urllib.parse import urlencode
            
            # 生成认证URL
            def generate_url():
                # 生成RFC1123格式的时间戳
                now = datetime.now()
                date = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
                
                # 拼接字符串
                signature_origin = f"host: spark-api.xf-yun.com\ndate: {date}\nGET /v1.1/chat HTTP/1.1"
                
                # 使用hmac-sha256进行加密
                signature_sha = hmac.new(
                    self.api_secret.encode('utf-8'),
                    signature_origin.encode('utf-8'),
                    digestmod=hashlib.sha256
                ).digest()
                
                signature_sha_base64 = base64.b64encode(signature_sha).decode()
                authorization_origin = f"api_key=\"{self.api_key}\", algorithm=\"hmac-sha256\", headers=\"host date request-line\", signature=\"{signature_sha_base64}\""
                authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode()
                
                # 将请求的鉴权参数组合为字典
                params = {
                    "authorization": authorization,
                    "date": date,
                    "host": "spark-api.xf-yun.com"
                }
                
                # 拼接鉴权参数，生成url
                spark_url = f"https://spark-api.xf-yun.com/v1.1/chat?{urlencode(params)}"
                return spark_url
            
            # 构建API请求
            url = generate_url()
            headers = {
                "Content-Type": "application/json",
            }
            
            payload = {
                "header": {
                    "app_id": self.app_id,
                    "uid": "user",
                },
                "parameter": {
                    "chat": {
                        "domain": self.model,
                        "temperature": temp,
                        "max_tokens": tokens,
                    },
                },
                "payload": {
                    "message": {
                        "text": xunfei_messages,
                    },
                },
            }
            
            # 发送请求
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url=url,
                    headers=headers,
                    json=payload,
                    timeout=120,  # 较长的超时时间
                )
                
                # 解析响应
                if response.status_code != 200:
                    logger.error(f"讯飞API错误: {response.status_code}, {response.text}")
                    return f"讯飞API调用失败: HTTP {response.status_code}"
                
                data = response.json()
                
                # 讯飞的响应格式
                if "payload" in data and "choices" in data["payload"] and "text" in data["payload"]["choices"]:
                    return data["payload"]["choices"]["text"][0]["content"]
                else:
                    logger.error(f"讯飞响应格式错误: {data}")
                    return "讯飞响应格式错误"
        
        except Exception as e:
            logger.error(f"讯飞API调用出错: {str(e)}")
            return f"API调用出错: {str(e)}"


def create_llm_adapter(provider: str = "zhipu", **kwargs) -> LLMAdapter:
    """
    创建LLM适配器实例
    
    Args:
        provider: LLM提供商
        **kwargs: 其他参数
        
    Returns:
        LLMAdapter: LLM适配器实例
    """
    # 读取环境变量中的API密钥
    if provider == "openai":
        api_key = kwargs.get("api_key", os.environ.get("OPENAI_API_KEY", ""))
        api_base_url = kwargs.get("api_base_url", os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1"))
        model = kwargs.get("model", os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo"))
        return OpenAIAdapter(api_key=api_key, api_base_url=api_base_url, model=model)
    
    elif provider == "zhipu":
        api_key = kwargs.get("api_key", os.environ.get("ZHIPU_API_KEY", ""))
        model = kwargs.get("model", os.environ.get("ZHIPU_MODEL", "glm-4"))
        return ZhipuAdapter(api_key=api_key, model=model)
    
    elif provider == "baidu":
        api_key = kwargs.get("api_key", os.environ.get("BAIDU_API_KEY", ""))
        secret_key = kwargs.get("secret_key", os.environ.get("BAIDU_SECRET_KEY", ""))
        model = kwargs.get("model", os.environ.get("BAIDU_MODEL", "ernie-bot-4"))
        return BaiduAdapter(api_key=api_key, secret_key=secret_key, model=model)
    
    elif provider == "xunfei":
        app_id = kwargs.get("app_id", os.environ.get("XUNFEI_APP_ID", ""))
        api_key = kwargs.get("api_key", os.environ.get("XUNFEI_API_KEY", ""))
        api_secret = kwargs.get("api_secret", os.environ.get("XUNFEI_API_SECRET", ""))
        model = kwargs.get("model", os.environ.get("XUNFEI_MODEL", "general"))
        return XunfeiAdapter(app_id=app_id, api_key=api_key, api_secret=api_secret, model=model)
    
    else:
        logger.warning(f"未知的LLM提供商: {provider}，将使用智谱AI")
        api_key = kwargs.get("api_key", os.environ.get("ZHIPU_API_KEY", ""))
        model = kwargs.get("model", os.environ.get("ZHIPU_MODEL", "glm-4"))
        return ZhipuAdapter(api_key=api_key, model=model) 