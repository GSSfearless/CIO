"""
应用配置文件
"""
import os
from pathlib import Path
from typing import Dict, Optional, Any, List

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# 加载环境变量
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)


class LLMConfig(BaseModel):
    """LLM服务配置"""
    provider: str = "zhipu"  # 可选：openai, zhipu, baidu, xunfei
    model: str = "glm-4"
    api_key: Optional[str] = None
    api_base_url: Optional[str] = None
    max_tokens: int = 2000
    temperature: float = 0.7
    
    # 特殊供应商配置
    # 百度文心
    secret_key: Optional[str] = None
    # 讯飞星火
    app_id: Optional[str] = None
    api_secret: Optional[str] = None


class DBConfig(BaseModel):
    """数据库配置"""
    db_type: str = "pocketbase"
    db_api_base: str = "http://127.0.0.1:8090"
    db_username: str = "admin@example.com"
    db_password: str = "password123"


class ScraperConfig(BaseModel):
    """爬虫配置"""
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    timeout: int = 30
    cache_dir: Optional[str] = None
    cache_ttl: int = 3600  # 缓存失效时间（秒）


class SearchConfig(BaseModel):
    """搜索配置"""
    engine: str = "zhipu"  # 可选：zhipu, bing, google
    api_key: Optional[str] = None
    max_results: int = 10


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
    db: DBConfig = Field(default_factory=DBConfig)
    llm: Dict[str, LLMConfig] = Field(default_factory=dict)
    scraper: ScraperConfig = Field(default_factory=ScraperConfig)
    search: SearchConfig = Field(default_factory=SearchConfig)
    
    # 路径配置
    base_dir: Path = Path(__file__).parent.parent
    cache_dir: Path = Path(__file__).parent / "cache"

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


def load_config() -> Config:
    """加载配置"""
    # 创建基础配置
    cfg = Config()
    
    # 环境变量集成
    # LLM配置
    if os.environ.get("LLM_PROVIDER"):
        default_llm = cfg.llm["default"]
        default_llm.provider = os.environ.get("LLM_PROVIDER", default_llm.provider)
        default_llm.model = os.environ.get("LLM_MODEL", default_llm.model)
        default_llm.api_key = os.environ.get("LLM_API_KEY", default_llm.api_key)
        default_llm.api_base_url = os.environ.get("LLM_API_BASE", default_llm.api_base_url)
        
        # 百度文心配置
        default_llm.secret_key = os.environ.get("BAIDU_SECRET_KEY", default_llm.secret_key)
        
        # 讯飞星火配置
        default_llm.app_id = os.environ.get("XUNFEI_APP_ID", default_llm.app_id)
        default_llm.api_secret = os.environ.get("XUNFEI_API_SECRET", default_llm.api_secret)
    
    # 智谱搜索配置
    if os.environ.get("ZHIPU_API_KEY"):
        cfg.search.api_key = os.environ.get("ZHIPU_API_KEY")
    
    # 数据库配置
    if os.environ.get("PB_API_BASE"):
        cfg.db.db_api_base = os.environ.get("PB_API_BASE")
    
    if os.environ.get("PB_API_AUTH"):
        auth_parts = os.environ.get("PB_API_AUTH", "").split("|")
        if len(auth_parts) == 2:
            cfg.db.db_username = auth_parts[0]
            cfg.db.db_password = auth_parts[1]
    
    # 缓存配置
    if os.environ.get("CACHE_DIR"):
        cfg.cache_dir = Path(os.environ.get("CACHE_DIR"))
        cfg.scraper.cache_dir = os.environ.get("CACHE_DIR")
    
    # 调试配置
    if os.environ.get("DEBUG"):
        cfg.debug = os.environ.get("DEBUG").lower() in ("true", "1", "yes")
    
    if os.environ.get("LOG_LEVEL"):
        cfg.log_level = os.environ.get("LOG_LEVEL")
    
    return cfg


# 全局配置实例
config = load_config() 