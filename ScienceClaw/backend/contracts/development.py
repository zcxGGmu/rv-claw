"""development 阶段数据契约.

定义开发阶段的数据模型，包括开发结果、补丁文件、变更统计等。
"""
from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class FileChange(BaseModel):
    """文件变更.

    Attributes:
        file_path: 文件路径
        change_type: 变更类型 (added/modified/deleted)
        patch: 补丁内容（可选）
        lines_added: 新增行数
        lines_removed: 删除行数
    """
    file_path: str = Field(..., description="文件路径")
    change_type: str = Field(default="modified", description="变更类型")
    patch: Optional[str] = Field(None, description="补丁内容")
    lines_added: int = Field(default=0, description="新增行数")
    lines_removed: int = Field(default=0, description="删除行数")


class DevelopmentResult(BaseModel):
    """开发阶段输出.

    Attributes:
        patch_files: 补丁文件路径列表
        changed_files: 变更的源文件列表
        file_changes: 文件变更详情列表
        commit_message: commit消息
        change_summary: 变更摘要
        lines_added: 总新增行数
        lines_removed: 总删除行数
    """
    patch_files: list[str] = Field(default_factory=list, description="补丁文件路径列表")
    changed_files: list[str] = Field(default_factory=list, description="变更的源文件列表")
    file_changes: list[FileChange] = Field(default_factory=list, description="文件变更详情列表")
    commit_message: str = Field(default="", description="commit消息")
    change_summary: str = Field(default="", description="变更摘要")
    lines_added: int = Field(default=0, description="总新增行数")
    lines_removed: int = Field(default=0, description="总删除行数")
