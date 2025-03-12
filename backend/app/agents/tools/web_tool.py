"""
网页抓取工具
用于抓取和解析网页内容
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from app.agents.tools.base_tool import BaseTool, ToolInput, ToolOutput
from app.scrapers.web_scraper import WebScraper, WebPage
from app.utils import logger


class WebToolInput(ToolInput):
    """网页抓取工具输入参数"""
    url: str = Field(..., description="要抓取的网页URL")
    force_update: bool = Field(default=False, description="是否强制更新，不使用缓存")


class WebToolOutput(ToolOutput):
    """网页抓取工具输出结果"""
    page: Optional[Dict[str, Any]] = Field(default=None, description="抓取的网页内容")
    url: str = Field(..., description="抓取的URL")
    title: Optional[str] = Field(default=None, description="网页标题")
    content: Optional[str] = Field(default=None, description="网页正文内容")
    message: Optional[str] = Field(default=None, description="额外信息或错误消息")
    success: bool = Field(default=True, description="抓取是否成功")


class WebTool(BaseTool):
    """网页抓取工具实现"""
    
    name: str = "web_scrape"
    description: str = "抓取和解析网页内容"
    input_schema = WebToolInput
    output_schema = WebToolOutput
    
    _scraper: Optional[WebScraper] = None
    
    async def _get_scraper(self) -> WebScraper:
        """
        获取或创建网页抓取器
        
        Returns:
            WebScraper: 网页抓取器实例
        """
        if self._scraper is None:
            self._scraper = WebScraper()
        return self._scraper
    
    async def _run(self, input_data: WebToolInput) -> WebToolOutput:
        """
        运行网页抓取工具
        
        Args:
            input_data: 网页抓取工具输入参数
            
        Returns:
            WebToolOutput: 网页抓取工具输出结果
        """
        try:
            # 获取网页抓取器
            scraper = await self._get_scraper()
            
            # 抓取网页
            page = await scraper.get_page(input_data.url, force_update=input_data.force_update)
            
            if page is None:
                return WebToolOutput(
                    url=input_data.url,
                    message="无法抓取网页",
                    success=False
                )
            
            # 返回结果
            return WebToolOutput(
                page=page.dict(),
                url=page.url,
                title=page.title,
                content=page.content,
                success=True
            )
        
        except Exception as e:
            logger.error(f"网页抓取工具执行失败: {e}")
            return WebToolOutput(
                url=input_data.url,
                message=f"抓取失败: {str(e)}",
                success=False
            )
    
    async def cleanup(self):
        """清理资源"""
        if self._scraper is not None:
            await self._scraper.cleanup()
            self._scraper = None 