# RV-Claw 完整重构计划

> **版本**: v1.0  
> **日期**: 2026-04-29  
> **对标基准**: ScienceClaw (完整功能迁移) + design.md (后端架构重构)  
> **目标**: 在保留 ScienceClaw 全部前端功能的基础上，实现 RV-Insights 五阶段 Agent Pipeline

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
  - [7.3 Phase 2: Pipeline 后端骨架 (3周)](#73-phase-2-pipeline-后端骨架-3周)
  - [7.4 Phase 3: Pipeline 前端与集成 (3周)](#74-phase-3-pipeline-前端与集成-3周)
  - [7.5 Phase 4: 高级功能 (2周)](#75-phase-4-高级功能-2周)
- [8. 风险与缓解](#8-风险与缓解)
- [9. 验收标准](#9-验收标准)

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
| **代码基线** | ScienceClaw 完整代码库（backend + frontend + sandbox + task-service + websearch） |
| **设计文档** | `tasks/design.md` 完整（4582 行），但 `mvp-tasks.md`, `migration-map.md`, `chat-architecture.md`, `conventions.md` 缺失 |
| **Pipeline 实现** | **零代码**。LangGraph Pipeline 引擎、5 个 Agent 节点、Human-in-the-Loop 均未实现 |
| **前端 Pipeline UI** | **零代码**。CaseListView, CaseDetailView, PipelineView, ReviewPanel, DiffViewer 均未实现 |
| **RISC-V 专用逻辑** | **零代码**。Patchwork API、ISA 扩展验证、checkpatch.pl 集成、QEMU 测试均未实现 |
| **RBAC** | ScienceClaw 使用简单本地认证，无角色区分。设计文档要求 admin/user 双角色 |
| **部署** | docker-compose.yml 存在，但按 ScienceClaw 配置，未加入 PostgreSQL 和 Pipeline 专用服务 |

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
    build: ./backend
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
// 最终路由配置
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
      { path: 'tasks', name: 'tasks', component: TasksListPage },
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

### 3.2 ScienceClaw 功能全量迁移清单

以下 **ScienceClaw 全部功能必须保留**，按模块列出迁移策略：

#### Module 1: Chat 核心 (零变更，直接复用)
```
src/pages/HomePage.vue          → 保留
src/pages/ChatPage.vue          → 保留
src/components/ChatBox.vue      → 保留
src/components/ChatMessage.vue  → 保留
src/components/ProcessMessage.vue → 保留
src/components/StepMessage.vue  → 保留
src/components/ActivityPanel.vue → 保留
src/components/PlanPanel.vue    → 保留
src/components/ToolUse.vue      → 保留
src/components/TakeOverView.vue → 保留
src/components/SuggestedQuestions.vue → 保留
src/components/AttachmentsMessage.vue → 保留
src/components/ChatBoxFiles.vue → 保留
src/components/toolViews/*.vue  → 保留
src/composables/usePendingChat.ts → 保留
src/composables/useMessageGrouper.ts → 保留
```

#### Module 2: 会话管理 (零变更，直接复用)
```
src/components/LeftPanel.vue    → 保留
src/components/SessionItem.vue  → 保留
src/components/SessionFileList.vue → 保留
src/components/SessionFileListContent.vue → 保留
src/composables/useLeftPanel.ts → 保留
src/composables/useSessionGrouping.ts → 保留
src/composables/useSessionListUpdate.ts → 保留
src/composables/useSessionNotifications.ts → 保留
src/composables/useSessionFileList.ts → 保留
```

#### Module 3: 文件系统 (零变更，直接复用)
```
src/components/FilePanel.vue    → 保留
src/components/FilePanelContent.vue → 保留
src/components/FilePreviewModal.vue → 保留
src/components/FileViewer.vue   → 保留
src/components/HtmlViewer.vue   → 保留
src/components/ImageViewer.vue  → 保留
src/components/VNCViewer.vue    → 保留
src/components/MoleculeViewer.vue → 保留
src/components/RoundFilesPopover.vue → 保留
src/components/filePreviews/*.vue → 全部保留
src/composables/useFilePanel.ts → 保留
src/composables/useRightPanel.ts → 保留
```

#### Module 4: 沙箱与终端 (零变更，直接复用)
```
src/components/SandboxPreview.vue → 保留
src/components/SandboxTerminal.vue → 保留
src/utils/sandbox.ts            → 保留
```

#### Module 5: 工具与技能 (零变更，直接复用)
```
src/pages/ToolsPage.vue         → 保留
src/pages/ToolDetailPage.vue    → 保留
src/pages/SkillsPage.vue        → 保留
src/pages/SkillDetailPage.vue   → 保留
src/pages/ScienceToolDetail.vue → 保留
src/components/ToolPanel.vue    → 保留
src/components/ToolPanelContent.vue → 保留
src/composables/useTool.ts      → 保留
src/api/tooluniverse.ts         → 保留
```

#### Module 6: 任务调度 (零变更，直接复用)
```
src/pages/TasksListPage.vue     → 保留
src/pages/TaskConfigPage.vue    → 保留
src/pages/TasksPage.vue         → 保留
src/api/tasks.ts                → 保留
src/api/taskSettings.ts         → 保留
```

#### Module 7: 设置系统 (扩展 RBAC，其余保留)
```
src/components/settings/SettingsDialog.vue → 保留
src/components/settings/SettingsTabs.vue   → 保留
src/components/settings/AccountSettings.vue → 保留
src/components/settings/ProfileSettings.vue → 保留
src/components/settings/GeneralSettings.vue → 保留
src/components/settings/PersonalizationSettings.vue → 保留
src/components/settings/ModelSettings.vue → 保留
src/components/settings/NotificationSettings.vue → 保留
src/components/settings/TaskSettings.vue → 保留
src/components/settings/TokenStatistics.vue → 保留 (数据扩展：增加 Pipeline Token 统计)
src/components/settings/IMSystemSettings.vue → 保留
src/components/settings/LarkBindingSettings.vue → 保留
src/components/settings/WeChatClawBotSettings.vue → 保留
src/components/settings/ChangePasswordDialog.vue → 保留
src/composables/useSettingsDialog.ts → 保留
```

**新增设置项**：
- `PipelineSettings.vue` — Pipeline 默认配置（max_review_iterations, default_model 等）

#### Module 8: 用户系统 (扩展 RBAC)
```
src/pages/LoginPage.vue         → 保留
src/components/login/*.vue      → 保留
src/components/UserMenu.vue     → 保留
src/components/LanguageSelector.vue → 保留
src/composables/useAuth.ts      → 扩展：增加 role 字段
src/utils/auth.ts               → 扩展：增加 role 判断
src/api/auth.ts                 → 扩展：返回 role 信息
```

#### Module 9: 统计 (改造 endpoint)
```
src/pages/MetricsView.vue → 重命名为 StatisticsPage.vue
src/api/statistics 相关   → 保留，endpoint 从 /metrics 改为 /statistics
```

#### Module 10: 共享 (零变更)
```
src/pages/ShareLayout.vue       → 保留
src/pages/SharePage.vue         → 保留
```

#### Module 11: UI 基础组件 (零变更)
```
src/components/ui/*.vue         → 全部保留
src/components/icons/*.vue      → 全部保留
src/components/CustomDialog.vue → 保留
src/components/ContextMenu.vue  → 保留
src/components/Toast.vue        → 保留
src/components/LoadingIndicator.vue → 保留
src/components/MonacoEditor.vue → 保留
src/components/SimpleBar.vue    → 保留
src/components/MarkdownEnhancements.vue → 保留
src/composables/useDialog.ts    → 保留
src/composables/useContextMenu.ts → 保留
src/composables/useTheme.ts     → 保留
src/composables/useTime.ts      → 保留
src/composables/useI18n.ts      → 保留
src/composables/useResizeObserver.ts → 保留
```

#### Module 12: API 基础设施 (扩展)
```
src/api/client.ts               → 保留（SSE 连接、Token 刷新）
src/api/index.ts                → 扩展：导出 cases, reviews, artifacts
src/api/auth.ts                 → 扩展：role 支持
src/api/agent.ts                → 保留
src/api/file.ts                 → 保留
src/api/im.ts                   → 保留
src/api/memory.ts               → 保留
src/api/models.ts               → 保留
src/api/webhooks.ts             → 保留
```

### 3.3 新增 Pipeline 前端模块

以下组件为 RV-Insights **全新开发**，不依赖 ScienceClaw 现有代码（但共享 UI 组件库）：

```
src/views/CaseListView.vue          # 案例列表（类似任务列表风格）
src/views/CaseDetailView.vue        # 案例详情 — 核心页面
src/views/StatisticsPage.vue        # 统计页（替代 MetricsView）

src/components/pipeline/
  ├── PipelineView.vue              # 5 阶段流水线可视化
  ├── StageNode.vue                 # 单阶段节点
  ├── StageConnector.vue            # 阶段连接线（带状态动画）
  ├── HumanGate.vue                 # 人工审核门禁 UI
  ├── IterationBadge.vue            # 迭代轮次标记
  ├── CostIndicator.vue             # 成本指示器
  └── PipelineTimeline.vue          # 时间线视图

src/components/review/
  ├── ReviewPanel.vue               # 审核决策面板
  ├── ReviewFinding.vue             # 单条审核发现
  ├── ReviewFindingList.vue         # 审核发现列表
  ├── DiffViewer.vue                # 基于 Monaco 的 Diff
  └── ReviewHistory.vue             # 历史审核记录

src/components/exploration/
  ├── ContributionCard.vue          # 贡献机会卡片
  ├── EvidenceChain.vue             # 证据链展示
  ├── EvidenceItem.vue              # 单条证据
  └── FeasibilityBadge.vue          # 可行性评分徽章

src/components/planning/
  ├── ExecutionPlanTree.vue         # 执行计划树
  ├── DevStepCard.vue               # 开发步骤卡片
  ├── TestCaseList.vue              # 测试用例列表
  └── RiskBadge.vue                 # 风险等级徽章

src/components/testing/
  ├── TestResultSummary.vue         # 测试结果摘要
  ├── TestLogViewer.vue             # 测试日志查看器
  ├── QemuStatus.vue                # QEMU 环境状态
  └── CoverageBadge.vue             # 覆盖率徽章

src/components/shared/
  ├── AgentEventLog.vue             # Agent 实时事件日志
  ├── ThinkingBlock.vue             # Agent 思考过程（可折叠）
  ├── ToolCallView.vue              # 工具调用可视化
  └── ArtifactViewer.vue            # 产物查看器

src/composables/
  ├── useCaseEvents.ts              # SSE 事件流管理（参考 usePendingChat）
  ├── usePipeline.ts                # Pipeline 状态追踪
  └── useReview.ts                  # 审核操作封装

src/composables/ (新增)
  ├── useCaseStore.ts               # 案例状态管理（模块级 ref 单例模式）
  ├── usePipelineStore.ts           # Pipeline 运行状态
  └── useReviewStore.ts             # 审核状态

src/types/
  ├── case.ts                       # 案例类型定义
  ├── pipeline.ts                   # Pipeline 类型定义
  ├── event.ts                      # SSE 事件类型
  ├── artifact.ts                   # 产物类型定义
  └── review.ts                     # 审核类型定义
```

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

### 3.6 API 层整合

```typescript
// src/api/cases.ts (新增)
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

// src/api/reviews.ts (新增)
export async function getReviewVerdict(caseId: string, iteration: number): Promise<ReviewVerdict>

// src/api/artifacts.ts (新增)
export async function downloadArtifact(caseId: string, path: string): Promise<Blob>
export async function getArtifactContent(caseId: string, path: string): Promise<string>
```

---

## 4. 后端重构计划

### 4.1 FastAPI 路由重构

```python
# backend/main.py (改造)
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

### 4.2 LangGraph Pipeline 引擎

```
backend/pipeline/
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

### 4.3 Agent 适配器层

```
backend/adapters/
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

### 4.4 数据源接入层

```
backend/datasources/
├── __init__.py
├── patchwork.py          # Patchwork API 客户端
├── mailing_list.py       # lore.kernel.org / groups.io 邮件解析
├── github_client.py      # GitHub API (OpenSBI, riscv-tests)
└── isa_registry.py       # RISC-V ISA 扩展注册表验证
```

### 4.5 产物与审计系统

```
backend/contracts/        # Pydantic 数据契约
├── __init__.py
├── exploration.py        # ExplorationResult, Evidence
├── planning.py           # ExecutionPlan, DevStep, TestCase
├── development.py        # DevelopmentResult
├── review.py             # ReviewVerdict, ReviewFinding
└── testing.py            # TestResult

backend/db/
├── mongo.py              # MongoDB 连接（ScienceClaw 现有）
├── collections.py        # 集合初始化与索引
└── audit.py              # 审计日志写入
```

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

### 5.2 PostgreSQL Checkpointer

```python
# 专用于 LangGraph 状态持久化，不存业务数据
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

# 自动管理的表：
# - checkpoints (状态快照)
# - checkpoint_blobs (大型状态数据)
# - checkpoint_writes (写入记录)
```

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

### 7.1 Phase 0: 基础架构 (2 周)

**目标**：搭建双模式开发基础，确保 ScienceClaw 功能无损。

| 任务 | 详情 | 产出 |
|------|------|------|
| P0.1 | 创建缺失设计文档：`mvp-tasks.md`, `migration-map.md`, `chat-architecture.md`, `conventions.md` | 4 份文档 |
| P0.2 | 初始化 `backend/pipeline/` 目录结构 | 空目录框架 |
| P0.3 | 初始化 `backend/adapters/` 目录结构 | 空目录框架 |
| P0.4 | 初始化 `backend/datasources/` 目录结构 | 空目录框架 |
| P0.5 | 初始化 `backend/contracts/` 目录结构 + Pydantic 基类 | 数据契约骨架 |
| P0.6 | 初始化前端 `src/views/`, `src/components/pipeline/` 目录 | 空目录框架 |
| P0.7 | Docker Compose 增加 `postgres` 服务 | 更新 docker-compose.yml |
| P0.8 | 数据库索引脚本 | `backend/db/collections.py` 更新 |
| P0.9 | 认证扩展：User 模型增加 `role` 字段 | DB migration + API 改造 |
| P0.10 | 回归测试：确保 ScienceClaw 所有现有功能正常 | 测试报告 |

**验收标准**：
- [ ] docker-compose up 成功启动所有服务
- [ ] ScienceClaw Chat 模式功能 100% 正常
- [ ] 数据库新增集合和索引正确创建
- [ ] admin/user 双角色认证正常

### 7.2 Phase 1: Chat 模式完整迁移 (2 周)

**目标**：将 ScienceClaw 前端功能完整迁移到 rv-claw，零功能丢失。

| 任务 | 详情 | 产出 |
|------|------|------|
| P1.1 | 前端路由重构：新增 `/cases/*`，保留所有现有路由 | `router/index.ts` |
| P1.2 | MainLayout 扩展：LeftPanel 增加 "Cases" 导航 | `LeftPanel.vue` 改造 |
| P1.3 | 统计 API 路径迁移：`/metrics/*` → `/statistics/*` | `route/statistics.py` |
| P1.4 | 前端 StatisticsPage 替换 MetricsView | `StatisticsPage.vue` |
| P1.5 | Settings 扩展：新增 PipelineSettings Tab | `PipelineSettings.vue` |
| P1.6 | API 层整合：导出 cases, reviews, artifacts API | `api/index.ts` |
| P1.7 | 类型定义：创建 case.ts, pipeline.ts, event.ts, artifact.ts, review.ts | `types/*.ts` |
| P1.8 | 状态管理：创建 caseStore.ts, pipelineStore.ts | `stores/*.ts` |
| P1.9 | 端到端回归测试：所有 ScienceClaw 页面可正常访问 | E2E 测试通过 |
| P1.10 | 国际化：新增 Pipeline 相关翻译键 | `locales/zh.ts`, `locales/en.ts` |

**验收标准**：
- [ ] 所有 ScienceClaw 页面可正常访问且功能完整
- [ ] 新增 `/cases` 路由可访问（空页面即可）
- [ ] 设置系统新增 PipelineSettings
- [ ] 左侧导航栏新增 Cases 入口

### 7.3 Phase 2: Pipeline 后端骨架 (3 周)

**目标**：实现 Pipeline 后端核心，包括 LangGraph 引擎、Agent 节点、SSE 事件流。

| 任务 | 详情 | 产出 |
|------|------|------|
| P2.1 | PipelineState Pydantic 模型 | `pipeline/state.py` |
| P2.2 | StateGraph 构建与编译 | `pipeline/graph.py` |
| P2.3 | AgentAdapter 抽象基类 + 统一事件模型 | `adapters/base.py` |
| P2.4 | ClaudeAgentAdapter 实现 | `adapters/claude_adapter.py` |
| P2.5 | OpenAIAgentAdapter 实现 | `adapters/openai_adapter.py` |
| P2.6 | EventPublisher (Redis Pub/Sub + Stream) | `pipeline/event_publisher.py` |
| P2.7 | ArtifactManager (文件系统产物管理) | `pipeline/artifact_manager.py` |
| P2.8 | CostCircuitBreaker (成本熔断器) | `pipeline/cost_guard.py` |
| P2.9 | explore_node 实现 (Claude SDK) | `pipeline/nodes/explore.py` |
| P2.10 | plan_node 实现 (OpenAI SDK) | `pipeline/nodes/plan.py` |
| P2.11 | develop_node 实现 (Claude SDK) | `pipeline/nodes/develop.py` |
| P2.12 | review_node 实现 (OpenAI/Codex + 确定性工具) | `pipeline/nodes/review.py` |
| P2.13 | test_node 实现 (Claude SDK + QEMU) | `pipeline/nodes/test.py` |
| P2.14 | human_gate_node 实现 (interrupt) | `pipeline/nodes/human_gate.py` |
| P2.15 | route_review_decision (迭代收敛检测) | `pipeline/routes.py` |
| P2.16 | route_human_decision | `pipeline/routes.py` |
| P2.17 | cases 路由：CRUD + start + events SSE | `route/cases.py` |
| P2.18 | reviews 路由：submit + history | `route/reviews.py` |
| P2.19 | artifacts 路由：download + content | `route/artifacts.py` |
| P2.20 | pipeline 路由：status + stop | `route/pipeline.py` |
| P2.21 | 数据源：PatchworkClient | `datasources/patchwork.py` |
| P2.22 | 数据源：MailingListCrawler | `datasources/mailing_list.py` |
| P2.23 | 数据源：ISA 扩展注册表验证 | `datasources/isa_registry.py` |
| P2.24 | 单元测试：路由决策函数 | `tests/unit/test_routes.py` |
| P2.25 | 单元测试：数据契约验证 | `tests/unit/test_contracts.py` |
| P2.26 | 集成测试：Pipeline 完整流程 | `tests/integration/test_pipeline.py` |

**验收标准**：
- [ ] 可通过 API 创建案例并启动 Pipeline
- [ ] SSE 事件流正常推送阶段变更
- [ ] 人工审核门可暂停并恢复 Pipeline
- [ ] 产物文件正确写入文件系统
- [ ] 3 轮 Develop↔Review 迭代正常
- [ ] 成本熔断器在超限时报错

### 7.4 Phase 3: Pipeline 前端与集成 (3 周)

**目标**：实现 Pipeline 前端全部组件，与后端联调。

| 任务 | 详情 | 产出 |
|------|------|------|
| P3.1 | CaseListView 页面（案例列表 + 筛选/搜索） | `views/CaseListView.vue` |
| P3.2 | CaseDetailView 页面（三栏布局骨架） | `views/CaseDetailView.vue` |
| P3.3 | PipelineView 组件（5 阶段可视化） | `components/pipeline/PipelineView.vue` |
| P3.4 | StageNode 组件 | `components/pipeline/StageNode.vue` |
| P3.5 | HumanGate 组件 | `components/pipeline/HumanGate.vue` |
| P3.6 | ReviewPanel 组件（审核决策面板） | `components/review/ReviewPanel.vue` |
| P3.7 | ReviewFinding 组件 | `components/review/ReviewFinding.vue` |
| P3.8 | DiffViewer 组件（Monaco Diff） | `components/review/DiffViewer.vue` |
| P3.9 | ContributionCard 组件 | `components/exploration/ContributionCard.vue` |
| P3.10 | EvidenceChain 组件 | `components/exploration/EvidenceChain.vue` |
| P3.11 | ExecutionPlanTree 组件 | `components/planning/ExecutionPlanTree.vue` |
| P3.12 | TestResultSummary 组件 | `components/testing/TestResultSummary.vue` |
| P3.13 | TestLogViewer 组件 | `components/testing/TestLogViewer.vue` |
| P3.14 | AgentEventLog 组件 | `components/shared/AgentEventLog.vue` |
| P3.15 | useCaseEvents composable（SSE 管理） | `composables/useCaseEvents.ts` |
| P3.16 | usePipeline composable | `composables/usePipeline.ts` |
| P3.17 | useReview composable | `composables/useReview.ts` |
| P3.18 | cases.ts API 客户端 | `api/cases.ts` |
| P3.19 | reviews.ts API 客户端 | `api/reviews.ts` |
| P3.20 | artifacts.ts API 客户端 | `api/artifacts.ts` |
| P3.21 | 前端与后端联调 | 端到端流程打通 |
| P3.22 | E2E 测试：创建案例 → 启动 Pipeline → 审核通过 → 完成 | Playwright 测试 |

**验收标准**：
- [ ] 可从前端创建案例并启动 Pipeline
- [ ] Pipeline 可视化实时更新阶段状态
- [ ] 人工审核面板在 pending 状态时正确显示
- [ ] DiffViewer 正确渲染补丁和 findings 高亮
- [ ] AgentEventLog 实时显示 Agent 执行过程
- [ ] E2E 测试覆盖完整案例生命周期

### 7.5 Phase 4: 高级功能 (2 周)

**目标**：QEMU 沙箱、安全加固、性能优化、监控。

| 任务 | 详情 | 产出 |
|------|------|------|
| P4.1 | QEMU Sandbox Docker 镜像 | `sandbox-qemu/Dockerfile` |
| P4.2 | Tester Agent 集成 QEMU | `pipeline/nodes/test.py` 更新 |
| P4.3 | 确定性工具集成：checkpatch.pl | `pipeline/nodes/review.py` 更新 |
| P4.4 | 确定性工具集成：sparse | `pipeline/nodes/review.py` 更新 |
| P4.5 | Prompt 注入防护 | `security/prompt_guard.py` |
| P4.6 | 速率限制中间件 | `middleware/rate_limit.py` |
| P4.7 | 安全响应头中间件 | `middleware/security.py` |
| P4.8 | 健康检查扩展 | `main.py` 更新 |
| P4.9 | 统计 API 扩展：Pipeline 数据 | `route/statistics.py` 更新 |
| P4.10 | TokenStatistics 扩展：Pipeline 成本 | `TokenStatistics.vue` 更新 |
| P4.11 | 性能测试：API 基准 | `tests/perf/test_api.py` |
| P4.12 | 性能测试：SSE 并发 | `tests/perf/test_sse.py` |
| P4.13 | 文档完善：部署指南 | `docs/deployment-guide.md` |
| P4.14 | 文档完善：API 文档 | 自动生成 OpenAPI 文档 |

**验收标准**：
- [ ] QEMU 沙箱可正确编译和运行 RISC-V 测试
- [ ] checkpatch.pl 和 sparse 在 Review 阶段自动运行
- [ ] API 速率限制生效
- [ ] 安全头正确设置
- [ ] 性能测试通过（50 并发 API, 100 SSE 连接）

---

## 8. 风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| ScienceClaw 代码变更导致迁移冲突 | 高 | 高 | 尽早锁定 ScienceClaw 版本；迁移脚本自动化；建立回归测试基线 |
| Claude Agent SDK Breaking Change | 高 | 高 | 适配器层隔离；版本锁定；fallback 到直接 API 调用 |
| LangGraph 0.3 → 0.4 API 变更 | 中 | 高 | 版本锁定 `<0.4.0`；关注 changelog |
| Pipeline 前端复杂度超预期 | 中 | 中 | 分阶段交付；MVP 先实现核心 CaseDetailView；复杂可视化延后 |
| QEMU 沙箱环境搭建困难 | 中 | 高 | 提前验证交叉编译工具链；准备预构建镜像 |
| OpenAI Codex 模型不可用 | 中 | 高 | Reviewer 支持模型降级链：codex-mini → gpt-4o → claude-sonnet |
| MongoDB 与 PostgreSQL 双数据库运维复杂度 | 低 | 中 | MongoDB 存业务，PostgreSQL 仅存 checkpointer；文档明确分工 |
| SSE 长连接在 Nginx 反向代理下异常 | 中 | 中 | 严格按 design.md §7.2 配置 Nginx SSE；充分测试重连恢复 |
| RISC-V 领域知识不足导致 Agent Prompt 效果差 | 中 | 高 | Prompt 工程单独迭代；建立评估数据集；预留 Prompt 回归测试 |

---

## 9. 验收标准

### 9.1 功能验收

| 验收项 | 标准 | 验证方式 |
|--------|------|----------|
| Chat 模式完整性 | ScienceClaw 所有功能 100% 可用 | E2E 测试通过 |
| Pipeline 创建与启动 | 可创建案例并启动 5 阶段 Pipeline | API + E2E 测试 |
| 人工审核门禁 | 每阶段完成后暂停，审核后正确前进/回退 | E2E 测试 |
| Develop↔Review 迭代 | 最多 3 轮迭代，收敛检测正确 | 单元测试 + E2E |
| SSE 实时通信 | 事件按序到达，断线重连无丢失 | 性能测试 |
| 产物管理 | 补丁/日志/报告正确存储和下载 | API 测试 |
| RBAC | admin/user 权限区分正确 | 单元测试 |
| QEMU 测试 | 可在沙箱中编译运行 RISC-V 测试 | 集成测试 |

### 9.2 性能验收

| 指标 | 目标 | 测试方法 |
|------|------|----------|
| API P99 响应时间 | < 500ms | locust / pytest |
| SSE 并发连接 | 100 连接稳定 | 压力测试 |
| Pipeline 并发执行 | 5 个 Pipeline 同时运行无死锁 | 集成测试 |
| 前端首屏加载 | < 2s (Desktop) | Lighthouse |

### 9.3 质量验收

| 指标 | 目标 |
|------|------|
| 单元测试覆盖率 | ≥ 85% (backend) |
| E2E 测试通过率 | 100% |
| 类型检查 | mypy --strict 通过 |
| 代码风格 | ruff check 通过 |
| 安全扫描 | bandit 无高危漏洞 |

---

## 附录 A: ScienceClaw → rv-claw 文件映射

### 前端文件映射

| ScienceClaw 路径 | rv-claw 路径 | 操作 |
|-----------------|-------------|------|
| `src/pages/MainLayout.vue` | `src/pages/MainLayout.vue` | 保留，扩展导航 |
| `src/pages/HomePage.vue` | `src/pages/HomePage.vue` | 保留 |
| `src/pages/ChatPage.vue` | `src/pages/ChatPage.vue` | 保留 |
| `src/pages/LoginPage.vue` | `src/pages/LoginPage.vue` | 保留 |
| `src/pages/Tasks*.vue` | `src/pages/Tasks*.vue` | 保留 |
| `src/pages/ToolsPage.vue` | `src/pages/ToolsPage.vue` | 保留 |
| `src/pages/SkillsPage.vue` | `src/pages/SkillsPage.vue` | 保留 |
| `src/pages/Share*.vue` | `src/pages/Share*.vue` | 保留 |
| N/A | `src/views/CaseListView.vue` | 新增 |
| N/A | `src/views/CaseDetailView.vue` | 新增 |
| N/A | `src/views/StatisticsPage.vue` | 新增（替换 MetricsView） |
| `src/components/*.vue` | `src/components/*.vue` | 大部分保留 |
| N/A | `src/components/pipeline/*.vue` | 新增 |
| N/A | `src/components/review/*.vue` | 新增 |
| N/A | `src/components/exploration/*.vue` | 新增 |
| N/A | `src/components/planning/*.vue` | 新增 |
| N/A | `src/components/testing/*.vue` | 新增 |
| N/A | `src/components/shared/*.vue` | 新增 |
| `src/api/*.ts` | `src/api/*.ts` | 保留，新增 cases/reviews/artifacts |
| `src/composables/*.ts` (含状态) | `src/composables/*.ts` | 保留，新增 useCaseStore/usePipelineStore/useReviewStore |
| `src/composables/*.ts` | `src/composables/*.ts` | 保留，新增 useCaseEvents/usePipeline/useReview |
| `src/types/*.ts` | `src/types/*.ts` | 保留，新增 case/pipeline/event/artifact/review |

### 后端文件映射

| ScienceClaw 路径 | rv-claw 路径 | 操作 |
|-----------------|-------------|------|
| `backend/main.py` | `backend/main.py` | 扩展：注册新路由 |
| `backend/route/*.py` | `backend/route/*.py` | 保留，新增 cases/reviews/artifacts/pipeline |
| `backend/deepagent/` | `backend/deepagent/` | 保留（Chat 引擎） |
| N/A | `backend/pipeline/` | 新增（Pipeline 引擎） |
| N/A | `backend/adapters/` | 新增 |
| N/A | `backend/contracts/` | 新增 |
| N/A | `backend/datasources/` | 新增 |
| `backend/mongodb/` | `backend/mongodb/` | 保留，扩展索引 |
| `backend/user/` | `backend/user/` | 保留，扩展 role |
| `backend/im/` | `backend/im/` | 保留 |
| `backend/builtin_skills/` | `backend/builtin_skills/` | 保留 |
| `backend/models.py` | `backend/models.py` | 保留 |

---

## 附录 B: 关键依赖版本锁定

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

*本文档为 rv-claw 项目重构的权威计划，所有开发工作应以此为准。*
