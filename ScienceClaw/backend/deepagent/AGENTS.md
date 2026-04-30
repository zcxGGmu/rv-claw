# DeepAgent Module Knowledge Base

**Generated:** 2026-04-30  
**Scope:** `ScienceClaw/backend/deepagent/`

## OVERVIEW
ReAct Chat Agent runtime with SSE streaming. Shared entry point `arun_science_task_stream()` used by web chat (`sessions.py` SSE), task-service (`chat.py`), and IM orchestrator (`im/orchestrator.py`). Supports tool middleware, skill routing, memory management, and sandbox backend.

## STRUCTURE
```
deepagent/
├── runner.py              # SSE streaming entry: arun_science_task_stream()
├── agent.py               # Agent factory: deep_agent(), deep_agent_eval()
├── engine.py              # LLM model factory + context window resolution
├── sessions.py            # ScienceSession dataclass + in-memory LRU cache (200)
├── tools.py               # Built-in tools: web_search, web_crawl, eval_skill, grade_eval
├── tooluniverse_tools.py  # ToolUniverse integration tools
├── sse_middleware.py      # Tool call interceptor for SSE events
├── offload_middleware.py  # Large tool result auto-offload to workspace files
├── sse_protocol.py        # Tool registry + SSE event protocol manager (singleton)
├── full_sandbox_backend.py # Remote sandbox REST API backend
├── filtered_backend.py    # Skills filtering layer over FilesystemBackend
├── diagnostic.py          # DIAGNOSTIC_MODE=1 LLM call logger
└── plan_types.py          # PlanStep TypedDict + normalize_plan_steps()
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Modify agent behavior | `agent.py` | System prompt, tool/skill composition, memory injection |
| Modify SSE streaming | `runner.py` | Event mapping, token budget, history truncation |
| Add tool | `tools.py` or `tooluniverse_tools.py` | Register in `sse_protocol.py` for SSE metadata |
| Add middleware | `sse_middleware.py` or `offload_middleware.py` | Wrap tool_call/awrap_tool_call |
| Change LLM model | `engine.py` | get_llm_model() factory; monkey-patches langchain-openai |
| Change session cache | `sessions.py` | LRU 200 max; workspace at `/home/scienceclaw/{session_id}` |
| Add skill routing | `filtered_backend.py` | Blocks skills by top-level directory name |
| Sandbox operations | `full_sandbox_backend.py` | Circuit breaker on malformed responses |
| Debug LLM calls | `diagnostic.py` | Set DIAGNOSTIC_MODE=1; logs to workspace/_diagnostic/ |
| Tool metadata | `sse_protocol.py` | Icons, categories, descriptions for frontend |

## CODE MAP

| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `arun_science_task_stream` | async func | `runner.py` | Shared streaming entry; SSE over agent.astream() |
| `deep_agent` | async func | `agent.py:315` | Builds LangGraph agent with tools, skills, middleware |
| `deep_agent_eval` | async func | `agent.py:502` | Lightweight eval agent (no propose_save, no external tools) |
| `get_llm_model` | async func | `engine.py:385` | Model factory; context window auto-detection |
| `ScienceSession` | dataclass | `sessions.py` | Session state + workspace path |
| `SSEMonitoringMiddleware` | class | `sse_middleware.py` | Intercepts tool calls → SSE events |
| `ToolResultOffloadMiddleware` | class | `offload_middleware.py` | Offloads >3KB results → files |
| `FullSandboxBackend` | class | `full_sandbox_backend.py` | Remote sandbox REST API client |
| `FilteredFilesystemBackend` | class | `filtered_backend.py` | Skills filtering wrapper |
| `SSEProtocolManager` | singleton | `sse_protocol.py` | Tool registry + metadata |

## CONVENTIONS
- **Agent signature**: `deep_agent(session_id, query, backend, model_config, skills, system_prompt?)`
- **Session workspace**: `/home/scienceclaw/{session_id}`
- **SSE event envelope**: `{event_id, timestamp, session_id, event_type, ...}`
- **Tool result offload**: Results >3KB auto-saved to `research_data/` with summary + `read_file` hint
- **Session cache**: Module-level `_sessions: Dict[str, ScienceSession]` with async lock, LRU eviction at 200
- **Monkey-patching**: `engine.py` patches `langchain_openai.chat_models.base` at import time for reasoning_content

## ANTI-PATTERNS (THIS PROJECT)
- **Do not rely on `GENERAL_PURPOSE_SUBAGENT` global** — `agent.py` mutates this global dict on every call (injecting policy text) then resets to DEFAULT. Concurrent calls can race.
- **Do not trust session cache for durability** — in-memory LRU, not persistent. Use MongoDB for long-lived sessions.
- **Do not use sync tool wrappers in async context** — `_run_async()` uses ThreadPoolExecutor fallback; prefer async tool definitions.
- **Do not bypass `SSEProtocolManager`** — tool metadata (icons, categories) must be registered for frontend rendering.
- **Engine monkey-patching affects entire process** — `_convert_dict_to_message` patches are process-wide, not scoped.

## UNIQUE STYLES
- **Single shared streaming entry**: `arun_science_task_stream()` serves web SSE, task-service JSON, and IM messages simultaneously. Formatting differs per consumer.
- **Tool middleware chain**: SSEMonitoring + ToolResultOffload wrap tool calls transparently. Agent sees original results; SSE gets enriched events; large results get offloaded.
- **Composite backend routing**: `/builtin-skills/` → FilesystemBackend, `/skills/` → FilteredFilesystemBackend. Agent uses `read_file` to load SKILL.md as instructions.
- **Diagnostic mode**: `DIAGNOSTIC_MODE=1` logs every LLM input to workspace `_diagnostic/` for replay/debugging.
- **Context window table**: `engine.py` maintains a hardcoded `_KNOWN_CONTEXT_WINDOWS` table for 100+ models. Auto-detect falls back to this table.
- **Filtered backend blocks by directory name**: Skills are blocked at the top-level directory level, not file-level.

## NOTES
- **Runner is 891 lines** — largest file in deepagent. Complex token extraction (4 API formats), 3-pass history trimming, middleware event polling.
- **Sessions.py cache is module-level** — shared across all requests. TTL-based eviction, not request-scoped.
- **Sandbox backend uses circuit breaker** — on malformed sandbox responses to prevent cascade failures.
- **Skill-creator is a mini-app** — `builtin_skills/skill-creator/` contains `agents/`, `eval-viewer/`, `references/`, `scripts/`. Far more complex than other skills.
- **ToolUniverse integration**: `tooluniverse_tools.py` bridges to ToolUniverse catalog. Lazy-loaded singleton.
- **Memory endpoint**: `route/memory.py` reads/writes user's AGENTS.md for persistent agent memory.
