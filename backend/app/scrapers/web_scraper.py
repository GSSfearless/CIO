"""
Web爬虫模块
负责获取和解析网页内容
"""
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from urllib.parse import urlparse, urljoin

import aiohttp
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Browser, Page
from pydantic import BaseModel, Field

from app.utils import logger


class WebPage(BaseModel):
    """网页内容模型"""
    url: str
    title: str = ""
    content: str = ""
    html: str = ""
    links: List[str] = []
    published_date: Optional[datetime] = None
    author: Optional[str] = None
    images: List[str] = []
    source_domain: str = ""
    
    class Config:
        arbitrary_types_allowed = True


class WebScraper:
    """Web爬虫类"""
    
    def __init__(self):
        """初始化"""
        self.cache: Dict[str, WebPage] = {}
        self.last_update: Dict[str, datetime] = {}
        self.update_interval = 3600  # 默认1小时更新一次
        self.browser: Optional[Browser] = None
        self.visited_urls: Set[str] = set()
        self.max_depth = 2  # 默认爬取深度
    
    async def _ensure_browser(self):
        """确保浏览器已启动"""
        if not self.browser:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(headless=True)
    
    async def _close_browser(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
            self.browser = None
    
    async def _extract_metadata(self, page: Page) -> Dict[str, Any]:
        """提取页面元数据"""
        metadata = {}
        
        # 提取标题
        metadata["title"] = await page.title()
        
        # 提取发布日期
        date_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="pubdate"]',
            'meta[name="publishdate"]',
            'meta[name="timestamp"]',
            'time[datetime]',
            '.publish-date',
            '.date',
        ]
        
        for selector in date_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    if selector.startswith('meta'):
                        date_str = await element.get_attribute('content')
                    elif selector.startswith('time'):
                        date_str = await element.get_attribute('datetime')
                    else:
                        date_str = await element.text_content()
                    
                    if date_str:
                        try:
                            # 尝试解析日期，这里可能需要更复杂的解析逻辑
                            metadata["published_date"] = date_str
                            break
                        except Exception as e:
                            logger.debug(f"Failed to parse date {date_str}: {e}")
            except Exception as e:
                logger.debug(f"Error extracting date with selector {selector}: {e}")
        
        # 提取作者
        author_selectors = [
            'meta[name="author"]',
            'meta[property="article:author"]',
            '.author',
            '.byline',
        ]
        
        for selector in author_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    if selector.startswith('meta'):
                        author = await element.get_attribute('content')
                    else:
                        author = await element.text_content()
                    
                    if author:
                        metadata["author"] = author.strip()
                        break
            except Exception as e:
                logger.debug(f"Error extracting author with selector {selector}: {e}")
        
        return metadata
    
    async def _extract_links(self, page: Page, base_url: str) -> List[str]:
        """提取页面中的链接"""
        links = []
        
        try:
            parsed_base = urlparse(base_url)
            base_domain = parsed_base.netloc
            
            # 获取所有链接
            elements = await page.query_selector_all('a[href]')
            for element in elements:
                href = await element.get_attribute('href')
                if href:
                    # 处理相对URL
                    full_url = urljoin(base_url, href)
                    parsed = urlparse(full_url)
                    
                    # 只收集同域名的链接
                    if parsed.netloc == base_domain and parsed.scheme in ('http', 'https'):
                        links.append(full_url)
        except Exception as e:
            logger.error(f"Error extracting links: {e}")
        
        return links
    
    async def _extract_images(self, page: Page, base_url: str) -> List[str]:
        """提取页面中的图片链接"""
        images = []
        
        try:
            # 获取所有图片
            elements = await page.query_selector_all('img[src]')
            for element in elements:
                src = await element.get_attribute('src')
                if src:
                    # 处理相对URL
                    full_url = urljoin(base_url, src)
                    images.append(full_url)
        except Exception as e:
            logger.error(f"Error extracting images: {e}")
        
        return images
    
    async def _extract_text_content(self, page: Page) -> str:
        """提取页面文本内容"""
        try:
            # 尝试使用主要内容选择器
            main_content_selectors = [
                'article',
                'main',
                '.content',
                '.article-content',
                '.post-content',
                '#content',
                '.main-content',
                '.entry-content',
            ]
            
            for selector in main_content_selectors:
                element = await page.query_selector(selector)
                if element:
                    content = await element.text_content()
                    if content and len(content) > 100:  # 确保内容足够长
                        return content.strip()
            
            # 如果找不到主要内容选择器，则使用body
            body = await page.query_selector('body')
            if body:
                return await body.text_content()
            
            return ""
        except Exception as e:
            logger.error(f"Error extracting text content: {e}")
            return ""
    
    async def get_page(self, url: str, force_update: bool = False) -> Optional[WebPage]:
        """
        获取并解析网页内容
        
        Args:
            url: 网页URL
            force_update: 是否强制更新，不使用缓存
            
        Returns:
            Optional[WebPage]: 网页内容对象，如果获取失败则返回None
        """
        current_time = datetime.now()
        
        # 检查缓存
        if (
            not force_update
            and url in self.cache
            and url in self.last_update
            and (current_time - self.last_update[url]).total_seconds() < self.update_interval
        ):
            logger.debug(f"Using cached web page for {url}")
            return self.cache[url]
        
        try:
            logger.info(f"Fetching web page from {url}")
            
            # 确保浏览器已启动
            await self._ensure_browser()
            
            # 创建新页面
            page = await self.browser.new_page()
            
            try:
                # 访问URL
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                
                # 等待页面加载完成
                await page.wait_for_load_state("networkidle", timeout=5000)
            except Exception as e:
                logger.warning(f"Page load timeout or error: {e}, continuing with partial content")
            
            # 提取内容
            html = await page.content()
            metadata = await self._extract_metadata(page)
            links = await self._extract_links(page, url)
            text_content = await self._extract_text_content(page)
            images = await self._extract_images(page, url)
            
            # 关闭页面
            await page.close()
            
            # 解析域名
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            
            # 创建WebPage对象
            web_page = WebPage(
                url=url,
                title=metadata.get("title", ""),
                content=text_content,
                html=html,
                links=links,
                author=metadata.get("author"),
                published_date=metadata.get("published_date"),
                images=images,
                source_domain=domain
            )
            
            # 更新缓存
            self.cache[url] = web_page
            self.last_update[url] = current_time
            
            logger.info(f"Successfully fetched web page from {url}")
            return web_page
        
        except Exception as e:
            logger.error(f"Error fetching web page from {url}: {e}")
            # 如果有缓存，返回缓存
            if url in self.cache:
                return self.cache[url]
            return None
    
    async def crawl(self, start_url: str, depth: int = 1, max_pages: int = 10) -> List[WebPage]:
        """
        从起始URL开始爬取，支持递归爬取
        
        Args:
            start_url: 起始URL
            depth: 爬取深度
            max_pages: 最大爬取页面数
            
        Returns:
            List[WebPage]: 爬取到的网页内容列表
        """
        self.visited_urls = set()
        to_visit = [(start_url, 0)]  # (url, depth)
        results = []
        
        while to_visit and len(results) < max_pages:
            url, current_depth = to_visit.pop(0)
            
            if url in self.visited_urls:
                continue
                
            self.visited_urls.add(url)
            
            page = await self.get_page(url)
            if page:
                results.append(page)
                
                # 如果未达到最大深度，添加链接到队列
                if current_depth < depth:
                    for link in page.links:
                        if link not in self.visited_urls and (link, current_depth + 1) not in to_visit:
                            to_visit.append((link, current_depth + 1))
        
        return results
    
    def set_update_interval(self, seconds: int):
        """设置更新间隔"""
        self.update_interval = seconds
    
    def set_max_depth(self, depth: int):
        """设置最大爬取深度"""
        self.max_depth = depth
    
    async def cleanup(self):
        """清理资源"""
        await self._close_browser() 