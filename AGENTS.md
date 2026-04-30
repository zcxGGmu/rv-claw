# RV-Claw Knowledge Base

**Generated:** 2026-04-30  
**Commit:** 4065ab0  
**Branch:** refactor/kimi

## OVERVIEW
RV-Claw is a dual-mode AI assistant: **Chat** (ScienceClaw ReAct agent with SSE streaming) + **Pipeline** (LangGraph StateGraph for structured RISC-V contribution workflows). Stack: FastAPI + Vue 3 + Vite + MongoDB + PostgreSQL (checkpointer) + Redis.

## STRUCTURE
```
.
├── ScienceClaw/
│   ├── backend/           # FastAPI monolith + microservices
│   │   ├── main.py        # App factory, lifespan, 11 route mounts
│   │   ├── deepagent/     # ReAct Chat agent runtime (SSE streaming)
│   │   ├── pipeline/      # LangGraph StateGraph (explore→plan→develop→review→test)
│   │   ├── route/         # FastAPI routers (auth, sessions, chat, cases, ...)
│   │   ├── builtin_skills/# Office/PDF tool scripts
│   │   ├── im/            # Lark/WeChat IM integration
│   │   ├── contracts/     # Pydantic data models for Pipeline stages
│   │   ├── datasources/   # Patchwork, mailing list, ISA registry clients
│   │   ├── adapters/      # Claude/OpenAI agent SDK wrappers
│   │   ├── db/            # MongoDB collections + PostgreSQL checkpointer
│   │   ├── user/          # Auth dependencies + admin bootstrap
│   │   └── tests/         # pytest unit tests (flat, no conftest.py)
│   ├── frontend/          # Vue 3 + TypeScript + Vite
│   │   ├── src/main.ts    # Inline router definition (no router/index.ts)
│   │   ├── src/composables/ # Module-level ref singletons (no Pinia)
│   │   ├── src/api/client.ts # Axios + SSE (fetchEventSource) with token refresh
│   │   ├── src/views/     # CaseListView, CaseDetailView, StatisticsPage
│   │   └── src/components/pipeline/ # PipelineView, StageNode, HumanGate
│   ├── task-service/      # Celery scheduler microservice
│   ├── websearch/         # SearXNG + Crawl4AI search microservice
│   └── sandbox/           # Code execution sandbox (all-in-one-sandbox base)
├── docker-compose.yml     # 10 services dev orchestration
├── tasks/                 # Design docs, progress tracking, conventions
├── tests/                 # E2E/component tests (vitest), baseline templates
└── docs/                  # Deployment, operations, user guides
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Add API endpoint | `backend/route/*.py` | Mount in `main.py` |
| Modify Chat agent | `backend/deepagent/runner.py` | `arun_science_task_stream()` is the entry |
| Modify Pipeline graph | `backend/pipeline/graph.py` | 10-node StateGraph; nodes in `pipeline/nodes/` |
| Add Pipeline stage | `backend/pipeline/nodes/*.py` + `graph.py` | Register node + edges + conditional routes |
| Change auth logic | `backend/user/dependencies.py` | Session-cookie based, not JWT |
| Add frontend page | `frontend/src/views/*.vue` | Register route inline in `main.ts` |
| Add frontend component | `frontend/src/components/**/*.vue` | No Storybook yet |
| Add API client method | `frontend/src/api/*.ts` | Export from `client.ts` or new file |
| Modify state management | `frontend/src/composables/use*.ts` | Module-level ref singleton pattern |
| Change DB schema | `mongo-init.js` or `backend/db/collections.py` | MongoDB validators + indexes |
| Change env var | `.env.example` + `backend/config.py` | `Settings` class uses `os.environ` |
| Add CI step | `.github/workflows/ci.yml` | All steps currently `\|\| true` (report-only) |
| Build release | `./release.sh` | Multi-arch buildx, pushes to Huawei SWR |

## CODE MAP

| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `create_app` | function | `backend/main.py:67` | FastAPI factory, mounts all routers |
| `lifespan` | function | `backend/main.py:32` | Boots MongoDB, models, admin, IM runtime |
| `arun_science_task_stream` | function | `backend/deepagent/runner.py` | Chat SSE streaming entry point |
| `build_pipeline_graph` | function | `backend/pipeline/graph.py:35` | Constructs LangGraph StateGraph |
| `compile_graph` | function | `backend/pipeline/graph.py:97` | Injects AsyncPostgresSaver checkpointer |
| `explore_node` | function | `backend/pipeline/nodes/explore.py` | Pipeline: exploration stage |
| `develop_node` | function | `backend/pipeline/nodes/develop.py` | Pipeline: development stage |
| `review_node` | function | `backend/pipeline/nodes/review.py` | Pipeline: deterministic + LLM review |
| `human_gate_node` | function | `backend/pipeline/nodes/human_gate.py` | Pipeline: `interrupt()` pause/resume |
| `route_review_decision` | function | `backend/pipeline/routes.py` | Review→approve/reject/escalate routing |
| `get_current_user` | function | `backend/user/dependencies.py:12` | Session cookie auth dependency |
| `require_user` | function | `backend/user/dependencies.py:53` | Enforces authentication |
| `apiClient` | const | `frontend/src/api/client.ts:37` | Axios instance with interceptors |
| `createSSEConnection` | function | `frontend/src/api/client.ts:284` | Generic SSE wrapper with token refresh |
| `useAuth` | composable | `frontend/src/composables/useAuth.ts:29` | Global auth state (module ref singleton) |
| `useCaseStore` | composable | `frontend/src/composables/useCaseStore.ts` | Case + Pipeline state (module ref singleton) |
| `useCaseEvents` | composable | `frontend/src/composables/useCaseEvents.ts` | SSE event stream management |

## CONVENTIONS
- **Backend**: `snake_case` files/functions, `PascalCase` classes, `UPPER_CASE` env vars. Routes use `ApiResponse` wrapper `{code, msg, data}`.
- **Frontend**: `PascalCase` components, `camelCase` functions/composables, `kebab-case` file names. Composables named `useXxx.ts`.
- **Auth**: Session cookie (not JWT). `Authorization: Bearer <session_id>` header also accepted. `auth_provider=none` disables auth entirely.
- **Routes**: All backend routers mounted at `/api/v1/*`. Frontend proxy in `vite.config.ts` forwards `/api` to backend.
- **State**: No Pinia/Vuex — frontend uses module-level `ref` singletons imported by composables.
- **Tests**: Backend pytest flat in `backend/tests/`. Frontend vitest in `tests/e2e/` (mislabelled; these are component tests).
- **Docker**: Every service has `Dockerfile` + `Dockerfile.china` (Huawei mirror variant).

## ANTI-PATTERNS (THIS PROJECT)
- **No `router/index.ts`** — all Vue routes are inline in `main.ts`. Do not create a separate router file unless refactoring.
- **No Pinia** — state is module-level ref singletons. Do not introduce Pinia without team discussion.
- **CI `|| true`** — all CI steps soft-fail. Do not rely on CI to block merges yet.
- **No `tests/unit/` or `tests/integration/`** — CI references these but they don't exist.
- **Pipeline graph compilation is lazy** — not at startup; called on first `POST /cases/:id/start`.
- **Do not use `os.getenv` directly** — always go through `backend/config.py::Settings`.
- **Do not hardcode API keys** — use `Settings` class; secrets masked in production.

## UNIQUE STYLES
- **Dual-mode frontend**: Chat (`/chat/*`) and Pipeline (`/cases/*`) share `MainLayout.vue` but isolate state via separate composables.
- **Inline SSE in axios client**: `createSSEConnection` lives in `client.ts` alongside REST axios instance, sharing token refresh logic.
- **Pipeline human gates use `langgraph.types.interrupt()`** — not a custom polling loop. State persists to PostgreSQL checkpointer automatically.
- **Feature flags control visibility**: `PIPELINE_ENABLED=false` hides Cases nav and returns 404 on `/cases` endpoints.
- **RBAC via `role` field on `User` model** — `admin`/`user`. `require_role` decorator on admin-only routes (e.g., `DELETE /cases/:id`).

## COMMANDS
```bash
# Dev — full stack
docker compose up -d

# Dev — backend only (with hot reload)
cd ScienceClaw/backend && uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Dev — frontend only
cd ScienceClaw/frontend && npm run dev

# Backend tests
cd ScienceClaw/backend && pytest tests/ -v

# Frontend build
cd ScienceClaw/frontend && npm run build

# Release (multi-arch, pushes to registry)
./release.sh

# Lint
ruff check ScienceClaw/backend/
mypy ScienceClaw/backend/ || true
cd ScienceClaw/frontend && npm run lint || true
```

## NOTES
- **MongoDB** runs on port `27014` (not default 27017) to avoid conflicts.
- **PostgreSQL** is used ONLY for LangGraph checkpointer (`rv_checkpoints` DB), not for application data.
- **Redis** is shared by Celery broker and Pipeline event Pub/Sub.
- **Task service** calls backend via HTTP (`/api/v1/chat`), so it can be scaled independently.
- **Frontend proxy** forwards `/api` → `localhost:12001` and `/task-service` → `localhost:12002`.
- **`requirements-pipeline.txt`** at repo root is NOT installed by backend Dockerfile — install manually if needed.
- **Baseline templates** in `tests/baseline/` are unfilled placeholders; run actual commands and paste output.
