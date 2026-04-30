"""PipelineState 定义 — LangGraph StateGraph 共享状态."""
from __future__ import annotations

from typing import Literal, Optional, Any
from pydantic import BaseModel, Field


class CostSnapshot(BaseModel):
    """成本快照."""
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_usd: float = 0.0


class PipelineState(BaseModel):
    """Pipeline 共享状态 — 在 LangGraph 节点间传递.

    注意：此模型用于 StateGraph 的状态定义，也作为 checkpointer 的持久化格式.
    """

    case_id: str = Field(description="案例唯一标识")
    target_repo: str = Field(description="目标仓库，如 linux/qemu/opensbi")
    current_stage: Literal[
        "explore", "human_gate_explore",
        "plan", "human_gate_plan",
        "develop", "review", "human_gate_code",
        "test", "human_gate_test",
        "escalate", "completed", "abandoned",
    ] = Field(default="explore", description="当前阶段")

    input_context: dict[str, Any] = Field(default_factory=dict, description="用户输入上下文")

    exploration_result_ref: Optional[str] = Field(default=None, description="探索产物路径引用")
    execution_plan_ref: Optional[str] = Field(default=None, description="规划产物路径引用")
    development_result_ref: Optional[str] = Field(default=None, description="开发产物路径引用")
    review_verdict_ref: Optional[str] = Field(default=None, description="审核产物路径引用")
    test_result_ref: Optional[str] = Field(default=None, description="测试产物路径引用")

    review_iterations: int = Field(default=0, description="当前审核迭代次数")
    max_review_iterations: int = Field(default=3, description="最大审核迭代次数")
    review_score_history: list[float] = Field(default_factory=list, description="历史审核评分")

    pending_approval_stage: Optional[str] = Field(default=None, description="等待人工审核的阶段")
    approval_count: int = Field(default=0, description="人工审核通过次数")

    total_input_tokens: int = Field(default=0, description="累计输入 Token")
    total_output_tokens: int = Field(default=0, description="累计输出 Token")
    estimated_cost_usd: float = Field(default=0.0, description="累计预估成本（美元）")

    last_error: Optional[str] = Field(default=None, description="最后错误信息")
    retry_count: int = Field(default=0, description="当前阶段重试次数")

    class Config:
        extra = "allow"
