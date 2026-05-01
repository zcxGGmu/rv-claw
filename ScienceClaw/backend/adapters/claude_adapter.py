"""Claude Agent SDK 适配器 — 统一使用 OpenAI 兼容接口.

注意: 由于所有 API 配置已统一为同一 OpenAI 兼容 endpoint，
本适配器内部实际调用 OpenAI 兼容 API，而非 Claude Agent SDK。
保留 ClaudeAgentAdapter 类名以兼容现有 Pipeline 节点代码。
"""
from __future__ import annotations

from typing import Any, AsyncIterator

from openai import AsyncOpenAI

from backend.adapters.base import AgentAdapter, AgentEvent
from backend.config import settings


class ClaudeAgentAdapter(AgentAdapter):
    """Claude 适配器 — 统一走 OpenAI 兼容接口."""

    def __init__(
        self,
        allowed_tools: list[str] | None = None,
        permission_mode: str = "acceptEdits",
        max_turns: int = 50,
        timeout_seconds: int = 1800,
    ):
        self.allowed_tools = allowed_tools or []
        self.permission_mode = permission_mode
        self.max_turns = max_turns
        self.timeout_seconds = timeout_seconds
        self._client: AsyncOpenAI | None = None
        self._cancelled = False

    def _get_client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(
                api_key=settings.claude_api_key or settings.openai_api_key,
                base_url=settings.openai_base_url,
            )
        return self._client

    async def execute(
        self,
        prompt: str,
        context: dict[str, Any],
        working_dir: str | None = None,
    ) -> AsyncIterator[AgentEvent]:
        """执行 Agent 任务，流式返回事件."""
        self._cancelled = False
        model = settings.claude_model
        system_prompt = context.get("system_prompt", "")

        input_content: list[dict[str, str]] = []
        if system_prompt:
            input_content.append({"role": "system", "content": system_prompt})
        input_content.append({"role": "user", "content": prompt})

        try:
            yield AgentEvent(
                event_type="thinking",
                data={"content": f"Calling {model} via {settings.openai_base_url}..."},
            )

            client = self._get_client()
            response = await client.responses.create(
                model=model,
                input=input_content,
                max_output_tokens=settings.max_tokens,
            )

            text_parts = []
            for item in response.output:
                if item.type == "message" and item.content:
                    for part in item.content:
                        if part.type == "output_text":
                            text_parts.append(part.text)

            full_text = "".join(text_parts)
            yield AgentEvent(
                event_type="output",
                data={"content": full_text, "finished": True},
            )

        except Exception as e:
            yield AgentEvent(
                event_type="error",
                data={"message": str(e), "recoverable": False},
            )

    async def cancel(self) -> None:
        """标记取消状态以终止流式输出."""
        self._cancelled = True
        if self._client:
            await self._client.close()
            self._client = None

    @staticmethod
    def _map_event_type(message: Any) -> str:
        """根据消息类型映射（兼容旧接口）."""
        msg_type = getattr(message, "type", "unknown")
        return {
            "assistant": "thinking",
            "tool_use": "tool_call",
            "tool_result": "tool_result",
            "result": "output",
        }.get(msg_type, "output")

    @staticmethod
    def _extract_data(message: Any) -> dict:
        """提取消息数据（兼容旧接口）."""
        return {
            "type": getattr(message, "type", "unknown"),
            "content": getattr(message, "content", str(message)),
        }
