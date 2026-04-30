"""AgentAdapter 抽象基类 — 统一 Claude/OpenAI SDK 接口."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator
from pydantic import BaseModel, Field


class AgentEvent(BaseModel):
    """Agent 执行过程中的事件."""
    event_type: str = Field(description="事件类型")
    data: dict[str, Any] = Field(default_factory=dict, description="事件数据")


class AgentAdapter(ABC):
    """跨 SDK Agent 适配器基类.

    注意：两个 SDK 的执行模型存在本质差异：
    - Claude Agent SDK：子进程模型，每次 query() 启动独立运行时
    - OpenAI Agents SDK：库原生模型，在当前进程内执行

    适配器层统一了外部接口（AsyncIterator[AgentEvent]），
    但内部实现需要分别处理进程管理和异步调用.
    """

    @abstractmethod
    async def execute(
        self,
        prompt: str,
        context: dict[str, Any],
        working_dir: str | None = None,
    ) -> AsyncIterator[AgentEvent]:
        """执行 Agent 任务，流式返回事件."""
        ...

    @abstractmethod
    async def cancel(self) -> None:
        """取消正在执行的任务."""
        ...
