"""Feature Flag 配置 — 控制 Pipeline 等实验性功能开关."""
from __future__ import annotations

from pydantic import BaseModel, Field
from backend.config import settings


class FeatureFlags(BaseModel):
    """功能开关配置."""

    PIPELINE_ENABLED: bool = Field(
        default=False,
        description="Pipeline 模式是否启用",
    )
    QEMU_SANDBOX_ENABLED: bool = Field(
        default=False,
        description="QEMU 沙箱是否启用",
    )

    @classmethod
    def from_settings(cls) -> FeatureFlags:
        """从全局配置加载功能开关."""
        return cls(
            PIPELINE_ENABLED=settings.pipeline_enabled,
            QEMU_SANDBOX_ENABLED=settings.qemu_sandbox_enabled,
        )
