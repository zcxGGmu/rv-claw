# rv-claw 重构计划

> 目标：前端完整对标当前仓库内的 ScienceClaw 可见功能；后端按 `tasks/design.md` 的双模式目标重构，并补齐 5 阶段 Agent Pipeline。
>
> 日期：2026-04-29
> 产出位置：`tasks/codex/rv-claw-refactor-plan.md`

---

## 1. 规划边界与权威来源

### 1.1 本计划解决的问题

rv-claw 当前本质上还是一份未改动的 ScienceClaw 基线代码。用户要求不是“做一个新项目”，而是：

1. 前端体验、入口、可见能力必须继续等同于 ScienceClaw 当前仓库。
2. 后端不能继续沿用 ScienceClaw 的旧实现，必须按 `tasks/design.md` 重构为 Chat + Pipeline 双模式。
3. 在保留 ScienceClaw 现有聊天生态的同时，实现 rv-claw 专属的 5 阶段 RISC-V 贡献流水线。

### 1.2 事实来源优先级

本计划以以下顺序作为实现时的决策依据：

1. 用户本次明确要求。
2. `tasks/design.md` 顶部的 v4 说明和 5.x/6.x/7.x/8.x 后端章节。
3. 当前仓库里 ScienceClaw 的真实前端代码、真实 API 客户端、真实后端路由。
4. `tasks/ds/adr/*.md` 中已经确认的架构决策。
5. `tasks/ds/refactoring-plan.md` 和 `tasks/kimi/refactor-plan-v2.md` 作为辅助材料，不作为最终权威。

### 1.3 已识别的文档缺口

`design.md` 顶部提到但仓库中当前未找到以下文件：

- `tasks/chat-architecture.md`
- `tasks/mvp-tasks.md`
- `tasks/migration-map.md`
- `tasks/api-contracts.md`

因此本计划中关于 Chat 后端、前端迁移路径、API 兼容层的部分，属于基于现有代码与 ADR 的补完性设计。实现时应以本计划为临时权威，避免继续引用缺失文档。

### 1.4 本计划的关键结论

- 不采用一次性“大爆炸替换”。
- 前端先保留 ScienceClaw 现有结构与交互，再增量接入 Cases / Pipeline 页面。
- 后端采用“新内核 + 兼容壳”策略：内部重写，外部 API 尽量保持 ScienceClaw 前端可无感切换。
- Chat 模式复用 ScienceClaw 已验证的 DeepAgents 能力；Pipeline 模式独立使用 LangGraph。

---

## 2. 当前基线盘点

### 2.1 当前仓库的真实服务构成

当前 `docker-compose.yml` 已经编排了以下核心服务：

- `frontend`：Vue 3 前端开发服务
- `backend`：ScienceClaw 旧 FastAPI 后端
- `sandbox`：AIO Sandbox
- `websearch` + `searxng`：网页搜索与抓取
- `mongo`：MongoDB
- `redis`：Redis
- `scheduler_api` + `celery_worker` + `celery_beat`：定时任务服务

结论：

- 任务调度、文件沙箱、工具生态、IM 集成都已经是“前端已暴露能力”的一部分，不能在重构时丢掉。
- PostgreSQL 当前不存在，必须新增，用于 LangGraph checkpointer。

### 2.2 ScienceClaw 当前前端已暴露的功能面

以下能力来自真实前端代码，不是只看 README 推断：

#### A. 认证与账户

- 登录：`/login`
- 注册
- 修改密码
- 修改姓名
- 默认管理员密码检查
- 认证状态检查
- 基于 Bearer token 的 API 调用

#### B. Chat 主工作台

- 首页欢迎页与建议问题
- 会话创建、列表、搜索、分组、置顶、重命名、删除
- 会话聊天 SSE 流
- 中断运行中的会话
- 消息流中的 `thinking / plan / step / tool / message / done / error / attachments`
- 右侧 `ActivityPanel` / `ToolPanel`
- 模型选择
- 文件上传
- 会话文件面板、文件预览、下载
- 分享 / 取消分享 / 公开分享页
- Shell / 文件查看 / VNC 相关能力入口
- 运行后保存生成的 Skill / Tool

#### C. 技能与工具生态

- Skills 列表 / 详情 / 文件浏览 / 读取 / 下载 / 屏蔽 / 删除
- Tools 列表 / 详情 / 读取 / 屏蔽 / 删除
- 从会话中保存 Tool 或 Skill
- ToolUniverse 工具浏览与执行

#### D. 设置系统

- Account / Profile
- Personalization（包括 memory）
- General Settings
- Models
- Tasks
- Statistics
- Notifications
- IM
- Lark 绑定
- WeChat bridge 管理

#### E. 统计与配置

- `/statistics/summary`
- `/statistics/models`
- `/statistics/trends`
- `/statistics/sessions`
- `/task-settings`
- `/memory`
- `/models`

#### F. 定时任务

- 前端独立调用 `task-service`
- 任务 CRUD
- 自然语言转 crontab
- Webhook 校验
- 任务运行历史分页
- 任务运行结果回链到聊天会话

#### G. 分享与只读访问

- `/share/:sessionId`
- 共享会话消息读取
- 共享会话文件读取

### 2.3 ScienceClaw 当前前端依赖的后端 API 面

按前端 API 客户端真实依赖，必须兼容或平滑迁移的接口分组如下：

- `auth`：`/auth/*`
- `sessions`：`/sessions/*`
- `files`：`/files/*`
- `models`：`/models/*`
- `memory`：`/memory`
- `statistics`：`/statistics/*`
- `task-settings`：`/task-settings`
- `im`：`/im/*`
- `science`：`/science/optimize_prompt`
- `chat`：`/chat`、`/task/parse-schedule`
- `tooluniverse`：`/tooluniverse/*`

### 2.4 `design.md` 对当前基线提出的新增要求

必须新增而当前 ScienceClaw 不具备的能力：

- `cases` 域模型与案例生命周期
- 5 阶段 Pipeline：Explore -> Plan -> Develop <-> Review -> Test
- 4 个 Human Gate
- LangGraph 状态机
- PostgreSQL 检查点恢复
- Redis Pub/Sub + Stream 的 Pipeline 事件总线
- QEMU 测试环境与测试产物管理
- 审核与测试产物的持久化、审计、回退

### 2.5 当前矛盾与实现风险

1. `design.md` 的前端章节大量还是 v1 Pipeline-only 内容，不能直接照搬。
2. 当前前端真实路由以 `/chat/*` 为中心，而不是 `design.md` 旧版里的 `/tools`、`/skills`、`/metrics` 形式。
3. 当前后端认证虽然前端叫 `access_token` / `refresh_token`，内部实际上是会话 token，并非 JWT。
4. 当前任务服务固定调用 `/api/v1/chat`，如果直接删除会导致定时任务全部失效。
5. 当前统计、IM、Skill/Tool 管理都嵌在 Chat 产品内，若只实现 Pipeline 会造成明显功能倒退。

---

## 3. 重构总策略

### 3.1 总体原则

本次重构遵循四条硬约束：

1. 前端先保功能，再谈重命名和目录美化。
2. 后端先做兼容层，再逐步替换内部实现。
3. Chat 与 Pipeline 共用一个 FastAPI 应用，但保持执行引擎隔离。
4. 任何阶段都必须能通过回归验证证明“没有把 ScienceClaw 现有能力做丢”。

### 3.2 推荐的切换方式：Strangler Fig

不建议直接在 `ScienceClaw/backend` 内原地大改。推荐路径：

1. 新建顶层 `backend/` 作为 rv-claw 新后端。
2. 保留 `ScienceClaw/backend` 作为参考实现，直到新后端完全接管。
3. 通过新的 `docker-compose.yml` 将流量切到新后端。
4. 前端先继续指向兼容 API；Cases 页面单独增量接入新接口。

这样做的好处：

- 不会把旧 DeepAgents 代码与新 Pipeline 代码搅在一起。
- 可随时对照老实现补齐遗漏接口。
- 能更清晰地区分“Chat 兼容域”和“Pipeline 新域”。

### 3.3 推荐目录策略

#### 第一阶段目录策略

- 保留 `ScienceClaw/frontend`
- 保留 `ScienceClaw/task-service`
- 保留 `ScienceClaw/sandbox`
- 保留 `ScienceClaw/websearch`
- 新建顶层 `backend`

#### 第二阶段目录策略

在功能完全稳定后，可再做统一整理，例如：

- `frontend/` 替代 `ScienceClaw/frontend`
- `services/task-service/`
- `services/sandbox/`
- `services/websearch/`

但这不是首要目标，不能优先于功能重构。

### 3.4 双模式后端的边界

#### Chat 模式

- 目标：对前端表现保持 ScienceClaw 行为一致
- 引擎：复用 DeepAgents
- 流式机制：进程内 `asyncio.Queue`
- 数据中心：`sessions`、`models`、`memory`、`task_settings`、IM/工具/技能相关集合

#### Pipeline 模式

- 目标：实现 `design.md` 中定义的案例驱动 5 阶段流水线
- 引擎：LangGraph StateGraph
- 流式机制：Redis Pub/Sub + Stream -> SSE
- 数据中心：`contribution_cases`、`human_reviews`、`stage_outputs`、`audit_log`

### 3.5 兼容性底线

下列行为不允许因为后端重构而消失：

- 现有聊天页可以继续对话
- 现有会话列表与分享页继续可用
- 现有任务调度继续能拉起一次 Chat 会话
- 现有 Settings 各 tab 不报错
- Skills / Tools / ToolUniverse 页面继续可打开
- 文件上传、下载、预览继续可用
- 统计页面或统计 tab 继续有数据

### 3.6 允许发生的有限行为变化

以下变化可以接受，但必须在执行与发布计划中显式说明：

1. **切换窗口后重新登录一次**：旧 ScienceClaw token 本质是 session id，新后端目标是 JWT。为了避免脆弱的双 token 兼容逻辑，允许切换后统一要求重新登录。
2. **新增 Cases 信息架构**：用户会多看到一个 Cases 入口与对应页面，但不应因此改变现有 Chat 主工作台的组织方式。
3. **统计增加 mode 维度**：现有统计能力继续保留，但可以新增 `chat / pipeline / all` 的聚合视图。
4. **任务调度首期只要求稳定驱动 Chat**：自动创建 Case 可作为第二阶段增强，而不是首版阻塞项。

### 3.7 明确禁止的实现捷径

以下做法虽然短期省事，但会严重污染后续架构，明确禁止：

1. 把 Pipeline case 数据直接塞进 `sessions` 文档。
2. 让前端在正式环境混合调用旧 backend 与新 backend。
3. 把大型 patch / log / build artifact 直接内嵌到 MongoDB 大文档。
4. 为实现 Cases 而重写整个 Chat 前端布局。
5. 在未完成兼容层前就删除 `ScienceClaw/backend` 中可复用的 DeepAgents、IM、统计与任务相关逻辑。
6. 在未完成验证前就做目录大搬家或 UI 全量重设计。

---

## 4. 目标架构

### 4.1 顶层目标拓扑

```text
Browser (ScienceClaw 前端 + Cases 新页面)
  -> Nginx / Vite proxy
  -> FastAPI (rv-claw backend)
     -> Chat domain (DeepAgents compatibility layer)
     -> Pipeline domain (LangGraph)
     -> MongoDB
     -> PostgreSQL
     -> Redis
     -> Sandbox / Websearch / ToolUniverse / Task-service / IM
```

### 4.2 新后端建议目录

```text
backend/
├── main.py
├── config.py
├── logging.py
├── api/
│   ├── auth.py
│   ├── sessions.py
│   ├── files.py
│   ├── models.py
│   ├── memory.py
│   ├── statistics.py
│   ├── task_settings.py
│   ├── im.py
│   ├── science.py
│   ├── chat.py
│   └── cases.py
├── auth/
│   ├── models.py
│   ├── jwt.py
│   ├── dependencies.py
│   └── bootstrap.py
├── chat/
│   ├── runner.py
│   ├── service.py
│   ├── sse.py
│   ├── serializers.py
│   └── deepagents_bridge.py
├── pipeline/
│   ├── state.py
│   ├── graph.py
│   ├── routes.py
│   ├── events.py
│   ├── artifacts.py
│   ├── resources.py
│   ├── cost_guard.py
│   ├── contracts.py
│   ├── adapters/
│   └── nodes/
├── db/
│   ├── mongo.py
│   ├── postgres.py
│   ├── collections.py
│   └── migrations.py
├── integrations/
│   ├── patchwork.py
│   ├── lore.py
│   ├── github.py
│   ├── sandbox.py
│   ├── websearch.py
│   └── tooluniverse.py
└── services/
    ├── sessions.py
    ├── files.py
    ├── statistics.py
    └── reviews.py
```

### 4.3 新前端增量结构

在现有 ScienceClaw 前端基础上新增：

```text
ScienceClaw/frontend/src/
├── api/
│   ├── cases.ts
│   ├── reviews.ts
│   └── artifacts.ts
├── pages/
│   ├── CaseListView.vue
│   └── CaseDetailView.vue
├── components/
│   ├── pipeline/
│   ├── review/
│   ├── exploration/
│   └── testing/
└── composables/
    └── useCaseEvents.ts
```

### 4.4 共享约束

- Chat 与 Pipeline 共用认证体系。
- Chat 与 Pipeline 共用模型配置中心。
- Chat 与 Pipeline 共用统计口径，但统计维度要可区分 mode。
- Chat 文件与 Pipeline 产物必须物理分目录，避免互相污染。
- 资源调度必须全局感知两个模式的并发占用。

### 4.5 领域归属矩阵

| 领域 | 是否保留 ScienceClaw 行为 | 新实现位置 | 说明 |
|------|---------------------------|-----------|------|
| 认证 | 是 | `backend/auth/*` | 外部契约尽量不变，内部改为 JWT + RBAC |
| Chat 会话 | 是 | `backend/chat/*` + `backend/api/sessions.py` | 对前端维持兼容 |
| 文件与预览 | 是 | `backend/services/files.py` + `backend/api/files.py` | Chat 文件优先，Pipeline 另分域 |
| Models | 是 | `backend/api/models.py` | Chat/Pipeline 共用模型配置中心 |
| Memory | 是 | `backend/api/memory.py` | 第一阶段只服务 Chat |
| Statistics | 是，且增强 | `backend/services/statistics.py` | 统一统计 chat + pipeline |
| IM | 是 | `backend/api/im.py` | 保留 Lark/WeChat 能力 |
| Tools / Skills | 是 | `backend/api/sessions.py` + `backend/integrations/tooluniverse.py` | 先维持 Chat 能力 |
| Task Scheduler | 是 | `task-service` + `backend/api/chat.py` | 第一阶段继续驱动 Chat |
| Cases | 否，新增 | `backend/api/cases.py` | rv-claw 专属域 |
| Reviews / Human Gates | 否，新增 | `backend/services/reviews.py` | Pipeline 专属域 |
| Pipeline Engine | 否，新增 | `backend/pipeline/*` | LangGraph 内核 |

### 4.6 三条关键调用链

#### 4.6.1 Chat 发送消息链路

```text
ChatPage
  -> api/agent.ts::chatWithSession()
  -> POST /api/v1/sessions/{id}/chat (SSE)
  -> ChatRunner
  -> DeepAgents bridge
  -> asyncio.Queue
  -> SSE encoder
  -> ChatPage / ActivityPanel / ToolPanel
```

关键要求：

- SSE 事件名与字段尽量保持当前前端兼容。
- `thinking / tool / step / plan / done / error` 事件必须保留。
- 生成 skill / tool 后的保存动作仍能从 session 上下文回溯。

#### 4.6.2 启动 Pipeline 链路

```text
CaseDetailView
  -> api/cases.ts::startCase()
  -> POST /api/v1/cases/{id}/start
  -> CaseService 创建 LangGraph thread
  -> Graph.ainvoke()
  -> Node publish -> Redis Pub/Sub + Stream
  -> GET /api/v1/cases/{id}/events (SSE)
  -> useCaseEvents()
  -> PipelineView / AgentEventLog / ReviewPanel
```

关键要求：

- 启动动作必须幂等。
- case 已在运行时必须返回显式冲突状态。
- 页面刷新后能通过 detail + SSE stream 恢复 UI。

#### 4.6.3 人工审核恢复链路

```text
ReviewPanel submit
  -> POST /api/v1/cases/{id}/review
  -> ReviewService 持久化 human_review
  -> Graph.ainvoke(Command(resume=...))
  -> 下一个节点继续执行
  -> 事件总线广播 stage_change / review_submitted / stage_resumed
```

关键要求：

- `review_id` 支持幂等去重。
- 先验证 case 当前确实处于 pending gate。
- 审核动作与审计日志都必须可追溯。

### 4.7 前端路由与信息架构策略

必须以当前 ScienceClaw 真实路由为基线，而不是以 `design.md` 旧版前端章节为基线。

#### 保留路由

- `/`
- `/chat/:sessionId`
- `/chat/skills`
- `/chat/skills/:skillName`
- `/chat/tools`
- `/chat/tools/:toolName`
- `/chat/science-tools/:toolName`
- `/chat/tasks`
- `/share/:sessionId`
- `/login`

#### 新增路由

- `/cases`
- `/cases/:id`

#### 路由调整原则

1. 不把 `chat/*` 改造成新的命名空间。
2. 不把 Cases 塞进 `/chat/*` 下。
3. `MainLayout` 继续作为主布局，Cases 页面复用全局框架。
4. `LeftPanel.vue` 只做增量扩展，不重写导航体系。

### 4.8 前后端复用策略

#### 前端复用优先级

| 组件/模块 | 处理方式 | 说明 |
|-----------|----------|------|
| `MainLayout.vue` | 直接复用 | 只补导航入口 |
| `LeftPanel.vue` | 增量改造 | 新增 Cases 入口与激活态逻辑 |
| `ActivityPanel.vue` | 直接复用 | Pipeline 事件日志可映射到类似 item 结构 |
| `FilePreviewModal.vue` | 直接复用 | Pipeline artifact 预览复用 |
| `MarkdownEnhancements.vue` | 直接复用 | 计划、审核与总结说明复用 |
| `ToolPanel.vue` | 仅 Chat 使用 | Pipeline 不强行复用工具细节面板 |
| `SettingsDialog.vue` | 增量扩展 | 可加 Pipeline settings，但不是第一阶段阻塞项 |

#### 后端复用优先级

| 现有代码 | 处理方式 | 说明 |
|----------|----------|------|
| `ScienceClaw/backend/deepagent/*` | 通过 bridge 复用 | 不直接暴露给 API 层 |
| `ScienceClaw/backend/im/*` | 优先迁入或包裹复用 | IM 不是本轮重构重点，不建议重写 |
| `ScienceClaw/backend/route/statistics.py` | 提取逻辑后重构 | 必须增加 pipeline 维度 |
| `ScienceClaw/backend/models.py` | 保留模型配置能力 | 需要适配新 auth/db 结构 |
| `ScienceClaw/backend/route/chat.py` | 兼容保留 | 专供 task-service 调用 |
| `ScienceClaw/task-service` | 服务保留，契约尽量不动 | 本轮不重写调度服务 |

---

## 5. 详细工作流拆分

## 5.1 工作流 A：基线冻结与契约提取

目的：先把当前 ScienceClaw 的“真实外部行为”固化下来，避免后续越改越偏。

关键动作：

- [ ] 导出当前前端路由清单
- [ ] 导出前端 API 客户端依赖清单
- [ ] 固化 Chat SSE 事件 schema
- [ ] 固化 Settings 各 tab 的接口依赖
- [ ] 固化 task-service 到 backend 的调用契约
- [ ] 记录当前 compose 服务图和端口图

交付物：

- 前端行为基线文档
- API 契约检查表
- 回归测试清单初版

## 5.2 工作流 B：认证与通用系统域重建

目标：按 `design.md` 改成 JWT + RBAC，同时保持前端登录体验不变。

关键动作：

- [ ] 新建 `users`、`refresh_tokens` 或等价持久化结构
- [ ] 实现 JWT access token + refresh token
- [ ] 保留当前 `login/register/status/refresh/logout/change-password/change-fullname` 返回结构
- [ ] 明确 `admin/user` 两角色权限
- [ ] 补齐前端可能调用的管理用户接口
- [ ] 在新后端实现 bootstrap admin

必须兼容：

- 前端本地 token 存储逻辑
- Bearer token 调用
- `/auth/status` 的登录态判断

## 5.3 工作流 C：Chat 模式兼容层

目标：新后端接管 ScienceClaw 现有 Chat 能力，不让前端改成另一套协议。

关键动作：

- [ ] 建立 `ChatRunner`
- [ ] 封装 DeepAgents 到 `chat/deepagents_bridge.py`
- [ ] 重建 `sessions` 的 CRUD、SSE、share、stop、notifications
- [ ] 保留现有事件类型：`tool/step/message/error/done/title/wait/plan/thinking/attachments`
- [ ] 实现 Session 文件、sandbox 文件、shell、VNC 相关读取接口
- [ ] 保持前端 `api/agent.ts` 不需要大改即可连通

重要原则：

- 前端只应感知“后端地址变了”，不应感知“Chat 协议变了”。
- 若新后端一开始无法完全替代所有旧接口，可先做兼容转发层，但最终要收敛到新代码。

## 5.4 工作流 D：Tools / Skills / ToolUniverse 兼容域

目标：保留 ScienceClaw 的工具生态和技能生态。

关键动作：

- [ ] 保留 `Skills/` 和 `Tools/` 目录扫描机制
- [ ] 保持会话内保存 skill / tool 的行为
- [ ] 保留 skills/tools 的 block/delete/read/files API
- [ ] 接通 ToolUniverse 浏览和运行 API
- [ ] 明确哪些工具只在 Chat 暴露，哪些可被 Pipeline 节点复用

## 5.5 工作流 E：Cases 领域与 Pipeline 数据层

目标：从无到有建立案例中心，而不是把 Pipeline 塞进现有 session 文档。

关键动作：

- [ ] 新建 `contribution_cases`
- [ ] 新建 `human_reviews`
- [ ] 新建 `stage_outputs`
- [ ] 新建 `audit_log`
- [ ] 设计 case 状态机字段、阶段引用字段、成本字段、错误字段
- [ ] 设计 artifact 目录与引用方式

建议状态字段：

- `created`
- `exploring`
- `pending_explore_review`
- `planning`
- `pending_plan_review`
- `developing`
- `reviewing`
- `pending_code_review`
- `testing`
- `pending_test_review`
- `completed`
- `abandoned`
- `failed`
- `escalated`

## 5.6 工作流 F：LangGraph Pipeline 引擎

目标：严格按 `design.md` 与 ADR-001/002/003 实现 Pipeline 内核。

关键动作：

- [ ] `PipelineState`
- [ ] `StateGraph`
- [ ] `AsyncPostgresSaver`
- [ ] `interrupt()` 人工审核门
- [ ] `Command(resume=...)` 恢复
- [ ] `AgentAdapter` 抽象层
- [ ] `ClaudeAgentAdapter`
- [ ] `OpenAIAgentAdapter`
- [ ] `CostCircuitBreaker`
- [ ] `ResourceScheduler`

图结构必须覆盖：

- Explore -> HumanGate
- Plan -> HumanGate
- Develop -> Review
- Review -> Develop / HumanGate / Escalate
- Test -> HumanGate

## 5.7 工作流 G：Agent 节点实现

目标：把 `design.md` 的阶段语义真正落成代码，而不是只做空壳。

关键动作：

- [ ] `explore_node`
- [ ] `plan_node`
- [ ] `develop_node`
- [ ] `review_node`
- [ ] `test_node`
- [ ] `human_gate_*`
- [ ] `escalate_node`

每个节点都必须定义：

- 输入契约
- 输出契约
- 允许的工具范围
- 超时与重试策略
- 产物写入位置
- 向 SSE 总线发送的事件

## 5.8 工作流 H：Cases API 与前端新页面

目标：前端新增 Cases，而不破坏现有 Chat 信息架构。

关键动作：

- [ ] 新增 `GET/POST /api/v1/cases`
- [ ] 新增 `GET/DELETE /api/v1/cases/{id}`
- [ ] 新增 `POST /api/v1/cases/{id}/start`
- [ ] 新增 `GET /api/v1/cases/{id}/events`
- [ ] 新增 `POST /api/v1/cases/{id}/review`
- [ ] 新增 `GET /api/v1/cases/{id}/artifacts/{stage}`
- [ ] 新增 `GET /api/v1/cases/{id}/history`
- [ ] 前端新增 `CaseListView.vue`
- [ ] 前端新增 `CaseDetailView.vue`
- [ ] 复用 `ActivityPanel`、`FilePreviewModal`、`MarkdownEnhancements`

前端策略：

- 不重写现有 Chat 页。
- 在左侧导航中新增 Cases 入口。
- CaseDetail 页面独立展示 Pipeline，可复用 ScienceClaw 的右侧活动流组件。

## 5.9 工作流 I：任务调度、IM、统计的双模式统一

目标：把现有外围系统接到新后端，不形成两套统计或两套通知体系。

关键动作：

- [ ] 保留 `/api/v1/chat` 给 task-service 调用
- [ ] 保留 `/api/v1/task/parse-schedule`
- [ ] 为统计系统增加 `mode=chat|pipeline`
- [ ] IM 设置和 Lark/WeChat 控制继续工作
- [ ] 视需要新增 Pipeline 审核通知
- [ ] 任务运行结果仍可落到 Chat session 或扩展支持创建 Case

阶段性决策：

- 第一版任务调度仍只要求稳定驱动 Chat 模式。
- Pipeline 自动化定时触发可作为第二阶段能力扩展。

## 5.10 工作流 J：部署、迁移、观测与回滚

目标：重构不是只跑得起来，还要可切换、可观测、可回退。

关键动作：

- [ ] 新 compose 增加 PostgreSQL
- [ ] 明确 artifact volume
- [ ] Mongo / PG / Redis 健康检查
- [ ] 结构化日志
- [ ] Pipeline 事件审计
- [ ] 数据迁移脚本
- [ ] 回滚方案：前端继续可回指旧 backend

## 5.11 前端页面与组件补强清单

### 页面级改造范围

| 页面 | 改造等级 | 具体动作 |
|------|----------|----------|
| `HomePage.vue` | 低 | 保持不动，只验证继续能创建 chat session |
| `ChatPage.vue` | 中 | 验证新后端 SSE 完整兼容；必要时只修补字段映射 |
| `MainLayout.vue` | 低 | 保留结构，确保 Cases route 可进入主内容区 |
| `LeftPanel.vue` | 中 | 增加 Cases 入口、活跃态逻辑、路由跳转 |
| `TasksPage.vue` / `TasksListPage.vue` | 低 | 保持 task-service 调用模型不变 |
| `SettingsDialog.vue` | 低到中 | 如增加 pipeline settings，必须不影响原 tab |
| `SharePage.vue` | 低 | 验证 shared session 接口兼容即可 |
| `ToolsPage.vue` / `SkillsPage.vue` | 低 | 保持 API 兼容 |
| `CaseListView.vue` | 新增 | 案例列表、筛选、分页、搜索、状态标签 |
| `CaseDetailView.vue` | 新增 | 核心页面，承载 Pipeline、审核、产物、日志 |

### CaseListView 详细建议

至少包含以下区域：

1. 顶部操作栏：`Create Case`、搜索框、repo 筛选、status 筛选。
2. 列表主体：card 或 table，必须显示 `title / target_repo / status / updated_at / current_stage / owner / iteration`。
3. 空状态：明确引导用户创建第一个 case。
4. 分页策略：初期可服务端分页，支持 `page / page_size / keyword / status / repo`。

### CaseDetailView 详细建议

推荐三栏布局：

1. 左栏：Case 概览、基础元数据、阶段时间线、当前状态。
2. 中栏：当前阶段主内容区。
   - Explore：证据链、目标文件、可行性评分
   - Plan：执行计划树、测试计划
   - Develop/Review：diff、findings、迭代信息
   - Test：测试结果摘要、日志入口
3. 右栏：实时事件流与人工审核操作。

核心交互：

- Start / Stop / Retry / Abandon
- 审核通过 / 驳回 / 驳回到指定阶段 / 放弃
- 产物切换与 diff 查看
- SSE 自动刷新当前阶段

## 5.12 后端模块交付矩阵

| 模块 | 必要文件 | 关键职责 | 主要依赖 |
|------|----------|----------|----------|
| 应用入口 | `main.py`, `config.py` | 应用工厂、生命周期、依赖注入 | Mongo, PG, Redis |
| 认证域 | `auth/*`, `api/auth.py` | JWT、RBAC、当前用户解析 | Mongo |
| Chat 域 | `chat/*`, `api/sessions.py`, `api/chat.py` | 会话、SSE、DeepAgents bridge | DeepAgents, Files |
| Pipeline 域 | `pipeline/*`, `api/cases.py` | 状态机、事件、人工门、节点调度 | LangGraph, Redis, PG |
| 通用服务 | `services/*` | files、statistics、reviews、session ops | Mongo, FS |
| 集成层 | `integrations/*` | sandbox/websearch/patchwork/github/tooluniverse | 外部服务 |
| 数据层 | `db/*` | 初始化、索引、迁移、连接池 | Mongo, PG |

交付要求：

- API 层只做参数校验和 response 组装，不写长业务逻辑。
- 所有跨域协作都经过 service 层或 domain 层，不允许 API 直接拼业务状态机。
- `pipeline/nodes/*` 只关心本阶段输入输出，不直接操作 HTTP 对象。

## 5.13 关键契约详细定义

### Chat SSE 事件契约

必须继续兼容以下事件名：

- `tool`
- `step`
- `message`
- `error`
- `done`
- `title`
- `wait`
- `plan`
- `attachments`
- `thinking`

必须继续兼容的共性字段：

- `event_id`
- `timestamp`

额外要求：

- `done` 事件中继续支持 `statistics` 与 `round_files`
- `tool` 事件继续支持 `tool_meta`
- `message` 事件继续支持 `attachments`

### Pipeline SSE 事件契约

新增事件建议统一为：

- `stage_change`
- `agent_output`
- `review_request`
- `review_submitted`
- `iteration_update`
- `artifact_created`
- `cost_update`
- `heartbeat`
- `pipeline_completed`
- `pipeline_failed`

建议统一 envelope：

```json
{
  "seq": 12,
  "case_id": "case_xxx",
  "event_type": "stage_change",
  "timestamp": "2026-04-29T13:00:00Z",
  "data": {}
}
```

### 审核动作契约

`POST /api/v1/cases/{id}/review` 建议请求体：

```json
{
  "review_id": "uuid-or-snowflake",
  "action": "approve | reject | reject_to | abandon | modify",
  "comment": "text",
  "reject_to_stage": "explore | plan | develop",
  "modified_artifact_ref": "optional"
}
```

约束：

- `reject_to` 必须指定 `reject_to_stage`
- `modify` 必须指定人工修改后的 artifact 引用
- `approve/reject/abandon` 不允许带多余字段污染状态

## 5.14 迁移与切换策略

### 切换步骤建议

1. 新 backend 先并行启动，使用独立端口。
2. 先跑自动化回归，对比旧 backend 与新 backend 的关键接口行为。
3. 前端在预发布环境指向新 backend，进行人工验收。
4. 切换生产流量前，提前公告“需要重新登录一次”。
5. 切换 Nginx / compose 上游到新 backend。
6. 保留旧 backend 作为短期回滚目标。

### 数据迁移策略

#### 无需迁移的数据

- 现有 `sessions`、`models`、`task_settings`、`memory`、IM 相关集合，可由新 backend 直接读取或渐进改写。

#### 需要新增但非迁移的数据

- `contribution_cases`
- `human_reviews`
- `stage_outputs`
- `audit_log`
- PostgreSQL checkpoints

#### 切换时需要处理的数据

- 旧 `user_sessions` / 旧 access token：统一失效或通过过渡层兼容 1 个版本周期。

### 回滚策略

1. 前端资源不回滚，只回切 backend 上游。
2. 若问题只在 Pipeline，可先隐藏 Cases 入口，保留 Chat 正常。
3. 若问题在认证层，可临时降级为旧 backend 恢复登录链路。
4. Mongo 新增集合不影响旧 backend 回退读取旧数据。

## 5.15 非功能性约束

### 性能预算

- Chat 首 token 响应：理想 < 2s，允许 < 5s
- Case 列表响应：P95 < 500ms
- Case 详情首次加载：P95 < 1s（不含 SSE 流）
- SSE 重连恢复：10s 内恢复并补齐断线事件

### 容错预算

- 单个 case 节点失败不应拖垮整个服务
- Redis 短时不可用时，Chat 仍应可用
- PostgreSQL 故障时，Pipeline 应拒绝启动而不是半运行

### 观测要求

- 每个 case 有唯一 `case_id`
- 每个 session 有唯一 `session_id`
- 每个 review 提交有唯一 `review_id`
- Chat 与 Pipeline 都要带 `mode` 标签写日志和统计

---

## 6. API 与数据兼容计划

### 6.1 必须保留的兼容 API

以下接口必须继续存在，哪怕内部实现全部换掉：

#### Auth

- `GET /api/v1/auth/check-default-password`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/register`
- `GET /api/v1/auth/status`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/change-password`
- `POST /api/v1/auth/change-fullname`
- `POST /api/v1/auth/logout`

#### Sessions / Chat

- `PUT /api/v1/sessions`
- `GET /api/v1/sessions`
- `GET /api/v1/sessions/{id}`
- `DELETE /api/v1/sessions/{id}`
- `PATCH /api/v1/sessions/{id}/pin`
- `PATCH /api/v1/sessions/{id}/title`
- `POST /api/v1/sessions/{id}/chat`
- `POST /api/v1/sessions/{id}/stop`
- `POST /api/v1/sessions/{id}/share`
- `DELETE /api/v1/sessions/{id}/share`
- `GET /api/v1/sessions/shared/{id}`
- `POST /api/v1/sessions/{id}/clear_unread_message_count`
- `GET /api/v1/sessions/{id}/files`
- `GET /api/v1/sessions/{id}/sandbox-file`
- `GET /api/v1/sessions/{id}/sandbox-file/download`

#### Skills / Tools / Science

- `/api/v1/sessions/skills*`
- `/api/v1/sessions/tools*`
- `/api/v1/tooluniverse/*`
- `POST /api/v1/science/optimize_prompt`

#### Files / Models / Memory / Statistics / IM

- `/api/v1/files/*`
- `/api/v1/models/*`
- `/api/v1/memory`
- `/api/v1/statistics/*`
- `/api/v1/task-settings`
- `/api/v1/im/*`

#### Scheduler compatibility

- `POST /api/v1/chat`
- `POST /api/v1/task/parse-schedule`

### 6.2 新增 Pipeline API

推荐以 `cases` 为核心，不再单独暴露旧式 `/reviews` 资源根路径：

- `POST /api/v1/cases`
- `GET /api/v1/cases`
- `GET /api/v1/cases/{id}`
- `DELETE /api/v1/cases/{id}`
- `POST /api/v1/cases/{id}/start`
- `POST /api/v1/cases/{id}/stop`
- `GET /api/v1/cases/{id}/events`
- `POST /api/v1/cases/{id}/review`
- `GET /api/v1/cases/{id}/artifacts/{stage}`
- `GET /api/v1/cases/{id}/history`

### 6.3 MongoDB 集合规划

#### 保留或重建的通用集合

- `users`
- `refresh_tokens` 或等价 token 表
- `sessions`
- `models`
- `task_settings`
- `memory`
- `blocked_skills`
- `blocked_tools`
- `im_user_bindings`
- `im_chat_sessions`
- `im_message_dedup`

#### 新增的 Pipeline 集合

- `contribution_cases`
- `human_reviews`
- `stage_outputs`
- `audit_log`
- `knowledge_entries`

说明：

- `knowledge_entries` 在功能上可后置，但集合规划先保留，避免后续再破 schema。

### 6.4 PostgreSQL 与 Redis 规划

#### PostgreSQL

仅用于 LangGraph checkpointer：

- `checkpoints`
- `checkpoint_blobs`
- `checkpoint_writes`

#### Redis

用途拆分：

- Chat 无需 Redis 流式总线
- Pipeline 事件：`case:{id}:events` + `case:{id}:stream`
- 调度与缓存：继续供 Celery / 限流 / 临时状态使用

### 6.5 文件与产物规划

建议物理分离：

```text
workspace/
├── chat/
│   └── {session_id}/...
└── cases/
    └── {case_id}/
        ├── explore/
        ├── plan/
        ├── develop/round_1/
        ├── review/
        └── test/
```

原则：

- Chat 会话文件仍按前端期望工作。
- Pipeline 产物不复用 session workspace，避免路径与权限模型混乱。

### 6.6 旧接口到新实现的映射表

| 旧接口分组 | 新模块 | 说明 |
|------------|--------|------|
| `/auth/*` | `backend/api/auth.py` | 外部响应结构维持，内部认证模型重写 |
| `/sessions/*` | `backend/api/sessions.py` + `backend/chat/service.py` | 会话与聊天入口兼容 |
| `/chat` | `backend/api/chat.py` | 专供 task-service 调用 |
| `/task/parse-schedule` | `backend/api/chat.py` | 兼容保留 |
| `/files/*` | `backend/api/files.py` + `backend/services/files.py` | 若前端真实只需少量接口，可先实现最常用子集 |
| `/models/*` | `backend/api/models.py` | 统一模型配置中心 |
| `/memory` | `backend/api/memory.py` | 继续以 user 维度存储 |
| `/statistics/*` | `backend/api/statistics.py` + `backend/services/statistics.py` | 增加 mode 维度 |
| `/task-settings` | `backend/api/task_settings.py` | 保持结构兼容 |
| `/im/*` | `backend/api/im.py` | 迁入或包裹现有 IM 逻辑 |
| `/tooluniverse/*` | `backend/api/tooluniverse.py` | 可先直接复用现有实现 |
| `/science/optimize_prompt` | `backend/api/science.py` | 兼容保留 |
| `/cases/*` | `backend/api/cases.py` | 新增 Pipeline 域 |

### 6.7 Chat Session 文档建议结构

```json
{
  "_id": "session_id",
  "session_id": "session_id",
  "user_id": "user_xxx",
  "title": "string|null",
  "mode": "deep|chat|research",
  "status": "pending|running|waiting|completed|failed",
  "source": "web|task|im",
  "model_config_id": "model_xxx|null",
  "is_shared": true,
  "pinned": false,
  "unread_message_count": 0,
  "latest_message": "string|null",
  "latest_message_at": 1710000000,
  "workspace_dir": "workspace/chat/session_xxx",
  "events": [],
  "statistics": {
    "input_tokens": 0,
    "output_tokens": 0,
    "total_cost_usd": 0
  },
  "created_at": 1710000000,
  "updated_at": 1710000000
}
```

建议说明：

- 为了兼容当前前端读取逻辑，第一阶段继续允许 `events` 内嵌存储。
- 若后续事件量过大，再拆出 `session_events` 集合，但这不应阻塞重构首版。

### 6.8 Case 文档建议结构

```json
{
  "_id": "case_20260429_001",
  "title": "Add Zicfiss support to Linux kernel",
  "description": "optional",
  "owner_user_id": "user_xxx",
  "target_repo": "linux",
  "target_branch": "master",
  "status": "pending_plan_review",
  "current_stage": "plan",
  "input_context": {
    "user_hint": "text",
    "target_repo": "linux",
    "contribution_type_hint": "isa_extension"
  },
  "exploration_result_ref": "stage_output_id",
  "execution_plan_ref": "stage_output_id",
  "development_result_ref": "stage_output_id",
  "review_verdict_ref": "stage_output_id",
  "test_result_ref": "stage_output_id",
  "review_iterations": 1,
  "max_review_iterations": 3,
  "last_error": null,
  "cost": {
    "input_tokens": 0,
    "output_tokens": 0,
    "estimated_cost_usd": 0
  },
  "created_at": "2026-04-29T00:00:00Z",
  "updated_at": "2026-04-29T00:00:00Z",
  "started_at": null,
  "completed_at": null,
  "abandoned_at": null
}
```

### 6.9 Stage Output / Human Review / Audit Log 建议结构

#### `stage_outputs`

```json
{
  "_id": "stage_output_id",
  "case_id": "case_xxx",
  "stage": "explore|plan|develop|review|test",
  "round_num": 1,
  "summary": "string",
  "payload": {},
  "artifact_paths": [],
  "created_by": "explore_node",
  "created_at": "2026-04-29T00:00:00Z"
}
```

#### `human_reviews`

```json
{
  "_id": "review_id",
  "case_id": "case_xxx",
  "stage": "plan",
  "action": "approve",
  "comment": "looks good",
  "reject_to_stage": null,
  "modified_artifact_ref": null,
  "reviewer_user_id": "user_xxx",
  "reviewer_name": "admin",
  "created_at": "2026-04-29T00:00:00Z"
}
```

#### `audit_log`

```json
{
  "_id": "audit_id",
  "entity_type": "session|case|review|auth",
  "entity_id": "case_xxx",
  "event_type": "case_started",
  "actor_user_id": "user_xxx",
  "data": {},
  "created_at": "2026-04-29T00:00:00Z"
}
```

### 6.10 统计口径设计

统计服务必须统一处理两类来源：

| 来源 | 主键 | 统计对象 | 典型指标 |
|------|------|----------|----------|
| Chat | `session_id` | 单会话 | input/output token、模型、耗时、工具调用数 |
| Pipeline | `case_id` | 单案例 | 各阶段 token、阶段耗时、review 轮次、测试通过率 |

建议新增维度：

- `mode`: `chat | pipeline`
- `owner_user_id`
- `model_provider`
- `source`: `web | task | im | pipeline`

建议新增聚合指标：

- `pipeline_total_cases`
- `pipeline_completed_cases`
- `pipeline_avg_iterations`
- `pipeline_avg_duration_minutes`
- `pipeline_cost_usd`

### 6.11 索引与 TTL 细化建议

#### `contribution_cases`

- `(owner_user_id, updated_at desc)`
- `(status, updated_at desc)`
- `(target_repo, updated_at desc)`

#### `stage_outputs`

- `(case_id, stage, round_num desc)`

#### `human_reviews`

- `(case_id, created_at desc)`
- `(reviewer_user_id, created_at desc)`

#### `audit_log`

- `(entity_type, entity_id, created_at desc)`
- `(event_type, created_at desc)`

TTL 建议：

- `audit_log`: 2 年
- `abandoned` case：90 天
- 非最终 artifact：30 天

### 6.12 文件服务兼容策略

当前前端对文件能力的依赖分为三类：

1. session 内上传与列举
2. file_id 下载与预览
3. sandbox path 直接读取 / 下载

因此文件服务重构时要区分：

- `files` 资源型 API
- `sessions/{id}/upload` 会话上下文 API
- `sessions/{id}/sandbox-file*` 受控路径访问 API

实现要求：

- 必须保留 allowed prefixes 白名单校验
- 必须防止路径遍历
- 必须支持前端附件消息与右侧文件面板

---

## 7. 分阶段实施计划

## Phase 0：基线冻结与脚手架

目标：先让“要保留什么”清晰，再开始动手替换。

- [ ] 建立前端功能清单与 API 契约清单
- [ ] 建立 Chat SSE 事件样例集
- [ ] 建立 compose 服务拓扑说明
- [ ] 创建新 `backend/` 目录骨架
- [ ] 创建 `tests/unit`、`tests/integration`、`tests/e2e`

退出标准：

- 有一份明确的“不可回退功能清单”
- 新 backend 骨架可被 `uvicorn` 启动到最小健康检查

## Phase 1：基础设施与应用骨架

目标：搭好新后端的运行底座。

- [ ] `config.py`
- [ ] `main.py`
- [ ] Mongo / PostgreSQL / Redis 连接层
- [ ] `/health`、`/ready`
- [ ] logging / CORS / security headers
- [ ] 新 compose 增加 PostgreSQL

退出标准：

- `docker compose up` 可拉起新旧依赖
- `/health` 能反映 Mongo / PG / Redis 状态

## Phase 2：认证与用户域

目标：先接住所有需要登录的前端路径。

- [ ] JWT 登录/刷新/登出
- [ ] 用户注册
- [ ] `admin/user` RBAC
- [ ] bootstrap admin
- [ ] `/auth/status`
- [ ] `/auth/me`
- [ ] 修改密码 / 修改姓名

退出标准：

- 前端登录页与用户菜单可正常工作
- Settings 中账户相关能力不报错

## Phase 3：Chat 模式最小可用

目标：现有 Chat 页面能在新后端跑通。

- [ ] Session CRUD
- [ ] Chat SSE
- [ ] stop / share / unshare
- [ ] unread / pin / rename
- [ ] shared session 只读页
- [ ] session files

退出标准：

- 首页 -> 新建会话 -> 对话 -> 停止 -> 分享 整链路通过

## Phase 4：Chat 全量兼容

目标：把外围生态全部补回来。

- [ ] Skills / Tools 管理
- [ ] ToolUniverse
- [ ] memory
- [ ] models
- [ ] statistics
- [ ] IM
- [ ] file preview / sandbox file / shell / vnc
- [ ] `/api/v1/chat` 与 `/task/parse-schedule`

退出标准：

- ScienceClaw 现有前端功能面无明显缺口
- task-service 可重新驱动 Chat

## Phase 5：Cases 域与数据模型

目标：开始引入 rv-claw 专属领域对象。

- [ ] `contribution_cases` schema
- [ ] `human_reviews` schema
- [ ] `stage_outputs` schema
- [ ] `audit_log` schema
- [ ] artifact manager
- [ ] `POST/GET/DELETE /cases`

退出标准：

- 能创建 case
- 能查询 case 列表与详情
- 能写入基础审计记录

## Phase 6：Pipeline 引擎骨架

目标：让 LangGraph 图可运行到空实现节点。

- [ ] `PipelineState`
- [ ] `build_pipeline_graph()`
- [ ] `AsyncPostgresSaver`
- [ ] human gate 中断/恢复
- [ ] Redis event publisher
- [ ] cases SSE endpoint

退出标准：

- 一个示例 case 可从 start 进入 graph
- graph 可在 gate 处暂停并恢复

## Phase 7：五阶段 Agent 节点实现

目标：把 Pipeline 真正做成有业务意义的流水线。

- [ ] explore 节点
- [ ] plan 节点
- [ ] develop 节点
- [ ] review 节点
- [ ] test 节点
- [ ] review 迭代与 escalate
- [ ] QEMU 测试接入

退出标准：

- 最小示例 case 可以完整走完五阶段
- review 最多 3 轮逻辑可验证

## Phase 8：Cases 前端与联调

目标：让前端真正看到 Pipeline。

- [ ] Cases 导航入口
- [ ] CaseListView
- [ ] CaseDetailView
- [ ] useCaseEvents
- [ ] Pipeline 可视化
- [ ] 人工审核面板
- [ ] artifact 查看与 diff 查看

退出标准：

- 前端可创建、启动、审核、查看产物
- Chat 页面未受影响

## Phase 9：统一统计、任务、通知与迁移

目标：完成双模式系统层打通。

- [ ] 统计区分 chat/pipeline
- [ ] task-service 对新后端稳定工作
- [ ] IM 支持 case review 通知
- [ ] 数据迁移脚本
- [ ] 兼容 API deprecation 清单

退出标准：

- 任务调度继续可用
- 统计不再只覆盖 chat

## Phase 10：验证、硬化与切换

目标：证明系统能替代当前基线，而不是只靠文档自证。

- [ ] 单元测试
- [ ] 集成测试
- [ ] E2E 测试
- [ ] 压测
- [ ] 安全扫描
- [ ] 故障恢复测试
- [ ] 回滚演练

退出标准：

- 可以明确给出“资深工程师会批准”的验收证据

### 7.1 各 Phase 的关键产出文件

| Phase | 关键产出 |
|-------|----------|
| 0 | `backend/` 骨架、测试目录、基线文档 |
| 1 | `backend/main.py`, `backend/config.py`, `backend/db/*`, 新 compose |
| 2 | `backend/auth/*`, `backend/api/auth.py` |
| 3 | `backend/chat/*`, `backend/api/sessions.py` |
| 4 | `backend/api/files.py`, `models.py`, `memory.py`, `statistics.py`, `im.py`, `science.py`, `chat.py` |
| 5 | `backend/api/cases.py`, `backend/services/reviews.py`, `backend/db/collections.py` |
| 6 | `backend/pipeline/state.py`, `graph.py`, `events.py`, `artifacts.py` |
| 7 | `backend/pipeline/nodes/*`, `backend/pipeline/adapters/*` |
| 8 | `frontend/src/pages/CaseListView.vue`, `CaseDetailView.vue`, `api/cases.ts`, `useCaseEvents.ts` |
| 9 | 统计整合、任务与 IM 扩展、迁移脚本 |
| 10 | 回归测试、压测、安全检查、回滚手册 |

### 7.2 依赖关系与并行边界

#### 可以并行的工作

- Phase 1 基础设施与前端 Cases 页面原型可以并行。
- Phase 4 的 Statistics / IM / ToolUniverse 兼容实现可部分并行。
- Phase 5 数据模型与 Phase 8 前端静态页面框架可以并行。

#### 不能并行的关键路径

- Phase 2 认证不稳定时，不要推进大规模 API 联调。
- Phase 3 Chat SSE 未稳定前，不要把前端 Chat 直接切到新 backend。
- Phase 6 Graph 骨架未稳定前，不要推进完整 Pipeline E2E。
- Phase 7 review/test 节点未完成前，不要宣称“五阶段已实现”。

### 7.3 建议的 PR 切分

为降低 review 成本，建议至少按以下粒度拆 PR：

1. `backend skeleton + infra`
2. `auth domain`
3. `chat sessions + sse`
4. `files/models/memory/task-settings/statistics`
5. `im + task-service compatibility`
6. `cases schema + api`
7. `pipeline graph + checkpoints + events`
8. `pipeline nodes`
9. `frontend cases pages`
10. `integration + tests + rollout`

### 7.4 每个 Phase 的最低验证命令

| Phase | 最低验证 |
|-------|----------|
| 1 | `curl /health`, `curl /ready` |
| 2 | 登录、刷新、退出、RBAC 403 |
| 3 | 创建 session -> SSE chat -> stop |
| 4 | Tools/Skills/Statistics/Task Settings/IM 页面冒烟 |
| 5 | 创建 case -> 查询列表 |
| 6 | start case -> pending gate -> resume |
| 7 | 完整 pipeline 走通最小样例 |
| 8 | 前端 CaseList/Detail 与 SSE 联动 |
| 9 | task-service 调 Chat + statistics mode 聚合 |
| 10 | 全量回归 + 压测 + 回滚演练 |

---

## 8. 验证计划

### 8.1 必做回归验证

- [ ] 登录 / 注册 / 刷新 token
- [ ] 创建会话 / 聊天 / 停止 / 分享
- [ ] Skills / Tools / ToolUniverse 页面
- [ ] 文件上传 / 下载 / 预览
- [ ] Settings 全部 tab
- [ ] 统计页面或统计 tab
- [ ] 任务创建 / 校验 / 执行 / 查看结果
- [ ] IM 管理接口

### 8.2 必做 Pipeline 验证

- [ ] 创建 case
- [ ] 启动 pipeline
- [ ] Explore -> Gate
- [ ] Plan -> Gate
- [ ] Develop <-> Review 迭代
- [ ] Code Gate
- [ ] Test -> Gate
- [ ] 完成 / 放弃 / 驳回 / 回退

### 8.3 必做恢复与稳定性验证

- [ ] Pipeline 在 gate 暂停后重启服务可恢复
- [ ] SSE 断线重连可补齐事件
- [ ] Redis 暂时不可用时有明确退化行为
- [ ] PostgreSQL checkpointer 工作正常
- [ ] 多个 chat 与 case 并发时资源调度不失控

### 8.4 自动化测试分层矩阵

| 层级 | 覆盖内容 | 重点 |
|------|----------|------|
| Unit | auth, models, review route, route functions, adapters | 输入输出、RBAC、状态转移 |
| Integration | Mongo/PG/Redis + FastAPI + Graph | checkpoint、SSE、review resume |
| E2E | 前端登录、chat、cases、task-service 联动 | 用户可见行为 |
| Eval | Agent 节点输出质量 | explore 证据有效性、review 发现质量 |

### 8.5 建议的冒烟场景

#### 场景 A：Chat 基线

1. 登录
2. 创建 chat session
3. 发送消息
4. 收到 thinking/tool/message/done
5. 上传文件
6. 分享会话
7. 打开 share 页面

#### 场景 B：Tasks 基线

1. 创建定时任务
2. 校验 schedule
3. 触发执行
4. 查看 run 记录
5. 从 run 记录跳转 chat session

#### 场景 C：Pipeline 核心

1. 创建 case
2. 启动 pipeline
3. Explore 完成 -> 审核通过
4. Plan 完成 -> 审核通过
5. Develop -> Review reject -> fix -> approve
6. Code gate 审核通过
7. Test 完成 -> 审核通过
8. 查看 artifacts 与 history

### 8.6 性能与恢复阈值

- 50 个并发普通 API 请求下，后端不应出现系统性 5xx
- 100 个 SSE 连接下，Redis/后端不应出现明显积压
- Pipeline 中断恢复成功率目标：> 95%
- Chat stop 成功率目标：> 95%

---

## 9. 风险与缓解

### 9.1 主要风险

1. 前端真实依赖面比 `design.md` 大，容易漏接口。
2. 认证从旧 session token 切到 JWT 时，容易破坏前端鉴权与 task-service。
3. 两套执行引擎并存，资源竞争和观测复杂度会明显上升。
4. QEMU 测试环境搭建比普通 Python 后端复杂得多。
5. 若过早重命名前端/服务目录，会制造大量无价值 churn。

### 9.2 缓解策略

1. 先做契约提取，再写新后端。
2. 所有旧接口先兼容，不先“清理 API”。
3. Chat 和 Pipeline 的流式机制分开实现，不强行统一。
4. 先跑通无 QEMU 的最小 pipeline，再补测试阶段的真实环境。
5. 目录统一放到最后一个非功能性阶段做。

### 9.3 详细风险台账

| 风险 | 触发信号 | 影响 | 兜底方案 |
|------|----------|------|----------|
| Chat SSE 字段不兼容 | 前端消息页空白或工具面板异常 | 高 | 保持旧事件 schema，必要时后端做字段适配 |
| JWT 改造破坏登录 | `/auth/status` 异常、前端循环跳登录页 | 高 | 切换窗口强制重登，先保协议后优化体验 |
| task-service 失效 | 新任务不执行、runs 为空 | 高 | 优先恢复 `/api/v1/chat` 兼容接口 |
| Redis 事件丢失 | CaseDetail 实时状态停滞 | 中 | 使用 Redis Stream 重放，必要时前端轮询详情补状态 |
| QEMU 测试环境不稳定 | test 阶段大量超时 | 中到高 | 首版允许用 mock / 编译验证降级，后续再拉齐真实环境 |
| 统计口径不统一 | Settings 统计与 case 成本对不上 | 中 | 引入统一 statistics service，所有 token 记账走同一入口 |
| IM 兼容性回退 | Lark/WeChat 绑定失效 | 中 | 先包裹复用现有模块，不做重写 |

### 9.4 需要尽早锁定的工程决策

1. 新 backend 是否与旧 backend 共用 MongoDB database name。
2. Chat 旧 token 是否直接废弃还是保留一个过渡验证器。
3. DeepAgents bridge 是直接 import 旧模块还是拷贝到新目录下维护。
4. Pipeline 的 QEMU 环境是复用现有 sandbox 还是增加专用 image/service。
5. Statistics UI 是否新增 mode 切换器还是仅在接口层支持。

---

## 10. 最终验收标准

只有同时满足以下条件，重构才算完成：

- ScienceClaw 当前前端所有已暴露能力在 rv-claw 中继续可用。
- rv-claw 新增 Cases 页面并能驱动完整 5 阶段 Pipeline。
- 后端已切换为双模式架构：Chat 兼容层 + LangGraph Pipeline。
- PostgreSQL checkpointer、Redis 事件总线、Mongo 业务数据三者职责清晰。
- task-service、IM、统计、文件、模型、memory 不再依赖旧 backend。
- 有自动化测试和运行验证证明系统可工作，不靠文档自证。

### 10.1 建议的验收演示脚本

验收时建议按以下顺序演示，而不是只展示 happy path：

1. 登录后创建普通 chat，会话流正常。
2. Tools / Skills / Statistics / Tasks / IM 设置页均可打开。
3. 创建定时任务并触发一次 chat。
4. 创建 case 并启动 pipeline。
5. 在至少一个 gate 上执行人工审核。
6. 演示一次 Develop -> Review 迭代。
7. 查看 artifact / diff / history。
8. 重启后端后恢复一个 pending case。

### 10.2 上线前 Checklist

- [ ] 全量 API 回归通过
- [ ] Chat SSE 回归通过
- [ ] Case SSE 回归通过
- [ ] 重新登录公告已准备
- [ ] Mongo / PG / Redis 备份可用
- [ ] 回滚目标服务与配置已保留
- [ ] 监控与错误日志可观察
- [ ] 至少一次预发布环境验收完成

---

## 11. 建议的第一批落地顺序

如果按最小风险推进，建议真正编码时采用以下顺序：

1. Phase 0 + Phase 1
2. Phase 2
3. Phase 3
4. Phase 4
5. Phase 5 + Phase 6
6. Phase 7
7. Phase 8
8. Phase 9 + Phase 10

原因：

- 先拿下 Chat 兼容，才能保证不会把现有产品打废。
- 再做 Cases / Pipeline，才能在稳定底座上叠加新领域能力。

### 11.1 推荐的两条实施主线

#### 主线 A：保本线

先把 ScienceClaw 已有前端功能完整接住：

1. 认证
2. Chat 会话
3. 文件
4. models / memory / task-settings
5. statistics / IM / task-service

这条线的目标是不丢功能。

#### 主线 B：增量线

在保本线稳定后，增加 rv-claw 专属能力：

1. cases schema
2. graph skeleton
3. review gates
4. pipeline nodes
5. cases UI

这条线的目标是新增价值。

### 11.2 方案优化后的核心建议

最终建议可以压缩成三句话：

1. **前端不重写，按页面与组件增量扩展。**
2. **后端不原地魔改旧 ScienceClaw backend，而是新建 backend 做兼容接管。**
3. **先稳定 Chat 再实现 Pipeline，避免“新能力还没交付，老能力先打坏”。**

---

## 12. 进一步优化后的方案

这一节不重复前文已有内容，只回答一个问题：**基于当前计划，哪些地方继续优化后，能显著降低执行风险、缩短交付路径、提升长期可维护性。**

### 12.1 最大的优化方向：先把“范围”再压实

当前计划已经覆盖完整目标，但仍偏“全功能最终态”。如果直接按完整态推进，风险是：

- Chat 兼容、Pipeline 新增、运维增强、任务调度、统计统一会同时争抢资源。
- 很容易在“想一次做到位”的过程中丢掉关键路径节奏。

建议将当前方案再压缩为 **3 个发布波次**：

#### Release A：兼容接管版

目标：只证明新 backend 能接住 ScienceClaw 现有前端。

必须包含：

- auth
- sessions/chat/sse
- files
- models
- memory
- statistics
- task-settings
- `/api/v1/chat`
- `/api/v1/task/parse-schedule`
- IM 基础管理
- task-service 继续可用

明确不要求：

- 完整 Pipeline
- QEMU 真测
- Cases UI 对全部用户开放

#### Release B：Pipeline 内测版

目标：仅对内部用户开放 Cases，打通最小五阶段链路。

必须包含：

- cases schema
- cases api
- LangGraph graph skeleton
- Explore / Plan / Develop / Review / Test 最小实现
- 人工 gate
- Redis SSE
- PostgreSQL checkpoint

允许降级：

- test 节点先做编译验证或 mock 测试环境
- ToolUniverse 与 Pipeline 不深度整合

#### Release C：生产增强版

目标：完整接近 `design.md` 目标态。

包含：

- QEMU 真测
- 完整统计口径
- IM 的 pipeline review 通知
- 更完整的 artifact / diff / history / observability
- 更严格的安全和回滚策略

结论：

- **把“兼容接管”和“Pipeline 新增”拆成两个发布门，是当前方案最值得做的优化。**

### 12.2 增加“契约冻结层”，避免后续反复返工

当前方案已经列了兼容 API，但还可以再强化为“可自动校验的契约资产”。

建议新增以下产物：

1. `tests/contracts/http/`
   - 保存关键接口的 request/response golden fixtures
2. `tests/contracts/sse/chat/`
   - 保存 Chat SSE 事件序列样本
3. `tests/contracts/sse/cases/`
   - 保存 Pipeline SSE 事件序列样本
4. `docs/compatibility-matrix.md`
   - 记录旧接口 -> 新实现 -> 验收状态

建议的 golden fixtures 范围：

- `/auth/login`
- `/auth/status`
- `/sessions`
- `/sessions/{id}`
- `/sessions/{id}/chat` SSE
- `/statistics/summary`
- `/task-settings`
- `/im/settings`
- `/api/v1/chat`

这项优化的价值：

- 能把“前端兼容”从人工感觉变成自动校验。
- 后续重构 statistics / auth / chat runner 时，不容易悄悄破契约。

### 12.3 增加“反腐层”，隔离新系统和旧 ScienceClaw 模块

当前计划中已经有 `deepagents_bridge.py` 的概念，但建议再明确成统一的 **Anti-Corruption Layer**。

建议新增：

```text
backend/legacy_bridge/
├── deepagents.py
├── im.py
├── tool_registry.py
├── skill_registry.py
└── task_invocation.py
```

设计原则：

1. 新代码不直接 import `ScienceClaw/backend/route/*`
2. 新代码尽量不依赖旧 Mongo 文档结构细节
3. 所有复用旧逻辑的入口都通过 bridge 层暴露稳定接口

推荐做法：

- DeepAgents：通过 `legacy_bridge/deepagents.py` 暴露 `run_chat() / stop_chat() / serialize_event()`
- IM：通过 `legacy_bridge/im.py` 暴露 `bind_lark() / get_settings() / start_wechat()`
- Tools/Skills：通过 `legacy_bridge/tool_registry.py` 和 `skill_registry.py` 暴露只读查询与保存动作

好处：

- 后续即使彻底移除旧 ScienceClaw backend，也只需要替换 bridge 实现，而不是全局改动。

### 12.4 增加“仓库工作区策略”，这是当前方案最缺的技术细节之一

当前方案已经区分了 `workspace/chat` 和 `workspace/cases`，但还缺少 **目标仓库 checkout / 缓存 / worktree / 清理策略**。这对 Pipeline 至关重要。

建议新增 `RepoWorkspaceManager`：

```text
backend/pipeline/repo_workspace.py
```

职责：

1. 维护目标仓库镜像缓存
2. 为每个 case 创建独立 worktree
3. 固定 base commit / branch
4. 生成 patch 之前保证工作树干净
5. 结束后清理临时目录，保留 final artifact

建议目录：

```text
workspace/
├── repo-cache/
│   ├── linux.git/
│   ├── qemu.git/
│   └── opensbi.git/
├── cases/
│   └── {case_id}/
│       ├── worktree/
│       ├── artifacts/
│       ├── manifests/
│       └── logs/
└── chat/
```

关键规则：

- 每个 case 使用独立 worktree，而不是直接操作 repo-cache。
- `target_repo + target_branch + base_commit` 必须写进 case metadata。
- `develop` / `review` / `test` 必须操作同一 worktree 快照或明确衍生快照。

这项优化的价值：

- 避免多个 case 互相污染代码树。
- 为 review/test/debug/reproduce 提供稳定基础。

### 12.5 增加“幂等 + 锁 + 状态卫兵”设计

这是当前方案第二个明显可优化点。现在虽然写了幂等和 review_id，但还不够系统。

建议新增三类控制：

#### A. Session 级锁

适用于：

- 同一个 session 同时发两次 chat
- 同时 stop + chat

实现建议：

- Redis lock：`lock:session:{session_id}`
- TTL 30-60s

#### B. Case 级锁

适用于：

- 重复 start case
- 同时两个 review submit
- stop / review / resume 竞争

实现建议：

- Redis lock：`lock:case:{case_id}`
- 所有变更 case 状态的写操作先拿锁

#### C. 状态卫兵

每个关键命令都先做状态校验，例如：

- 只有 `created|failed|abandoned` 可 `start`
- 只有 `pending_*` 可 `review`
- 只有 `running` 可 `stop`

建议新增：

```text
backend/pipeline/guards.py
```

把所有状态转换合法性收口在一个模块里。

### 12.6 增加 Feature Flags 和 Kill Switch

当前方案已经有“隐藏 Cases 入口”的概念，但建议系统化。

建议增加以下 flags：

- `FEATURE_CASES_UI_ENABLED`
- `FEATURE_PIPELINE_EXECUTION_ENABLED`
- `FEATURE_PIPELINE_TEST_NODE_ENABLED`
- `FEATURE_NEW_AUTH_ENABLED`
- `FEATURE_NEW_STATISTICS_ENABLED`
- `FEATURE_IM_PIPELINE_NOTIFICATIONS_ENABLED`

建议用途：

1. 新 backend 已上线，但先隐藏 Cases UI
2. Cases UI 可见，但 Pipeline start 按钮对非 admin 关闭
3. test 节点临时异常时，仅关闭 test node，其他链路仍可联调
4. 新统计异常时，可临时切回兼容实现

这项优化会极大提高发布与回滚的灵活性。

### 12.7 增加统一“用量账本”，不要把成本统计散落在各模块里

当前方案已有 statistics 和 cost 字段，但还可以再优化成统一 ledger。

建议新增：

```text
backend/services/usage_ledger.py
```

统一记录：

- `mode`
- `entity_type`：`session|case`
- `entity_id`
- `stage`
- `model_provider`
- `model_name`
- `input_tokens`
- `output_tokens`
- `cost_usd`
- `duration_ms`
- `created_at`

建议存储：

- Mongo 集合 `usage_ledger`

用途：

1. Chat 统计
2. Pipeline 统计
3. 成本对账
4. 异常排查
5. 未来配额/预算控制

价值：

- 避免 session、case、statistics 各自记一套 token 数据导致口径漂移。

### 12.8 增加 Artifact Manifest，提升可追溯性与可恢复性

当前方案已经有 artifact 路径规划，但还缺少“每轮产物的结构化清单”。

建议每个阶段/轮次增加 manifest：

```text
workspace/cases/{case_id}/manifests/
├── explore.json
├── plan.json
├── develop.round1.json
├── review.round1.json
└── test.json
```

建议 manifest 字段：

- `case_id`
- `stage`
- `round_num`
- `input_refs`
- `artifact_paths`
- `summary`
- `workspace_snapshot`
- `base_commit`
- `created_at`

作用：

1. 断点恢复时快速找到本阶段产物
2. UI 展示 artifact 列表时不用扫描目录
3. 回放与审计更容易

### 12.9 增加“渐进发布路径”，不要只有最终切换和回滚

当前方案有切换和回滚，但还可以加一层灰度路径。

建议发布顺序：

1. 本地开发环境
2. 单机预发布环境
3. 仅 admin 用户启用新 auth + new backend
4. 仅 admin 显示 Cases 入口
5. 内部用户开放 Pipeline
6. 全量用户开放 Cases

对应策略：

- 前端根据 user role + feature flag 决定是否显示 Cases
- backend 根据 feature flag 决定是否允许执行 pipeline

这样做能把事故半径控制在更小范围。

### 12.10 再做一次范围裁剪，减少不必要耦合

如果追求第一阶段更稳，建议明确以下内容不是首版阻塞项：

1. `knowledge_entries` 的前端页面
2. Pipeline 的定时任务自动创建 case
3. Pipeline 的 IM 富通知卡片
4. Pipeline 复用 ToolUniverse 进行复杂科研工具编排
5. QEMU 真机级复杂回归测试
6. 多目标仓库并行支持

首版必须做好的只有：

1. Chat 全量兼容
2. Cases 可创建可查看
3. 五阶段能最小跑通
4. 人工 gate、生存恢复、事件流可工作

### 12.11 优化后的推荐实施模型

在当前 Phase 划分之上，建议实际执行时按下面的“里程碑驱动”来收口：

#### M1：兼容后端可接前端

验收：

- 登录
- chat
- files
- statistics
- tasks

#### M2：Cases 可见但仅静态

验收：

- `/cases`
- `/cases/:id`
- case CRUD

#### M3：Pipeline 可运行到 gate

验收：

- start
- pause
- resume
- SSE 正常

#### M4：五阶段最小跑通

验收：

- 完整 case 生命周期
- review 迭代
- artifact/history

#### M5：增强与上线

验收：

- QEMU / 统计统一 / IM 扩展 / 回滚演练

这比单纯按 Phase 更适合真实执行，因为每个里程碑都能形成可演示、可验收的闭环。

### 12.12 对当前项目方案的最终优化结论

基于现有方案，最应该补的不是更多“功能描述”，而是以下 6 个工程化支点：

1. **发布波次**：把兼容接管和 Pipeline 新增拆开。
2. **契约资产**：把 API/SSE 兼容变成自动化 golden tests。
3. **反腐层**：把新 backend 与旧 ScienceClaw 逻辑隔开。
4. **工作区管理**：为 repo cache / worktree / artifact manifest 建立明确机制。
5. **控制平面**：补齐锁、幂等、状态卫兵、feature flags。
6. **统一账本**：把 token/cost/duration 收口到 usage ledger。

如果把这 6 个点补上，当前方案会从“完整但偏重”变成“完整且可执行、可灰度、可回滚”的工程方案。
