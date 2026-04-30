"""Patchwork API 客户端.

提供对 patchwork.kernel.org REST API 的异步访问。
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Any

import httpx


class PatchworkClient:
    """Patchwork REST API 客户端.

    用于获取内核补丁信息、事件流和长期未处理的补丁。
    """

    BASE_URL = "https://patchwork.kernel.org/api/1.3"

    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout

    async def _request(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """执行 HTTP 请求并处理错误.

        Args:
            endpoint: API 端点路径（如 /patches/）
            params: 查询参数

        Returns:
            JSON 响应数据

        Raises:
            httpx.HTTPError: 当 HTTP 请求失败时
        """
        url = f"{self.BASE_URL}{endpoint}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()

    async def get_recent_patches(
        self,
        project: str = "linux-riscv",
        state: str = "open",
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """获取最近的补丁列表.

        Args:
            project: 项目名称，如 "linux-riscv"
            state: 补丁状态，如 "open", "closed", "accepted"
            limit: 返回的最大补丁数量

        Returns:
            补丁列表，每个补丁是一个字典
        """
        params = {
            "project": project,
            "state": state,
            "order": "-date",
            "per_page": limit,
        }
        data = await self._request("/patches/", params)
        if isinstance(data, dict) and "patches" in data:
            return data["patches"]
        return data if isinstance(data, list) else []

    async def get_patch_events(
        self,
        project: str = "linux-riscv",
    ) -> list[dict[str, Any]]:
        """获取补丁事件流（状态变更、新补丁）.

        Args:
            project: 项目名称

        Returns:
            事件列表
        """
        params = {"project": project}
        data = await self._request("/events/", params)
        return data if isinstance(data, list) else []

    @staticmethod
    def _extract_date(patch: dict[str, Any]) -> datetime | None:
        """从补丁数据中提取日期.

        Args:
            patch: 补丁数据字典

        Returns:
            解析的日期时间，如果无法解析则返回 None
        """
        date_fields = ["date", "date_created", "date_updated", "date_pushed"]
        for field in date_fields:
            if field in patch:
                date_str = patch[field]
                try:
                    # 尝试 ISO 格式
                    return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    try:
                        # 尝试常见格式
                        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
                    except (ValueError, AttributeError):
                        continue
        return None

    async def get_stale_patches(
        self,
        days: int = 30,
        project: str = "linux-riscv",
    ) -> list[dict[str, Any]]:
        """查找长期未处理的补丁（贡献机会信号）.

        Args:
            days: 多少天前算陈旧
            project: 项目名称

        Returns:
            陈旧补丁列表
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        patches = await self.get_recent_patches(project=project, state="open", limit=100)
        stale = []
        for patch in patches:
            patch_date = self._extract_date(patch)
            if patch_date and patch_date < cutoff:
                stale.append(patch)
        return stale
