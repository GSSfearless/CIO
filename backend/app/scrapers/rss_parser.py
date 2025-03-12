"""
RSS解析器模块
负责获取和解析RSS订阅内容
"""
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse

import feedparser
from pydantic import BaseModel, Field

from app.utils import logger


class RSSItem(BaseModel):
    """RSS条目模型"""
    title: str = Field(default="")
    link: str = Field(default="")
    description: str = Field(default="")
    content: str = Field(default="")
    published: Optional[str] = Field(default=None)
    published_parsed: Optional[datetime] = Field(default=None)
    author: Optional[str] = Field(default=None)
    source: str = Field(default="")
    
    class Config:
        arbitrary_types_allowed = True


class RSSParser:
    """RSS解析器类"""
    
    def __init__(self):
        """初始化"""
        self.cache: Dict[str, List[RSSItem]] = {}
        self.last_update: Dict[str, datetime] = {}
        self.update_interval = 3600  # 默认1小时更新一次
    
    def _clean_content(self, content: str) -> str:
        """清理HTML内容，提取纯文本"""
        # 简单实现，实际项目中可使用BeautifulSoup等库进行更精确的处理
        import re
        content = re.sub(r'<.*?>', ' ', content)
        content = re.sub(r'\s+', ' ', content)
        return content.strip()
    
    def _get_content(self, entry: Dict[str, Any]) -> str:
        """获取条目的内容"""
        # 尝试从不同的字段获取内容
        content = ""
        
        # 尝试从content字段获取
        if "content" in entry and entry["content"]:
            for content_item in entry["content"]:
                if "value" in content_item:
                    content += content_item["value"] + " "
        
        # 如果没有content，尝试从summary或description获取
        if not content and "summary" in entry:
            content = entry["summary"]
        elif not content and "description" in entry:
            content = entry["description"]
        
        # 清理HTML标签
        return self._clean_content(content)
    
    async def get_feed(self, url: str, force_update: bool = False) -> List[RSSItem]:
        """
        获取并解析RSS订阅内容
        
        Args:
            url: RSS订阅URL
            force_update: 是否强制更新，不使用缓存
            
        Returns:
            List[RSSItem]: RSS条目列表
        """
        current_time = datetime.now()
        
        # 检查缓存
        if (
            not force_update
            and url in self.cache
            and url in self.last_update
            and (current_time - self.last_update[url]).total_seconds() < self.update_interval
        ):
            logger.debug(f"Using cached RSS feed for {url}")
            return self.cache[url]
        
        try:
            logger.info(f"Fetching RSS feed from {url}")
            
            # 使用asyncio.to_thread在线程中执行同步函数
            loop = asyncio.get_event_loop()
            feed = await loop.run_in_executor(None, feedparser.parse, url)
            
            # 处理feed.entries中的每个条目
            parsed_domain = urlparse(url).netloc
            items = []
            
            for entry in feed.entries:
                item = RSSItem(
                    title=entry.get("title", ""),
                    link=entry.get("link", ""),
                    description=entry.get("summary", ""),
                    content=self._get_content(entry),
                    published=entry.get("published", None),
                    author=entry.get("author", None),
                    source=parsed_domain
                )
                
                # 尝试解析发布时间
                if "published_parsed" in entry and entry["published_parsed"]:
                    try:
                        item.published_parsed = datetime(*entry["published_parsed"][:6])
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Error parsing date: {e}")
                
                items.append(item)
            
            # 更新缓存
            self.cache[url] = items
            self.last_update[url] = current_time
            
            logger.info(f"Successfully parsed {len(items)} items from {url}")
            return items
        
        except Exception as e:
            logger.error(f"Error fetching RSS feed from {url}: {e}")
            # 如果有缓存，返回缓存
            if url in self.cache:
                return self.cache[url]
            return []
    
    def set_update_interval(self, seconds: int):
        """设置更新间隔"""
        self.update_interval = seconds 