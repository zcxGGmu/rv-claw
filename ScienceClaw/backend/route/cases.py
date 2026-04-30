from __future__ import annotations

import time
import json
import uuid
import asyncio
from typing import Any, Optional, List

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from backend.mongodb.db import db
from backend.config import settings
from backend.user.dependencies import require_user, User

router = APIRouter(prefix="/cases", tags=["cases"])


class ApiResponse(BaseModel):
    code: int = Field(default=0, description="Business status code, 0 means success")
    msg: str = Field(default="ok", description="Business message")
    data: Any = Field(default=None, description="Response data")


class CreateCaseRequest(BaseModel):
    target_repo: str = Field(..., description="Target repository (e.g. owner/repo)")
    input_context: dict[str, Any] = Field(default_factory=dict, description="Input context for the case")


class CaseItem(BaseModel):
    id: str
    target_repo: str
    input_context: dict[str, Any]
    status: str
    created_at: int
    created_by: str


class ListCases(BaseModel):
    cases: List[CaseItem]


class CaseDetail(BaseModel):
    id: str
    target_repo: str
    input_context: dict[str, Any]
    status: str
    created_at: int
    created_by: str


class ReviewRequest(BaseModel):
    decision: str = Field(..., description="Human review decision, e.g. 'approve' or 'reject'")
    notes: Optional[str] = Field(None, description="Optional reviewer notes")


class HistoryItem(BaseModel):
    id: str
    case_id: str
    decision: str
    notes: Optional[str] = None
    reviewer_id: str
    timestamp: int


class HistoryData(BaseModel):
    reviews: List[HistoryItem] = Field(default_factory=list)


@router.post("", response_model=ApiResponse)
async def create_case(body: CreateCaseRequest, current_user: User = Depends(require_user)) -> ApiResponse:
    """Create a new cases entry.

    Body:
      - target_repo: Target repository to solve
      - input_context: User provided input context
    """
    case_id = str(uuid.uuid4())
    now = int(time.time())

    doc = {
        "_id": case_id,
        "target_repo": body.target_repo,
        "input_context": body.input_context,
        "status": "pending",
        "created_at": now,
        "created_by": current_user.id,
    }
    await db.get_collection("contribution_cases").insert_one(doc)

    case_view = CaseDetail(
        id=case_id,
        target_repo=body.target_repo,
        input_context=body.input_context,
        status="pending",
        created_at=now,
        created_by=current_user.id,
    ).model_dump()
    return ApiResponse(data=case_view)


@router.get("", response_model=ApiResponse)
async def list_cases(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    target_repo: Optional[str] = Query(None),
    current_user: User = Depends(require_user),
) -> ApiResponse:
    """List cases with optional filters and pagination."""
    filt: dict[str, Any] = {}
    if status:
        filt["status"] = status
    if target_repo:
        filt["target_repo"] = target_repo

    skip = max((page - 1) * limit, 0)
    cursor = db.get_collection("contribution_cases").find(
        filt,
        {"_id": 1, "target_repo": 1, "input_context": 1, "status": 1, "created_at": 1, "created_by": 1},
    ).sort("created_at", -1).skip(skip).limit(limit)

    items: List[CaseItem] = []
    async for doc in cursor:
        items.append(
            CaseItem(
                id=str(doc.get("_id")),
                target_repo=doc.get("target_repo", ""),
                input_context=doc.get("input_context", {}),
                status=doc.get("status", ""),
                created_at=doc.get("created_at", 0),
                created_by=str(doc.get("created_by", "")),
            )
        )

    return ApiResponse(data=ListCases(cases=items).model_dump())


@router.get("/{case_id}", response_model=ApiResponse)
async def get_case(case_id: str = Path(..., description="Case ID"), current_user: User = Depends(require_user)) -> ApiResponse:
    """Get case details by id."""
    doc = await db.get_collection("contribution_cases").find_one({"_id": case_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Case not found")
    item = CaseDetail(
        id=case_id,
        target_repo=doc.get("target_repo", ""),
        input_context=doc.get("input_context", {}),
        status=doc.get("status", ""),
        created_at=doc.get("created_at", 0),
        created_by=str(doc.get("created_by", "")),
    ).model_dump()
    return ApiResponse(data=item)


@router.delete("/{case_id}", response_model=ApiResponse)
async def delete_case(case_id: str = Path(..., description="Case ID"), current_user: User = Depends(require_user)) -> ApiResponse:
    """Delete a case by id."""
    result = await db.get_collection("contribution_cases").delete_one({"_id": case_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Case not found")
    return ApiResponse(data={"ok": True})


@router.post("/{case_id}/start", response_model=ApiResponse)
async def start_case(case_id: str, current_user: User = Depends(require_user)) -> ApiResponse:
    """Start pipeline execution for a case (placeholder state management)."""
    doc = await db.get_collection("contribution_cases").find_one({"_id": case_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Case not found")
    # Simple access control: only creator can start unless admin in future
    if doc.get("created_by") != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    now = int(time.time())
    update = {
        "$set": {
            "status": "running",
            "current_stage": "explore",
            "started_at": now,
        }
    }
    await db.get_collection("contribution_cases").update_one({"_id": case_id}, update)

    # Persist an initial PipelineState snapshot in the case document (embedded)
    try:
        state = {
            "case_id": case_id,
            "target_repo": doc.get("target_repo", ""),
            "current_stage": "explore",
            "input_context": doc.get("input_context", {}),
        }
        await db.get_collection("contribution_cases").update_one({"_id": case_id}, {"$set": {"state": state}})
    except Exception:
        # best-effort embedding; ignore failures
        pass

    # Publish a start event to Redis for SSE consumers
    try:
        import redis.asyncio as aioredis
        r = aioredis.from_url(settings.redis_url)
        payload = {"case_id": case_id, "event_type": "start", "data": {"stage": "explore"}}
        await r.publish(f"case:{case_id}:events", json.dumps(payload))
        await r.close()
    except Exception:
        pass

    return ApiResponse(data={"case_id": case_id, "status": "running"})


@router.get("/{case_id}/events")
async def case_events(case_id: str, request: Request, current_user: User = Depends(require_user)):
    """SSE event stream for a given case, backed by Redis Pub/Sub."""
    # Fetch case to verify access
    doc = await db.get_collection("contribution_cases").find_one({"_id": case_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Case not found")
    if doc.get("created_by") != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    import redis.asyncio as aioredis
    redis_client = aioredis.from_url(settings.redis_url)
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(f"case:{case_id}:events")

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                except asyncio.CancelledError:
                    break
                if message:
                    data = message.get("data")
                    if isinstance(data, (bytes, bytearray)):
                        data = data.decode()
                    try:
                        ev = json.loads(data)
                        event_type = ev.get("event_type") or ev.get("event") or "message"
                        payload = ev.get("data", {})
                        yield {
                            "event": event_type,
                            "data": json.dumps(payload, ensure_ascii=False),
                        }
                    except Exception:
                        # Fallback: emit raw string
                        yield {"event": "message", "data": json.dumps({"raw": data})}
                else:
                    await asyncio.sleep(0.1)
        finally:
            try:
                await pubsub.unsubscribe(f"case:{case_id}:events")
            finally:
                await pubsub.close()
                await redis_client.close()

    return EventSourceResponse(event_generator())


@router.post("/{case_id}/review", response_model=ApiResponse)
async def submit_review(case_id: str, body: ReviewRequest, current_user: User = Depends(require_user)) -> ApiResponse:
    """Submit a human review decision for a case."""
    case_doc = await db.get_collection("contribution_cases").find_one({"_id": case_id})
    if not case_doc:
        raise HTTPException(status_code=404, detail="Case not found")

    review = {
        "_id": str(uuid.uuid4()),
        "case_id": case_id,
        "decision": body.decision,
        "notes": body.notes,
        "reviewed_by": current_user.id,
        "timestamp": int(time.time()),
    }
    await db.get_collection("human_reviews").insert_one(review)
    return ApiResponse(data={"review_id": review["_id"], "case_id": case_id, "decision": body.decision})


@router.get("/{case_id}/artifacts/{stage}", response_model=ApiResponse)
async def get_artifact(case_id: str, stage: str, current_user: User = Depends(require_user)) -> ApiResponse:
    """Retrieve artifacts for a given stage of a case."""
    stage = stage.strip().lower()
    field_map = {
        "explore": "exploration_result_ref",
        "plan": "execution_plan_ref",
        "develop": "development_result_ref",
        "review": "review_verdict_ref",
        "test": "test_result_ref",
    }
    if stage not in field_map:
        raise HTTPException(status_code=400, detail="Unsupported artifact stage")

    doc = await db.get_collection("contribution_cases").find_one({"_id": case_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Case not found")
    artifact_ref = doc.get(field_map[stage])
    return ApiResponse(data={"case_id": case_id, "stage": stage, "artifact_ref": artifact_ref})


@router.get("/{case_id}/history", response_model=ApiResponse)
async def get_history(case_id: str, current_user: User = Depends(require_user)) -> ApiResponse:
    """Get human review history for a case."""
    docs = db.get_collection("human_reviews")
    cursor = docs.find({"case_id": case_id}).sort("timestamp", -1)
    reviews: List[HistoryItem] = []
    async for d in cursor:
        reviews.append(
            HistoryItem(
                id=str(d.get("_id")),
                case_id=str(d.get("case_id")),
                decision=str(d.get("decision")),
                notes=d.get("notes"),
                reviewer_id=str(d.get("reviewed_by")),
                timestamp=int(d.get("timestamp") or 0),
            )
        )
    return ApiResponse(data=HistoryData(reviews=reviews).model_dump())
