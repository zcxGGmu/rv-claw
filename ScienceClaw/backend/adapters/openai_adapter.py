"""OpenAI Agents SDK 适配器 — 统一使用 OpenAI 兼容接口."""
from __future__ import annotations

from typing import Any, AsyncIterator

from openai import AsyncOpenAI

from backend.adapters.base import AgentAdapter, AgentEvent
from backend.config import settings


class OpenAIAgentAdapter(AgentAdapter):
    """OpenAI 兼容 API 适配器 — 所有 LLM 调用统一走此接口."""

    def __init__(self, agent_config: dict[str, Any] | None = None):
        self.agent_config = agent_config or {}
        self._client: AsyncOpenAI | None = None
        self._cancelled = False

    def _get_client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(
                api_key=settings.openai_api_key,
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
        model = self.agent_config.get("model", settings.openai_model)
        system_prompt = self.agent_config.get("system_prompt", "")

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
