# MVP 任务定义

> **版本**: v2.0  
> **日期**: 2026-05-01  
> **状态**: 已审计（2026-05-01 全量代码审计后更新）  
> **关联文档**: [refactor-plan-v3.md](./refactor-plan.md), [design.md](./design.md), [progress.md](./progress.md)

---

## 1. MVP 范围

### 1.1 包含范围

| 维度 | 包含 | 说明 |
|------|------|------|
| **目标仓库** | Linux 内核 `arch/riscv/` | 首期仅支持内核 |
| **贡献类型** | ISA 扩展支持, 代码清理 | Bug 修复延后 |
| **探索方式** | 用户输入 + Patchwork API | 邮件列表自动爬取延后 |
| **审核迭代** | 最多 3 轮 | 3 轮后 escalate |
| **测试环境** | 编译验证 + QEMU 运行时 | 完整测试套件延后 |
| **前端** | Chat + Pipeline 双模式 | 仪表盘/知识库延后 |
| **部署** | Docker Compose 单机 | K8s 延后 |

### 1.2 不包含范围（Phase 2+）

- QEMU, GCC, LLVM, OpenSBI 目标仓库
- 邮件列表自动爬取
- 性能优化贡献类型
- K8s 多节点部署
- 知识库模块
- 高级仪表盘

---

## 2. Sprint 规划（10 Sprint × 2周）

### Sprint 0: 基础架构（Week 1-2）—— ✅ 已完成

**目标**: 搭建双模式开发基础，确保 ScienceClaw 功能无损

| 任务 | 负责人 | DoD | 实际状态 |
|------|--------|-----|----------|
| P0.1 创建缺失设计文档 | AI Agent | 4 份文档通过评审 | ✅ 完成（progress.md, migration-map.md, migration-rules.md, conventions.md, chat-architecture.md, ai-behavior-contract.md, state-machine-rules.md） |
| P0.2 初始化后端目录结构 | AI Agent | 7 个目录 + 空文件骨架 | ✅ 完成 |
| P0.3 Docker Compose 扩展 | AI Agent | postgres + qemu-sandbox 服务就绪 | ✅ 完成（12 个服务定义，qemu-sandbox 为占位符） |
| P0.4 PostgreSQL 初始化 | AI Agent | checkpointer 表自动创建 | ✅ 完成 |
| P0.5 MongoDB 索引脚本 | AI Agent | 4 个集合 + 索引就绪 | ⚠️ 迁移脚本存在，但 `db/collections.py` 索引函数为空（`...`） |
| P0.6 认证扩展（RBAC）| AI Agent | admin/user 双角色认证正常 | ✅ 完成 |
| P0.7 环境变量配置 | AI Agent | .env.example 完整 | ✅ 完成 |
| P0.8 依赖锁定 | AI Agent | pip install 成功 | ✅ 完成 |
| P0.9 健康检查扩展 | AI Agent | /health 返回完整状态 | ✅ 完成 |
| P0.10 回归测试基线 | AI Agent | 现有功能测试清单记录 | ⚠️ 模板存在但未填充 |
| P0.11 CI/CD 配置 | AI Agent | GitHub Actions 4 stage 运行 | ✅ 完成（lint, unit-test, e2e-test, docker-build） |
| P0.12 数据库迁移脚本 | AI Agent | 幂等迁移脚本就绪 | ✅ 完成 |
| P0.13 Secrets 管理 | AI Agent | .env 不进入版本控制 | ✅ 完成 |
| P0.14 Feature Flag | AI Agent | Pipeline 默认关闭 | ✅ 完成 |

### Sprint 1-2: Chat 模式完整迁移（Week 3-4）—— 🔄 90% 完成

**目标**: ScienceClaw 前端功能完整迁移到 rv-claw

| 任务 | 说明 | 实际状态 |
|------|------|----------|
| P1.1 前端路由重构 | 新增 /cases, /cases/:id | ✅ 完成 |
| P1.2 LeftPanel 扩展 | 新增 Cases 导航入口 | ✅ 完成 |
| P1.3 MainLayout 改造 | 适配 Cases 页面布局 | ✅ 完成 |
| P1.4 类型定义 | case.ts, pipeline.ts, event.ts, artifact.ts, review.ts | ✅ 完成 |
| P1.5 API 类型定义 | cases.ts, reviews.ts, artifacts.ts | ✅ 完成 |
| P1.6 Statistics API 迁移 | /metrics/* → /statistics/* | ✅ 完成 |
| P1.7 StatisticsPage | 新增 Pipeline 统计占位 | ⚠️ 9 行占位符，未实现图表 |
| P1.8 Settings 扩展 | PipelineSettings Tab | ❌ 未实现 |
| P1.9 API 层整合 | index.ts 导出新增 API | ✅ 完成 |
| P1.10 i18n 扩展 | pipeline/review/case_status 命名空间 | ❓ 未确认（需人工核查） |
| P1.11 E2E 基线测试 | 所有页面可访问 | ✅ Playwright 13/14 通过 |
| P1.12 前端测试基础设施 | Vitest + Playwright | ⚠️ Playwright ✅, Vitest ❌ |
| P1.13 Mock Server | MSW 配置 | ❌ 未实现 |
| P1.14 OpenAPI → TS | 自动生成类型 | ❌ 未实现 |

### Sprint 3-6: Pipeline 后端骨架（Week 5-8）—— 🔄 65% 完成（骨架就绪，核心节点为占位符）

**目标**: Pipeline 后端核心实现

| 任务 | 说明 | 实际状态 |
|------|------|----------|
| P2.1 PipelineState 模型 | Pydantic 模型 | ✅ 完成 |
| P2.2 StateGraph 构建 | 10 节点 + 条件边 | ✅ 完成 |
| P2.3 AgentAdapter 基类 | ABC + 统一事件接口 | ⚠️ base.py ✅, event_mapper 空文件 |
| P2.4 ClaudeAgentAdapter | Claude SDK 封装 | ⚠️ 结构完整，但 execute() 为占位符 |
| P2.5 OpenAIAgentAdapter | OpenAI SDK 封装 | ⚠️ 结构完整，但 execute() 为占位符 |
| P2.6 EventPublisher | Redis Pub/Sub + Stream | ✅ 完成 |
| P2.7 ArtifactManager | 产物文件系统管理 | ✅ 完成 |
| P2.8 CostCircuitBreaker | 成本熔断器 | ✅ 完成 |
| P2.9 explore_node | 探索 Agent | ⚠️ 占位符（静态 JSON，无 LLM 调用） |
| P2.10 plan_node | 规划 Agent | ⚠️ 占位符（静态 JSON，无 LLM 调用） |
| P2.11 develop_node | 开发 Agent | ⚠️ 占位符（静态 patch，无 LLM 调用） |
| P2.12 human_gate_node | 人工审核门 | ✅ 功能完整（含 interrupt + fallback） |
| P2.13 route_human_decision | 条件路由 | ✅ 完成 |
| P2.14 review_node | 审核 Agent | ⚠️ 占位符（仅迭代计数，无 checkpatch/LLM） |
| P2.15 test_node | 测试 Agent | ⚠️ 占位符（确定性成功，无 QEMU） |
| P2.16 route_review_decision | Review 路由 | ✅ 完成（含收敛/重叠检测） |
| P2.17 escalate_node | 升级处理 | ✅ 完成 |
| P2.18 数据源实现 | Patchwork, MailingList, ISA Registry | ✅ 3/4 完成（github_client 空文件） |
| P2.19 cases 路由 | CRUD + 启动 Pipeline + SSE | ✅ 完成（8 个端点整合在 cases.py） |
| P2.20 reviews 路由 | 人工审核提交 | ✅ 已整合到 cases.py |
| P2.21 artifacts 路由 | 产物下载 | ✅ 已整合到 cases.py |
| P2.22 pipeline 路由 | 状态查询/强制停止 | ✅ 已整合到 cases.py |
| P2.23 FastAPI 主入口扩展 | 挂载新路由 | ✅ 完成（12 个 router） |
| P2.24 数据契约实现 | Pydantic 模型 | ✅ 全部 5 个阶段完成 |
| P2.25 资源调度器 | Semaphore 并发控制 | ❌ 未实现 |
| P2.26 审计日志 | audit_log 集合 | ⚠️ audit.py 存在但未接入 cases.py |
| P2.27 数据种子/Fixture | Mock 工厂函数 | ❌ tests/fixtures/ 目录不存在 |

### Sprint 7-10: Pipeline 前端与集成（Week 9-12）—— 🔄 85% 完成（组件齐全，6 个文件有导入错误）

**目标**: Pipeline 前端全部组件，与后端联调

| 任务 | 说明 | 实际状态 |
|------|------|----------|
| P3.1 CaseListView | 案例列表 | ✅ 完成（266 行） |
| P3.2 CaseDetailView | 案例详情（核心页面）| ✅ 完成（373 行） |
| P3.3 PipelineView | 5 阶段流水线可视化 | ✅ 完成 |
| P3.4 StageNode | 单阶段节点 | ✅ 完成 |
| P3.5 useCaseEvents | SSE 事件流管理 | ✅ 完成（指数退避重连） |
| P3.6 HumanGate | 人工审核门禁 UI | ✅ 完成 |
| P3.7 ReviewPanel | 审核决策面板 | ⚠️ 完成，但导入 `@/contracts/review` 不存在 |
| P3.8 ReviewFinding | 审核发现项 | ⚠️ 完成，但导入 `@/contracts/review` 不存在 |
| P3.9 DiffViewer | 基于 Monaco 的 Diff | ⚠️ 基础 diff 渲染完成，无 Monaco 集成 |
| P3.10 CostIndicator | 成本指示器 | ❓ 未确认 |
| P3.11 ContributionCard | 贡献机会卡片 | ⚠️ 完成，但导入 `@/contracts/exploration` 不存在 |
| P3.12 EvidenceChain | 证据链展示 | ⚠️ 完成，但导入 `@/contracts/exploration` 不存在 |
| P3.13 ExecutionPlan | 执行计划展示 | ⚠️ 完成，但导入 `@/contracts/planning` 不存在 |
| P3.14 AgentEventLog | Agent 实时事件日志 | ❌ 独立组件不存在 |
| P3.15 TestResultSummary | 测试结果摘要 | ⚠️ 完成，但导入 `@/contracts/testing` 不存在 |
| P3.16-3.21 API + Store + 联调 | 前后端联调 | ✅ 核心流程联调通过（Playwright 验证） |
| P3.22 E2E 测试 | 完整案例生命周期 | ⚠️ Playwright 基础 E2E 通过，未覆盖完整生命周期 |
| P3.23 Storybook | 组件文档 | ❌ 未实现 |

---

## 3. 技术债务记录

| ID | 描述 | 引入时间 | 计划解决 Sprint | 实际状态 |
|----|------|----------|----------------|----------|
| TD-1 | 当前认证使用简单本地认证，未使用 JWT | Sprint 0 | Sprint 1 | ✅ 已解决（JWT + RBAC 已实现） |
| TD-2 | MongoDB 集合初始化分散在各模块，未统一 | Sprint 0 | Sprint 0 | ⚠️ 部分解决（`db/collections.py` 函数体为空） |
| TD-3 | frontend 使用模块级 ref 单例，未使用 Pinia | 已有 | 保持 | ✅ 保持（继续使用 composable 模式） |
| TD-4 | ScienceClaw 后端未按分层架构设计 | 已有 | 渐进重构 | 🔄 进行中 |
| TD-5 | docker-compose.yml 未区分 dev/prod 环境 | Sprint 0 | Sprint 1 | ⚠️ 有 override/release/china 变体，但未完全区分 dev/prod |
| TD-11 | 前端 6 个组件导入 `@/contracts/*` 路径不存在 | Sprint 7-10 | Sprint 7-10 | ❌ 阻塞编译 |
| TD-12 | `db/collections.py` 索引函数为空 | Sprint 0 | Sprint 0 | ❌ 未解决 |
| TD-13 | Pipeline 5 个核心节点均为占位符 | Sprint 3-6 | Sprint 3-6 | ❌ 未解决 |
| TD-14 | `POST /cases/:id/start` 未调用 LangGraph graph | Sprint 3-6 | Sprint 3-6 | ❌ 未解决 |
| TD-15 | `adapters/event_mapper.py` 为空文件 | Sprint 3-6 | Sprint 3-6 | ❌ 未解决 |
| TD-16 | `datasources/github_client.py` 为空文件 | Sprint 3-6 | Sprint 3-6 | ❌ 未解决 |
| TD-17 | `audit.py` 未接入 `cases.py` | Sprint 3-6 | Sprint 3-6 | ❌ 未解决 |
| TD-18 | `api/reviews.ts` 与 `api/cases.ts` 功能重复 | Sprint 1-2 | Sprint 1-2 | ❌ 未解决 |
| TD-19 | `useCaseStore` 为实例级而非模块级单例 | Sprint 7-10 | Sprint 7-10 | ❌ 未解决 |
| TD-20 | `tests/fixtures/` 目录不存在 | Sprint 3-6 | Sprint 3-6 | ❌ 未解决 |
| TD-22 | StatisticsPage 为占位符 | Sprint 1-2 | Sprint 1-2 | ❌ 未解决 |
| TD-23 | PipelineSettings.vue / SettingsTabs Tab 未实现 | Sprint 1-2 | Sprint 1-2 | ❌ 未解决 |

---

## 4. 边界定义

### Phase 1/2 边界
- **Phase 1 结束标志**: /cases 路由可访问，前端显示空案例列表
- **Phase 2 开始标志**: 后端 Pipeline 引擎就绪，可创建案例并启动

### Phase 2/3 边界
- **Phase 2 结束标志**: POST /cases/:id/start 后 Pipeline 可运行到第一个 human_gate
- **Phase 3 开始标志**: 前端 CaseDetailView 可显示 Pipeline 实时状态

### Sprint 评审标准
每个 Sprint 结束必须满足：
1. `pytest` 通过率 ≥ 基线
2. `pnpm build` 成功
3. 新增功能有对应测试
4. `docker compose up` 服务全部 healthy

---

> **本文档自 2026-04-30 起生效。范围变更需通过人类工程师审批。**
