"""
关注点管理API路由
这个模块包含了管理用户关注点的API端点
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel

from app.models.pocketbase import PocketBase
from app.models.schemas import FocusPoint

router = APIRouter()

# 创建和更新关注点的请求模型
class FocusPointCreate(BaseModel):
    focuspoint: str
    explanation: Optional[str] = None
    activated: bool = True
    per_hour: int = 1
    search_engine: bool = True
    source_ids: List[str] = []
    owner: Optional[str] = None

class FocusPointUpdate(BaseModel):
    focuspoint: Optional[str] = None
    explanation: Optional[str] = None
    activated: Optional[bool] = None
    per_hour: Optional[int] = None
    search_engine: Optional[bool] = None
    source_ids: Optional[List[str]] = None
    owner: Optional[str] = None

# 数据库依赖
async def get_db():
    """获取数据库连接"""
    db = PocketBase()
    try:
        yield db
    finally:
        # 此处无需关闭连接，因为PocketBase是RESTful API客户端
        pass

@router.get("/", response_model=List[FocusPoint])
async def list_focus_points(
    activated: Optional[bool] = None,
    owner: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: PocketBase = Depends(get_db)
):
    """
    获取关注点列表
    可选择按激活状态和所有者进行筛选
    """
    try:
        filter_params = {}
        if activated is not None:
            filter_params["activated"] = activated
        if owner is not None:
            filter_params["owner"] = owner
            
        focus_points = await db.get_collection_list("focus_points", filter_params, skip, limit)
        return [FocusPoint.from_dict(fp) for fp in focus_points]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取关注点列表失败: {str(e)}")

@router.get("/{focus_id}", response_model=FocusPoint)
async def get_focus_point(
    focus_id: str,
    db: PocketBase = Depends(get_db)
):
    """
    通过ID获取特定关注点的详细信息
    """
    try:
        focus_point = await db.get_record("focus_points", focus_id)
        return FocusPoint.from_dict(focus_point)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"未找到ID为 {focus_id} 的关注点")

@router.post("/", response_model=FocusPoint, status_code=201)
async def create_focus_point(
    focus_point: FocusPointCreate,
    db: PocketBase = Depends(get_db)
):
    """
    创建新的关注点
    """
    try:
        # 检查是否已经存在相同的关注点
        existing = await db.find_by_field("focus_points", "focuspoint", focus_point.focuspoint)
        if existing:
            raise HTTPException(status_code=400, detail="该关注点已存在")
        
        # 创建关注点
        focus_data = focus_point.dict()
        created_focus = await db.create_record("focus_points", focus_data)
        return FocusPoint.from_dict(created_focus)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建关注点失败: {str(e)}")

@router.patch("/{focus_id}", response_model=FocusPoint)
async def update_focus_point(
    focus_id: str,
    focus_point: FocusPointUpdate,
    db: PocketBase = Depends(get_db)
):
    """
    更新现有关注点
    """
    try:
        # 检查关注点是否存在
        await db.get_record("focus_points", focus_id)
        
        # 更新只包含非空字段
        update_data = {k: v for k, v in focus_point.dict().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=400, detail="没有提供要更新的数据")
        
        # 执行更新
        updated_focus = await db.update_record("focus_points", focus_id, update_data)
        return FocusPoint.from_dict(updated_focus)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"未找到ID为 {focus_id} 的关注点或更新失败")

@router.delete("/{focus_id}", status_code=204)
async def delete_focus_point(
    focus_id: str,
    db: PocketBase = Depends(get_db)
):
    """
    删除关注点
    """
    try:
        # 检查关注点是否存在
        await db.get_record("focus_points", focus_id)
        
        # 删除关注点
        await db.delete_record("focus_points", focus_id)
        return None
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"未找到ID为 {focus_id} 的关注点或删除失败") 