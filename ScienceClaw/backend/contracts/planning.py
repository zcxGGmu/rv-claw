"""planning 阶段数据契约.

定义规划阶段的数据模型，包括开发步骤、测试用例、执行计划等。
"""
from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class DevStep(BaseModel):
    """开发步骤.

    Attributes:
        id: 步骤唯一标识
        description: 步骤描述
        target_files: 目标文件列表
        expected_changes: 预期变更说明
        risk_level: 风险等级 (low/medium/high)
        dependencies: 依赖的步骤ID列表
    """
    id: str = Field(..., description="步骤唯一标识")
    description: str = Field(..., description="步骤描述")
    target_files: list[str] = Field(default_factory=list, description="目标文件列表")
    expected_changes: str = Field(..., description="预期变更说明")
    risk_level: str = Field(default="low", description="风险等级")
    dependencies: list[str] = Field(default_factory=list, description="依赖的步骤ID列表")


class TestCase(BaseModel):
    """测试用例.

    Attributes:
        id: 用例唯一标识
        name: 用例名称
        type: 用例类型 (unit/integration/regression)
        description: 用例描述
        expected_result: 预期结果
        qemu_required: 是否需要QEMU环境
    """
    id: str = Field(..., description="用例唯一标识")
    name: str = Field(..., description="用例名称")
    type: str = Field(..., description="用例类型")
    description: str = Field(..., description="用例描述")
    expected_result: str = Field(..., description="预期结果")
    qemu_required: bool = Field(default=False, description="是否需要QEMU环境")


class ExecutionPlan(BaseModel):
    """规划阶段输出 — 执行计划.

    Attributes:
        dev_steps: 开发步骤列表
        test_cases: 测试用例列表
        qemu_config: QEMU配置（可选）
        estimated_tokens: 估计Token消耗
        risk_assessment: 风险评估报告
    """
    dev_steps: list[DevStep] = Field(default_factory=list, description="开发步骤列表")
    test_cases: list[TestCase] = Field(default_factory=list, description="测试用例列表")
    qemu_config: Optional[dict[str, Any]] = Field(None, description="QEMU配置")
    estimated_tokens: int = Field(default=0, description="估计Token消耗")
    risk_assessment: str = Field(default="", description="风险评估报告")
