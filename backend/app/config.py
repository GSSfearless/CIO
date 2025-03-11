"""
应用配置文件
"""
import os
from pathlib import Path
from typing import Dict, Optional, Any

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# 加载环境变量
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)


class LLMConfig(BaseModel):
    """LLM 配置"""
    api_key: Optional[str] = Field(default=None)
    api_base_url: Optional[str] = Field(default=None)
    model: str = Field(default="gpt-4o")
    temperature: float = Field(default=0.0)
    max_tokens: int = Field(default=4000)
    

class DatabaseConfig(BaseModel):
    """数据库配置"""
    db_api_base: str = Field(default="http://127.0.0.1:8090")
    db_username: str = Field(default="admin@example.com")
    db_password: str = Field(default="password")


class AppConfig(BaseModel):
    """应用配置"""
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")
    project_dir: str = Field(default="work_dir")
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    

class Config(BaseModel):
    """总配置"""
    app: AppConfig = Field(default_factory=AppConfig)
    db: DatabaseConfig = Field(default_factory=DatabaseConfig)
    llm: Dict[str, LLMConfig] = Field(default_factory=dict)

    def __init__(self, **data: Any):
        super().__init__(**data)
        
        # 加载LLM配置
        # 默认LLM配置
        default_llm = LLMConfig(
            api_key=os.getenv("LLM_API_KEY"),
            api_base_url=os.getenv("LLM_API_BASE"),
            model=os.getenv("PRIMARY_MODEL", "gpt-4o"),
        )
        self.llm["default"] = default_llm
        
        # 辅助LLM配置（如果有）
        if os.getenv("SECONDARY_MODEL"):
            secondary_llm = LLMConfig(
                api_key=os.getenv("LLM_API_KEY"),
                api_base_url=os.getenv("LLM_API_BASE"),
                model=os.getenv("SECONDARY_MODEL"),
            )
            self.llm["secondary"] = secondary_llm
        
        # 视觉LLM配置（如果有）
        if os.getenv("VL_MODEL"):
            vl_llm = LLMConfig(
                api_key=os.getenv("LLM_API_KEY"),
                api_base_url=os.getenv("LLM_API_BASE"),
                model=os.getenv("VL_MODEL"),
            )
            self.llm["vision"] = vl_llm
        
        # 更新数据库配置
        if os.getenv("PB_API_BASE"):
            self.db.db_api_base = os.getenv("PB_API_BASE")
        if os.getenv("PB_API_AUTH"):
            auth_parts = os.getenv("PB_API_AUTH", "").split("|")
            if len(auth_parts) == 2:
                self.db.db_username = auth_parts[0]
                self.db.db_password = auth_parts[1]
        
        # 更新应用配置
        if os.getenv("DEBUG", "").lower() == "true":
            self.app.debug = True
        if os.getenv("LOG_LEVEL"):
            self.app.log_level = os.getenv("LOG_LEVEL")
        if os.getenv("PROJECT_DIR"):
            self.app.project_dir = os.getenv("PROJECT_DIR")


# 创建全局配置实例
config = Config() 