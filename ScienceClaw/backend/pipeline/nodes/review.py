"""review node implementation.

This module implements a deterministic, placeholder review loop for the
RV-Claw pipeline. It is intentionally self-contained and does not perform any
real SDK calls. All logic is designed to be easily replaceable by real review
mechanisms while preserving the expected state contract for the LangGraph
pipeline.

Design reference: tasks/design.md sections 5.3.4 and 5.3.5.
"""

from __future__ import annotations

from typing import Any

from ..state import PipelineState  # type: ignore


async def review_node(state: PipelineState) -> dict[str, Any]:
    """Deterministic, placeholder review node.

    Behaviour (placeholder):
- Increment iteration counter. If iterations reach max_review_iterations,
  approve the change; otherwise route back to develop for another cycle.
- Run deterministic (stub) checks resembling checkpatch.pl / sparse results.
- Produce a verdict and references for the review artefacts.
- Prepare convergence metadata to hint when the process has converged.

    Returns a state update dict containing:
- current_stage: next stage to execute (human_gate_code on approve, develop on reject)
- review_verdict_ref: path reference to the stored verdict artefact
- review_iterations: updated iteration count
- convergence: boolean flag indicating potential convergence
- review_score_history: appended score placeholder
- last_error: error message if any error occurred
- Any new keys (e.g. test_iterations) are allowed due to PipelineState.extra = 'allow'.
    """
    try:
        # Deterministic, placeholder iteration handling
        iteration = getattr(state, "review_iterations", 0) + 1

        # Deterministic check: approve only when reaching max iterations
        approved = iteration >= int(getattr(state, "max_review_iterations", 3))

        # Placeholder for deterministic checks (simulate checkpatch.pl / sparse)
        checks = {
            "patch_quality": "ok" if iteration < 2 else "ok",  # deterministic stub
            "sparse_scan": "pass" if iteration % 2 != 0 else "pass",
        }

        # Generate a verdict reference artefact path
        verdict_ref = f"{state.case_id}/review/round_{iteration}_verdict.json"

        verdict = {
            "approved": bool(approved),
            "checks": checks,
            "notes": f"Review round {iteration} {'approved' if approved else 'rejected'} by placeholder verifier.",
            "evidence": {
                "llm_review": "placeholder_llm_review",
                "deterministic_checks": True,
            },
        }

        # Update score history with a simple heuristic score (0.0-1.0)
        state_score_history = list(getattr(state, "review_score_history", []))
        state_score_history.append(1.0 if approved else 0.5)

        return {
            "current_stage": "human_gate_code" if approved else "develop",
            "review_verdict_ref": verdict_ref,
            "review_iterations": iteration,
            "review_verdict": verdict,
            "review_score_history": state_score_history,
            "convergence": {
                "converged": bool(approved) and iteration >= int(getattr(state, "max_review_iterations", 3))
            },
        }
    except Exception as e:
        # Graceful error handling
        return {
            "current_stage": "develop",
            "last_error": str(e),
        }
