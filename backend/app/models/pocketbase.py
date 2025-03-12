"""
PocketBase连接器
负责与PocketBase数据库进行交互
"""
import json
from typing import Dict, List, Optional, Any, Union

import aiohttp
from pydantic import BaseModel

from app.config import config
from app.utils import logger


class PocketBaseAuthError(Exception):
    """PocketBase认证错误"""
    pass


class PocketBaseRequestError(Exception):
    """PocketBase请求错误"""
    pass


class PocketBase:
    """PocketBase连接器"""
    
    def __init__(
        self,
        api_base: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None
    ):
        """
        初始化
        
        Args:
            api_base: API基础URL
            username: 用户名
            password: 密码
        """
        self.api_base = api_base or config.db.db_api_base
        self.username = username or config.db.db_username
        self.password = password or config.db.db_password
        
        # 认证相关
        self.auth_token = ""
        self.authenticated = False
    
    async def _authenticate(self) -> bool:
        """
        认证
        
        Returns:
            bool: 认证成功返回True，否则返回False
        """
        if self.authenticated and self.auth_token:
            return True
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/api/admins/auth-with-password",
                    json={"identity": self.username, "password": self.password}
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"PocketBase认证失败: {response.status}, {error_text}")
                        raise PocketBaseAuthError(f"认证失败: {error_text}")
                    
                    result = await response.json()
                    self.auth_token = result.get("token", "")
                    self.authenticated = bool(self.auth_token)
                    
                    return self.authenticated
        
        except Exception as e:
            logger.error(f"PocketBase认证时出错: {e}")
            self.authenticated = False
            return False
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        auth_required: bool = True
    ) -> Any:
        """
        发送请求
        
        Args:
            method: 请求方法
            endpoint: 请求端点
            data: 请求数据
            params: 请求参数
            auth_required: 是否需要认证
            
        Returns:
            Any: 响应数据
        """
        if auth_required and not await self._authenticate():
            raise PocketBaseAuthError("未认证")
        
        url = f"{self.api_base}/api/collections/{endpoint}"
        headers = {}
        
        if auth_required and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with getattr(session, method.lower())(
                    url,
                    json=data,
                    params=params,
                    headers=headers
                ) as response:
                    response_data = await response.json()
                    
                    if response.status >= 400:
                        error_message = response_data.get("message", "未知错误")
                        logger.error(f"PocketBase请求失败: {response.status}, {error_message}")
                        raise PocketBaseRequestError(f"请求失败: {error_message}")
                    
                    return response_data
        
        except Exception as e:
            if not isinstance(e, PocketBaseRequestError):
                logger.error(f"PocketBase请求时出错: {e}")
            raise
    
    async def list_records(
        self,
        collection: str,
        filter_str: str = "",
        sort: str = "",
        page: int = 1,
        per_page: int = 30
    ) -> Dict[str, Any]:
        """
        获取记录列表
        
        Args:
            collection: 集合名称
            filter_str: 过滤字符串
            sort: 排序字符串
            page: 页码
            per_page: 每页记录数
            
        Returns:
            Dict[str, Any]: 记录列表
        """
        params = {
            "page": page,
            "perPage": per_page
        }
        
        if filter_str:
            params["filter"] = filter_str
        
        if sort:
            params["sort"] = sort
        
        return await self._request("get", f"{collection}/records", params=params)
    
    async def get_record(self, collection: str, record_id: str) -> Dict[str, Any]:
        """
        获取单条记录
        
        Args:
            collection: 集合名称
            record_id: 记录ID
            
        Returns:
            Dict[str, Any]: 记录数据
        """
        return await self._request("get", f"{collection}/records/{record_id}")
    
    async def create_record(self, collection: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建记录
        
        Args:
            collection: 集合名称
            data: 记录数据
            
        Returns:
            Dict[str, Any]: 创建的记录
        """
        return await self._request("post", f"{collection}/records", data=data)
    
    async def update_record(self, collection: str, record_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新记录
        
        Args:
            collection: 集合名称
            record_id: 记录ID
            data: 更新数据
            
        Returns:
            Dict[str, Any]: 更新后的记录
        """
        return await self._request("patch", f"{collection}/records/{record_id}", data=data)
    
    async def delete_record(self, collection: str, record_id: str) -> bool:
        """
        删除记录
        
        Args:
            collection: 集合名称
            record_id: 记录ID
            
        Returns:
            bool: 删除成功返回True，否则返回False
        """
        try:
            await self._request("delete", f"{collection}/records/{record_id}")
            return True
        except Exception as e:
            logger.error(f"删除记录时出错: {e}")
            return False 