"""exploration 阶段数据契约.

定义探索阶段的数据模型，包括发现结果、证据、可行性评分等。
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class ContributionType(str, Enum):
    """贡献类型枚举."""
    ISA_EXTENSION = "isa_extension"
    BUG_FIX = "bug_fix"
    OPTIMIZATION = "optimization"
    DOCUMENTATION = "documentation"
    TEST_COVERAGE = "test_coverage"
    CLEANUP = "cleanup"


class Evidence(BaseModel):
    """证据项 — 支撑贡献机会的依据.

    Attributes:
        source: 证据来源，如 "patchwork", "mailing_list", "code_analysis"
        url: 来源链接（可选）
        content: 证据内容摘要
        relevance: 相关性评分 0-1
    """
    source: str = Field(..., description="证据来源")
    url: Optional[str] = Field(None, description="来源链接")
    content: str = Field(..., description="证据内容摘要")
    relevance: float = Field(default=0.5, ge=0, le=1, description="相关性评分 0-1")


class ExplorationResult(BaseModel):
    """探索阶段输出.

    Attributes:
        contribution_type: 贡献类型
        title: 贡献标题
        summary: 贡献摘要
        target_repo: 目标仓库
        target_files: 目标文件列表
        evidence: 证据列表
        feasibility_score: 可行性评分 0-1
        estimated_complexity: 估计复杂度 (low/medium/high)
        upstream_status: 上游接受可能性评估
    """
    contribution_type: ContributionType = Field(..., description="贡献类型")
    title: str = Field(..., description="贡献标题")
    summary: str = Field(..., description="贡献摘要")
    target_repo: str = Field(..., description="目标仓库")
    target_files: list[str] = Field(default_factory=list, description="目标文件列表")
    evidence: list[Evidence] = Field(default_factory=list, description="证据列表")
    feasibility_score: float = Field(default=0.5, ge=0, le=1, description="可行性评分 0-1")
    estimated_complexity: str = Field(default="medium", description="估计复杂度")
    upstream_status: str = Field(default="unknown", description="上游接受可能性评估")


class ContributionOpportunity(BaseModel):
    """贡献机会 — 用于展示给用户的候选项目.

    Attributes:
        id: 机会唯一标识
        exploration_result: 探索结果
        discovered_at: 发现时间戳
        status: 状态 (new/viewed/accepted/rejected)
    """
    id: str = Field(..., description="机会唯一标识")
    exploration_result: ExplorationResult = Field(..., description="探索结果")
    discovered_at: int = Field(..., description="发现时间戳")
    status: str = Field(default="new", description="状态")
