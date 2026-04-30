"""审计日志 — 操作审计和合规追踪."""
from __future__ import annotations

import time
import uuid
from typing import Any, Optional
from datetime import datetime

from backend.mongodb.db import db


class AuditLogger:
    """审计日志记录器.

    记录所有关键操作，支持合规审计和问题追踪。
    """

    # 审计事件类型
    CASE_CREATED = "case_created"
    CASE_STARTED = "case_started"
    CASE_COMPLETED = "case_completed"
    CASE_CANCELLED = "case_cancelled"
    CASE_DELETED = "case_deleted"
    HUMAN_REVIEW_SUBMITTED = "human_review_submitted"
    PIPELINE_STAGE_CHANGED = "pipeline_stage_changed"
    ARTIFACT_CREATED = "artifact_created"
    AGENT_ACTION = "agent_action"
    COST_THRESHOLD_EXCEEDED = "cost_threshold_exceeded"
    SECURITY_ALERT = "security_alert"

    def __init__(self):
        self._collection = "audit_logs"

    async def log(
        self,
        event_type: str,
        user_id: Optional[str],
        case_id: Optional[str],
        details: dict[str, Any],
        ip_address: Optional[str] = None,
    ) -> str:
        """记录审计事件.

        Args:
            event_type: 事件类型
            user_id: 用户 ID
            case_id: 案例 ID
            details: 事件详情
            ip_address: 客户端 IP

        Returns:
            审计日志 ID
        """
        log_id = str(uuid.uuid4())
        doc = {
            "_id": log_id,
            "event_type": event_type,
            "user_id": user_id,
            "case_id": case_id,
            "details": details,
            "ip_address": ip_address,
            "timestamp": int(time.time()),
            "created_at": datetime.utcnow().isoformat(),
        }
        await db.get_collection(self._collection).insert_one(doc)
        return log_id

    async def get_logs(
        self,
        case_id: Optional[str] = None,
        user_id: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """查询审计日志.

        Args:
            case_id: 按案例 ID 过滤
            user_id: 按用户 ID 过滤
            event_type: 按事件类型过滤
            limit: 返回数量限制

        Returns:
            审计日志列表
        """
        filt: dict[str, Any] = {}
        if case_id:
            filt["case_id"] = case_id
        if user_id:
            filt["user_id"] = user_id
        if event_type:
            filt["event_type"] = event_type

        cursor = db.get_collection(self._collection).find(filt).sort("timestamp", -1).limit(limit)
        return [doc async for doc in cursor]

    async def get_case_timeline(self, case_id: str) -> list[dict[str, Any]]:
        """获取案例完整时间线.

        Args:
            case_id: 案例 ID

        Returns:
            按时间排序的审计事件列表
        """
        return await self.get_logs(case_id=case_id, limit=1000)


# 全局审计日志实例
audit_logger = AuditLogger()


async def log_case_created(
    case_id: str,
    user_id: str,
    target_repo: str,
    ip_address: Optional[str] = None,
) -> str:
    """记录案例创建事件."""
    return await audit_logger.log(
        event_type=AuditLogger.CASE_CREATED,
        user_id=user_id,
        case_id=case_id,
        details={"target_repo": target_repo},
        ip_address=ip_address,
    )


async def log_case_started(
    case_id: str,
    user_id: str,
    stage: str = "explore",
) -> str:
    """记录案例启动事件."""
    return await audit_logger.log(
        event_type=AuditLogger.CASE_STARTED,
        user_id=user_id,
        case_id=case_id,
        details={"initial_stage": stage},
    )


async def log_human_review(
    case_id: str,
    user_id: str,
    decision: str,
    stage: str,
) -> str:
    """记录人工审核事件."""
    return await audit_logger.log(
        event_type=AuditLogger.HUMAN_REVIEW_SUBMITTED,
        user_id=user_id,
        case_id=case_id,
        details={"decision": decision, "stage": stage},
    )


async def log_stage_transition(
    case_id: str,
    from_stage: str,
    to_stage: str,
) -> str:
    """记录阶段转换事件."""
    return await audit_logger.log(
        event_type=AuditLogger.PIPELINE_STAGE_CHANGED,
        user_id=None,
        case_id=case_id,
        details={"from": from_stage, "to": to_stage},
    )


async def log_cost_threshold(
    case_id: str,
    current_cost: float,
    threshold: float,
) -> str:
    """记录成本阈值警告."""
    return await audit_logger.log(
        event_type=AuditLogger.COST_THRESHOLD_EXCEEDED,
        user_id=None,
        case_id=case_id,
        details={"current_cost_usd": current_cost, "threshold_usd": threshold},
    )
