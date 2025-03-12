"""
数据模型定义
"""
from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    """基础模型"""
    id: Optional[str] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None


class Source(BaseSchema):
    """信息源模型"""
    url: str
    type: str = "web"  # web, rss
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    activated: bool = True
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Source":
        """从字典创建对象"""
        return cls(**data)


class FocusPoint(BaseSchema):
    """关注点模型"""
    focuspoint: str
    explanation: Optional[str] = None
    activated: bool = True
    per_hour: int = 24  # 爬取频率，单位小时
    search_engine: bool = False  # 是否开启搜索引擎
    sources: List[str] = []  # 信息源ID列表
    owner: Optional[str] = None
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FocusPoint":
        """从字典创建对象"""
        return cls(**data)


class Info(BaseSchema):
    """信息模型"""
    title: str
    content: str
    summary: Optional[str] = None
    url: str
    url_title: Optional[str] = None
    published: Optional[str] = None
    author: Optional[str] = None
    source: Optional[str] = None
    tags: List[str] = []
    relevance_score: float = 0.0
    focus_id: str  # 关联的关注点ID
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Info":
        """从字典创建对象"""
        return cls(**data)


class Query(BaseSchema):
    """查询模型"""
    query: str
    focus_id: Optional[str] = None
    response: str
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Query":
        """从字典创建对象"""
        return cls(**data) 