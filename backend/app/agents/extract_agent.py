"""
信息提取代理
负责从原始内容中提取结构化信息
"""
import json
from typing import Dict, List, Optional, Any, Union

from pydantic import BaseModel, Field

from app.agents.base_agent import BaseAgent
from app.llm import LLMService, Message
from app.utils import logger


class Information(BaseModel):
    """提取的信息模型"""
    title: str
    content: str
    tags: List[str] = []
    relevance_score: float = 0.0
    source_url: str
    published_date: Optional[str] = None
    author: Optional[str] = None
    summary: Optional[str] = None


class ExtractAgent(BaseAgent):
    """信息提取代理"""
    
    def __init__(
        self,
        llm_service: Optional[LLMService] = None,
        focus_point: str = "",
        explanation: str = "",
        **kwargs
    ):
        """
        初始化
        
        Args:
            llm_service: LLM服务实例
            focus_point: 关注点
            explanation: 关注点解释
            **kwargs: 其他参数
        """
        super().__init__(llm_service, **kwargs)
        self.focus_point = focus_point
        self.explanation = explanation
        
        # 构建系统提示词
        self._build_system_prompt()
    
    def _build_system_prompt(self):
        """构建系统提示词"""
        if not self.focus_point:
            self.system_message = """
            你是一个专业的信息提取助手，负责从给定的文本中提取关键信息。
            你需要分析文本内容，识别其中的重要信息，并生成结构化的输出。
            """
        else:
            self.system_message = f"""
            你是一个专业的信息提取助手，负责从给定的文本中提取与特定关注点相关的信息。
            
            关注点: {self.focus_point}
            """
            
            if self.explanation:
                self.system_message += f"\n关注点解释: {self.explanation}\n"
                
            self.system_message += """
            你需要:
            1. 分析文本内容，判断其是否与关注点相关
            2. 如果相关，提取重要信息并标记相关性评分(0.0-1.0)
            3. 如果不相关，返回空列表
            
            请确保提取的信息准确、简洁，并且真实反映原文内容。不要添加不存在于原文中的信息。
            """
    
    def _create_extraction_prompt(self, content: str, url: str, author: str = "", published_date: str = "") -> str:
        """
        创建提取提示词
        
        Args:
            content: 待提取的内容
            url: 内容来源URL
            author: 作者
            published_date: 发布日期
            
        Returns:
            str: 提取提示词
        """
        prompt = f"""
        请从以下文本中提取与关注点相关的信息。

        文本来源: {url}
        """
        
        if author:
            prompt += f"作者: {author}\n"
        
        if published_date:
            prompt += f"发布日期: {published_date}\n"
        
        prompt += f"""
        文本内容:
        ```
        {content}
        ```
        
        请以JSON格式返回提取的信息，格式如下:
        ```json
        [
            {{
                "title": "信息标题",
                "content": "提取的主要内容",
                "tags": ["相关标签1", "相关标签2"],
                "relevance_score": 0.85,
                "source_url": "{url}",
                "published_date": "日期字符串",
                "author": "作者",
                "summary": "一个简短的摘要"
            }}
        ]
        ```
        
        如果内容与关注点无关，请返回空数组 `[]`。
        请确保返回的是有效的JSON格式，且只返回JSON内容，不要有其他说明文字。
        """
        
        return prompt
    
    async def _parse_response(self, response: str) -> List[Information]:
        """
        解析LLM响应
        
        Args:
            response: LLM响应文本
            
        Returns:
            List[Information]: 提取的信息列表
        """
        try:
            # 尝试提取JSON部分
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].strip()
            else:
                json_str = response.strip()
            
            # 解析JSON
            info_list = json.loads(json_str)
            result = []
            
            for info in info_list:
                try:
                    # 创建Information对象
                    information = Information(**info)
                    result.append(information)
                except Exception as e:
                    logger.warning(f"解析单条信息时出错: {e}, info: {info}")
            
            return result
        except Exception as e:
            logger.error(f"解析LLM响应时出错: {e}, response: {response}")
            return []
    
    async def process(
        self,
        content: str,
        url: str,
        author: str = "",
        published_date: str = "",
        **kwargs
    ) -> List[Information]:
        """
        处理输入内容，提取信息
        
        Args:
            content: 待提取的内容
            url: 内容来源URL
            author: 作者
            published_date: 发布日期
            **kwargs: 其他参数
            
        Returns:
            List[Information]: 提取的信息列表
        """
        try:
            # 创建提取提示词
            extraction_prompt = self._create_extraction_prompt(content, url, author, published_date)
            
            # 准备消息
            messages = await self._prepare_messages(
                messages=[{"role": "user", "content": extraction_prompt}]
            )
            
            # 调用LLM服务
            response = await self.llm_service.chat(
                messages=messages,
                temperature=self.temperature
            )
            
            # 解析响应
            return await self._parse_response(response)
        
        except Exception as e:
            logger.error(f"信息提取处理时出错: {e}")
            return [] 