"""OpenAI Agents SDK 适配器 — 库原生模型."""
from __future__ import annotations

from typing import Any, AsyncIterator

from backend.adapters.base import AgentAdapter, AgentEvent


class OpenAIAgentAdapter(AgentAdapter):
    """OpenAI Agents SDK 适配器 — 用于 Planner / Reviewer."""

    def __init__(self, agent_config: dict[str, Any]):
        self.agent_config = agent_config

    async def execute(
        self,
        prompt: str,
        context: dict[str, Any],
        working_dir: str | None = None,
    ) -> AsyncIterator[AgentEvent]:
        """执行 Agent 任务，流式返回事件."""
        try:
            yield AgentEvent(
                event_type="output",
                data={"content": f"OpenAI Agent execution placeholder for: {prompt[:50]}..."},
            )
        except Exception as e:
            yield AgentEvent(
                event_type="error",
                data={"message": str(e), "recoverable": False},
            )

    async def cancel(self) -> None:
        """OpenAI SDK 通过 Runner 管理取消."""
        pass
