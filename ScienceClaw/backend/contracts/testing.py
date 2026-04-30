"""testing 阶段数据契约.

定义测试阶段的数据模型，包括测试结果、测试日志、覆盖率等。
"""
from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class TestFailure(BaseModel):
    """测试失败详情.

    Attributes:
        test_name: 测试名称
        error_message: 错误信息
        stack_trace: 堆栈跟踪（可选）
    """
    test_name: str = Field(..., description="测试名称")
    error_message: str = Field(..., description="错误信息")
    stack_trace: Optional[str] = Field(None, description="堆栈跟踪")


class TestResult(BaseModel):
    """测试阶段输出.

    Attributes:
        passed: 是否通过
        total_tests: 总测试数
        passed_tests: 通过数
        failed_tests: 失败数
        test_log_path: 测试日志路径
        coverage_percent: 覆盖率百分比（可选）
        qemu_version: QEMU版本（可选）
        failure_details: 失败详情列表
    """
    passed: bool = Field(default=False, description="是否通过")
    total_tests: int = Field(default=0, description="总测试数")
    passed_tests: int = Field(default=0, description="通过数")
    failed_tests: int = Field(default=0, description="失败数")
    test_log_path: str = Field(default="", description="测试日志路径")
    coverage_percent: Optional[float] = Field(None, ge=0, le=100, description="覆盖率百分比")
    qemu_version: Optional[str] = Field(None, description="QEMU版本")
    failure_details: list[TestFailure] = Field(default_factory=list, description="失败详情列表")
