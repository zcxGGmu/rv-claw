# Pipeline 状态机转换规则

> **版本**: v1.0  
> **日期**: 2026-04-29  
> **适用范围**: rv-claw Pipeline 案例（Case）的全生命周期状态管理  
> **权威来源**: `tasks/design.md` §5.x + `tasks/codex/rv-claw-refactor-plan.md` §5.5  
> **强制执行**: 所有修改 `case.status` 的代码必须通过本规则的校验

---

## 0. 状态定义

Pipeline Case 共有 **13 个状态**：

| 状态 | 说明 | 是否可人工审核 |
|------|------|--------------|
| `created` | 案例已创建，尚未启动 | ❌ |
| `exploring` | Explore 节点运行中 | ❌ |
| `pending_explore_review` | Explore 完成，等待人工审核 | ✅ |
| `planning` | Plan 节点运行中 | ❌ |
| `pending_plan_review` | Plan 完成，等待人工审核 | ✅ |
| `developing` | Develop 节点运行中 | ❌ |
| `reviewing` | Review 节点运行中 | ❌ |
| `pending_code_review` | Review 完成，等待人工审核 | ✅ |
| `testing` | Test 节点运行中 | ❌ |
| `pending_test_review` | Test 完成，等待人工审核 | ✅ |
| `completed` | 全部阶段完成 | ❌ |
| `failed` | 某阶段失败且无法恢复 | ❌ |
| `abandoned` | 人工放弃 | ❌ |
| `escalated` | 升级到人工处理（超出自动能力） | ✅（仅 admin） |

---

## 1. 合法转换矩阵

### 1.1 核心转换图

```text
                              +------------------+
                              |     created      |
                              +--------+---------+
                                       | start()
                                       v
                              +--------+---------+
                              |    exploring     |
                              +--------+---------+
                                       | explore_node 完成
                                       v
                       +---------------+---------------+
                       |  pending_explore_review       |
                       +---------------+---------------+
            approve() /| reject() / abandon()          |\ reject_to(explore)
                      |                                   |
                      v                                   v
            +---------+---------+             +-----------+-----------+
            |     planning       |             |    exploring (retry)  |
            +---------+---------+             +-----------------------+
                      | plan_node 完成
                      v
       +--------------+--------------+
       |   pending_plan_review        |
       +--------------+--------------+
approve()/| reject()/abandon()        |\ reject_to(plan)
         |                              |
         v                              v
+--------+---------+      +------------+------------+
|    developing     |      |    planning (retry)   |
+--------+---------+      +-----------------------+
         | develop_node 完成
         v
  +------+------+
  |   reviewing  |
  +------+------+
         | review_node 完成
         v
+--------+---------+
| pending_code_review|
+--------+---------+
approve()/| reject()/abandon()        |\ reject_to(develop)
         |                              |
         v                              v
+--------+---------+      +------------+------------+
|     testing       |      |   developing (retry)  |
+--------+---------+      +-----------------------+
         | test_node 完成
         v
+--------+---------+
| pending_test_review|
+--------+---------+
approve()/| reject()/abandon()        |\ reject_to(test)
         |                              |
         v                              v
+--------+---------+      +------------+------------+
|    completed      |      |    testing (retry)    |
+-------------------+      +-----------------------+
```

### 1.2 合法转换表

| 当前状态 | 允许的目标状态 | 触发条件 | 执行者 |
|----------|--------------|----------|--------|
| `created` | `exploring` | `POST /cases/{id}/start` | 任意认证用户 |
| `exploring` | `pending_explore_review` | `explore_node` 成功完成 | 系统（Agent） |
| `exploring` | `failed` | `explore_node` 失败且重试耗尽 | 系统（Agent） |
| `pending_explore_review` | `planning` | `review.action = "approve"` | 人工 |
| `pending_explore_review` | `exploring` | `review.action = "reject_to"` + `reject_to_stage = "explore"` | 人工 |
| `pending_explore_review` | `abandoned` | `review.action = "abandon"` | 人工 |
| `planning` | `pending_plan_review` | `plan_node` 成功完成 | 系统（Agent） |
| `planning` | `failed` | `plan_node` 失败且重试耗尽 | 系统（Agent） |
| `pending_plan_review` | `developing` | `review.action = "approve"` | 人工 |
| `pending_plan_review` | `planning` | `review.action = "reject_to"` + `reject_to_stage = "plan"` | 人工 |
| `pending_plan_review` | `abandoned` | `review.action = "abandon"` | 人工 |
| `developing` | `reviewing` | `develop_node` 成功完成 | 系统（Agent） |
| `developing` | `failed` | `develop_node` 失败且重试耗尽 | 系统（Agent） |
| `reviewing` | `pending_code_review` | `review_node` 成功完成（无严重问题） | 系统（Agent） |
| `reviewing` | `developing` | `review_node` 发现需修复（自动迭代） | 系统（Agent） |
| `reviewing` | `escalated` | `review_node` 判定需人工介入（第 3 轮仍不通过） | 系统（Agent） |
| `pending_code_review` | `testing` | `review.action = "approve"` | 人工 |
| `pending_code_review` | `developing` | `review.action = "reject_to"` + `reject_to_stage = "develop"` | 人工 |
| `pending_code_review` | `abandoned` | `review.action = "abandon"` | 人工 |
| `testing` | `pending_test_review` | `test_node` 成功完成 | 系统（Agent） |
| `testing` | `failed` | `test_node` 失败且重试耗尽 | 系统（Agent） |
| `pending_test_review` | `completed` | `review.action = "approve"` | 人工 |
| `pending_test_review` | `testing` | `review.action = "reject_to"` + `reject_to_stage = "test"` | 人工 |
| `pending_test_review` | `abandoned` | `review.action = "abandon"` | 人工 |
| `failed` | `exploring` | `POST /cases/{id}/retry`（从第一阶段重试） | 任意认证用户 |
| `abandoned` | — | 终止态，不允许任何转换 | — |
| `completed` | — | 终止态，不允许任何转换 | — |
| `escalated` | `developing` | admin 判定继续 | admin |
| `escalated` | `abandoned` | admin 判定放弃 | admin |

### 1.3 非法转换（必须拒绝）

以下转换**绝对禁止**，后端必须返回 `409 Conflict`：

| 非法转换 | 拒绝理由 |
|----------|----------|
| `created` → 除 `exploring` 外的任何状态 | 必须先调用 start |
| `exploring` → `developing` / `testing` / `completed` | 必须经历审核门 |
| `pending_*_review` → `completed` | 必须按顺序通过所有阶段 |
| `developing` → `testing` | 必须经过 review |
| `testing` → `completed` | 必须经过最终审核 |
| 任意状态 → `created` | created 是初始态 |
| `completed` / `abandoned` → 任意状态 | 终止态不可恢复（如需重新执行，创建新 case） |
| `failed` → `completed` / `abandoned` 之外 | 只能从 failed retry 到 exploring |

---

## 2. 转换触发条件详解

### 2.1 系统自动推进

由 LangGraph 节点执行完成后自动触发：

```python
# 节点完成后的状态转换逻辑（伪代码）
async def on_node_complete(case_id: str, stage: str, result: NodeResult):
    case = await case_service.get(case_id)
    
    # 只有运行中状态才能自动推进
    if case.status != f"{stage}_ing":
        raise StateTransitionError(f"Case not in {stage}ing state")
    
    if result.success:
        # 成功：进入 pending_review
        new_status = f"pending_{stage}_review"
        await case_service.update_status(case_id, new_status)
        await audit_service.log(case_id, "stage_completed", {"stage": stage})
        await event_publisher.publish(case_id, "stage_change", {"to": new_status})
    else:
        # 失败：进入 failed
        if result.retry_exhausted:
            await case_service.update_status(case_id, "failed")
            await case_service.update_field(case_id, "last_error", result.error)
            await audit_service.log(case_id, "stage_failed", {"stage": stage, "error": result.error})
```

### 2.2 人工审核触发

由 `POST /cases/{id}/review` 触发：

```python
# 审核请求体
class ReviewRequest(BaseModel):
    review_id: str           # 幂等去重
    action: Literal["approve", "reject", "reject_to", "abandon", "modify"]
    comment: str
    reject_to_stage: Optional[Literal["explore", "plan", "develop", "test"]]
    modified_artifact_ref: Optional[str]

# 转换规则
async def process_review(case_id: str, review: ReviewRequest):
    case = await case_service.get(case_id)
    
    # 校验：当前必须是 pending_*_review 状态
    if not case.status.startswith("pending_"):
        raise HTTPException(409, f"Case is not pending review (current: {case.status})")
    
    # 校验：action 与状态匹配
    current_stage = case.status.replace("pending_", "").replace("_review", "")
    
    if review.action == "approve":
        # 确定下一个阶段
        next_stage = _get_next_stage(current_stage)
        if next_stage:
            new_status = f"{next_stage}_ing"
        else:
            new_status = "completed"
    
    elif review.action == "reject_to":
        if not review.reject_to_stage:
            raise HTTPException(422, "reject_to action requires reject_to_stage")
        # 校验：reject_to_stage 必须在当前阶段之前或等于当前阶段
        if _stage_order(review.reject_to_stage) > _stage_order(current_stage):
            raise HTTPException(422, "Cannot reject to a future stage")
        new_status = f"{review.reject_to_stage}_ing"
    
    elif review.action == "abandon":
        new_status = "abandoned"
    
    elif review.action == "modify":
        if not review.modified_artifact_ref:
            raise HTTPException(422, "modify action requires modified_artifact_ref")
        # 使用人工修改后的 artifact 继续
        await artifact_service.apply_modification(case_id, review.modified_artifact_ref)
        new_status = f"{current_stage}_ing"  # 重新执行当前阶段
    
    # 幂等校验
    if await review_service.exists(review.review_id):
        raise HTTPException(409, "Review already processed")
    
    # 执行转换
    await case_service.update_status(case_id, new_status)
    await review_service.save(review)
    await audit_service.log(case_id, "review_submitted", {
        "action": review.action,
        "stage": current_stage,
        "reviewer": current_user.id
    })
    
    # 恢复 LangGraph 执行
    if review.action in ("approve", "reject_to", "modify"):
        await pipeline_service.resume(case_id, review.action, review.reject_to_stage)
    
    await event_publisher.publish(case_id, "review_submitted", {
        "action": review.action,
        "new_status": new_status
    })
```

### 2.3 阶段顺序映射

```python
_STAGE_ORDER = {
    "explore": 1,
    "plan": 2,
    "develop": 3,
    "review": 4,
    "test": 5,
}

def _get_next_stage(current: str) -> Optional[str]:
    mapping = {
        "explore": "plan",
        "plan": "develop",
        "develop": "test",
        "test": None,  # completed
    }
    return mapping.get(current)
```

---

## 3. 转换副作用

每次状态转换必须触发以下副作用：

### 3.1 必须执行的副作用

| 副作用 | 说明 | 失败处理 |
|--------|------|----------|
| 更新 `case.status` | MongoDB 原子更新 | 失败则整体回滚 |
| 更新 `case.current_stage` | 与 status 同步 | 同左 |
| 更新 `case.updated_at` | ISO 8601 时间戳 | 同左 |
| 写入 `audit_log` | 记录转换事件 | 异步写入，失败告警但不阻塞 |
| 发送 SSE 事件 | `stage_change` 或 `review_submitted` | 异步发送，失败重试 3 次 |
| 更新 `case.cost` | 累计当前阶段成本 | 异步更新，失败记录日志 |

### 3.2 条件性副作用

| 条件 | 副作用 |
|------|--------|
| `approve` 且是最终阶段 | 设置 `case.completed_at` |
| `abandon` | 设置 `case.abandoned_at` |
| `failed` | 设置 `case.last_error`，保存失败产物 |
| `reject_to` | 递增 `case.review_iterations`（若超过 `max_review_iterations` → `escalated`） |
| `modify` | 保存人工修改后的 artifact 版本 |

---

## 4. 并发控制

### 4.1 状态转换互斥

```python
# 使用 MongoDB 乐观锁
async def update_status_atomic(case_id: str, expected_status: str, new_status: str):
    result = await cases_collection.update_one(
        {"_id": case_id, "status": expected_status},
        {"$set": {"status": new_status, "updated_at": now()}}
    )
    if result.modified_count == 0:
        raise StateTransitionError(
            f"Case {case_id} status changed concurrently. Expected {expected_status}."
        )
```

### 4.2 审核幂等性

- `review_id` 必须全局唯一（UUID v4 或 Snowflake）。
- 同一 `review_id` 多次提交 → 返回 `409`，不重复执行转换。
- 建议 Redis 缓存 `review_id` 24h，防止 MongoDB 查询延迟。

### 4.3 节点执行锁

- 每个 case 同时只能有一个节点在运行（LangGraph 单线程执行）。
- 人工审核提交时，若节点仍在运行 → 返回 `409`（"Case is still running"）。

---

## 5. API 响应规范

### 5.1 成功转换

```json
{
  "status": "ok",
  "case_id": "case_xxx",
  "previous_status": "pending_explore_review",
  "new_status": "planning",
  "review_id": "rev_xxx",
  "timestamp": "2026-04-29T13:00:00Z"
}
```

### 5.2 非法转换（409 Conflict）

```json
{
  "detail": "Invalid state transition",
  "error_code": "INVALID_STATE_TRANSITION",
  "current_status": "exploring",
  "requested_action": "approve",
  "allowed_actions": ["wait"],
  "message": "Case is in 'exploring' status. Only automatic node completion can change this state."
}
```

### 5.3 并发冲突（409 Conflict）

```json
{
  "detail": "Case status changed concurrently",
  "error_code": "CONCURRENT_MODIFICATION",
  "expected_status": "pending_explore_review",
  "actual_status": "planning",
  "suggestion": "Refresh case details and retry."
}
```

### 5.4 审核重复提交（409 Conflict）

```json
{
  "detail": "Review already processed",
  "error_code": "DUPLICATE_REVIEW",
  "review_id": "rev_xxx",
  "processed_at": "2026-04-29T13:00:00Z"
}
```

---

## 6. 测试要求

### 6.1 必须测试的转换路径

| 测试场景 | 类型 |
|----------|------|
| `created` → `exploring` → `pending_explore_review` → `planning` | 单元测试 |
| 完整 happy path（全部 4 个审核通过） | 集成测试 |
| `developing` → `reviewing` → `developing`（迭代 3 轮后 escalate） | 集成测试 |
| 非法转换（如 `exploring` → `approve`）→ 409 | 单元测试 |
| 并发修改 → 409 | 单元测试 |
| 重复 review_id → 409 | 单元测试 |
| `failed` → `exploring`（retry） | 集成测试 |
| `abandon` 任意 pending 状态 | 单元测试 |

### 6.2 状态机不变式

以下不变式必须在所有测试中保持：

1. `status` 永远是 13 个合法值之一。
2. `current_stage` 与 `status` 一致（`exploring` → `explore`，`pending_explore_review` → `explore`）。
3. 终止态（`completed`, `abandoned`, `failed`）不允许任何出边。
4. 审核态（`pending_*_review`）只允许人工 action 转换。
5. 运行态（`*ing`）只允许节点完成或失败转换。

---

## 7. 与 LangGraph 的集成

### 7.1 节点返回与状态映射

```python
# LangGraph 节点返回 dict，必须包含 "status" 字段
async def explore_node(state: PipelineState) -> dict:
    try:
        result = await agent_adapter.explore(state)
        return {
            "status": "pending_explore_review",
            "exploration_result": result,
            "messages": state.messages + [result.summary_message]
        }
    except Exception as e:
        return {
            "status": "failed",
            "last_error": str(e),
            "messages": state.messages + [error_message(e)]
        }
```

### 7.2 条件边路由

```python
def route_after_explore(state: PipelineState) -> str:
    if state.status == "pending_explore_review":
        return "human_gate_explore"
    elif state.status == "failed":
        return "escalate_node"
    else:
        raise StateMachineError(f"Unexpected status after explore: {state.status}")

builder.add_conditional_edges("explore_node", route_after_explore)
```

### 7.3 Human-in-the-Loop 中断

```python
# 在 human_gate 节点调用 interrupt()
async def human_gate_explore(state: PipelineState) -> dict:
    # 发送审核请求事件
    await event_publisher.publish(state.case_id, "review_request", {
        "stage": "explore",
        "artifact_ref": state.exploration_result_ref
    })
    # 中断执行，等待人工审核
    raise NodeInterrupt("Waiting for human review of exploration result")

# 恢复时
# ReviewService 调用 Command(resume={"action": "approve", ...})
```

---

> **本规则自 2026-04-29 起生效。所有修改 `case.status` 的代码必须实现本规则定义的转换矩阵、副作用和并发控制。**  
> **规则本身的修改需通过人类工程师审批。**
