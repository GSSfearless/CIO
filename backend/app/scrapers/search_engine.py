"""
搜索引擎集成模块
负责与各类搜索引擎API交互，获取搜索结果
"""
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import re

import aiohttp
from pydantic import BaseModel, Field

from app.config import config
from app.utils import logger


class SearchResult(BaseModel):
    """搜索结果模型"""
    title: str
    snippet: str
    url: str
    published_date: Optional[str] = None
    source: Optional[str] = None


class SearchEngine:
    """搜索引擎基类"""
    
    def __init__(self):
        """初始化"""
        self.cache: Dict[str, List[SearchResult]] = {}
        self.last_update: Dict[str, datetime] = {}
        self.update_interval = 86400  # 默认24小时更新一次
    
    async def search(self, query: str, force_update: bool = False) -> List[SearchResult]:
        """
        执行搜索
        
        Args:
            query: 搜索关键词
            force_update: 是否强制更新，不使用缓存
            
        Returns:
            List[SearchResult]: 搜索结果列表
        """
        raise NotImplementedError("子类必须实现此方法")
    
    def set_update_interval(self, seconds: int):
        """设置更新间隔"""
        self.update_interval = seconds


class ZhipuSearchEngine(SearchEngine):
    """智谱搜索引擎"""
    
    def __init__(self, api_key: Optional[str] = None):
        """初始化"""
        super().__init__()
        self.api_key = api_key or config.env.get("ZHIPU_API_KEY", "")
        self.api_url = "https://open.bigmodel.cn/api/paas/v4/web/search"
        
        if not self.api_key:
            logger.warning("智谱搜索API密钥未设置")
    
    async def _parse_date(self, text: str) -> Optional[str]:
        """解析发布日期"""
        # 尝试匹配YYYY-MM-DD格式的日期
        date_match = re.search(r'\d{4}-\d{2}-\d{2}', text)
        if date_match:
            return date_match.group()
        return None
    
    async def _parse_results(self, response_data: Dict[str, Any]) -> List[SearchResult]:
        """解析搜索结果"""
        results = []
        
        try:
            search_results = response_data.get("search_result", [])
            
            for item in search_results:
                # 检查必要字段
                if "title" not in item or "content" not in item or "link" not in item:
                    continue
                
                title = item["title"]
                snippet = item["content"]
                url = item["link"]
                
                # 尝试提取发布日期
                published_date = None
                if "（发布时间" in title:
                    title_parts = title.split("（发布时间")
                    title = title_parts[0].strip()
                    if len(title_parts) > 1:
                        date_text = title_parts[1].strip('）')
                        published_date = await self._parse_date(date_text)
                
                # 尝试提取来源
                source = item.get("media", "")
                
                # 创建搜索结果对象
                result = SearchResult(
                    title=title,
                    snippet=snippet,
                    url=url,
                    published_date=published_date,
                    source=source
                )
                
                results.append(result)
        
        except Exception as e:
            logger.error(f"解析搜索结果时出错: {e}")
        
        return results
    
    async def search(self, query: str, force_update: bool = False) -> List[SearchResult]:
        """
        执行搜索
        
        Args:
            query: 搜索关键词
            force_update: 是否强制更新，不使用缓存
            
        Returns:
            List[SearchResult]: 搜索结果列表
        """
        if not self.api_key:
            logger.error("智谱搜索API密钥未设置，无法执行搜索")
            return []
        
        current_time = datetime.now()
        
        # 检查缓存
        if (
            not force_update
            and query in self.cache
            and query in self.last_update
            and (current_time - self.last_update[query]).total_seconds() < self.update_interval
        ):
            logger.debug(f"Using cached search results for query: {query}")
            return self.cache[query]
        
        try:
            logger.info(f"Executing search for query: {query}")
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "query": query,
                "search_query_params": {
                    "per_page": 10,
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"搜索API请求失败: {response.status}, {error_text}")
                        if query in self.cache:
                            return self.cache[query]
                        return []
                    
                    response_data = await response.json()
            
            # 解析搜索结果
            search_results = await self._parse_results(response_data)
            
            # 更新缓存
            self.cache[query] = search_results
            self.last_update[query] = current_time
            
            logger.info(f"Successfully retrieved {len(search_results)} search results for query: {query}")
            return search_results
        
        except Exception as e:
            logger.error(f"执行搜索时出错: {e}")
            # 如果有缓存，返回缓存
            if query in self.cache:
                return self.cache[query]
            return []


# 可以在这里添加其他搜索引擎实现，如百度、必应等


# 工厂函数，根据配置创建搜索引擎实例
def create_search_engine(engine_type: str = "zhipu") -> SearchEngine:
    """
    创建搜索引擎实例
    
    Args:
        engine_type: 搜索引擎类型，支持"zhipu"
        
    Returns:
        SearchEngine: 搜索引擎实例
    """
    if engine_type.lower() == "zhipu":
        return ZhipuSearchEngine()
    else:
        logger.warning(f"未知的搜索引擎类型: {engine_type}，使用默认的智谱搜索")
        return ZhipuSearchEngine() 