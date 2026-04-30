"""资源调度器 — Pipeline 资源管理."""
from __future__ import annotations

import asyncio
from typing import Any, Callable
from datetime import datetime

from backend.pipeline.state import PipelineState


class ResourceScheduler:
    """Pipeline 资源调度器.

    管理并发案例执行、资源配额和队列调度。
    """

    def __init__(
        self,
        max_concurrent_cases: int = 3,
        max_cases_per_user: int = 5,
    ):
        self.max_concurrent_cases = max_concurrent_cases
        self.max_cases_per_user = max_cases_per_user
        self._running: set[str] = set()
        self._queue: asyncio.Queue[tuple[str, Callable]] = asyncio.Queue()
        self._user_cases: dict[str, set[str]] = {}

    async def submit(
        self,
        case_id: str,
        user_id: str,
        task: Callable,
    ) -> bool:
        """提交案例到调度器.

        Args:
            case_id: 案例 ID
            user_id: 用户 ID
            task: 要执行的任务函数

        Returns:
            是否成功提交
        """
        # 检查用户配额
        user_case_count = len(self._user_cases.get(user_id, set()))
        if user_case_count >= self.max_cases_per_user:
            return False

        # 记录用户案例
        if user_id not in self._user_cases:
            self._user_cases[user_id] = set()
        self._user_cases[user_id].add(case_id)

        # 尝试立即执行或加入队列
        if len(self._running) < self.max_concurrent_cases:
            await self._start_case(case_id, user_id, task)
        else:
            await self._queue.put((case_id, task))

        return True

    async def _start_case(
        self,
        case_id: str,
        user_id: str,
        task: Callable,
    ) -> None:
        """启动案例执行."""
        self._running.add(case_id)

        async def _run_and_cleanup():
            try:
                await task()
            finally:
                self._running.discard(case_id)
                self._user_cases.get(user_id, set()).discard(case_id)
                await self._process_queue()

        asyncio.create_task(_run_and_cleanup())

    async def _process_queue(self) -> None:
        """处理队列中的下一个案例."""
        if not self._queue.empty() and len(self._running) < self.max_concurrent_cases:
            case_id, task = await self._queue.get()
            # 这里简化处理，实际应该传递 user_id
            await self._start_case(case_id, "unknown", task)

    def get_status(self) -> dict[str, Any]:
        """获取调度器状态.

        Returns:
            包含运行中案例数、队列长度等信息的字典
        """
        return {
            "running_count": len(self._running),
            "queue_size": self._queue.qsize(),
            "running_cases": list(self._running),
            "max_concurrent": self.max_concurrent_cases,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def cancel_case(self, case_id: str) -> bool:
        """取消案例.

        Args:
            case_id: 案例 ID

        Returns:
            是否成功取消
        """
        # 简化的取消逻辑，实际实现需要更复杂的任务管理
        if case_id in self._running:
            self._running.discard(case_id)
            return True
        return False


class TokenBucket:
    """令牌桶限流器.

    用于限制 API 调用频率。
    """

    def __init__(self, rate: float, capacity: int):
        """初始化令牌桶.

        Args:
            rate: 每秒产生的令牌数
            capacity: 桶容量
        """
        self.rate = rate
        self.capacity = capacity
        self._tokens = capacity
        self._last_update = asyncio.get_event_loop().time()
        self._lock = asyncio.Lock()

    async def acquire(self, tokens: int = 1) -> bool:
        """获取令牌.

        Args:
            tokens: 需要的令牌数

        Returns:
            是否成功获取
        """
        async with self._lock:
            now = asyncio.get_event_loop().time()
            elapsed = now - self._last_update
            self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)
            self._last_update = now

            if self._tokens >= tokens:
                self._tokens -= tokens
                return True
            return False


class CostLimiter:
    """成本限制器.

    跟踪和控制 API 调用成本。
    """

    def __init__(self, daily_budget_usd: float = 50.0):
        self.daily_budget_usd = daily_budget_usd
        self._daily_cost: float = 0.0
        self._last_reset: str = datetime.utcnow().strftime("%Y-%m-%d")

    def check_budget(self, estimated_cost: float) -> bool:
        """检查预算是否足够.

        Args:
            estimated_cost: 估计成本（美元）

        Returns:
            是否在预算内
        """
        self._reset_if_new_day()
        return (self._daily_cost + estimated_cost) <= self.daily_budget_usd

    def add_cost(self, cost_usd: float) -> None:
        """记录成本.

        Args:
            cost_usd: 实际成本（美元）
        """
        self._reset_if_new_day()
        self._daily_cost += cost_usd

    def _reset_if_new_day(self) -> None:
        """如果是新的一天则重置计数器."""
        today = datetime.utcnow().strftime("%Y-%m-%d")
        if today != self._last_reset:
            self._daily_cost = 0.0
            self._last_reset = today

    def get_status(self) -> dict[str, Any]:
        """获取成本状态."""
        self._reset_if_new_day()
        return {
            "daily_budget_usd": self.daily_budget_usd,
            "daily_cost_usd": self._daily_cost,
            "remaining_usd": self.daily_budget_usd - self._daily_cost,
            "usage_percent": (self._daily_cost / self.daily_budget_usd * 100) if self.daily_budget_usd > 0 else 0,
        }
