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
    
    async def find_by_field(self, collection: str, field: str, value: Any) -> Optional[Dict[str, Any]]:
        """
        按字段查找记录
        
        Args:
            collection: 集合名称
            field: 字段名
            value: 字段值
            
        Returns:
            Optional[Dict[str, Any]]: 找到的记录或None
        """
        if isinstance(value, str):
            # 如果值是字符串，需要加引号
            filter_str = f'{field}="{value}"'
        else:
            filter_str = f'{field}={value}'
        
        try:
            result = await self.list_records(collection, filter_str=filter_str, per_page=1)
            items = result.get("items", [])
            
            if items:
                return items[0]
            return None
        except Exception as e:
            logger.error(f"按字段查找记录时出错: {e}")
            return None
    
    async def get_collection_list(
        self,
        collection: str,
        filter_params: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 100,
        sort: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        获取集合列表，支持复杂过滤
        
        Args:
            collection: 集合名称
            filter_params: 过滤参数
            skip: 跳过的记录数
            limit: 返回的最大记录数
            sort: 排序参数，例如["-created"]
            
        Returns:
            List[Dict[str, Any]]: 记录列表
        """
        # 计算页码和每页记录数
        page = (skip // limit) + 1
        per_page = limit
        
        # 构建过滤条件
        filter_str = ""
        if filter_params:
            conditions = []
            for key, value in filter_params.items():
                if isinstance(value, dict):
                    # 处理复杂条件，如 {"$gte": 10}
                    for op, op_value in value.items():
                        if op == "$gte":
                            conditions.append(f'{key}>={op_value}')
                        elif op == "$lte":
                            conditions.append(f'{key}<={op_value}')
                        elif op == "$gt":
                            conditions.append(f'{key}>{op_value}')
                        elif op == "$lt":
                            conditions.append(f'{key}<{op_value}')
                        elif op == "$eq":
                            if isinstance(op_value, str):
                                conditions.append(f'{key}="{op_value}"')
                            else:
                                conditions.append(f'{key}={op_value}')
                        elif op == "$ne":
                            if isinstance(op_value, str):
                                conditions.append(f'{key}!="{op_value}"')
                            else:
                                conditions.append(f'{key}!={op_value}')
                        elif op == "$in":
                            values_str = ", ".join([f'"{v}"' if isinstance(v, str) else str(v) for v in op_value])
                            conditions.append(f'{key} ~ [{values_str}]')
                        elif op == "$containsAny":
                            # 对于数组字段，使用特殊语法
                            values_str = ", ".join([f'"{v}"' if isinstance(v, str) else str(v) for v in op_value])
                            conditions.append(f'{key} ?~ [{values_str}]')
                elif isinstance(value, str):
                    conditions.append(f'{key}="{value}"')
                elif isinstance(value, (bool, int, float)):
                    conditions.append(f'{key}={str(value).lower() if isinstance(value, bool) else value}')
                elif value is None:
                    conditions.append(f'{key}=null')
            
            if conditions:
                filter_str = " && ".join(conditions)
        
        # 构建排序条件
        sort_str = ""
        if sort:
            sort_str = ",".join(sort)
        
        try:
            result = await self.list_records(
                collection,
                filter_str=filter_str,
                sort=sort_str,
                page=page,
                per_page=per_page
            )
            
            return result.get("items", [])
        except Exception as e:
            logger.error(f"获取集合列表时出错: {e}")
            return [] 