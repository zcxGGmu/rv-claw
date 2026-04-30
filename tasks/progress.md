# RV-Claw 重构开发进度跟踪

> **文档用途**: 细粒度任务清单，用于跟踪重构各阶段实际开发进度
> **关联文档**: [refactor-plan-v3.md](./refactor-plan-v3.md)（权威重构方案）
> **更新规则**: 每完成一个子任务立即标记 ✅，状态变更需记录日期
> **版本**: v2.0（2026-04-29）
> **优化项**: 增加依赖关系图、验收标准（AC）、拆分粗粒度任务、补充遗漏任务

---

## 进度总览

```
Phase 0: 基础架构          [░░░░░░░░░░] 0%  (0/25)
Phase 1: Chat 模式完整迁移  [░░░░░░░░░░] 0%  (0/21)
Phase 2: Pipeline 后端骨架  [░░░░░░░░░░] 0%  (0/38)
Phase 3: Pipeline 前端集成  [░░░░░░░░░░] 0%  (0/31)
Phase 4: 集成测试与优化      [░░░░░░░░░░] 0%  (0/22)
Phase 5: 生产准备           [░░░░░░░░░░] 0%  (0/8)
─────────────────────────────────────────
总计: 0% (0/145)
```

---

## Phase 0: 基础架构（Week 1-2）

**目标**: 搭建双模式开发基础，确保 ScienceClaw 功能无损
**DoD**: docker compose up 成功启动 10+ 服务 | pytest 现有测试通过 | pnpm build 成功 | admin/user 双角色认证正常 | PostgreSQL checkpointer 表自动创建 | 所有新目录结构就绪 | Secrets 管理方案落地 | Feature Flag 机制就绪

### Phase 0 任务依赖关系

```mermaid
flowchart TD
    P01[P0.1 设计文档] --> P02[P0.2 目录结构]
    P02 --> P03[P0.3 Docker扩展]
    P02 --> P04[P0.4 PG初始化]
    P02 --> P05[P0.5 Mongo索引]
    P02 --> P08[P0.8 依赖锁定]
    P03 --> P07[P0.7 环境变量]
    P04 --> P09[P0.9 健康检查]
    P05 --> P09
    P06[P0.6 RBAC] --> P010[P0.10 回归基线]
    P07 --> P010
    P08 --> P010
    P09 --> P010
    P010 --> P011[P0.11 CI/CD]
    P012[P0.12 DB迁移] --> P010
    P013[P0.13 Secrets] --> P07
    P014[P0.14 FeatureFlag] --> P010
```

> **图例**: 箭头表示"完成后才能开始"。无箭头连接的任务可并行开发。

---

### P0.1 创建缺失设计文档

- [ ] **P0.1.1** 创建 `tasks/mvp-tasks.md`
  - [ ] 定义 MVP 范围（Chat + Pipeline 双模式）
  - [ ] 列出 Sprint 0-10 任务分配
  - [ ] 明确 Phase 1/2/3 边界
  - [ ] 记录已知技术债务
  > **AC**: 文档通过团队评审，无阻塞意见，已同步到所有干系人
- [ ] **P0.1.2** 创建 `tasks/migration-map.md`
  - [ ] 前端组件迁移矩阵（ScienceClaw → rv-claw）
  - [ ] 后端路由迁移矩阵
  - [ ] 文件重命名/路径变更清单
  - [ ] 废弃 API 清单
  > **AC**: 矩阵覆盖率100%，每个 ScienceClaw 组件都有明确去向（保留/改造/废弃/新增）
- [ ] **P0.1.3** 创建 `tasks/chat-architecture.md`
  - [ ] Chat 模式后端架构图（ChatRunner + asyncio.Queue SSE）
  - [ ] Session 状态管理流程
  - [ ] 与 Pipeline 模式的资源隔离说明
  > **AC**: 架构图能清晰说明 Chat SSE 与 Pipeline SSE 使用不同 Redis channel 隔离
- [ ] **P0.1.4** 创建 `tasks/conventions.md`
  - [ ] Python 编码规范（black, ruff, mypy）
  - [ ] TypeScript/Vue 编码规范
  - [ ] Git commit message 规范
  - [ ] 目录命名约定
  - [ ] API 设计规范（REST + SSE）
  > **AC**: 规范文件通过团队评审，CI 中已配置对应 linter 规则

---

### P0.2 初始化后端目录结构

- [ ] **P0.2.1** 创建 `ScienceClaw/backend/pipeline/` 目录
  - [ ] `__init__.py`
  - [ ] `graph.py`（空文件，带 TODO 注释）
  - [ ] `state.py`（空文件，带 TODO 注释）
  - [ ] `routes.py`（空文件，带 TODO 注释）
  - [ ] `cost_guard.py`（空文件，带 TODO 注释）
  - [ ] `event_publisher.py`（空文件，带 TODO 注释）
  - [ ] `artifact_manager.py`（空文件，带 TODO 注释）
  > **AC**: `find ScienceClaw/backend/pipeline -type f | wc -l` 返回 7
- [ ] **P0.2.2** 创建 `ScienceClaw/backend/pipeline/nodes/` 目录
  - [ ] `__init__.py`
  - [ ] `explore.py`（空文件）
  - [ ] `plan.py`（空文件）
  - [ ] `develop.py`（空文件）
  - [ ] `review.py`（空文件）
  - [ ] `test.py`（空文件）
  - [ ] `human_gate.py`（空文件）
  - [ ] `escalate.py`（空文件）
  > **AC**: 目录结构符合 design.md 附录 A
- [ ] **P0.2.3** 创建 `ScienceClaw/backend/adapters/` 目录
  - [ ] `__init__.py`
  - [ ] `base.py`（空文件，带抽象基类骨架注释）
  - [ ] `claude_adapter.py`（空文件）
  - [ ] `openai_adapter.py`（空文件）
  - [ ] `event_mapper.py`（空文件）
  > **AC**: 目录结构符合 design.md 附录 A
- [ ] **P0.2.4** 创建 `ScienceClaw/backend/datasources/` 目录
  - [ ] `__init__.py`
  - [ ] `patchwork.py`（空文件）
  - [ ] `mailing_list.py`（空文件）
  - [ ] `github_client.py`（空文件）
  - [ ] `isa_registry.py`（空文件）
  > **AC**: 目录结构符合 design.md 附录 A
- [ ] **P0.2.5** 创建 `ScienceClaw/backend/contracts/` 目录
  - [ ] `__init__.py`
  - [ ] `exploration.py`（空文件）
  - [ ] `planning.py`（空文件）
  - [ ] `development.py`（空文件）
  - [ ] `review.py`（空文件）
  - [ ] `testing.py`（空文件）
  > **AC**: 目录结构符合 design.md 附录 A

---

### P0.3 Docker Compose 扩展

- [ ] **P0.3.1** 修改根目录 `docker-compose.yml`
  - [ ] 新增 `postgres` 服务配置
  - [ ] 新增 `qemu-sandbox` 服务占位配置
  - [ ] `backend` 服务增加 `depends_on: postgres`
  - [ ] 更新服务间网络配置
  > **AC**: `docker compose config` 无语法错误，可解析出 10+ 个服务定义
- [ ] **P0.3.2** 创建 `docker-compose.override.yml`（本地开发用）
  > **AC**: 本地开发时 volume mount 源码目录，热重载生效
- [ ] **P0.3.3** 验证 `docker compose config` 无语法错误
  > **AC**: 命令返回 exit code 0，无 stderr 报错

---

### P0.4 PostgreSQL 初始化

- [ ] **P0.4.1** 创建 `postgres-init.sql`
  - [ ] 创建 `rv_checkpoints` 数据库
  - [ ] 创建 `rv` 用户并授权
  - [ ] 预留 LangGraph checkpointer 表（或依赖 `checkpointer.setup()`）
  > **AC**: 脚本能在干净 PostgreSQL 容器中成功执行，无 ERROR
- [ ] **P0.4.2** 创建 `ScienceClaw/backend/db/postgres.py`
  - [ ] `init_checkpointer()` 函数骨架
  - [ ] `AsyncConnectionPool` 配置
  > **AC**: 文件能通过 `python -m py_compile` 语法检查
- [ ] **P0.4.3** 本地验证 PostgreSQL 容器启动成功
  > **AC**: `docker compose up postgres` 后 `pg_isready -U rv -d rv_checkpoints` 返回 accepting connections
- [ ] **P0.4.4** 验证 `AsyncPostgresSaver.setup()` 自动建表成功
  > **AC**: 执行 setup() 后 `\dt` 能看到 checkpoints / checkpoint_blobs / checkpoint_writes 表

---

### P0.5 MongoDB 索引脚本

- [ ] **P0.5.1** 创建 `mongo-init.js`
  - [ ] `contribution_cases` 集合 + validator
  - [ ] `human_reviews` 集合
  - [ ] `audit_log` 集合
  - [ ] `stage_outputs` 集合
  > **AC**: `mongosh < mongo-init.js` 成功执行，`db.getCollectionNames()` 包含上述4个集合
- [ ] **P0.5.2** 在 `ScienceClaw/backend/db/collections.py` 中新增索引函数
  - [ ] `create_pipeline_indexes(db)`
  - [ ] `create_ttl_indexes(db)`
  > **AC**: 函数定义完整，包含 design.md §6.3 中所有索引
- [ ] **P0.5.3** 本地验证索引创建成功
  > **AC**: `db.contribution_cases.getIndexes()` 返回包含 status+created_at 复合索引

---

### P0.6 认证扩展（RBAC）

- [ ] **P0.6.1** 修改 `ScienceClaw/backend/user/dependencies.py`
  - [ ] 在 `User` 模型/Pydantic schema 中增加 `role` 字段（`admin` | `user`）
  - [ ] 修改 `get_current_user` 返回 `role`
  - [ ] 新增 `require_role(*roles)` 依赖装饰器
  > **AC**: `require_role("admin")` 能正确拦截 role=user 的请求并返回 403
- [ ] **P0.6.2** 修改 `ScienceClaw/backend/route/auth.py`
  - [ ] 注册接口默认 `role=user`
  - [ ] `/auth/me` 返回 `role`
  - [ ] `/auth/login` 返回 `role`
  > **AC**: 注册新用户后 MongoDB 文档含 `role: "user"`；admin 登录返回 `role: "admin"`
- [ ] **P0.6.3** 修改 `ScienceClaw/backend/user/bootstrap.py`
  - [ ] `ensure_admin_user()` 确保默认 admin 账号 `role=admin`
  > **AC**: 删除 users 集合并重启后端，admin 用户重建后 role=admin
- [ ] **P0.6.4** 数据库迁移：为现有 `users` 集合补 `role` 字段（默认 `user`）
  > **AC**: 运行迁移脚本后，所有现有用户都有 role 字段，无 null
- [ ] **P0.6.5** 验证 admin/user 双角色认证正常
  > **AC**: admin 能访问 DELETE /cases，user 访问同一端点返回 403

---

### P0.7 环境变量配置

- [ ] **P0.7.1** 更新 `.env.example`
  - [ ] `POSTGRES_URI`
  - [ ] `MAX_REVIEW_ITERATIONS=3`
  - [ ] `MAX_AGENT_TURNS=50`
  - [ ] `CLAUDE_MODEL`
  - [ ] `OPENAI_MODEL`
  - [ ] `CODEX_MODEL`
  - [ ] `MAX_CONCURRENT_CLAUDE=3`
  - [ ] `MAX_CONCURRENT_OPENAI=5`
  - [ ] `MAX_CONCURRENT_QEMU=2`
  > **AC**: 每个新增变量都有默认值和注释说明用途
- [ ] **P0.7.2** 更新 `ScienceClaw/backend/config.py`
  - [ ] 新增 PostgreSQL 配置项
  - [ ] 新增 Pipeline 配置项
  - [ ] 新增资源限制配置项
  > **AC**: `python -c "from config import settings; print(settings.POSTGRES_URI)"` 不报错

---

### P0.8 依赖锁定

- [ ] **P0.8.1** 更新 `ScienceClaw/backend/requirements.txt`
  - [ ] `langgraph>=0.3.0,<0.4.0`
  - [ ] `langchain>=0.3.0`
  - [ ] `claude-agent-sdk>=0.1.0,<1.0.0`
  - [ ] `openai-agents-sdk>=0.1.0,<1.0.0`
  - [ ] `psycopg_pool>=3.2.0`
  - [ ] `redis>=5.0.0`
  - [ ] `sse-starlette>=2.1.0`
  - [ ] `structlog>=24.0.0`
  - [ ] `tenacity>=9.0.0`
  - [ ] `aiofiles>=24.0.0`
  > **AC**: 所有新增依赖包能在 requirements.txt 中 `pip install` 成功（不报错）
- [ ] **P0.8.2** 创建 `requirements-pipeline.txt`（Pipeline 专用依赖）
  > **AC**: 文件包含 langgraph/langchain/claude-agent-sdk/openai-agents-sdk/psycopg_pool
- [ ] **P0.8.3** 本地验证 `pip install -r requirements.txt` 成功
  > **AC**: `pip install` 返回 exit code 0，`python -c "import langgraph, redis, structlog"` 成功

---

### P0.9 健康检查扩展

- [ ] **P0.9.1** 修改 `ScienceClaw/backend/main.py` `/health` 端点
  - [ ] 新增 PostgreSQL 连接检查
  - [ ] 新增 Redis 连接检查
  - [ ] 返回结构化健康状态 JSON
  > **AC**: `/health` 返回 `{status: "healthy", checks: {mongodb: "ok", postgres: "ok", redis: "ok"}}`
- [ ] **P0.9.2** 修改 `/ready` 端点
  - [ ] 检查 MongoDB + PostgreSQL + Redis 全部就绪
  > **AC**: 任一团数据库断开时 `/ready` 返回 503，`checks` 中对应项为 error

---

### P0.10 回归测试基线

- [ ] **P0.10.1** 记录当前 ScienceClaw 功能测试通过清单
  - [ ] Chat 多轮对话测试
  - [ ] 会话创建/删除/重命名测试
  - [ ] 文件上传/预览测试
  - [ ] 技能/工具加载测试
  - [ ] 登录/注册测试
  - [ ] 统计页面加载测试
  > **AC**: 清单文档化到 `tests/baseline/v1-functional-checklist.md`，每项有通过/失败标记
- [ ] **P0.10.2** 记录当前 `pytest` 通过率基线
  > **AC**: 记录 `pytest --tb=short` 输出中的 passed/failed 数量到 `tests/baseline/v1-pytest-summary.txt`
- [ ] **P0.10.3** 记录当前 `pnpm build` 是否成功
  > **AC**: 记录 `pnpm build` 的 exit code 和构建时间到 `tests/baseline/v1-build-summary.txt`

---

### P0.11 CI/CD 配置

- [ ] **P0.11.1** 创建/更新 `.github/workflows/ci.yml`
  - [ ] lint 阶段（ruff + mypy）
  - [ ] unit-test 阶段
  - [ ] integration-test 阶段
  - [ ] docker-build 阶段
  > **AC**: PR 提交后 GitHub Actions 4 个 stage 全部执行，lint 和 unit-test 为必填检查
- [ ] **P0.11.2** 配置 dependabot 监控依赖更新
  > **AC**: `.github/dependabot.yml` 存在，配置监控 pip 和 npm 依赖

---

### P0.12 数据库迁移脚本

- [ ] **P0.12.1** 创建 `ScienceClaw/backend/db/migrations/001_add_user_role.py`
  - [ ] 遍历 `users` 集合，为缺 `role` 字段的文档补 `role: "user"`
  - [ ] 幂等执行（重复运行无副作用）
  > **AC**: 脚本可重复执行，执行后 `db.users.find({role: {$exists: false}}).count() == 0`
- [ ] **P0.12.2** 创建 `ScienceClaw/backend/db/migrations/002_create_pipeline_collections.py`
  - [ ] 创建 `contribution_cases` / `human_reviews` / `audit_log` / `stage_outputs`
  - [ ] 创建 validator 和索引
  > **AC**: 迁移后 MongoDB 包含上述4个集合及对应索引

---

### P0.13 Secrets 管理方案

- [ ] **P0.13.1** 创建 `ScienceClaw/backend/config/secrets.py`
  - [ ] 从环境变量读取 API Key（不硬编码）
  - [ ] 支持 `.env` 文件加载（python-dotenv）
  - [ ] 生产环境敏感字段不可打印/日志泄露
  > **AC**: `str(settings.CLAUDE_API_KEY)` 在生产环境返回 `***` 或抛出异常，不暴露真实 key
- [ ] **P0.13.2** 更新 `.env.example`，标注哪些为 secrets
  > **AC**: secrets 变量名以 `***` 为默认值示例，并有 `⚠️ DO NOT COMMIT REAL VALUES` 注释
- [ ] **P0.13.3** 配置 `.gitignore` 确保 `.env` 不进入版本控制
  > **AC**: `.env` 和 `*.pem` / `*.key` 已在 `.gitignore` 中

---

### P0.14 Feature Flag 机制

- [ ] **P0.14.1** 创建 `ScienceClaw/backend/config/features.py`
  - [ ] `FeatureFlags` 配置类
  - [ ] `PIPELINE_ENABLED: bool = False`（默认关闭）
  - [ ] `QEMU_SANDBOX_ENABLED: bool = False`
  > **AC**: `PIPELINE_ENABLED=False` 时，访问 `/cases` 返回 404 或 503，前端隐藏 Cases 导航入口
- [ ] **P0.14.2** 前端读取 Feature Flag
  - [ ] 在 `useAuth` 或全局状态中增加 `featureFlags`
  - [ ] 根据 flag 动态显示/隐藏 Cases 导航
  > **AC**: 当后端 flag 关闭时，前端 LeftPanel 不显示 "Cases" 入口，直接访问 `/cases` 被重定向

---

### Phase 0 里程碑检查点

- [ ] **M0.1** Docker Compose 能启动全部服务（backend + postgres + mongo + redis + frontend + ...）
- [ ] **M0.2** admin/user 双角色认证端到端通过（登录→访问 admin 接口→切换 user→被拦截）
- [ ] **M0.3** `pytest` 现有测试全部通过（与基线一致，无回归）
- [ ] **M0.4** `pnpm build` 构建成功，无新增 error
- [ ] **M0.5** Feature Flag 机制就绪，Pipeline 功能默认关闭，不影响现有 Chat 功能
- [ ] **M0.6** Secrets 管理方案落地，`.env` 不被提交到 git

---

## Phase 1: Chat 模式完整迁移（Week 3-4）

**目标**: 将 ScienceClaw 前端功能完整迁移到 rv-claw，零功能丢失
**DoD**: 所有 ScienceClaw 页面可正常访问且功能完整 | 新增 `/cases` 路由可访问 | 设置系统新增 PipelineSettings | 左侧导航栏新增 Cases 入口 | E2E 回归测试基线通过 | 前端测试基础设施就绪 | Mock Server 可用 | OpenAPI → TS 自动生成链路打通

### Phase 1 任务依赖关系

```mermaid
flowchart TD
    P14[P1.4 类型定义] --> P15[P1.5 API类型]
    P15 --> P16[P1.6 Statistics迁移]
    P15 --> P19[P1.9 API整合]
    P11[P1.1 路由重构] --> P12[P1.2 LeftPanel]
    P12 --> P13[P1.3 MainLayout]
    P16 --> P17[P1.7 StatisticsPage]
    P18[P1.8 Settings] --> P110[P1.10 i18n]
    P111[P1.11 MockServer] --> P121[P1.12 前端测试]
    P113[P1.13 OpenAPI→TS] --> P14
    P121 --> P1111[P1.11 E2E基线]
```

---

### P1.1 前端路由重构

- [ ] **P1.1.1** 修改 `ScienceClaw/frontend/src/main.ts`
  - [ ] 导入 `CaseListView`、`CaseDetailView`、`StatisticsPage`
  - [ ] 新增 `/cases` 路由（`CaseListView`）
  - [ ] 新增 `/cases/:id` 路由（`CaseDetailView`）
  - [ ] 将 `/statistics` 路由指向 `StatisticsPage`
  - [ ] 保留所有现有路由不变
  > **AC**: `router.resolve('/cases')` 返回有效 route record，`/cases/:id` 含动态参数
- [ ] **P1.1.2** 修改 `MainLayout.vue` 路由守卫
  - [ ] 确保 `/cases` 走 `requiresAuth: true`
  > **AC**: 未登录用户访问 `/cases` 被重定向到 `/login?redirect=/cases`
- [ ] **P1.1.3** 验证路由表无冲突
  > **AC**: `pnpm build` 无路由警告，`vue-router` 不报告 duplicate path

---

### P1.2 LeftPanel 扩展

- [ ] **P1.2.1** 修改 `ScienceClaw/frontend/src/components/LeftPanel.vue`
  - [ ] 新增 "Cases" 导航入口图标 + 文字
  - [ ] 点击跳转 `/cases`
  - [ ] 当前路由高亮逻辑包含 `/cases`
  > **AC**: 点击 Cases 导航后 URL 变为 `/cases`，Cases 项高亮显示
- [ ] **P1.2.2** 调整导航顺序（Sessions → Cases → Tools → Skills → Tasks）
  > **AC**: 导航栏顺序与上述一致，无错位
- [ ] **P1.2.3** 移动端折叠逻辑适配新增入口
  > **AC**: 屏幕宽度 <768px 时 LeftPanel 折叠为图标，Cases 图标可见且可点击

---

### P1.3 MainLayout 改造

- [ ] **P1.3.1** 修改 `ScienceClaw/frontend/src/pages/MainLayout.vue`
  - [ ] 监听 `/cases` 路由时关闭 FilePanel（或保持打开但过滤 case 文件）
  - [ ] 确保 Cases 页面布局正确（不与 Chat 布局冲突）
  > **AC**: 从 Chat 切换到 Cases 后 FilePanel 自动隐藏（或显示 case 相关文件），布局无错位

---

### P1.4 类型定义

- [ ] **P1.4.1** 创建 `ScienceClaw/frontend/src/types/case.ts`
  - [ ] `CaseStatus` 联合类型（13 个状态值）
  - [ ] `Case` 接口（含 `cost`, `review_iterations` 等）
  - [ ] `CreateCaseRequest` 接口
  - [ ] `ListCasesParams` 接口
  - [ ] `PaginatedCases` 接口
  > **AC**: TypeScript 编译无类型错误，`CaseStatus` 能正确约束赋值
- [ ] **P1.4.2** 创建 `ScienceClaw/frontend/src/types/pipeline.ts`
  - [ ] `PipelineStage` 接口
  - [ ] `StageStatus` 联合类型
  - [ ] `StageType` 联合类型
  > **AC**: 类型能正确 import 并在组件中使用
- [ ] **P1.4.3** 创建 `ScienceClaw/frontend/src/types/event.ts`
  - [ ] `AgentEvent` 接口
  - [ ] `EventType` 联合类型（stage_change | agent_output | review_request | iteration_update | cost_update | error | completed）
  - [ ] `SSECallbacks` 类型
  > **AC**: `EventType` 与后端 PipelineEvent 的 event_type 一一对应
- [ ] **P1.4.4** 创建 `ScienceClaw/frontend/src/types/artifact.ts`
  - [ ] `Artifact` 接口
  - [ ] `ArtifactType` 联合类型
  > **AC**: 类型定义完整，无 any
- [ ] **P1.4.5** 创建 `ScienceClaw/frontend/src/types/review.ts`
  - [ ] `ReviewDecision` 接口
  - [ ] `ReviewVerdict` 接口
  - [ ] `ReviewFinding` 接口
  - [ ] `ReviewRecord` 接口
  > **AC**: `ReviewFinding.severity` 使用联合类型而非 string

---

### P1.5 API 类型定义

- [ ] **P1.5.1** 创建 `ScienceClaw/frontend/src/api/cases.ts`
  - [ ] `createCase(data)` 函数签名 + 类型
  - [ ] `listCases(params?)` 函数签名 + 类型
  - [ ] `getCase(caseId)` 函数签名 + 类型
  - [ ] `deleteCase(caseId)` 函数签名 + 类型
  - [ ] `startPipeline(caseId)` 函数签名 + 类型
  - [ ] `submitReview(caseId, decision)` 函数签名 + 类型
  - [ ] `getArtifacts(caseId, stage, round?)` 函数签名 + 类型
  - [ ] `getHistory(caseId)` 函数签名 + 类型
  - [ ] `subscribeCaseEvents(caseId, callbacks)` 函数签名 + 类型
  > **AC**: 所有函数签名与后端 API 一一对应，TypeScript 编译通过
- [ ] **P1.5.2** 创建 `ScienceClaw/frontend/src/api/reviews.ts`
  - [ ] `getReviewVerdict(caseId, iteration)` 函数签名
  > **AC**: 函数签名正确
- [ ] **P1.5.3** 创建 `ScienceClaw/frontend/src/api/artifacts.ts`
  - [ ] `downloadArtifact(caseId, path)` 函数签名
  - [ ] `getArtifactContent(caseId, path)` 函数签名
  > **AC**: 函数签名正确

---

### P1.6 Statistics API 迁移

- [ ] **P1.6.1** 修改 `ScienceClaw/backend/route/statistics.py`
  - [ ] 将 `/metrics/overview` 改为 `/statistics/summary`
  - [ ] 将 `/metrics/costs` 改为 `/statistics/costs`
  - [ ] 将 `/metrics/models` 改为 `/statistics/models`
  - [ ] 将 `/metrics/trends` 改为 `/statistics/trends`
  - [ ] 将 `/metrics/sessions` 改为 `/statistics/sessions`
  - [ ] 保留旧路由做 301 重定向（或直接废弃，前端同步改）
  > **AC**: 新路径返回 200，旧路径返回 301（如保留）或 404（如废弃），响应体结构不变
- [ ] **P1.6.2** 修改 `ScienceClaw/frontend/src/api/statistics.ts`
  - [ ] 更新所有 endpoint 路径
  > **AC**: 前端统计页面数据加载正常，Network 面板中请求 URL 为新路径

---

### P1.7 StatisticsPage

- [ ] **P1.7.1** 创建 `ScienceClaw/frontend/src/views/StatisticsPage.vue`
  - [ ] 从现有统计页复制基础布局
  - [ ] 新增 Pipeline 统计数据占位区域
  - [ ] 响应式布局适配
  > **AC**: 页面能正常渲染，Pipeline 统计区域有占位（显示 "Coming Soon" 或空图表）
- [ ] **P1.7.2** 删除旧 `MetricsView.vue`（如存在）
  > **AC**: 项目中无 `MetricsView.vue` 残留引用

---

### P1.8 Settings 扩展

- [ ] **P1.8.1** 创建 `ScienceClaw/frontend/src/components/settings/PipelineSettings.vue`
  - [ ] max_review_iterations 滑块（1-5）
  - [ ] default_model 下拉选择
  - [ ] cost_limit 输入框
  - [ ] QEMU 环境路径配置
  > **AC**: 表单能正确绑定数据，点击保存后数据持久化到后端（或 localStorage 临时方案）
- [ ] **P1.8.2** 修改 `SettingsTabs.vue`
  - [ ] 新增 "Pipeline" Tab
  - [ ] 点击渲染 `PipelineSettings`
  > **AC**: SettingsDialog 中能看到 Pipeline Tab，切换正常

---

### P1.9 API 层整合

- [ ] **P1.9.1** 修改 `ScienceClaw/frontend/src/api/index.ts`
  - [ ] 导出 `cases.ts` 中所有函数
  - [ ] 导出 `reviews.ts` 中所有函数
  - [ ] 导出 `artifacts.ts` 中所有函数
  > **AC**: `import { createCase, listCases } from '@/api'` 不报错

---

### P1.10 i18n 扩展

- [ ] **P1.10.1** 修改 `ScienceClaw/frontend/src/locales/zh.ts`
  - [ ] 新增 `pipeline` 命名空间（探索/规划/开发/审核/测试）
  - [ ] 新增 `review_actions` 命名空间（通过/驳回/放弃）
  - [ ] 新增 `case_status` 命名空间（13 个状态翻译）
  - [ ] 新增 `settings.pipeline` 翻译
  > **AC**: 前端切换语言后 Pipeline 相关文本正确显示中文
- [ ] **P1.10.2** 修改 `ScienceClaw/frontend/src/locales/en.ts`
  - [ ] 同步新增上述翻译键
  > **AC**: 中英文翻译键完全一致，无缺漏

---

### P1.11 E2E 基线测试

- [ ] **P1.11.1** 验证所有现有页面可访问
  - [ ] `/` HomePage
  - [ ] `/chat/:sessionId` ChatPage
  - [ ] `/chat/skills` SkillsPage
  - [ ] `/chat/tools` ToolsPage
  - [ ] `/chat/tasks` TasksPage
  - [ ] `/login` LoginPage
  - [ ] `/share/:token` SharePage
  > **AC**: 每个页面 HTTP 200，无 console error，核心功能可操作
- [ ] **P1.11.2** 验证新增 `/cases` 路由可访问（空页面即可）
  > **AC**: `/cases` 返回 200，页面有 "Cases" 标题，无 404/500
- [ ] **P1.11.3** 记录 E2E 基线通过截图
  > **AC**: `tests/e2e/baseline/` 目录下有各页面截图，与上次无视觉回归（通过 pixelmatch 或人工确认）

---

### P1.12 前端测试基础设施

- [ ] **P1.12.1** 配置 Vitest + Vue Test Utils
  - [ ] 安装 `vitest`、`@vue/test-utils`、`jsdom`、`@vitejs/plugin-vue`
  - [ ] 创建 `vite.config.test.ts`
  - [ ] 配置 `vitest.config.ts`（含 globals, environment: jsdom）
  > **AC**: `pnpm test:unit` 能运行，`HelloWorld.spec.ts` 样例测试通过
- [ ] **P1.12.2** 配置 Vue 组件覆盖率（v8 coverage）
  > **AC**: `pnpm test:unit --coverage` 生成覆盖率报告，`coverage/` 目录存在
- [ ] **P1.12.3** 配置 Playwright E2E 基线
  - [ ] `playwright.config.ts` 已配置 baseURL、screenshot 策略
  > **AC**: `pnpm test:e2e` 能运行，至少通过 1 个样例测试

---

### P1.13 Mock Server

- [ ] **P1.13.1** 创建 `ScienceClaw/frontend/mocks/handlers.ts`（MSW 或自定义 mock）
  - [ ] Mock `POST /api/v1/cases` → 返回 201 + mock case
  - [ ] Mock `GET /api/v1/cases` → 返回 mock case 列表
  - [ ] Mock `GET /api/v1/cases/:id/events` → 返回 mock SSE 事件流
  > **AC**: 前端在 Mock 模式下能完整展示 CaseListView 和 CaseDetailView，无需后端启动
- [ ] **P1.13.2** 配置前端开发环境自动启用 Mock
  > **AC**: `pnpm dev` 时 API 请求被拦截到 Mock Server，Network 面板显示 mock 响应

---

### P1.14 OpenAPI → TypeScript 自动生成

- [ ] **P1.14.1** 配置 `openapi-typescript` 或 `orval`
  - [ ] 安装生成工具到 `devDependencies`
  - [ ] 配置从 FastAPI `/openapi.json` 自动生成 `types/api.generated.ts`
  > **AC**: 运行 `pnpm gen:api` 后，`types/api.generated.ts` 自动更新，与后端 API 同步
- [ ] **P1.14.2** 在 CI 中增加类型生成检查
  > **AC**: CI 中运行生成命令后 `git diff --exit-code` 不报错（即已提交的生成文件是最新的）

---

### Phase 1 里程碑检查点

- [ ] **M1.1** 所有 ScienceClaw 原有页面功能 100% 正常（与 P0.10 基线对比无 regression）
- [ ] **M1.2** `/cases` 路由可访问，Cases 导航入口可见
- [ ] **M1.3** Settings 新增 PipelineSettings Tab，表单可交互
- [ ] **M1.4** 前端单元测试基础设施就绪，至少 1 个组件测试通过
- [ ] **M1.5** Mock Server 可用，前端开发无需依赖后端启动
- [ ] **M1.6** OpenAPI → TS 自动生成链路打通，前后端类型一致

---

## Phase 2: Pipeline 后端骨架（Week 5-8）

**目标**: 实现 Pipeline 后端核心，包括 LangGraph 引擎、Agent 节点、SSE 事件流
**DoD**: 可通过 API 创建案例并启动 Pipeline | SSE 事件流正常推送阶段变更 | 人工审核门可暂停并恢复 Pipeline | 产物文件正确写入文件系统 | 3 轮 Develop↔Review 迭代正常 | 成本熔断器在超限时报错 | 单元测试覆盖率 ≥ 70% | 数据种子/Fixture 就绪

### Phase 2 任务依赖关系

```mermaid
flowchart TD
    P21[P2.1 State] --> P22[P2.2 Graph]
    P22 --> P212[P2.12 HumanGate]
    P22 --> P29[P2.9 Explore]
    P23[P2.3 AdapterBase] --> P24[P2.4 Claude]
    P23 --> P25[P2.5 OpenAI]
    P26[P2.6 EventPub] --> P29
    P27[P2.7 Artifact] --> P29
    P28[P2.8 Cost] --> P29
    P24 --> P29
    P25 --> P210[P2.10 Plan]
    P24 --> P211[P2.11 Develop]
    P25 --> P214[P2.14 Review]
    P24 --> P215[P2.15 Test]
    P29 --> P213[P2.13 RouteHuman]
    P214 --> P216[P2.16 RouteReview]
    P212 --> P219[P2.19 Cases路由]
    P216 --> P219
    P218[P2.18 数据源] --> P29
    P220[P2.20 Reviews路由] --> P212
    P221[P2.21 Artifacts] --> P27
    P222[P2.22 Pipeline路由] --> P22
    P223[P2.23 main.py] --> P219
    P224[P2.24 契约] --> P29
    P224 --> P210
    P225[P2.25 调度器] --> P24
    P226[P2.26 审计] --> P219
    P227[P2.27 种子数据] --> P219
```

---

### P2.1 PipelineState 模型

- [ ] **P2.1.1** 创建 `ScienceClaw/backend/pipeline/state.py`
  - [ ] `PipelineState` TypedDict 定义
  - [ ] `case_id: str`
  - [ ] `target_repo: str`
  - [ ] `current_stage: Literal[...]`
  - [ ] `input_context: dict`
  - [ ] `exploration_result_ref: Optional[str]`
  - [ ] `execution_plan_ref: Optional[str]`
  - [ ] `development_result_ref: Optional[str]`
  - [ ] `review_verdict_ref: Optional[str]`
  - [ ] `test_result_ref: Optional[str]`
  - [ ] `review_iterations: int`
  - [ ] `max_review_iterations: int`
  - [ ] `review_score_history: list[float]`
  - [ ] `pending_approval_stage: Optional[str]`
  - [ ] `approval_count: int`
  - [ ] `total_input_tokens: int`
  - [ ] `total_output_tokens: int`
  - [ ] `estimated_cost_usd: float`
  - [ ] `last_error: Optional[str]`
  - [ ] `retry_count: int`
  > **AC**: `PipelineState` 能通过 `model_validate_json()` 成功序列化/反序列化，无丢失字段
- [ ] **P2.1.2** 编写 `test_state.py` 验证 PipelineState 序列化/反序列化
  > **AC**: pytest 通过，覆盖正常构造、缺失可选字段、类型错误三种场景

---

### P2.2 StateGraph 构建

- [ ] **P2.2.1** 创建 `ScienceClaw/backend/pipeline/graph.py`
  - [ ] `build_pipeline_graph()` 函数
  - [ ] 注册 9 个节点（explore, human_gate_explore, plan, human_gate_plan, develop, review, human_gate_code, test, human_gate_test, escalate）
  - [ ] 设置入口点 `set_entry_point("explore")`
  - [ ] 定义线性边（explore → human_gate_explore → plan → ...）
  - [ ] 定义人工门条件边（approve/reject/abandon）
  - [ ] 定义 Review 条件边（approve/reject/escalate）
  - [ ] `compile_graph()` 函数注入 `AsyncPostgresSaver`
  > **AC**: `build_pipeline_graph().compile()` 不报错，打印 `graph.get_graph().draw_mermaid()` 可见完整 10 节点拓扑
- [ ] **P2.2.2** 编写 `test_graph.py` 验证图结构
  > **AC**: 单元测试验证：从 explore 出发经 approve 到 plan 的最短路径存在；经 reject 回到 explore 的路径存在

---

### P2.3 AgentAdapter 基类

- [ ] **P2.3.1** 创建 `ScienceClaw/backend/adapters/base.py`
  - [ ] `AgentEvent` Pydantic 模型
  - [ ] `AgentAdapter` ABC 抽象基类
  - [ ] `execute()` 抽象方法（返回 `AsyncIterator[AgentEvent]`）
  - [ ] `cancel()` 抽象方法
  > **AC**: `issubclass(ClaudeAgentAdapter, AgentAdapter)` 为 True，未实现抽象方法的类实例化时抛出 TypeError
- [ ] **P2.3.2** 创建 `ScienceClaw/backend/adapters/event_mapper.py`
  - [ ] `map_claude_event()` 函数
  - [ ] `map_openai_event()` 函数
  > **AC**: 输入 SDK 原始事件对象，输出符合 `AgentEvent` schema 的字典

---

### P2.4 ClaudeAgentAdapter

- [ ] **P2.4.1** 创建 `ScienceClaw/backend/adapters/claude_adapter.py`
  - [ ] `ClaudeAgentAdapter` 类继承 `AgentAdapter`
  - [ ] `__init__` 配置（allowed_tools, permission_mode, max_turns, timeout_seconds=1800）
  - [ ] `_current_process` 进程追踪
  - [ ] `execute()` 方法：调用 `claude_agent_sdk.query()` + `asyncio.timeout()`
  - [ ] `cancel()` 方法：`SIGTERM` → `SIGKILL`
  - [ ] `_map_event_type()` 静态方法
  - [ ] `_extract_data()` 静态方法
  > **AC**: Mock SDK 调用下，`execute()` 能产出 AgentEvent 流；`cancel()` 能正确发送 SIGTERM 到子进程
- [ ] **P2.4.2** 编写 `test_claude_adapter.py`（Mock SDK 调用）
  > **AC**: Mock 测试通过，覆盖 execute 正常流、超时异常、cancel 三种场景

---

### P2.5 OpenAIAgentAdapter

- [ ] **P2.5.1** 创建 `ScienceClaw/backend/adapters/openai_adapter.py`
  - [ ] `OpenAIAgentAdapter` 类继承 `AgentAdapter`
  - [ ] `__init__` 配置（agent_config dict）
  - [ ] `execute()` 方法：调用 `agents.Agent` + `Runner.run()`
  - [ ] `cancel()` 方法（空实现或 Runner 取消）
  > **AC**: Mock SDK 调用下，`execute()` 能产出 AgentEvent 流，返回的 `final_output` 被正确映射
- [ ] **P2.5.2** 编写 `test_openai_adapter.py`（Mock SDK 调用）
  > **AC**: Mock 测试通过

---

### P2.6 EventPublisher

- [ ] **P2.6.1** 创建 `ScienceClaw/backend/pipeline/event_publisher.py`
  - [ ] `PipelineEvent` Pydantic 模型（seq, case_id, event_type, data, timestamp）
  - [ ] `EventPublisher` 类
  - [ ] `__init__` 接收 `aioredis.Redis`
  - [ ] `_seq_counters: dict[str, int]` 序列号管理
  - [ ] `publish()` 方法：
    - [ ] 序列号递增
    - [ ] `redis.publish()` 到 Pub/Sub
    - [ ] `redis.xadd()` 到 Stream（maxlen=500）
  - [ ] `get_events_since()` 方法：从 Stream 恢复事件
  > **AC**: `publish()` 后 Redis 中 `case:test:stream` 长度 +1；`get_events_since(0)` 能返回已发布的事件
- [ ] **P2.6.2** 编写 `test_event_publisher.py`
  > **AC**: 使用 fakeredis 或 mock 测试 publish/subscribe/recover 全流程

---

### P2.7 ArtifactManager

- [ ] **P2.7.1** 创建 `ScienceClaw/backend/pipeline/artifact_manager.py`
  - [ ] `ArtifactManager` 类
  - [ ] `__init__` 接收 `base_dir: str = "/data/artifacts"`
  - [ ] `get_case_dir(case_id, stage, round_num?)` 方法
  - [ ] `save_artifact(case_id, stage, filename, content, round_num?)` 方法
  - [ ] `load_artifact(relative_path)` 方法
  - [ ] `cleanup_case(case_id, keep_final=True)` 方法
  > **AC**: `save_artifact` 后文件系统存在对应路径；`load_artifact` 返回内容与保存一致；`cleanup_case` 后旧 round 目录被删除
- [ ] **P2.7.2** 编写 `test_artifact_manager.py`
  > **AC**: 使用临时目录测试，不依赖真实 `/data/artifacts`

---

### P2.8 CostCircuitBreaker

- [ ] **P2.8.1** 创建 `ScienceClaw/backend/pipeline/cost_guard.py`
  - [ ] `CostCircuitBreaker` 类
  - [ ] `__init__` 配置（max_cost_per_case=10.0, max_cost_per_hour=50.0）
  - [ ] `check_before_agent(state)` 方法
  - [ ] `_estimate_cost(state)` 方法（Claude: $3/M input, $15/M output）
  > **AC**: `check_before_agent` 在成本 9.9 美元时返回 True，在 10.1 美元时返回 False
- [ ] **P2.8.2** 编写 `test_cost_guard.py`
  > **AC**: 边界值测试通过（刚好低于/等于/高于阈值）

---

### P2.9 explore_node（已拆分：6 个子任务）

- [ ] **P2.9.1** 创建 `ScienceClaw/backend/pipeline/nodes/explore.py` 骨架 + Prompt 工程
  - [ ] `explore_node(state)` 函数签名
  - [ ] 定义 `EXPLORER_SYSTEM_PROMPT`（RISC-V 专用，含输出格式 JSON 要求）
  - [ ] 构建动态 prompt（拼接 input_context + target_repo）
  > **AC**: Prompt 字符串长度 >500 字符，包含明确的 JSON Schema 示例
- [ ] **P2.9.2** 实现 SDK 调用与流式事件处理
  - [ ] 实例化 `ClaudeAgentAdapter`
  - [ ] 调用 `execute()` 并异步迭代 `AgentEvent`
  - [ ] 每个 event 调用 `EventPublisher.publish()` 实时推送
  > **AC**: Mock 测试下，调用 explore_node 后 Redis 中至少收到 2 个 event（thinking + output）
- [ ] **P2.9.3** 实现结果解析与反序列化
  - [ ] 收集 SDK 输出字符串
  - [ ] 调用 `parse_agent_output()` 解析为 `ExplorationResult`
  - [ ] 处理 Markdown 代码块包裹、尾随逗号等容错
  > **AC**: 输入有效 JSON 返回 ExplorationResult 实例；输入带 Markdown 包裹的 JSON 也能正确解析
- [ ] **P2.9.4** 实现程序化验证 `verify_exploration_claims()`
  - [ ] URL 可达性验证（httpx head，超时 10s）
  - [ ] 文件路径安全检查（防止 `..` 遍历）
  - [ ] ISA 扩展名验证（对照 `RATIFIED_EXTENSIONS` 集合）
  - [ ] 证据数量检查（≥2 条）
  > **AC**: 输入含无效 URL 时该证据被过滤；输入含 `../etc/passwd` 时被拒绝；输入未知 ISA 扩展时 feasibility_score 下降
- [ ] **P2.9.5** 实现产物保存与状态返回
  - [ ] 调用 `ArtifactManager.save_artifact()` 保存 exploration_report.json
  - [ ] 更新 MongoDB `contribution_cases` 状态为 `pending_explore_review`
  - [ ] 返回 `{"exploration_result": ..., "current_stage": "human_gate_explore"}`
  > **AC**: MongoDB 中案例状态正确更新，产物文件存在且内容完整
- [ ] **P2.9.6** 编写 `test_explore_node.py`
  > **AC**: Mock 测试覆盖：正常探索、URL 不可达、JSON 解析失败并重试、证据不足

---

### P2.10 plan_node

- [ ] **P2.10.1** 创建 `ScienceClaw/backend/pipeline/nodes/plan.py`
  - [ ] `plan_node(state)` 异步函数
  - [ ] 定义 `dev_planner` Agent（OpenAI SDK）
  - [ ] 定义 `test_planner` Agent（OpenAI SDK）
  - [ ] 定义 `planner` Manager Agent（含 handoffs + InputGuardrail）
  - [ ] 调用 `OpenAIAgentAdapter.execute()`
  - [ ] 解析 `ExecutionPlan`
  - [ ] 保存产物
  - [ ] 返回 `{"execution_plan": ..., "current_stage": "human_gate_plan"}`
  > **AC**: Mock 测试下返回的 execution_plan 包含 dev_steps 和 test_cases 数组
- [ ] **P2.10.2** 编写 `test_plan_node.py`
  > **AC**: Mock 测试通过

---

### P2.11 develop_node

- [ ] **P2.11.1** 创建 `ScienceClaw/backend/pipeline/nodes/develop.py`
  - [ ] `develop_node(state)` 异步函数
  - [ ] 区分首次开发 vs 迭代修复（review_iterations > 0）
  - [ ] 构建开发提示（含 ExecutionPlan 或 ReviewVerdict）
  - [ ] 调用 `ClaudeAgentAdapter.execute()`（allowed_tools: Read/Write/Edit/Bash/Grep/Glob）
  - [ ] 收集开发产物（patch 文件、变更说明）
  - [ ] 保存产物
  - [ ] 返回 `{"development_result": ..., "current_stage": "review"}`
  > **AC**: Mock 测试下，review_iterations=0 时提示含 ExecutionPlan；review_iterations>0 时提示含 ReviewVerdict
- [ ] **P2.11.2** 编写 `test_develop_node.py`
  > **AC**: Mock 测试通过，覆盖首次开发和迭代修复两种场景

---

### P2.12 human_gate_node

- [ ] **P2.12.1** 创建 `ScienceClaw/backend/pipeline/nodes/human_gate.py`
  - [ ] `human_gate_node(state)` 异步函数
  - [ ] 使用 `langgraph.types.interrupt()` 暂停执行
  - [ ] 构建审批请求（含当前阶段产物摘要）
  - [ ] 返回 `Command(goto=decision["action"], update={...})`
  > **AC**: `interrupt()` 调用后 Pipeline 暂停，状态持久化到 PostgreSQL checkpointer
- [ ] **P2.12.2** 编写 `test_human_gate.py`
  > **AC**: Mock 测试验证 interrupt 被调用，返回的 Command.goto 与输入 decision 一致

---

### P2.13 route_human_decision

- [ ] **P2.13.1** 修改 `ScienceClaw/backend/pipeline/routes.py`
  - [ ] `route_human_decision(state)` 函数
  - [ ] 从 `approval_history` 读取最后决策
  - [ ] 返回 `"approve" | "reject" | "abandon"`
  > **AC**: 输入 approve 返回 "approve"；输入 reject 返回 "reject"；无历史记录返回 "abandon"
- [ ] **P2.13.2** 编写 `test_route_human.py`
  > **AC**: 三种决策路径全部覆盖

---

### P2.14 review_node（已拆分：5 个子任务）

- [ ] **P2.14.1** 实现确定性静态分析工具集成
  - [ ] 创建 `run_deterministic_checks(patch_path)` 函数
  - [ ] `checkpatch.pl` 集成（调用 perl 脚本，解析 WARNING/ERROR 行）
  - [ ] `sparse` 集成（如可用，解析 stderr 中的 warning/error）
  - [ ] `smatch` 集成（如可用）
  > **AC**: 提供测试 patch 文件，函数返回非空 findings 列表，每个 finding 含 severity/category/description
- [ ] **P2.14.2** 定义 LLM 多视角审核 Agent
  - [ ] 定义 `security_reviewer` Agent（Codex，安全维度）
  - [ ] 定义 `correctness_reviewer` Agent（Codex，正确性维度）
  - [ ] 定义 `style_reviewer` Agent（Codex，风格维度）
  - [ ] 定义 `reviewer` Manager Agent（汇总子 Agent 结果）
  > **AC**: 4 个 Agent 定义完整，含 name/instructions/model 字段
- [ ] **P2.14.3** 实现 LLM 审核调用与结果解析
  - [ ] 调用 `OpenAIAgentAdapter.execute()`
  - [ ] 解析输出为 `ReviewVerdict`
  > **AC**: Mock 测试下返回的 ReviewVerdict.approved 为布尔值，findings 为数组
- [ ] **P2.14.4** 实现结果合并与最终 Verdict 生成
  - [ ] 合并 deterministic findings + LLM findings
  - [ ] 规则：如果 deterministic 发现 critical/major，则 approved 强制为 False
  - [ ] 生成 reviewer_model 字段（标注使用了哪些模型/工具）
  > **AC**: 输入含 checkpatch ERROR 时，即使 LLM 认为通过，最终 approved=False
- [ ] **P2.14.5** 实现产物保存与状态返回
  - [ ] 保存 verdict 到 ArtifactManager
  - [ ] 返回 `{"review_verdict": ..., "review_iterations": +1, "review_history": +[...]}`
  > **AC**: 返回的状态中 review_iterations 比输入大 1
- [ ] **P2.14.6** 编写 `test_review_node.py`
  > **AC**: 覆盖：无 finding 通过、有 major finding 拒绝、deterministic + LLM 合并、3 轮迭代边界

---

### P2.15 test_node

- [ ] **P2.15.1** 创建 `ScienceClaw/backend/pipeline/nodes/test.py`
  - [ ] `test_node(state)` 异步函数
  - [ ] 构建测试提示（含 ExecutionPlan.test_plan + DevelopmentResult）
  - [ ] 调用 `ClaudeAgentAdapter.execute()`（含 QEMU 相关 Bash 命令）
  - [ ] 收集测试结果（通过/失败、日志路径、覆盖率）
  - [ ] 保存产物
  - [ ] 返回 `{"test_result": ..., "current_stage": "human_gate_test"}`
  > **AC**: Mock 测试下返回的 test_result.passed 为布尔值，含 total_tests 和 passed_tests 字段
- [ ] **P2.15.2** 编写 `test_test_node.py`
  > **AC**: Mock 测试通过

---

### P2.16 route_review_decision

- [ ] **P2.16.1** 修改 `ScienceClaw/backend/pipeline/routes.py`
  - [ ] `route_review_decision(state)` 函数
  - [ ] `compute_review_score(findings)` 加权评分（critical=10, major=5, minor=1）
  - [ ] 如果 `approved=True` → `"approve"`
  - [ ] 如果 `review_iterations >= max_review_iterations` → `"escalate"`
  - [ ] 收敛检测：连续 2 轮评分不下降 → `"escalate"`
  - [ ] 重叠检测：≥50% 问题重复出现 → `"escalate"`
  - [ ] 否则 → `"reject"`
  > **AC**: 6 种场景单元测试全部通过（approve、max_iter、converge、overlap、normal_reject、escalate）
- [ ] **P2.16.2** 编写 `test_route_review.py`
  > **AC**: 6 种场景覆盖

---

### P2.17 escalate_node

- [ ] **P2.17.1** 创建 `ScienceClaw/backend/pipeline/nodes/escalate.py`
  - [ ] `escalate_node(state)` 异步函数
  - [ ] 标记 case 状态为 `"escalated"`
  - [ ] 生成升级报告
  - [ ] 发送到 `human_gate_code`
  > **AC**: 返回后 case MongoDB 文档 status="escalated"，升级报告写入 ArtifactManager

---

### P2.18 数据源实现

- [ ] **P2.18.1** 创建 `ScienceClaw/backend/datasources/patchwork.py`
  - [ ] `PatchworkClient` 类
  - [ ] `get_recent_patches(project, state, limit)`
  - [ ] `get_patch_events(project)`
  - [ ] `get_stale_patches(days)`
  > **AC**: Mock HTTP 测试通过，返回数据结构符合预期
- [ ] **P2.18.2** 创建 `ScienceClaw/backend/datasources/mailing_list.py`
  - [ ] `MailingListCrawler` 类
  - [ ] `crawl_lore_kernel_org(query)`
  - [ ] `crawl_groups_io(list_name)`
  > **AC**: Mock HTTP 测试通过
- [ ] **P2.18.3** 创建 `ScienceClaw/backend/datasources/isa_registry.py`
  - [ ] `RATIFIED_EXTENSIONS` 常量集合（≥50 个扩展名）
  - [ ] `validate_extension(name)` 函数
  > **AC**: `validate_extension("Zicfiss")` 返回 True，`validate_extension("Zzzzz")` 返回 False
- [ ] **P2.18.4** 编写各数据源单元测试
  > **AC**: 三个数据源测试文件均通过，不依赖外部网络

---

### P2.19 cases 路由（已拆分：3 个子任务）

- [ ] **P2.19.1** 创建 `ScienceClaw/backend/route/cases.py` 骨架 + CRUD 端点
  - [ ] `POST /cases` — 创建案例（插入 MongoDB）
  - [ ] `GET /cases` — 案例列表（分页 + 筛选，支持 status/target_repo 过滤）
  - [ ] `GET /cases/:id` — 案例详情
  - [ ] `DELETE /cases/:id` — 删除案例（admin only，使用 `require_role`）
  - [ ] `GET /cases/:id/artifacts` — 获取阶段产物列表（读取 ArtifactManager）
  - [ ] `GET /cases/:id/artifacts/:path` — 获取产物内容
  - [ ] `GET /cases/:id/history` — 审核历史（查询 human_reviews 集合）
  - [ ] `POST /cases/:id/stop` — 强制停止 Pipeline
  > **AC**: 所有 CRUD 端点通过 pytest + testcontainers 集成测试，返回正确 HTTP status code 和 JSON 结构
- [ ] **P2.19.2** 实现 `POST /cases/:id/start` — 启动 Pipeline
  - [ ] 参数校验（案例存在、状态为 created）
  - [ ] 调用 `graph.ainvoke(initial_state, config={"thread_id": case_id})`
  - [ ] 异步启动（不阻塞 HTTP 响应）
  > **AC**: 调用后 MongoDB 中案例状态变为 "exploring"，返回 200 含 case_id
- [ ] **P2.19.3** 实现 `GET /cases/:id/events` — SSE 事件流
  - [ ] 使用 `EventSourceResponse`（sse-starlette）
  - [ ] 重连恢复：读取 `Last-Event-ID` header，调用 `get_events_since()` 补发丢失事件
  - [ ] 实时订阅 Redis Pub/Sub
  - [ ] 心跳（每 30 秒发送 comment 事件）
  > **AC**: 使用 `curl -N` 或 EventSource 客户端测试：连接建立后收到事件；断开重连后收到 seq 连续的事件

---

### P2.20 reviews 路由

- [ ] **P2.20.1** 创建 `ScienceClaw/backend/route/reviews.py`
  - [ ] `POST /cases/:id/review` — 提交人工审核
    - [ ] 幂等性检查（review_id 去重）
    - [ ] 状态检查（确认处于 pending_* 状态）
    - [ ] 写入 `human_reviews` 集合
    - [ ] 调用 `graph.ainvoke(Command(resume=...))` 恢复 Pipeline
  > **AC**: 重复提交相同 review_id 返回 200 但不重复处理；非 pending 状态返回 409
- [ ] **P2.20.2** 编写 `test_reviews_route.py`
  > **AC**: 覆盖幂等性、状态冲突、正常恢复三种场景

---

### P2.21 artifacts 路由

- [ ] **P2.21.1** 创建 `ScienceClaw/backend/route/artifacts.py`
  - [ ] `GET /artifacts/download` — 下载产物（Blob 响应）
  - [ ] `GET /artifacts/content` — 读取产物内容（文本响应）
  > **AC**: 下载端点返回正确 Content-Type 和 Content-Length；文本端点返回 UTF-8 字符串
- [ ] **P2.21.2** 编写 `test_artifacts_route.py`
  > **AC**: 覆盖下载和内容读取两种场景

---

### P2.22 pipeline 路由

- [ ] **P2.22.1** 创建 `ScienceClaw/backend/route/pipeline.py`
  - [ ] `GET /pipeline/status` — 系统 Pipeline 状态（admin only）
  - [ ] `POST /pipeline/:case_id/stop` — 强制停止（迁移到 cases 路由下也保留此处）
  > **AC**: `/pipeline/status` 返回当前活跃 Pipeline 数量列表；user 角色访问返回 403
- [ ] **P2.22.2** 编写 `test_pipeline_route.py`
  > **AC**: 权限测试通过

---

### P2.23 FastAPI 主入口扩展

- [ ] **P2.23.1** 修改 `ScienceClaw/backend/main.py`
  - [ ] 导入 4 个新 router
  - [ ] `app.include_router(cases_router)`
  - [ ] `app.include_router(reviews_router)`
  - [ ] `app.include_router(artifacts_router)`
  - [ ] `app.include_router(pipeline_router)`
  - [ ] lifespan 中初始化 `app.state.graph`（调用 `compile_graph()`）
  - [ ] lifespan 中初始化 `app.state.artifact_manager`
  - [ ] lifespan 中初始化 `app.state.event_publisher`
  > **AC**: `/docs` 中能看到所有新增端点；`docker compose up` 后 backend 容器 healthy

---

### P2.24 数据契约实现

- [ ] **P2.24.1** 实现 `ScienceClaw/backend/contracts/exploration.py`
  - [ ] `ContributionType` Enum
  - [ ] `Evidence` Pydantic 模型
  - [ ] `ExplorationResult` Pydantic 模型
  > **AC**: `ExplorationResult(feasibility_score=1.5)` 抛出 ValidationError
- [ ] **P2.24.2** 实现 `ScienceClaw/backend/contracts/planning.py`
  - [ ] `DevStep` 模型
  - [ ] `TestCase` 模型
  - [ ] `ExecutionPlan` 模型
  > **AC**: `ExecutionPlan` 序列化/反序列化无丢失字段
- [ ] **P2.24.3** 实现 `ScienceClaw/backend/contracts/development.py`
  - [ ] `DevelopmentResult` 模型
  > **AC**: 模型验证通过
- [ ] **P2.24.4** 实现 `ScienceClaw/backend/contracts/review.py`
  - [ ] `ReviewFinding` 模型
  - [ ] `ReviewVerdict` 模型
  > **AC**: `ReviewVerdict` 序列化后 approved 为布尔值
- [ ] **P2.24.5** 实现 `ScienceClaw/backend/contracts/testing.py`
  - [ ] `TestResult` 模型
  > **AC**: 模型验证通过

---

### P2.25 资源调度器

- [ ] **P2.25.1** 创建 `ScienceClaw/backend/scheduler.py`
  - [ ] `ResourceScheduler` 类
  - [ ] `claude_semaphore = asyncio.Semaphore(3)`
  - [ ] `openai_semaphore = asyncio.Semaphore(5)`
  - [ ] `qemu_semaphore = asyncio.Semaphore(2)`
  - [ ] `acquire/release` 方法族
  > **AC**: 并发调用 `acquire_claude()` 第 4 次时阻塞，直到前 3 次释放

---

### P2.26 审计日志

- [ ] **P2.26.1** 创建 `ScienceClaw/backend/db/audit.py`
  - [ ] `record_audit_event(db, case_id, event_type, data, user?)` 函数
  - [ ] `AUDIT_EVENTS` 常量字典
  > **AC**: 调用后 MongoDB `audit_log` 集合新增文档，含 timestamp 和 case_id

---

### P2.27 数据种子/Fixture

- [ ] **P2.27.1** 创建 `tests/fixtures/cases.py`
  - [ ] `mock_case()` 工厂函数
  - [ ] `mock_exploration_result()` 工厂函数
  - [ ] `mock_execution_plan()` 工厂函数
  - [ ] `mock_review_verdict()` 工厂函数
  > **AC**: 每个工厂函数返回符合 Pydantic 模型的有效数据，可直接用于测试
- [ ] **P2.27.2** 创建 `tests/fixtures/patches/sample.patch`
  > **AC**: patch 文件能被 `checkpatch.pl` 解析（如果有 kernel 源码环境）
- [ ] **P2.27.3** 配置 pytest fixture 自动加载
  > **AC**: 任意 pytest 测试文件中 `from tests.fixtures import mock_case` 可用

---

### Phase 2 里程碑检查点

- [ ] **M2.1** 可通过 API 创建案例（POST /cases 返回 201）
- [ ] **M2.2** 可启动 Pipeline（POST /cases/:id/start 后状态变为 exploring）
- [ ] **M2.3** SSE 事件流推送正常（客户端收到 stage_change 事件）
- [ ] **M2.4** 人工审核门可暂停 Pipeline（状态卡在 pending_explore_review）
- [ ] **M2.5** 提交审核后 Pipeline 恢复执行（状态变为 planning）
- [ ] **M2.6** Develop↔Review 迭代循环正常（mock 测试验证 3 轮迭代路径）
- [ ] **M2.7** 成本熔断器触发（mock 高成本状态返回 cost exceeded）
- [ ] **M2.8** 单元测试覆盖率 ≥ 70%（pytest --cov 报告）
- [ ] **M2.9** 数据种子就绪，所有集成测试可用 Fixture

---

## Phase 3: Pipeline 前端与集成（Week 9-12）

**目标**: 实现 Pipeline 前端全部组件，与后端联调
**DoD**: 可从前端创建案例并启动 Pipeline | Pipeline 可视化实时更新阶段状态 | 人工审核面板在 pending 状态时正确显示 | DiffViewer 正确渲染补丁和 findings 高亮 | AgentEventLog 实时显示 Agent 执行过程 | E2E 测试覆盖完整案例生命周期 | 前端组件文档（Storybook）就绪

### Phase 3 任务依赖关系

```mermaid
flowchart TD
    P31[P3.1 CaseList] --> P32[P3.2 CaseDetail]
    P34[P3.4 StageNode] --> P33[P3.3 PipelineView]
    P35[P3.5 useCaseEvents] --> P36[P3.6 HumanGate]
    P35 --> P315[P3.15 AgentEventLog]
    P36 --> P37[P3.7 ReviewPanel]
    P37 --> P38[P3.8 ReviewFinding]
    P38 --> P39[P3.9 DiffViewer]
    P32 --> P311[P3.11 ContributionCard]
    P32 --> P313[P3.13 ExecutionPlan]
    P316[P3.16 cases.ts] --> P321[P3.21 联调]
    P319[P3.19 useCaseStore] --> P321
    P315 --> P321
    P322[P3.22 E2E] --> P321
    P323[P3.23 Storybook] --> P33
```

---

### P3.1 CaseListView

- [ ] **P3.1.1** 创建 `ScienceClaw/frontend/src/views/CaseListView.vue`
  - [ ] 页面标题 + 新建案例按钮
  - [ ] 案例列表表格（标题、状态、目标仓库、创建时间、操作）
  - [ ] 状态筛选下拉框
  - [ ] 目标仓库筛选
  - [ ] 搜索框（按标题搜索）
  - [ ] 分页组件
  - [ ] 空状态展示
  > **AC**: 页面渲染无 console error，列表数据与 Mock/API 一致，分页切换正常
- [ ] **P3.1.2** 新建案例弹窗/抽屉
  - [ ] 标题输入
  - [ ] 目标仓库选择（linux/qemu/opensbi/gcc/llvm）
  - [ ] 输入上下文文本域
  - [ ] 贡献类型选择（可选）
  - [ ] 提交按钮调用 `createCase()`
  > **AC**: 表单校验：标题必填、目标仓库必选；提交成功后弹窗关闭并刷新列表

---

### P3.2 CaseDetailView（已拆分：3 个子任务）

- [ ] **P3.2.1** 创建 `ScienceClaw/frontend/src/views/CaseDetailView.vue` 布局骨架
  - [ ] 三栏布局容器（左 200px | 中 auto | 右 320px）
  - [ ] 顶部栏：案例标题、状态徽章、成本统计、操作按钮
  - [ ] 响应式断点：Desktop/Tablet/Mobile 三种布局切换
  > **AC**: 三种屏幕宽度下布局无错位，无横向滚动条（除非内容溢出）
- [ ] **P3.2.2** 实现左侧 Pipeline 阶段导航 + 右侧审核面板
  - [ ] 左侧：Pipeline 阶段列表（点击切换中间内容区）
  - [ ] 右侧：HumanGate 面板（pending 状态显示，否则折叠为历史记录）
  - [ ] 右侧：成本明细（按阶段分列）
  > **AC**: 点击左侧阶段项，中间内容区切换；pending 状态时右侧显示审核按钮
- [ ] **P3.2.3** 实现中间内容区 + 底部 AgentEventLog
  - [ ] 中间：动态组件渲染（根据当前阶段显示 ContributionCard / ExecutionPlanTree / DiffViewer / ...）
  - [ ] 底部：AgentEventLog 可折叠面板，支持拖拽调整高度
  > **AC**: 切换阶段后中间渲染对应组件；AgentEventLog 能实时追加事件并自动滚动

---

### P3.3 PipelineView

- [ ] **P3.3.1** 创建 `ScienceClaw/frontend/src/components/pipeline/PipelineView.vue`
  - [ ] 5 阶段横向流程图（探索 → 规划 → 开发 ↔ 审核 → 测试）
  - [ ] 人工门禁节点渲染
  - [ ] 各阶段状态图标（✅/🔄/⏳/❌）
  - [ ] 阶段间连接线（含状态颜色）
  - [ ] 当前活跃阶段高亮动画
  > **AC**: 5 个阶段全部渲染，状态变化时图标正确切换，当前阶段有 pulse 动画
- [ ] **P3.3.2** 响应式适配
  - [ ] Desktop XL (≥1440px)：完整横向流程
  - [ ] Desktop (1024-1439px)：紧凑横向流程
  - [ ] Tablet (<1024px)：纵向列表
  > **AC**: 三种断点下布局正确，无元素重叠

---

### P3.4 StageNode

- [ ] **P3.4.1** 创建 `ScienceClaw/frontend/src/components/pipeline/StageNode.vue`
  - [ ] 状态图标（根据 `stage.status`）
  - [ ] 阶段名称（i18n）
  - [ ] 耗时显示
  - [ ] Token 消耗显示
  - [ ] 点击事件（切换主内容区）
  > **AC**: 传入不同 status 时渲染不同颜色和图标，点击触发 emit 事件

---

### P3.5 useCaseEvents

- [ ] **P3.5.1** 创建 `ScienceClaw/frontend/src/composables/useCaseEvents.ts`
  - [ ] `events: Ref<AgentEvent[]>`
  - [ ] `isConnected: Ref<boolean>`
  - [ ] `lastEventId: Ref<string | null>`
  - [ ] `connect(caseId)` 使用 `fetchEventSource`
  - [ ] `disconnect()` 使用 `AbortController`
  - [ ] 心跳检测（45s 超时自动重连）
  - [ ] 断线重连恢复（携带 `Last-Event-ID`）
  - [ ] 事件去重（基于 `seq`）
  - [ ] 事件分发（stage_change → updateStage, review_request → setPendingReview, cost_update → updateCost）
  > **AC**: Mock SSE 测试：连接建立后收到 3 个事件；断开 5s 后重连收到 seq 连续的事件；重复 seq 被过滤

---

### P3.6 HumanGate

- [ ] **P3.6.1** 创建 `ScienceClaw/frontend/src/components/pipeline/HumanGate.vue`
  - [ ] 仅在 `pending_*_review` 状态时显示
  - [ ] 阶段产物摘要预览
  - [ ] 操作按钮组：通过 / 驳回 / 放弃
  - [ ] 审核意见文本域
  - [ ] 驳回目标选择（可选，驳回到指定阶段）
  - [ ] 提交按钮调用 `submitReview()`
  - [ ] 键盘快捷键（A=Approve, R=Reject, Esc=Cancel）
  > **AC**: 非 pending 状态时不渲染；点击 Approve 后 emit 事件并显示 loading；键盘快捷键绑定正确

---

### P3.7 ReviewPanel

- [ ] **P3.7.1** 创建 `ScienceClaw/frontend/src/components/review/ReviewPanel.vue`
  - [ ] 审核决策按钮组
  - [ ] 审核意见输入区
  - [ ] 驳回目标选择器（下拉）
  - [ ] 提交状态反馈
  > **AC**: 表单数据能正确 v-model 绑定，提交后回调父组件

---

### P3.8 ReviewFinding

- [ ] **P3.8.1** 创建 `ScienceClaw/frontend/src/components/review/ReviewFinding.vue`
  - [ ] Severity 图标（critical=🔴, major=🟠, minor=🟡, suggestion=🔵）
  - [ ] Category 标签
  - [ ] 文件路径 + 行号
  - [ ] 问题描述
  - [ ] 修复建议（可折叠）
  > **AC**: 传入不同 severity 渲染不同颜色，修复建议默认折叠，点击展开

---

### P3.9 DiffViewer

- [ ] **P3.9.1** 创建 `ScienceClaw/frontend/src/components/review/DiffViewer.vue`
  - [ ] 基于 Monaco Editor DiffEditor
  - [ ] Unified Diff 渲染
  - [ ] ReviewFinding 行内高亮（安全问题红色、风格问题黄色、建议蓝色）
  - [ ] 文件树导航（多文件补丁）
  > **AC**: 传入 patch 文本后 Monaco DiffEditor 正确渲染；传入 findings 后对应行高亮

---

### P3.10 ReviewHistory

- [ ] **P3.10.1** 创建 `ScienceClaw/frontend/src/components/review/ReviewHistory.vue`
  - [ ] 折叠列表展示历史审核记录
  - [ ] 每条记录：阶段、决策、评论、审核人、时间
  > **AC**: 传入历史记录数组后正确渲染，空数组显示空状态

---

### P3.11 ContributionCard

- [ ] **P3.11.1** 创建 `ScienceClaw/frontend/src/components/exploration/ContributionCard.vue`
  - [ ] 贡献标题
  - [ ] 类型标签
  - [ ] 可行性评分（进度条）
  - [ ] 目标文件列表
  - [ ] 摘要文本
  > **AC**: 传入 ExplorationResult 后正确渲染，进度条百分比与 score 一致

---

### P3.12 EvidenceChain

- [ ] **P3.12.1** 创建 `ScienceClaw/frontend/src/components/exploration/EvidenceChain.vue`
  - [ ] 证据列表（来源图标 + URL + 摘要 + 相关性评分）
  > **AC**: 传入 Evidence 数组后列表渲染正确，URL 可点击跳转

---

### P3.13 ExecutionPlanTree

- [ ] **P3.13.1** 创建 `ScienceClaw/frontend/src/components/planning/ExecutionPlanTree.vue`
  - [ ] 开发步骤树形展示
  - [ ] 测试用例列表
  - [ ] 风险等级标签
  > **AC**: 传入 ExecutionPlan 后树形结构渲染正确，风险等级不同颜色

---

### P3.14 TestResultSummary

- [ ] **P3.14.1** 创建 `ScienceClaw/frontend/src/components/testing/TestResultSummary.vue`
  - [ ] 通过/失败状态
  - [ ] 测试总数 / 通过数 / 失败数
  - [ ] 覆盖率百分比
  - [ ] QEMU 版本信息
  > **AC**: 传入 TestResult 后数据正确显示，通过/失败不同颜色

---

### P3.15 AgentEventLog

- [ ] **P3.15.1** 创建 `ScienceClaw/frontend/src/components/shared/AgentEventLog.vue`
  - [ ] 实时事件列表（thinking / tool_call / tool_result / output / error）
  - [ ] ThinkingBlock 可折叠
  - [ ] ToolCallView 参数/结果展示
  - [ ] 搜索过滤
  - [ ] 自动滚动到底部
  > **AC**: 事件列表自动追加新项，搜索框过滤后只显示匹配项，点击 ThinkingBlock 展开/折叠

---

### P3.16 cases.ts API 客户端

- [ ] **P3.16.1** 实现 `ScienceClaw/frontend/src/api/cases.ts`
  - [ ] 所有函数实际调用 `client.ts` axios 实例
  - [ ] `createCase` POST 实现
  - [ ] `listCases` GET 实现（含 query params）
  - [ ] `getCase` GET 实现
  - [ ] `deleteCase` DELETE 实现
  - [ ] `startPipeline` POST 实现
  - [ ] `submitReview` POST 实现
  - [ ] `getArtifacts` GET 实现
  - [ ] `getHistory` GET 实现
  - [ ] `subscribeCaseEvents` SSE 封装实现
  > **AC**: 每个函数在 Mock Server 环境下返回预期数据结构；错误处理统一（401 跳转登录，403 toast 提示）

---

### P3.17 reviews.ts API 客户端

- [ ] **P3.17.1** 实现 `ScienceClaw/frontend/src/api/reviews.ts`
  - [ ] `getReviewVerdict` GET 实现
  > **AC**: 返回数据结构符合 ReviewVerdict 类型

---

### P3.18 artifacts.ts API 客户端

- [ ] **P3.18.1** 实现 `ScienceClaw/frontend/src/api/artifacts.ts`
  - [ ] `downloadArtifact` GET Blob 实现
  - [ ] `getArtifactContent` GET text 实现
  > **AC**: `downloadArtifact` 触发浏览器下载；`getArtifactContent` 返回字符串

---

### P3.19 useCaseStore

- [ ] **P3.19.1** 创建 `ScienceClaw/frontend/src/composables/useCaseStore.ts`
  - [ ] `cases: Ref<Case[]>`（模块级单例）
  - [ ] `currentCase: Ref<Case | null>`
  - [ ] `pipelineStages: Ref<PipelineStage[]>`
  - [ ] `reviewIterations: Ref<number>`
  - [ ] `pendingReview: ComputedRef<boolean>`
  - [ ] `loadCases()` 方法
  - [ ] `loadCase(id)` 方法
  - [ ] `createCase(data)` 方法
  - [ ] `submitReview(decision)` 方法
  - [ ] `startPipeline(caseId)` 方法
  - [ ] `updateStage(eventData)` 方法
  - [ ] `updateCost(eventData)` 方法
  - [ ] `setPendingReview(eventData)` 方法
  > **AC**: 两个组件同时调用 `useCaseStore()` 时共享同一状态（ref 单例验证）

---

### P3.20 usePipelineStore / useReviewStore

- [ ] **P3.20.1** 创建 `ScienceClaw/frontend/src/composables/usePipelineStore.ts`
  > **AC**: 模块级单例状态，暴露 pipeline 运行状态
- [ ] **P3.20.2** 创建 `ScienceClaw/frontend/src/composables/useReviewStore.ts`
  > **AC**: 模块级单例状态，暴露审核相关状态

---

### P3.21 前后端联调（已拆分：5 个子任务）

- [ ] **P3.21.1** 联调：案例创建与列表展示
  - [ ] 前端创建案例 → 后端写入 MongoDB → 前端列表自动刷新
  > **AC**: 创建案例后列表出现新项，状态为 "created"，无页面刷新
- [ ] **P3.21.2** 联调：Pipeline 启动与 SSE 实时推送
  - [ ] 前端启动 Pipeline → 后端触发 LangGraph → SSE 推送 stage_change 事件
  > **AC**: 点击启动后 3 秒内 PipelineView 中 explore 阶段变为 active（收到 SSE 事件）
- [ ] **P3.21.3** 联调：人工审核提交与 Pipeline 恢复
  - [ ] 等待 pending 状态 → 右侧 HumanGate 显示 → 提交 Approve → Pipeline 进入下一阶段
  > **AC**: 提交审核后 3 秒内阶段状态从 pending 变为下一阶段 active
- [ ] **P3.21.4** 联调：产物文件预览与下载
  - [ ] 产物文件生成 → 前端预览（文本/Diff）→ 下载按钮触发 Blob 下载
  > **AC**: 产物文件内容正确渲染，下载后文件大小与后端一致
- [ ] **P3.21.5** 联调调试：修复端到端流程中发现的问题
  > **AC**: 记录所有 bug 到 `tests/e2e/bugs-fixed.md`，每个 bug 含复现步骤和修复方案

---

### P3.22 E2E 测试

- [ ] **P3.22.1** 创建 `tests/e2e/test_case_lifecycle.spec.ts`
  - [ ] 登录 → 创建案例 → 启动 Pipeline → 等待探索完成 → 审核通过 → 验证进入 planning
  > **AC**: Playwright 测试通过，无 flaky（连续运行 3 次均通过）
- [ ] **P3.22.2** 创建 `tests/e2e/test_case_review.spec.ts`
  - [ ] 审核驳回 → 验证回到当前阶段
  - [ ] 审核放弃 → 验证标记 abandoned
  > **AC**: 两种审核决策路径测试通过
- [ ] **P3.22.3** 创建 `tests/e2e/test_sse_reconnect.spec.ts`
  - [ ] 断网 → 恢复 → 验证事件无丢失
  > **AC**: 模拟网络断开后重连，seq 连续无跳跃

---

### P3.23 Storybook 组件文档

- [ ] **P3.23.1** 配置 Storybook 环境
  - [ ] 安装 `@storybook/vue3-vite`
  - [ ] 配置 `main.ts` 和 `preview.ts`
  > **AC**: `pnpm storybook` 能启动，显示组件列表
- [ ] **P3.23.2** 为核心 Pipeline 组件编写 Stories
  - [ ] `PipelineView.stories.ts`（含多种状态：未开始/进行中/已完成）
  - [ ] `StageNode.stories.ts`（含 4 种 status）
  - [ ] `HumanGate.stories.ts`（含 pending/非 pending 状态）
  - [ ] `ReviewFinding.stories.ts`（含 4 种 severity）
  > **AC**: 每个组件至少 2 个 Story，Controls 面板可交互修改 props
- [ ] **P3.23.3** 配置 Chromatic 或截图测试（可选）
  > **AC**: CI 中运行 Storybook 构建并通过（如有 Chromatic token）

---

### Phase 3 里程碑检查点

- [ ] **M3.1** 可从前端创建案例并启动 Pipeline（端到端手动验证通过）
- [ ] **M3.2** PipelineView 实时更新阶段状态（SSE 事件驱动）
- [ ] **M3.3** 人工审核面板在 pending 状态时正确显示，提交后 Pipeline 前进
- [ ] **M3.4** DiffViewer 正确渲染补丁和 findings 高亮
- [ ] **M3.5** AgentEventLog 实时显示 Agent 执行过程（thinking/tool_call/output）
- [ ] **M3.6** E2E 测试覆盖完整案例生命周期（test_case_lifecycle.spec.ts 通过）
- [ ] **M3.7** Storybook 中核心组件有文档，新成员可通过 Storybook 了解组件用法

---

## Phase 4: 集成测试与优化（Week 13-15）

**目标**: 系统联调、性能优化、混沌测试、安全加固
**DoD**: QEMU 沙箱可正确编译和运行 RISC-V 测试 | checkpatch.pl 和 sparse 在 Review 阶段自动运行 | API 速率限制生效 | 故障恢复测试通过 | 性能测试通过 | 安全扫描无高危漏洞 | 性能基准数据采集完成

### Phase 4 任务依赖关系

```mermaid
flowchart TD
    P41[P4.1 端到端联调] --> P42[P4.2 性能基准]
    P41 --> P43[P4.3 SSE压力]
    P41 --> P44[P4.4 内存泄漏]
    P45[P4.5 QEMU] --> P46[P4.6 确定性工具]
    P47[P4.7 PromptGuard] --> P411[P4.11 渗透测试]
    P48[P4.8 速率限制] --> P42
    P49[P4.9 故障注入] --> P41
    P410[P4.10 安全扫描] --> P411
    P412[P4.12 数据备份] --> P41
    P413[P4.13 性能基准] --> P42
```

---

### P4.1 端到端联调

- [ ] **P4.1.1** Chat + Pipeline 双模式切换测试
  - [ ] 从 Chat 页面跳转到 Cases 页面
  - [ ] 从 Cases 页面跳转到 Chat 页面
  - [ ] 同时打开 Chat SSE 和 Case SSE 不冲突
  > **AC**: 双 SSE 连接稳定，各自收到正确事件，无串流
- [ ] **P4.1.2** 完整案例生命周期手动验证
  - [ ] ISA 扩展支持场景（Zicfiss）
  - [ ] Bug 修复场景
  - [ ] 代码清理场景
  > **AC**: 三个场景各至少跑通 1 次完整 Pipeline（explore→plan→develop→review→test），产物可下载

---

### P4.2 性能基准测试

- [ ] **P4.2.1** API P99 响应时间测试
  - [ ] `locust -f tests/perf/load_api.py -u 50 -r 10 --run-time 5m`
  - [ ] 目标：P99 < 500ms
  > **AC**: Locust 报告中 P99 列 < 500ms，错误率 < 0.1%
- [ ] **P4.2.2** 并发案例创建测试
  - [ ] 50 并发 POST /cases
  - [ ] 验证无死锁、无重复 ID
  > **AC**: 50 个请求全部 201，MongoDB 中 case_id 唯一

---

### P4.3 SSE 压力测试

- [ ] **P4.3.1** 100 并发 SSE 连接测试
  - [ ] 使用 `tests/perf/test_sse_load.py`
  - [ ] 持续 10 分钟
  - [ ] 目标：无断连、事件延迟 < 1s
  > **AC**: 100 个连接 10 分钟内无异常断开，事件到达延迟 < 1s（通过 seq 和时间戳计算）

---

### P4.4 内存泄漏检测

- [ ] **P4.4.1** 长时间运行稳定性测试
  - [ ] `docker stats` 监控 24 小时
  - [ ] 目标：内存增长 < 100MB/天
  > **AC**: backend 容器内存曲线平稳，24h 增长 < 100MB
- [ ] **P4.4.2** MongoDB 连接池监控
  - [ ] 目标：连接数稳定，无泄漏
  > **AC**: `db.serverStatus().connections.current` 稳定在 < 20

---

### P4.5 QEMU Sandbox

- [ ] **P4.5.1** 创建 `sandbox-qemu/Dockerfile`
  - [ ] 基于 ubuntu:22.04
  - [ ] 安装 `gcc-riscv64-linux-gnu`
  - [ ] 安装 `qemu-system-riscv64`
  - [ ] 安装 `qemu-user-static`
  - [ ] 安装 `opensbi`
  - [ ] 配置交叉编译环境变量
  > **AC**: `docker build` 成功，`riscv64-linux-gnu-gcc --version` 在容器内输出版本号
- [ ] **P4.5.2** 构建并验证 QEMU 沙箱镜像
  > **AC**: 镜像能启动，`uname -m` 在 qemu-user 下输出 riscv64（如使用用户态模拟测试）
- [ ] **P4.5.3** 在 Test 节点集成 QEMU 沙箱调用
  > **AC**: Test 节点执行 Bash 命令时，QEMU 相关命令返回 0

---

### P4.6 确定性工具集成

- [ ] **P4.6.1** `checkpatch.pl` 集成验证
  - [ ] 在 Linux 内核源码目录执行
  - [ ] 验证 WARNING/ERROR 解析正确
  > **AC**: 提供测试 patch，函数返回 findings 列表，WARNING 和 ERROR 被正确分类
- [ ] **P4.6.2** `sparse` 集成验证（如可用）
  > **AC**: sparse 可用时返回 findings，不可用时 gracefully skip
- [ ] **P4.6.3** 在 Review 节点确认确定性工具输出合并到 Verdict
  > **AC**: Review 节点执行后，deterministic findings 出现在 review_verdict.findings 中

---

### P4.7 Prompt Guard

- [ ] **P4.7.1** 创建 `ScienceClaw/backend/security/prompt_guard.py`
  - [ ] `INJECTION_PATTERNS` 正则列表
  - [ ] `detect_prompt_injection(user_input)` 函数
  - [ ] `sanitize_user_input(user_input)` 函数
  > **AC**: 输入 "ignore previous instructions" 时 `detect_prompt_injection` 返回 True；sanitize 后输出被截断或清理
- [ ] **P4.7.2** 在 `cases.py` 创建案例前调用 `sanitize_user_input`
  > **AC**: 创建案例时输入恶意 prompt，后端返回 400 或已清理内容存入 DB

---

### P4.8 速率限制

- [ ] **P4.8.1** 创建 `ScienceClaw/backend/middleware/rate_limit.py`
  - [ ] `Limiter` 配置（Redis 存储）
  - [ ] 100 req/min/user
  > **AC**: 1 分钟内发送 101 次请求，第 101 次返回 429 Too Many Requests
- [ ] **P4.8.2** 在 `main.py` 中注册限流中间件
  > **AC**: 限流对 `/api/v1/*` 全部生效，/health 和 /ready 可豁免

---

### P4.9 故障注入测试

- [ ] **P4.9.1** 后端重启恢复测试
  - [ ] `docker restart backend`
  - [ ] 验证 Pipeline 从 checkpointer 恢复
  > **AC**: Pipeline 在中断前阶段恢复执行，状态不丢失
- [ ] **P4.9.2** MongoDB 中断测试
  - [ ] `docker stop mongodb`
  - [ ] 验证返回 503，不崩溃
  > **AC**: 停止 MongoDB 后 API 返回 503，backend 容器不重启/不崩溃
- [ ] **P4.9.3** Redis 中断测试
  - [ ] `docker stop redis`
  - [ ] 验证 SSE 降级为轮询（或优雅降级）
  > **AC**: SSE 连接断开但前端自动重连；或前端降级为短轮询（如已实现）
- [ ] **P4.9.4** 网络延迟测试
  - [ ] `tc qdisc add dev eth0 delay 500ms`
  - [ ] 验证超时重试正常
  > **AC**: API 请求延迟增加但无失败，Tenacity 重试日志可见

---

### P4.10 安全扫描

- [ ] **P4.10.1** Python 安全扫描
  - [ ] `bandit -r ScienceClaw/backend/`
  - [ ] `safety check`
  > **AC**: bandit 无 High 级别 issue，safety 无已知 CVE 漏洞
- [ ] **P4.10.2** Node.js 安全扫描
  - [ ] `npm audit`
  > **AC**: `npm audit` 无 High/Critical 漏洞（或可接受的有修复方案）
- [ ] **P4.10.3** 处理所有高危漏洞
  > **AC**: 所有 High/Critical 漏洞已修复或有接受的缓解措施文档

---

### P4.11 渗透测试

- [ ] **P4.11.1** OWASP Top 10 检查清单
  - [ ] SQL/NoSQL 注入测试
  - [ ] JWT 伪造测试
  - [ ] SSRF 测试
  - [ ] 路径遍历测试
  - [ ] 权限绕过测试
  > **AC**: 每项测试有具体测试用例和结果记录，无未修复的高危漏洞

---

### P4.12 数据备份恢复

- [ ] **P4.12.1** 创建 `scripts/backup.sh`
  - [ ] `mongodump` 每日备份
  - [ ] `pg_dump` 每日备份
  - [ ] 30 天滚动清理
  > **AC**: 脚本执行后 `/data/backups/YYYYMMDD/` 目录包含 mongo 和 postgres 备份
- [ ] **P4.12.2** 验证备份可恢复
  > **AC**: 使用备份恢复到新容器，数据完整性与原库一致（抽样验证）

---

### P4.13 性能基准数据采集

- [ ] **P4.13.1** 采集首次性能基准数据
  - [ ] API P99（各端点）
  - [ ] SSE 并发连接数与延迟
  - [ ] Pipeline 单阶段平均耗时
  - [ ] 前端首屏加载时间（Lighthouse）
  > **AC**: 数据记录到 `tests/baseline/perf-baseline-v1.json`，作为后续优化对比基线
- [ ] **P4.13.2** 配置 Prometheus + Grafana 监控
  - [ ] `/metrics` 端点暴露业务指标
  - [ ] Grafana dashboard 配置
  > **AC**: Grafana 能看到 Active Pipelines、Stage Duration、Cost USD 三个面板

---

### Phase 4 里程碑检查点

- [ ] **M4.1** QEMU 沙箱可正确编译和运行 RISC-V 测试（至少一个 hello world）
- [ ] **M4.2** checkpatch.pl 在 Review 阶段自动运行，输出被合并到 Verdict
- [ ] **M4.3** API 速率限制生效（100 req/min 触发 429）
- [ ] **M4.4** 故障恢复测试通过（backend 重启后 Pipeline 可恢复）
- [ ] **M4.5** 性能测试通过（API P99 < 500ms，100 SSE 连接稳定）
- [ ] **M4.6** 安全扫描无高危漏洞（bandit + npm audit High=0）
- [ ] **M4.7** 性能基准数据已采集，Grafana 监控面板可用

---

## Phase 5: 生产准备（Week 16）

**目标**: 文档完善、部署验证、培训
**DoD**: 生产环境部署成功 | 所有文档完备 | 团队培训完成 | 上线检查清单全部通过

### Phase 5 任务依赖关系

```mermaid
flowchart TD
    P51[P5.1 部署文档] --> P55[P5.5 生产部署]
    P52[P5.2 API文档] --> P55
    P53[P5.3 运维手册] --> P56[P5.6 培训]
    P54[P5.4 用户手册] --> P56
    P55 --> P56
```

---

### P5.1 部署文档

- [ ] **P5.1.1** 创建 `docs/deployment-guide.md`
  - [ ] 环境要求（CPU/内存/磁盘）
  - [ ] 依赖安装步骤
  - [ ] Docker Compose 启动步骤
  - [ ] 环境变量配置说明
  - [ ] Nginx 配置示例
  - [ ] SSL/TLS 配置（Let's Encrypt）
  - [ ] 常见问题排查
  > **AC**: 新成员按照文档能在 30 分钟内完成本地部署

---

### P5.2 API 文档

- [ ] **P5.2.1** 配置 FastAPI 自动生成 OpenAPI
  - [ ] 所有端点添加 `summary` 和 `description`
  - [ ] 所有模型添加 `Field(description=...)`
  > **AC**: `/docs` 页面中所有 Pipeline 端点有中文/英文描述，请求/响应 schema 可展开查看
- [ ] **P5.2.2** 验证 Swagger UI (`/docs`) 完整可用
  > **AC**: `/docs` 页面加载时间 < 3s，所有端点可 Try it out

---

### P5.3 运维手册

- [ ] **P5.3.1** 创建 `docs/operations.md`
  - [ ] 监控指标说明
  - [ ] 告警规则解释
  - [ ] 故障处理流程（后端重启、数据库恢复、Pipeline 卡住）
  - [ ] 日志查看命令
  - [ ] 备份恢复步骤
  > **AC**: 运维人员按照手册能在 15 分钟内定位并处理常见故障

---

### P5.4 用户手册

- [ ] **P5.4.1** 创建 `docs/user-guide.md`
  - [ ] 快速开始（创建第一个案例）
  - [ ] 界面截图 + 操作步骤
  - [ ] 审核操作指南
  - [ ] Chat 模式使用指南
  - [ ] 设置配置说明
  > **AC**: 新用户按照手册能在 10 分钟内完成第一个案例创建和 Pipeline 启动

---

### P5.5 生产环境部署

- [ ] **P5.5.1** 在目标服务器执行完整部署
  - [ ] `docker compose up -d` 成功
  - [ ] 所有服务 Healthy
  - [ ] `/health` 返回全绿
  - [ ] `/ready` 返回就绪
  > **AC**: `docker compose ps` 全部服务状态为 healthy，无 restarting
- [ ] **P5.5.2** 域名 + SSL 配置验证
  > **AC**: HTTPS 访问正常，SSL Labs 评分 ≥ B
- [ ] **P5.5.3** 飞书 webhook 通知验证
  > **AC**: Pipeline 完成时飞书群收到通知消息

---

### P5.6 团队培训

- [ ] **P5.6.1** 开发团队培训
  - [ ] 代码结构讲解
  - [ ] Pipeline 调试方法
  - [ ] Agent Prompt 修改指南
  > **AC**: 培训后开发团队能独立修改 Agent Prompt 并验证效果
- [ ] **P5.6.2** 运维团队培训
  - [ ] 部署流程
  - [ ] 监控告警响应
  - [ ] 故障恢复演练
  > **AC**: 培训后运维团队能在无协助情况下完成部署和故障恢复

---

### Phase 5 里程碑检查点

- [ ] **M5.1** 生产环境部署成功，域名 + SSL 可用
- [ ] **M5.2** 部署文档、运维手册、用户手册完备并通过评审
- [ ] **M5.3** 开发团队和运维团队培训完成，有培训记录
- [ ] **M5.4** 上线检查清单全部通过（ checklist 见 `docs/go-live-checklist.md`）

---

## 附录 A：每日站会状态标记规范

**每日更新时，请在对应任务前标记状态**：
- `[ ]` = 未开始
- `[~]` = 进行中（添加开始日期）
- `[?]` = 阻塞中（添加阻塞原因）
- `[x]` = 已完成（添加完成日期）

**示例**：
```
- [x] **P0.2.1** 创建 pipeline/ 目录（2026-04-29 完成）
- [~] **P0.6.1** 修改 user/dependencies.py（2026-04-30 开始）
- [?] **P0.8.1** 更新 requirements.txt（阻塞：等待 claude-agent-sdk 发布）
```

---

## 附录 B：风险登记册

| 风险 ID | 风险描述 | 概率 | 影响 | 缓解措施 | 负责人 | 状态 |
|---------|----------|------|------|----------|--------|------|
| R01 | ScienceClaw 上游更新导致迁移冲突 | 高 | 高 | 版本锁定、抽象层隔离、回归测试 | TechLead | 未开始 |
| R02 | Claude Agent SDK Breaking Change | 高 | 高 | 适配器隔离、版本锁定、fallback 方案 | BackendDev | 未开始 |
| R03 | Pipeline 前端复杂度超预期 | 中 | 中 | MVP 简化、组件复用、增量交付 | FrontendDev | 未开始 |
| R04 | LangGraph 0.3→0.4 API 变更 | 中 | 高 | 版本锁定 `<0.4.0`、封装层隔离 | BackendDev | 未开始 |
| R05 | QEMU 沙箱环境搭建困难 | 中 | 高 | 提前验证工具链、预构建镜像 | DevOps | 未开始 |
| R06 | OpenAI Codex 模型不可用 | 中 | 高 | 降级链：codex-mini → gpt-4o → claude-sonnet | BackendDev | 未开始 |
| R07 | SSE 长连接在 Nginx 下异常 | 中 | 中 | Nginx SSE 专用配置、充分测试重连 | DevOps | 未开始 |
| R08 | RISC-V 领域知识不足导致 Prompt 效果差 | 中 | 高 | Prompt 工程单独迭代、评估数据集 | TechLead | 未开始 |

---

## 附录 C：变更日志

| 日期 | 版本 | 变更类型 | 任务 ID | 变更内容 | 变更人 |
|------|------|----------|---------|----------|--------|
| 2026-04-29 | v1.0 | 创建 | - | 初始版本 | Sisyphus |
| 2026-04-29 | v2.0 | 优化 | 全部 | 增加依赖图、AC、拆分粗任务、补充遗漏任务 | Sisyphus |

---

## 附录 D：周会模板

### Week N 计划（YYYY-MM-DD 至 YYYY-MM-DD）

- **本周目标**:
- **关键任务**（不超过 3 项）:
  1.
  2.
  3.
- **预期风险**:
- **需要协助**:

### Week N-1 总结

- **完成任务**:
- **未完成任务及原因**:
- **阻塞项**:
- **本周工时投入**:

---

## 附录 E：PR 检查清单

提交 PR 前，请确保以下检查项全部通过：

- [ ] 代码已通过 `ruff check`（Python）或 `eslint`（TS/Vue）
- [ ] 类型检查通过：`mypy --strict`（Python）或 `vue-tsc --noEmit`（TS）
- [ ] 新增/修改的代码有单元测试覆盖
- [ ] 所有测试通过：`pytest` + `pnpm test:unit`
- [ ] i18n 键已添加（如涉及 UI 文本）
- [ ] API 文档已更新（FastAPI summary/description）
- [ ] 变更已记录到 [附录 C：变更日志](#附录-c变更日志)
- [ ] 代码 Review 通过（至少 1 人 approve）

---

## 附录 F：脚本（自动统计进度）

```bash
#!/bin/bash
# scripts/progress.sh — 自动计算 progress.md 完成百分比

total=$(grep -cE '^\s*- \[\s*[x~?]\s*\] \*\*P[0-9]' tasks/kimi/progress.md)
done=$(grep -cE '^\s*- \[x\] \*\*P[0-9]' tasks/kimi/progress.md)
blocked=$(grep -cE '^\s*- \[\?\] \*\*P[0-9]' tasks/kimi/progress.md)
inprogress=$(grep -cE '^\s*- \[\~\] \*\*P[0-9]' tasks/kimi/progress.md)

pct=$(( done * 100 / total ))
echo "Total: $total | Done: $done | In Progress: $inprogress | Blocked: $blocked | Completion: $pct%"
```

使用方式：
```bash
bash scripts/progress.sh
# 输出示例：Total: 145 | Done: 23 | In Progress: 5 | Blocked: 1 | Completion: 15%
```

---

## 附录 G：环境变量完整清单

> **用途**: 开发/测试/生产环境统一配置参考，禁止在业务代码中直接使用 `os.getenv()`  
> **读取方式**: 统一通过 `backend/config.py::Settings` 访问  
> **优先级**: `.env` 文件 > 系统环境变量 > 默认值

### G.1 数据库与存储

| 变量名 | 必需 | 默认值 | 说明 | 示例 |
|--------|------|--------|------|------|
| `MONGODB_URI` | ✅ | — | MongoDB 连接字符串 | `mongodb://mongo:27017/scienceclaw` |
| `POSTGRES_URI` | ✅ | — | PostgreSQL 连接字符串（LangGraph checkpointer） | `postgresql+asyncpg://rv:pass@postgres:5432/rv_checkpoints` |
| `REDIS_URI` | ✅ | — | Redis 连接字符串 | `redis://redis:6379/0` |
| `MONGO_DB_NAME` | — | `scienceclaw` | MongoDB 数据库名 | `scienceclaw` |
| `PG_POOL_MIN` | — | `1` | PostgreSQL 连接池最小连接数 | `1` |
| `PG_POOL_MAX` | — | `10` | PostgreSQL 连接池最大连接数 | `10` |

### G.2 认证与安全

| 变量名 | 必需 | 默认值 | 说明 | 示例 |
|--------|------|--------|------|------|
| `JWT_SECRET_KEY` | ✅ | — | JWT 签名密钥（≥32字符） | `***` |
| `JWT_ALGORITHM` | — | `HS256` | JWT 算法 | `HS256` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | — | `30` | Access Token 过期时间（分钟） | `30` |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | — | `7` | Refresh Token 过期时间（天） | `7` |
| `ADMIN_DEFAULT_PASSWORD` | ✅ | `admin123` | 默认管理员密码（首次启动后必须修改） | `***` |
| `CORS_ORIGINS` | — | `http://localhost:5173` | 允许的 CORS 来源，逗号分隔 | `http://localhost:5173,https://rv-claw.io` |

### G.3 LLM API 密钥

| 变量名 | 必需 | 默认值 | 说明 | 示例 |
|--------|------|--------|------|------|
| `CLAUDE_API_KEY` | ✅ | — | Anthropic Claude API Key | `***` |
| `OPENAI_API_KEY` | ✅ | — | OpenAI API Key | `***` |
| `OPENAI_ORG_ID` | — | — | OpenAI Organization ID | `org-xxx` |
| `CODEX_API_KEY` | — | — | OpenAI Codex API Key（如与 OpenAI 不同） | `***` |

### G.4 模型配置

| 变量名 | 必需 | 默认值 | 说明 | 示例 |
|--------|------|--------|------|------|
| `CLAUDE_MODEL` | — | `claude-sonnet-4-20250514` | Claude 默认模型 | `claude-sonnet-4-20250514` |
| `OPENAI_MODEL` | — | `gpt-4o` | OpenAI 默认模型 | `gpt-4o` |
| `CODEX_MODEL` | — | `codex-mini` | Codex 默认模型 | `codex-mini` |
| `CLAUDE_FALLBACK_MODEL` | — | `claude-haiku-4` | Claude 降级模型 | `claude-haiku-4` |
| `OPENAI_FALLBACK_MODEL` | — | `gpt-4o-mini` | OpenAI 降级模型 | `gpt-4o-mini` |

### G.5 Pipeline 控制参数

| 变量名 | 必需 | 默认值 | 说明 | 示例 |
|--------|------|--------|------|------|
| `MAX_REVIEW_ITERATIONS` | — | `3` | 单案例最大审核轮次 | `3` |
| `MAX_AGENT_TURNS` | — | `50` | 单个 Agent 节点最大轮次 | `50` |
| `MAX_COST_PER_CASE_USD` | — | `10.0` | 单案例成本熔断阈值（美元） | `10.0` |
| `AGENT_TIMEOUT_SECONDS` | — | `300` | Agent 节点超时时间（秒） | `300` |
| `PIPELINE_ENABLED` | — | `False` | Feature Flag：是否启用 Pipeline 功能 | `False` |
| `QEMU_SANDBOX_ENABLED` | — | `False` | Feature Flag：是否启用 QEMU 沙箱 | `False` |

### G.6 资源限制

| 变量名 | 必需 | 默认值 | 说明 | 示例 |
|--------|------|--------|------|------|
| `MAX_CONCURRENT_CLAUDE` | — | `3` | 并发 Claude Agent 数量上限 | `3` |
| `MAX_CONCURRENT_OPENAI` | — | `5` | 并发 OpenAI Agent 数量上限 | `5` |
| `MAX_CONCURRENT_QEMU` | — | `2` | 并发 QEMU 实例数量上限 | `2` |
| `MAX_CONCURRENT_CASES` | — | `10` | 全局并发 Case 数量上限 | `10` |

### G.7 外部服务

| 变量名 | 必需 | 默认值 | 说明 | 示例 |
|--------|------|--------|------|------|
| `SANDBOX_BASE_URL` | — | `http://sandbox:8080` | AIO Sandbox 服务地址 | `http://sandbox:8080` |
| `WEBSEARCH_BASE_URL` | — | `http://websearch:8000` | WebSearch 服务地址 | `http://websearch:8000` |
| `SEARXNG_URL` | — | `http://searxng:8080` | SearXNG 地址 | `http://searxng:8080` |
| `TASK_SERVICE_URL` | — | `http://task-service:8000` | Task Service 地址 | `http://task-service:8000` |
| `GITHUB_TOKEN` | — | — | GitHub API Token（用于 Patchwork） | `ghp_***` |

### G.8 日志与监控

| 变量名 | 必需 | 默认值 | 说明 | 示例 |
|--------|------|--------|------|------|
| `LOG_LEVEL` | — | `INFO` | 日志级别（DEBUG/INFO/WARNING/ERROR） | `INFO` |
| `LOG_FORMAT` | — | `json` | 日志格式（json/text） | `json` |
| `PROMETHEUS_PORT` | — | `9090` | Prometheus 暴露端口 | `9090` |
| `GRAFANA_PORT` | — | `3000` | Grafana 暴露端口 | `3000` |
| `SENTRY_DSN` | — | — | Sentry 错误追踪 DSN（生产环境） | `https://...@sentry.io/...` |

### G.9 开发专用

| 变量名 | 必需 | 默认值 | 说明 | 示例 |
|--------|------|--------|------|------|
| `ENV` | — | `development` | 运行环境（development/staging/production） | `development` |
| `DEBUG` | — | `True` | 调试模式（开发环境） | `True` |
| `RELOAD` | — | `True` | FastAPI 热重载（开发环境） | `True` |
| `MOCK_LLM` | — | `False` | 是否 Mock LLM 调用（单元测试用） | `False` |

### G.10 环境变量校验规则

```python
# config.py 中的校验逻辑（伪代码）
class Settings(BaseSettings):
    # 密钥长度校验
    @field_validator("JWT_SECRET_KEY")
    def validate_jwt_secret(cls, v):
        if len(v) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters")
        return v

    # 成本阈值校验
    @field_validator("MAX_COST_PER_CASE_USD")
    def validate_cost(cls, v):
        if v <= 0:
            raise ValueError("MAX_COST_PER_CASE_USD must be positive")
        return v

    # Feature Flag 类型校验
    @field_validator("PIPELINE_ENABLED", "QEMU_SANDBOX_ENABLED")
    def validate_bool(cls, v):
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes")
        return bool(v)
```

---

## 附录 H：接口契约速查

> **用途**: 快速查阅所有 API 的输入输出、SSE 事件格式、WebSocket 契约  
> **详细定义**: 见 `tasks/kimi/refactor-plan-v3.md` §5.13 及 `tasks/codex/state-machine-rules.md`

### H.1 REST API 概览

#### 认证域 (`/api/v1/auth`)

| 方法 | 路径 | 请求体 | 响应 | 说明 |
|------|------|--------|------|------|
| POST | `/login` | `{username, password}` | `{access_token, refresh_token, token_type, role}` | 登录 |
| POST | `/register` | `{username, password, full_name}` | `{id, username, role}` | 注册 |
| GET | `/status` | — | `{is_authenticated: bool}` | 检查登录态 |
| GET | `/me` | — | `{id, username, full_name, role}` | 当前用户 |
| POST | `/refresh` | `{refresh_token}` | `{access_token, refresh_token}` | 刷新 Token |
| POST | `/change-password` | `{old_password, new_password}` | `{status: "ok"}` | 修改密码 |
| POST | `/change-fullname` | `{full_name}` | `{status: "ok"}` | 修改姓名 |
| POST | `/logout` | — | `{status: "ok"}` | 登出 |
| GET | `/check-default-password` | — | `{is_default: bool}` | 检查默认密码 |

#### Chat 会话域 (`/api/v1/sessions`)

| 方法 | 路径 | 请求体 | 响应 | 说明 |
|------|------|--------|------|------|
| PUT | `/` | `{title?, mode?}` | Session | 创建会话 |
| GET | `/` | `?page&page_size` | `{items, total, ...}` | 列表 |
| GET | `/{id}` | — | Session | 详情 |
| DELETE | `/{id}` | — | `204` | 删除 |
| PATCH | `/{id}/pin` | `{pinned: bool}` | Session | 置顶 |
| PATCH | `/{id}/title` | `{title}` | Session | 重命名 |
| POST | `/{id}/chat` | `{message, attachments?}` | SSE Stream | 聊天 |
| POST | `/{id}/stop` | — | `{status: "ok"}` | 停止 |
| POST | `/{id}/share` | — | `{share_url}` | 分享 |
| DELETE | `/{id}/share` | — | `204` | 取消分享 |
| GET | `/shared/{id}` | — | Session（只读） | 获取分享 |
| GET | `/{id}/files` | — | `{files: []}` | 文件列表 |
| GET | `/{id}/sandbox-file` | `?path` | File Stream | 读取沙箱文件 |
| GET | `/{id}/sandbox-file/download` | `?path` | File Download | 下载沙箱文件 |

#### Pipeline Cases 域 (`/api/v1/cases`)

| 方法 | 路径 | 请求体 | 响应 | 说明 |
|------|------|--------|------|------|
| POST | `/` | `{title, target_repo, description?, input_context?}` | Case | 创建 |
| GET | `/` | `?page&page_size&status&target_repo&keyword` | `{items, total, ...}` | 列表 |
| GET | `/{id}` | — | Case | 详情 |
| DELETE | `/{id}` | — | `204` | 删除（admin 或 owner） |
| POST | `/{id}/start` | — | `{status: "started"}` | 启动 Pipeline |
| POST | `/{id}/stop` | — | `{status: "stopped"}` | 停止 |
| GET | `/{id}/events` | `?last_event_id` | SSE Stream | 事件流 |
| POST | `/{id}/review` | `{review_id, action, comment?, reject_to_stage?, modified_artifact_ref?}` | `{status, new_status}` | 提交审核 |
| GET | `/{id}/artifacts/{stage}` | — | `{artifacts: []}` | 获取产物 |
| GET | `/{id}/history` | — | `{events: []}` | 历史记录 |

#### 其他保留域

| 域 | 路径前缀 | 说明 |
|----|----------|------|
| Files | `/api/v1/files/*` | 文件上传/下载/预览 |
| Models | `/api/v1/models/*` | 模型配置 |
| Memory | `/api/v1/memory` | 用户记忆 |
| Statistics | `/api/v1/statistics/*` | 统计（支持 `?mode=chat\|pipeline`） |
| Task Settings | `/api/v1/task-settings` | 定时任务设置 |
| IM | `/api/v1/im/*` | IM 集成（Lark/WeChat） |
| ToolUniverse | `/api/v1/tooluniverse/*` | 工具浏览/执行 |
| Science | `/api/v1/science/optimize_prompt` | Prompt 优化 |
| Scheduler | `/api/v1/chat`, `/api/v1/task/parse-schedule` | Task Service 兼容 |

### H.2 SSE 事件契约

#### Chat SSE 事件（保留 ScienceClaw 全部事件名）

```json
// 通用字段（每个事件都有）
{
  "event_id": "uuid",
  "timestamp": "2026-04-29T13:00:00Z",
  "session_id": "sess_xxx",
  "event_type": "message"  // 见下表
}
```

| 事件名 | 触发时机 | 特有字段 | 说明 |
|--------|----------|----------|------|
| `thinking` | Agent 开始思考 | `{content}` | 思考过程 |
| `plan` | Agent 生成计划 | `{plan_steps: []}` | 执行计划 |
| `step` | 计划步骤完成 | `{step_index, total_steps, content}` | 步骤进度 |
| `tool` | 工具调用 | `{tool_name, tool_input, tool_output?}` | 工具执行 |
| `message` | 生成回复 | `{content, attachments?}` | 最终消息 |
| `done` | 会话完成 | `{statistics, round_files?}` | 完成事件 |
| `error` | 发生错误 | `{error_code, message}` | 错误 |
| `title` | 自动生成标题 | `{title}` | 标题更新 |
| `wait` | 等待用户输入 | `{}` | 等待状态 |
| `attachments` | 文件附件 | `{files: []}` | 附件列表 |

#### Pipeline SSE 事件

```json
// 统一信封格式
{
  "seq": 12,
  "case_id": "case_xxx",
  "event_type": "stage_change",
  "timestamp": "2026-04-29T13:00:00Z",
  "data": {}
}
```

| 事件名 | 触发时机 | data 字段 | 说明 |
|--------|----------|-----------|------|
| `stage_change` | 阶段切换 | `{from, to, stage}` | 状态变更 |
| `agent_output` | Agent 产生输出 | `{stage, content, type}` | Agent 输出 |
| `review_request` | 需要人工审核 | `{stage, artifact_ref, summary}` | 审核请求 |
| `review_submitted` | 审核已提交 | `{action, reviewer, comment}` | 审核结果 |
| `iteration_update` | Review 迭代 | `{round_num, max_rounds, findings}` | 迭代信息 |
| `artifact_created` | 产物生成 | `{stage, artifact_path, artifact_type}` | 产物通知 |
| `cost_update` | 成本更新 | `{cost_usd, input_tokens, output_tokens}` | 成本累计 |
| `heartbeat` | 心跳 | `{}` | 每 30s |
| `pipeline_completed` | Pipeline 完成 | `{duration_seconds, total_cost}` | 完成 |
| `pipeline_failed` | Pipeline 失败 | `{stage, error, last_error}` | 失败 |

### H.3 审核动作契约

```json
// POST /api/v1/cases/{id}/review 请求体
{
  "review_id": "uuid-v4-or-snowflake",
  "action": "approve | reject | reject_to | abandon | modify",
  "comment": "string",
  "reject_to_stage": "explore | plan | develop | test",  // action=reject_to 时必填
  "modified_artifact_ref": "string"  // action=modify 时必填
}

// 约束
// - reject_to 必须指定 reject_to_stage
// - modify 必须指定 modified_artifact_ref
// - approve/reject/abandon 不允许带多余字段
```

### H.4 分页响应统一格式

```json
{
  "items": [],
  "total": 42,
  "page": 1,
  "page_size": 20,
  "total_pages": 3
}
```

### H.5 错误响应统一格式

```json
{
  "detail": "人类可读的错误描述",
  "error_code": "CASE_NOT_FOUND",
  "field": "target_repo",
  "suggestion": "Valid values: linux, qemu, opensbi, gcc, llvm"
}
```

---

## 附录 I：数据模型速查表

> **用途**: 快速查阅 MongoDB 集合结构和 PostgreSQL 表结构  
> **详细定义**: 见 `tasks/kimi/refactor-plan-v3.md` §6.7~6.9

### I.1 MongoDB 集合

#### `users`（保留 + 扩展）

```json
{
  "_id": "ObjectId",
  "username": "string",
  "password_hash": "string",
  "full_name": "string",
  "role": "admin | user",           // 新增
  "created_at": "ISODate",
  "updated_at": "ISODate"
}
```

#### `refresh_tokens`

```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId",
  "token_hash": "string",
  "expires_at": "ISODate",
  "created_at": "ISODate"
}
```

#### `sessions`（保留）

```json
{
  "_id": "string",
  "session_id": "string",
  "user_id": "string",
  "title": "string | null",
  "mode": "deep | chat | research",
  "status": "pending | running | waiting | completed | failed",
  "source": "web | task | im",
  "model_config_id": "string | null",
  "is_shared": "boolean",
  "pinned": "boolean",
  "unread_message_count": "integer",
  "latest_message": "string | null",
  "latest_message_at": "timestamp",
  "workspace_dir": "string",
  "events": "array",
  "statistics": {
    "input_tokens": "integer",
    "output_tokens": "integer",
    "total_cost_usd": "float"
  },
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

#### `contribution_cases`（新增）

```json
{
  "_id": "string",
  "title": "string",
  "description": "string | null",
  "owner_user_id": "string",
  "target_repo": "linux | qemu | opensbi | gcc | llvm",
  "target_branch": "string",
  "status": "created | exploring | pending_explore_review | planning | pending_plan_review | developing | reviewing | pending_code_review | testing | pending_test_review | completed | failed | abandoned | escalated",
  "current_stage": "explore | plan | develop | review | test | null",
  "input_context": {
    "user_hint": "string",
    "target_repo": "string",
    "contribution_type_hint": "string"
  },
  "exploration_result_ref": "string | null",
  "execution_plan_ref": "string | null",
  "development_result_ref": "string | null",
  "review_verdict_ref": "string | null",
  "test_result_ref": "string | null",
  "review_iterations": "integer",
  "max_review_iterations": "integer",
  "last_error": "string | null",
  "cost": {
    "input_tokens": "integer",
    "output_tokens": "integer",
    "estimated_cost_usd": "float"
  },
  "created_at": "ISODate",
  "updated_at": "ISODate",
  "started_at": "ISODate | null",
  "completed_at": "ISODate | null",
  "abandoned_at": "ISODate | null"
}
```

#### `human_reviews`（新增）

```json
{
  "_id": "string",
  "case_id": "string",
  "stage": "explore | plan | develop | review | test",
  "action": "approve | reject | reject_to | abandon | modify",
  "comment": "string",
  "reject_to_stage": "string | null",
  "modified_artifact_ref": "string | null",
  "reviewer_user_id": "string",
  "reviewer_name": "string",
  "created_at": "ISODate"
}
```

#### `stage_outputs`（新增）

```json
{
  "_id": "string",
  "case_id": "string",
  "stage": "explore | plan | develop | review | test",
  "round_num": "integer",
  "summary": "string",
  "payload": "object",
  "artifact_paths": "array[string]",
  "created_by": "string",
  "created_at": "ISODate"
}
```

#### `audit_log`（新增）

```json
{
  "_id": "string",
  "entity_type": "session | case | review | auth",
  "entity_id": "string",
  "event_type": "string",
  "actor_user_id": "string",
  "data": "object",
  "created_at": "ISODate"
}
```

### I.2 MongoDB 索引速查

| 集合 | 索引 | 类型 |
|------|------|------|
| `contribution_cases` | `(owner_user_id, updated_at DESC)` | 复合 |
| `contribution_cases` | `(status, updated_at DESC)` | 复合 |
| `contribution_cases` | `(target_repo, updated_at DESC)` | 复合 |
| `stage_outputs` | `(case_id, stage, round_num DESC)` | 复合 |
| `human_reviews` | `(case_id, created_at DESC)` | 复合 |
| `human_reviews` | `(reviewer_user_id, created_at DESC)` | 复合 |
| `audit_log` | `(entity_type, entity_id, created_at DESC)` | 复合 |
| `audit_log` | `(event_type, created_at DESC)` | 复合 |

### I.3 MongoDB TTL 策略

| 集合/条件 | TTL | 说明 |
|-----------|-----|------|
| `audit_log` | 2 年 | 自动清理旧审计记录 |
| `abandoned` case | 90 天 | 放弃的案例自动清理 |
| 非最终 artifact | 30 天 | 中间产物自动清理 |

### I.4 PostgreSQL 表（LangGraph Checkpointer）

| 表名 | 用途 | 关键字段 |
|------|------|----------|
| `checkpoints` | 检查点元数据 | `thread_id`, `checkpoint_ns`, `checkpoint_id`, `parent_checkpoint_id` |
| `checkpoint_blobs` | 大对象存储 | `thread_id`, `checkpoint_ns`, `checkpoint_id`, `channel`, `version`, `type`, `blob` |
| `checkpoint_writes` | 写入记录 | `thread_id`, `checkpoint_ns`, `checkpoint_id`, `task_id`, `idx`, `channel`, `type`, `blob` |

### I.5 Redis Key 命名规范

| 用途 | Key 格式 | 示例 |
|------|----------|------|
| Pipeline 实时事件 | `case:{case_id}:events` | `case:abc123:events` |
| Pipeline 事件流 | `case:{case_id}:stream` | `case:abc123:stream` |
| 审核幂等缓存 | `review:{review_id}` | `review:rev456` |
| 全局资源锁 | `lock:resource:{type}` | `lock:resource:qemu` |
| 会话锁 | `session:{session_id}:lock` | `session:sess789:lock` |

---

## 附录 J：技术债务跟踪

> **用途**: 记录已知技术债务，防止临时方案永久化  
> **更新规则**: 发现新债务立即添加；偿还后标记完成并记录日期  
> **偿还优先级**: P0=阻塞开发 P1=影响质量 P2=可延后

| ID | 债务描述 | 引入原因 | 影响 | 优先级 | 计划偿还 Phase | 状态 | 记录日期 |
|----|----------|----------|------|--------|---------------|------|----------|
| TD-01 | Chat 事件 `events` 内嵌在 `sessions` 文档 | 兼容 ScienceClaw 现有结构 | 大文档性能下降 | P1 | Phase 4 | 未偿还 | 2026-04-29 |
| TD-02 | DeepAgents 与 LangGraph 两套 Agent 引擎并存 | 保留 ScienceClaw 功能 | 认知负担、资源调度复杂 | P1 | Phase 5（长期） | 未偿还 | 2026-04-29 |
| TD-03 | `sessions` 文档同时服务 Chat 和 Pipeline 查询 | Phase 1 快速迁移 | 统计查询性能差 | P2 | Phase 4 | 未偿还 | 2026-04-29 |
| TD-04 | 前端 Cases 页面未做虚拟滚动 | MVP 简化 | 大量案例时渲染慢 | P2 | Phase 4 | 未偿还 | 2026-04-29 |
| TD-05 | QEMU 沙箱首版用 mock 降级 | 环境搭建复杂 | Test 阶段非真实验证 | P0 | Phase 2.23 | 未偿还 | 2026-04-29 |
| TD-06 | Statistics 服务未区分 chat/pipeline 维度 | Phase 1 保留兼容 | 统计口径不统一 | P1 | Phase 4 | 未偿还 | 2026-04-29 |
| TD-07 | 旧 `user_sessions` token 与 JWT 双轨运行 | 平滑迁移需求 | 认证逻辑复杂 | P1 | Phase 2 | 未偿还 | 2026-04-29 |
| TD-08 | Redis Pub/Sub 消息不持久化 | 设计权衡 | Redis 重启期间事件丢失（Stream 补偿） | P2 | Phase 5（长期） | 未偿还 | 2026-04-29 |
| TD-09 | 文件服务未拆分 chat/cases 物理目录 | Phase 0 简化 | 路径和权限模型可能混乱 | P1 | Phase 1.15 | 未偿还 | 2026-04-29 |
| TD-10 | 缺少 OpenAPI → TypeScript 自动生成 | 工具链未搭建 | 前端类型与后端不同步风险 | P1 | Phase 1.14 | 未偿还 | 2026-04-29 |

### 技术债务偿还检查清单

偿还某项债务时，必须：

- [ ] 编写/更新相关测试，证明偿还后行为正确
- [ ] 更新 `progress.md` 本表格状态为"已偿还"并填写日期
- [ ] 在变更日志（附录 C）中记录债务偿还
- [ ] 运行回归测试，确认未引入新问题
- [ ] 如果债务偿还会导致 API 变更，遵循 API 稳定性契约（`tasks/codex/migration-rules.md` §4.2）

---

## 附录 K：部署与回滚检查清单

> **用途**: 确保每次部署和紧急回滚都有标准操作流程（SOP）  
> **执行者**: DevOps + 值班工程师  
> **关联文档**: `tasks/kimi/refactor-plan-v3.md` §5.14

### K.1 预部署检查（每次发布前必须完成）

- [ ] **代码检查**
  - [ ] `main` 分支 CI 全部通过（lint + unit + integration + build）
  - [ ] 无 `TODO`/`FIXME` 阻塞项残留（或已在 progress.md 中跟踪）
  - [ ] 代码 Review 完成（至少 1 人 approve）
  - [ ] PR 已 Squash merge，commit message 符合规范
- [ ] **数据库检查**
  - [ ] 迁移脚本已在 staging 环境执行通过
  - [ ] 迁移脚本幂等性已验证（重复执行无副作用）
  - [ ] 数据库备份已完成（MongoDB + PostgreSQL）
- [ ] **配置检查**
  - [ ] 环境变量清单（附录 G）已全部配置到生产环境
  - [ ] Secrets 已注入（不存储在 git 中）
  - [ ] Feature Flag 默认值符合发布策略
- [ ] **兼容性检查**
  - [ ] 旧 API 契约未被破坏（向后兼容）
  - [ ] 前端资源路径未变更（或已配置 redirect）
  - [ ] Task Service 调用契约未变更

### K.2 部署步骤

```bash
# 1. 备份数据（5 分钟）
docker compose exec mongo mongodump --out /backup/pre-deploy-$(date +%Y%m%d_%H%M%S)
docker compose exec postgres pg_dump -U rv rv_checkpoints > /backup/pg-pre-deploy-$(date +%Y%m%d_%H%M%S).sql

# 2. 拉取最新代码（1 分钟）
git pull origin main

# 3. 执行数据库迁移（2 分钟）
docker compose exec backend python -m db.migrations

# 4. 构建并重启服务（3 分钟）
docker compose -f docker-compose-release.yml up -d --build --no-deps backend frontend

# 5. 健康检查（2 分钟）
curl -sf http://localhost:8000/health || (echo "HEALTH CHECK FAILED"; exit 1)
curl -sf http://localhost:8000/ready || (echo "READY CHECK FAILED"; exit 1)

# 6. 冒烟测试（5 分钟）
# - 登录页可访问
# - 创建 Chat session + 发送消息
# - Cases 列表页可访问（如果 Pipeline 已启用）
# - 文件上传/下载正常

# 7. 监控确认（持续 10 分钟）
# - Grafana 面板无异常告警
# - 错误日志率 < 1%
# - P95 响应时间 < 500ms
```

### K.3 回滚方案

#### 场景 1：Pipeline 功能异常，Chat 正常

- **操作**: 关闭 `PIPELINE_ENABLED=false`，隐藏 Cases 入口
- **影响**: Chat 用户无感知，Pipeline 用户暂时无法使用
- **步骤**:
  1. 修改 `.env`：`PIPELINE_ENABLED=False`
  2. `docker compose restart backend`
  3. 前端强制刷新（CDN 缓存清除）
  4. 告警通知用户 Cases 功能暂时下线

#### 场景 2：认证层异常，全站无法登录

- **操作**: 回切到旧 `ScienceClaw/backend`
- **影响**: 所有用户需要重新登录，Pipeline 功能不可用
- **步骤**:
  1. 停止 rv-claw backend：`docker compose stop backend`
  2. 启动旧 backend（独立端口或修改 Nginx upstream）
  3. 恢复旧 `.env` 中的数据库连接（指向旧 MongoDB 实例）
  4. 发布公告：需要重新登录一次
  5. 修复认证层后重新切换

#### 场景 3：数据库迁移失败

- **操作**: 恢复备份，回滚代码
- **影响**: 数据可能回退到部署前状态（期间数据丢失）
- **步骤**:
  1. 立即停止 backend：`docker compose stop backend`
  2. 恢复 MongoDB：`mongorestore --drop /backup/...`
  3. 恢复 PostgreSQL：`psql -U rv rv_checkpoints < /backup/...`
  4. 回滚代码：`git reset --hard HEAD~1`
  5. 重启服务：`docker compose up -d`

#### 场景 4：SSE 事件总线异常

- **操作**: 切换到前端轮询降级模式
- **影响**: Pipeline 实时性下降，但功能可用
- **步骤**:
  1. 配置 `SSE_FALLBACK_POLLING=true`
  2. 前端自动检测 SSE 连接失败，切换到 5s 轮询 `/cases/{id}` detail
  3. 修复 Redis 后恢复 SSE

### K.4 紧急联系人

| 角色 | 职责 | 联系渠道 |
|------|------|----------|
| 值班工程师 | 第一响应人 | Slack #on-call |
| Tech Lead | 架构决策 | Slack #tech-lead |
| DevOps | 基础设施 | Slack #devops |
| 产品负责人 | 业务决策 | Slack #product |

### K.5 监控告警规则

| 告警名称 | 条件 | 级别 | 响应时间 |
|----------|------|------|----------|
| Backend Down | `/health` 返回非 200 连续 3 次 | P0 | 5 分钟内 |
| DB Connection Fail | PostgreSQL/MongoDB 连接失败 | P0 | 5 分钟内 |
| High Error Rate | 5xx 率 > 1% 持续 5 分钟 | P1 | 15 分钟内 |
| High Latency | P95 > 2s 持续 10 分钟 | P1 | 30 分钟内 |
| Disk Full | 磁盘使用 > 85% | P1 | 1 小时内 |
| SSE Connection Drop | SSE 连接断开率 > 10% | P2 | 1 小时内 |
| Agent Cost Spike | 单案例成本 > $5 美元 | P2 | 4 小时内 |

---

> **本文档版本**: v2.1（2026-04-29）  
> **更新规则**: 每完成一个子任务立即标记 ✅；新增附录需同步更新版本号
