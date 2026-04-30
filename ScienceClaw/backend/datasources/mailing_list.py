"""邮件列表爬取器.

提供对 lore.kernel.org 和 groups.io 邮件归档的异步爬取功能。
"""
from __future__ import annotations

import re
from typing import Any
from urllib.parse import quote_plus

import httpx


class MailingListCrawler:
    """邮件列表爬取器.

    用于从 lore.kernel.org 和 groups.io 搜索和解析邮件线程。
    """

    LORE_BASE = "https://lore.kernel.org"
    GROUPS_IO_BASE = "https://groups.io"

    def __init__(self, timeout: float = 15.0):
        self.timeout = timeout

    async def _get(self, url: str) -> str:
        """执行 HTTP GET 请求.

        Args:
            url: 目标 URL

        Returns:
            响应文本内容
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(url)
                resp.raise_for_status()
                return resp.text
            except httpx.HTTPError:
                return ""

    async def search_lore_kernel(
        self,
        query: str,
        list_name: str = "linux-kernel",
        days: int = 30,
    ) -> list[dict[str, Any]]:
        """搜索 lore.kernel.org 邮件归档.

        Args:
            query: 搜索关键词
            list_name: 邮件列表名称，如 "linux-kernel"
            days: 搜索最近多少天的邮件

        Returns:
            邮件线程列表，每个包含 title, url, snippet
        """
        encoded_query = quote_plus(query)
        url = f"{self.LORE_BASE}/{list_name}/?q={encoded_query}"
        html = await self._get(url)
        if not html:
            return []

        # 简单的正则提取线程链接
        results = []
        # 匹配邮件线程链接和标题
        pattern = r'<a[^>]*href="(/[^"/]+/[^"]+)"[^>]*>([^<]+)</a>'
        matches = re.findall(pattern, html)
        seen_urls = set()

        for match in matches[:50]:  # 限制结果数量
            path, title = match
            full_url = f"{self.LORE_BASE}{path}"
            if full_url in seen_urls:
                continue
            seen_urls.add(full_url)
            results.append({
                "title": title.strip(),
                "url": full_url,
                "snippet": "",  # 简化实现，不提取摘要
            })

        return results

    async def parse_thread(self, message_id: str) -> dict[str, Any]:
        """解析邮件线程详情.

        Args:
            message_id: 邮件 ID 或完整 URL

        Returns:
            线程详情字典，包含 thread_id, url, subject, snippets
        """
        if message_id.startswith("http"):
            url = message_id
            thread_id = url.split("/")[-1]
        else:
            thread_id = message_id
            url = f"{self.LORE_BASE}/linux-kernel/{message_id}"

        html = await self._get(url)
        if not html:
            return {
                "thread_id": thread_id,
                "url": url,
                "subject": "",
                "snippets": [],
            }

        # 提取标题
        subject_match = re.search(r"<title>([^<]+)</title>", html)
        subject = subject_match.group(1).strip() if subject_match else ""

        # 提取片段（前3个 <p> 标签内容）
        snippets = []
        p_matches = re.findall(r"<p[^>]*>([^<]+)</p>", html)
        for content in p_matches[:3]:
            snippet = content.strip()
            if snippet:
                snippets.append(snippet)

        return {
            "thread_id": thread_id,
            "url": url,
            "subject": subject,
            "snippets": snippets,
        }

    async def extract_patches(self, thread_url: str) -> list[dict[str, Any]]:
        """从邮件线程中提取补丁文件.

        Args:
            thread_url: 邮件线程 URL

        Returns:
            补丁文件列表，每个包含 patch_url 和 filename
        """
        html = await self._get(thread_url)
        if not html:
            return []

        patches = []
        # 匹配补丁文件链接（.patch, .diff, .patch.gz, .diff.gz）
        pattern = r'<a[^>]*href="([^"]+\.(?:patch|diff)(?:\.gz)?)"[^>]*>([^<]+)</a>'
        matches = re.findall(pattern, html)
        seen_urls = set()

        for href, filename in matches:
            patch_url = href if href.startswith("http") else f"{self.LORE_BASE}{href}"
            if patch_url in seen_urls:
                continue
            seen_urls.add(patch_url)
            patches.append({
                "patch_url": patch_url,
                "filename": filename.strip() or "patch",
            })

        return patches

    async def get_groups_io_archive(
        self,
        group: str,
        topic: str = "",
    ) -> list[dict[str, Any]]:
        """获取 groups.io 归档邮件.

        Args:
            group: 群组名称，如 "tech-riscv"
            topic: 可选的主题过滤

        Returns:
            邮件列表，每个包含 title 和 url
        """
        base = f"{self.GROUPS_IO_BASE}/g/{group}"
        url = f"{base}/messages" if not topic else f"{base}/topics/{topic}"
        html = await self._get(url)
        if not html:
            return []

        results = []
        # 提取消息链接
        pattern = r'<a[^>]*href="(/g/[^"]+/message/[^"]+)"[^>]*>([^<]+)</a>'
        matches = re.findall(pattern, html)
        seen_urls = set()

        for path, title in matches[:30]:
            full_url = f"{self.GROUPS_IO_BASE}{path}"
            if full_url in seen_urls:
                continue
            seen_urls.add(full_url)
            results.append({
                "title": title.strip(),
                "url": full_url,
            })

        return results
