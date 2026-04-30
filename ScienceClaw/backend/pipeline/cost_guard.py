"""成本熔断器 — 防止 Pipeline 成本超限."""
from __future__ import annotations

from backend.pipeline.state import PipelineState


class CostCircuitBreaker:
    """成本熔断器."""

    def __init__(
        self,
        max_cost_per_case: float = 10.0,
        max_cost_per_hour: float = 50.0,
    ):
        self.max_cost_per_case = max_cost_per_case
        self.max_cost_per_hour = max_cost_per_hour

    def check_before_agent(self, state: PipelineState) -> bool:
        """检查是否允许继续执行 Agent."""
        estimated = self._estimate_cost(state)
        return estimated < self.max_cost_per_case

    def _estimate_cost(self, state: PipelineState) -> float:
        """估算当前成本.

        使用 Claude Sonnet 4 定价：$3/M input, $15/M output.
        """
        input_tokens = state.total_input_tokens
        output_tokens = state.total_output_tokens

        input_cost = (input_tokens / 1_000_000) * 3.0
        output_cost = (output_tokens / 1_000_000) * 15.0

        return input_cost + output_cost
