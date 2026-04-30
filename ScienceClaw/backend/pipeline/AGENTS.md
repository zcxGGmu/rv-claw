# Pipeline Module Knowledge Base

**Generated:** 2026-04-30  
**Scope:** `ScienceClaw/backend/pipeline/` + related contracts, datasources, adapters

## OVERVIEW
LangGraph StateGraph engine for structured RISC-V contribution workflows. 10-node DAG: explore → plan → develop → review → test, with human approval gates between each stage and escalation on review convergence. State persists to PostgreSQL checkpointer.

## STRUCTURE
```
backend/pipeline/
├── graph.py              # StateGraph builder + compiler
├── state.py              # PipelineState Pydantic model
├── routes.py             # Conditional edge routing (human + review)
├── event_publisher.py    # Redis Pub/Sub + Stream for SSE bridge
├── artifact_manager.py   # Filesystem artifact persistence
├── cost_guard.py         # Cost circuit breaker ($10/case)
└── nodes/
    ├── explore.py        # Discovery: contribution opportunities
    ├── plan.py           # Planning: execution plan generation
    ├── develop.py        # Development: patch/code production
    ├── review.py         # Review: deterministic + LLM checks
    ├── test.py           # Testing: QEMU sandbox execution
    ├── human_gate.py     # Human-in-the-loop: interrupt() pause
    └── escalate.py       # Escalation: terminal node on convergence
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Add pipeline stage | `graph.py` + `nodes/*.py` | Register node + edges + conditional routes |
| Modify state schema | `state.py` | Add fields with `Config.extra = "allow"` |
| Change review logic | `routes.py` + `nodes/review.py` | Convergence detection, score weighting |
| Change human gate | `nodes/human_gate.py` | Uses `langgraph.types.interrupt()` |
| Add event type | `event_publisher.py` | Publish to Redis Pub/Sub + Stream |
| Change artifact storage | `artifact_manager.py` | Base path: `/data/artifacts` |
| Change cost limits | `cost_guard.py` | Claude Sonnet 4 pricing model |
| Add data source | `backend/datasources/*.py` | Patchwork, mailing list, ISA registry |
| Add data contract | `backend/contracts/*.py` | Pydantic models per stage |
| Add LLM adapter | `backend/adapters/*.py` | Claude (subprocess) vs OpenAI (in-process) |

## CODE MAP

| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `build_pipeline_graph` | function | `graph.py:35` | Constructs 10-node StateGraph |
| `compile_graph` | async function | `graph.py:97` | Injects AsyncPostgresSaver checkpointer |
| `route_human_decision` | function | `routes.py` | Reads `approval_history[-1]` → approve/reject/abandon |
| `route_review_decision` | function | `routes.py` | Convergence: approve/reject/escalate |
| `PipelineState` | Pydantic | `state.py` | Shared state across all nodes |
| `EventPublisher` | class | `event_publisher.py` | Redis Pub/Sub + Stream (maxlen=500) |
| `ArtifactManager` | class | `artifact_manager.py` | `save_artifact`, `load_artifact`, `cleanup_case` |
| `CostCircuitBreaker` | class | `cost_guard.py` | $3/M input, $15/M output pricing |
| `explore_node` | async function | `nodes/explore.py` | Calls Patchwork + ISA registry |
| `plan_node` | async function | `nodes/plan.py` | Generates ExecutionPlan |
| `develop_node` | async function | `nodes/develop.py` | Produces FileChange patches |
| `review_node` | async function | `nodes/review.py` | Deterministic + LLM review |
| `human_gate_node` | async function | `nodes/human_gate.py` | `interrupt()` → Command(resume=...) |
| `escalate_node` | async function | `nodes/escalate.py` | Terminal: status=escalated |

## CONVENTIONS
- **Node signature**: `async def xxx_node(state: PipelineState) -> dict[str, Any]`
- **State updates**: Return partial dict; LangGraph merges into state
- **Artifact refs**: Store relative path string in state (e.g., `exploration_result_ref`)
- **Events**: Nodes do NOT call EventPublisher directly (router layer handles SSE)
- **Cost tracking**: Each node updates `total_input_tokens`, `total_output_tokens`, `estimated_cost_usd`

## ANTI-PATTERNS (THIS PROJECT)
- **Do not call `EventPublisher` from nodes** — event publishing is handled by the router layer
- **Do not use `ArtifactManager` in nodes yet** — nodes currently write to local `artifacts/` directly; this gap is pending closure
- **Do not modify state in-place** — always return a new dict for LangGraph merge
- **Pipeline graph compilation is lazy** — `compile_graph()` is called on first `POST /cases/:id/start`, not at startup
- **Do not hardcode pricing** — use `CostCircuitBreaker` config; current rates are Claude Sonnet 4 specific

## UNIQUE STYLES
- **Single reusable `human_gate_node`** registered 4 times under different names (`human_gate_explore`, `human_gate_plan`, `human_gate_code`, `human_gate_test`) — one function, multiple graph node identities
- **LangGraph `interrupt()`** for human gates — not a custom polling loop. State auto-persists to PostgreSQL checkpointer. Resume via `graph.ainvoke(Command(resume=...))`
- **Review convergence detection**: Escalate if `review_iterations >= max` OR score plateau with >50% finding overlap
- **Deterministic + LLM hybrid review**: `checkpatch.pl`/`sparse` findings are merged with LLM verdict; deterministic critical/major findings force `approved=False`
- **Dual adapter model**: Claude Agent SDK (subprocess, SIGTERM cancel) for explore/develop; OpenAI Agents SDK (in-process) for plan/review

## NOTES
- **Nodes are currently placeholders** — they return stub artifacts without real LLM calls. Adapters exist but aren't wired into nodes.
- **`POST /cases/:id/start` does NOT invoke the compiled graph** — it only sets MongoDB state and publishes a Redis event. Graph execution integration is pending.
- **`event_mapper.py` and `github_client.py` are TODO stubs**.
- **Artifact path**: `{base_dir}/{case_id}/{stage}/round_{n}/`
- **Redis keys**: `case:{case_id}:events` (Pub/Sub), `case:{case_id}:stream` (Stream, maxlen=500)
- **Review iterations default**: 3 (configurable via `MAX_REVIEW_ITERATIONS`)
