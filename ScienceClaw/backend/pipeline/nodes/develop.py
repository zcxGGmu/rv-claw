"""Develop Node – placeholder implementation.

This module implements develop_node(state) as a placeholder for the Claude
Agent SDK driven development step. Real code generation / patch application will
be wired in future iterations. For now we create a minimal development artifact
and move the pipeline to the next review stage.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend.pipeline.state import PipelineState


async def develop_node(state: PipelineState) -> dict[str, Any]:
    """Developer Agent – placeholder development.

    Creates a placeholder patch artifact and a corresponding development result
    reference. Advances the pipeline to the review stage for human inspection.
    """
    try:
        # Placeholder development result structure
        patch_dir = Path("artifacts") / state.case_id / "develop" / "round_1"
        patch_dir.mkdir(parents=True, exist_ok=True)
        patch_path = patch_dir / "0001-placeholder.patch"
        patch_path.write_text("# placeholder patch\n", encoding="utf-8")

        development_result = {
            "patch_files": [str(patch_path)],
            "changes": [{"file": "placeholder.txt", "patch": "- placeholder"}],
            "description": "Placeholder development result for the case.",
        }

        dev_result_path = patch_dir / "development_result.json"
        with dev_result_path.open("w", encoding="utf-8") as f:
            json.dump(development_result, f, indent=2)

        return {
            "development_result_ref": str(dev_result_path),
            "current_stage": "review",
        }
    except Exception as e:
        return {
            "current_stage": "escalate",
            "last_error": str(e),
        }
