# ScienceClaw (RV-Claw) 项目深度分析

> 分析日期：2026-05-01
> 分析范围：完整代码库（后端、前端、微服务、工具与技能系统）

---

## 1. 项目概述

**ScienceClaw**（内部代号 RV-Claw）是一款面向科研领域的个人 AI 助手，由中科自动太初（北京）科技有限公司开发，技术合作方为中科院自动化所 NLP 组。项目基于 **LangChain DeepAgents** 和 **AIO Sandbox** 基础设施构建，采用完全 Docker 化的多服务架构。

### 1.1 核心定位

- **目标用户**：科研人员、开发者、学生
- **核心能力**：多模态科研任务自动化（文献检索、数据分析、报告生成、代码执行）
- **差异化优势**：
  - 1,900+ 内置科学工具（ToolUniverse）
  - 多格式报告生成（PDF/DOCX/PPTX/XLSX）
  - 完全本地部署，隐私优先
  - 隔离沙箱执行，安全可控

### 1.2 版本与发布

- **当前版本**：v0.0.1（2026-03-13 发布）
- **许可证**：MIT
- **支持平台**：Windows（桌面安装包）、macOS/Linux（Docker）

---

## 2. 技术架构总览

### 2.1 技术栈全景

| 层级 | 技术选型 | 版本/说明 |
|---|---|---|
| **前端** | Vue 3 + TypeScript + Vite | Vue 3.3.4, Vite 4.3.9 |
| **前端 UI** | Tailwind CSS + reka-ui + lucide-vue-next | Tailwind 3.3.2 |
| **后端** | FastAPI + Python 3.13 | FastAPI 0.128.7 |
| **AI 框架** | LangChain + LangGraph + DeepAgents | LangGraph 1.0.8, DeepAgents 0.4.4 |
| **数据库** | MongoDB（主存储）+ PostgreSQL（Checkpointer） | MongoDB latest |
| **缓存/队列** | Redis | Redis 7-alpine |
| **搜索** | SearXNG + Crawl4AI | 微服务化部署 |
| **沙箱** | AIO Sandbox（Docker 隔离） | 字节跳动 VolcEngine 镜像 |
| **任务调度** | Celery + Celery Beat | Celery 5.3+ |
| **容器编排** | Docker Compose | 10 服务编排 |

### 2.2 服务拓扑图

```
┌─────────────────────────────────────────────────────────────┐
│                        用户浏览器                            │
│              http://localhost:5173 (Vue 3 SPA)              │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   frontend   │    │   backend    │    │scheduler_api │
│  (Node 20)   │    │  (FastAPI)   │    │ (FastAPI)    │
│   :5173      │    │   :8000      │    │   :8001      │
└──────────────┘    └──────┬───────┘    └──────┬───────┘
                           │                    │
        ┌──────────────────┼────────────────────┤
        │                  │                    │
        ▼                  ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   sandbox    │    │   mongo      │    │    redis     │
│ (AIO Sandbox)│    │  (MongoDB)   │    │   (Redis)    │
│   :8080      │    │   :27014     │    │   :6379      │
└──────────────┘    └──────────────┘    └──────────────┘
        │
        ▼
┌──────────────┐    ┌──────────────┐
│   websearch  │◄───│   searxng    │
│ (Search API) │    │ (SearXNG)    │
│   :8068      │    │   :8080      │
└──────────────┘    └──────────────┘
        ▲
        │
┌──────────────┐
│celery_worker │
│celery_beat   │
└──────────────┘
```

---

## 3. 后端架构详解（Backend）

后端位于 `ScienceClaw/backend/`，是项目的核心大脑，采用 **FastAPI** 框架构建，全部使用异步编程模型（async/await）。

### 3.1 应用入口与生命周期

**文件**：`main.py`

FastAPI 应用通过 `create_app()` 工厂函数创建，使用 `@asynccontextmanager` 管理生命周期：

```python
# 启动时依次执行
1. 连接 MongoDB
2. 初始化系统模型（init_system_models）
3. 创建默认管理员用户（ensure_admin_user）
4. 清理孤立会话（cleanup_orphaned_sessions）
5. 回填会话来源（backfill_session_sources）
6. 启动 IM 运行时（start_im_runtime）

# 关闭时依次执行
1. 优雅关闭 Agent（graceful_shutdown_agents）
2. 停止 IM 运行时（stop_im_runtime）
3. 断开 MongoDB 连接
```

**挂载的路由模块**（前缀 `/api/v1`）：
- `auth` — 认证与授权
- `sessions` — 会话管理（CRUD + SSE 聊天 + 文件操作）
- `file` — 文件上传下载
- `models` — LLM 模型配置管理
- `tooluniverse` — 科学工具查询与执行
- `task_settings` — 任务设置
- `memory` — 记忆/上下文管理
- `science` — 科学计算相关
- `chat` — 任务调用的聊天接口
- `statistics` — 使用统计
- `im` — 即时通讯（飞书/微信）

### 3.2 配置管理

**全局配置**：`config.py`

采用 **Pydantic Settings** 进行类型安全的配置管理，支持环境变量覆盖：

```python
class Settings(BaseSettings):
    model_ds_name: str      # LLM 模型名称
    model_ds_api_key: str   # API Key
    model_ds_base_url: str  # OpenAI 兼容接口地址
    max_tokens: int
    context_window: int
    mongodb_host: str       # MongoDB 连接
    websearch_base_url: str # 搜索服务地址
    sandbox_mcp_url: str    # 沙箱 MCP 地址
    # ... 飞书、认证、任务调度等配置
```

**用户级任务配置**：`task_settings.py`

存储在 MongoDB 中，支持按用户定制任务执行参数：

| 参数 | 默认值 | 说明 |
|---|---|---|
| `agent_stream_timeout` | 10800s (3h) | Agent 流式执行超时 |
| `sandbox_exec_timeout` | 1200s (20min) | 沙箱命令执行超时 |
| `max_tokens` | 8192 | 单次输出最大 token |
| `output_reserve` | 16384 | 输出预留 token |
| `max_history_rounds` | 10 | 历史消息保留轮数 |
| `max_output_chars` | 50000 | 输出最大字符数 |

### 3.3 DeepAgent 引擎（核心）

**目录**：`deepagent/`

这是整个系统最复杂的模块，负责 AI Agent 的构建、执行和监控。

#### 3.3.1 模型工厂（engine.py）

- **职责**：根据配置动态构造 LLM 实例
- **支持模型**：OpenAI GPT 系列、DeepSeek、Google Gemini、Kimi、MiniMax 等
- **关键特性**：
  - **Context Window 自动匹配**：根据模型名称自动匹配已知模型的上下文窗口大小（如 deepseek-chat → 131K）
  - **Monkey-patch**：对 langchain-openai 进行 monkey-patch，保留 `reasoning_content` 字段，支持 DeepSeek/Kimi 等思考模型的多轮工具调用
  - **`_SafeChatOpenAI` 包装类**：处理 content 扁平化、reasoning_content 注入、空响应容错

```python
# 已知模型上下文窗口映射（节选）
_KNOWN_CONTEXT_WINDOWS = [
    ("deepseek-v4",       1_000_000),
    ("deepseek-chat",     131_072),
    ("gpt-4o",            128_000),
    ("claude-3-5-sonnet", 200_000),
    # ... 共 30+ 模型
]
```

#### 3.3.2 Agent 组装器（agent.py）

- **职责**：将模型、工具、提示词、Skills、监控中间件组装成可执行的 DeepAgent
- **后端架构（Backend）**：
  - `HybridSandboxBackend`：混合沙箱后端
    - 文件操作（read/write/edit/ls/glob/grep）→ 本地 `/home/scienceclaw/`
    - 命令执行（execute）→ 远程 sandbox 容器（通过 REST API）
    - 通过 Docker 共享卷同步文件
  - `CompositeBackend`：组合后端，路由不同路径到不同后端
    - `/builtin-skills/` → `FilesystemBackend`（内置技能，只读，始终加载）
    - `/skills/` → `FilteredFilesystemBackend`（外置技能，可屏蔽/删除）
- **外部工具热加载**：
  - 从 `Tools/` 目录自动扫描 `@tool` 装饰的函数
  - 支持运行时热加载，无需重启服务
  - 通过 `dir_watcher.py` 监听文件变化（基于文件列表 + max mtime 快照对比）
- **Skills 加载**：
  - 内置 skills：`/app/builtin_skills/`（打包进 Docker 镜像，避免 macOS 大小写不敏感问题）
  - 外置 skills：`/app/Skills/`（用户下载或自行安装，支持管理）
  - 技能屏蔽：用户可在设置中屏蔽特定技能，存储在 MongoDB `blocked_skills` 集合
- **记忆系统**：
  - 全局记忆：`_memory/{user_id}/AGENTS.md` — 用户偏好 + 通用模式（超过 4000 字符自动截断）
  - 会话级记忆：`{workspace}/CONTEXT.md` — 当前项目上下文
- **中间件管道**（按顺序执行）：
  1. `ToolResultOffloadMiddleware`：大型结果自动落盘（默认阈值 3000 chars，read_file 等宽松工具 30000 chars）
  2. `SSEMonitoringMiddleware`：拦截工具执行前后，捕获参数/结果/耗时
  3. `SummarizationMiddleware`（deepagents 内置）：长上下文自动摘要
- **诊断模式**：`DiagnosticLogger` 通过 LangChain `BaseCallbackHandler` 记录每步 LLM 调用的完整上下文到 `_diagnostic/` 目录

#### 3.3.3 流式执行器（runner.py）

- **职责**：执行 Agent 对话，将结果以 **SSE（Server-Sent Events）** 流式推送给前端
- **架构设计**：
  - **双层事件来源**：
    1. **中间件层**：精确的工具前后拦截（参数、结果、精准计时、todolist 变化）
    2. **Stream 层**：AI 回复内容、最终消息
  - **思考内容提取**：支持三种模型格式的思考过程
    1. DeepSeek（OpenAI API）：`additional_kwargs["reasoning_content"]`
    2. Claude：content blocks 中 `type="thinking"`
    3. DeepSeek/Qwen（原生 API）：`<think>...</think>` 标签
- **SSE 事件类型**（共 12 种）：

| 事件类型 | 说明 |
|---|---|
| `message` | 完整的用户/助手消息 |
| `message_chunk` | 流式 token（逐字生成） |
| `message_chunk_done` | 流式结束标记 |
| `tool` | 工具调用事件（calling → called） |
| `step` | 执行步骤状态变化 |
| `plan` | Agent 执行计划更新 |
| `thinking` | 思考过程（reasoning_content） |
| `title` | 自动生成的会话标题 |
| `done` | 轮次完成（含统计数据+文件列表） |
| `error` | 错误事件 |
| `skill_save_prompt` | 提示保存技能 |
| `tool_save_prompt` | 提示保存工具 |

- **关键保护机制**：
  - **超时保护**：`agent_stream_timeout` 默认 3 小时
  - **取消支持**：`session.is_cancelled()` 检查，用户可随时停止会话
  - **历史预算**：`_compute_history_token_budget()` 动态计算历史 token 预算，三重保护（单条截断 + 轮次截取 + token 估算）
  - **Eval 模式**：`run_eval_task()` 非 SSE 执行，收集完整输出用于 Skill 测试

- **执行流程**：
  ```
  用户输入 → 创建/获取会话 → 构建 Agent → 流式执行（arun_science_task_stream）
    → 轮询中间件事件（drain_events）→ 合并 Stream 事件 → SSE 推送前端
  ```

#### 3.3.4 会话管理（sessions.py）

- **核心数据结构**：`ScienceSession`（dataclass）
  ```python
  @dataclass
  class ScienceSession:
      session_id: str
      thread_id: str          # LangGraph 线程 ID
      vm_root_dir: Path       # 沙箱工作目录
      mode: str = "deep"      # 会话模式
      plan: List[PlanStep]    # 执行计划
      user_id: Optional[str] = None
      model_config: Optional[Dict] = None
      status: str = "pending" # pending/running/completed
      # ... 未读消息、分享状态、置顶等
  ```
- **持久化**：会话数据同时保存在内存（活跃会话）和 MongoDB（持久化）
- **Planner**：自动生成 Markdown 格式的执行计划，保存到工作目录供 Agent 读取

#### 3.3.5 工具系统（tools.py & tooluniverse_tools.py）

**内置工具（tools.py）**：
- `web_search`：通过 websearch 微服务调用 SearXNG 进行多搜索引擎聚合查询
- `web_crawl`：通过 websearch 微服务调用 Crawl4AI 进行网页内容爬取
- `propose_skill_save` / `propose_tool_save`：Skill/Tool 创建提议
- `eval_skill` / `grade_eval`：Skill 评估与打分

**科学工具（tooluniverse_tools.py）**：
- `tooluniverse_search`：在 1,900+ 工具中搜索匹配项
- `tooluniverse_info`：获取工具详细信息
- `tooluniverse_run`：执行指定工具

#### 3.3.6 沙箱后端（full_sandbox_backend.py & filtered_backend.py）

- `FullSandboxBackend`：完整的沙箱后端实现，将文件操作和命令执行代理到 sandbox 容器
- `FilteredFilesystemBackend`：带过滤的文件系统后端，支持路径黑白名单、文件屏蔽

#### 3.3.7 SSE 协议与监控（sse_protocol.py & sse_middleware.py）

- **SSEProtocolManager**：全局单例，维护所有已知工具的元数据（图标、分类、描述），供前端展示
  - 注册约 **50+ 工具**的元数据，分为 search、filesystem、execution、network、data、skill、system、custom **8 个类别**
- **SSEMonitoringMiddleware**：
  - `wrap_tool_call` / `awrap_tool_call`：包装工具调用，捕获前后状态
  - `sse_events`：线程安全的 Lock 保护的事件队列
  - `drain_events()`：被 runner 轮询消费，在每个 stream chunk 后调用
  - 支持 todolist 变化追踪：对比前后 todo list，生成 `middleware_todos_update` 事件

### 3.4 路由层（route/）

各路由模块的职责：

| 模块 | 核心职责 |
|---|---|
| `auth.py` | 登录/注册/登出、JWT/Session 认证、OAuth 集成 |
| `sessions.py` | 会话 CRUD、SSE 聊天流、会话停止/分享、沙箱文件操作 |
| `chat.py` | 任务服务调用的聊天接口、自然语言转 crontab |
| `file.py` | 文件上传、下载、预览、删除 |
| `models.py` | LLM 模型配置管理（增删改查） |
| `tooluniverse.py` | 科学工具查询、执行、缓存 |
| `task_settings.py` | 任务执行参数配置 |
| `memory.py` | 长期记忆管理、上下文检索 |
| `science.py` | 科学计算任务接口 |
| `statistics.py` | 使用量统计、资源监控 |
| `im.py` | 飞书/Lark 消息收发、Webhook 处理 |

### 3.5 数据层（mongodb/ & db/）

- **Motor**：异步 MongoDB 驱动（motor 3.7.1）
- **数据库连接**：`mongodb/db.py` 中的 `db` 单例，管理连接池
- **数据集合**：sessions、users、models、tasks、files、statistics 等

**索引设计**：

| 集合 | 索引 | 用途 |
|---|---|---|
| `users` | `username` (unique) | 用户管理 |
| `sessions` | `user_id`, `updated_at` (desc) | 会话列表查询排序 |
| `session_events` | `session_id`, `timestamp` | 事件查询 |
| `blocked_skills` | `(user_id, skill_name)` (unique) | Skills 屏蔽 |
| `im_user_bindings` | `(platform, platform_user_id)` (unique) | IM 用户绑定 |
| `im_chat_sessions` | `(platform, chat_id, user_id, status)` | IM 聊天会话 |
| `im_message_dedup` | `(platform, message_id)` (unique) + TTL 24h | 消息去重 |

### 3.6 用户与认证（user/）

- **认证方式**：支持本地认证（bcrypt 哈希）和 OAuth 集成
- **依赖注入**：`get_current_user`、`require_user` FastAPI Dependencies
- **默认管理员**：启动时自动创建 admin/admin123（可配置）

**认证流程**：
```
用户登录 → bcrypt 密码验证 → secrets.token_urlsafe 生成 access_token/refresh_token
  → 存入 MongoDB user_sessions 集合 → 设置 httponly Cookie
  → 前端存储 access_token 到 localStorage
```

**Token 刷新**：axios 拦截器自动处理 401 响应，调用 `/auth/refresh` 获取新 token

### 3.7 IM 集成（im/）

采用**适配器模式**设计，支持多平台 IM 集成：

**架构组件**：
- `base.py`：定义 `IMPlatform` 枚举和基础接口
- `orchestrator.py`：`IMServiceOrchestrator` — 统一编排，注册多平台适配器
- `adapters/lark.py`：飞书适配器 + 消息格式化
- `lark_long_connection.py`：飞书长连接服务（事件订阅）
- `wechat_bridge.py`：微信 Bridge 实现
- `user_binding.py` / `user_binding_service.py`：跨平台用户绑定管理
- `session_manager.py`：IM 聊天会话管理
- `command_handler.py`：IM 命令处理（如 `/help`、`/status`）
- `migrations.py`：数据迁移（backfill session sources）

**消息流转**：
```
飞书/Lark 消息 → 长连接接收 → orchestrator 分发 → adapter 解析
  → 调用 backend /api/v1/sessions/{id}/chat → 获取 SSE 流
    → 格式化后推送回飞书群聊/私聊
```

### 3.8 通知总线（notifications.py）

**内存级异步通知系统**，基于 `asyncio.Queue` 实现扇出模式：

- 后端产生通知（如新消息、会话更新）时，推送到中央 Queue
- 多个 SSE 客户端（前端通知连接）订阅该 Queue，实现一对多广播
- 由 `useSessionNotifications` composable 管理连接生命周期（引用计数自动重连）

---

## 4. 前端架构详解（Frontend）

前端位于 `ScienceClaw/frontend/`，是一个基于 **Vue 3 + TypeScript + Vite** 的单页应用（SPA）。

### 4.1 技术栈

| 技术 | 用途 |
|---|---|
| Vue 3.3.4 | 前端框架（Composition API） |
| TypeScript 5.6.3 | 类型安全 |
| Vite 4.3.9 | 构建工具 |
| Tailwind CSS 3.3.2 | 原子化 CSS |
| reka-ui 2.5.0 | 无头 UI 组件库（Radix Vue） |
| lucide-vue-next 0.511.0 | 图标库 |
| vue-router 4.5.1 | 路由管理 |
| vue-i18n 9.14.4 | 国际化 |
| axios 1.8.4 | HTTP 客户端 |
| @microsoft/fetch-event-source 2.0.1 | SSE 连接 |
| marked 15.0.8 | Markdown 渲染 |
| highlight.js 11.11.1 | 代码高亮 |
| katex 0.16.38 | 数学公式渲染 |
| mermaid 11.13.0 | 流程图/图表 |
| monaco-editor 0.52.2 | 代码编辑器 |
| @xterm/xterm 6.0.0 + addon-fit | 终端模拟器 |
| @novnc/novnc 1.5.0 | VNC 浏览器预览 |
| framer-motion 10.12.16 | 动画库 |

### 4.2 路由结构

```typescript
// 主布局（需认证）
/chat
  ├── /              → HomePage（首页/会话列表）
  ├── /:sessionId    → ChatPage（聊天界面）
  ├── /skills        → SkillsPage（技能市场）
  ├── /skills/:name  → SkillDetailPage（技能详情）
  ├── /tools         → ToolsPage（工具市场）
  ├── /tools/:name   → ToolDetailPage（工具详情）
  ├── /science-tools/:name → ScienceToolDetail（科学工具详情）
  └── /tasks         → TasksPage（定时任务管理）

// 分享页面（无需认证）
/share/:sessionId    → SharePage（分享会话查看）

// 登录
/login               → LoginPage
```

### 4.3 目录结构

```
src/
├── main.ts              # 应用入口：路由创建 + 全局守卫 + i18n/MoleculeViewer 注册
├── App.vue              # 根组件：<router-view> + Toast + 主题初始化
├── api/                 # API 层（12 个模块）
│   ├── client.ts        # axios 实例 + SSE 封装 + token 自动刷新
│   ├── agent.ts         # 核心 Agent API（会话/对话/VNC/文件/技能/工具）
│   ├── auth.ts          # 认证 API（登录/注册/Token 管理）
│   ├── file.ts          # 文件上传/下载/签名 URL
│   ├── models.ts        # LLM 模型配置 CRUD
│   ├── tasks.ts         # 定时任务 API（独立 task-service）
│   ├── im.ts            # IM 集成（飞书 Webhook）
│   ├── memory.ts        # 记忆 API
│   ├── tooluniverse.ts  # ToolUniverse 科学工具 API
│   ├── webhooks.ts      # Webhook 配置
│   ├── taskSettings.ts  # 任务设置
│   └── index.ts         # 统一导出 + auth 初始化
├── pages/               # 页面组件（14 个）
│   ├── MainLayout.vue   # 主布局壳（LeftPanel + router-view + FilePanel + Settings）
│   ├── HomePage.vue     # 首页（欢迎区 + 快速提示卡 + 打字机动画）
│   ├── ChatPage.vue     # 核心对话页（~1340 行，SSE 事件驱动）
│   ├── LoginPage.vue    # 登录
│   ├── SharePage.vue    # 分享（公开对话）
│   ├── ShareLayout.vue  # 分享布局壳
│   ├── SkillsPage.vue   # 技能列表
│   ├── SkillDetailPage.vue
│   ├── ToolsPage.vue    # 工具列表
│   ├── ToolDetailPage.vue
│   ├── ScienceToolDetail.vue
│   ├── TasksPage.vue    # 定时任务
│   ├── TasksListPage.vue
│   └── TaskConfigPage.vue
├── components/          # 可复用组件（38+ 个）
│   ├── ChatBox.vue      # 输入框 + 文件附件 + 模型选择 + 技能管理 + Prompt 优化
│   ├── ChatMessage.vue  # 消息渲染（Markdown 管线）
│   ├── LeftPanel.vue    # 左侧导航 + 会话列表
│   ├── ToolPanel.vue    # 工具面板容器
│   ├── ToolPanelContent.vue  # 工具面板内容分发
│   ├── ActivityPanel.vue     # 思考+计划+工具时间线（Cursor 风格）
│   ├── SandboxTerminal.vue   # xterm 终端（只读，从 SSE 事件回放）
│   ├── VNCViewer.vue         # noVNC 浏览器查看
│   ├── FilePanel.vue         # 文件浏览面板
│   ├── PlanPanel.vue         # 执行计划面板
│   ├── MoleculeViewer.vue    # 3D 分子结构查看器（全局注册）
│   ├── toolViews/       # 5 个专用工具视图
│   │   ├── ShellToolView.vue     # Shell 命令 → SandboxTerminal
│   │   ├── BrowserToolView.vue   # 浏览器操作 → VNCViewer
│   │   ├── FileToolView.vue      # 文件操作（Monaco Editor）
│   │   ├── SearchToolView.vue    # 搜索结果展示
│   │   └── McpToolView.vue       # MCP 工具视图
│   ├── settings/        # 14 个设置面板组件
│   ├── login/           # 5 个登录相关表单
│   ├── icons/           # 28 个自定义图标组件
│   └── ui/              # 基础 UI（Dialog/Popover/Select/Toast/MonacoEditor...）
├── composables/         # 18 个 Composable（替代 Store）
│   ├── useAuth.ts       # 认证状态（全局单例）
│   ├── useI18n.ts       # 国际化创建 + locale 管理
│   ├── useTheme.ts      # 主题（light/dark）
│   ├── useLeftPanel.ts  # 左面板展开/折叠
│   ├── useFilePanel.ts  # 文件面板状态
│   ├── useSessionFileList.ts
│   ├── useSessionGrouping.ts   # 会话分组（按时间、置顶、运行中）
│   ├── useSessionListUpdate.ts # 会话列表更新协调
│   ├── useSessionNotifications.ts  # SSE 通知订阅（全局单例，引用计数）
│   ├── useMessageGrouper.ts   # 消息分组（process 组 vs 单条消息）
│   ├── usePendingChat.ts      # 首页→对话页的数据传递
│   ├── useSettingsDialog.ts   # 设置弹窗状态
│   ├── useTool.ts             # 工具名→视图/图标映射
│   └── ...
├── types/               # TypeScript 类型定义
│   ├── event.ts         # SSE 事件类型（12 种事件）
│   ├── message.ts       # 消息类型（6 种消息）
│   └── response.ts      # 后端响应类型
├── constants/           # 常量
│   ├── event.ts         # 事件总线常量
│   └── tool.ts          # 工具常量
├── utils/               # 工具函数
│   ├── eventBus.ts      # mitt 事件总线
│   ├── content.ts       # 内容转换/DOMPurify 配置
│   ├── markdownFormatter.ts  # Markdown 预格式化
│   ├── fileType.ts      # 文件类型判断
│   └── toast.ts         # Toast 通知
├── locales/             # 国际化
│   ├── en.ts            # 英文
│   └── zh.ts            # 中文
├── assets/              # 样式
│   ├── global.css       # 全局样式
│   └── theme.css        # CSS 变量主题定义
└── lib/
    └── utils.ts         # 通用工具（cn/clsx）
```

### 4.4 核心组件职责

| 组件 | 职责 |
|---|---|
| `ChatBox.vue` | 多行文本输入 + 文件附件（ChatBoxFiles）+ 模型选择下拉 + 技能管理面板 + **Prompt 智能优化**（调用 `/science/optimize_prompt`，LCS diff 高亮展示优化前后对比）+ 发送/停止按钮 |
| `ChatMessage.vue` | 完整的 Markdown 渲染管线：`formatMarkdown` → `preprocessMath`（KaTeX 占位符）→ `marked()` → `postprocessMath` → `DOMPurify.sanitize` → DOM 解析提取特殊组件（molecule-viewer / image-viewer / html-viewer / suggested-questions）；代码块支持语言标签/行号/折叠/全屏/复制；Mermaid 异步渲染+缓存；底部操作栏（点赞/点踩/复制/转PDF/查看本轮文件/统计信息） |
| `LeftPanel.vue` | 左侧双栏布局：60px 导航轨道（Chat/Skills/Tools/Tasks/Settings/Avatar）+ 可折叠抽屉（会话列表，支持搜索/过滤 All/Pinned/Running/按时间分组折叠） |
| `ToolPanel.vue` + `ToolPanelContent.vue` | 工具详情侧面板，根据工具类型分发到 5 种专用视图或通用 JSON 视图；显示工具名称、参数、状态、耗时 |
| `ActivityPanel.vue` | **Cursor 风格的思考+执行时间线面板**，分三个可折叠区域：Thoughts（流式思考内容）、To-dos（计划步骤+关联工具）、Actions（工具调用时间线） |
| `SandboxTerminal.vue` | xterm.js **只读终端**，从 SSE `tool` 事件历史中回放 shell 命令和输出（非实时 WebSocket），支持 ANSI 颜色、折叠长输出、自动滚动 |
| `VNCViewer.vue` | noVNC 远程桌面查看器，通过 `POST /sessions/:id/vnc/signed-url` 获取签名 WebSocket URL → 创建 RFB 连接，支持 `viewOnly` 和 `scaleViewport` |
| `MoleculeViewer.vue` | 分子结构 3D 查看器（全局组件，科研场景专用） |

### 4.5 前后端通信

#### 4.5.1 SSE（Server-Sent Events）

实时接收 Agent 执行流，使用 `@microsoft/fetch-event-source` 库：

- 支持自动重连、自定义请求头（认证）
- **10 分钟 SSE 超时**：无事件自动断开连接
- **12 种 SSE 事件类型**：

| 事件类型 | 数据 | 前端处理 |
|---|---|---|
| `message` | 完整消息 | 渲染到聊天列表 |
| `message_chunk` | `{content, event_id}` | 逐字追加到当前消息 |
| `message_chunk_done` | — | 结束当前流式消息 |
| `tool` | 工具调用元数据 | 更新 ToolPanel，显示 calling/called 状态 |
| `step` | 步骤状态 | 更新执行进度 |
| `plan` | 计划步骤列表 | 更新 PlanPanel，显示待办/完成 |
| `thinking` | 思考内容 | 渲染到 ActivityPanel 的 Thoughts 区域 |
| `title` | 自动标题 | 更新会话列表中的标题 |
| `done` | 统计数据+文件列表 | 显示本轮总结，刷新文件列表 |
| `error` | 错误信息 | Toast 提示 |
| `skill_save_prompt` | `{skill_name}` | 弹出保存技能提示栏 |
| `tool_save_prompt` | `{tool_name}` | 弹出保存工具提示栏 |

#### 4.5.2 REST API

- axios 实例封装，统一错误处理、认证头注入
- **Token 刷新**：401 响应自动触发 refresh token 流程
- 统一 `ApiResponse<T>` 响应格式（`{code, msg, data}`）

#### 4.5.3 文件上传/下载

- 上传：`POST /sessions/:id/upload`，Multipart form-data
- 下载：Blob 处理，支持大文件流式下载
- 沙箱文件读取：`GET /sessions/:id/sandbox-file`（Monaco Editor 预览）

### 4.6 沙箱交互

#### 4.6.1 终端（Shell）
- `SandboxTerminal.vue` 使用 `@xterm/xterm` 创建**只读终端**
- **不是实时 WebSocket 连接**，而是从 SSE `tool` 事件中提取 shell 命令的 `calling`（显示命令）和 `called`（显示输出）数据
- `ShellToolView.vue` 聚合所有 shell 执行历史，传入 `SandboxTerminal` 组件

#### 4.6.2 浏览器预览（VNC）
- `VNCViewer.vue` 使用 `@novnc/novnc` 的 RFB 类
- 流程：`POST /sessions/:id/vnc/signed-url` 获取签名 WebSocket URL → 创建 RFB 连接
- 支持 `viewOnly`（默认可交互）和 `scaleViewport`（自适应缩放）

#### 4.6.3 文件管理
- `FileToolView.vue`：使用 Monaco Editor 展示沙箱文件内容
- `FilePanel` / `SessionFileList`：浏览会话产出的文件
- 通过 `GET /sessions/:id/sandbox-file` 读取，`GET /sessions/:id/sandbox-file/download` 下载

---

## 5. 微服务架构

### 5.1 定时任务服务（task-service/）

**技术栈**：FastAPI + Celery + Celery Beat + Redis + Motor

**架构**：
- `scheduler_api`：FastAPI 服务，提供任务管理 REST API
- `celery_worker`：Celery Worker，执行任务
- `celery_beat`：Celery Beat，每 60 秒触发 `check_due_tasks` 检查到期任务

**核心功能**：
- 任务 CRUD（创建/列表/更新/删除）
- 自然语言定时规则：用户输入「每天早上9点」，LLM 转换为 crontab 表达式
  - 若主服务不可用，使用本地兜底规则（如「每天」→ `0 9 * * *`）
- **Webhook 多平台通知**：支持飞书、钉钉、企业微信卡片消息推送

**执行流程**：
```
Celery Beat 触发 → Worker 执行 run_task
  → 调用 backend POST /api/v1/chat（带 X-API-Key 认证，timeout=300s）
    → 记录 task_runs（status: pending → running → success/failed）
      → 推送 Webhook 通知到所有配置的渠道
```

**API 端点**：
- `POST /tasks` — 创建任务
- `GET /tasks` — 任务列表
- `GET /tasks/{id}` — 任务详情
- `PUT /tasks/{id}` — 更新任务
- `DELETE /tasks/{id}` — 删除任务
- `GET /tasks/{id}/runs` — 执行历史
- `POST /webhooks` — 创建 Webhook 渠道
- `GET /webhooks` — Webhook 列表
- `POST /webhooks/{id}/test` — 测试 Webhook

### 5.2 搜索爬虫服务（websearch/）

**技术栈**：FastAPI + SearXNG + Crawl4AI + Playwright

**职责**：
- 聚合多个搜索引擎结果（SearXNG 作为元搜索后端）
- 智能网页内容爬取和提取（Crawl4AI）

**目录结构**：
```
websearch/
├── main.py           # FastAPI 入口，启动时安装 Playwright Chromium
├── config.py         # 配置模块（SearXNG 地址/API 端口/爬虫参数）
├── logger.py         # 统一日志模块
├── seekr_sdk.py      # 轻量客户端 SDK（COPY 到 sandbox 供脚本使用）
├── api/
│   ├── search.py     # POST /web_search（纯搜索）+ POST /search（搜索+爬取）
│   └── crawler.py    # POST /crawl_urls（批量 URL 爬取）
├── service/
│   ├── search.py     # SearXNG 请求封装 + 搜索+爬取组合逻辑
│   └── crawler.py    # WebCrawler 类：Crawl4AI AsyncWebCrawler + Markdown 提取
├── config/
│   └── settings.yml  # SearXNG 引擎配置（Google/Bing/360Search）
└── i18n/             # 国际化
```

**爬虫技术细节**：
- **浏览器**：Playwright Chromium（headless 模式），启动时自动安装
- **内容过滤**：`PruningContentFilter`（threshold=0.6）剪枝噪音内容
- **Markdown 生成**：`DefaultMarkdownGenerator`（忽略链接/图片，不转义 HTML）
- **重试机制**：每个 URL 最多重试 2 次

**API 端点**：
- `POST /web_search` — 纯搜索（参数：query, limit）
- `POST /search` — 搜索+爬取（先搜索再爬取每个结果）
- `POST /crawl_urls` — 批量爬取 URL（参数：urls）

**安全配置**：
- API Key 验证（`apikey` Header）
- 请求超时：120 秒

### 5.3 隔离沙箱（sandbox/）

**基础镜像**：`enterprise-public-cn-beijing.cr.volces.com/vefaas-public/all-in-one-sandbox:latest`（字节跳动 VolcEngine AIO Sandbox）

**环境配置**：
- Python 3.12（通过符号链接统一）
- Node.js（npm 全局安装 skills、docx、pptxgenjs）
- 系统工具：poppler-utils（PDF）、pandoc（文档转换）、LibreOffice（Office 文档）
- 中文字体：fonts-wqy-microhei
- 开发工具：build-essential、clang

**核心文件**：
- `tool_runner.py`：**@tool 函数的沙箱执行器**
  - 接收 backend 通过 `POST /v1/shell/exec` 发起的调用
  - 使用 `importlib` 动态加载 `.py` 文件中的 `@tool` 函数
  - 执行 `tool_obj.invoke(args)`
  - **标记协议**：使用 `>>>TOOL_RESULT_JSON>>>` / `<<<TOOL_RESULT_JSON<<<` 标记包裹 JSON 结果，与工具自身的 print 输出分离，确保可靠解析
- `seekr_sdk.py`：websearch 微服务的客户端 SDK（COPY 到 sandbox site-packages，供脚本直接调用）

**安全隔离**：
- Docker 容器隔离
- `seccomp:unconfined`（完整系统调用支持，用于科研计算）
- 内存限制：默认 8GB（可配置）
- CPU 限制：默认 4 核（可配置）
- 共享卷：`./workspace` 挂载到 `/home/scienceclaw`，数据持久化在宿主机

**与 backend 的交互**：
- REST API（port 8080）：`POST /v1/shell/exec`、`POST /v1/file/{read,write,str_replace_editor}`、`POST /v1/file/list`
- 共享文件系统：backend 和 sandbox 通过 Docker volume 共享 `./workspace`

---

## 6. 工具与技能系统

### 6.1 四层工具架构

ScienceClaw 设计了清晰的分层工具架构，满足从基础搜索到专业科研的不同需求：

| 层级 | 说明 | 示例 |
|---|---|---|
| **Built-in Tools** | 核心搜索与爬取能力 | `web_search`, `web_crawl` |
| **ToolUniverse** | 1,900+ 科学工具，即开即用 | UniProt, OpenTargets, FAERS, PDB, ADMET |
| **Sandbox Tools** | 文件操作与代码执行 | `read_file`, `write_file`, `execute`, `shell` |
| **Custom @tool** | 用户自定义 Python 函数 | `Tools/` 目录热加载 |

### 6.2 工具热加载机制（AST + Sandbox 代理执行）

**目录**：`Tools/`

ScienceClaw 采用了精巧的 **AST 静态解析 + Sandbox 代理执行** 架构，这是其工具系统的核心设计亮点：

**加载流程**：
1. **变更检测**：`dir_watcher.py` 通过文件列表 + max mtime 快照对比检测 `Tools/` 目录变更
2. **AST 静态解析**：`__init__.py` 中的 `_parse_tool_file()` 用 Python AST 解析 `.py` 文件，提取 `@tool` 装饰器函数的元数据（函数名、docstring、参数类型、默认值）—— **不在 Backend 中 import 模块**
3. **代理工具创建**：`_create_proxy_tool()` 为每个工具创建 LangChain `StructuredTool`，其 `func` 是一个代理函数
4. **沙箱执行**：代理函数调用时，通过 Sandbox REST API 执行 `python3 /app/_tool_runner.py <file> <func> '<json_args>'`
5. **结果解析**：从沙箱输出中提取 `>>>TOOL_RESULT_JSON>>>` 和 `<<<TOOL_RESULT_JSON<<<` 之间的 JSON

**核心优势**：
- **测试环境 = 生产环境**：Backend 不需要安装工具的依赖包，彻底消除环境不一致问题
- **安全隔离**：所有自定义工具代码在 sandbox 容器中执行，backend 不受影响
- **热加载**：目录变更后自动重新扫描，Agent 下次执行时使用最新工具

**缓存策略**：
- 使用线程锁保护的 `_cached_tools` 列表
- `reload_external_tools(force=False)` 只在检测到目录变更时重新扫描
- Agent 启动时 `force=True` 强制扫描一次

### 6.3 技能系统（Skills）

Skills 是**结构化指令文档（SKILL.md）**，指导 Agent 完成复杂多步骤工作流。

**内置技能**（`builtin_skills/`）：

| 技能 | 能力 |
|---|---|
| `pdf` | 读取、创建、合并、拆分、OCR、生成专业 PDF 研究报告 |
| `docx` | 创建和编辑 Word 文档（封面、目录、表格、图表） |
| `pptx` | 生成和编辑 PowerPoint 幻灯片 |
| `xlsx` | 创建和操作 Excel 表格、CSV/TSV 数据处理 |
| `tool-creator` | 创建和升级自定义 `@tool` 函数（写 → 测 → 存） |
| `skill-creator` | 创建和优化技能（草稿 → 测试 → 评审 → 迭代） |
| `find-skills` | 从开放生态搜索、发现和安装社区技能 |
| `tooluniverse` | 统一访问 1,900+ 科学工具 |

**技能加载机制**：
- 内置 skills：打包进 Docker 镜像（`/app/builtin_skills/`），只读，始终加载
- 外置 skills：用户通过 `find-skills` 下载或手动安装到 `Skills/` 目录
- `CompositeBackend` 路由不同路径到不同后端，实现内置/外置 skills 的隔离管理

### 6.4 多格式报告生成

| 格式 | 技术实现 | 特性 |
|---|---|---|
| **PDF** | LaTeX (xelatex) + pandoc | 封面、目录、图表（柱状/饼状/折线）、文内引用、参考文献、学术排版 |
| **DOCX** | python-docx / docx (Node) | 封面、目录、表格、图片、蓝色上标引用、Word 原生格式 |
| **PPTX** | pptxgenjs (Node) | 幻灯片标题、要点、图片、演讲者备注 |
| **XLSX** | openpyxl / xlsx (Node) | 数据表、图表、多工作簿、CSV/TSV 导出 |

---

## 7. 数据流与交互流程

### 7.1 典型聊天会话流程

```
用户输入（前端 ChatInput）
    │
    ▼
POST /api/v1/sessions/{id}/chat （SSE 连接建立）
    │
    ▼
backend/route/sessions.py
    │
    ▼
runner.arun_science_task_stream()
    │
    ├──► agent.py 构建 DeepAgent（模型 + 工具 + Skills + 中间件）
    │
    ├──► LangGraph 执行图（规划 → 工具调用 → 观察 → 回复）
    │       │
    │       ├──► web_search / web_crawl → websearch 微服务
    │       ├──► tooluniverse_run → ToolUniverse 工具
    │       ├──► read_file / write_file / execute → sandbox 容器
    │       └──► 自定义工具 → Tools/ 目录热加载
    │
    ├──► SSEMonitoringMiddleware 捕获工具调用事件
    │
    └──► runner 轮询事件 + Stream chunks → SSE 推送
              │
              ▼
         前端 ChatMessage 实时渲染
```

### 7.2 定时任务执行流程

```
Celery Beat （每分钟检查）
    │
    ▼
发现到期任务 → Celery Worker 执行
    │
    ▼
调用 backend POST /api/v1/chat
    │
    ▼
创建临时会话 → 执行 LLM 任务
    │
    ▼
记录 task_runs 到 MongoDB
    │
    ▼
推送结果到飞书 Webhook（如配置）
```

### 7.3 文件操作数据流

```
前端文件上传
    │
    ▼
POST /api/v1/file/upload → backend 接收
    │
    ▼
保存到 ./workspace/{session_id}/
    │
    ▼
sandbox 容器通过共享卷访问同一文件
    │
    ▼
Agent 执行 read_file / write_file 操作
```

---

## 8. 安全与隔离设计

### 8.1 沙箱隔离

| 层面 | 措施 |
|---|---|
| **容器隔离** | Agent 代码执行完全在 sandbox Docker 容器内 |
| **资源限制** | 内存 8GB（可配置）、CPU 4 核（可配置）、shm 2GB |
| **文件隔离** | 宿主机 `./workspace` 挂载到容器 `/home/scienceclaw`，Agent 无法访问宿主机其他目录 |
| **网络隔离** | 容器间通过 Docker 内部网络通信，sandbox 不暴露公网端口（仅 18080 用于内部通信） |
| **seccomp** | `seccomp:unconfined` 允许完整系统调用（科研计算需要），但受容器边界限制 |

### 8.2 认证与授权

- **本地认证**：bcrypt 密码哈希，Session Cookie 或 JWT
- **OAuth 集成**：支持第三方 OAuth 登录（通过 `AUTH_PROVIDER` 配置）
- **路由保护**：`requiresAuth` meta + `get_current_user` dependency
- **API Key**：任务服务调用 backend 时使用共享 API Key 验证

### 8.3 数据隐私

- **本地优先**：所有数据存储在本地 MongoDB 和 `./workspace`，不上传外部服务器
- **环境变量敏感信息**：API Key、密码等通过环境变量或 `.env` 注入，不硬编码
- **诊断模式**：可选开启，仅用于本地质量分析，数据不外传

---

## 9. 部署与运维

### 9.1 Docker Compose 服务清单

| 服务名 | 镜像/构建 | 端口 | 依赖 |
|---|---|---|---|
| `sandbox` | `scienceclaw-sandbox:local` | 18080:8080 | - |
| `mongo` | `mongo:latest` | 27014:27017 | - |
| `redis` | `redis:7-alpine` | - | - |
| `searxng` | `searxng/searxng:latest` | 26080:8080 | - |
| `websearch` | `scienceclaw-websearch:local` | 8068:8068 | searxng |
| `backend` | `scienceclaw-backend:local` | 12001:8000 | sandbox, mongo, websearch |
| `scheduler_api` | `scienceclaw-task-service:local` | 12002:8001 | mongo, redis, backend |
| `celery_worker` | `scienceclaw-task-service:local` | - | scheduler_api, redis, backend |
| `celery_beat` | `scienceclaw-task-service:local` | - | scheduler_api, redis |
| `frontend` | `node:20-bookworm-slim` | 5173:5173 | backend, scheduler_api |

### 9.2 部署模式

1. **生产部署（推荐）**：
   ```bash
   docker compose -f docker-compose-release.yml up -d --pull always
   ```
   - 拉取预构建镜像，无需本地编译
   - 适合普通用户

2. **开发部署**：
   ```bash
   docker compose up -d --build
   ```
   - 从源码构建所有镜像
   - 支持热重载（backend `--reload`，frontend `npm run dev`）

3. **国内加速**：
   ```bash
   docker compose -f docker-compose-china.yml up -d --build
   ```
   - 使用国内镜像源加速依赖下载

### 9.3 健康检查

- **sandbox**：`curl http://127.0.0.1:8080/v1/docs`
- **backend**：`curl http://127.0.0.1:8000/api/v1/auth/status`
- 自动重启策略：`unless-stopped`

### 9.4 日志与监控

- **日志**：`loguru` 统一日志，`docker compose logs -f [service]` 查看
- **诊断模式**：`DIAGNOSTIC_MODE=1` 记录每步 LLM 调用的完整上下文
- **资源监控**：前端内置资源监控面板，显示 LLM 资源消耗和服务健康状态
- **Google Analytics**：前端集成 `vue-gtag`（Tag ID: G-XCRZ3HH31S）

---

## 10. 项目亮点与评价

### 10.1 架构优势

1. **模块化微服务设计**：10 个服务各司其职，通过 Docker Compose 统一编排，易于扩展和维护
2. **双层 Agent 架构**：LangGraph 负责底层执行图，DeepAgents 提供高层抽象（Skills、Tools、Sandbox 集成）
3. **四层工具系统**：从基础搜索到专业科研工具，覆盖全面，扩展性强
4. **热加载机制**：Tools 和 Skills 支持运行时热加载，无需重启服务，开发体验优秀
5. **多模型支持**：通过 engine.py 的模型工厂，支持 OpenAI、DeepSeek、Gemini、Claude 等主流模型
6. **SSE 流式通信**：前后端通过 SSE 实时传输 Agent 执行流，用户体验流畅

### 10.2 工程实践亮点

1. **AST 解析 + Sandbox 代理执行**：Tools 热加载采用 AST 静态解析提取元数据（不在 backend import 模块），代理函数将实际执行转发到 sandbox 容器。这一设计彻底消除了「开发环境装了一套依赖，生产环境另一套」的问题，是科研工具系统的典范架构
2. **`_SafeChatOpenAI` 包装类**：在 langchain-openai 之上封装安全层，处理 content 扁平化、reasoning_content 注入、空响应容错，提升生产稳定性
3. **Monkey-patch 的务实性**：对 langchain-openai 进行 monkey-patch 以支持 reasoning_content，虽然不够优雅，但有效解决了 DeepSeek/Kimi 等思考模型的多轮工具调用问题
4. **Docker BuildKit 缓存**：Dockerfile 中大量使用 `--mount=type=cache` 加速构建，首次构建后依赖层可复用
5. **混合沙箱后端**：文件操作本地执行、命令执行远程 sandbox，平衡了性能与安全
6. **CompositeBackend 路由**：内置/外置 skills 的隔离管理，避免用户误删核心能力
7. **原子文件写入**：`_atomic_write_text` 使用临时文件 + replace 保证文件写入原子性
8. **计划持久化**：Planner 生成的 Markdown 计划保存到工作目录，Agent 可随时读取当前进度
9. **结果自动落盘**：`ToolResultOffloadMiddleware` 在工具返回超过阈值（默认 3000 chars，read_file 等 30000 chars）时自动将完整结果写入文件，避免阻塞 LLM 上下文

### 10.3 潜在改进点

1. **⚠️ 测试覆盖严重不足**：`tests/` 目录为空，项目完全没有单元测试、集成测试或 E2E 测试。这是最大的技术债务，建议优先引入 pytest + Playwright 测试体系
2. **数据库选型**：目前主要使用 MongoDB，对于关系型数据（如用户权限、任务依赖）可能不够理想，可考虑引入 PostgreSQL 处理结构化数据
3. **配置分散**：环境变量分布在 `.env`、`docker-compose.yml`、代码默认值多处，维护成本较高，建议统一配置管理中心
4. **错误处理**：部分模块使用大量 `try/except Exception` 捕获，可能隐藏真正的错误根因，建议细化异常类型
5. **前端状态管理**：采用 18 个 composable 替代 Pinia/Vuex，虽然轻量但复杂状态（如 ChatPage 的 22 个状态字段）可能难以维护
6. **API 版本控制**：当前仅 `/api/v1`，未来扩展时需注意向后兼容
7. **文档生成耦合**：PDF/DOCX/PPTX/XLSX 四种格式的生成逻辑分散在 Python/Node.js 脚本中，维护和调试成本较高

### 10.4 与竞品的差异化

| 维度 | ScienceClaw | OpenAI ChatGPT | Claude Projects | AutoGPT |
|---|---|---|---|---|
| **本地部署** | ✅ 完全本地 | ❌ 云端 | ❌ 云端 | ✅ 可本地 |
| **沙箱隔离** | ✅ Docker 隔离 | ❌ 无 | ❌ 无 | ⚠️ 有限 |
| **科学工具** | ✅ 1,900+ | ⚠️ 有限 | ⚠️ 有限 | ❌ 无 |
| **报告生成** | ✅ 4 种格式 | ⚠️ 仅文本 | ⚠️ 仅文本 | ❌ 无 |
| **定时任务** | ✅ 内置 Celery | ❌ 无 | ❌ 无 | ❌ 无 |
| **IM 集成** | ✅ 飞书/Lark | ❌ 无 | ❌ 无 | ❌ 无 |
| **开源** | ✅ MIT | ❌ 闭源 | ❌ 闭源 | ✅ MIT |

---

## 11. 总结

ScienceClaw 是一款架构清晰、功能完整的科研 AI 助手。其设计充分体现了**模块化、可扩展、安全优先**的理念：

- **后端**以 FastAPI + LangGraph + DeepAgents 为核心，构建了强大的 Agent 执行引擎
- **前端**以 Vue 3 实现了流畅的聊天体验和丰富的工具面板
- **微服务**通过 Celery、SearXNG、AIO Sandbox 等专业化组件，实现了任务调度、搜索、隔离执行的能力
- **工具与技能系统**通过四层架构和 SKILL.md 规范，提供了极强的扩展性

项目适合作为个人科研工作站部署，也具备良好的二次开发基础。建议在后续版本中加强测试覆盖、完善文档、优化配置管理，以提升生产环境的稳定性和可维护性。

---

*本文档基于对 ScienceClaw 代码库的全面分析生成，涵盖后端、前端、微服务、工具与技能系统的实现细节。*
