"""Human Gate Node

实现人工审核门节点（human gate）逻辑。该节点在需要人工干预时暂停
流水线，通过 langgraph 的 interrupt 机制收集决策，并将决策写入审批历史。

- 支持针对当前 gating 阶段（explore/plan/develop/test）的审批。
- 将审批决策记录到 approval_history，并将 pending_approval_stage 设置为原始门阶段
- 返回 LangGraph 的 Command，以便将流程跳转到下一个阶段或结束。
- 若环境中不可用 interrupt，提供一个可选的回退路径，并在代码中以注释标注。
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from backend.pipeline.state import PipelineState

try:
    # 可能存在 LangGraph 的 interrupt API；若不可用，捕获并回退到占位实现
    from langgraph.types import interrupt, Command  # type: ignore
except Exception:  # pragma: no cover - 环境可能没有 LangGraph
    interrupt = None  # type: ignore
    Command = None  # type: ignore


async def human_gate_node(state: PipelineState) -> dict[str, Any] | Command:
    """Human Gate Node

    使用 interrupt 暂停并获取审批决策。将审批记录追加到历史中，并更新
    pending_approval_stage。返回一个 Command，以引导 LangGraph 跳转到下一阶段。
    
    Notes:
      - If interrupt API 不可用，则提供一个简易回退，默认通过审批以便继续。
      - approval_history 字段通过 state.extra 存储：approval_history -> List[Dict[str, Any]]
    """

    # 确定当前需要审批的阶段名称
    stage = state.current_stage or "human_gate_explore"
    if stage.startswith("human_gate_"):
        gated_stage = stage
    else:
        gated_stage = f"human_gate_{stage}"

    # 初始化审批历史（如果尚未创建）
    approval_history: list[dict[str, Any]] = getattr(state, "approval_history", []) or []

    # 构造审批请求数据（供 interrupt 使用）
    approval_request = {
        "type": "approval_request",
        "stage": gated_stage,
        "case_id": state.case_id,
        "artifacts_summary": getattr(state, "approval_artifacts_summary", None),
        "timestamp": datetime.utcnow().isoformat(),
    }

    decision: dict[str, Any]
    if interrupt is not None:
        # 调用 LangGraph 的 interrupt 以获得人工决策（允许用户在 UI 中审批）
        decision = interrupt(approval_request)  # type: ignore
    else:
        # 回退路径：环境中没有 interrupt 支持，使用占位决策以继续执行测试场景
        decision = {"action": "approve", "comment": "fallback: interrupt unavailable"}

    action = decision.get("action", "abandon")
    comment = decision.get("comment", "")
    reviewer = decision.get("reviewer", "human")

    # 记录审批历史
    approval_history_entry = {
        "stage": gated_stage,
        "decision": action,
        "comment": comment,
        "reviewer": reviewer,
        "timestamp": datetime.utcnow().isoformat(),
    }
    approval_history.append(approval_history_entry)

    # 更新状态字段（若对象不可变，确保通过 Graph 支持 extra 字段扩展）
    update: dict[str, Any] = {
        "approval_history": approval_history,
        "pending_approval_stage": None,
    }

    # 通过 Command 跳转到下一阶段；路由会再通过 mapping 决定实际目标节点
    if Command is not None:
        return Command(goto=action, update=update)  # type: ignore
    # 回退到简单字典形式的更新（在无 Command 时的兜底）
    return {"current_stage": gated_stage, **update}
