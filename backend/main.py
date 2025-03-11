"""
CIO - Chief Intelligence Officer
主应用入口文件
"""
import asyncio
import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import config
from app.utils import logger


# 创建FastAPI应用
app = FastAPI(
    title="CIO - Chief Intelligence Officer",
    description="个人情报助手API",
    version="0.1.0",
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """API根路径"""
    return {
        "name": "CIO - Chief Intelligence Officer",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


# 启动时执行的操作
@app.on_event("startup")
async def startup_event():
    """应用启动时执行的操作"""
    logger.info("CIO应用启动中...")
    
    # 确保工作目录存在
    work_dir = Path(config.app.project_dir)
    work_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"工作目录: {work_dir.absolute()}")
    logger.info(f"日志级别: {config.app.log_level}")
    logger.info(f"调试模式: {'开启' if config.app.debug else '关闭'}")
    logger.info("CIO应用已启动")


# 关闭时执行的操作
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行的操作"""
    logger.info("CIO应用正在关闭...")
    # 在这里添加清理代码
    logger.info("CIO应用已关闭")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.app.host,
        port=config.app.port,
        reload=config.app.debug
    ) 