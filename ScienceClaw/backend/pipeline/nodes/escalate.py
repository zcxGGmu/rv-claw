"""Escalation Node

实现流水线升级分支的节点。该节点将当前阶段标记为 escalated，并
记录升级原因。执行结束后，流水线通过 END 入口终止流程。"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from backend.pipeline.state import PipelineState


async def escalate_node(state: PipelineState) -> Dict[str, Any]:
    """Escalate the pipeline to a human-in-the-loop review or end state.

    This node records the escalation reason and moves the pipeline into the
    'escalate' stage. The surrounding graph defines the transition from
    'escalate' to END, effectively stopping the pipeline until manual intervention.
    """
    reason = getattr(state, "last_error", None) or getattr(state, "escalation_reason", None)
    if not reason:
        reason = "Unspecified escalation trigger."

    return {
        "current_stage": "escalate",
        "last_error": f"Escalation triggered: {reason} @ {datetime.utcnow().isoformat()}",
        "escalation_reason": reason,
    }
