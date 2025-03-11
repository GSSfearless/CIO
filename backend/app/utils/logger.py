"""
日志工具模块
"""
import os
import sys
from pathlib import Path

from loguru import logger

from app.config import config


def setup_logger():
    """
    设置日志配置
    """
    # 清除默认处理程序
    logger.remove()
    
    # 确保日志目录存在
    log_dir = Path(config.app.project_dir) / "logs"
    if not log_dir.exists():
        log_dir.mkdir(parents=True, exist_ok=True)
    
    # 添加控制台日志
    logger.add(
        sys.stderr,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        level=config.app.log_level,
        backtrace=True,
        diagnose=config.app.debug,
    )
    
    # 添加文件日志
    logger.add(
        log_dir / "cio_{time:YYYY-MM-DD}.log",
        rotation="00:00",  # 每天凌晨创建新文件
        retention="30 days",  # 保留30天的日志
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        level=config.app.log_level,
        backtrace=True,
        diagnose=config.app.debug,
    )
    
    return logger


# 创建全局日志实例
logger = setup_logger() 