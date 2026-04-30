"""review 阶段数据契约.

定义审核阶段的数据模型，包括审核发现、审核裁决等。
"""
from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class ReviewFinding(BaseModel):
    """审核发现项.

    Attributes:
        severity: 严重级别 (critical/major/minor/suggestion)
        category: 类别 (security/correctness/style/performance)
        file: 文件路径
        line: 行号（可选）
        description: 问题描述
        suggestion: 修复建议（可选）
    """
    severity: str = Field(..., description="严重级别")
    category: str = Field(..., description="类别")
    file: str = Field(..., description="文件路径")
    line: Optional[int] = Field(None, description="行号")
    description: str = Field(..., description="问题描述")
    suggestion: Optional[str] = Field(None, description="修复建议")


class StaticAnalysisResult(BaseModel):
    """静态分析结果.

    Attributes:
        tool: 工具名称 (checkpatch/sparse/smatch)
        findings: 发现列表
        passed: 是否通过
    """
    tool: str = Field(..., description="工具名称")
    findings: list[str] = Field(default_factory=list, description="发现列表")
    passed: bool = Field(default=True, description="是否通过")


class ReviewVerdict(BaseModel):
    """审核阶段输出.

    Attributes:
        approved: 是否通过
        findings: 审核发现列表
        iteration: 当前迭代次数
        reviewer_model: 审核使用的模型
        summary: 审核总结
        static_analysis: 静态分析结果
    """
    approved: bool = Field(default=False, description="是否通过")
    findings: list[ReviewFinding] = Field(default_factory=list, description="审核发现列表")
    iteration: int = Field(default=1, description="当前迭代次数")
    reviewer_model: str = Field(default="", description="审核使用的模型")
    summary: str = Field(default="", description="审核总结")
    static_analysis: list[StaticAnalysisResult] = Field(default_factory=list, description="静态分析结果")
