"""Agent 产物管理器."""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import aiofiles


class ArtifactManager:
    """Agent 产物管理器."""

    def __init__(self, base_dir: str = "/data/artifacts"):
        self.base_dir = Path(base_dir)

    def get_case_dir(
        self,
        case_id: str,
        stage: str,
        round_num: int | None = None,
    ) -> Path:
        """获取案例目录路径."""
        path = self.base_dir / case_id / stage
        if round_num is not None:
            path = path / f"round_{round_num}"
        path.mkdir(parents=True, exist_ok=True)
        return path

    async def save_artifact(
        self,
        case_id: str,
        stage: str,
        filename: str,
        content: str | bytes,
        round_num: int | None = None,
    ) -> str:
        """保存产物并返回相对路径."""
        dir_path = self.get_case_dir(case_id, stage, round_num)
        file_path = dir_path / filename
        mode = "wb" if isinstance(content, bytes) else "w"
        async with aiofiles.open(file_path, mode) as f:
            await f.write(content)
        return str(file_path.relative_to(self.base_dir))

    async def load_artifact(self, relative_path: str) -> str:
        """根据相对路径加载产物."""
        file_path = self.base_dir / relative_path
        async with aiofiles.open(file_path, "r") as f:
            return await f.read()

    async def cleanup_case(self, case_id: str, keep_final: bool = True) -> None:
        """清理案例产物."""
        case_dir = self.base_dir / case_id
        if not case_dir.exists():
            return

        if not keep_final:
            shutil.rmtree(case_dir, ignore_errors=True)
            return

        for stage_dir in case_dir.iterdir():
            if stage_dir.is_dir():
                rounds = sorted(stage_dir.glob("round_*"))
                for old_round in rounds[:-1]:
                    shutil.rmtree(old_round)
