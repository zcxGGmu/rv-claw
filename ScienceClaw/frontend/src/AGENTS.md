# Frontend Knowledge Base

**Generated:** 2026-04-30  
**Scope:** `ScienceClaw/frontend/src/`

## OVERVIEW
Vue 3 + TypeScript + Vite frontend. Dual-mode: Chat (`/chat/*`) and Pipeline (`/cases/*`). Chat mode uses Tailwind CSS + reka-ui primitives; Pipeline mode uses Element Plus (inconsistency noted). No Pinia — state is module-level `ref` singletons.

## STRUCTURE
```
src/
├── main.ts              # App bootstrap + inline router (no router/index.ts)
├── App.vue              # Root: router-view + Toast + theme init
├── pages/               # Chat mode route components (eager import)
│   ├── MainLayout.vue   # Shell: LeftPanel + router-view + FilePanel
│   ├── ChatPage.vue     # Core chat (~1300 lines, god component)
│   ├── HomePage.vue     # Landing with quick prompts
│   └── ...
├── views/               # Pipeline mode route components (lazy import)
│   ├── CaseListView.vue     # Uses Element Plus (el-table, el-select)
│   ├── CaseDetailView.vue   # Three-column layout
│   └── StatisticsPage.vue   # Placeholder
├── components/
│   ├── ui/              # Primitives: Toast, CustomDialog, MonacoEditor, reka-ui
│   ├── icons/           # SVG icon components
│   ├── toolViews/       # Tool renderers (Shell, File, Browser, Search, MCP)
│   ├── filePreviews/    # File type renderers
│   ├── pipeline/        # PipelineView, StageNode, HumanGate
│   ├── review/          # ReviewPanel, DiffViewer, ReviewHistory
│   ├── exploration/     # EvidenceChain, ContributionCard
│   ├── planning/        # ExecutionPlanTree
│   ├── testing/         # TestResultSummary
│   └── shared/          # AgentEventLog (shared between modes)
├── composables/         # Module-level ref singletons (no Pinia)
│   ├── useAuth.ts       # Global auth state
│   ├── useCaseStore.ts  # Case CRUD state
│   ├── useCaseEvents.ts # SSE subscription with reconnect
│   ├── useDialog.ts     # Global confirm dialog
│   ├── usePendingChat.ts # One-shot bridge: HomePage -> ChatPage
│   └── ...
├── api/
│   ├── client.ts        # Axios + SSE (fetchEventSource) with token refresh
│   ├── index.ts         # Barrel export + auto-init auth
│   ├── cases.ts         # Pipeline case CRUD (BUG: imports `client` not `apiClient`)
│   ├── agent.ts         # Session CRUD + chat SSE
│   └── ...
├── types/               # TypeScript domain types
│   ├── message.ts       # Chat message types
│   ├── case.ts          # Pipeline case types
│   ├── pipeline.ts      # Pipeline stage types
│   └── ...
└── locales/             # i18n translations (zh.ts, en.ts)
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Add page | `views/*.vue` or `pages/*.vue` | Register route inline in `main.ts` |
| Add component | `components/**/*.vue` | Pipeline-specific under `pipeline/`, `review/`, etc. |
| Add API method | `api/*.ts` | Import `apiClient` from `client.ts` (NOT `client`) |
| Add state | `composables/useXxx.ts` | Module-level `ref` for global; inside function for instance |
| Add route | `main.ts` | No separate router file |
| Change auth | `composables/useAuth.ts` + `api/client.ts` interceptors | Token refresh with queue dedup |
| Change SSE | `api/client.ts` `createSSEConnection` | fetchEventSource, auth headers, 401 retry |
| Change toast | `components/ui/Toast.vue` + `utils/toast.ts` | window.CustomEvent dispatch/listen |
| Change dialog | `composables/useDialog.ts` + `components/ui/CustomDialog.vue` | Module-level state |
| Change file preview | `components/filePreviews/*.vue` + `useFilePanel` | Routes by file extension |

## CODE MAP

| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `router` | const | `main.ts:36` | Inline router, no separate file |
| `apiClient` | const | `api/client.ts:37` | Axios instance with interceptors |
| `createSSEConnection` | function | `api/client.ts:284` | Generic SSE wrapper with token refresh |
| `useAuth` | composable | `composables/useAuth.ts` | Global auth state (module ref singleton) |
| `useCaseStore` | composable | `composables/useCaseStore.ts` | Case + Pipeline state |
| `useCaseEvents` | composable | `composables/useCaseEvents.ts` | SSE event stream with reconnect |
| `useDialog` | composable | `composables/useDialog.ts` | Global confirm dialog state |
| `ChatPage` | component | `pages/ChatPage.vue` | Core chat (~1300 lines, god component) |
| `MainLayout` | component | `pages/MainLayout.vue` | Shell layout |
| `PipelineView` | component | `components/pipeline/PipelineView.vue` | Stage visualization |
| `HumanGate` | component | `components/pipeline/HumanGate.vue` | Human review UI |
| `StageNode` | component | `components/pipeline/StageNode.vue` | Single stage display |
| `CaseListView` | component | `views/CaseListView.vue` | Case list (Element Plus) |
| `CaseDetailView` | component | `views/CaseDetailView.vue` | Case detail |

## CONVENTIONS
- **Components**: `PascalCase.vue`, `kebab-case` file names
- **Composables**: `useXxx.ts`, camelCase functions
- **State**: Module-level `ref` singletons for global state (shared across all callers); instance-level refs inside composable functions for per-component state
- **API**: Each domain has its own `api/*.ts` file; barrel export in `api/index.ts`
- **Auth**: Token refresh with queue-based deduplication (`isRefreshing` + `failedQueue`)
- **SSE**: `@microsoft/fetch-event-source` for POST-capable SSE with auth headers
- **Events**: `window.dispatchEvent(CustomEvent)` for toast/auth; `mitt` event bus for file panel
- **i18n**: `$t(key)` pattern; tests mock with `{ global: { mocks: { $t: (k) => k } } }`
- **Lazy loading**: Only `views/` components use dynamic `import()`

## ANTI-PATTERNS (THIS PROJECT)
- **No `router/index.ts`** — all routes inline in `main.ts`. Do not create a separate router file unless refactoring.
- **No Pinia/Vuex** — state is module-level ref singletons. Do not introduce Pinia without team discussion.
- **Do NOT import `{ client }` from `api/client.ts`** — the export is `apiClient`. `cases.ts`, `reviews.ts`, and `artifacts.ts` have this bug.
- **`useReviewStore` imports `@/contracts/review`** — this path does not exist; should be `@/types/review`.
- **`CaseListView` uses Element Plus** — but Element Plus is not in `package.json`. Pipeline UI library choice is inconsistent with Chat mode.
- **`ChatPage.vue` is a god component** (~1300 lines) — handles SSE, messages, tools, plans, activity, sharing, scroll. Consider extracting `useChatSession` composable.
- **`MainLayout` remounts on session change** — `:key="$route.params.sessionId"` on `<router-view>`. Intentional for SSE cleanup but costly.

## UNIQUE STYLES
- **Dual-mode UI libraries**: Chat mode = Tailwind + reka-ui; Pipeline mode = Element Plus. Two design systems coexist.
- **Module-level ref singletons**: Global state without Pinia. E.g., `useAuth` declares `currentUser = ref<User | null>()` at module scope, shared by all callers.
- **`usePendingChat` bridge**: Plain `let _pending` (not reactive) as one-shot data bridge from HomePage → ChatPage during navigation.
- **Inline SSE in axios client**: `createSSEConnection` lives in `client.ts` alongside REST axios instance, sharing token refresh logic.
- **`api/index.ts` auto-init**: Barrel file calls `initializeAuth()` on import side-effect.
- **Toast via CustomEvent**: `window.dispatchEvent(new CustomEvent('toast', { detail }))` → `Toast.vue` listens globally.

## NOTES
- **Element Plus not in package.json** — `CaseListView.vue` uses `el-table`, `el-dialog`, `el-select`. If this is active code, it will fail at runtime.
- **Pipeline API import bug**: `cases.ts`, `reviews.ts`, `artifacts.ts` import `{ client }` but `client.ts` exports `apiClient`. These files are likely broken or dead code.
- **No test runner configured** — no vitest config, no `test:unit` script in package.json.
- **Vite proxy**: `/api` → backend:8000, `/task-service` → task-service:8001
- **Path alias**: `@/` → `src/`
- **Dark mode**: CSS class-based (`darkMode: 'class'` in tailwind.config.js)
