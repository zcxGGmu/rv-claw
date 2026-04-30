"""test node implementation.

This module implements a placeholder test_node for RV-Claw. It intentionally
avoids any real sandboxing or QEMU integration, providing a deterministic
stub that can be easily swapped out with real test execution logic.

Design reference: tasks/design.md sections 5.3.4 and 5.3.5.
"""

from __future__ import annotations

from typing import Any

from ..state import PipelineState  # type: ignore


async def test_node(state: PipelineState) -> dict[str, Any]:
    """Test node placeholder.

    Behaviour (placeholder):
- Increment a per-test counter (stored in extra state) to simulate iterations.
- Simulate a QEMU sandbox run by a deterministic flag.
- Produce a test_result_ref artefact path and a minimal result payload.
- Route to human_gate_test for human verification after test execution.

    Returns a state update dict containing:
- current_stage: always set to "human_gate_test" to indicate human gate is next
- test_result_ref: artefact path for the test outcome
- test_iterations: updated iteration counter (optional, stored in extra state)
- test_verdict: summary verdict payload
- last_error: error message if any error occurred
    """
    try:
        # Simple, deterministic iteration counter using extra state
        iterations = int(getattr(state, "test_iterations", 0)) + 1

        # Placeholder for test execution using a QEMU sandbox (not real execution)
        sandbox_success = True  # deterministic placeholder

        verdict_ref = f"{state.case_id}/test/round_{iterations}_verdict.json"
        verdict = {
            "round": iterations,
            "success": sandbox_success,
            "logs": "placeholder_sandbox_logs",
        }

        # Persist the next iteration count back into the state for next round
        next_iterations = iterations

        return {
            "current_stage": "human_gate_test",
            "test_result_ref": verdict_ref,
            "test_iterations": next_iterations,
            "test_verdict": verdict,
        }
    except Exception as e:
        return {
            "current_stage": "test",
            "last_error": str(e),
        }
