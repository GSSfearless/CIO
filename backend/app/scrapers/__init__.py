"""
信息采集模块初始化文件
"""
from app.scrapers.rss_parser import RSSParser
from app.scrapers.web_scraper import WebScraper

__all__ = ["RSSParser", "WebScraper"] 