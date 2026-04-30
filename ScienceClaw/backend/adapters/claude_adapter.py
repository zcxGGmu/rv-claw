"""Claude Agent SDK 适配器 — 子进程模型."""
from __future__ import annotations

import asyncio
from typing import Any, AsyncIterator

from backend.adapters.base import AgentAdapter, AgentEvent


class ClaudeAgentAdapter(AgentAdapter):
    """Claude Agent SDK 适配器 — 子进程模型.

    重要：Claude Agent SDK 基于 Claude Code 架构，每次 query() 调用
    启动一个独立子进程。这意味着：
    - 不能共享进程内状态，需通过文件系统或 stdin/stdout 传递数据
    - 资源管理需要进程级控制（信号、PID 追踪、超时）
    - cancel() 需要发送 SIGTERM 到子进程
    """

    def __init__(
        self,
        allowed_tools: list[str],
        permission_mode: str = "acceptEdits",
        max_turns: int = 50,
        timeout_seconds: int = 1800,
    ):
        self.allowed_tools = allowed_tools
        self.permission_mode = permission_mode
        self.max_turns = max_turns
        self.timeout_seconds = timeout_seconds
        self._current_process: asyncio.subprocess.Process | None = None

    async def execute(
        self,
        prompt: str,
        context: dict[str, Any],
        working_dir: str | None = None,
    ) -> AsyncIterator[AgentEvent]:
        """执行 Agent 任务，流式返回事件."""
        try:
            async with asyncio.timeout(self.timeout_seconds):
                yield AgentEvent(
                    event_type="output",
                    data={"content": f"Claude Agent execution placeholder for: {prompt[:50]}..."},
                )
        except asyncio.TimeoutError:
            yield AgentEvent(
                event_type="error",
                data={
                    "message": f"Agent 执行超时 ({self.timeout_seconds}s)",
                    "recoverable": True,
                },
            )
        except Exception as e:
            yield AgentEvent(
                event_type="error",
                data={"message": str(e), "recoverable": False},
            )

    async def cancel(self) -> None:
        """通过信号终止子进程."""
        if self._current_process and self._current_process.returncode is None:
            self._current_process.terminate()
            try:
                await asyncio.wait_for(self._current_process.wait(), timeout=5)
            except asyncio.TimeoutError:
                self._current_process.kill()

    @staticmethod
    def _map_event_type(message: Any) -> str:
        """根据 Claude Agent SDK 消息类型映射."""
        msg_type = getattr(message, "type", "unknown")
        return {
            "assistant": "thinking",
            "tool_use": "tool_call",
            "tool_result": "tool_result",
            "result": "output",
        }.get(msg_type, "output")

    @staticmethod
    def _extract_data(message: Any) -> dict:
        """提取消息数据."""
        return {
            "type": getattr(message, "type", "unknown"),
            "content": getattr(message, "content", str(message)),
        }
