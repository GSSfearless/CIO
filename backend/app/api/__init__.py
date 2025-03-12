"""
API包初始化文件
"""
from fastapi import APIRouter

from app.api.sources import router as sources_router
from app.api.focus_points import router as focus_points_router
from app.api.info import router as info_router
from app.api.query import router as query_router

# 创建API主路由
api_router = APIRouter()

# 注册子路由
api_router.include_router(sources_router, prefix="/sources", tags=["sources"])
api_router.include_router(focus_points_router, prefix="/focus-points", tags=["focus-points"])
api_router.include_router(info_router, prefix="/info", tags=["info"])
api_router.include_router(query_router, prefix="/query", tags=["query"])

__all__ = ["api_router"] 