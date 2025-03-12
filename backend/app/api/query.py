"""
交互式查询API路由
这个模块包含了用户查询和LLM交互的API端点
"""

from fastapi import APIRouter, Depends, HTTPException, Query as QueryParam
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.models.pocketbase import PocketBase
from app.models.schemas import Query
from app.llm.llm_service import process_query

router = APIRouter()

# 查询请求的模型
class QueryRequest(BaseModel):
    query: str
    focus_id: Optional[str] = None
    context_info_ids: Optional[List[str]] = []  # 可选的上下文信息ID列表

class QueryResponse(BaseModel):
    query_id: str
    query: str
    response: str
    focus_id: Optional[str] = None
    timestamp: datetime
    
# 数据库依赖
async def get_db():
    """获取数据库连接"""
    db = PocketBase()
    try:
        yield db
    finally:
        # 此处无需关闭连接，因为PocketBase是RESTful API客户端
        pass

@router.post("/", response_model=QueryResponse)
async def create_query(
    query_request: QueryRequest,
    db: PocketBase = Depends(get_db)
):
    """
    处理用户查询并获取响应
    """
    try:
        # 检查关联的focus_id是否存在（如果提供了）
        if query_request.focus_id:
            try:
                await db.get_record("focus_points", query_request.focus_id)
            except Exception:
                raise HTTPException(status_code=400, detail=f"关联的关注点ID {query_request.focus_id} 不存在")
        
        # 获取上下文信息（如果提供了）
        context_info = []
        if query_request.context_info_ids:
            for info_id in query_request.context_info_ids:
                try:
                    info = await db.get_record("info", info_id)
                    context_info.append(info)
                except Exception:
                    # 如果某个信息不存在，记录警告但继续处理
                    pass
        
        # 使用LLM服务处理查询
        response = await process_query(
            query_request.query, 
            focus_id=query_request.focus_id,
            context_info=context_info
        )
        
        # 创建查询记录
        query_data = {
            "query": query_request.query,
            "focus_id": query_request.focus_id,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
        
        created_query = await db.create_record("queries", query_data)
        
        # 格式化并返回响应
        return QueryResponse(
            query_id=created_query["id"],
            query=created_query["query"],
            response=created_query["response"],
            focus_id=created_query.get("focus_id"),
            timestamp=datetime.fromisoformat(created_query["timestamp"])
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理查询失败: {str(e)}")

@router.get("/", response_model=List[Query])
async def list_queries(
    focus_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = QueryParam(0, ge=0),
    limit: int = QueryParam(100, ge=1, le=100),
    db: PocketBase = Depends(get_db)
):
    """
    获取查询历史记录列表
    可选择按关注点和日期范围进行筛选
    """
    try:
        filter_params = {}
        if focus_id:
            filter_params["focus_id"] = focus_id
            
        # 日期筛选
        date_filter = {}
        if start_date:
            date_filter["$gte"] = start_date.isoformat()
        if end_date:
            date_filter["$lte"] = end_date.isoformat()
        if date_filter:
            filter_params["timestamp"] = date_filter
            
        queries = await db.get_collection_list("queries", filter_params, skip, limit, ["-timestamp"])
        return [Query.from_dict(q) for q in queries]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取查询历史记录失败: {str(e)}")

@router.get("/{query_id}", response_model=Query)
async def get_query(
    query_id: str,
    db: PocketBase = Depends(get_db)
):
    """
    通过ID获取特定查询的详细信息
    """
    try:
        query = await db.get_record("queries", query_id)
        return Query.from_dict(query)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"未找到ID为 {query_id} 的查询")

@router.delete("/{query_id}", status_code=204)
async def delete_query(
    query_id: str,
    db: PocketBase = Depends(get_db)
):
    """
    删除查询历史记录
    """
    try:
        # 检查查询是否存在
        await db.get_record("queries", query_id)
        
        # 删除查询
        await db.delete_record("queries", query_id)
        return None
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"未找到ID为 {query_id} 的查询或删除失败") 