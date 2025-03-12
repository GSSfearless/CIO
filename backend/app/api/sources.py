"""
信息源API路由
"""
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.models import PocketBase, Source
from app.utils import logger


router = APIRouter()


class SourceCreate(BaseModel):
    """创建信息源请求体"""
    url: str
    type: str = "web"
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    activated: bool = True


class SourceUpdate(BaseModel):
    """更新信息源请求体"""
    url: Optional[str] = None
    type: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    activated: Optional[bool] = None


async def get_db():
    """获取数据库连接"""
    db = PocketBase()
    return db


@router.get("/", response_model=List[Source])
async def list_sources(
    activated: Optional[bool] = None,
    category: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: PocketBase = Depends(get_db)
):
    """
    获取信息源列表
    
    Args:
        activated: 是否激活
        category: 分类
        page: 页码
        page_size: 每页数量
        db: 数据库连接
    
    Returns:
        List[Source]: 信息源列表
    """
    try:
        # 构建过滤条件
        filter_conditions = []
        
        if activated is not None:
            filter_conditions.append(f"activated={str(activated).lower()}")
        
        if category:
            filter_conditions.append(f"category='{category}'")
        
        filter_str = " && ".join(filter_conditions) if filter_conditions else ""
        
        # 查询数据
        response = await db.list_records(
            "sources",
            filter_str=filter_str,
            sort="-created",
            page=page,
            per_page=page_size
        )
        
        sources = []
        for item in response.get("items", []):
            try:
                source = Source.from_dict(item)
                sources.append(source)
            except Exception as e:
                logger.error(f"解析信息源时出错: {e}")
        
        return sources
    
    except Exception as e:
        logger.error(f"获取信息源列表时出错: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{source_id}", response_model=Source)
async def get_source(source_id: str, db: PocketBase = Depends(get_db)):
    """
    获取信息源详情
    
    Args:
        source_id: 信息源ID
        db: 数据库连接
    
    Returns:
        Source: 信息源详情
    """
    try:
        response = await db.get_record("sources", source_id)
        return Source.from_dict(response)
    
    except Exception as e:
        logger.error(f"获取信息源详情时出错: {e}")
        raise HTTPException(status_code=404, detail="信息源不存在")


@router.post("/", response_model=Source)
async def create_source(source: SourceCreate, db: PocketBase = Depends(get_db)):
    """
    创建信息源
    
    Args:
        source: 创建信息源请求体
        db: 数据库连接
    
    Returns:
        Source: 创建的信息源
    """
    try:
        # 检查URL是否已存在
        existing = await db.list_records(
            "sources",
            filter_str=f"url='{source.url}'"
        )
        
        if existing.get("totalItems", 0) > 0:
            raise HTTPException(status_code=400, detail="信息源URL已存在")
        
        # 准备数据
        source_data = source.dict()
        
        # 创建记录
        response = await db.create_record("sources", source_data)
        
        return Source.from_dict(response)
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"创建信息源时出错: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{source_id}", response_model=Source)
async def update_source(
    source_id: str,
    source: SourceUpdate,
    db: PocketBase = Depends(get_db)
):
    """
    更新信息源
    
    Args:
        source_id: 信息源ID
        source: 更新信息源请求体
        db: 数据库连接
    
    Returns:
        Source: 更新后的信息源
    """
    try:
        # 检查信息源是否存在
        await db.get_record("sources", source_id)
        
        # 准备更新数据
        update_data = {k: v for k, v in source.dict().items() if v is not None}
        
        # 更新记录
        response = await db.update_record("sources", source_id, update_data)
        
        return Source.from_dict(response)
    
    except Exception as e:
        logger.error(f"更新信息源时出错: {e}")
        raise HTTPException(status_code=404, detail="信息源不存在")


@router.delete("/{source_id}")
async def delete_source(source_id: str, db: PocketBase = Depends(get_db)):
    """
    删除信息源
    
    Args:
        source_id: 信息源ID
        db: 数据库连接
    
    Returns:
        Dict: 删除结果
    """
    try:
        # 删除记录
        success = await db.delete_record("sources", source_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="信息源不存在")
        
        return {"success": True, "message": "信息源已删除"}
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"删除信息源时出错: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 