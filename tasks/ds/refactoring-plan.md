# RV-Insights 重构计划：对标 ScienceClaw + design.md 完整实现

> **版本**: v1.0  
> **日期**: 2026-04-29  
> **状态**: 规划阶段  
> **作者**: RV-Insights Team  

---

## 目录

- [0. 核心目标](#0-核心目标)
- [1. 现状分析](#1-现状分析)
- [2. ScienceClaw 前端功能清单](#2-scienceclaw-前端功能清单)
- [3. 前端迁移与改造方案](#3-前端迁移与改造方案)
- [4. 后端架构重构方案](#4-后端架构重构方案)
- [5. API 接口全景图](#5-api-接口全景图)
- [6. 数据库设计](#6-数据库设计)
- [7. Agent Pipeline 实现方案](#7-agent-pipeline-实现方案)
- [8. Chat 模式实现方案](#8-chat-模式实现方案)
- [9. Docker Compose 重构](#9-docker-compose-重构)
- [10. 实施计划（分 Sprint）](#10-实施计划分-sprint)
- [11. 风险评估与缓解](#11-风险评估与缓解)
- [12. 跨领域关注点](#12-跨领域关注点)
- [附录 A. 文件级变更清单](#附录-a-文件级变更清单)
- [附录 B. 与 ScienceClaw 的差异对照表](#附录-b-与-scienceclaw-的差异对照表)
- [附录 C. 探索验证后修正（2026-04-29）](#附录-c-探索验证后修正2026-04-29)
- [附录 D. 核心 Vue 组件详细规格](#附录-d-核心-vue-组件详细规格)
- [附录 E. 关键后端模块实现细节](#附录-e-关键后端模块实现细节)
- [附录 F. 完整 API 请求/响应 Schema](#附录-f-完整-api-请求响应-schema)
- [附录 G. 完整 MongoDB 文档 Schema](#附录-g-完整-mongodb-文档-schema)
- [附录 H. Sprint 任务验收标准](#附录-h-sprint-任务验收标准)
- [附录 I. 错误处理与重试策略](#附录-i-错误处理与重试策略)
- [附录 J. Nginx 反向代理详细配置](#附录-j-nginx-反向代理详细配置)
- [附录 K. 测试策略详细方案](#附录-k-测试策略详细方案)
- [附录 L. 配置管理体系](#附录-l-配置管理体系)
- [附录 M. 部署与回滚策略](#附录-m-部署与回滚策略)
- [附录 N. 数据迁移策略（ScienceClaw → RV-Insights）](#附录-n-数据迁移策略scienceclaw--rv-insights)
- [附录 O. 监控与可观测性](#附录-o-监控与可观测性)
- [附录 P. Chat 模式完整实现方案](#附录-p-chat-模式完整实现方案)

---

## 0. 核心目标

### 0.1 总体原则

**"前端直接迁移 ScienceClaw，后端按 design.md 全部重构"**

| 层级 | 策略 | 说明 |
|------|------|------|
| **前端** | 直接迁移 + 扩展 | ScienceClaw 全部功能保留，新增 RV-Insights 专属页面（案例管理、Pipeline 可视化、审核面板） |
| **后端** | 完全重写 | 保留 ScienceClaw 的 API 契约（auth、sessions、files、models、statistics、task-settings），内部实现全部替换为 design.md 架构 |
| **基础设施** | 保留 + 新增 | 保留 sandbox/searxng/websearch，新增 PostgreSQL，修改 MongoDB schema |

### 0.2 不可变更项

- **前端**：必须暴露 ScienceClaw 的全部功能（Chat、Session、Files、Tools/Skills、Task Scheduling、Statistics、Auth、Sharing）
- **后端**：必须实现 design.md 定义的 5 阶段 Agent Pipeline（LangGraph + Redis Pub/Sub + Human-in-the-Loop）
- **双模式**：Chat 模式（通用对话）与 Pipeline 模式（RISC-V 贡献流水线）必须并存

---

## 1. 现状分析

### 1.1 当前 rv-claw 代码状态

rv-claw 当前是 ScienceClaw 的**完整克隆**，目录结构完全一致：

```
rv-claw/
├── ScienceClaw/          # ScienceClaw 完整代码
│   ├── backend/          # FastAPI + DeepAgents + MongoDB
│   ├── frontend/         # Vue 3 + TailwindCSS
│   ├── sandbox/          # Docker 隔离执行环境
│   ├── task-service/     # 定时任务调度 (Celery)
│   └── websearch/        # SearXNG + Crawl4AI 搜索服务
├── Skills/               # 自定义技能包
├── Tools/                # 自定义工具
├── tasks/                # 项目任务文档
│   └── design.md         # RV-Insights 设计方案
└── docker-compose.yml    # 9 服务编排
```

### 1.2 ScienceClaw 后端当前架构

| 组件 | 技术栈 | 用途 |
|------|--------|------|
| 后端框架 | FastAPI + Uvicorn | REST API + SSE |
| Agent 引擎 | LangChain DeepAgents | 通用 Agent 对话 |
| 沙箱 | AIO Sandbox (Docker) | 隔离代码执行 |
| 数据库 | MongoDB | 会话、用户、配置、消息 |
| 缓存队列 | Redis | Celery 任务队列、会话锁定 |
| 搜索 | SearXNG + Crawl4AI | 网页搜索 |
| IM | Lark/Feishu Webhook | 即时通知 |
| 任务调度 | Celery + Celery Beat | 定时任务执行 |
| 文件存储 | 本地文件系统 (workspace/) | 会话产物 |

### 1.3 需要保留的 ScienceClaw 组件

| 组件 | 处理方式 | 理由 |
|------|----------|------|
| **frontend/** | 直接迁移 | 用户要求"可直接迁移"，功能完整 |
| **sandbox/** | 保留 | 隔离代码执行，Pipeline Developer/Tester 需要 |
| **websearch/** | 保留 | Explorer Agent 需要网页搜索 |
| **Skills/** | 保留 | 通用技能包体系 |
| **Tools/** | 保留 | 通用工具生态 |
| **task-service/** | 保留（改造） | 定时任务调度，需对接新后端 API |

### 1.4 需要完全重写的组件

| 组件 | 原因 |
|------|------|
| **backend/** | 全部替换为 design.md 架构：LangGraph Pipeline + ChatRunner + Redis Pub/Sub + PostgreSQL |
| **docker-compose.yml** | 新增 PostgreSQL、分离 Chat/Pipeline 后端、调整服务依赖 |

---

## 2. ScienceClaw 前端功能清单

### 2.1 页面一览

| 页面 | 文件 | 路由 | 功能 |
|------|------|------|------|
| 首页（Chat 欢迎页） | `HomePage.vue` | `/` | 输入框 + 建议问题 + 会话入口 |
| Chat 对话页 | `ChatPage.vue` | `/chat/:id` | 核心聊天页（消息流、工具调用、文件预览） |
| 登录页 | `LoginPage.vue` | `/login` | 用户名/密码登录 |
| 主布局 | `MainLayout.vue` | — | 左侧栏 + 顶部栏 + 主内容区 |
| 分享页 | `SharePage.vue` + `ShareLayout.vue` | `/share/:id` | 只读分享（无需登录） |
| 工具页 | `ToolsPage.vue` | `/tools` | 工具列表、搜索、分类 |
| 工具详情 | `ToolDetailPage.vue` | `/tools/:id` | 工具规格、使用说明 |
| 技能页 | `SkillsPage.vue` | `/skills` | 技能包列表 |
| 技能详情 | `SkillDetailPage.vue` | `/skills/:id` | 技能包详情 |
| 任务列表 | `TasksListPage.vue` | `/tasks` | 定时任务列表 |
| 任务详情/执行 | `TasksPage.vue` | `/tasks/:id` | 任务执行结果 |
| 任务配置 | `TaskConfigPage.vue` | `/tasks/config` | 新建/编辑定时任务 |
| 科研工具 | `ScienceToolDetail.vue` | `/science-tools` | ToolUniverse 科研工具 |
| 统计页 | (需确认) | `/statistics` | Token 使用统计 |

### 2.2 核心组件

| 组件 | 功能 | 是否需要改造 |
|------|------|------------|
| `ChatBox.vue` | 消息输入框 + 文件上传 + 深度研究模式 | ✅ 保留 |
| `ChatMessage.vue` | 消息渲染（Markdown + 工具调用 + 产物） | ✅ 保留 |
| `ActivityPanel.vue` | Agent 实时事件日志（Thinking/Tool Call/Plan） | ✅ 保留，RV 页面复用 |
| `ProcessMessage.vue` | Agent 处理中消息（加载动画） | ✅ 保留 |
| `StepMessage.vue` | Agent 步骤消息（进度展示） | ✅ 保留 |
| `LeftPanel.vue` | 左侧会话列表 + 文件面板 | ✅ 保留 |
| `FilePanel.vue` | 文件管理面板 | ✅ 保留 |
| `FilePreviewModal.vue` | 文件预览（PDF/图片/代码） | ✅ 保留 |
| `PlanPanel.vue` | Agent 执行计划面板 | ✅ 保留 |
| `SessionItem.vue` | 会话列表项 | ✅ 保留 |
| `UserMenu.vue` | 用户菜单（设置、主题、语言） | ✅ 保留 |
| `ToolPanel.vue` | 工具面板 | ✅ 保留 |
| `ToolUse.vue` | 工具调用可视化 | ✅ 保留 |
| `MarkdownEnhancements.vue` | Markdown 增强渲染 | ✅ 保留 |
| `SandboxPreview.vue` | 沙箱预览 | ✅ 保留 |

### 2.3 API 客户端层

| 文件 | 用途 |
|------|------|
| `api/client.ts` | HTTP 客户端 + SSE 封装（axios + fetch-event-source） |
| `api/auth.ts` | 登录/注册/状态/刷新 Token |
| `api/agent.ts` | Agent 对话 SSE 流 |
| `api/sessions.ts` | 会话 CRUD + 聊天 |
| `api/file.ts` | 文件上传/下载/列表 |
| `api/models.ts` | LLM 模型配置 |
| `api/taskSettings.ts` | 定时任务配置 |
| `api/tasks.ts` | 任务日志 |
| `api/tooluniverse.ts` | 科研工具 API |
| `api/im.ts` | IM 通知配置 |
| `api/memory.ts` | Agent 全局记忆 |
| `api/webhooks.ts` | Webhook 管理 |

### 2.4 状态管理（Composables）

| 文件 | 功能 |
|------|------|
| `useAuth.ts` | 认证状态、登录/登出 |
| `useTheme.ts` | 主题切换 |
| `useI18n.ts` | 国际化 |
| `useTool.ts` | 工具状态管理 |
| `useLeftPanel.ts` | 左侧面板状态 |
| `useFilePanel.ts` | 文件面板状态 |
| `useSessionGrouping.ts` | 会话分组 |
| `useSessionNotifications.ts` | 会话通知 |
| `useResizeObserver.ts` | 响应式尺寸 |
| `useMessageGrouper.ts` | 消息分组 |

---

## 3. 前端迁移与改造方案

### 3.1 迁移策略

**Step 1**: 将 ScienceClaw 的 `ScienceClaw/frontend/` 完整复制为 `web-console/`（改名对齐 design.md）。  
**Step 2**: 改造路由，新增 RV-Insights 专属页面。  
**Step 3**: 扩展 API 客户端层，新增 cases/pipeline API。  
**Step 4**: 新增 RV-Insights 专属组件（Pipeline 可视化、审核面板、Diff 查看器等）。  
**Step 5**: 适配新的后端 API 基地址和 SSE 端点。

### 3.2 路由设计（最终）

```typescript
// router/index.ts
const routes = [
  // === 认证（无需登录） ===
  { path: '/login', name: 'login', component: LoginPage },
  { path: '/share/:id', name: 'share', component: SharePage, meta: { layout: 'share' } },

  // === 主布局（需要登录） ===
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      // --- ScienceClaw 原有页面 (保留) ---
      { path: '', name: 'home', component: HomePage },                             // Chat 欢迎页
      { path: 'chat/:id', name: 'chat', component: ChatPage },                    // Chat 对话
      { path: 'tools', name: 'tools', component: ToolsPage },                      // 工具列表
      { path: 'tools/:id', name: 'tool-detail', component: ToolDetailPage },       // 工具详情
      { path: 'skills', name: 'skills', component: SkillsPage },                   // 技能列表
      { path: 'skills/:id', name: 'skill-detail', component: SkillDetailPage },    // 技能详情
      { path: 'tasks', name: 'tasks', component: TasksListPage },                  // 任务列表
      { path: 'tasks/:id', name: 'task-detail', component: TasksPage },            // 任务详情
      { path: 'tasks/config', name: 'task-config', component: TaskConfigPage },    // 任务配置
      { path: 'science-tools', name: 'science-tools', component: ScienceToolDetail }, // 科研工具
      { path: 'statistics', name: 'statistics', component: StatisticsPage },       // 统计页

      // --- RV-Insights 新增页面 ---
      { path: 'cases', name: 'cases', component: CaseListView },                   // 案例列表
      { path: 'cases/:id', name: 'case-detail', component: CaseDetailView },       // 案例详情 ★核心页面
    ],
  },
]
```

### 3.3 RV-Insights 新增前端组件

需要从零开发的组件（design.md 第 4.4 节定义）：

| 组件 | 文件路径 | 功能 | 复杂度 |
|------|----------|------|--------|
| `PipelineView.vue` | `components/pipeline/PipelineView.vue` | 5阶段流水线状态可视化 | ★★★★★ |
| `StageNode.vue` | `components/pipeline/StageNode.vue` | 单阶段节点（图标+状态+耗时+Token） | ★★★ |
| `HumanGate.vue` | `components/pipeline/HumanGate.vue` | 人工审核门禁按钮 | ★★★ |
| `IterationBadge.vue` | `components/pipeline/IterationBadge.vue` | 迭代轮次标记 | ★★ |
| `ReviewPanel.vue` | `components/review/ReviewPanel.vue` | 审核决策面板（Approve/Reject/Abandon） | ★★★★ |
| `ReviewFinding.vue` | `components/review/ReviewFinding.vue` | 审核发现项卡片 | ★★★ |
| `DiffViewer.vue` | `components/review/DiffViewer.vue` | Monaco-based Unified Diff 查看器 | ★★★★★ |
| `ContributionCard.vue` | `components/exploration/ContributionCard.vue` | 贡献机会卡片 | ★★★ |
| `EvidenceChain.vue` | `components/exploration/EvidenceChain.vue` | 证据链展示 | ★★★ |
| `TestResultSummary.vue` | `components/testing/TestResultSummary.vue` | 测试结果摘要 | ★★★ |
| `TestLogViewer.vue` | `components/testing/TestLogViewer.vue` | 测试日志查看器 | ★★ |
| `CaseListView.vue` | `views/CaseListView.vue` | 案例列表页（状态筛选/搜索/排序） | ★★★ |
| `CaseDetailView.vue` | `views/CaseDetailView.vue` | 案例详情页（三栏布局，核心页面） | ★★★★★ |

### 3.4 RV-Insights 新增 API 客户端

新增 `api/cases.ts`：

```typescript
// api/cases.ts
import { fetchEventSource } from '@microsoft/fetch-event-source'
import { client } from './client'  // 复用 ScienceClaw 的 axios 实例

// REST API
export const casesApi = {
  create: (data: CreateCaseRequest) => client.post('/api/v1/cases', data),
  list: (params: CaseListParams) => client.get('/api/v1/cases', { params }),
  get: (id: string) => client.get(`/api/v1/cases/${id}`),
  delete: (id: string) => client.delete(`/api/v1/cases/${id}`),
  start: (id: string) => client.post(`/api/v1/cases/${id}/start`),
  review: (id: string, decision: ReviewDecision) =>
    client.post(`/api/v1/cases/${id}/review`, decision),
  getArtifacts: (id: string, stage: string) =>
    client.get(`/api/v1/cases/${id}/artifacts/${stage}`),
  getHistory: (id: string) =>
    client.get(`/api/v1/cases/${id}/history`),
}

// SSE 事件流（复用 ScienceClaw 的 fetchEventSource 模式）
export function subscribeCaseEvents(caseId: string, handlers: SSEHandlers) {
  return fetchEventSource(`/api/v1/cases/${caseId}/events`, {
    headers: { Authorization: `Bearer ${getToken()}` },
    onmessage(ev) { handlers.onEvent?.(JSON.parse(ev.data)) },
    onerror(err) { handlers.onError?.(err) },
    onclose() { handlers.onClose?.() },
  })
}
```

### 3.5 需要重用的 ScienceClaw 组件

以下 ScienceClaw 组件可直接在 RV-Insights 页面中复用：

| 组件 | 复用场景 |
|------|----------|
| `ActivityPanel.vue` | CaseDetailView 的 Agent 实时事件日志区 |
| `ProcessMessage.vue` | Pipeline 阶段执行中状态 |
| `StepMessage.vue` | Pipeline 阶段步骤展示 |
| `FilePanel.vue` / `FilePreviewModal.vue` | 产物文件浏览 |
| `MarkdownEnhancements.vue` | 审核意见、规划方案 Markdown 渲染 |
| `UserMenu.vue` | 全局用户菜单 |

### 3.6 i18n 方案

ScienceClaw 已有 i18n 支持（`locales/`），扩展时遵循相同模式：

```typescript
// locales/zh.json 新增
{
  "pipeline": {
    "explore": "探索",
    "plan": "规划",
    "develop": "开发",
    "review": "审核",
    "test": "测试"
  },
  "case": {
    "status": { "created": "已创建", "exploring": "探索中", ... },
    "actions": { "start": "启动 Pipeline", "approve": "通过", "reject": "驳回" }
  }
}
```

---

## 4. 后端架构重构方案

### 4.1 新架构总览

```
┌─────────────────────────────────────────────────────────┐
│                    Nginx (:80)                          │
├──────────┬──────────────────────┬───────────────────────┤
│ 静态资源  │  /api/v1/sessions/*  │  /api/v1/cases/*      │
│ (Vue SPA) │  /api/v1/auth/*     │  /api/v1/pipeline/*   │
│           │  /api/v1/models/*   │  SSE Events           │
│           │  /api/v1/files/*    │                       │
├──────────┴──────────────────────┴───────────────────────┤
│                     Backend (:8000)                      │
│  ┌─────────────────────┐  ┌───────────────────────────┐ │
│  │  Chat Module        │  │  Pipeline Module           │ │
│  │  (ChatRunner +      │  │  (LangGraph StateGraph +  │ │
│  │   asyncio.Queue)    │  │   Redis Pub/Sub)           │ │
│  │                     │  │                           │ │
│  │  Sessions CRUD      │  │  5-Stage Agent Pipeline:  │ │
│  │  Agent Chat SSE     │  │  Explore → Plan →         │ │
│  │  File Management    │  │  Develop ↔ Review → Test  │ │
│  │  Task Scheduling    │  │  Human-in-the-Loop Gates  │ │
│  │  Tool/Skill API     │  │  (4 个 interrupt() 审批门) │ │
│  │  User/Auth          │  │                           │ │
│  │  Statistics         │  │  EventPublisher → Redis   │ │
│  │  Models Config      │  │  SSE Endpoint ← Redis     │ │
│  └─────────────────────┘  └───────────────────────────┘ │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │  AgentAdapter Layer (跨 SDK 抽象)                  │   │
│  │  ClaudeAgentAdapter  |  OpenAIAgentAdapter        │   │
│  └──────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────┤
│  MongoDB       PostgreSQL        Redis                  │
│  (业务数据)     (检查点)          (事件总线+缓存)         │
├─────────────────────────────────────────────────────────┤
│  Sandbox       WebSearch         Task-Service           │
│  (代码执行)     (搜索引擎)         (定时调度)              │
└─────────────────────────────────────────────────────────┘
```

### 4.2 后端模块映射：ScienceClaw → RV-Insights

| ScienceClaw 模块 | RV-Insights 对应模块 | 处理方式 |
|------------------|---------------------|----------|
| `deepagent/engine.py` → LLM 调度 | `adapters/claude_adapter.py` + `adapters/openai_adapter.py` | **重写**：替换为 design.md 的双 SDK 适配器 |
| `deepagent/runner.py` → Agent 执行 | `chat/runner.py` (Chat) + `pipeline/nodes/*.py` (Pipeline) | **重写**：分离为两个独立运行器 |
| `deepagent/sessions.py` → 会话管理 | `chat/sessions.py` | **重构**：保留 API 契约，改用 MongoDB 新 schema |
| `route/sessions.py` → 会话 API | `route/sessions.py` | **重构**：保留 POST/PUT/GET/DELETE 不变 |
| `route/chat.py` → 任务 Chat API | `route/chat.py` | **重构**：改为对接 ChatRunner |
| `route/auth.py` → 认证 | `route/auth.py` | **重构**：保留 API 契约，改用 JWT |
| `route/file.py` → 文件管理 | `route/file.py` | **重构**：保留 API 契约 |
| `route/models.py` → 模型配置 | `route/models.py` | **保留/微调** |
| `route/statistics.py` → 统计 | `route/statistics.py` | **扩展**：新增 Pipeline 统计 |
| `route/task_settings.py` → 任务配置 | `route/task_settings.py` | **保留/微调** |
| `route/tooluniverse.py` → 工具 | `route/tooluniverse.py` | **保留** |
| `route/im.py` → IM 集成 | `route/im.py` | **保留** |
| `route/memory.py` → 全局记忆 | `route/memory.py` | **保留** |
| `user/` → 用户管理 | `user/` | **重构**：改为 JWT + bcrypt |
| `mongodb/` → 数据库 | `db/mongo.py` | **重构**：新 collection schema |
| `config.py` → 配置 | `config.py` | **扩展**：新增 Pipeline 相关配置 |
| `models.py` → 模型配置 | `models.py` | **保留/微调** |

### 4.3 后端目录结构（最终）

```
backend/
├── main.py                      # FastAPI 入口 + lifespan
├── config.py                    # 配置管理（扩展 Pipeline 配置）
├── models.py                    # LLM 模型配置（保留 ScienceClaw）
│
├── route/                       # API 路由
│   ├── auth.py                  # 认证（JWT + bcrypt）
│   ├── sessions.py              # 会话 CRUD + Chat SSE（保留 ScienceClaw 契约）
│   ├── chat.py                  # 任务 Chat API（保留 ScienceClaw 契约）
│   ├── file.py                  # 文件管理（保留 ScienceClaw 契约）
│   ├── models.py                # 模型配置（保留）
│   ├── statistics.py            # 统计（扩展）
│   ├── task_settings.py         # 任务配置（保留）
│   ├── tooluniverse.py          # 科研工具（保留）
│   ├── im.py                    # IM 集成（保留）
│   ├── memory.py                # 全局记忆（保留）
│   ├── cases.py                 # ★新增★ 案例 CRUD + SSE 事件流
│   └── reviews.py               # ★新增★ 审核操作 + Pipeline 恢复
│
├── pipeline/                    # ★新增★ LangGraph Pipeline 引擎
│   ├── graph.py                 # StateGraph 定义 + 编译
│   ├── state.py                 # PipelineState Pydantic 模型
│   ├── routes.py                # 条件边路由（review 迭代、human gate）
│   ├── cost_guard.py            # 成本熔断器
│   ├── nodes/                   # Agent 节点
│   │   ├── explore.py           # Explorer Agent (Claude SDK)
│   │   ├── plan.py              # Planner Agent (OpenAI SDK)
│   │   ├── develop.py           # Developer Agent (Claude SDK)
│   │   ├── review.py            # Reviewer Agent (OpenAI SDK + 确定性工具)
│   │   ├── test.py              # Tester Agent (Claude SDK)
│   │   └── human_gate.py        # 人工审批门 (interrupt)
│   └── prompts/                 # Agent System Prompts
│       ├── explorer.py
│       ├── reviewer.py
│       └── ...
│
├── chat/                        # ★新增★ Chat 模式引擎
│   ├── runner.py                # ChatRunner + asyncio.Queue SSE
│   └── sessions.py              # 会话管理
│
├── adapters/                    # ★新增★ 跨 SDK 适配器层
│   ├── base.py                  # AgentAdapter 基类
│   ├── claude_adapter.py        # ClaudeAgentAdapter (子进程管理)
│   └── openai_adapter.py        # OpenAIAgentAdapter
│
├── contracts/                   # ★新增★ Agent 间数据契约
│   ├── exploration.py           # ExplorationResult
│   ├── planning.py              # ExecutionPlan
│   ├── development.py           # DevelopmentResult
│   ├── review.py                # ReviewVerdict + ReviewFinding
│   └── testing.py               # TestResult
│
├── events/                      # ★新增★ SSE 事件系统
│   ├── publisher.py             # EventPublisher (Redis Pub/Sub + Stream)
│   └── models.py                # PipelineEvent 模型
│
├── datasources/                 # ★新增★ 外部数据源客户端
│   ├── patchwork.py             # Patchwork API
│   ├── mailing_list.py          # lore.kernel.org
│   └── github_client.py         # GitHub API
│
├── db/                          # 数据库
│   ├── mongo.py                 # MongoDB 连接 + 索引
│   ├── postgres.py              # PostgreSQL (LangGraph Checkpointer)
│   └── collections.py           # Collection schema 定义
│
├── artifacts/                   # ★新增★ 产物管理
│   └── manager.py               # ArtifactManager
│
├── user/                        # 用户管理
│   ├── models.py                # User model
│   ├── dependencies.py          # JWT 验证 + 角色依赖注入
│   └── auth.py                  # Token 生成/验证
│
├── scheduler.py                 # ★新增★ ResourceScheduler (并发控制)
├── security/                    # 安全
│   └── prompt_guard.py          # Prompt 注入防护
│
├── builtin_skills/              # 内置技能包（保留）
├── translations/                # i18n（保留）
├── im/                          # IM 集成（保留）
├── scripts/                     # 工具脚本（保留）
├── notifications.py             # 通知（保留）
├── seekr_sdk.py                 # SearXNG SDK（保留）
├── task_settings.py             # 任务设置（保留）
├── requirements.txt             # Python 依赖
└── Dockerfile
```

---

## 5. API 接口全景图

### 5.1 API 分类

| 分类 | 前缀 | 来源 | 说明 |
|------|------|------|------|
| **Auth** | `/api/v1/auth/*` | ScienceClaw（保留契约） | 登录/注册/状态/刷新 |
| **Sessions** | `/api/v1/sessions/*` | ScienceClaw（保留契约） | 会话 CRUD + Chat SSE |
| **Chat** | `/api/v1/chat/*` | ScienceClaw（保留契约） | 任务调用的 Chat API |
| **Files** | `/api/v1/files/*` | ScienceClaw（保留契约） | 文件管理 |
| **Models** | `/api/v1/models/*` | ScienceClaw（保留） | LLM 模型配置 |
| **Statistics** | `/api/v1/statistics/*` | ScienceClaw（扩展） | Token 统计 + Pipeline 统计 |
| **Task Settings** | `/api/v1/task-settings/*` | ScienceClaw（保留） | 定时任务 CRUD |
| **Tasks** | `/api/v1/tasks/*` | ScienceClaw（保留） | 任务执行日志 |
| **ToolUniverse** | `/api/v1/tooluniverse/*` | ScienceClaw（保留） | 科研工具 |
| **IM** | `/api/v1/im/*` | ScienceClaw（保留） | 飞书/Lark 集成 |
| **Memory** | `/api/v1/memory/*` | ScienceClaw（保留） | 全局记忆 |
| **Cases** | `/api/v1/cases/*` | **新增** | 案例 CRUD + SSE 事件流 |
| **Reviews** | `/api/v1/reviews/*` | **新增** | 审核决策提交 |

### 5.2 完整 API 端点清单

#### Auth（保留 ScienceClaw 契约）
| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| `POST` | `/api/v1/auth/login` | 登录（返回 access_token + refresh_token） | ❌ |
| `POST` | `/api/v1/auth/register` | 注册 | ❌ |
| `GET` | `/api/v1/auth/status` | 当前认证状态 | ✅ |
| `POST` | `/api/v1/auth/refresh` | 刷新 Token | ❌ |
| `POST` | `/api/v1/auth/logout` | 登出 | ✅ |

#### Sessions（保留 ScienceClaw 契约）
| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| `PUT` | `/api/v1/sessions` | 创建新会话 | ✅ |
| `GET` | `/api/v1/sessions` | 会话列表（分页） | ✅ |
| `GET` | `/api/v1/sessions/{id}` | 会话详情 | ✅ |
| `DELETE` | `/api/v1/sessions/{id}` | 删除会话 | ✅ |
| `POST` | `/api/v1/sessions/{id}/chat` | Chat SSE 流 | ✅ |
| `POST` | `/api/v1/sessions/{id}/stop` | 停止会话执行 | ✅ |
| `POST` | `/api/v1/sessions/{id}/clear_unread_message_count` | 清未读 | ✅ |
| `POST` | `/api/v1/sessions/{id}/share` | 开启分享 | ✅ |
| `DELETE` | `/api/v1/sessions/{id}/share` | 取消分享 | ✅ |
| `GET` | `/api/v1/sessions/{id}/files` | 会话文件列表 | ✅ |
| `GET` | `/api/v1/sessions/{id}/sandbox-file` | 读取沙箱文件 | ✅ |
| `GET` | `/api/v1/sessions/shared/{id}` | 获取分享会话（无需登录） | ❌ |

#### Chat（保留 ScienceClaw 契约）
| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| `POST` | `/api/v1/chat` | 任务调度触发的 Chat API | API Key |
| `POST` | `/api/v1/task/parse-schedule` | 自然语言→crontab | ✅ |

#### Files（保留 ScienceClaw 契约）
| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| `POST` | `/api/v1/files/upload` | 上传文件 | ✅ |
| `GET` | `/api/v1/files/download` | 下载文件 | ✅ |
| `GET` | `/api/v1/files/list` | 文件列表 | ✅ |

#### Statistics（扩展）
| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| `GET` | `/api/v1/statistics/summary` | 统计汇总（保留） | ✅ |
| `GET` | `/api/v1/statistics/pipeline` | ★新增★ Pipeline 统计 | ✅ |
| `GET` | `/api/v1/statistics/costs` | ★新增★ Token 消耗明细 | ✅ |

#### Cases（★新增★）
| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| `POST` | `/api/v1/cases` | 创建新案例 | ✅ |
| `GET` | `/api/v1/cases` | 案例列表（分页/筛选/搜索） | ✅ |
| `GET` | `/api/v1/cases/{id}` | 案例详情 | ✅ |
| `DELETE` | `/api/v1/cases/{id}` | 删除案例 | ✅(admin) |
| `POST` | `/api/v1/cases/{id}/start` | 启动 Pipeline | ✅ |
| `GET` | `/api/v1/cases/{id}/events` | SSE 事件流 | ✅ |
| `GET` | `/api/v1/cases/{id}/artifacts/{stage}` | 获取阶段产物 | ✅ |

#### Reviews（★新增★）
| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| `POST` | `/api/v1/cases/{id}/review` | 提交人工审核决策 | ✅ |
| `GET` | `/api/v1/cases/{id}/history` | 审核历史记录 | ✅ |

---

## 6. 数据库设计

### 6.1 MongoDB 集合（完整）

保留 ScienceClaw 的集合 + 新增 RV-Insights 集合：

| 集合 | 来源 | 用途 |
|------|------|------|
| `users` | 保留（改造） | 用户管理（新增 role: "admin"/"user"） |
| `sessions` | 保留（改造） | Chat 会话（保留原 schema） |
| `session_messages` | 保留 | Chat 消息记录 |
| `tools` | 保留 | 工具配置 |
| `tasks` | 保留 | 定时任务配置 |
| `task_logs` | 保留 | 任务执行日志 |
| `webhooks` | 保留 | Webhook 配置 |
| `memory` | 保留 | 全局记忆 |
| **`contribution_cases`** | **新增** | ★ 案例主集合（嵌入式文档） |
| **`human_reviews`** | **新增** | ★ 人工审核记录 |
| **`stage_outputs`** | **新增** | ★ 阶段产物（通过 ref 引用） |
| **`audit_log`** | **新增** | ★ 审计日志（append-only） |
| **`knowledge_entries`** | **新增** | ★ 知识库（Phase 2） |

### 6.2 MongoDB 索引

```python
# 保留 ScienceClaw 原有索引
# 新增以下索引：

# contribution_cases
db.contribution_cases.create_index([("status", 1), ("created_at", -1)])
db.contribution_cases.create_index([("target_repo", 1)])
db.contribution_cases.create_index([("updated_at", -1)])

# human_reviews
db.human_reviews.create_index([("case_id", 1), ("created_at", -1)])
db.human_reviews.create_index([("reviewer", 1)])

# audit_log
db.audit_log.create_index([("case_id", 1), ("timestamp", -1)])
db.audit_log.create_index([("event_type", 1)])

# knowledge_entries
db.knowledge_entries.create_index([("title", "text"), ("content", "text")])
db.knowledge_entries.create_index([("tags", 1)])
```

### 6.3 PostgreSQL（LangGraph Checkpointer）

```python
# 专用于 LangGraph 检查点持久化
# 表由 AsyncPostgresSaver.setup() 自动创建：
#   - checkpoints
#   - checkpoint_blobs
#   - checkpoint_writes
```

### 6.4 Redis

| 用途 | Key 模式 | 数据类型 |
|------|----------|----------|
| Pipeline SSE 事件 | `case:{id}:events` | Pub/Sub Channel |
| Pipeline 事件恢复 | `case:{id}:stream` | Stream (maxlen=500) |
| Chat SSE 事件 | `session:{id}:events` | asyncio.Queue (进程内) |
| 会话锁定 | `session:{id}:lock` | String (TTL) |
| 速率限制 | `rate_limit:{ip}` | Sorted Set |
| Celery 任务队列 | `celery:*` | List (保留) |

---

## 7. Agent Pipeline 实现方案

### 7.1 Pipeline 生命周期

```
Created → Exploring → [Human Gate 1] → Planning → [Human Gate 2]
       → Developing ↔ Reviewing (≤3 rounds) → [Human Gate 3]
       → Testing → [Human Gate 4] → Completed

任意 Human Gate 可 → Abandoned
```

### 7.2 SDK 分配

| 阶段 | SDK | 模型 | 关键工具 |
|------|-----|------|----------|
| Explore | Claude Agent SDK | claude-sonnet-4 | Read/Grep/Glob/WebSearch/Bash |
| Plan | OpenAI Agents SDK | gpt-4o | Guardrails/Handoff |
| Develop | Claude Agent SDK | claude-sonnet-4 | Write/Edit/Bash/Grep/MCP |
| Review | OpenAI Agents SDK | codex-mini | Handoff (security/correctness/style) + checkpatch.pl + sparse |
| Test | Claude Agent SDK | claude-sonnet-4 | Bash/Read (QEMU sandbox) |

### 7.3 Human-in-the-Loop

使用 LangGraph `interrupt()` 机制，在 4 个审批门暂停：

```python
# pipeline/nodes/human_gate.py
async def human_gate_node(state: PipelineState) -> Command:
    decision = interrupt({
        "type": "review_request",
        "stage": state["current_stage"],
        "artifacts_summary": summarize_artifacts(state),
    })
    return Command(goto=decision["action"],
                   update={"approval_history": [...]})
```

用户通过 `POST /api/v1/cases/{id}/review` 提交决策后，Pipeline 恢复执行。

### 7.4 SSE 事件流

```
Agent Node → EventPublisher.publish() → Redis Pub/Sub
                                      → Redis Stream (恢复)

FastAPI SSE Endpoint ← Redis Pub/Sub Subscription
                     ← Redis Stream (重连恢复)
                     → EventSourceResponse → Vue Client
```

事件类型表（design.md 4.6.2 定义）：

| 事件类型 | 触发时机 |
|----------|----------|
| `stage_change` | 阶段状态变更 |
| `agent_output` | Agent 输出（thinking/tool_call/result） |
| `review_request` | 需要人工审核 |
| `iteration_update` | Develop↔Review 迭代更新 |
| `cost_update` | Token 消耗更新 |
| `error` | 错误事件 |
| `completed` | Pipeline 完成 |

---

## 8. Chat 模式实现方案

### 8.1 架构

Chat 模式独立于 Pipeline 模式，使用 `ChatRunner` + `asyncio.Queue` 实现 SSE 推送。

```python
# chat/runner.py
class ChatRunner:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.queue = asyncio.Queue()  # SSE 事件队列
        self._stop_event = asyncio.Event()

    async def run(self, user_message: str) -> None:
        """执行 Chat 任务，推送事件到 queue"""
        # 复用 ScienceClaw 的 DeepAgents 逻辑
        # 或者桥接到 Claude/OpenAI Agent SDK
        ...

    async def stop(self) -> None:
        self._stop_event.set()
```

Chat SSE 端点保持 ScienceClaw 的契约：
```
POST /api/v1/sessions/{id}/chat → EventSourceResponse
```

### 8.2 与 Pipeline 的边界

- **Chat 模式**：通用对话，无固定流程，用户自由交互
- **Pipeline 模式**：结构化 5 阶段流水线，有固定状态机和审批门
- **共享**：用户系统、文件管理、MongoDB 数据库
- **独立**：Chat 用 asyncio.Queue，Pipeline 用 Redis Pub/Sub

---

## 9. Docker Compose 重构

### 9.1 服务变化

| 服务 | 当前 (ScienceClaw) | 重构后 (RV-Insights) | 变化 |
|------|-------------------|---------------------|------|
| `sandbox` | ✅ | ✅ 保留 | — |
| `mongo` | ✅ | ✅ 保留 | 新 collection schema |
| `redis` | ✅ | ✅ 保留 | 新 channel/stream |
| `searxng` | ✅ | ✅ 保留 | — |
| `websearch` | ✅ | ✅ 保留 | — |
| `postgres` | ❌ | ✅ **新增** | LangGraph Checkpointer |
| `backend` | ✅ (DeepAgents) | ✅ **重写** (Chat + Pipeline) | 完全替换 |
| `scheduler_api` | ✅ (FastAPI) | ✅ 保留（改造） | 对接新 backend API |
| `celery_worker` | ✅ | ✅ 保留 | — |
| `celery_beat` | ✅ | ✅ 保留 | — |
| `frontend` | ✅ (node dev) | ✅ 保留（改名 web-console） | Vite 代理配置调整 |
| `nginx` | ❌ | ✅ **新增** (生产部署) | 反向代理 + 静态资源 |

### 9.2 新 docker-compose.yml 结构

```yaml
services:
  # === 保留：基础设施 ===
  sandbox:        # 代码执行沙箱
  mongo:          # MongoDB
  redis:          # Redis
  searxng:        # 搜索引擎
  websearch:      # 搜索 API

  # === 新增：Pipeline 数据库 ===
  postgres:       # PostgreSQL 16 (LangGraph Checkpointer)

  # === 重写：后端 ===
  backend:        # Chat + Pipeline + API
    build: ./backend
    environment:
      MONGO_URI: mongodb://...
      POSTGRES_URI: postgresql://...
      REDIS_URL: redis://...
      CLAUDE_API_KEY: ${CLAUDE_API_KEY}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      JWT_SECRET: ${JWT_SECRET}
    depends_on: [mongo, postgres, redis, sandbox, websearch]

  # === 保留：任务调度 ===
  scheduler_api:
  celery_worker:
  celery_beat:

  # === 保留：前端 ===
  frontend:       # 或 nginx + dist
```

### 9.3 前端部署方式

**开发模式**（当前 ScienceClaw 方式）：
```yaml
frontend:
  image: node:20
  command: npm run dev -- --host 0.0.0.0 --port 5173
  environment:
    BACKEND_URL: http://backend:8000
```

**生产模式**（design.md 推荐）：
```yaml
nginx:
  image: nginx:alpine
  volumes:
    - ./web-console/dist:/usr/share/nginx/html:ro
    - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
  ports:
    - "80:80"
```

---

## 10. 实施计划（分 Sprint）

### Sprint 0：基础架构搭建（1 周）

| # | 任务 | 产出 | 优先级 |
|---|------|------|--------|
| 0.1 | 初始化 backend 目录结构（按 4.3 节） | `backend/` 骨架 | P0 |
| 0.2 | 配置 FastAPI 入口 + lifespan（MongoDB/PostgreSQL/Redis 连接） | `main.py`, `config.py` | P0 |
| 0.3 | 搭建 Docker Compose（新增 postgres + nginx） | `docker-compose.yml` | P0 |
| 0.4 | 实现 MongoDB 连接 + 索引初始化（保留 ScienceClaw 集合 + 新增 RV 集合） | `db/mongo.py`, `db/collections.py` | P0 |
| 0.5 | 实现 PostgreSQL 连接（LangGraph Checkpointer） | `db/postgres.py` | P0 |
| 0.6 | 实现 Redis 连接 + EventPublisher | `events/publisher.py` | P0 |
| 0.7 | 迁移 ScienceClaw 前端到 `web-console/`，验证构建 | 前端可用 | P0 |

### Sprint 1：认证 + 用户系统（1 周）

| # | 任务 | 产出 | 优先级 |
|---|------|------|--------|
| 1.1 | 实现 JWT 生成/验证（access + refresh token） | `user/auth.py` | P0 |
| 1.2 | 实现用户注册/登录 API（保留 ScienceClaw 契约） | `route/auth.py` | P0 |
| 1.3 | 实现依赖注入（get_current_user + require_role） | `user/dependencies.py` | P0 |
| 1.4 | 实现 RBAC（admin/user 2 角色） | — | P0 |
| 1.5 | 实现 bootstrap admin 创建逻辑 | `main.py` lifespan | P0 |
| 1.6 | 前端：验证登录/注册流程 | — | P1 |

### Sprint 2：Chat 模式（1.5 周）

| # | 任务 | 产出 | 优先级 |
|---|------|------|--------|
| 2.1 | 实现 ChatRunner + asyncio.Queue SSE 引擎 | `chat/runner.py` | P0 |
| 2.2 | 实现会话管理（创建/列表/详情/删除） | `chat/sessions.py` | P0 |
| 2.3 | 实现 Chat SSE 端点（保留 ScienceClaw 契约） | `route/sessions.py` | P0 |
| 2.4 | 实现文件管理 API（上传/下载/列表） | `route/file.py` | P0 |
| 2.5 | 实现模型配置 API | `route/models.py` | P1 |
| 2.6 | 实现统计 API | `route/statistics.py` | P1 |
| 2.7 | 前后端联调：Chat 对话完整流程 | — | P0 |

### Sprint 3：Pipeline 引擎核心（2 周）

| # | 任务 | 产出 | 优先级 |
|---|------|------|--------|
| 3.1 | 实现 PipelineState 模型 + StateGraph 定义 | `pipeline/state.py`, `pipeline/graph.py` | P0 |
| 3.2 | 实现 AgentAdapter 基类 + ClaudeAgentAdapter | `adapters/base.py`, `adapters/claude_adapter.py` | P0 |
| 3.3 | 实现 OpenAIAgentAdapter | `adapters/openai_adapter.py` | P0 |
| 3.4 | 实现 5 个 Agent 节点的基架（Mock Agent 通过） | `pipeline/nodes/*.py` | P0 |
| 3.5 | 实现条件边路由（review 迭代 + human gate） | `pipeline/routes.py` | P0 |
| 3.6 | 实现 Human Gate 节点（interrupt）+ 审核 API | `pipeline/nodes/human_gate.py`, `route/reviews.py` | P0 |
| 3.7 | 实现案例 CRUD API + Pipeline 启动 | `route/cases.py` | P0 |
| 3.8 | 实现 SSE 事件流端点（Redis Pub/Sub → SSE） | `route/cases.py` SSE 部分 | P0 |
| 3.9 | 集成测试：Mock Agent 完整 5 阶段流程（含审核门） | `tests/integration/` | P0 |

### Sprint 4：Agent 节点实现（2 周）

| # | 任务 | 产出 | 优先级 |
|---|------|------|--------|
| 4.1 | 实现 Explorer Agent（Claude SDK + 幻觉验证） | `pipeline/nodes/explore.py` | P0 |
| 4.2 | 实现 Planner Agent（OpenAI SDK + Guardrails + Handoff） | `pipeline/nodes/plan.py` | P0 |
| 4.3 | 实现 Developer Agent（Claude SDK + canUseTool 审批） | `pipeline/nodes/develop.py` | P0 |
| 4.4 | 实现 Reviewer Agent（OpenAI SDK Handoff + checkpatch.pl + sparse） | `pipeline/nodes/review.py` | P0 |
| 4.5 | 实现 Tester Agent（Claude SDK + QEMU 环境） | `pipeline/nodes/test.py` | P0 |
| 4.6 | 实现数据契约 Pydantic 模型 | `contracts/*.py` | P0 |
| 4.7 | 实现 Agent System Prompts | `pipeline/prompts/*.py` | P0 |
| 4.8 | 实现数据源客户端（Patchwork/Mailing List/GitHub） | `datasources/*.py` | P1 |
| 4.9 | 实现 ArtifactManager（产物存储） | `artifacts/manager.py` | P0 |
| 4.10 | 实现 ResourceScheduler（并发控制） | `scheduler.py` | P1 |
| 4.11 | 实现 CostCircuitBreaker（成本熔断） | `pipeline/cost_guard.py` | P2 |

### Sprint 5：前端 RV-Insights 页面（2 周）

| # | 任务 | 产出 | 优先级 |
|---|------|------|--------|
| 5.1 | 实现 CaseListView（案例列表 + 状态筛选 + 搜索） | `views/CaseListView.vue` | P0 |
| 5.2 | 实现 CaseDetailView 三栏布局框架 | `views/CaseDetailView.vue` | P0 |
| 5.3 | 实现 PipelineView + StageNode + HumanGate 组件 | `components/pipeline/*.vue` | P0 |
| 5.4 | 实现 ReviewPanel + ReviewFinding 组件 | `components/review/*.vue` | P0 |
| 5.5 | 实现 DiffViewer（Monaco Editor） | `components/review/DiffViewer.vue` | P1 |
| 5.6 | 实现 ContributionCard + EvidenceChain | `components/exploration/*.vue` | P1 |
| 5.7 | 实现 TestResultSummary + TestLogViewer | `components/testing/*.vue` | P1 |
| 5.8 | 实现 SSE 事件流 comosable（useCaseEvents） | `composables/useCaseEvents.ts` | P0 |
| 5.9 | 实现 case Pinia store | `stores/caseStore.ts` | P0 |
| 5.10 | 前后端联调：完整 Pipeline 交互流程 | — | P0 |

### Sprint 6：定时任务 + IM + 安全（1.5 周）

| # | 任务 | 产出 | 优先级 |
|---|------|------|--------|
| 6.1 | 迁移 task-service（调度器对接新 backend API） | `task-service/` | P1 |
| 6.2 | 实现 Prompt 注入防护 | `security/prompt_guard.py` | P2 |
| 6.3 | 实现安全响应头中间件 | `middleware/` | P2 |
| 6.4 | 实现速率限制（slowapi + Redis） | `middleware/rate_limit.py` | P2 |
| 6.5 | 实现审计日志记录 | `db/audit.py` | P2 |
| 6.6 | 前后端联调：定时任务 + IM 通知 | — | P2 |

### Sprint 7：测试 + 文档 + 部署（1 周）

| # | 任务 | 产出 | 优先级 |
|---|------|------|--------|
| 7.1 | 编写后端单元测试（Pydantic 模型 + 路由函数） | `tests/unit/` | P0 |
| 7.2 | 编写集成测试（testcontainers: MongoDB + PostgreSQL） | `tests/integration/` | P0 |
| 7.3 | 编写前端 E2E 测试（Playwright） | `tests/e2e/` | P1 |
| 7.4 | 编写 Agent 评估数据集 | `tests/eval/` | P2 |
| 7.5 | 生产部署配置（Nginx 配置 + 环境变量） | `nginx/` + `.env.example` | P0 |
| 7.6 | 编写运维文档（部署 + 监控 + 备份） | `docs/` | P1 |

### 里程碑总览

| 里程碑 | Sprint | 交付物 | 验收标准 |
|--------|--------|--------|----------|
| **M1: 基础就绪** | S0-S1 | 运行中的前后端 + 认证 | 可登录，Docker Compose 全部服务 healthy |
| **M2: Chat 可用** | S2 | Chat 模式完整可用 | 前端 Chat 对话正常工作 |
| **M3: Pipeline 贯通** | S3-S4 | 5 阶段 Pipeline 端到端可运行 | Mock Agent 完成完整流程 |
| **M4: 前端完整** | S5 | RV-Insights 专属页面就绪 | 案例创建→Pipeline 可视化→审核→完成 |
| **M5: 生产就绪** | S6-S7 | 安全加固 + 测试 + 文档 | 全部测试通过，可部署 |

---

## 11. 风险评估与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| ScienceClaw API 契约理解偏差 | 中 | 高 | 逐接口对比，保留所有请求/响应格式 |
| Claude Agent SDK API 不稳定 | 高 | 中 | Adapter 层隔离，版本锁定 |
| LangGraph StateGraph 复杂度超预期 | 中 | 高 | 先 Mock Agent 验证流程，再替换真实 Agent |
| Chat + Pipeline 双模式共享资源冲突 | 中 | 中 | ResourceScheduler 并发控制，独立 asyncio.Queue/Redis PubSub |
| 前端适配新后端时间不足 | 高 | 中 | 优先保证核心页面（CaseDetailView），次要页面（Knowledge）延后 Phase 2 |
| QEMU 沙箱搭建困难 | 中 | 中 | 先用编译验证替代 QEMU 运行时测试（MVP 降级） |
| MongoDB schema 迁移导致 ScienceClaw 数据丢失 | 低 | 高 | 新增集合，不删除原集合；双写过渡期 |

---

## 附录 A. 文件级变更清单

### A.1 新增文件（完整列表）

```
backend/
├── adapters/
│   ├── __init__.py
│   ├── base.py                    # AgentAdapter 基类
│   ├── claude_adapter.py          # ClaudeAgentAdapter
│   └── openai_adapter.py          # OpenAIAgentAdapter
├── pipeline/
│   ├── __init__.py
│   ├── graph.py                   # StateGraph 构建
│   ├── state.py                   # PipelineState 模型
│   ├── routes.py                  # 条件边路由
│   ├── cost_guard.py              # 成本熔断
│   ├── nodes/
│   │   ├── __init__.py
│   │   ├── explore.py
│   │   ├── plan.py
│   │   ├── develop.py
│   │   ├── review.py
│   │   ├── test.py
│   │   └── human_gate.py
│   └── prompts/
│       ├── __init__.py
│       ├── explorer.py
│       └── reviewer.py
├── chat/
│   ├── __init__.py
│   ├── runner.py                  # ChatRunner
│   └── sessions.py                # 会话管理
├── contracts/
│   ├── __init__.py
│   ├── exploration.py
│   ├── planning.py
│   ├── development.py
│   ├── review.py
│   └── testing.py
├── events/
│   ├── __init__.py
│   ├── publisher.py               # EventPublisher
│   └── models.py                  # PipelineEvent
├── datasources/
│   ├── __init__.py
│   ├── patchwork.py
│   ├── mailing_list.py
│   └── github_client.py
├── db/
│   ├── __init__.py
│   ├── mongo.py                   # MongoDB 连接
│   ├── postgres.py                # PostgreSQL 检查点
│   └── collections.py             # Collection schema
├── artifacts/
│   ├── __init__.py
│   └── manager.py                 # ArtifactManager
├── route/
│   ├── cases.py                   # ★新增★ 案例 CRUD + SSE
│   └── reviews.py                 # ★新增★ 审核操作
├── security/
│   ├── __init__.py
│   └── prompt_guard.py            # Prompt 注入防护
├── middleware/
│   ├── __init__.py
│   ├── rate_limit.py
│   └── security_headers.py
└── scheduler.py                   # ResourceScheduler

web-console/src/ (新增 RV-Insights 组件)
├── views/
│   ├── CaseListView.vue
│   └── CaseDetailView.vue
├── components/
│   ├── pipeline/
│   │   ├── PipelineView.vue
│   │   ├── StageNode.vue
│   │   ├── HumanGate.vue
│   │   └── IterationBadge.vue
│   ├── review/
│   │   ├── ReviewPanel.vue
│   │   ├── ReviewFinding.vue
│   │   └── DiffViewer.vue
│   ├── exploration/
│   │   ├── ContributionCard.vue
│   │   └── EvidenceChain.vue
│   └── testing/
│       ├── TestResultSummary.vue
│       └── TestLogViewer.vue
├── api/
│   └── cases.ts                   # ★新增★ 案例 API
├── composables/
│   └── useCaseEvents.ts           # ★新增★ SSE 事件流
├── stores/
│   └── caseStore.ts               # ★新增★ 案例状态管理
└── types/
    ├── case.ts                    # ★新增★ 案例类型
    ├── pipeline.ts                # ★新增★ Pipeline 类型
    └── event.ts                   # ★新增★ SSE 事件类型
```

### A.2 需要修改的文件

| 文件 | 修改内容 |
|------|----------|
| `backend/main.py` | 重写：Chat + Pipeline 双模式注册 |
| `backend/config.py` | 扩展：新增 Pipeline 配置项 |
| `backend/route/auth.py` | 重构：JWT 替换 Session Token |
| `backend/route/sessions.py` | 重构：对接 ChatRunner |
| `backend/route/chat.py` | 重构：对接 ChatRunner |
| `backend/route/file.py` | 重构：保留 API 契约，对接新存储 |
| `backend/route/statistics.py` | 扩展：新增 Pipeline 统计 |
| `backend/db/mongo.py` (原 mongodb/) | 重构：新 collection schema |
| `backend/user/` | 重构：JWT + bcrypt |
| `docker-compose.yml` | 重写：新增 postgres + nginx |
| `web-console/src/router/index.ts` | 扩展：新增 /cases 路由 |
| `web-console/src/api/client.ts` | 微调：后端 URL 配置 |
| `task-service/` | 改造：对接新 backend API |

### A.3 需要删除的文件

| 文件 | 原因 |
|------|------|
| `backend/deepagent/` | 替换为 `adapters/` + `chat/` + `pipeline/` |
| `backend/mongodb/` (原) | 替换为 `db/mongo.py` |
| `ScienceClaw/backend/` (整个) | 已重写到 `backend/` |

---

## 附录 B. 与 ScienceClaw 的差异对照表

| 维度 | ScienceClaw | RV-Insights |
|------|------------|-------------|
| **Agent 引擎** | LangChain DeepAgents | LangGraph StateGraph + ChatRunner |
| **Pipeline** | 无 | 5 阶段 Agent Pipeline (Explore→Plan→Develop↔Review→Test) |
| **Chat 模式** | 有（DeepAgents） | 有（ChatRunner，保留 API 契约） |
| **Human-in-the-Loop** | 无 | 4 个 interrupt() 审批门 |
| **SSE 事件总线** | 直接 SSE | Redis Pub/Sub + Stream（断线重连恢复） |
| **双 SDK** | 单一 DeepAgents | Claude Agent SDK + OpenAI Agents SDK |
| **数据库** | MongoDB | MongoDB + PostgreSQL（检查点） |
| **前端框架** | Vue 3 + TailwindCSS | 同（直接迁移） |
| **核心页面** | Chat, Tools, Skills, Tasks, Statistics | 上述全部 + Cases, Pipeline 可视化, Review |
| **认证** | Session + API Key | JWT + API Key |
| **RBAC** | 单角色（admin bootstrap） | 2 角色：admin / user |
| **定时任务** | Celery + Celery Beat | 同（保留） |
| **IM 集成** | Lark/Feishu | 同（保留） |
| **搜索** | SearXNG + Crawl4AI | 同（保留） |
| **沙箱** | AIO Sandbox (Docker) | 同（保留）+ QEMU 扩展 |
| **部署** | Docker Compose 9 服务 | Docker Compose 11 服务（+PostgreSQL +Nginx） |

---

> **本计划经 design.md v4 变更摘要、mvp-tasks.md、chat-architecture.md、migration-map.md 交叉验证，确保与最新设计一致。**

---

## 附录 C. 探索验证后修正（2026-04-29）

> 以下修正基于对 ScienceClaw 实际代码（frontend + backend）和当前 rv-claw 仓库的深度探索得出。

### C.1 关键发现

| 发现 | 影响 | 处理 |
|------|------|------|
| **ScienceClaw 前端使用 Composables（非 Pinia）** | 状态管理模式差异 | 3.4 节 RV 新增 component 的 store 改为 composable 模式，保持一致性 |
| **ScienceClaw 后端使用 Session Token（非 JWT）** | 认证机制差异 | design.md 要求 JWT，后端按 JWT 实现，前端适配 Bearer token |
| **ScienceClaw 有完善的 IM 集成（Lark + WeChat bridge）** | 功能范围大 | 保留整个 `im/` 模块，API 契约不变 |
| **ScienceClaw 有完善的内置技能系统（xlsx/pdf/docx/pptx 等）** | 需保留 | 保留 `builtin_skills/` 目录 |
| **ScienceClaw 使用 LangChain DeepAgents（非 LangGraph）** | Agent 引擎完全不同 | Chat 模式可选择保留 DeepAgents 或改为 ChatRunner；Pipeline 必须用 LangGraph |
| **rv-claw 当前无任何 RV-Insights 专属代码** | 从零开始 | 全部后端需新建，前端在 ScienceClaw 基础上扩展 |
| **tasks/ 目录仅有 design.md，无 mvp-tasks.md 等文件** | 缺少任务文件 | design.md 引用的文件都需创建（或在计划中覆盖） |
| **ScienceClaw 有 in-memory pub/sub（notifications.py），非 Redis** | SSE 机制差异 | 改为 Redis Pub/Sub + Stream（design.md 要求）用于 Pipeline；Chat 保留 asyncio.Queue |
| **ScienceClaw 有资源监控仪表盘 + Token 统计** | 前端已有统计页 | 保留并扩展，新增 Pipeline 统计 |
| **ScienceClaw 有任务调度（Celery + Celery Beat + FastAPI scheduler_api）** | 调度系统完善 | 保留 task-service，对接新 backend API |

### C.2 文档修正

| 原计划章节 | 修正内容 |
|-----------|----------|
| 3.4 节 stores/caseStore.ts | 改为 composables/useCaseStore.ts，遵循 ScienceClaw 的 composable 模式（module-level ref） |
| 4.2 节后端目录结构 | Chat 模式可选择保留 `deepagent/`（原 DeepAgents 引擎），在 `chat/runner.py` 中调用 |
| 5.2 节 Auth API | login 返回的 token 结构按 ScienceClaw 契约：`{user, access_token, refresh_token, token_type}` |
| 7.2 节 Chat 实现 | 可选方案 A: 保留 DeepAgents 引擎（兼容性好）；方案 B: 重写为 LangGraph create_react_agent（统一架构） |
| 9.2 节 Mongo 集合 | 保留全部 ScienceClaw 集合（14 个），新增 RV-Insights 5 个集合 |
| 附录 B 差异表 | 补充：ScienceClaw 的 IM 集成、内置技能系统、资源监控仪表盘 RV-Insights 全部保留 |

### C.3 Sprint 修正

| Sprint | 原估算 | 修正 | 原因 |
|--------|--------|------|------|
| S2 Chat 模式 | 1.5 周 | 2 周 | 需完整保留 DeepAgents 引擎 + 技能/工具系统 |
| S3 Pipeline 核心 | 2 周 | 2.5 周 | Redis Pub/Sub + LangGraph 集成复杂度高于预期 |
| S6 定时任务 | 1.5 周 | 1 周 | task-service 几乎无需改动（仅 API URL 调整） |
| **总计** | 10 周 | 11 周 | —**

---

## 附录 D. 核心 Vue 组件详细规格

### D.1 CaseListView（案例列表页）

```
功能：展示所有贡献案例，支持状态筛选、搜索、排序、分页
路由：/cases
状态管理：useCaseList composable (module-level ref)
```

**组件树**：
```
CaseListView
├── TopBar (标题 + "新建案例"按钮 + 搜索框)
├── StatusFilterBar (状态筛选标签：全部/已创建/探索中/规划中/开发中/审核中/测试中/已完成/已放弃)
├── CaseTable (表格视图)
│   ├── CaseRow（每行：标题、状态徽章、目标仓库、进度、创建时间）
│   │   └── CaseStatusBadge (状态颜色映射)
│   └── Pagination (分页控件)
└── CreateCaseDialog (新建案例模态框)
    ├── TitleInput
    ├── TargetRepoSelect (Linux内核/QEMU/OpenSBI/GCC/LLVM)
    ├── ContextTextarea (用户提示/需求描述)
    └── SubmitButton
```

**Props/Events 接口**：
```typescript
// CaseListView emits
interface CaseListViewEmits {
  'select-case': [caseId: string]
  'create-case': [data: CreateCaseRequest]
}

// CreateCaseRequest
interface CreateCaseRequest {
  title: string
  target_repo: 'linux' | 'qemu' | 'opensbi' | 'gcc' | 'llvm'
  input_context: string
  contribution_type?: ContributionType
}

// CaseListParams (查询参数)
interface CaseListParams {
  status?: CaseStatus | ''
  search?: string
  target_repo?: string
  page: number
  page_size: number  // 默认 20
  sort_by?: 'created_at' | 'updated_at' | 'cost'
  sort_order?: 'asc' | 'desc'
}
```

**状态徽章颜色映射**：
```typescript
const STATUS_COLORS: Record<CaseStatus, string> = {
  'created': 'bg-gray-500',
  'exploring': 'bg-blue-500 animate-pulse',
  'pending_explore_review': 'bg-yellow-500',
  'planning': 'bg-indigo-500 animate-pulse',
  'pending_plan_review': 'bg-yellow-500',
  'developing': 'bg-green-500 animate-pulse',
  'reviewing': 'bg-purple-500 animate-pulse',
  'pending_code_review': 'bg-yellow-500',
  'testing': 'bg-orange-500 animate-pulse',
  'pending_test_review': 'bg-yellow-500',
  'completed': 'bg-emerald-600',
  'abandoned': 'bg-red-500',
}
```

### D.2 CaseDetailView（案例详情页 — ★核心页面★）

```
功能：三栏布局展示 Pipeline 全生命周期
路由：/cases/:id
状态管理：useCaseDetail composable + useCaseEvents SSE composable
```

**布局结构**（三栏响应式）：
```
CaseDetailView
├── TopBar (案例标题 + 状态徽章 + 成本统计 + 操作按钮组)
│   ├── CaseTitle (可编辑标题)
│   ├── CaseStatusBadge (大号状态 + 阶段进度条)
│   ├── CostSummary (Token消耗 | 预估费用)
│   └── ActionButtons
│       ├── StartPipelineBtn (created 状态显示)
│       ├── AbandonCaseBtn (非终态显示)
│       └── DeleteCaseBtn (admin 显示)
│
├── LeftSidebar (左侧 Pipeline 导航栏, width: 200px)
│   ├── PipelineProgress (5 阶段垂直进度条)
│   │   ├── StageNavItem × 5 (图标 + 名称 + 状态圆点)
│   │   │   └── onClick → 切换主内容区展示
│   │   └── IterationCounter ("第 N 轮/3 轮", 仅 develop/review 阶段)
│   └── CostBreakdown (按阶段分列的成本明细)
│
├── MainContent (主内容区, flex: 1)
│   ├── [动态组件，根据当前查看阶段渲染]
│   │   ├── ExplorationTab → ContributionCard + EvidenceChain
│   │   ├── PlanTab → ExecutionPlanTree (步骤列表 + 风险标注)
│   │   ├── DevelopTab → DiffViewer (代码变更) + CommitMessageView
│   │   ├── ReviewTab → ReviewFindings (审核发现列表)
│   │   └── TestTab → TestResultSummary + TestLogViewer
│   │
│   └── AgentEventLog (底部可折叠区域, 默认高度 200px, 可拖拽)
│       ├── LogToolbar (搜索/过滤/清空/自动滚动开关)
│       ├── EventList (虚拟滚动，事件按时间排列)
│       │   ├── ThinkingBlock (可折叠，黄色背景)
│       │   ├── ToolCallBlock (工具名 + 参数摘要 + 展开详情)
│       │   ├── StageTransition (阶段变更通知，蓝色边框)
│       │   └── ErrorBlock (红色高亮)
│       └── AutoScrollButton
│
└── RightPanel (右侧审核面板, width: 320px, 仅 pending_* 状态显示)
    ├── ReviewPanel (审核决策面板)
    │   ├── StageArtifactsSummary (当前阶段产物摘要)
    │   ├── DecisionButtons
    │   │   ├── ApproveBtn (绿色，主操作)
    │   │   ├── RejectBtn (红色)
    │   │   ├── AbandonBtn (灰色)
    │   │   └── ModifyBtn (蓝色，可选：人工修改后通过)
    │   ├── CommentTextarea (审核意见，必填驳回时)
    │   └── SubmitReviewBtn
    ├── ReviewHistory (折叠列表)
    │   └── ReviewHistoryItem × N (审核人 + 决策 + 意见 + 时间)
    └── KeyboardShortcuts (快捷键提示浮层)
```

**SSE 事件处理流程**（`useCaseEvents` composable）：
```typescript
// composables/useCaseEvents.ts
export function useCaseEvents(caseId: Ref<string>) {
  const events = ref<PipelineEvent[]>([])
  const isConnected = ref(false)
  const lastEventId = ref<string | null>(null)
  const reconnectAttempt = ref(0)
  let abortController: AbortController | null = null
  let heartbeatTimer: ReturnType<typeof setTimeout> | null = null

  const HEARTBEAT_TIMEOUT = 45_000   // 45s 无心跳 → 重连
  const MAX_RECONNECT_ATTEMPTS = 5
  const BASE_RECONNECT_DELAY = 1_000  // 1s 起始，指数退避

  function connect() {
    abortController = new AbortController()
    resetHeartbeat()
    isConnected.value = true

    fetchEventSource(`/api/v1/cases/${caseId.value}/events`, {
      signal: abortController.signal,
      headers: {
        Authorization: `Bearer ${getToken()}`,
        ...(lastEventId.value ? { 'Last-Event-ID': lastEventId.value } : {}),
      },
      onmessage(ev) {
        resetHeartbeat()
        reconnectAttempt.value = 0
        if (ev.event === 'heartbeat') return
        if (ev.id) lastEventId.value = ev.id

        const event: PipelineEvent = JSON.parse(ev.data)
        // 去重
        if (events.value.some(e => e.seq === event.seq)) return
        events.value.push(event)

        // 事件分发
        switch (event.event_type) {
          case 'stage_change':
            caseDetail.value!.status = event.data.status
            caseDetail.value!.current_stage = event.data.stage
            break
          case 'review_request':
            caseDetail.value!.pending_review = event.data
            break
          case 'agent_output':
            // 追加到实时日志
            break
          case 'iteration_update':
            caseDetail.value!.review_iterations = event.data.round
            break
          case 'cost_update':
            caseDetail.value!.cost = event.data
            break
          case 'completed':
            caseDetail.value!.status = 'completed'
            disconnect()
            break
          case 'error':
            toast.error(event.data.message)
            break
        }
      },
      onerror(err) {
        isConnected.value = false
        if (reconnectAttempt.value >= MAX_RECONNECT_ATTEMPTS) {
          throw err // 放弃重连
        }
        const delay = BASE_RECONNECT_DELAY * Math.pow(2, reconnectAttempt.value)
        reconnectAttempt.value++
        return delay // fetchEventSource 自动重试
      },
      onclose() {
        isConnected.value = false
      },
    })
  }

  function resetHeartbeat() {
    clearTimeout(heartbeatTimer!)
    heartbeatTimer = setTimeout(() => {
      disconnect()
      connect()
    }, HEARTBEAT_TIMEOUT)
  }

  function disconnect() {
    abortController?.abort()
    clearTimeout(heartbeatTimer!)
    isConnected.value = false
  }

  onMounted(() => connect())
  onUnmounted(() => disconnect())

  return { events, isConnected, connect, disconnect }
}
```

### D.3 PipelineView（5 阶段流水线可视化）

```
功能：水平展示 5 阶段状态 + 4 个审批门
位置：CaseDetailView 的左侧栏（垂直模式）或顶部（水平模式）
```

**StageNode Props 接口**：
```typescript
interface StageNodeProps {
  stage: 'explore' | 'plan' | 'develop' | 'review' | 'test'
  status: StageStatus  // 'pending' | 'in_progress' | 'completed' | 'failed'
  icon: Component       // 对应 Lucide 图标
  label: string
  duration?: number     // 秒
  tokens?: { input: number; output: number }
  cost?: number         // USD
}

// HumanGate Props
interface HumanGateProps {
  stage: string
  isActive: boolean     // 当前是否等待审核
  decision?: 'approve' | 'reject' | 'abandon' | null
}
```

### D.4 DiffViewer（代码差异查看器）

```
功能：基于 Monaco Editor 的 Unified Diff 查看器
技术：@monaco-editor/vue + 自定义 diff 语言高亮
```

**关键实现**：
```typescript
// DiffViewer.vue props
interface DiffViewerProps {
  originalCode: string       // 原始代码
  modifiedCode: string       // 修改后代码
  fileName: string           // 文件名
  language: string           // Monaco 语言 ID (c/cpp/python/asm)
  findings?: ReviewFinding[] // 审核发现（行号高亮）
  readOnly?: boolean         // 默认 true
}

// ReviewFinding 高亮映射
const SEVERITY_DECORATIONS: Record<Severity, DecorationOptions> = {
  critical: { className: 'bg-red-200 dark:bg-red-900/40', glyphMarginClassName: 'critical-glyph' },
  major: { className: 'bg-orange-200 dark:bg-orange-900/40', glyphMarginClassName: 'major-glyph' },
  minor: { className: 'bg-yellow-100 dark:bg-yellow-900/30', glyphMarginClassName: 'minor-glyph' },
  suggestion: { className: 'bg-blue-50 dark:bg-blue-900/20', glyphMarginClassName: 'suggestion-glyph' },
}

// 左侧文件树（多文件补丁时）
interface FileTreeNode {
  path: string
  type: 'added' | 'modified' | 'deleted'
  additions: number
  deletions: number
  children?: FileTreeNode[]
}
```

---

## 附录 E. 关键后端模块实现细节

### E.1 PipelineState 完整定义

```python
# pipeline/state.py
from typing import Annotated, Any, Literal, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class StageStatus(str):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class PipelineState(BaseModel):
    """LangGraph Pipeline 共享状态 — 编排状态与产物引用分离"""

    # === 案例标识 ===
    case_id: str
    target_repo: Literal["linux", "qemu", "opensbi", "gcc", "llvm"]
    title: str = ""

    # === 编排状态 ===
    current_stage: Literal[
        "explore", "plan", "develop", "review", "test",
        "human_gate_explore", "human_gate_plan",
        "human_gate_code", "human_gate_test",
        "completed", "abandoned", "escalated"
    ] = "explore"

    stage_statuses: dict[str, str] = Field(default_factory=lambda: {
        "explore": "pending", "plan": "pending",
        "develop": "pending", "review": "pending", "test": "pending",
    })

    # === 输入 ===
    input_context: dict[str, Any] = Field(default_factory=dict)
    # 示例: {"user_hint": "检查 Zicfiss 扩展支持", "target_repo": "linux"}

    # === 产物引用（仅存储路径/ID，不存储完整数据） ===
    exploration_result_ref: Optional[str] = None    # MongoDB stage_outputs _id
    execution_plan_ref: Optional[str] = None
    development_result_ref: Optional[str] = None    # 产物目录路径
    review_verdict_ref: Optional[str] = None
    test_result_ref: Optional[str] = None

    # === 内联缓存（小型产物，避免额外 MongoDB 查询） ===
    exploration_result: Optional[dict] = None       # < 64KB 直接嵌入
    execution_plan: Optional[dict] = None
    review_verdict: Optional[dict] = None

    # === Develop ↔ Review 迭代控制 ===
    review_iterations: int = 0
    max_review_iterations: int = 3
    review_score_history: list[float] = Field(default_factory=list)
    review_history: list[dict] = Field(default_factory=list)
    # review_history 每项: {"iteration": int, "verdict": dict, "score": float, "timestamp": str}

    # === 人工审核 ===
    pending_approval_stage: Optional[str] = None
    approval_history: list[dict] = Field(default_factory=list)
    # approval_history 每项: {"stage": str, "action": str, "comment": str, "reviewer": str, "timestamp": str}

    # === 成本追踪 ===
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    estimated_cost_usd: float = 0.0
    stage_costs: dict[str, dict] = Field(default_factory=dict)
    # stage_costs 每项: {"input_tokens": int, "output_tokens": int, "cost_usd": float}

    # === 时间追踪 ===
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    stage_durations: dict[str, float] = Field(default_factory=dict)  # 秒

    # === 错误状态 ===
    last_error: Optional[str] = None
    error_stage: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 2
```

### E.2 StateGraph 完整构建

```python
# pipeline/graph.py
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.types import Command

from backend.pipeline.state import PipelineState
from backend.pipeline.nodes import (
    explore_node, plan_node, develop_node, review_node, test_node,
    human_gate_node, escalate_node,
)

def build_pipeline_graph() -> StateGraph:
    """构建 RV-Insights 5 阶段 Pipeline StateGraph"""
    builder = StateGraph(PipelineState)

    # === 注册节点 ===
    builder.add_node("explore", explore_node)
    builder.add_node("human_gate_explore", human_gate_node)
    builder.add_node("plan", plan_node)
    builder.add_node("human_gate_plan", human_gate_node)
    builder.add_node("develop", develop_node)
    builder.add_node("review", review_node)
    builder.add_node("human_gate_code", human_gate_node)
    builder.add_node("test", test_node)
    builder.add_node("human_gate_test", human_gate_node)
    builder.add_node("escalate", escalate_node)

    # === 入口 ===
    builder.set_entry_point("explore")

    # === 线性边 ===
    builder.add_edge("explore", "human_gate_explore")
    builder.add_edge("plan", "human_gate_plan")
    builder.add_edge("develop", "review")
    builder.add_edge("test", "human_gate_test")
    builder.add_edge("escalate", "human_gate_code")

    # === 条件边 — 人工审核门禁 ===
    gate_routes = [
        ("human_gate_explore", {"approve": "plan", "reject": "explore", "abandon": END}),
        ("human_gate_plan", {"approve": "develop", "reject": "plan", "abandon": END}),
        ("human_gate_code", {"approve": "test", "reject": "develop", "abandon": END}),
        ("human_gate_test", {"approve": END, "reject": "develop", "abandon": END}),
    ]
    for gate, routes in gate_routes:
        builder.add_conditional_edges(gate, route_human_decision, routes)

    # === 条件边 — Review 迭代/通过/升级 ===
    builder.add_conditional_edges("review", route_review_decision, {
        "approve": "human_gate_code",
        "reject": "develop",
        "escalate": "escalate",
    })

    return builder


async def compile_graph(checkpointer: AsyncPostgresSaver) -> StateGraph:
    """编译 Pipeline 图，注入持久化检查点"""
    builder = build_pipeline_graph()
    # interrupt_before: 在人工审核节点前自动暂停
    compiled = builder.compile(
        checkpointer=checkpointer,
        interrupt_before=[
            "human_gate_explore",
            "human_gate_plan",
            "human_gate_code",
            "human_gate_test",
        ],
    )
    return compiled
```

### E.3 事件发布器完整实现

```python
# events/publisher.py
import json
from datetime import datetime, timezone
from pydantic import BaseModel
import redis.asyncio as aioredis

class PipelineEvent(BaseModel):
    """Pipeline SSE 事件 — 通过 Redis Pub/Sub + Stream 传递"""
    seq: int
    case_id: str
    event_type: str  # stage_change | agent_output | review_request | iteration_update | cost_update | error | completed
    data: dict
    timestamp: str


class EventPublisher:
    """Agent 事件发布器 — 桥接 LangGraph 节点到 SSE 端点

    双通道设计:
    - Pub/Sub: 实时推送到在线客户端 (fire-and-forget)
    - Stream: 持久化事件历史 (客户端重连恢复)
    """

    def __init__(self, redis: aioredis.Redis):
        self.redis = redis
        self._seq_counters: dict[str, int] = {}
        self._stream_maxlen = 500  # 每个 case 保留最近 500 条事件

    async def publish(
        self,
        case_id: str,
        event_type: str,
        data: dict,
        *,
        persist: bool = True,  # 是否写入 Stream (heartbeat 等不持久化)
    ) -> PipelineEvent:
        """发布事件到 Redis"""
        # 递增序列号
        seq = self._seq_counters.get(case_id, 0) + 1
        self._seq_counters[case_id] = seq

        event = PipelineEvent(
            seq=seq,
            case_id=case_id,
            event_type=event_type,
            data=data,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        event_json = event.model_dump_json()

        # Channel 1: Pub/Sub (实时)
        await self.redis.publish(f"case:{case_id}:events", event_json)

        # Channel 2: Stream (持久化恢复)
        if persist:
            await self.redis.xadd(
                f"case:{case_id}:stream",
                {"event": event_json},
                maxlen=self._stream_maxlen,
            )

        return event

    async def publish_stage_change(
        self, case_id: str, stage: str, status: str, **extra
    ) -> PipelineEvent:
        """便捷方法：发布阶段状态变更"""
        return await self.publish(case_id, "stage_change", {
            "stage": stage,
            "status": status,  # "in_progress" | "completed" | "failed"
            **extra,
        })

    async def publish_agent_output(
        self, case_id: str, output_type: str, content: str, **extra
    ) -> PipelineEvent:
        """便捷方法：发布 Agent 输出"""
        return await self.publish(case_id, "agent_output", {
            "type": output_type,  # "thinking" | "tool_call" | "tool_result" | "plan_update"
            "content": content,
            **extra,
        })

    async def publish_review_request(
        self, case_id: str, stage: str, artifacts_summary: dict
    ) -> PipelineEvent:
        """便捷方法：发布审核请求"""
        return await self.publish(case_id, "review_request", {
            "stage": stage,
            "artifacts_summary": artifacts_summary,
        })

    async def publish_error(
        self, case_id: str, message: str, recoverable: bool = True, **extra
    ) -> PipelineEvent:
        """便捷方法：发布错误"""
        return await self.publish(case_id, "error", {
            "message": message,
            "recoverable": recoverable,
            **extra,
        })

    async def publish_heartbeat(self, case_id: str) -> None:
        """发布心跳（不持久化）"""
        await self.publish(case_id, "heartbeat", {}, persist=False)

    async def get_events_since(
        self, case_id: str, last_seq: int
    ) -> list[PipelineEvent]:
        """重连恢复：获取 last_seq 之后的所有事件"""
        raw = await self.redis.xrange(
            f"case:{case_id}:stream",
            min=f"{last_seq + 1}-0",  # Stream ID 格式
            max="+",
            count=500,
        )
        events = []
        for msg_id, fields in raw:
            event_json = fields.get(b"event", fields.get("event", "{}"))
            if isinstance(event_json, bytes):
                event_json = event_json.decode()
            try:
                events.append(PipelineEvent.model_validate_json(event_json))
            except Exception:
                continue
        return events

    async def cleanup_case(self, case_id: str) -> None:
        """清理 case 相关 Redis 数据"""
        await self.redis.delete(f"case:{case_id}:stream")
        self._seq_counters.pop(case_id, None)
```

### E.4 ClaudeAgentAdapter 完整实现

```python
# adapters/claude_adapter.py
import asyncio
import signal
from typing import AsyncIterator
from claude_agent_sdk import query, ClaudeAgentOptions

from backend.adapters.base import AgentAdapter, AgentEvent

class ClaudeAgentAdapter(AgentAdapter):
    """Claude Agent SDK 适配器 — 子进程模型

    关键实现决策:
    - Claude Agent SDK 每次 query() 启动独立子进程
    - 通过 asyncio.subprocess 管理进程生命周期
    - cancel() 通过 SIGTERM → SIGKILL 优雅终止
    - 超时控制使用 asyncio.timeout + 进程级超时
    """

    def __init__(
        self,
        allowed_tools: list[str],
        permission_mode: str = "acceptEdits",
        max_turns: int = 50,
        timeout_seconds: int = 1800,  # 30 分钟
        model: str = "claude-sonnet-4-20250514",
        system_prompt: str = "",
    ):
        self.allowed_tools = allowed_tools
        self.permission_mode = permission_mode
        self.max_turns = max_turns
        self.timeout_seconds = timeout_seconds
        self.model = model
        self.system_prompt = system_prompt
        self._current_task: asyncio.Task | None = None

    async def execute(
        self,
        prompt: str,
        context: dict | None = None,
        working_dir: str | None = None,
    ) -> AsyncIterator[AgentEvent]:
        """执行 Claude Agent 任务，流式返回事件"""
        options = ClaudeAgentOptions(
            cwd=working_dir or "/tmp",
            allowed_tools=self.allowed_tools,
            permission_mode=self.permission_mode,
            max_turns=self.max_turns,
            model=self.model,
            system_prompt=self.system_prompt,
            # 通过 context 传递额外数据（如 session_id）
            **(context or {}),
        )

        try:
            async with asyncio.timeout(self.timeout_seconds):
                async for message in query(prompt=prompt, options=options):
                    event = self._convert_message(message)
                    if event:
                        yield event
        except asyncio.TimeoutError:
            yield AgentEvent(
                event_type="error",
                data={
                    "message": f"Agent execution timed out after {self.timeout_seconds}s",
                    "recoverable": True,
                    "error_type": "timeout",
                },
            )
        except Exception as e:
            yield AgentEvent(
                event_type="error",
                data={
                    "message": str(e),
                    "recoverable": False,
                    "error_type": type(e).__name__,
                },
            )

    async def cancel(self) -> None:
        """取消正在执行的任务"""
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()
            try:
                await self._current_task
            except asyncio.CancelledError:
                pass

    def _convert_message(self, message) -> AgentEvent | None:
        """将 Claude Agent SDK 消息转换为统一的 AgentEvent"""
        msg_type = getattr(message, "type", "unknown")

        type_map = {
            "assistant": "thinking",
            "tool_use": "tool_call",
            "tool_result": "tool_result",
            "result": "output",
            "system": "system",
            "user": "input",
        }

        event_type = type_map.get(msg_type, "output")

        # 提取内容
        content = getattr(message, "content", None)
        if content is None:
            if hasattr(message, "text"):
                content = message.text
            elif hasattr(message, "result"):
                content = message.result
            else:
                content = str(message)

        # 提取工具调用详情
        extra = {}
        if msg_type == "tool_use":
            extra["tool_name"] = getattr(message, "name", "unknown")
            extra["tool_input"] = getattr(message, "input", {})
        elif msg_type == "tool_result":
            extra["tool_use_id"] = getattr(message, "tool_use_id", "")
            # 大结果截断
            if isinstance(content, str) and len(content) > 5000:
                extra["truncated"] = True
                content = content[:5000] + "\n... (truncated)"

        return AgentEvent(
            event_type=event_type,
            data={
                "type": msg_type,
                "content": content,
                **extra,
            },
        )
```

### E.5 route/cases.py SSE 端点完整实现

```python
# route/cases.py
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Header
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
import redis.asyncio as aioredis
from typing import Optional

from backend.events.publisher import EventPublisher, PipelineEvent
from backend.user.dependencies import get_current_user, require_role, User
from backend.db.mongo import get_db
from backend.pipeline.graph import get_compiled_graph

router = APIRouter(prefix="/cases", tags=["cases"])

# ═══════════════════════════════════════════════════════
# REST Endpoints
# ═══════════════════════════════════════════════════════

@router.post("", status_code=201)
async def create_case(
    body: CreateCaseRequest,
    user: User = Depends(require_role("admin", "user")),
    db=Depends(get_db),
):
    """创建新案例"""
    case_doc = {
        "title": body.title,
        "status": "created",
        "target_repo": body.target_repo,
        "input_context": body.input_context,
        "created_by": user.id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "review_iterations": 0,
        "cost": {"input_tokens": 0, "output_tokens": 0, "estimated_usd": 0.0},
    }
    result = await db.contribution_cases.insert_one(case_doc)
    return {"id": str(result.inserted_id), **case_doc}


@router.get("")
async def list_cases(
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    target_repo: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """案例列表（分页/筛选/搜索）"""
    query_filter = {}
    if status:
        query_filter["status"] = status
    if target_repo:
        query_filter["target_repo"] = target_repo
    if search:
        query_filter["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"input_context.user_hint": {"$regex": search, "$options": "i"}},
        ]

    total = await db.contribution_cases.count_documents(query_filter)
    sort_dir = -1 if sort_order == "desc" else 1
    cursor = db.contribution_cases.find(query_filter) \
        .sort(sort_by, sort_dir) \
        .skip((page - 1) * page_size) \
        .limit(page_size)

    items = []
    async for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        items.append(doc)

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, (total + page_size - 1) // page_size),
    }


@router.get("/{case_id}")
async def get_case(
    case_id: str,
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """案例详情"""
    from bson import ObjectId
    doc = await db.contribution_cases.find_one({"_id": ObjectId(case_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Case not found")
    doc["id"] = str(doc.pop("_id"))
    return doc


@router.post("/{case_id}/start")
async def start_pipeline(
    case_id: str,
    user: User = Depends(require_role("admin", "user")),
    db=Depends(get_db),
):
    """启动 Pipeline — 异步执行 LangGraph"""
    from bson import ObjectId
    import asyncio

    case = await db.contribution_cases.find_one({"_id": ObjectId(case_id)})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    if case["status"] != "created":
        raise HTTPException(status_code=409, detail="Case is not in 'created' status")

    # 更新状态
    await db.contribution_cases.update_one(
        {"_id": ObjectId(case_id)},
        {"$set": {"status": "exploring", "updated_at": datetime.utcnow()}},
    )

    # 异步启动 LangGraph Pipeline（后台任务，不阻塞 HTTP 响应）
    graph = await get_compiled_graph()
    config = {"configurable": {"thread_id": case_id}}

    initial_state = {
        "case_id": case_id,
        "target_repo": case["target_repo"],
        "title": case.get("title", ""),
        "input_context": case.get("input_context", {}),
        "started_at": datetime.utcnow().isoformat(),
    }

    asyncio.create_task(
        graph.ainvoke(initial_state, config=config)
    )

    return {"case_id": case_id, "status": "exploring"}


# ═══════════════════════════════════════════════════════
# SSE Event Stream
# ═══════════════════════════════════════════════════════

@router.get("/{case_id}/events")
async def case_events(
    case_id: str,
    request: Request,
    last_event_id: Optional[int] = Header(None, alias="Last-Event-ID"),
    user: User = Depends(get_current_user),
):
    """SSE 事件流 — Redis Pub/Sub + Stream 双通道"""
    publisher: EventPublisher = request.app.state.event_publisher
    redis: aioredis.Redis = request.app.state.redis

    async def event_generator():
        # Phase 1: 重连恢复 — 发送断连期间丢失的事件
        if last_event_id is not None:
            missed = await publisher.get_events_since(case_id, last_event_id)
            for event in missed:
                yield {
                    "id": str(event.seq),
                    "event": event.event_type,
                    "data": event.model_dump_json(),
                }

        # Phase 2: 实时订阅 Redis Pub/Sub
        pubsub = redis.pubsub()
        await pubsub.subscribe(f"case:{case_id}:events")

        # Phase 3: 心跳任务 (30s 间隔)
        heartbeat_task = asyncio.create_task(_send_heartbeats(publisher, case_id))

        try:
            async for message in pubsub.listen():
                if message["type"] != "message":
                    continue

                data = message["data"]
                if isinstance(data, bytes):
                    data = data.decode()

                try:
                    event = PipelineEvent.model_validate_json(data)
                except Exception:
                    continue

                yield {
                    "id": str(event.seq),
                    "event": event.event_type,
                    "data": data,
                }

                # Pipeline 完成时主动断开
                if event.event_type == "completed":
                    break

        except asyncio.CancelledError:
            pass
        finally:
            heartbeat_task.cancel()
            try:
                await heartbeat_task
            except asyncio.CancelledError:
                pass
            await pubsub.unsubscribe(f"case:{case_id}:events")
            await pubsub.close()

    return EventSourceResponse(event_generator())


async def _send_heartbeats(publisher: EventPublisher, case_id: str):
    """每 30 秒发送心跳保持连接"""
    while True:
        await asyncio.sleep(30)
        await publisher.publish_heartbeat(case_id)
```

### E.6 route/reviews.py 审核端点实现

```python
# route/reviews.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Literal, Optional
from uuid import uuid4
from datetime import datetime

from backend.user.dependencies import get_current_user, User
from backend.db.mongo import get_db
from backend.pipeline.graph import get_compiled_graph
from langgraph.types import Command

router = APIRouter(tags=["reviews"])

class ReviewDecision(BaseModel):
    """人工审核决策"""
    action: Literal["approve", "reject", "abandon"]
    comment: str = Field(default="", max_length=2000)
    review_id: Optional[str] = None  # 幂等性 key

@router.post("/cases/{case_id}/review")
async def submit_review(
    case_id: str,
    decision: ReviewDecision,
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """提交人工审核决策，恢复 Pipeline 执行

    幂等性保证：通过 review_id 防止重复提交
    """
    from bson import ObjectId

    # 1. 幂等性检查
    if decision.review_id:
        existing = await db.human_reviews.find_one({"review_id": decision.review_id})
        if existing:
            return {"status": "ok", "message": "Review already submitted (idempotent)", "review_id": decision.review_id}

    # 2. 状态检查
    case = await db.contribution_cases.find_one({"_id": ObjectId(case_id)})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    if not case["status"].startswith("pending_"):
        raise HTTPException(status_code=409, detail=f"Case is not pending review (status: {case['status']})")

    # 3. 记录审核
    review_doc = {
        "review_id": decision.review_id or str(uuid4()),
        "case_id": case_id,
        "stage": case["status"].replace("pending_", "").replace("_review", ""),
        "action": decision.action,
        "comment": decision.comment,
        "reviewer": user.username,
        "reviewer_id": user.id,
        "created_at": datetime.utcnow(),
    }
    await db.human_reviews.insert_one(review_doc)

    # 4. 更新案例状态
    stage_map = {
        "pending_explore_review": ("explore", decision.action),
        "pending_plan_review": ("plan", decision.action),
        "pending_code_review": ("code", decision.action),
        "pending_test_review": ("test", decision.action),
    }
    stage, action = stage_map.get(case["status"], (None, None))

    if action == "abandon":
        await db.contribution_cases.update_one(
            {"_id": ObjectId(case_id)},
            {"$set": {"status": "abandoned", "updated_at": datetime.utcnow()}},
        )

    # 5. 恢复 Pipeline（通过 LangGraph Command）
    graph = await get_compiled_graph()
    config = {"configurable": {"thread_id": case_id}}

    await graph.ainvoke(
        Command(resume={
            "action": decision.action,
            "comment": decision.comment,
            "reviewer": user.username,
        }),
        config=config,
    )

    return {
        "status": "ok",
        "message": f"Pipeline resumed with action: {decision.action}",
        "review_id": review_doc["review_id"],
    }


@router.get("/cases/{case_id}/history")
async def get_review_history(
    case_id: str,
    user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """获取案例的审核历史"""
    cursor = db.human_reviews.find({"case_id": case_id}).sort("created_at", -1)
    history = []
    async for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        history.append(doc)
    return {"case_id": case_id, "reviews": history}
```

---

## 附录 F. 完整 API 请求/响应 Schema

### F.1 Auth

```python
# POST /api/v1/auth/login
# Request:
{
    "username": "admin",
    "password": "admin123"
}
# Response 200:
{
    "user": {
        "id": "user_xxx",
        "fullname": "Administrator",
        "email": "admin@localhost",
        "role": "admin",
        "is_active": true,
        "created_at": "2026-04-25T10:00:00Z",
        "updated_at": "2026-04-25T10:00:00Z",
        "last_login_at": "2026-04-29T08:00:00Z"
    },
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "dGhpcyBpcyBhIHJlZnJl...",
    "token_type": "Bearer"
}
# Response 401: {"detail": "Invalid credentials"}

# POST /api/v1/auth/register
# Request:
{
    "fullname": "New User",
    "email": "user@example.com",
    "password": "securepass123",
    "username": "newuser"  // 可选，默认用邮箱前缀
}
# Response 201: 同 login 返回 TokenResponse

# GET /api/v1/auth/status
# Response 200:
{
    "authenticated": true,
    "auth_provider": "local",
    "user": { ... }  // AuthUser
}
# Response 200 (未登录):
{
    "authenticated": false,
    "auth_provider": "local",
    "user": null
}

# POST /api/v1/auth/refresh
# Request: {"refresh_token": "dGhpcyBpcyBhIHJlZnJl..."}
# Response 200: {"access_token": "new_eyJhbGciOi..."}
# Response 401: {"detail": "Invalid refresh token"}

# POST /api/v1/auth/logout
# Response 200: {"ok": true}
```

### F.2 Cases

```python
# POST /api/v1/cases
# Request:
{
    "title": "Add Zicfiss support to Linux kernel",
    "target_repo": "linux",
    "input_context": {
        "user_hint": "Zicfiss extension was ratified on 2025-06-15. Check if kernel support exists.",
        "target_repo": "linux",
        "contribution_type": "isa_extension"
    }
}
# Response 201:
{
    "id": "60d5f9f8b8e5e7a1c8f4e3d2",
    "title": "Add Zicfiss support to Linux kernel",
    "status": "created",
    "target_repo": "linux",
    "created_at": "2026-04-29T08:00:00Z",
    "updated_at": "2026-04-29T08:00:00Z"
}

# GET /api/v1/cases?status=exploring&page=1&page_size=20
# Response 200:
{
    "items": [...],
    "total": 42,
    "page": 1,
    "page_size": 20,
    "total_pages": 3
}

# GET /api/v1/cases/{id}
# Response 200:
{
    "id": "60d5f9f8...",
    "title": "...",
    "status": "exploring",
    "target_repo": "linux",
    "input_context": {...},
    "exploration_result": null,
    "execution_plan": null,
    "development_result": null,
    "review_verdict": null,
    "test_result": null,
    "review_iterations": 0,
    "cost": {"input_tokens": 5234, "output_tokens": 1892, "estimated_usd": 0.04},
    "created_at": "...",
    "updated_at": "..."
}

# POST /api/v1/cases/{id}/start
# Response 200: {"case_id": "...", "status": "exploring"}
# Response 409: {"detail": "Case is not in 'created' status"}

# GET /api/v1/cases/{id}/artifacts/{stage}
# stage ∈ {explore, plan, develop, review, test}
# Response 200:
{
    "stage": "explore",
    "artifacts": {
        "contribution_type": "isa_extension",
        "target_files": ["arch/riscv/kernel/cpufeature.c"],
        "evidence": [{"source": "patchwork", "url": "...", "content": "..."}],
        "feasibility_score": 0.85
    },
    "files": [
        {"path": "exploration_report.json", "size": 4096, "created_at": "..."}
    ]
}
```

### F.3 SSE Events (GET /api/v1/cases/{id}/events)

```
# event: stage_change
# id: 1
# data: {"seq":1,"case_id":"...","event_type":"stage_change","data":{"stage":"explore","status":"in_progress"},"timestamp":"..."}

# event: agent_output
# id: 2
# data: {"seq":2,...,"event_type":"agent_output","data":{"type":"thinking","content":"正在分析 Patchwork API..."},...}

# event: agent_output
# id: 3
# data: {"seq":3,...,"event_type":"agent_output","data":{"type":"tool_call","tool_name":"web_search","tool_input":{"query":"..."}},...}

# event: agent_output
# id: 4
# data: {"seq":4,...,"event_type":"agent_output","data":{"type":"tool_result","content":"Found 23 patches..."},...}

# event: stage_change
# id: 5
# data: {"seq":5,...,"event_type":"stage_change","data":{"stage":"explore","status":"completed","duration_seconds":45.2},"timestamp":"..."}

# event: review_request
# id: 6
# data: {"seq":6,...,"event_type":"review_request","data":{"stage":"explore","artifacts_summary":{"type":"isa_extension","score":0.85}},...}

# event: heartbeat
# data: {}

# event: completed
# id: 42
# data: {"seq":42,...,"event_type":"completed","data":{"total_cost_usd":1.59,"total_duration_seconds":482}},...}
```

---

## 附录 G. 完整 MongoDB 文档 Schema

### G.1 contribution_cases（案例主集合）

```json
{
    "_id": "ObjectId",
    "title": "Add Zicfiss support to Linux kernel",
    "status": "exploring",
    "target_repo": "linux",
    "created_by": "user_xxx",
    "input_context": {
        "user_hint": "Check Zicfiss extension support",
        "target_repo": "linux",
        "contribution_type": "isa_extension"
    },
    "exploration_result": {
        "contribution_type": "isa_extension",
        "title": "Add Zicfiss (Shadow Stack) Support to Linux Kernel",
        "summary": "The Zicfiss extension was ratified on 2025-06-15...",
        "target_repo": "linux",
        "target_files": [
            "arch/riscv/kernel/cpufeature.c",
            "arch/riscv/include/asm/hwcap.h",
            "arch/riscv/Kconfig"
        ],
        "evidence": [
            {
                "source": "patchwork",
                "url": "https://patchwork.kernel.org/...",
                "content": "No existing patches for Zicfiss",
                "relevance": 0.95
            }
        ],
        "feasibility_score": 0.85,
        "estimated_complexity": "medium",
        "upstream_status": "likely_accepted"
    },
    "execution_plan": {
        "dev_steps": [
            {
                "id": "step_1",
                "description": "Add Zicfiss hwcap bit definition",
                "target_files": ["arch/riscv/include/asm/hwcap.h"],
                "expected_changes": "Add #define COMPAT_HWCAP_ISA_ZICFISS",
                "risk_level": "low",
                "dependencies": []
            }
        ],
        "test_cases": [
            {
                "id": "test_1",
                "name": "Verify /proc/cpuinfo shows zicfiss",
                "type": "integration",
                "description": "Boot QEMU and check cpuinfo",
                "expected_result": "zicfiss appears in /proc/cpuinfo",
                "qemu_required": true
            }
        ],
        "qemu_config": {
            "machine": "virt",
            "cpu": "rv64",
            "extra_args": "-cpu rv64,zicfiss=true"
        },
        "estimated_tokens": 8000,
        "risk_assessment": "Low risk: standard ISA extension addition"
    },
    "development_result": {
        "patch_files": ["/data/artifacts/case_001/develop/round_1/0001-riscv-Add-Zicfiss-support.patch"],
        "changed_files": [
            "arch/riscv/kernel/cpufeature.c",
            "arch/riscv/include/asm/hwcap.h",
            "arch/riscv/Kconfig"
        ],
        "commit_message": "riscv: Add Zicfiss extension support\n\nZicfiss (Shadow Stack) extension was ratified on 2025-06-15.\nThis adds hwcap registration, cpufeature detection, and Kconfig option.\n\nSigned-off-by: RV-Insights <rv-insights@example.com>",
        "change_summary": "Added hwcap bit, cpufeature entry, and Kconfig option for Zicfiss",
        "lines_added": 47,
        "lines_removed": 0
    },
    "review_verdict": {
        "approved": true,
        "findings": [
            {
                "severity": "minor",
                "category": "style",
                "file": "arch/riscv/kernel/cpufeature.c",
                "line": 245,
                "description": "Line exceeds 80 characters",
                "suggestion": "Break the riscv_isa_extension_check call across multiple lines"
            }
        ],
        "iteration": 2,
        "reviewer_model": "codex-mini-latest + checkpatch.pl",
        "summary": "All critical and major findings resolved. 1 minor style issue remains (non-blocking)."
    },
    "test_result": {
        "passed": true,
        "total_tests": 3,
        "passed_tests": 3,
        "failed_tests": 0,
        "test_log_path": "/data/artifacts/case_001/test/test_output.log",
        "coverage_percent": null,
        "qemu_version": "QEMU emulator version 9.0.0",
        "failure_details": []
    },
    "review_iterations": 2,
    "max_review_iterations": 3,
    "approval_history": [
        {
            "stage": "explore",
            "action": "approve",
            "comment": "Feasibility score 0.85, evidence complete.",
            "reviewer": "admin",
            "timestamp": "2026-04-29T08:30:00Z"
        }
    ],
    "cost": {
        "input_tokens": 280000,
        "output_tokens": 78000,
        "estimated_usd": 1.59
    },
    "stage_costs": {
        "explore": {"input_tokens": 50000, "output_tokens": 15000, "cost_usd": 0.35},
        "plan": {"input_tokens": 20000, "output_tokens": 8000, "cost_usd": 0.14},
        "develop": {"input_tokens": 120000, "output_tokens": 35000, "cost_usd": 0.80},
        "review": {"input_tokens": 60000, "output_tokens": 10000, "cost_usd": 0.10},
        "test": {"input_tokens": 30000, "output_tokens": 10000, "cost_usd": 0.20}
    },
    "stage_durations": {
        "explore": 45.2,
        "plan": 28.7,
        "develop": 120.5,
        "review": 35.1,
        "test": 60.3
    },
    "started_at": "2026-04-29T08:00:00Z",
    "completed_at": "2026-04-29T08:12:50Z",
    "created_at": "2026-04-29T08:00:00Z",
    "updated_at": "2026-04-29T08:12:50Z"
}
```

### G.2 human_reviews（审核记录）

```json
{
    "_id": "ObjectId",
    "review_id": "uuid-v4",
    "case_id": "60d5f9f8...",
    "stage": "explore",
    "action": "approve",
    "comment": "Feasibility score 0.85, evidence complete.",
    "reviewer": "admin",
    "reviewer_id": "user_xxx",
    "created_at": "2026-04-29T08:30:00Z"
}
```

### G.3 stage_outputs（阶段产物）

```json
{
    "_id": "ObjectId",
    "case_id": "60d5f9f8...",
    "stage": "explore",
    "round_num": null,
    "output_type": "ExplorationResult",
    "data": { /* 完整的 ExplorationResult Pydantic model */ },
    "file_paths": ["/data/artifacts/case_001/explore/exploration_report.json"],
    "created_at": "2026-04-29T08:05:00Z"
}
```

### G.4 audit_log（审计日志 — append-only）

```json
{
    "_id": "ObjectId",
    "case_id": "60d5f9f8...",
    "event_type": "pipeline_started",
    "data": {
        "target_repo": "linux",
        "initiated_by": "admin"
    },
    "user": "admin",
    "timestamp": "2026-04-29T08:00:00Z"
}
```

---

## 附录 H. Sprint 任务验收标准

### H.1 Sprint 0 验收标准

| # | 验收标准 |
|---|----------|
| 0.1 | `backend/` 目录结构完整，含所有空文件和 `__init__.py` |
| 0.2 | `uvicorn main:create_app --factory` 可启动，`/health` 返回 200 |
| 0.3 | `docker compose up -d` 所有 11 个服务 healthy |
| 0.4 | MongoDB 所有集合创建完毕，索引生效（`db.contribution_cases.getIndexes()` 确认） |
| 0.5 | PostgreSQL 连接池正常，`AsyncPostgresSaver.setup()` 创建 `checkpoints` 表 |
| 0.6 | `EventPublisher.publish()` 可写入 Redis Pub/Sub + Stream |
| 0.7 | `npm run build` 在 `web-console/` 目录成功，无错误 |

### H.2 Sprint 1 验收标准

| # | 验收标准 |
|---|----------|
| 1.1 | JWT Token 生成和验证单元测试通过（正常/过期/伪造 3 个 case） |
| 1.2 | `POST /auth/login` → 200 + TokenResponse；错误密码 → 401 |
| 1.3 | 无 token → 401 `{"detail": "Not authenticated"}`；有 token → 正常注入 `User` |
| 1.4 | admin 可 DELETE cases；user 尝试 DELETE → 403 `{"detail": "Insufficient permissions"}` |
| 1.5 | 首次启动自动创建 admin/admin123 用户；`BOOTSTRAP_UPDATE_ADMIN_PASSWORD=false` 时不覆盖 |
| 1.6 | 前端登录页可正常登录；token 过期后自动刷新；登出清空状态 |

### H.3 Sprint 2 验收标准

| # | 验收标准 |
|---|----------|
| 2.1 | ChatRunner 可接收消息，通过 asyncio.Queue 推送 SSE 事件 |
| 2.2 | `PUT /sessions` 创建会话；`GET /sessions` 返回列表；`DELETE /sessions/{id}` 删除成功 |
| 2.3 | `POST /sessions/{id}/chat` 返回 SSE 流；`POST /sessions/{id}/stop` 停止执行 |
| 2.4 | 文件上传/下载/列表 API 正常工作 |
| 2.5 | 模型 CRUD 正常；`detect-context-window` 返回正确窗口大小 |
| 2.6 | Token 统计汇总正确（按 time_range 筛选） |
| 2.7 | 前端 Chat 对话：输入消息 → SSE 流 → 渲染 Markdown + 工具调用 + 文件 |

### H.4 Sprint 3 验收标准

| # | 验收标准 |
|---|----------|
| 3.1 | `PipelineState` 模型验证通过（合法/非法字段测试）；`StateGraph` 编译无错误 |
| 3.2 | Mock ClaudeAgentAdapter 可流式返回事件；cancel() 可中断执行 |
| 3.3 | Mock OpenAIAgentAdapter 可调用并返回结构化输出 |
| 3.4 | 5 个节点函数签名正确，接收 PipelineState 返回 dict；集成到 StateGraph 无报错 |
| 3.5 | `route_review_decision` 单元测试 6 个 case 全部通过（approve/reject/escalate/convergence） |
| 3.6 | `interrupt()` 暂停 → API 提交 approve → Pipeline 前进；API 提交 reject → Pipeline 回退 |
| 3.7 | `POST /cases` 创建成功；`GET /cases/{id}` 返回详情；`POST /cases/{id}/start` 启动 Pipeline |
| 3.8 | SSE 连接 → 接收 `stage_change` → `agent_output` → `review_request` → `completed` 全部事件 |
| 3.9 | 集成测试：Mock Agent 完成 Created → Completed 完整流程（无真实 LLM 调用） |

### H.5 Sprint 4 验收标准

| # | 验收标准 |
|---|----------|
| 4.1 | Explorer 对真实 Linux 内核仓库运行，返回合法 ExplorationResult；幻觉验证通过 |
| 4.2 | Planner 输入 ExplorationResult → 输出 ExecutionPlan（含 dev_steps + test_cases） |
| 4.3 | Developer 根据 ExecutionPlan 生成 patch 文件（.patch）；canUseTool 审批回调工作 |
| 4.4 | Reviewer 发现至少 2 类问题（安全/正确性/风格）；checkpatch.pl 输出被合并到 findings |
| 4.5 | Tester 在 sandbox 中编译 + 运行 QEMU 验证（或编译验证降级方案） |
| 4.6 | 所有 Pydantic 模型序列化/反序列化测试通过（合法 JSON + 边界值 + 非法值拒绝） |
| 4.7 | Explorer/Reviewer System Prompt 英文语法正确；包含必要输出格式指令 |
| 4.8 | Patchwork API 客户端可获取 linux-riscv 项目最近的 patches |
| 4.9 | ArtifactManager 保存/加载产物路径正确；cleanup 保留最终版本 |
| 4.10 | 3 个 Claude 并发 + 5 个 OpenAI 并发可同时执行不阻塞 |
| 4.11 | 单 case 成本超 $10 → 熔断器触发 → Pipeline 升级到 human_gate |

### H.6 Sprint 5 验收标准

| # | 验收标准 |
|---|----------|
| 5.1 | 案例列表页：状态筛选正确过滤；搜索关键词匹配标题；分页正常 |
| 5.2 | 案例详情页：三栏布局正常渲染；左侧导航点击切换主内容 |
| 5.3 | PipelineView：5 个阶段状态图标正确；HumanGate 高亮显示审核中阶段 |
| 5.4 | ReviewPanel：Approve/Reject/Abandon 按钮提交 API 成功；驳回时弹出评论输入框 |
| 5.5 | DiffViewer：Monaco Editor 正确渲染 diff；ReviewFinding 行高亮正确 |
| 5.6 | ContributionCard：贡献类型图标 + 可行性评分 + 证据数量 badge 正确显示 |
| 5.7 | TestResultSummary：通过/失败/总计数字 + 进度条正确；TestLogViewer 可滚动查看日志 |
| 5.8 | useCaseEvents：SSE 连接自动重连（模拟断网→恢复）；事件去重正确 |
| 5.9 | useCaseStore：loadCase 加载案例详情；submitReview 提交审核决策 |
| 5.10 | 完整交互：创建案例 → 启动 Pipeline → SSE 推送状态 → 审核操作 → Pipeline 推进 → 完成 |

### H.7 Sprint 6 验收标准

| # | 验收标准 |
|---|----------|
| 6.1 | task-service 的 `POST /chat` 调用新 backend API 成功返回 |
| 6.2 | 输入 "ignore all previous instructions" → `detect_prompt_injection()` 返回 True |
| 6.3 | 所有 API 响应含安全头：`X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection` |
| 6.4 | 同一 IP 1 分钟内超过 100 次请求 → 429 `{"detail": "Too many requests"}` |
| 6.5 | case 创建/启动/审核/完成等操作在 `audit_log` 中记录完整 |
| 6.6 | 定时任务定时触发 → LLM 执行 → 结果通知前端 |

### H.8 Sprint 7 验收标准

| # | 验收标准 |
|---|----------|
| 7.1 | `pytest tests/unit/ -v` 全部通过，覆盖率 ≥ 80%（Pydantic 模型 95%，路由函数 90%） |
| 7.2 | `pytest tests/integration/ -v` 全部通过（testcontainers 自动启停 MongoDB+PostgreSQL） |
| 7.3 | Playwright E2E 测试：登录→创建案例→启动 Pipeline→查看详情 全流程无报错 |
| 7.4 | 至少 3 个 eval case 可运行；输出 eval_report.json 含 precision/recall 指标 |
| 7.5 | `docker compose up -d` 生产模式 nginx 反向代理正常工作；HTTPS 可选配置 |
| 7.6 | `docs/deploy.md` 包含完整部署步骤；`docs/api.md` 包含所有端点文档 |

---

## 附录 I. 错误处理与重试策略

### I.1 错误分类与处理

```python
from enum import Enum

class ErrorCategory(str, Enum):
    TRANSIENT = "transient"        # 瞬时错误 → 重试
    MODEL = "model"                # 模型错误 → 降级
    LOGIC = "logic"                # 逻辑错误 → 记录 + 升级
    RESOURCE = "resource"          # 资源错误 → 等待 + 重试
    FATAL = "fatal"                # 致命错误 → 标记失败

ERROR_HANDLING_MAP = {
    ErrorCategory.TRANSIENT: {
        "strategy": "exponential_backoff",
        "max_retries": 3,
        "base_delay": 2,           # 秒
        "max_delay": 30,
        "examples": ["API timeout", "Network jitter", "Rate limit (429)"],
    },
    ErrorCategory.MODEL: {
        "strategy": "fallback_chain",
        "fallback_models": {
            "claude-sonnet-4": "claude-haiku-4",
            "gpt-4o": "gpt-4o-mini",
            "codex-mini": "gpt-4o",
        },
        "examples": ["Claude API rate limited", "Model unavailable"],
    },
    ErrorCategory.LOGIC: {
        "strategy": "record_and_escalate",
        "action": "log → notify → escalate to human_gate",
        "examples": ["Agent output format mismatch", "JSON parse failure after retries"],
    },
    ErrorCategory.RESOURCE: {
        "strategy": "wait_and_retry",
        "max_wait": 300,           # 秒
        "examples": ["QEMU sandbox unavailable", "PostgreSQL connection pool exhausted"],
    },
    ErrorCategory.FATAL: {
        "strategy": "mark_failed",
        "action": "log → set status=failed → notify",
        "examples": ["Target repo not found", "Invalid API key"],
    },
}
```

### I.2 tenacity 重试装饰器配置

```python
from tenacity import (
    retry, stop_after_attempt, wait_exponential,
    retry_if_exception_type, before_sleep_log,
)
import httpx
from loguru import logger

# LLM API 重试（瞬时错误）
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception_type((
        httpx.TimeoutException,
        httpx.HTTPStatusError,  # 429, 5xx
        ConnectionError,
    )),
    before_sleep=before_sleep_log(logger, "WARNING"),
)
async def call_llm_api_with_retry(client, **kwargs):
    return await client.post(**kwargs)

# 数据库操作重试（瞬时连接问题）
@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=0.5, min=1, max=10),
    retry=retry_if_exception_type((
        ConnectionError,
        TimeoutError,
    )),
)
async def db_operation_with_retry(operation, *args, **kwargs):
    return await operation(*args, **kwargs)
```

### I.3 Agent 节点统一错误处理包装

```python
# pipeline/nodes/_error_handler.py
from functools import wraps
from backend.events.publisher import EventPublisher

def agent_node_error_handler(stage_name: str):
    """Agent 节点统一错误处理装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(state, *args, **kwargs):
            publisher = get_event_publisher()
            case_id = state.get("case_id", "unknown")

            try:
                await publisher.publish_stage_change(case_id, stage_name, "in_progress")
                result = await func(state, *args, **kwargs)
                await publisher.publish_stage_change(case_id, stage_name, "completed")
                return result

            except asyncio.TimeoutError:
                await publisher.publish_error(case_id, f"{stage_name} timed out", recoverable=True)
                return {
                    "last_error": f"{stage_name} timed out",
                    "error_stage": stage_name,
                    "retry_count": state.get("retry_count", 0) + 1,
                }

            except Exception as e:
                await publisher.publish_error(case_id, str(e), recoverable=False)
                logger.exception(f"{stage_name}_failed", case_id=case_id)
                return {
                    "last_error": str(e),
                    "error_stage": stage_name,
                    "current_stage": f"human_gate_{stage_name}",
                }

        return wrapper
    return decorator

# 使用示例
@agent_node_error_handler("explore")
async def explore_node(state: PipelineState) -> dict:
    # ... 正常逻辑
    pass
```

---

## 附录 J. Nginx 反向代理详细配置

```nginx
# nginx/nginx.conf
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 2048;
    use epoll;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # === 日志格式 ===
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    'rt=$request_time uct="$upstream_connect_time" '
                    'uht="$upstream_header_time" urt="$upstream_response_time"';

    access_log /var/log/nginx/access.log main;

    # === 性能优化 ===
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;  # 文件上传限制

    # === Gzip 压缩 ===
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript
               text/xml application/xml application/xml+rss text/javascript
               image/svg+xml;

    # === 后端上游 ===
    upstream backend {
        server backend:8000;
        keepalive 32;  # 连接池
    }

    # === 前端静态资源 ===
    server {
        listen 80;
        server_name localhost;

        # 健康检查
        location /health {
            return 200 '{"status":"ok"}';
            add_header Content-Type application/json;
        }

        # 前端 SPA
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
            index index.html;

            # 静态资源缓存
            location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
                expires 30d;
                add_header Cache-Control "public, immutable";
            }
        }

        # === API 反向代理 ===
        location /api/ {
            proxy_pass http://backend;
            proxy_http_version 1.1;

            # 请求头转发
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # 连接池复用
            proxy_set_header Connection "";

            # 超时配置
            proxy_connect_timeout 10s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # === SSE 事件流专用配置 ===
        location ~ ^/api/v1/(cases|sessions)/.*/events$ {
            proxy_pass http://backend;
            proxy_http_version 1.1;

            # SSE 必需：禁用所有缓冲
            proxy_buffering off;
            proxy_cache off;
            proxy_request_buffering off;

            # SSE 必需：清除 Connection 头
            proxy_set_header Connection '';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

            # SSE 长连接：24 小时超时
            proxy_read_timeout 86400s;
            proxy_send_timeout 86400s;

            # 禁用分块传输编码
            chunked_transfer_encoding off;
        }

        # === SSE 事件流（sessions 通知） ===
        location ~ ^/api/v1/sessions/notifications$ {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_buffering off;
            proxy_cache off;
            proxy_set_header Connection '';
            proxy_set_header Host $host;
            proxy_read_timeout 86400s;
            chunked_transfer_encoding off;
        }
    }

    # === HTTPS (可选，生产环境使用) ===
    # server {
    #     listen 443 ssl http2;
    #     server_name your-domain.com;
    #
    #     ssl_certificate /etc/nginx/ssl/fullchain.pem;
    #     ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    #     ssl_protocols TLSv1.2 TLSv1.3;
    #     ssl_ciphers HIGH:!aNULL:!MD5;
    #
    #     # ... 同上的 location 配置 ...
    # }
}
```

---

## 12. 跨领域关注点

### 12.1 双模式并发安全

Chat 模式和 Pipeline 模式在同一 FastAPI 进程中运行，需确保资源隔离：

```python
# 并发控制边界
class ConcurrencyBoundary:
    _chat_runners: dict[str, ChatRunner] = {}
    _claude_semaphore = asyncio.Semaphore(3)   # Chat + Pipeline 共享
    _openai_semaphore = asyncio.Semaphore(5)
    _qemu_semaphore = asyncio.Semaphore(2)
```

### 12.2 LangGraph Checkpoint 恢复

服务重启后，正在执行的 Pipeline 通过 PostgreSQL 检查点自动恢复。启动时查询所有非终态 case，调用 `graph.aget_state(config)` 获取最新 checkpoint，若 `state.next` 非空则 `graph.ainvoke(None, config=config)` 从断点继续执行。

### 12.3 前端路由守卫对齐

ScienceClaw 原有路由依赖 `useAuth` composable。RV-Insights 新增 `/cases` 路由需在 `router.beforeEach` 中添加 admin 权限检查：
- `/cases/:id/delete` 等操作 → 非 admin 角色重定向到 `/cases`
- `/cases` 列表页 → 任何已认证用户可访问

### 12.4 环境一致性保证

| 关注点 | 开发环境 | 生产环境 | 验证方式 |
|--------|----------|----------|----------|
| Python | 3.12 | 3.12 (Docker) | `python --version` |
| Node | 20 | 20 (Docker) | `node --version` |
| MongoDB | 7.0 | 7.0 (Docker) | `mongosh --version` |
| PostgreSQL | 16 | 16 (Docker) | `psql --version` |
| Redis | 7 | 7 (Docker) | `redis-cli --version` |
| 依赖锁定 | `requirements.txt` + `package-lock.json` | 同 | `pip freeze` + `npm ci` |

### 12.5 灰度发布策略（Phase 2+）

Nginx `split_clients` 按 IP+UA 哈希分流：90% stable → 10% canary。Canary 版本验证 15 分钟无异常后全量滚动更新。

---

## 附录 K. 测试策略详细方案

### K.1 测试金字塔

```
         ┌──────┐
         │ E2E  │  5% — 10 个 Playwright 用例
        ┌┴──────┴┐
        │ 集成测试 │  25% — ~50 个 testcontainers 用例
       ┌┴─────────┴┐
       │  单元测试   │  70% — ~200 个 pytest 用例
      └─────────────┘
```

### K.2 单元测试核心用例

```python
# tests/unit/test_pipeline_state.py
class TestPipelineState:
    def test_valid_state(self):
        state = PipelineState(case_id="test", target_repo="linux")
        assert state.current_stage == "explore"

    def test_invalid_target_repo(self):
        with pytest.raises(ValidationError):
            PipelineState(case_id="test", target_repo="invalid_repo")

    def test_cost_calculation(self):
        state = PipelineState(case_id="test", target_repo="linux")
        state.total_input_tokens = 50000
        state.total_output_tokens = 15000
        cost = (50000 * 3 + 15000 * 15) / 1_000_000
        assert cost == 0.375  # Claude Sonnet pricing


# tests/unit/test_route_review.py
class TestRouteReviewDecision:
    def test_approve(self):
        state = PipelineState(case_id="t1", target_repo="linux",
            review_verdict={"approved": True, "findings": []})
        assert route_review_decision(state) == "approve"

    def test_escalate_max_iterations(self):
        state = PipelineState(case_id="t1", target_repo="linux",
            review_verdict={"approved": False, "findings": [{"severity": "major"}]},
            review_iterations=3, max_review_iterations=3)
        assert route_review_decision(state) == "escalate"

    def test_escalate_convergence(self):
        """≥50% findings 重复 → 升级为人工作处理"""
        state = PipelineState(case_id="t1", target_repo="linux",
            review_verdict={"approved": False, "findings": [
                {"file": "a.c", "line": 10, "severity": "major"},
                {"file": "b.c", "line": 20, "severity": "minor"},
            ]},
            review_iterations=2, max_review_iterations=3,
            review_history=[
                {"findings": [{"file": "a.c", "line": 10, "severity": "major"}]},
                {"findings": [{"file": "a.c", "line": 10, "severity": "major"}]},
            ])
        assert route_review_decision(state) == "escalate"


# tests/unit/test_event_publisher.py
@pytest.mark.asyncio
class TestEventPublisher:
    async def test_sequence_numbering(self, redis_mock):
        publisher = EventPublisher(redis_mock)
        e1 = await publisher.publish("case1", "stage_change", {})
        e2 = await publisher.publish("case1", "agent_output", {})
        assert e1.seq == 1 and e2.seq == 2

    async def test_heartbeat_not_persisted(self, redis_mock):
        publisher = EventPublisher(redis_mock)
        await publisher.publish_heartbeat("case1")
        redis_mock.xadd.assert_not_called()
```

### K.3 集成测试核心用例

```python
# tests/integration/test_pipeline_flow.py
@pytest.mark.integration
class TestPipelineIntegration:

    async def test_full_mock_pipeline(self, app_client, mocker):
        """Mock Agent 完成 Created → Completed 全流程（含所有审批门）"""
        mocker.patch("backend.adapters.claude_adapter.ClaudeAgentAdapter.execute",
                     return_value=_mock_claude_events())
        mocker.patch("backend.adapters.openai_adapter.OpenAIAgentAdapter.execute",
                     return_value=_mock_openai_events())

        # 创建 → 启动 → 4 次 approve → 验证 completed
        case_id = await _create_case(app_client, "Test", "linux")
        await app_client.post(f"/api/v1/cases/{case_id}/start")
        await asyncio.sleep(0.5)

        for _ in range(4):  # explore, plan, code, test 四个审批门
            resp = await app_client.get(f"/api/v1/cases/{case_id}")
            assert resp.json()["status"].startswith("pending_")
            await app_client.post(f"/api/v1/cases/{case_id}/review",
                                  json={"action": "approve"})
            await asyncio.sleep(0.5)

        resp = await app_client.get(f"/api/v1/cases/{case_id}")
        assert resp.json()["status"] == "completed"

    async def test_sse_event_stream(self, app_client, mocker):
        """SSE 事件流完整性"""
        mocker.patch(...)
        case_id = await _create_and_start_case(app_client)

        events = []
        async with app_client.stream("GET", f"/api/v1/cases/{case_id}/events") as resp:
            async for line in resp.aiter_lines():
                if line.startswith("data:"):
                    events.append(json.loads(line[5:]))

        event_types = [e["event_type"] for e in events if e["event_type"] != "heartbeat"]
        assert "stage_change" in event_types
        assert "agent_output" in event_types

    async def test_review_idempotency(self, app_client, mocker):
        """相同 review_id 不重复处理"""
        case_id = await _get_case_at_review(app_client)
        review_id = str(uuid4())

        r1 = await app_client.post(f"/api/v1/cases/{case_id}/review",
                                   json={"action": "approve", "review_id": review_id})
        assert r1.status_code == 200

        r2 = await app_client.post(f"/api/v1/cases/{case_id}/review",
                                   json={"action": "approve", "review_id": review_id})
        assert "idempotent" in r2.json()["message"]
```

### K.4 Prompt 回归测试

```python
# tests/eval/test_explorer_prompt.py
GOLDEN_CASES = [
    {"id": "gc_001", "input": "Check Zicfiss kernel support",
     "expected_type": "isa_extension", "min_evidence": 2, "min_feasibility": 0.5},
]

@pytest.mark.eval
@pytest.mark.parametrize("case", GOLDEN_CASES)
async def test_golden_case(case, explorer_adapter):
    result = await run_explorer(explorer_adapter, case["input"])
    assert result.contribution_type == case["expected_type"]
    assert len(result.evidence) >= case["min_evidence"]
    assert result.feasibility_score >= case["min_feasibility"]
```

---

## 附录 L. 配置管理体系

### L.1 配置分层

```
优先级 (高 → 低):
1. 环境变量 (最高，覆盖一切)
2. .env 文件 (Docker Compose 注入)
3. config.py 默认值 (最低保证可运行)
```

### L.2 关键环境变量（完整清单）

```bash
# .env.example

# LLM
CLAUDE_API_KEY=sk-ant-...          # 必需
OPENAI_API_KEY=sk-...              # 必需
CLAUDE_MODEL=claude-sonnet-4-20250514
OPENAI_MODEL=gpt-4o
CODEX_MODEL=codex-mini-latest

# 数据库
MONGO_URI=mongodb://mongo:27017/ai_agent
POSTGRES_URI=postgresql://rv:rv_pass@postgres:5432/rv_checkpoints
REDIS_URL=redis://redis:6379/0

# 认证 (生产环境必须修改!)
JWT_SECRET=change-me-in-production
BOOTSTRAP_ADMIN_PASSWORD=admin123

# Pipeline
MAX_REVIEW_ITERATIONS=3
MAX_COST_PER_CASE_USD=10.0
MAX_CONCURRENT_CLAUDE=3
MAX_CONCURRENT_OPENAI=5
MAX_CONCURRENT_QEMU=2

# 安全
CORS_ORIGINS=http://localhost:5173
RATE_LIMIT_PER_MINUTE=100

# 环境
ENVIRONMENT=development            # development | staging | production
LOG_LEVEL=INFO
```

### L.3 config.py 实现（Pydantic Settings）

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_config = {"env_file": ".env", "extra": "ignore"}
    environment: str = "development"
    mongo_uri: str = "mongodb://localhost:27017/ai_agent"
    claude_api_key: Optional[str] = None
    jwt_secret: str = "dev-secret"
    max_review_iterations: int = 3
    # ... 所有配置项带类型 + 默认值

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

---

## 附录 M. 部署与回滚策略

### M.1 部署流水线

```
Git Push (main)
  → CI: Lint + Unit Tests + Integration Tests
  → Build Docker Images
  → Staging Deploy (自动)
  → Health Check + Smoke Test
  → Production Deploy (手动触发)
     ├── 备份数据库
     ├── docker compose up -d --no-deps backend (滚动更新)
     └── 监控确认 (5 分钟无异常)
```

### M.2 回滚流程

```bash
# scripts/rollback.sh
docker compose stop backend
export BACKEND_TAG=$PREVIOUS_VERSION
docker compose up -d --no-deps backend
# 健康检查 30 次 (每次 2s)
# 失败则恢复数据库备份
```

### M.3 数据库迁移（版本化）

```python
# db/migrations.py
MIGRATIONS = {
    1: "add_rv_insights_collections",   # 创建 RV 集合+索引
    2: "add_approval_history_to_cases", # 案例审批历史
    3: "add_stage_costs_breakdown",     # 按阶段成本
}

async def run_migrations(db):
    """幂等迁移：只执行未应用的版本"""
    current = await _get_current_version(db)
    for v in sorted(MIGRATIONS.keys()):
        if v > current:
            await globals()[MIGRATIONS[v]](db)
            await _set_version(db, v)
```

### M.4 每日备份

```bash
#!/bin/bash
# crontab: 0 2 * * * /scripts/backup.sh
DATE=$(date +%Y%m%d)
BACKUP_DIR="/data/backups/${DATE}"
mongodump --uri="${MONGO_URI}" --gzip --out="${BACKUP_DIR}/mongo"
pg_dump "${POSTGRES_URI}" | gzip > "${BACKUP_DIR}/postgres.sql.gz"
find /data/backups -mtime +30 -exec rm -rf {} \;
```

---

## 附录 N. 数据迁移策略（ScienceClaw → RV-Insights）

| ScienceClaw 集合 | 迁移方式 |
|------------------|----------|
| `users` | 添加 `role` 字段（默认 "user"，admin 设为 "admin"） |
| `user_sessions` | 清空（JWT 替代，用户需重新登录） |
| `sessions`, `models`, `blocked_skills/tools`, `task_settings`, `im_*` | 直接复用（schema 不变） |
| `contribution_cases`, `human_reviews`, `stage_outputs`, `audit_log` | 全新创建 |

**原则**：不删除原数据，新增集合，可随时回退到 ScienceClaw 后端。

---

## 附录 O. 监控与可观测性

### O.1 健康检查端点

- `GET /health` — 基础健康（Docker healthcheck）
- `GET /ready` — 就绪检查（MongoDB + PostgreSQL + Redis + Sandbox 全部可达）
- 任一依赖不可达 → 503 `{"status": "degraded", "checks": {...}}`

### O.2 关键告警规则

| 告警 | 条件 | 级别 | 通知 |
|------|------|------|------|
| Pipeline 卡死 | 单阶段 > 30min | Warning | Feishu |
| Agent 连续失败 | 同阶段 3 次失败 | Critical | Feishu + SMS |
| 成本异常 | >$10/case 或 >$50/h | Warning | Feishu |
| 高错误率 | 5xx > 5%/5min | Critical | Feishu + SMS |
| 数据库满 | 连接池 >90% 或磁盘 >85% | Warning | Feishu |

### O.3 结构化日志规范

```python
import structlog
logger = structlog.get_logger()

# 每条日志绑定 case_id / session_id，便于关联查询
log = logger.bind(case_id=case_id, stage="explore")
log.info("explore_started")
log.info("explore_completed", feasibility=0.85, tokens_in=50000)
log.error("explore_failed", error=str(e), exc_info=True)
```

---

## 附录 P. Chat 模式完整实现方案

### P.1 ChatRunner 核心实现

```python
# chat/runner.py
class ChatRunner:
    """管理单个会话的 Agent 对话生命周期

    架构：复用 ScienceClaw DeepAgents 引擎 → asyncio.Queue → SSE
    与 Pipeline 隔离：Chat = asyncio.Queue (进程内)，Pipeline = Redis Pub/Sub (进程外)
    """

    _instances: dict[str, "ChatRunner"] = {}
    _global_semaphore = asyncio.Semaphore(10)  # 全局并发限制

    def __init__(self, session_id: str, user_id: str, model_config_id: str = None):
        self.session_id = session_id
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=256)
        self._stop_event = asyncio.Event()
        self._task: Optional[asyncio.Task] = None
        ChatRunner._instances[session_id] = self

    async def run(self, user_message: str, language: str = "zh",
                  attachments: list[str] | None = None) -> None:
        """执行 Chat 任务，推送事件到 queue"""
        if self._task and not self._task.done():
            raise RuntimeError(f"Session {self.session_id} already running")

        self._stop_event.clear()
        self._task = asyncio.create_task(
            self._execute(user_message, language, attachments)
        )

    async def _execute(self, user_message, language, attachments):
        await ChatRunner._global_semaphore.acquire()
        try:
            llm = get_llm_model(self.model_config_id)
            async for event_data in arun_science_task_stream(
                session_id=self.session_id,
                user_message=user_message,
                language=language,
                llm=llm,
                stop_event=self._stop_event,
            ):
                try:
                    self.queue.put_nowait(ChatEvent(**event_data))
                except asyncio.QueueFull:
                    try: self.queue.get_nowait()  # 丢弃最旧事件
                    except: pass
                    self.queue.put_nowait(ChatEvent(**event_data))
            self.queue.put_nowait(ChatEvent(event_type="done", data={}))
        except asyncio.CancelledError:
            self.queue.put_nowait(ChatEvent(event_type="stopped", data={"reason": "cancelled"}))
        except Exception as e:
            self.queue.put_nowait(ChatEvent(event_type="error", data={"message": str(e)}))
        finally:
            ChatRunner._global_semaphore.release()

    async def stop(self) -> None:
        self._stop_event.set()
        if self._task: self._task.cancel()

    async def event_stream(self) -> AsyncIterator[dict]:
        """SSE 事件生成器"""
        while True:
            try:
                event = await asyncio.wait_for(self.queue.get(), timeout=30)
                yield {"event": event.event_type, "data": event.model_dump_json()}
            except asyncio.TimeoutError:
                yield {"event": "heartbeat", "data": "{}"}

        ChatRunner._instances.pop(self.session_id, None)
```

### P.2 Chat SSE 端点

```python
@router.post("/sessions/{session_id}/chat")
async def session_chat(session_id: str, body: ChatRequest,
                       user: User = Depends(get_current_user)):
    runner = ChatRunner.get(session_id) or ChatRunner(
        session_id=session_id, user_id=user.id,
        model_config_id=body.model_config_id,
    )
    asyncio.create_task(runner.run(
        user_message=body.message,
        language=body.language or "zh",
        attachments=body.attachments,
    ))
    return EventSourceResponse(runner.event_stream())
```

### P.3 Chat 与 Pipeline 资源分配

| 资源 | 总量 | Pipeline 保留 | Chat 可用 |
|------|------|-------------|----------|
| Claude SDK 并发 | 10 | 3 | 7 |
| OpenAI SDK 并发 | 15 | 5 | 10 |
| QEMU 沙箱 | 2 | 2 (Pipeline 独占) | 0 |

Pipeline 优先：chat 请求排队超过 60s 返回 429。
