"""Plan Node – placeholder implementation.

Implements plan_node(state) as a placeholder following design.md sections
5.3.2. The real planning logic will be wired to an OpenAI Agents Planner in
future iterations. Here we generate a minimal execution plan artifact and
advance the pipeline to the next human gate stage.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend.pipeline.state import PipelineState


async def plan_node(state: PipelineState) -> dict[str, Any]:
    """Planner Agent – placeholder planning.

    Generates a simple, placeholder execution plan and stores it as an artifact.
    Updates state with a reference to the artifact and advances to the human gate
    for planning results.

    Returns:
        A dict containing:
        - execution_plan_ref: path to the saved artifact
        - current_stage: next stage in the pipeline (human_gate_plan)
    """
    try:
        plan = {
            "plan_summary": "Placeholder development plan for the given exploration result.",
            "steps": [
                {"step": 1, "description": "Placeholder step: initialize environment"},
                {"step": 2, "description": "Placeholder step: apply patch scaffold"},
            ],
            "risks": {"complexity": "low"},
        }

        artifact_dir = Path("artifacts") / state.case_id / "plan"
        artifact_dir.mkdir(parents=True, exist_ok=True)
        report_path = artifact_dir / "execution_plan.json"
        with report_path.open("w", encoding="utf-8") as f:
            json.dump(plan, f, indent=2)

        return {
            "execution_plan_ref": str(report_path),
            "current_stage": "human_gate_plan",
        }
    except Exception as e:
        return {
            "current_stage": "escalate",
            "last_error": str(e),
        }
