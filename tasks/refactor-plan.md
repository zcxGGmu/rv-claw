# RV-Claw 完整重构计划 v3.0（整合版）

> **版本**: v3.1
> **日期**: 2026-05-01
> **对标基准**: ScienceClaw (完整功能迁移) + design.md (后端架构重构)
> **目标**: 在保留 ScienceClaw 全部前端功能的基础上，实现 RV-Insights 五阶段 Agent Pipeline
> **整合来源**: refactor-plan.md (v1.0) + refactor-plan-v2.md (v2.0) + design.md (权威架构) + 实际代码库分析
> **审计状态**: 2026-05-01 完成全量代码审计，进度和已知问题已同步到 [progress.md](./progress.md)。本文档保留原始设计规划，实际实现偏差详见 progress.md 各 Phase 审计注释。

---

## 目录

- [1. 现状分析与对标基准](#1-现状分析与对标基准)
  - [1.1 ScienceClaw 功能全景清单](#11-scienceclaw-功能全景清单)
  - [1.2 rv-claw 当前状态](#12-rv-claw-当前状态)
  - [1.3 核心矛盾与解决思路](#13-核心矛盾与解决思路)
- [2. 架构总览](#2-架构总览)
  - [2.1 双模式架构 (Chat + Pipeline)](#21-双模式架构-chat--pipeline)
  - [2.2 服务拓扑](#22-服务拓扑)
  - [2.3 技术栈锁定](#23-技术栈锁定)
- [3. 前端重构计划](#3-前端重构计划)
  - [3.1 页面路由矩阵](#31-页面路由矩阵)
  - [3.2 ScienceClaw 功能全量迁移清单](#32-scienceclaw-功能全量迁移清单)
  - [3.3 新增 Pipeline 前端模块](#33-新增-pipeline-前端模块)
  - [3.4 组件复用与改造策略](#34-组件复用与改造策略)
  - [3.5 状态管理重构](#35-状态管理重构)
  - [3.6 API 层整合](#36-api-层整合)
- [4. 后端重构计划](#4-后端重构计划)
  - [4.1 FastAPI 路由重构](#41-fastapi-路由重构)
  - [4.2 LangGraph Pipeline 引擎](#42-langgraph-pipeline-引擎)
  - [4.3 Agent 适配器层](#43-agent-适配器层)
  - [4.4 数据源接入层](#44-数据源接入层)
  - [4.5 产物与审计系统](#45-产物与审计系统)
  - [4.6 SSE 事件总线](#46-sse-事件总线)
  - [4.7 认证鉴权重构](#47-认证鉴权重构)
- [5. 数据库重构](#5-数据库重构)
  - [5.1 MongoDB Schema 变更](#51-mongodb-schema-变更)
  - [5.2 PostgreSQL Checkpointer](#52-postgresql-checkpointer)
  - [5.3 Redis 使用策略](#53-redis-使用策略)
- [6. API 契约](#6-api-契约)
  - [6.1 保留的 ScienceClaw API](#61-保留的-scienceclaw-api)
  - [6.2 新增的 Pipeline API](#62-新增的-pipeline-api)
  - [6.3 变更的 API](#63-变更的-api)
- [7. 实现阶段规划](#7-实现阶段规划)
  - [7.1 Phase 0: 基础架构 (2周)](#71-phase-0-基础架构-2周)
  - [7.2 Phase 1: Chat 模式完整迁移 (2周)](#72-phase-1-chat-模式完整迁移-2周)
  - [7.3 Phase 2: Pipeline 后端骨架 (4周)](#73-phase-2-pipeline-后端骨架-4周)
  - [7.4 Phase 3: Pipeline 前端与集成 (4周)](#74-phase-3-pipeline-前端与集成-4周)
  - [7.5 Phase 4: 集成测试与优化 (3周)](#75-phase-4-集成测试与优化-3周)
  - [7.6 Phase 5: 生产准备 (1周)](#76-phase-5-生产准备-1周)
- [8. 测试策略](#8-测试策略)
  - [8.1 测试金字塔](#81-测试金字塔)
  - [8.2 测试分层详情](#82-测试分层详情)
- [9. 监控与可观测性](#9-监控与可观测性)
  - [9.1 三大支柱](#91-三大支柱)
  - [9.2 业务指标](#92-业务指标)
  - [9.3 日志规范](#93-日志规范)
  - [9.4 关键告警规则](#94-关键告警规则)
- [10. 风险与缓解](#10-风险与缓解)
  - [10.1 风险矩阵](#101-风险矩阵)
  - [10.2 详细缓解措施](#102-详细缓解措施)
- [11. 验收标准](#11-验收标准)
  - [11.1 功能验收](#111-功能验收)
  - [11.2 性能验收](#112-性能验收)
  - [11.3 质量验收](#113-质量验收)
- [附录 A: 术语表](#附录-a-术语表)
- [附录 B: 参考文档](#附录-b-参考文档)
- [附录 C: ScienceClaw → rv-claw 文件映射](#附录-c-scienceclaw--rv-claw-文件映射)
- [附录 D: 关键依赖版本锁定](#附录-d-关键依赖版本锁定)

---

## 1. 现状分析与对标基准

### 1.1 ScienceClaw 功能全景清单

ScienceClaw 是一个功能完备的**个人科研助手**，基于 LangChain DeepAgents + AIO Sandbox。以下是其**全部暴露给用户的前端功能**（必须全量迁移）：

#### A. 核心 Chat 功能
| 功能 | 说明 | 前端组件 |
|------|------|----------|
| 多轮对话 | 支持长上下文多轮聊天 | ChatBox.vue, ChatMessage.vue |
| 会话管理 | 创建/删除/重命名/置顶会话 | SessionItem.vue, LeftPanel.vue |
| SSE 流式输出 | 实时接收 Agent 思考过程和结果 | usePendingChat.ts |
| 附件上传 | 图片/文档/代码文件上传 | ChatBoxFiles.vue, AttachmentsMessage.vue |
| 会话分享 | 私有/公开分享链接 | SharePage.vue, ShareLayout.vue |
| 未读消息 | 会话未读计数 | useSessionNotifications.ts |
| 快捷提示词 | 首页快速开始卡片 | SuggestedQuestions.vue |

#### B. Agent 执行可视化
| 功能 | 说明 | 前端组件 |
|------|------|----------|
| 思考过程展示 | Agent 的 reasoning 步骤 | ProcessMessage.vue |
| 工具调用展示 | Search/Shell/File/Browser/MCP | ToolUse.vue, toolViews/*.vue |
| 计划面板 | Agent 执行计划展示 | PlanPanel.vue |
| 步骤消息 | 执行步骤的进度展示 | StepMessage.vue |
| 接管视图 | 人工接管 Agent 执行 | TakeOverView.vue |
| 活动面板 | 实时活动日志 | ActivityPanel.vue |

#### C. 文件管理系统
| 功能 | 说明 | 前端组件 |
|------|------|----------|
| 文件面板 | 侧边文件浏览器 | FilePanel.vue, FilePanelContent.vue |
| 文件预览 | 多格式预览支持 | FilePreviewModal.vue + filePreviews/*.vue |
| 代码预览 | Monaco Editor 高亮 | CodeFilePreview.vue, MonacoEditor.vue |
| 图片预览 | 图片查看器 | ImageViewer.vue |
| PDF 预览 | PDF 渲染 | PdfFilePreview.vue |
| Office 预览 | DOCX/XLSX/PPTX | DocxFilePreview.vue, ExcelFilePreview.vue |
| 分子结构预览 | 3D 分子查看 | MoleculeViewer.vue, MoleculeFilePreview.vue |
| HTML 预览 | 渲染 HTML 内容 | HtmlViewer.vue |
| 沙箱终端 | Web Terminal | SandboxTerminal.vue |
| VNC 查看器 | 远程桌面 | VNCViewer.vue |
| 沙箱预览 | 沙箱状态预览 | SandboxPreview.vue |
| 会话文件列表 | 按会话组织文件 | SessionFileList.vue, SessionFileListContent.vue |
| 轮次文件弹出框 | 按轮次查看文件 | RoundFilesPopover.vue |

#### D. 工具与技能系统
| 功能 | 说明 | 前端组件 |
|------|------|----------|
| 工具面板 | 可用工具列表 | ToolPanel.vue, ToolPanelContent.vue |
| 工具详情页 | 单个工具详情 | ToolDetailPage.vue |
| 技能页面 | 技能列表与管理 | SkillsPage.vue |
| 技能详情页 | 单个技能详情 | SkillDetailPage.vue |
| 科学工具详情 | 1900+ 工具展示 | ScienceToolDetail.vue |
| 工具市场 | 工具发现与安装 | ToolsPage.vue |

#### E. 任务调度系统
| 功能 | 说明 | 前端组件 |
|------|------|----------|
| 任务列表 | 定时任务管理 | TasksListPage.vue |
| 任务配置 | 创建/编辑定时任务 | TaskConfigPage.vue |
| 任务执行页 | 任务运行状态 | TasksPage.vue |
| 飞书 webhook | 任务结果推送 | LarkBindingSettings.vue |

#### F. 设置系统 (12 个子模块)
| 设置项 | 说明 |
|--------|------|
| 账户设置 | 用户名/邮箱/头像 |
| 个人资料 | 个人信息管理 |
| 通用设置 | 语言/主题/通知 |
| 个性化设置 | UI 自定义 |
| 模型设置 | LLM 模型配置与选择 |
| 通知设置 | 消息通知偏好 |
| 任务设置 | 定时任务默认配置 |
| Token 统计 | 用量与成本统计 |
| IM 系统设置 | 即时通讯配置 |
| 飞书绑定 | 飞书机器人绑定 |
| 微信 ClawBot | 微信集成 |
| 修改密码 | 密码安全 |

#### G. 用户系统
| 功能 | 说明 |
|------|------|
| 登录 | JWT 认证 |
| 注册 | 新用户注册 |
| 重置密码 | 邮箱验证重置 |
| 用户菜单 | 下拉菜单导航 |
| 语言切换 | 中英文切换 |
| 主题切换 | 暗黑/亮色模式 |

#### H. 统计与监控
| 功能 | 说明 | 前端/API |
|------|------|----------|
| 资源概览 | 系统资源使用 | statistics/summary |
| 模型统计 | 各模型调用统计 | statistics/models |
| 趋势分析 | 调用趋势图表 | statistics/trends |
| 会话统计 | 会话使用统计 | statistics/sessions |

#### I. IM 集成
| 功能 | 说明 |
|------|------|
| 飞书绑定 | 飞书机器人配置 |
| 微信控制 | 微信机器人启停 |
| 消息推送 | 任务结果推送 |

---

### 1.2 rv-claw 当前状态

| 维度 | 现状 |
|------|------|
| **代码基线** | ScienceClaw 完整代码库（backend + frontend + sandbox + task-service + websearch），位于 `ScienceClaw/` 目录下 |
| **设计文档** | `tasks/design.md` 完整（4582 行），但 `mvp-tasks.md`, `migration-map.md`, `chat-architecture.md`, `conventions.md` 缺失 |
| **Pipeline 实现** | **零代码**。LangGraph Pipeline 引擎、5 个 Agent 节点、Human-in-the-Loop 均未实现 |
| **前端 Pipeline UI** | **零代码**。CaseListView, CaseDetailView, PipelineView, ReviewPanel, DiffViewer 均未实现 |
| **RISC-V 专用逻辑** | **零代码**。Patchwork API、ISA 扩展验证、checkpatch.pl 集成、QEMU 测试均未实现 |
| **RBAC** | ScienceClaw 使用简单本地认证，无角色区分。设计文档要求 admin/user 双角色 |
| **部署** | docker-compose.yml 存在，但按 ScienceClaw 配置，未加入 PostgreSQL 和 Pipeline 专用服务 |

**当前前端路由**（`ScienceClaw/frontend/src/main.ts`）：
```typescript
/chat               -> MainLayout -> HomePage (alias /, /home)
/chat/:sessionId    -> MainLayout -> ChatPage
/chat/skills        -> MainLayout -> SkillsPage
/chat/skills/:name  -> MainLayout -> SkillDetailPage
/chat/tools         -> MainLayout -> ToolsPage
/chat/tools/:name   -> MainLayout -> ToolDetailPage
/chat/science-tools/:name -> MainLayout -> ScienceToolDetail
/chat/tasks         -> MainLayout -> TasksPage
/share/:sessionId   -> ShareLayout -> SharePage
/login              -> LoginPage
```

**当前后端路由**（`ScienceClaw/backend/main.py`）：
```python
/api/v1/auth        # 登录/注册/Token 刷新
/api/v1/sessions    # 会话 CRUD + SSE Chat
/api/v1/file        # 文件操作
/api/v1/models      # 模型配置
/api/v1/tooluniverse # 工具宇宙
/api/v1/task_settings # 任务设置
/api/v1/memory      # 记忆管理
/api/v1/science     # 科学工具
/api/v1/chat        # 通用聊天
/api/v1/statistics  # 统计
/api/v1/im          # IM 集成（飞书/微信）
```

---

### 1.3 核心矛盾与解决思路

| 矛盾 | 解决思路 |
|------|----------|
| ScienceClaw 是**通用科研助手**，RV-Insights 是**RISC-V 专项贡献平台** | **双模式共存**：保留 Chat 模式的全部功能，新增 Pipeline 模式作为独立工作流 |
| ScienceClaw 前端以**Chat 为中心**，RV-Insights 需要**Pipeline 为中心** | **路由隔离**：`/chat/*` 走 Chat 模式，`/cases/*` 走 Pipeline 模式，共享布局组件 |
| ScienceClaw 后端以**DeepAgent 会话**为核心，RV-Insights 需要**LangGraph StateGraph** | **服务扩展**：保留现有会话路由，新增 `/cases`, `/reviews`, `/artifacts` 路由，共享基础设施 |
| 前端技术栈相同但组件模式不同 | **组件级复用**：ChatBox、FilePanel、Settings 等直接复用；Pipeline 专用组件新建 |

---

## 2. 架构总览

### 2.1 双模式架构 (Chat + Pipeline)

```
┌─────────────────────────────────────────────────────────────────┐
│                        前端 (Vue 3 SPA)                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐ │
│  │  HomePage   │    │  ChatPage   │    │   CaseDetailView    │ │
│  │  (欢迎页)    │◄──►│ (通用对话)   │    │  (Pipeline 核心)     │ │
│  └─────────────┘    └─────────────┘    └─────────────────────┘ │
│         ▲                  ▲                      ▲             │
│         └──────────────────┴──────────────────────┘             │
│                        共享组件层                                 │
│     LeftPanel | FilePanel | SettingsDialog | UserMenu | Theme   │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Gateway (Port 8000)                   │
│  ┌────────────────────────┐    ┌─────────────────────────────┐ │
│  │    Chat 模式路由        │    │      Pipeline 模式路由       │ │
│  │  /api/v1/sessions/*    │    │   /api/v1/cases/*           │ │
│  │  /api/v1/chat          │    │   /api/v1/reviews/*         │ │
│  │  /api/v1/models        │    │   /api/v1/artifacts/*       │ │
│  │  /api/v1/statistics    │    │   /api/v1/pipeline/*        │ │
│  │  /api/v1/tasks/*       │    │                             │ │
│  └────────────────────────┘    └─────────────────────────────┘ │
│  ┌────────────────────────┐    ┌─────────────────────────────┐ │
│  │    共享路由             │    │      新增服务路由            │ │
│  │  /api/v1/auth/*        │    │   /api/v1/knowledge (Phase2)│ │
│  │  /api/v1/files/*       │    │   /api/v1/metrics           │ │
│  │  /api/v1/im/*          │    │                             │ │
│  │  /api/v1/memory        │    │                             │ │
│  └────────────────────────┘    └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                    │
           ┌────────────────────────┼────────────────────────┐
           ▼                        ▼                        ▼
┌─────────────────┐      ┌────────────────────┐     ┌─────────────────┐
│  Chat 引擎       │      │  LangGraph Pipeline │     │   基础设施       │
│  (DeepAgent)     │      │  (StateGraph)       │     │                 │
│  · Session管理   │      │  · Explore Node     │     │  · MongoDB      │
│  · SSE 推送      │      │  · Plan Node        │     │  · PostgreSQL   │
│  · Tool执行      │      │  · Develop Node     │     │  · Redis        │
│  · Skill加载     │      │  · Review Node      │     │  · Sandbox      │
│                  │      │  · Test Node        │     │  · WebSearch    │
│                  │      │  · Human Gate       │     │                 │
└─────────────────┘      └────────────────────┘     └─────────────────┘
```

---

### 2.2 服务拓扑

```yaml
# 最终部署拓扑 (docker-compose.yml)
services:
  # ── 前端 ──
  nginx:
    image: nginx:1.25-alpine
    ports: ["80:80"]

  # ── 后端 API ──
  backend:
    build: ./ScienceClaw/backend   # 保留原目录结构
    ports: ["8000:8000"]
    depends_on: [mongodb, postgres, redis]

  # ── Chat 沙箱 (ScienceClaw 现有) ──
  sandbox:
    build: ./ScienceClaw/sandbox
    ports: ["18080:8080"]

  # ── Pipeline 专用 QEMU 沙箱 (新增) ──
  qemu-sandbox:
    build: ./sandbox-qemu  # 新增 Dockerfile
    # 交叉编译工具链 + QEMU RISC-V

  # ── 数据库 ──
  mongodb:
    image: mongo:7.0
    ports: ["27017:27017"]

  postgres:
    image: postgres:16-alpine  # 新增：LangGraph checkpointer
    ports: ["5432:5432"]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  # ── 搜索服务 (ScienceClaw 现有) ──
  websearch:
    build: ./ScienceClaw/websearch
    ports: ["8068:8068"]

  searxng:
    image: searxng/searxng:latest
    ports: ["26080:8080"]

  # ── 任务调度 (ScienceClaw 现有) ──
  scheduler_api:
    build: ./ScienceClaw/task-service

  celery_worker:
    build: ./ScienceClaw/task-service

  celery_beat:
    build: ./ScienceClaw/task-service
```

---

### 2.3 技术栈锁定

| 层级 | 技术 | 来源 | 变更 |
|------|------|------|------|
| 前端框架 | Vue 3 + Vite + TypeScript | ScienceClaw | ❌ 不变 |
| UI 库 | TailwindCSS + reka-ui | ScienceClaw | ❌ 不变 |
| 状态管理 | Composables (模块级 ref 单例) | ScienceClaw | ❌ 不变 |
| 后端框架 | FastAPI | ScienceClaw | ❌ 不变 |
| 数据库 | MongoDB (motor) | ScienceClaw | ❌ 不变 |
| 缓存/队列 | Redis | ScienceClaw | ❌ 不变 |
| Pipeline 引擎 | LangGraph StateGraph | design.md | ⚠️ 新增 |
| Checkpointer | PostgreSQL + AsyncPostgresSaver | design.md | ⚠️ 新增 |
| SSE | @microsoft/fetch-event-source | ScienceClaw | ❌ 不变 |
| 沙箱 | AIO Sandbox | ScienceClaw | ❌ 不变 |
| QEMU 沙箱 | 自定义 Docker (riscv64) | design.md | ⚠️ 新增 |
| Agent SDK | claude-agent-sdk + openai-agents-sdk | design.md | ⚠️ 新增 |

---

## 3. 前端重构计划

### 3.1 页面路由矩阵

```typescript
// 最终路由配置 (ScienceClaw/frontend/src/main.ts 改造后)
const routes = [
  // ── 公开路由 ──
  { path: '/login', component: LoginPage },
  { path: '/share/:token', component: ShareLayout, children: [
    { path: '', component: SharePage }
  ]},

  // ── 认证后布局 ──
  {
    path: '/',
    component: MainLayout,  // ScienceClaw 现有：LeftPanel + FilePanel + 主内容区
    meta: { requiresAuth: true },
    children: [
      // Chat 模式 (ScienceClaw 现有，全量保留)
      { path: '', name: 'home', component: HomePage },
      { path: 'chat/:sessionId', name: 'chat', component: ChatPage },

      // Pipeline 模式 (新增)
      { path: 'cases', name: 'cases', component: CaseListView },
      { path: 'cases/:id', name: 'case-detail', component: CaseDetailView },

      // 工具与技能 (ScienceClaw 现有)
      { path: 'tools', name: 'tools', component: ToolsPage },
      { path: 'tools/:name', name: 'tool-detail', component: ToolDetailPage },
      { path: 'skills', name: 'skills', component: SkillsPage },
      { path: 'skills/:name', name: 'skill-detail', component: SkillDetailPage },
      { path: 'science-tools/:name', name: 'science-tool', component: ScienceToolDetail },

      // 任务调度 (ScienceClaw 现有)
      { path: 'tasks', name: 'tasks', component: TasksPage },
      { path: 'tasks/config', name: 'task-config', component: TaskConfigPage },
      { path: 'tasks/:id', name: 'task-run', component: TasksPage },

      // 统计 (改造：从 metrics 改为 statistics)
      { path: 'statistics', name: 'statistics', component: StatisticsPage },

      // 知识库 (Phase 2)
      // { path: 'knowledge', name: 'knowledge', component: KnowledgeView },
    ]
  }
]
```

---

### 3.2 ScienceClaw 功能全量迁移清单

以下 **ScienceClaw 全部功能必须保留**，按模块列出迁移策略：

#### Module 1: Chat 核心 (零变更，直接复用)
```
ScienceClaw/frontend/src/pages/HomePage.vue          → 保留
ScienceClaw/frontend/src/pages/ChatPage.vue          → 保留
ScienceClaw/frontend/src/components/ChatBox.vue      → 保留
ScienceClaw/frontend/src/components/ChatMessage.vue  → 保留
ScienceClaw/frontend/src/components/ProcessMessage.vue → 保留
ScienceClaw/frontend/src/components/StepMessage.vue  → 保留
ScienceClaw/frontend/src/components/ActivityPanel.vue → 保留
ScienceClaw/frontend/src/components/PlanPanel.vue    → 保留
ScienceClaw/frontend/src/components/ToolUse.vue      → 保留
ScienceClaw/frontend/src/components/TakeOverView.vue → 保留
ScienceClaw/frontend/src/components/SuggestedQuestions.vue → 保留
ScienceClaw/frontend/src/components/AttachmentsMessage.vue → 保留
ScienceClaw/frontend/src/components/ChatBoxFiles.vue → 保留
ScienceClaw/frontend/src/components/toolViews/*.vue  → 保留
ScienceClaw/frontend/src/composables/usePendingChat.ts → 保留
ScienceClaw/frontend/src/composables/useMessageGrouper.ts → 保留
```

#### Module 2: 会话管理 (零变更，直接复用)
```
ScienceClaw/frontend/src/components/LeftPanel.vue    → 保留
ScienceClaw/frontend/src/components/SessionItem.vue  → 保留
ScienceClaw/frontend/src/components/SessionFileList.vue → 保留
ScienceClaw/frontend/src/components/SessionFileListContent.vue → 保留
ScienceClaw/frontend/src/composables/useLeftPanel.ts → 保留
ScienceClaw/frontend/src/composables/useSessionGrouping.ts → 保留
ScienceClaw/frontend/src/composables/useSessionListUpdate.ts → 保留
ScienceClaw/frontend/src/composables/useSessionNotifications.ts → 保留
ScienceClaw/frontend/src/composables/useSessionFileList.ts → 保留
```

#### Module 3: 文件系统 (零变更，直接复用)
```
ScienceClaw/frontend/src/components/FilePanel.vue    → 保留
ScienceClaw/frontend/src/components/FilePanelContent.vue → 保留
ScienceClaw/frontend/src/components/FilePreviewModal.vue → 保留
ScienceClaw/frontend/src/components/FileViewer.vue   → 保留
ScienceClaw/frontend/src/components/HtmlViewer.vue   → 保留
ScienceClaw/frontend/src/components/ImageViewer.vue  → 保留
ScienceClaw/frontend/src/components/VNCViewer.vue    → 保留
ScienceClaw/frontend/src/components/MoleculeViewer.vue → 保留
ScienceClaw/frontend/src/components/RoundFilesPopover.vue → 保留
ScienceClaw/frontend/src/components/filePreviews/*.vue → 全部保留
ScienceClaw/frontend/src/composables/useFilePanel.ts → 保留
ScienceClaw/frontend/src/composables/useRightPanel.ts → 保留
```

#### Module 4: 沙箱与终端 (零变更，直接复用)
```
ScienceClaw/frontend/src/components/SandboxPreview.vue → 保留
ScienceClaw/frontend/src/components/SandboxTerminal.vue → 保留
ScienceClaw/frontend/src/utils/sandbox.ts            → 保留
```

#### Module 5: 工具与技能 (零变更，直接复用)
```
ScienceClaw/frontend/src/pages/ToolsPage.vue         → 保留
ScienceClaw/frontend/src/pages/ToolDetailPage.vue    → 保留
ScienceClaw/frontend/src/pages/SkillsPage.vue        → 保留
ScienceClaw/frontend/src/pages/SkillDetailPage.vue   → 保留
ScienceClaw/frontend/src/pages/ScienceToolDetail.vue → 保留
ScienceClaw/frontend/src/components/ToolPanel.vue    → 保留
ScienceClaw/frontend/src/components/ToolPanelContent.vue → 保留
ScienceClaw/frontend/src/composables/useTool.ts      → 保留
ScienceClaw/frontend/src/api/tooluniverse.ts         → 保留
```

#### Module 6: 任务调度 (零变更，直接复用)
```
ScienceClaw/frontend/src/pages/TasksPage.vue         → 保留
ScienceClaw/frontend/src/pages/TasksListPage.vue     → 保留
ScienceClaw/frontend/src/pages/TaskConfigPage.vue    → 保留
ScienceClaw/frontend/src/api/tasks.ts                → 保留
ScienceClaw/frontend/src/api/taskSettings.ts         → 保留
```

#### Module 7: 设置系统 (扩展 RBAC，其余保留)
```
ScienceClaw/frontend/src/components/settings/SettingsDialog.vue → 保留
ScienceClaw/frontend/src/components/settings/SettingsTabs.vue   → 保留
ScienceClaw/frontend/src/components/settings/AccountSettings.vue → 保留
ScienceClaw/frontend/src/components/settings/ProfileSettings.vue → 保留
ScienceClaw/frontend/src/components/settings/GeneralSettings.vue → 保留
ScienceClaw/frontend/src/components/settings/PersonalizationSettings.vue → 保留
ScienceClaw/frontend/src/components/settings/ModelSettings.vue → 保留
ScienceClaw/frontend/src/components/settings/NotificationSettings.vue → 保留
ScienceClaw/frontend/src/components/settings/TaskSettings.vue → 保留
ScienceClaw/frontend/src/components/settings/TokenStatistics.vue → 保留 (数据扩展：增加 Pipeline Token 统计)
ScienceClaw/frontend/src/components/settings/IMSystemSettings.vue → 保留
ScienceClaw/frontend/src/components/settings/LarkBindingSettings.vue → 保留
ScienceClaw/frontend/src/components/settings/WeChatClawBotSettings.vue → 保留
ScienceClaw/frontend/src/components/settings/ChangePasswordDialog.vue → 保留
ScienceClaw/frontend/src/composables/useSettingsDialog.ts → 保留
```

**新增设置项**：
- `PipelineSettings.vue` — Pipeline 默认配置（max_review_iterations, default_model 等）

#### Module 8: 用户系统 (扩展 RBAC)
```
ScienceClaw/frontend/src/pages/LoginPage.vue         → 保留
ScienceClaw/frontend/src/components/login/*.vue      → 保留
ScienceClaw/frontend/src/components/UserMenu.vue     → 保留
ScienceClaw/frontend/src/components/LanguageSelector.vue → 保留
ScienceClaw/frontend/src/composables/useAuth.ts      → 扩展：增加 role 字段
ScienceClaw/frontend/src/utils/auth.ts               → 扩展：增加 role 判断
ScienceClaw/frontend/src/api/auth.ts                 → 扩展：返回 role 信息
```

#### Module 9: 统计 (改造 endpoint)
```
ScienceClaw/frontend/src/pages/StatisticsPage.vue    → 新增（替代 MetricsView）
ScienceClaw/frontend/src/api/statistics.ts           → 保留，endpoint 从 /metrics 改为 /statistics
```

#### Module 10: 共享 (零变更)
```
ScienceClaw/frontend/src/pages/ShareLayout.vue       → 保留
ScienceClaw/frontend/src/pages/SharePage.vue         → 保留
```

#### Module 11: UI 基础组件 (零变更)
```
ScienceClaw/frontend/src/components/ui/*.vue         → 全部保留
ScienceClaw/frontend/src/components/icons/*.vue      → 全部保留
ScienceClaw/frontend/src/components/CustomDialog.vue → 保留
ScienceClaw/frontend/src/components/ContextMenu.vue  → 保留
ScienceClaw/frontend/src/components/Toast.vue        → 保留
ScienceClaw/frontend/src/components/LoadingIndicator.vue → 保留
ScienceClaw/frontend/src/components/MonacoEditor.vue → 保留
ScienceClaw/frontend/src/components/SimpleBar.vue    → 保留
ScienceClaw/frontend/src/components/MarkdownEnhancements.vue → 保留
ScienceClaw/frontend/src/composables/useDialog.ts    → 保留
ScienceClaw/frontend/src/composables/useContextMenu.ts → 保留
ScienceClaw/frontend/src/composables/useTheme.ts     → 保留
ScienceClaw/frontend/src/composables/useTime.ts      → 保留
ScienceClaw/frontend/src/composables/useI18n.ts      → 保留
ScienceClaw/frontend/src/composables/useResizeObserver.ts → 保留
```

#### Module 12: API 基础设施 (扩展)
```
ScienceClaw/frontend/src/api/client.ts               → 保留（SSE 连接、Token 刷新）
ScienceClaw/frontend/src/api/index.ts                → 扩展：导出 cases, reviews, artifacts
ScienceClaw/frontend/src/api/auth.ts                 → 扩展：role 支持
ScienceClaw/frontend/src/api/agent.ts                → 保留
ScienceClaw/frontend/src/api/file.ts                 → 保留
ScienceClaw/frontend/src/api/im.ts                   → 保留
ScienceClaw/frontend/src/api/memory.ts               → 保留
ScienceClaw/frontend/src/api/models.ts               → 保留
ScienceClaw/frontend/src/api/webhooks.ts             → 保留
```

---

### 3.3 新增 Pipeline 前端模块

以下组件为 RV-Insights **全新开发**，不依赖 ScienceClaw 现有代码（但共享 UI 组件库）：

```
ScienceClaw/frontend/src/views/CaseListView.vue          # 案例列表（类似任务列表风格）
ScienceClaw/frontend/src/views/CaseDetailView.vue        # 案例详情 — 核心页面
ScienceClaw/frontend/src/views/StatisticsPage.vue        # 统计页（替代 MetricsView）

ScienceClaw/frontend/src/components/pipeline/
  ├── PipelineView.vue              # 5 阶段流水线可视化
  ├── StageNode.vue                 # 单阶段节点
  ├── StageConnector.vue            # 阶段连接线（带状态动画）
  ├── HumanGate.vue                 # 人工审核门禁 UI
  ├── IterationBadge.vue            # 迭代轮次标记
  ├── CostIndicator.vue             # 成本指示器
  └── PipelineTimeline.vue          # 时间线视图

ScienceClaw/frontend/src/components/review/
  ├── ReviewPanel.vue               # 审核决策面板
  ├── ReviewFinding.vue             # 单条审核发现
  ├── ReviewFindingList.vue         # 审核发现列表
  ├── DiffViewer.vue                # 基于 Monaco 的 Diff
  └── ReviewHistory.vue             # 历史审核记录

ScienceClaw/frontend/src/components/exploration/
  ├── ContributionCard.vue          # 贡献机会卡片
  ├── EvidenceChain.vue             # 证据链展示
  ├── EvidenceItem.vue              # 单条证据
  └── FeasibilityBadge.vue          # 可行性评分徽章

ScienceClaw/frontend/src/components/planning/
  ├── ExecutionPlanTree.vue         # 执行计划树
  ├── DevStepCard.vue               # 开发步骤卡片
  ├── TestCaseList.vue              # 测试用例列表
  └── RiskBadge.vue                 # 风险等级徽章

ScienceClaw/frontend/src/components/testing/
  ├── TestResultSummary.vue         # 测试结果摘要
  ├── TestLogViewer.vue             # 测试日志查看器
  ├── QemuStatus.vue                # QEMU 环境状态
  └── CoverageBadge.vue             # 覆盖率徽章

ScienceClaw/frontend/src/components/shared/
  ├── AgentEventLog.vue             # Agent 实时事件日志
  ├── ThinkingBlock.vue             # Agent 思考过程（可折叠）
  ├── ToolCallView.vue              # 工具调用可视化
  └── ArtifactViewer.vue            # 产物查看器

ScienceClaw/frontend/src/composables/
  ├── useCaseEvents.ts              # SSE 事件流管理（参考 usePendingChat）
  ├── usePipeline.ts                # Pipeline 状态追踪
  └── useReview.ts                  # 审核操作封装

ScienceClaw/frontend/src/composables/ (新增)
  ├── useCaseStore.ts               # 案例状态管理（模块级 ref 单例模式）
  ├── usePipelineStore.ts           # Pipeline 运行状态
  └── useReviewStore.ts             # 审核状态

ScienceClaw/frontend/src/types/
  ├── case.ts                       # 案例类型定义
  ├── pipeline.ts                   # Pipeline 类型定义
  ├── event.ts                      # SSE 事件类型
  ├── artifact.ts                   # 产物类型定义
  └── review.ts                     # 审核类型定义
```

---

### 3.4 组件复用与改造策略

| ScienceClaw 组件 | Pipeline 复用方式 | 改造点 |
|-----------------|-------------------|--------|
| `LeftPanel.vue` | ✅ 复用 | 增加 "Cases" 导航入口，与 "Sessions" 并列 |
| `FilePanel.vue` | ✅ 复用 | 支持按 `case_id` 过滤文件 |
| `MonacoEditor.vue` | ✅ 复用 | DiffViewer 直接基于 Monaco Editor 扩展 |
| `ChatMessage.vue` | ⚠️ 改造 | AgentEventLog 中的 tool_call 展示复用其样式 |
| `ProcessMessage.vue` | ⚠️ 改造 | ThinkingBlock 复用其折叠/展开交互 |
| `ActivityPanel.vue` | ⚠️ 改造 | AgentEventLog 参考其实时日志展示 |
| `FilePreviewModal.vue` | ✅ 复用 | ArtifactViewer 直接调用 |
| `SettingsDialog.vue` | ✅ 复用 | 增加 PipelineSettings Tab |
| `TokenStatistics.vue` | ⚠️ 改造 | 增加 Pipeline 各阶段 Token 消耗展示 |
| `LoadingIndicator.vue` | ✅ 复用 | StageNode 加载状态使用 |

---

### 3.5 状态管理重构

> **重要发现**: ScienceClaw 前端**未使用 Pinia**，而是采用 **Composable 模块级 ref 单例模式**（在 composable 文件顶部定义 `ref()`，所有调用者共享同一状态）。为保持一致性，Pipeline 新增状态也应遵循此模式，而非引入 Pinia。

```typescript
// composables/useCaseStore.ts (新增)
// 模块级单例状态（与 useAuth.ts / useLeftPanel.ts 保持一致）
const cases = ref<Case[]>([])
const currentCase = ref<Case | null>(null)
const pipelineStages = ref<PipelineStage[]>([])
const reviewIterations = ref(0)
const pendingReview = computed(() => /* ... */)

export function useCaseStore() {
  async function loadCases() { /* ... */ }
  async function loadCase(id: string) { /* ... */ }
  async function createCase(data: CreateCaseRequest) { /* ... */ }
  async function submitReview(decision: ReviewDecision) { /* ... */ }
  async function startPipeline(caseId: string) { /* ... */ }

  return {
    cases: readonly(cases),
    currentCase: readonly(currentCase),
    pipelineStages: readonly(pipelineStages),
    reviewIterations: readonly(reviewIterations),
    pendingReview,
    loadCases, loadCase, createCase, submitReview, startPipeline
  }
}

// composables/useAuth.ts (扩展)
// 在现有 useAuth 中扩展 role 支持
const userRole = ref<'admin' | 'user'>('user')  // 新增
const isAdmin = computed(() => userRole.value === 'admin')  // 新增

export function useAuth() {
  // ... 现有逻辑 ...
  return { /* ... */, userRole: readonly(userRole), isAdmin }
}
```

---

### 3.6 API 层整合

```typescript
// ScienceClaw/frontend/src/api/cases.ts (新增)
export interface CreateCaseRequest {
  title: string
  target_repo: string
  input_context: string
  contribution_type?: string
}

export interface ReviewDecision {
  action: 'approve' | 'reject' | 'reject_to' | 'modify' | 'abandon'
  comment?: string
  reject_to_stage?: string
  modified_artifacts?: Record<string, string>
}

export async function createCase(data: CreateCaseRequest): Promise<Case>
export async function listCases(params?: ListCasesParams): Promise<PaginatedCases>
export async function getCase(caseId: string): Promise<Case>
export async function deleteCase(caseId: string): Promise<void>
export async function startPipeline(caseId: string): Promise<void>
export async function submitReview(caseId: string, decision: ReviewDecision): Promise<void>
export async function getArtifacts(caseId: string, stage: string, round?: number): Promise<Artifact[]>
export async function getHistory(caseId: string): Promise<ReviewRecord[]>
export function subscribeCaseEvents(caseId: string, callbacks: SSECallbacks): Promise<() => void>

// ScienceClaw/frontend/src/api/reviews.ts (新增)
export async function getReviewVerdict(caseId: string, iteration: number): Promise<ReviewVerdict>

// ScienceClaw/frontend/src/api/artifacts.ts (新增)
export async function downloadArtifact(caseId: string, path: string): Promise<Blob>
export async function getArtifactContent(caseId: string, path: string): Promise<string>
```

---

## 4. 后端重构计划

### 4.1 FastAPI 路由重构

```python
# ScienceClaw/backend/main.py (改造)
from backend.route.cases import router as cases_router        # 新增
from backend.route.reviews import router as reviews_router    # 新增
from backend.route.artifacts import router as artifacts_router # 新增
from backend.route.pipeline import router as pipeline_router  # 新增

app.include_router(auth_router, prefix="/api/v1")
app.include_router(sessions_router, prefix="/api/v1")      # 保留
app.include_router(file_router, prefix="/api/v1")          # 保留
app.include_router(models_router, prefix="/api/v1")        # 保留
app.include_router(tooluniverse_router, prefix="/api/v1")  # 保留
app.include_router(task_settings_router, prefix="/api/v1") # 保留
app.include_router(memory_router, prefix="/api/v1")        # 保留
app.include_router(science_router, prefix="/api/v1")       # 保留
app.include_router(chat_router, prefix="/api/v1")          # 保留
app.include_router(statistics_router, prefix="/api/v1")    # 保留（改造 endpoint）
app.include_router(im_router, prefix="/api/v1")            # 保留

# 新增 Pipeline 路由
app.include_router(cases_router, prefix="/api/v1")
app.include_router(reviews_router, prefix="/api/v1")
app.include_router(artifacts_router, prefix="/api/v1")
app.include_router(pipeline_router, prefix="/api/v1")
```

**各路由文件职责**：

| 路由文件 | 职责 | 来源 |
|----------|------|------|
| `route/auth.py` | 登录/注册/Token 刷新/用户信息 | ScienceClaw 保留 |
| `route/sessions.py` | 会话 CRUD / Chat SSE / 文件上传 / 技能工具管理 | ScienceClaw 保留 |
| `route/chat.py` | 通用聊天 / 定时解析 | ScienceClaw 保留 |
| `route/models.py` | 模型配置 / 上下文窗口检测 | ScienceClaw 保留 |
| `route/file.py` | 文件下载 / 签名 URL | ScienceClaw 保留 |
| `route/tooluniverse.py` | 工具宇宙查询 / 分类 / 执行 | ScienceClaw 保留 |
| `route/task_settings.py` | 任务设置 | ScienceClaw 保留 |
| `route/memory.py` | 记忆管理 | ScienceClaw 保留 |
| `route/science.py` | 科学工具 / Prompt 优化 | ScienceClaw 保留 |
| `route/statistics.py` | 统计摘要 / 模型 / 趋势 / 会话 | ScienceClaw 保留（endpoint 改为 /statistics） |
| `route/im.py` | 飞书绑定 / 微信控制 / 设置 | ScienceClaw 保留 |
| `route/cases.py` | **案例 CRUD / Pipeline 启动 / SSE 事件流 / 产物获取 / 历史记录** | **新增** |
| `route/reviews.py` | **人工审核提交 / 审核历史 / Verdict 获取** | **新增** |
| `route/artifacts.py` | **产物下载 / 内容读取 / 路径浏览** | **新增** |
| `route/pipeline.py` | **Pipeline 内部控制 / 状态查询 / 强制停止** | **新增** |

---

### 4.2 LangGraph Pipeline 引擎

```
ScienceClaw/backend/pipeline/
├── __init__.py
├── graph.py              # StateGraph 构建与编译
├── state.py              # PipelineState Pydantic 模型
├── nodes/                # Agent 节点实现
│   ├── __init__.py
│   ├── explore.py        # Explorer Agent (Claude SDK)
│   ├── plan.py           # Planner Agent (OpenAI SDK)
│   ├── develop.py        # Developer Agent (Claude SDK)
│   ├── review.py         # Reviewer Agent (OpenAI/Codex SDK)
│   ├── test.py           # Tester Agent (Claude SDK)
│   ├── human_gate.py     # 人工审批门 (interrupt)
│   └── escalate.py       # 升级处理节点
├── routes.py             # 条件边路由函数
├── cost_guard.py         # 成本熔断器
├── event_publisher.py    # Redis Pub/Sub 事件发布
└── artifact_manager.py   # 产物文件系统管理
```

**StateGraph 定义**（严格按 design.md §5.2）：

```python
# pipeline/graph.py
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

# 9 个节点 + 1 个入口 + 3 个人工门 + 1 个升级节点
NODES = [
    "explore", "human_gate_explore",
    "plan", "human_gate_plan",
    "develop", "review", "human_gate_code",
    "test", "human_gate_test",
    "escalate"
]

# 条件边映射
HUMAN_GATE_ROUTES = {
    "human_gate_explore": {"approve": "plan", "reject": "explore", "abandon": END},
    "human_gate_plan": {"approve": "develop", "reject": "plan", "abandon": END},
    "human_gate_code": {"approve": "test", "reject": "develop", "abandon": END},
    "human_gate_test": {"approve": END, "reject": "develop", "abandon": END},
}

REVIEW_ROUTES = {
    "approve": "human_gate_code",
    "reject": "develop",
    "escalate": "escalate",
}
```

---

### 4.3 Agent 适配器层

```
ScienceClaw/backend/adapters/
├── __init__.py
├── base.py               # AgentAdapter 抽象基类
├── claude_adapter.py     # Claude Agent SDK 适配器
├── openai_adapter.py     # OpenAI Agents SDK 适配器
└── event_mapper.py       # 统一事件映射
```

**关键实现约束**（按 design.md §2.6, §3.4）：

1. **Claude Agent Adapter**：
   - 子进程模型，每次 `query()` 启动独立运行时
   - `cancel()` 通过 `SIGTERM` 终止子进程
   - 超时控制：30 分钟
   - 支持 `resume: sessionId` 会话恢复

2. **OpenAI Agent Adapter**：
   - 库原生模型，当前进程内执行
   - `Runner.run()` 驱动
   - 支持 `output_type=PydanticModel` 结构化输出
   - `RunState.to_state()` / `from_json()` 持久化

3. **统一接口**：
   - 对外暴露 `AsyncIterator[AgentEvent]`
   - `AgentEvent` 包含 `event_type` 和 `data`

---

### 4.4 数据源接入层

```
ScienceClaw/backend/datasources/
├── __init__.py
├── patchwork.py          # Patchwork API 客户端
├── mailing_list.py       # lore.kernel.org / groups.io 邮件解析
├── github_client.py      # GitHub API (OpenSBI, riscv-tests)
└── isa_registry.py       # RISC-V ISA 扩展注册表验证
```

---

### 4.5 产物与审计系统

```
ScienceClaw/backend/contracts/        # Pydantic 数据契约
├── __init__.py
├── exploration.py        # ExplorationResult, Evidence
├── planning.py           # ExecutionPlan, DevStep, TestCase
├── development.py        # DevelopmentResult
├── review.py             # ReviewVerdict, ReviewFinding
└── testing.py            # TestResult

ScienceClaw/backend/db/
├── mongo.py              # MongoDB 连接（ScienceClaw 现有）
├── collections.py        # 集合初始化与索引
└── audit.py              # 审计日志写入
```

---

### 4.6 SSE 事件总线

```python
# pipeline/event_publisher.py
class PipelineEventPublisher:
    """桥接 LangGraph 节点 → Redis Pub/Sub → FastAPI SSE"""

    async def publish(self, case_id: str, event_type: str, data: dict):
        # 1. 序列号递增
        # 2. 发布到 Redis Pub/Sub (实时)
        # 3. 写入 Redis Stream (重连恢复，保留 500 条)

    async def get_events_since(self, case_id: str, last_seq: int) -> list[PipelineEvent]:
        # 重连时恢复丢失事件
```

**SSE Endpoint**（cases 路由中）：
```python
@router.get("/cases/{case_id}/events")
async def case_events(case_id: str, last_event_id: int | None = Header(None, alias="Last-Event-ID")):
    # 1. 重连恢复：发送 missed events
    # 2. 实时订阅 Redis Pub/Sub
    # 3. 心跳（每 30 秒）
```

---

### 4.7 认证鉴权重构

```python
# auth/dependencies.py (扩展)

# 现有：get_current_user, get_db
# 新增：

def require_role(*roles: str):
    """角色权限装饰器"""
    async def checker(user: User = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return checker

# 使用示例
@router.delete("/cases/{case_id}")
async def delete_case(case_id: str, user: User = Depends(require_role("admin"))):
    ...
```

**RBAC 权限矩阵**（按 design.md §5.11）：

| 权限 | admin | user |
|------|-------|------|
| 创建案例 | ✅ | ✅ |
| 启动 Pipeline | ✅ | ✅ |
| 提交审核决策 | ✅ | ✅ |
| 查看案例详情 | ✅ | ✅ |
| 查看实时日志 | ✅ | ✅ |
| Chat 对话 | ✅ | ✅ |
| 管理用户 | ✅ | ❌ |
| 管理系统设置 | ✅ | ❌ |
| 删除案例 | ✅ | ❌ |
| 查看全部统计 | ✅ | ❌ (user 仅看自己) |

---

## 5. 数据库重构

### 5.1 MongoDB Schema 变更

**保留 ScienceClaw 现有集合**（零变更）：
- `sessions` — Chat 会话
- `users` — 用户
- `files` — 文件元数据
- `tasks` / `task_runs` — 定时任务
- `models` — 模型配置
- `memories` — 记忆
- `im_settings` — IM 配置

**新增集合**：

```javascript
// contribution_cases — 案例主集合
db.createCollection("contribution_cases", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["title", "status", "target_repo", "created_at", "updated_at"],
      properties: {
        _id: { bsonType: "string" },
        title: { bsonType: "string" },
        status: {
          enum: [
            "created", "exploring", "pending_explore_review",
            "planning", "pending_plan_review",
            "developing", "reviewing", "pending_code_review",
            "testing", "pending_test_review",
            "completed", "abandoned", "escalated"
          ]
        },
        target_repo: { bsonType: "string" },
        input_context: { bsonType: "object" },
        exploration_result: { bsonType: "object" },
        execution_plan: { bsonType: "object" },
        development_result: { bsonType: "object" },
        review_verdict: { bsonType: "object" },
        test_result: { bsonType: "object" },
        review_iterations: { bsonType: "int" },
        cost: {
          bsonType: "object",
          properties: {
            input_tokens: { bsonType: "int" },
            output_tokens: { bsonType: "int" },
            estimated_usd: { bsonType: "double" }
          }
        },
        created_by: { bsonType: "string" },  // user_id
        created_at: { bsonType: "date" },
        updated_at: { bsonType: "date" },
        abandoned_at: { bsonType: "date" }
      }
    }
  }
})

// human_reviews — 人工审核记录
db.createCollection("human_reviews")
// 字段: case_id, stage, action, comment, reviewer, created_at

// audit_log — 审计日志 (append-only)
db.createCollection("audit_log")
// 字段: case_id, event_type, data, user, timestamp

// stage_outputs — 阶段产物引用 (可选，用于大产物)
db.createCollection("stage_outputs")
// 字段: case_id, stage, round_num, document, created_at
```

**新增索引**：
```javascript
db.contribution_cases.createIndex({ status: 1, created_at: -1 })
db.contribution_cases.createIndex({ target_repo: 1 })
db.contribution_cases.createIndex({ created_by: 1 })
db.contribution_cases.createIndex({ abandoned_at: 1 },
  { expireAfterSeconds: 7776000, partialFilterExpression: { status: "abandoned" } })

db.human_reviews.createIndex({ case_id: 1, created_at: -1 })
db.audit_log.createIndex({ case_id: 1, timestamp: -1 })
db.audit_log.createIndex({ timestamp: 1 }, { expireAfterSeconds: 63072000 }) // 2年TTL
```

---

### 5.2 PostgreSQL Checkpointer

```python
# 专用于 LangGraph 状态持久化，不存业务数据
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

# 自动管理的表：
# - checkpoints (状态快照)
# - checkpoint_blobs (大型状态数据)
# - checkpoint_writes (写入记录)
```

---

### 5.3 Redis 使用策略

| 用途 | Key 模式 | TTL |
|------|----------|-----|
| SSE Pub/Sub | `case:{case_id}:events` | 实时 |
| SSE Stream (重连恢复) | `case:{case_id}:stream` | 500 条 maxlen |
| Token 限流计数 | `rate_limit:{user_id}` | 1 分钟 |
| 会话状态缓存 | `session:{session_id}` | 1 小时 |
| Pipeline 状态缓存 | `pipeline:{case_id}` | 24 小时 |

---

## 6. API 契约

### 6.1 保留的 ScienceClaw API

以下 API **零变更保留**，前端直接复用：

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/login` | 登录 |
| POST | `/api/v1/auth/register` | 注册 |
| GET | `/api/v1/auth/status` | 认证状态 |
| GET | `/api/v1/auth/me` | 当前用户 |
| PUT | `/api/v1/sessions` | 创建会话 |
| GET | `/api/v1/sessions` | 会话列表 |
| GET | `/api/v1/sessions/:id` | 会话详情 |
| DELETE | `/api/v1/sessions/:id` | 删除会话 |
| PATCH | `/api/v1/sessions/:id/pin` | 置顶/取消置顶 |
| PATCH | `/api/v1/sessions/:id/title` | 重命名会话 |
| POST | `/api/v1/sessions/:id/chat` | SSE Chat |
| POST | `/api/v1/sessions/:id/stop` | 停止会话 |
| POST | `/api/v1/sessions/:id/share` | 分享会话 |
| DELETE | `/api/v1/sessions/:id/share` | 取消分享 |
| POST | `/api/v1/sessions/:id/upload` | 文件上传 |
| GET | `/api/v1/sessions/:id/files` | 会话文件列表 |
| GET | `/api/v1/sessions/notifications` | 会话通知 SSE |
| POST | `/api/v1/chat` | 通用聊天 |
| GET | `/api/v1/models` | 模型列表 |
| POST | `/api/v1/models` | 创建模型配置 |
| PUT | `/api/v1/models/:id` | 更新模型配置 |
| DELETE | `/api/v1/models/:id` | 删除模型配置 |
| GET | `/api/v1/tooluniverse/tools` | 工具列表 |
| GET | `/api/v1/tooluniverse/tools/:name` | 工具详情 |
| POST | `/api/v1/tooluniverse/tools/:name/run` | 执行工具 |
| GET | `/api/v1/tooluniverse/categories` | 工具分类 |
| GET | `/api/v1/files/:id/download` | 文件下载 |
| POST | `/api/v1/files/:id/signed-url` | 签名 URL |
| GET | `/api/v1/memory` | 记忆列表 |
| POST | `/api/v1/memory` | 创建记忆 |
| GET | `/api/v1/im/bind/lark/status` | 飞书绑定状态 |
| POST | `/api/v1/im/bind/lark` | 绑定飞书 |
| DELETE | `/api/v1/im/bind/lark` | 解绑飞书 |
| GET | `/api/v1/im/settings` | IM 设置 |
| PUT | `/api/v1/im/settings` | 更新 IM 设置 |
| GET | `/api/v1/task-settings` | 任务设置 |
| PUT | `/api/v1/task-settings` | 更新任务设置 |

---

### 6.2 新增的 Pipeline API

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/v1/cases` | 创建案例 | ✅ |
| GET | `/api/v1/cases` | 案例列表（分页/筛选） | ✅ |
| GET | `/api/v1/cases/:id` | 案例详情 | ✅ |
| DELETE | `/api/v1/cases/:id` | 删除案例 | ✅ admin |
| POST | `/api/v1/cases/:id/start` | 启动 Pipeline | ✅ |
| GET | `/api/v1/cases/:id/events` | SSE 事件流 | ✅ |
| POST | `/api/v1/cases/:id/review` | 提交人工审核 | ✅ |
| GET | `/api/v1/cases/:id/artifacts` | 获取阶段产物列表 | ✅ |
| GET | `/api/v1/cases/:id/artifacts/:path` | 获取产物内容 | ✅ |
| GET | `/api/v1/cases/:id/history` | 审核历史 | ✅ |
| POST | `/api/v1/cases/:id/stop` | 强制停止 Pipeline | ✅ |
| GET | `/api/v1/pipeline/status` | 系统 Pipeline 状态 | ✅ admin |

---

### 6.3 变更的 API

| 方法 | 原路径 | 新路径 | 变更说明 |
|------|--------|--------|----------|
| GET | `/api/v1/metrics/overview` | `/api/v1/statistics/summary` | 路径变更，增加 Pipeline 统计数据 |
| GET | `/api/v1/metrics/costs` | `/api/v1/statistics/costs` | 路径变更，增加按案例成本 |
| GET | `/api/v1/metrics/models` | `/api/v1/statistics/models` | 路径变更 |
| GET | `/api/v1/metrics/trends` | `/api/v1/statistics/trends` | 路径变更 |
| GET | `/api/v1/metrics/sessions` | `/api/v1/statistics/sessions` | 路径变更 |

---

## 7. 实现阶段规划

### 7.0 时间线总览

```
Week:  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16
       ├─Phase 0─┤  ├─Phase 1─┤  ├────Phase 2────┤  ├────Phase 3────┤  ├─Phase 4─┤
       基础架构    Chat 迁移    Pipeline 后端      Pipeline 前端      高级功能

里程碑:
M0 (W2): 基础架构就绪，所有服务可启动
M1 (W4): Chat 功能 100% 迁移完成
M2 (W8): Pipeline 后端可跑通单阶段
M3 (W12): Pipeline 前后端联调完成
M4 (W14): E2E 测试通过，可演示完整案例
M5 (W16): 生产就绪，性能/安全/监控完备
```

---

### 7.1 Phase 0: 基础架构（2周）

**目标**: 搭建双模式开发基础，确保 ScienceClaw 功能无损

#### Week 1: 基础设施

| 任务 ID | 任务 | 详情 | 产出 | 负责人 | 阻塞项 |
|---------|------|------|------|--------|--------|
| P0.1 | 创建缺失设计文档 | `mvp-tasks.md`, `migration-map.md`, `chat-architecture.md`, `conventions.md` | 4 份文档 | Tech Lead | 无 |
| P0.2 | 初始化后端目录结构 | `ScienceClaw/backend/pipeline/`, `adapters/`, `datasources/`, `contracts/` | 目录框架 | Backend Dev | 无 |
| P0.3 | Docker Compose 扩展 | 增加 `postgres`, `qemu-sandbox` 服务 | `docker-compose.yml` | DevOps | 无 |
| P0.4 | PostgreSQL 初始化脚本 | `postgres-init.sql` 创建 checkpointer 表 | SQL 脚本 | Backend Dev | P0.2 |
| P0.5 | MongoDB 索引脚本 | `mongo-init.js` 创建 cases/audit 索引 | JS 脚本 | Backend Dev | P0.2 |
| P0.6 | 认证扩展 | User 模型增加 `role` 字段，RBAC 中间件 | `user.py`, `dependencies.py` | Backend Dev | 无 |

#### Week 2: 验证与配置

| 任务 ID | 任务 | 详情 | 产出 | 负责人 | 阻塞项 |
|---------|------|------|------|--------|--------|
| P0.7 | 环境变量配置 | `.env.example` 更新所有新配置项 | 配置文件 | DevOps | P0.3 |
| P0.8 | 依赖锁定 | `requirements.txt` 追加新依赖 | 依赖文件 | Backend Dev | P0.2 |
| P0.9 | 健康检查端点 | `/health` 扩展检查 PostgreSQL | `main.py` | Backend Dev | P0.3 |
| P0.10 | 回归测试基线 | 记录 ScienceClaw 功能测试通过基线 | 测试报告 | QA | P0.6 |
| P0.11 | CI/CD 配置 | GitHub Actions 增加 Pipeline 阶段检查 | `.github/workflows/ci.yml` | DevOps | 无 |

**Phase 0 DoD (Definition of Done)**:
- [x] `docker compose up` 成功启动 10+ 个服务 ✅（12 个服务定义）
- [x] `pytest` 现有测试全部通过 ✅（16 个测试通过）
- [x] `pnpm build` 前端构建成功 ✅
- [x] admin/user 双角色认证正常 ✅
- [x] PostgreSQL checkpointer 表自动创建 ✅
- [x] 所有新目录结构就绪 ✅
- [ ] MongoDB 索引自动创建 ❌（`db/collections.py` 函数体为空）

---

### 7.2 Phase 1: Chat 模式完整迁移（2周）

**目标**: 将 ScienceClaw 前端功能完整迁移到 rv-claw，零功能丢失

#### Week 3: 前端路由与布局

| 任务 ID | 任务 | 详情 | 产出 | 阻塞项 |
|---------|------|------|------|--------|
| P1.1 | 路由重构 | 新增 `/cases/*` 路由，保留现有路由 | `router/index.ts` | 无 |
| P1.2 | LeftPanel 扩展 | 增加 "Cases" 导航入口 | `LeftPanel.vue` | P1.1 |
| P1.3 | MainLayout 改造 | 整合 Cases 导航状态 | `MainLayout.vue` | P1.2 |
| P1.4 | 类型定义 | 创建 `case.ts`, `pipeline.ts`, `event.ts`, `artifact.ts`, `review.ts` | `types/*.ts` | 无 |
| P1.5 | API 类型定义 | cases/reviews/artifacts API 请求/响应类型 | `api/types.ts` | P1.4 |

#### Week 4: API 与设置

| 任务 ID | 任务 | 详情 | 产出 | 阻塞项 |
|---------|------|------|------|--------|
| P1.6 | Statistics API 迁移 | `/metrics/*` → `/statistics/*` | `statistics.py` | 无 |
| P1.7 | StatisticsPage | 替换 MetricsView，增加 Pipeline 统计 | `StatisticsPage.vue` | P1.6 |
| P1.8 | Settings 扩展 | 新增 PipelineSettings Tab | `PipelineSettings.vue` | 无 |
| P1.9 | API 层整合 | 导出 cases, reviews, artifacts API | `api/index.ts` | P1.5 |
| P1.10 | i18n 扩展 | 新增 Pipeline 相关翻译键（中英文） | `locales/*.ts` | 无 |
| P1.11 | E2E 基线测试 | 验证所有 ScienceClaw 页面可访问 | 测试通过 | P1.1-P1.10 |

**Phase 1 DoD**:
- [x] 所有 ScienceClaw 页面可正常访问且功能完整 ✅
- [x] 新增 `/cases` 路由可访问 ✅
- [ ] 设置系统新增 PipelineSettings Tab ❌（未实现）
- [x] 统计 API endpoint 迁移完成 ✅
- [x] E2E 回归测试基线通过 ✅（Playwright 13/14 测试通过）
- [ ] 前端 Vitest 单元测试基础设施 ❌（未配置）
- [ ] Mock Server 可用 ❌（未实现）
- [ ] OpenAPI → TS 自动生成链路 ❌（未实现）

---

### 7.3 Phase 2: Pipeline 后端骨架（4周）

**目标**: 实现 Pipeline 后端核心，包括 LangGraph 引擎、Agent 节点、SSE 事件流

#### Week 5-6: Pipeline 基础设施

| 任务 ID | 任务 | 详情 | 产出 | 阻塞项 | 复杂度 |
|---------|------|------|------|--------|--------|
| P2.1 | PipelineState 模型 | TypedDict 定义所有状态字段 | `state.py` | 无 | ⭐⭐ |
| P2.2 | StateGraph 构建 | 9 节点 + 4 门 + 条件边定义 | `graph.py` | P2.1 | ⭐⭐⭐ |
| P2.3 | AgentAdapter 基类 | 抽象基类 + 统一 AgentEvent 模型 | `adapters/base.py` | 无 | ⭐⭐ |
| P2.4 | ClaudeAgentAdapter | 子进程模型实现 | `claude_adapter.py` | P2.3 | ⭐⭐⭐⭐ |
| P2.5 | OpenAIAgentAdapter | 库原生模型实现 | `openai_adapter.py` | P2.3 | ⭐⭐⭐ |
| P2.6 | EventPublisher | Redis Pub/Sub + Stream 实现 | `event_publisher.py` | 无 | ⭐⭐⭐ |
| P2.7 | ArtifactManager | 文件系统产物管理 | `artifact_manager.py` | 无 | ⭐⭐ |
| P2.8 | CostCircuitBreaker | 成本熔断器装饰器 | `cost_guard.py` | 无 | ⭐⭐ |

#### Week 7: Agent 节点实现（上）

| 任务 ID | 任务 | 详情 | 产出 | 阻塞项 | 复杂度 |
|---------|------|------|------|--------|--------|
| P2.9 | explore_node | Explorer Agent (Claude SDK) | `nodes/explore.py` | P2.4 | ⭐⭐⭐⭐ |
| P2.10 | plan_node | Planner Agent (OpenAI SDK) | `nodes/plan.py` | P2.5 | ⭐⭐⭐ |
| P2.11 | develop_node | Developer Agent (Claude SDK) | `nodes/develop.py` | P2.4 | ⭐⭐⭐⭐ |
| P2.12 | human_gate_node | 人工审批门 (interrupt) | `nodes/human_gate.py` | P2.2 | ⭐⭐⭐ |
| P2.13 | route_human_decision | 人工决策路由函数 | `routes.py` | P2.12 | ⭐⭐ |

#### Week 8: Agent 节点实现（下）

| 任务 ID | 任务 | 详情 | 产出 | 阻塞项 | 复杂度 |
|---------|------|------|------|--------|--------|
| P2.14 | review_node | Reviewer Agent + 确定性工具 | `nodes/review.py` | P2.5 | ⭐⭐⭐⭐ |
| P2.15 | test_node | Tester Agent + QEMU 集成 | `nodes/test.py` | P2.4 | ⭐⭐⭐⭐ |
| P2.16 | route_review_decision | 迭代收敛检测路由 | `routes.py` | P2.14 | ⭐⭐⭐ |
| P2.17 | escalate_node | 升级处理节点 | `nodes/escalate.py` | P2.2 | ⭐⭐ |
| P2.18 | 数据源实现 | PatchworkClient, MailingListCrawler | `datasources/*.py` | P2.9 | ⭐⭐⭐ |

**并行任务 Week 7-8**: API 路由实现

| 任务 ID | 任务 | 详情 | 产出 | 阻塞项 |
|---------|------|------|------|--------|
| P2.19 | cases 路由 | CRUD + start + events SSE | `route/cases.py` | P2.2 |
| P2.20 | reviews 路由 | submit + history | `route/reviews.py` | P2.12 |
| P2.21 | artifacts 路由 | download + content | `route/artifacts.py` | P2.7 |
| P2.22 | pipeline 路由 | status + stop | `route/pipeline.py` | P2.2 |

**Phase 2 DoD**:
- [x] 可通过 API 创建案例并启动 Pipeline ✅
- [x] SSE 事件流正常推送阶段变更 ✅
- [x] 人工审核门可暂停并恢复 Pipeline ✅
- [x] 产物文件正确写入文件系统 ✅（ArtifactManager 实现完整）
- [~] 3 轮 Develop↔Review 迭代正常 ⚠️（结构支持，但节点为占位符，无真实迭代）
- [~] 成本熔断器在超限时报错 ⚠️（实现完整，但未被调用，无测试验证）
- [ ] 单元测试覆盖率 ≥ 70% ❌（仅 16 个测试，大量模块无覆盖）

---

### 7.4 Phase 3: Pipeline 前端与集成（4周）

**目标**: 实现 Pipeline 前端全部组件，与后端联调

#### Week 9: 基础组件

| 任务 ID | 任务 | 详情 | 产出 | 阻塞项 |
|---------|------|------|------|--------|
| P3.1 | CaseListView | 案例列表 + 筛选/搜索 | `views/CaseListView.vue` | P1.4 |
| P3.2 | CaseDetailView 骨架 | 三栏布局（左/中/右） | `views/CaseDetailView.vue` | P3.1 |
| P3.3 | PipelineView | 5 阶段流水线可视化 | `components/pipeline/PipelineView.vue` | P3.2 |
| P3.4 | StageNode | 单阶段节点组件 | `components/pipeline/StageNode.vue` | P3.3 |
| P3.5 | useCaseEvents | SSE 事件流管理 composable | `composables/useCaseEvents.ts` | 无 |

#### Week 10: 审核组件

| 任务 ID | 任务 | 详情 | 产出 | 阻塞项 |
|---------|------|------|------|--------|
| P3.6 | HumanGate | 人工审核门禁 UI | `components/pipeline/HumanGate.vue` | P3.5 |
| P3.7 | ReviewPanel | 审核决策面板 | `components/review/ReviewPanel.vue` | P3.6 |
| P3.8 | ReviewFinding | 单条审核发现 | `components/review/ReviewFinding.vue` | P3.7 |
| P3.9 | DiffViewer | Monaco Diff 查看器 | `components/review/DiffViewer.vue` | P3.8 |
| P3.10 | ReviewHistory | 历史审核记录 | `components/review/ReviewHistory.vue` | P3.7 |

#### Week 11: 阶段展示组件

| 任务 ID | 任务 | 详情 | 产出 | 阻塞项 |
|---------|------|------|------|--------|
| P3.11 | ContributionCard | 探索结果卡片 | `components/exploration/ContributionCard.vue` | P3.2 |
| P3.12 | EvidenceChain | 证据链展示 | `components/exploration/EvidenceChain.vue` | P3.11 |
| P3.13 | ExecutionPlanTree | 执行计划树 | `components/planning/ExecutionPlanTree.vue` | P3.2 |
| P3.14 | TestResultSummary | 测试结果摘要 | `components/testing/TestResultSummary.vue` | P3.2 |
| P3.15 | AgentEventLog | 实时事件日志 | `components/shared/AgentEventLog.vue` | P3.5 |

#### Week 12: API 集成与测试

| 任务 ID | 任务 | 详情 | 产出 | 阻塞项 |
|---------|------|------|------|--------|
| P3.16 | cases.ts API | API 客户端实现 | `api/cases.ts` | P2.19 |
| P3.17 | reviews.ts API | 审核 API 客户端 | `api/reviews.ts` | P2.20 |
| P3.18 | artifacts.ts API | 产物 API 客户端 | `api/artifacts.ts` | P2.21 |
| P3.19 | 前后端联调 | 打通完整流程 | 可运行 Demo | P3.1-P3.18 |
| P3.20 | E2E 测试 | 案例生命周期测试 | Playwright 测试 | P3.19 |

**Phase 3 DoD**:
- [x] 可从前端创建案例并启动 Pipeline ✅
- [x] Pipeline 可视化实时更新阶段状态 ✅
- [x] 人工审核面板在 pending 状态时正确显示 ✅
- [~] DiffViewer 正确渲染补丁和 findings 高亮 ⚠️（基础 diff 渲染完成，无 Monaco 集成，无 findings 高亮）
- [ ] AgentEventLog 实时显示 Agent 执行过程 ❌（独立组件不存在）
- [~] E2E 测试覆盖完整案例生命周期 ⚠️（Playwright 基础 E2E 通过，未覆盖完整 UI 生命周期）

---

### 7.5 Phase 4: 集成测试与优化（3周）

**目标**: 系统联调、性能优化、混沌测试、安全加固

#### Week 13: 集成与稳定性

| 任务 ID | 任务 | 详情 | 产出 | 阻塞项 |
|---------|------|------|------|--------|
| P4.1 | 端到端联调 | Chat + Pipeline 双模式切换 | 完整系统 | P3.20 |
| P4.2 | 性能基准测试 | API P99 < 500ms | 测试报告 | P4.1 |
| P4.3 | SSE 压力测试 | 100 连接并发 | 测试报告 | P4.1 |
| P4.4 | 内存泄漏检测 | 长时间运行稳定性 | 检测报告 | P4.1 |

#### Week 14: 高级功能

| 任务 ID | 任务 | 详情 | 产出 | 阻塞项 |
|---------|------|------|------|--------|
| P4.5 | QEMU Sandbox | Docker 镜像 + 集成 | `sandbox-qemu/` | P2.15 |
| P4.6 | 确定性工具 | checkpatch.pl, sparse 集成 | `nodes/review.py` | P4.5 |
| P4.7 | Prompt Guard | 注入检测 | `security/prompt_guard.py` | 无 |
| P4.8 | 速率限制 | Redis 限流中间件 | `middleware/rate_limit.py` | 无 |

#### Week 15: 混沌工程与安全

| 任务 ID | 任务 | 详情 | 产出 | 阻塞项 |
|---------|------|------|------|--------|
| P4.9 | 故障注入测试 | 服务重启/网络中断恢复 | 测试报告 | P4.1 |
| P4.10 | 安全扫描 | bandit, safety, npm audit | 扫描报告 | 无 |
| P4.11 | 渗透测试 | OWASP Top 10 检查 | 测试报告 | P4.10 |
| P4.12 | 数据备份恢复 | MongoDB/PostgreSQL 备份 | 脚本 + 测试 | 无 |

**Phase 4 DoD**:
- [ ] QEMU 沙箱可正确编译和运行 RISC-V 测试 ❌（docker-compose 中为 sleep infinity 占位符）
- [ ] checkpatch.pl 和 sparse 在 Review 阶段自动运行 ❌（review_node 为占位符）
- [ ] API 速率限制生效 ❌（未实现）
- [ ] 故障恢复测试通过（服务重启后 Pipeline 可恢复）❌（未测试）
- [ ] 性能测试通过（50 并发 API, 100 SSE 连接）❌（未实现）
- [ ] 安全扫描无高危漏洞 ❌（未执行）

---

### 7.6 Phase 5: 生产准备（1周）

**目标**: 文档完善、部署验证、培训

| 任务 ID | 任务 | 详情 | 产出 |
|---------|------|------|------|
| P5.1 | 部署文档 | 完整部署指南 | `docs/deployment-guide.md` |
| P5.2 | API 文档 | OpenAPI 自动生成 | Swagger UI |
| P5.3 | 运维手册 | 监控/告警/故障处理 | `docs/operations.md` |
| P5.4 | 用户手册 | 最终用户指南 | `docs/user-guide.md` |
| P5.5 | 生产环境部署 | 真实环境验证 | 生产可用系统 |
| P5.6 | 团队培训 | 使用与运维培训 | 培训完成 |

**Phase 5 DoD**:
- [ ] 生产环境部署成功 ❌
- [~] 所有文档完备 ⚠️（docs/ 目录存在但需人工核查完备性）
- [ ] 团队培训完成 ❌
- [ ] 上线检查清单全部通过 ❌

---

## 8. 测试策略

### 8.1 测试金字塔

```
                    ┌─────────┐
                    │  E2E    │  ← 20 个场景，覆盖核心用户旅程
                    │  (10%)  │
                   ├───────────┤
                   │ Integration│ ← API 集成测试，边界情况
                   │   (20%)   │
                  ├─────────────┤
                  │    Unit      │ ← 业务逻辑、工具函数、路由决策
                  │   (70%)     │
                 └───────────────┘
```

---

### 8.2 测试分层详情

#### 单元测试（pytest）

| 模块 | 测试文件 | 覆盖目标 | 关键用例 |
|------|----------|----------|----------|
| Pipeline 路由 | `test_route_review.py` | 90% | 迭代收敛、escalate 触发 |
| Pipeline 路由 | `test_route_human.py` | 90% | approve/reject/abandon 路由 |
| 数据契约 | `test_contracts.py` | 95% | Pydantic 验证、序列化 |
| CostGuard | `test_cost_guard.py` | 85% | 熔断触发、成本累加 |
| ArtifactManager | `test_artifact_manager.py` | 80% | 文件存储/读取/清理 |
| EventPublisher | `test_event_publisher.py` | 75% | 事件发布/订阅/恢复 |

**示例单元测试**:
```python
# tests/unit/pipeline/test_route_review.py
import pytest
from backend.pipeline.routes import route_review_decision
from backend.pipeline.state import PipelineState

class TestRouteReviewDecision:
    """Review 路由决策单元测试"""

    def test_approve_when_verdict_approved(self):
        state = PipelineState(
            case_id="test",
            target_repo="linux",
            review_verdict={"approved": True, "findings": []},
            review_iterations=1,
        )
        assert route_review_decision(state) == "approve"

    def test_escalate_when_max_iterations_reached(self):
        state = PipelineState(
            case_id="test",
            target_repo="linux",
            review_verdict={"approved": False, "findings": [{"severity": "major"}]},
            review_iterations=3,
            max_review_iterations=3,
        )
        assert route_review_decision(state) == "escalate"

    def test_escalate_when_not_converging(self):
        """连续 2 轮评分不下降则 escalate"""
        state = PipelineState(
            case_id="test",
            target_repo="linux",
            review_verdict={"approved": False, "findings": [
                {"severity": "major", "file": "a.c", "line": 10}
            ]},
            review_iterations=2,
            review_history=[
                {"findings": [{"severity": "major", "file": "a.c", "line": 10}]}
            ]
        )
        assert route_review_decision(state) == "escalate"
```

#### 集成测试（pytest + testcontainers）

| 场景 | 测试文件 | 说明 |
|------|----------|------|
| Pipeline 完整流程 | `test_pipeline_flow.py` | 创建→启动→审核→完成 |
| 人工审核门禁 | `test_human_gate.py` | interrupt/resume 流程 |
| Develop↔Review 迭代 | `test_review_iteration.py` | 3 轮迭代 → escalate |
| 检查点恢复 | `test_checkpoint_recovery.py` | 中断后恢复 Pipeline |
| SSE 事件流 | `test_sse_events.py` | 事件顺序、重连恢复 |
| 产物管理 | `test_artifact_lifecycle.py` | 上传/下载/清理 |

**示例集成测试**:
```python
# tests/integration/test_pipeline_flow.py
import pytest
from testcontainers.mongodb import MongoDbContainer
from testcontainers.postgres import PostgresContainer

@pytest.fixture(scope="module")
async def app():
    with MongoDbContainer("mongo:7.0") as mongo, \
         PostgresContainer("postgres:16-alpine") as pg:
        app = create_app(
            mongo_uri=mongo.get_connection_url(),
            postgres_uri=pg.get_connection_url(),
        )
        yield app

class TestPipelineFlow:
    async def test_create_and_start_pipeline(self, client):
        # 创建案例
        resp = await client.post("/api/v1/cases", json={
            "title": "Test Zicfiss support",
            "target_repo": "linux",
            "input_context": {"hint": "Add Zicfiss"}
        })
        assert resp.status_code == 201
        case_id = resp.json()["data"]["id"]

        # 启动 Pipeline
        resp = await client.post(f"/api/v1/cases/{case_id}/start")
        assert resp.status_code == 200

        # 验证状态变为 exploring
        resp = await client.get(f"/api/v1/cases/{case_id}")
        assert resp.json()["data"]["status"] == "exploring"
```

#### E2E 测试（Playwright）

| 场景 | 测试文件 | 步骤 |
|------|----------|------|
| 完整案例生命周期 | `test_case_lifecycle.spec.ts` | 创建→启动→审核→完成 |
| Chat 对话 | `test_chat.spec.ts` | 登录→新建会话→聊天 |
| 文件管理 | `test_file_management.spec.ts` | 上传→预览→下载 |
| 设置修改 | `test_settings.spec.ts` | 修改模型→保存→验证 |
| 错误处理 | `test_error_handling.spec.ts` | 网络中断→恢复→继续 |

**示例 E2E 测试**:
```typescript
// tests/e2e/test_case_lifecycle.spec.ts
import { test, expect } from '@playwright/test';

test('完整案例生命周期', async ({ page }) => {
  // 登录
  await page.goto('/login');
  await page.fill('[data-testid="username"]', 'admin');
  await page.fill('[data-testid="password"]', 'admin123');
  await page.click('[data-testid="login-btn"]');
  await page.waitForURL('**/');

  // 创建案例
  await page.click('[data-testid="new-case-btn"]');
  await page.fill('[data-testid="case-title"]', 'E2E Test Case');
  await page.fill('[data-testid="target-repo"]', 'linux');
  await page.fill('[data-testid="input-context"]', 'Test context');
  await page.click('[data-testid="submit-case-btn"]');

  // 验证案例创建成功
  await page.waitForURL('**/cases/**');
  await expect(page.locator('[data-testid="case-status"]')).toHaveText('created');

  // 启动 Pipeline
  await page.click('[data-testid="start-pipeline-btn"]');
  await expect(page.locator('[data-testid="stage-explore"]')).toHaveClass(/active/);

  // 等待探索完成，提交审核
  await page.waitForSelector('[data-testid="review-panel"]', { timeout: 120000 });
  await page.fill('[data-testid="review-comment"]', 'Looks good');
  await page.click('[data-testid="approve-btn"]');

  // 验证进入 planning 阶段
  await expect(page.locator('[data-testid="stage-plan"]')).toHaveClass(/active/);
});
```

#### 混沌测试（Chaos Mesh / 手动）

| 故障场景 | 测试方法 | 期望结果 |
|----------|----------|----------|
| 后端重启 | `docker restart backend` | Pipeline 从 checkpointer 恢复 |
| MongoDB 中断 | `docker stop mongodb` | 优雅降级，返回 503 |
| Redis 中断 | `docker stop redis` | SSE 降级为轮询 |
| 网络延迟 | `tc qdisc add dev eth0 delay 500ms` | 超时重试正常 |
| 高并发 | `locust -f load_test.py -u 100` | 无死锁，响应时间可接受 |

### 8.3 回归测试策略

```bash
# 在迁移前建立基线
cd ScienceClaw
pytest tests/e2e/ --generate-baseline=baseline-v1.json

# 迁移后对比
cd rv-claw
pytest tests/e2e/ --compare-baseline=baseline-v1.json --threshold=95
```

---

## 9. 监控与可观测性

### 9.1 三大支柱

```
┌─────────────────────────────────────────────────────────────────┐
│                     可观测性三大支柱                              │
├─────────────────┬─────────────────┬─────────────────────────────┤
│    Metrics      │      Logs       │         Tracing             │
│    (指标)        │     (日志)       │         (追踪)              │
├─────────────────┼─────────────────┼─────────────────────────────┤
│ • Prometheus    │ • structlog     │ • OpenTelemetry             │
│ • Grafana       │ • JSON 结构化   │ • LangGraph 自带 trace      │
│ • 业务指标       │ • 日志级别动态   │ • 分布式追踪                 │
│ • 系统指标       │ • 日志采样      │ • 性能热点分析               │
└─────────────────┴─────────────────┴─────────────────────────────┘
```

---

### 9.2 业务指标（Prometheus）

```python
# backend/metrics/pipeline.py
from prometheus_client import Counter, Histogram, Gauge

# Pipeline 业务指标
PIPELINE_CREATED = Counter(
    'rv_pipeline_created_total',
    'Total cases created',
    ['contribution_type', 'target_repo']
)

PIPELINE_COMPLETED = Counter(
    'rv_pipeline_completed_total',
    'Total cases completed',
    ['status', 'contribution_type']
)

STAGE_DURATION = Histogram(
    'rv_stage_duration_seconds',
    'Time spent in each stage',
    ['stage'],
    buckets=[60, 300, 600, 1800, 3600, 7200]  # 1m, 5m, 10m, 30m, 1h, 2h
)

REVIEW_ITERATIONS = Histogram(
    'rv_review_iterations',
    'Number of review iterations',
    buckets=[1, 2, 3, 4]
)

COST_USD = Histogram(
    'rv_cost_usd',
    'Pipeline cost in USD',
    ['stage'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

ACTIVE_PIPELINES = Gauge(
    'rv_active_pipelines',
    'Number of active pipelines',
    ['stage']
)

# 在代码中使用
@router.post("/cases/{case_id}/start")
async def start_pipeline(case_id: str):
    PIPELINE_CREATED.inc()
    ACTIVE_PIPELINES.inc()
    # ... 启动逻辑
```

---

### 9.3 日志规范（structlog）

```python
# backend/logging_config.py
import structlog
import logging

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.filter_by_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

# 使用示例
logger = structlog.get_logger()

async def explore_node(state: PipelineState):
    logger.info(
        "stage_started",
        case_id=state["case_id"],
        stage="explore",
        target_repo=state["target_repo"],
        iteration=state["review_iterations"],
    )

    try:
        # ... 执行逻辑
        logger.info(
            "stage_completed",
            case_id=state["case_id"],
            stage="explore",
            duration_seconds=elapsed,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            cost_usd=result.cost_usd,
        )
    except Exception as e:
        logger.error(
            "stage_failed",
            case_id=state["case_id"],
            stage="explore",
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True,
        )
        raise
```

---

### 9.4 关键告警规则

```yaml
# prometheus/alerts.yml
groups:
  - name: rv-claw-pipeline
    rules:
      # Pipeline 卡住
      - alert: PipelineStuck
        expr: |
          time() - rv_stage_last_activity_seconds > 1800
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Pipeline {{ $labels.case_id }} stuck in {{ $labels.stage }}"

      # 成本异常
      - alert: HighPipelineCost
        expr: |
          rv_cost_usd_bucket{le="10.0"} > 0
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "Pipeline cost exceeded $10"

      # Agent 失败率高
      - alert: HighAgentFailureRate
        expr: |
          rate(rv_agent_errors_total[5m]) / rate(rv_agent_calls_total[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Agent failure rate > 10%"

      # 后端错误率高
      - alert: HighErrorRate
        expr: |
          rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Backend 5xx rate > 5%"

      # 数据库连接池耗尽
      - alert: DatabasePoolExhausted
        expr: |
          mongodb_connections{state="available"} < 5
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "MongoDB connection pool nearly exhausted"
```

---

## 10. 风险与缓解

### 10.1 风险矩阵

| 风险 | 概率 | 影响 | 风险值 | 优先级 |
|------|------|------|--------|--------|
| ScienceClaw 代码变更导致迁移冲突 | 高 | 高 | 🔴 高 | P0 |
| Claude Agent SDK Breaking Change | 高 | 高 | 🔴 高 | P0 |
| Pipeline 前端复杂度超预期 | 中 | 中 | 🟡 中 | P1 |
| LangGraph 0.3→0.4 API 变更 | 中 | 高 | 🟡 中 | P1 |
| QEMU 沙箱环境搭建困难 | 中 | 高 | 🟡 中 | P1 |
| OpenAI Codex 模型不可用 | 中 | 高 | 🟡 中 | P1 |
| SSE 长连接在 Nginx 下异常 | 中 | 中 | 🟡 中 | P1 |
| RISC-V 领域知识不足 | 中 | 高 | 🟡 中 | P2 |
| MongoDB 与 PG 双库运维 | 低 | 中 | 🟢 低 | P2 |

---

### 10.2 详细缓解措施

#### 风险 1: ScienceClaw 代码变更

**描述**: ScienceClaw 上游持续更新，导致迁移代码冲突

**缓解措施**:
1. **版本锁定**: 在 `P0.1` 时锁定 ScienceClaw commit hash
2. **抽象层**: 创建 `scienceclaw-compat/` 目录，封装所有移植代码
3. **自动化脚本**: 编写 `scripts/sync-scienceclaw.sh` 自动检测变更
4. **回归测试**: 每次 ScienceClaw 更新后运行全量回归测试

**应急方案**:
- 如果冲突过多，fork ScienceClaw 并维护稳定分支
- 优先保证 rv-claw 功能，延迟同步非关键更新

#### 风险 2: Claude Agent SDK Breaking Change

**描述**: SDK 尚处 Beta，API 可能大幅变更

**缓解措施**:
1. **适配器隔离**: 所有 SDK 调用通过 `adapters/claude_adapter.py`
2. **版本锁定**: `requirements.txt` 严格锁定 `claude-agent-sdk>=0.1.0,<0.2.0`
3. **功能降级**: 如果 SDK 不可用，降级到直接 Anthropic API 调用
4. **抽象接口**: `AgentAdapter` 基类确保可切换实现

**降级代码**:
```python
# adapters/claude_fallback.py
class ClaudeFallbackAdapter(AgentAdapter):
    """SDK 不可用时，直接调用 Anthropic API"""

    async def execute(self, prompt, context, working_dir=None):
        client = anthropic.Anthropic()
        async with client.messages.stream(
            model="claude-3-sonnet-20240229",
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            async for text in stream.text_stream:
                yield AgentEvent(event_type="output", data={"content": text})
```

#### 风险 3: Pipeline 前端复杂度

**描述**: Pipeline 可视化组件可能比预期复杂

**缓解措施**:
1. **MVP 简化**: Phase 3 先用简单列表代替复杂可视化
2. **组件复用**: 优先复用 ScienceClaw 的 `ActivityPanel`, `ProcessMessage`
3. **增量交付**: Week 9 完成骨架，Week 10-11 逐步丰富
4. **设计评审**: Week 9 结束进行设计评审，必要时简化

**简化方案**:
```
Plan A (完整): PipelineView → StageNode → StageConnector → Animation
Plan B (简化): ListView → StatusBadge → ProgressBar
Plan C (极简): TextLog → 纯文本展示阶段状态
```

#### 风险 4: LangGraph API 变更

**描述**: LangGraph 0.4 可能引入 Breaking Change

**缓解措施**:
1. **版本锁定**: `requirements.txt` 锁定 `langgraph>=0.3.0,<0.4.0`
2. **封装层**: 所有 LangGraph 调用通过 `pipeline/graph.py`
3. **单元测试**: 路由函数独立测试，不依赖 LangGraph 内部
4. **关注社区**: 订阅 LangGraph changelog，提前评估影响

---

## 11. 验收标准

### 11.1 功能验收

| 模块 | 验收项 | 通过标准 | 验证方式 |
|------|--------|----------|----------|
| Chat | 多轮对话 | 支持 10 轮以上上下文 | E2E 测试 |
| Chat | 文件上传 | 支持 10MB 文件 | 手动测试 |
| Chat | SSE 流式 | 延迟 < 1s | 性能测试 |
| Pipeline | 创建案例 | 必填字段验证 | 单元测试 |
| Pipeline | 5 阶段执行 | 阶段正确流转 | E2E 测试 |
| Pipeline | 人工审核 | 可暂停/恢复 | E2E 测试 |
| Pipeline | 3 轮迭代 | 收敛检测正确 | 单元测试 |
| Pipeline | 产物管理 | 文件正确存储 | 集成测试 |
| 系统 | RBAC | admin/user 权限区分 | 单元测试 |
| 系统 | 并发 | 5 Pipeline 同时运行 | 压力测试 |

---

### 11.2 性能验收

| 指标 | 目标 | 测试方法 |
|------|------|----------|
| API P99 | < 500ms | locust -u 50 -r 10 |
| SSE 延迟 | < 1s | WebSocket 测试工具 |
| 前端首屏 | < 2s | Lighthouse |
| 并发 Pipeline | 5 个无死锁 | 手动测试 |
| 内存使用 | < 4GB | docker stats |

---

### 11.3 质量验收

| 指标 | 目标 | 工具 |
|------|------|------|
| 单元测试覆盖率 | ≥ 85% | pytest-cov |
| E2E 测试通过率 | 100% | Playwright |
| 类型检查 | 0 errors | mypy --strict |
| 代码风格 | 0 warnings | ruff |
| 安全扫描 | 0 high | bandit, safety |

---

## 附录 A: 术语表

| 术语 | 说明 |
|------|------|
| Case | 贡献案例，Pipeline 的执行单元 |
| Pipeline | 5 阶段 Agent 流水线 |
| Stage | Pipeline 中的单个阶段（Explore/Plan/Develop/Review/Test） |
| Human Gate | 人工审核门禁，Pipeline 暂停等待人工决策 |
| Iteration | Develop ↔ Review 的一轮迭代 |
| Escalation | 迭代次数超限后升级为人工处理 |
| Artifact | Agent 产物（补丁、日志、报告等） |
| Evidence | 支撑贡献机会的证据项 |
| Verdict | 审核 Agent 的审核结论 |
| Checkpoint | LangGraph 状态快照，用于中断恢复 |
| SSE | Server-Sent Events，服务端推送 |
| Composable | Vue 3 组合式函数 |
| Adapter | 适配器模式，隔离 SDK 差异 |

---

## 附录 B: 参考文档

| 文档 | 路径 | 说明 |
|------|------|------|
| design.md | `tasks/design.md` | 架构设计权威来源 |
| mvp-tasks.md | `tasks/mvp-tasks.md` | 详细任务清单 |
| migration-map.md | `tasks/migration-map.md` | 组件迁移映射 |
| chat-architecture.md | `tasks/chat-architecture.md` | Chat 后端架构 |
| sse-protocol.md | `tasks/sse-protocol.md` | SSE 协议规范 |
| api-contracts.md | `tasks/api-contracts.md` | API 契约 |
| error-codes.md | `tasks/error-codes.md` | 错误码定义 |
| conventions.md | `tasks/conventions.md` | 开发规范 |
| openapi.yaml | `docs/openapi.yaml` | OpenAPI 定义 |

---

## 附录 C: ScienceClaw → rv-claw 文件映射

### 前端文件映射

| ScienceClaw 路径 | rv-claw 路径 | 操作 |
|-----------------|-------------|------|
| `src/pages/MainLayout.vue` | `ScienceClaw/frontend/src/pages/MainLayout.vue` | 保留，扩展导航 |
| `src/pages/HomePage.vue` | `ScienceClaw/frontend/src/pages/HomePage.vue` | 保留 |
| `src/pages/ChatPage.vue` | `ScienceClaw/frontend/src/pages/ChatPage.vue` | 保留 |
| `src/pages/LoginPage.vue` | `ScienceClaw/frontend/src/pages/LoginPage.vue` | 保留 |
| `src/pages/Tasks*.vue` | `ScienceClaw/frontend/src/pages/Tasks*.vue` | 保留 |
| `src/pages/ToolsPage.vue` | `ScienceClaw/frontend/src/pages/ToolsPage.vue` | 保留 |
| `src/pages/SkillsPage.vue` | `ScienceClaw/frontend/src/pages/SkillsPage.vue` | 保留 |
| `src/pages/Share*.vue` | `ScienceClaw/frontend/src/pages/Share*.vue` | 保留 |
| N/A | `ScienceClaw/frontend/src/views/CaseListView.vue` | 新增 |
| N/A | `ScienceClaw/frontend/src/views/CaseDetailView.vue` | 新增 |
| N/A | `ScienceClaw/frontend/src/views/StatisticsPage.vue` | 新增（替换 MetricsView） |
| `src/components/*.vue` | `ScienceClaw/frontend/src/components/*.vue` | 大部分保留 |
| N/A | `ScienceClaw/frontend/src/components/pipeline/*.vue` | 新增 |
| N/A | `ScienceClaw/frontend/src/components/review/*.vue` | 新增 |
| N/A | `ScienceClaw/frontend/src/components/exploration/*.vue` | 新增 |
| N/A | `ScienceClaw/frontend/src/components/planning/*.vue` | 新增 |
| N/A | `ScienceClaw/frontend/src/components/testing/*.vue` | 新增 |
| N/A | `ScienceClaw/frontend/src/components/shared/*.vue` | 新增 |
| `src/api/*.ts` | `ScienceClaw/frontend/src/api/*.ts` | 保留，新增 cases/reviews/artifacts |
| `src/composables/*.ts` (含状态) | `ScienceClaw/frontend/src/composables/*.ts` | 保留，新增 useCaseStore/usePipelineStore/useReviewStore |
| `src/composables/*.ts` | `ScienceClaw/frontend/src/composables/*.ts` | 保留，新增 useCaseEvents/usePipeline/useReview |
| `src/types/*.ts` | `ScienceClaw/frontend/src/types/*.ts` | 保留，新增 case/pipeline/event/artifact/review |

### 后端文件映射

| ScienceClaw 路径 | rv-claw 路径 | 操作 |
|-----------------|-------------|------|
| `backend/main.py` | `ScienceClaw/backend/main.py` | 扩展：注册新路由 |
| `backend/route/*.py` | `ScienceClaw/backend/route/*.py` | 保留，新增 cases/reviews/artifacts/pipeline |
| `backend/deepagent/` | `ScienceClaw/backend/deepagent/` | 保留（Chat 引擎） |
| N/A | `ScienceClaw/backend/pipeline/` | 新增（Pipeline 引擎） |
| N/A | `ScienceClaw/backend/adapters/` | 新增 |
| N/A | `ScienceClaw/backend/contracts/` | 新增 |
| N/A | `ScienceClaw/backend/datasources/` | 新增 |
| `backend/mongodb/` | `ScienceClaw/backend/mongodb/` | 保留，扩展索引 |
| `backend/user/` | `ScienceClaw/backend/user/` | 保留，扩展 role |
| `backend/im/` | `ScienceClaw/backend/im/` | 保留 |
| `backend/builtin_skills/` | `ScienceClaw/backend/builtin_skills/` | 保留 |
| `backend/models.py` | `ScienceClaw/backend/models.py` | 保留 |

---

## 附录 D: 关键依赖版本锁定

| 包名 | 版本 | 说明 |
|------|------|------|
| fastapi | `>=0.115.0,<0.130.0` | 稳定 |
| langgraph | `>=0.3.0,<0.4.0` | 检查点 API 可能变更 |
| langchain | `>=0.3.0` | 配合 langgraph |
| claude-agent-sdk | `>=0.1.0,<1.0.0` | Beta，需隔离 |
| openai-agents-sdk | `>=0.1.0,<1.0.0` | Beta，需隔离 |
| motor | `>=3.6.0` | MongoDB async |
| psycopg_pool | `>=3.2.0` | PostgreSQL pool |
| redis | `>=5.0.0` | async redis |
| pydantic | `>=2.9.0` | 结构化输出 |
| sse-starlette | `>=2.1.0` | SSE endpoint |
| structlog | `>=24.0.0` | 结构化日志 |
| tenacity | `>=9.0.0` | 重试策略 |
| aiofiles | `>=24.0.0` | 异步文件操作 |

---

*本文档为 rv-claw 项目重构的权威计划（整合版 v3.0），所有开发工作应以此为准。*

**文档历史**:
- v1.0 (2026-04-29): 初始版本 (refactor-plan.md)
- v2.0 (2026-04-29): 优化版，补充实施细节 (refactor-plan-v2.md)
- v3.0 (2026-04-29): 整合版，融合 design.md 权威架构 + 实际代码库分析，修正文件路径，补充完整模块清单
