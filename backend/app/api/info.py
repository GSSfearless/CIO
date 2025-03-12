"""
信息查询API路由
这个模块包含了查询信息的API端点
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.models.pocketbase import PocketBase
from app.models.schemas import Info

router = APIRouter()

# 创建和更新信息的请求模型
class InfoCreate(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    url: Optional[str] = None
    url_title: Optional[str] = None
    published: Optional[datetime] = None
    author: Optional[str] = None
    source: Optional[str] = None
    tags: List[str] = []
    relevance_score: Optional[float] = None
    focus_id: str

class InfoUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    url: Optional[str] = None
    url_title: Optional[str] = None
    published: Optional[datetime] = None
    author: Optional[str] = None
    source: Optional[str] = None
    tags: Optional[List[str]] = None
    relevance_score: Optional[float] = None
    focus_id: Optional[str] = None

# 数据库依赖
async def get_db():
    """获取数据库连接"""
    db = PocketBase()
    try:
        yield db
    finally:
        # 此处无需关闭连接，因为PocketBase是RESTful API客户端
        pass

@router.get("/", response_model=List[Info])
async def list_info(
    focus_id: Optional[str] = None,
    source: Optional[str] = None,
    tags: Optional[str] = None,  # 逗号分隔的标签列表
    min_relevance: Optional[float] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: PocketBase = Depends(get_db)
):
    """
    获取信息列表
    可选择按关注点、来源、标签、相关性得分和日期范围进行筛选
    """
    try:
        filter_params = {}
        if focus_id:
            filter_params["focus_id"] = focus_id
        if source:
            filter_params["source"] = source
        if tags:
            # 处理标签筛选逻辑，需要在PocketBase查询中实现
            tag_list = tags.split(",")
            # 假设PocketBase支持类似的标签筛选语法
            filter_params["tags"] = {"$containsAny": tag_list}
        if min_relevance is not None:
            filter_params["relevance_score"] = {"$gte": min_relevance}
        
        # 日期筛选
        date_filter = {}
        if start_date:
            date_filter["$gte"] = start_date.isoformat()
        if end_date:
            date_filter["$lte"] = end_date.isoformat()
        if date_filter:
            filter_params["published"] = date_filter
            
        info_items = await db.get_collection_list("info", filter_params, skip, limit)
        return [Info.from_dict(item) for item in info_items]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取信息列表失败: {str(e)}")

@router.get("/{info_id}", response_model=Info)
async def get_info(
    info_id: str,
    db: PocketBase = Depends(get_db)
):
    """
    通过ID获取特定信息的详细内容
    """
    try:
        info_item = await db.get_record("info", info_id)
        return Info.from_dict(info_item)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"未找到ID为 {info_id} 的信息")

@router.post("/", response_model=Info, status_code=201)
async def create_info(
    info: InfoCreate,
    db: PocketBase = Depends(get_db)
):
    """
    创建新的信息
    """
    try:
        # 检查关联的focus_id是否存在
        try:
            await db.get_record("focus_points", info.focus_id)
        except Exception:
            raise HTTPException(status_code=400, detail=f"关联的关注点ID {info.focus_id} 不存在")
        
        # 创建信息
        info_data = info.dict()
        
        # 如果提供了URL，检查是否已存在相同URL的信息
        if info.url:
            existing = await db.find_by_field("info", "url", info.url)
            if existing:
                raise HTTPException(status_code=400, detail="该URL的信息已存在")
        
        # 设置默认值
        if not info_data.get("published"):
            info_data["published"] = datetime.now().isoformat()
            
        created_info = await db.create_record("info", info_data)
        return Info.from_dict(created_info)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建信息失败: {str(e)}")

@router.patch("/{info_id}", response_model=Info)
async def update_info(
    info_id: str,
    info: InfoUpdate,
    db: PocketBase = Depends(get_db)
):
    """
    更新现有信息
    """
    try:
        # 检查信息是否存在
        await db.get_record("info", info_id)
        
        # 检查关联的focus_id是否存在
        if info.focus_id:
            try:
                await db.get_record("focus_points", info.focus_id)
            except Exception:
                raise HTTPException(status_code=400, detail=f"关联的关注点ID {info.focus_id} 不存在")
        
        # 更新只包含非空字段
        update_data = {k: v for k, v in info.dict().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=400, detail="没有提供要更新的数据")
        
        # 执行更新
        updated_info = await db.update_record("info", info_id, update_data)
        return Info.from_dict(updated_info)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"未找到ID为 {info_id} 的信息或更新失败")

@router.delete("/{info_id}", status_code=204)
async def delete_info(
    info_id: str,
    db: PocketBase = Depends(get_db)
):
    """
    删除信息
    """
    try:
        # 检查信息是否存在
        await db.get_record("info", info_id)
        
        # 删除信息
        await db.delete_record("info", info_id)
        return None
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"未找到ID为 {info_id} 的信息或删除失败")

@router.get("/focus/{focus_id}/latest", response_model=List[Info])
async def get_latest_info_by_focus(
    focus_id: str,
    limit: int = Query(10, ge=1, le=50),
    db: PocketBase = Depends(get_db)
):
    """
    获取指定关注点的最新信息
    """
    try:
        # 检查关注点是否存在
        await db.get_record("focus_points", focus_id)
        
        # 使用特定排序规则获取最新信息
        filter_params = {"focus_id": focus_id}
        sort_params = ["-published"]  # 按发布时间倒序排列
        
        info_items = await db.get_collection_list("info", filter_params, 0, limit, sort_params)
        return [Info.from_dict(item) for item in info_items]
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"未找到ID为 {focus_id} 的关注点或获取信息失败")

@router.get("/search", response_model=List[Info])
async def search_info(
    query: str,
    focus_id: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: PocketBase = Depends(get_db)
):
    """
    全文搜索信息内容
    """
    try:
        # 构建搜索参数
        search_params = {"$search": query}
        if focus_id:
            search_params["focus_id"] = focus_id
            
        # 执行搜索
        # 注意：这里简化了实现，实际上需要根据PocketBase的搜索API来调整
        search_results = await db.search_records("info", search_params, skip, limit)
        return [Info.from_dict(item) for item in search_results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索信息失败: {str(e)}") 