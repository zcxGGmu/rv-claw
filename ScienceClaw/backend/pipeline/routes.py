"""Pipeline 条件边路由函数实现

实现两组路由函数：
- route_human_decision(state) 根据人工审核历史返回 approve/reject/abandon
- route_review_decision(state) 根据 Develop ↔ Review 的迭代收敛逻辑返回
  approve/reject/escalate
"""

from __future__ import annotations

from typing import Any, Dict

from backend.pipeline.state import PipelineState

# NOTE: 设计文档中的行为模式：保持无副作用的只读路由函数

def route_human_decision(state: PipelineState) -> str:
    """根据审批历史返回路由关键字。

    - 当 approvals_history 为空时，返回 'abandon' 表示放弃
    - 否则返回最近一次决策的 action（'approve'/'reject'/'abandon'）
    """
    history = getattr(state, "approval_history", []) or []  # type: ignore
    if not history:
        return "abandon"
    last = history[-1]
    decision = last.get("decision") or last.get("action")
    if decision not in {"approve", "reject", "abandon"}:
        return "abandon"
    return decision


def route_review_decision(state: PipelineState) -> str:
    """Convergence-based routing for Review stage.

    Implements convergence detention as described in design.md §5.5:
    - If an explicit approval exists, return 'approve'
    - If iterations >= max, escalate
    - If last two scores do not decrease and there is >50% overlap in findings,
      escalate; otherwise reject to continue iterations
    - Default to reject
    """
    # 1) 直接通过 verdict（若已经明确通过）
    verdict = getattr(state, "review_verdict", None) or getattr(state, "review_verdict_ref", None)
    if isinstance(verdict, dict) and verdict.get("approved"):
        return "approve"

    # 2) 迭代次数达到上限，升级
    iterations = int(getattr(state, "review_iterations", 0))
    max_iters = int(getattr(state, "max_review_iterations", 3))
    if iterations >= max_iters:
        return "escalate"

    # 3) 收敛检测：简单实现，基于评分历史和 findings 的 overlap
    scores: list[float] = list(getattr(state, "review_score_history", []))
    findings_history: list[list[Dict[str, Any]]] = list(getattr(state, "review_history", [])) if hasattr(state, "review_history") else []

    if len(scores) >= 2:
        last_score = scores[-1]
        prev_score = scores[-2]
        # 简单判定：若分数未减少且存在历史 findings，尝试 overlap 检测
        if last_score >= prev_score and len(findings_history) >= 2:
            curr_findings = verdict.get("findings", []) if isinstance(verdict, dict) else []
            prev_findings = findings_history[-2].get("findings", []) if isinstance(findings_history[-2], dict) else []
            def key_pair(f):
                return (f.get("file"), f.get("line"))
            prev_ids = {key_pair(f) for f in prev_findings}
            curr_ids = {key_pair(f) for f in curr_findings}
            overlap = len(prev_ids & curr_ids) / max(len(curr_ids) or 1, 1)
            if overlap > 0.5:
                return "escalate"

    # 4) 兜底：拒绝，继续迭代
    return "reject"
