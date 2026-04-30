"""Redis Pub/Sub + Stream 事件发布器."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import redis.asyncio as aioredis
from pydantic import BaseModel, Field


class PipelineEvent(BaseModel):
    """Pipeline 事件（通过 Redis Pub/Sub 传递）."""
    seq: int = Field(description="单调递增序列号")
    case_id: str = Field(description="案例 ID")
    event_type: str = Field(description="事件类型")
    data: dict[str, Any] = Field(default_factory=dict, description="事件数据")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class EventPublisher:
    """Agent 事件发布器 — 桥接 LangGraph 节点到 SSE."""

    def __init__(self, redis: aioredis.Redis):
        self.redis = redis
        self._seq_counters: dict[str, int] = {}

    async def publish(self, case_id: str, event_type: str, data: dict[str, Any]) -> None:
        """发布事件到 Redis."""
        seq = self._seq_counters.get(case_id, 0) + 1
        self._seq_counters[case_id] = seq

        event = PipelineEvent(
            seq=seq,
            case_id=case_id,
            event_type=event_type,
            data=data,
        )

        event_json = event.model_dump_json()

        await self.redis.publish(f"case:{case_id}:events", event_json)
        await self.redis.xadd(
            f"case:{case_id}:stream",
            {"event": event_json},
            maxlen=500,
        )

    async def get_events_since(self, case_id: str, last_seq: int) -> list[PipelineEvent]:
        """重连时恢复丢失的事件."""
        raw = await self.redis.xrange(f"case:{case_id}:stream")
        events = []
        for _, fields in raw:
            event_data = fields.get("event", "{}")
            try:
                event = PipelineEvent.model_validate_json(event_data)
                if event.seq > last_seq:
                    events.append(event)
            except Exception:
                continue
        return events
