# MVP 任务定义

> **版本**: v1.0  
> **日期**: 2026-04-30  
> **状态**: 初稿  
> **关联文档**: [refactor-plan-v3.md](./refactor-plan.md), [design.md](./design.md)

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

### Sprint 0: 基础架构（Week 1-2）

**目标**: 搭建双模式开发基础，确保 ScienceClaw 功能无损

| 任务 | 负责人 | DoD |
|------|--------|-----|
| P0.1 创建缺失设计文档 | AI Agent | 4 份文档通过评审 |
| P0.2 初始化后端目录结构 | AI Agent | 7 个目录 + 空文件骨架 |
| P0.3 Docker Compose 扩展 | AI Agent | postgres + qemu-sandbox 服务就绪 |
| P0.4 PostgreSQL 初始化 | AI Agent | checkpointer 表自动创建 |
| P0.5 MongoDB 索引脚本 | AI Agent | 4 个集合 + 索引就绪 |
| P0.6 认证扩展（RBAC）| AI Agent | admin/user 双角色认证正常 |
| P0.7 环境变量配置 | AI Agent | .env.example 完整 |
| P0.8 依赖锁定 | AI Agent | pip install 成功 |
| P0.9 健康检查扩展 | AI Agent | /health 返回完整状态 |
| P0.10 回归测试基线 | AI Agent | 现有功能测试清单记录 |
| P0.11 CI/CD 配置 | AI Agent | GitHub Actions 4 stage 运行 |
| P0.12 数据库迁移脚本 | AI Agent | 幂等迁移脚本就绪 |
| P0.13 Secrets 管理 | AI Agent | .env 不进入版本控制 |
| P0.14 Feature Flag | AI Agent | Pipeline 默认关闭 |

### Sprint 1-2: Chat 模式完整迁移（Week 3-4）

**目标**: ScienceClaw 前端功能完整迁移到 rv-claw

| 任务 | 说明 |
|------|------|
| P1.1 前端路由重构 | 新增 /cases, /cases/:id |
| P1.2 LeftPanel 扩展 | 新增 Cases 导航入口 |
| P1.3 MainLayout 改造 | 适配 Cases 页面布局 |
| P1.4 类型定义 | case.ts, pipeline.ts, event.ts, artifact.ts, review.ts |
| P1.5 API 类型定义 | cases.ts, reviews.ts, artifacts.ts |
| P1.6 Statistics API 迁移 | /metrics/* → /statistics/* |
| P1.7 StatisticsPage | 新增 Pipeline 统计占位 |
| P1.8 Settings 扩展 | PipelineSettings Tab |
| P1.9 API 层整合 | index.ts 导出新增 API |
| P1.10 i18n 扩展 | pipeline/review/case_status 命名空间 |
| P1.11 E2E 基线测试 | 所有页面可访问 |
| P1.12 前端测试基础设施 | Vitest + Playwright |
| P1.13 Mock Server | MSW 配置 |
| P1.14 OpenAPI → TS | 自动生成类型 |

### Sprint 3-6: Pipeline 后端骨架（Week 5-8）

**目标**: Pipeline 后端核心实现

| 任务 | 说明 |
|------|------|
| P2.1 PipelineState 模型 | TypedDict 定义 |
| P2.2 StateGraph 构建 | 9 节点 + 条件边 |
| P2.3 AgentAdapter 基类 | ABC + 统一事件接口 |
| P2.4 ClaudeAgentAdapter | Claude SDK 封装 |
| P2.5 OpenAIAgentAdapter | OpenAI SDK 封装 |
| P2.6 EventPublisher | Redis Pub/Sub + Stream |
| P2.7 ArtifactManager | 产物文件系统管理 |
| P2.8 CostCircuitBreaker | 成本熔断器 |
| P2.9 explore_node | 探索 Agent |
| P2.10 plan_node | 规划 Agent |
| P2.11 develop_node | 开发 Agent |
| P2.12 human_gate_node | 人工审核门 |
| P2.13 route_human_decision | 条件路由 |
| P2.14 review_node | 审核 Agent |
| P2.15 test_node | 测试 Agent |
| P2.16 route_review_decision | Review 路由 |
| P2.17 escalate_node | 升级处理 |
| P2.18 数据源实现 | Patchwork, MailingList, ISA Registry |
| P2.19 cases 路由 | CRUD + 启动 Pipeline + SSE |
| P2.20 reviews 路由 | 人工审核提交 |
| P2.21 artifacts 路由 | 产物下载 |
| P2.22 pipeline 路由 | 状态查询/强制停止 |
| P2.23 FastAPI 主入口扩展 | 挂载新路由 |
| P2.24 数据契约实现 | Pydantic 模型 |
| P2.25 资源调度器 | Semaphore 并发控制 |
| P2.26 审计日志 | audit_log 集合 |
| P2.27 数据种子/Fixture | Mock 工厂函数 |

### Sprint 7-10: Pipeline 前端与集成（Week 9-12）

**目标**: Pipeline 前端全部组件，与后端联调

| 任务 | 说明 |
|------|------|
| P3.1 CaseListView | 案例列表 |
| P3.2 CaseDetailView | 案例详情（核心页面）|
| P3.3 PipelineView | 5 阶段流水线可视化 |
| P3.4 StageNode | 单阶段节点 |
| P3.5 useCaseEvents | SSE 事件流管理 |
| P3.6 HumanGate | 人工审核门禁 UI |
| P3.7 ReviewPanel | 审核决策面板 |
| P3.8 ReviewFinding | 审核发现项 |
| P3.9 DiffViewer | 基于 Monaco 的 Diff |
| P3.10 CostIndicator | 成本指示器 |
| P3.11 ContributionCard | 贡献机会卡片 |
| P3.12 EvidenceChain | 证据链展示 |
| P3.13 ExecutionPlan | 执行计划展示 |
| P3.14 AgentEventLog | Agent 实时事件日志 |
| P3.15 TestResultSummary | 测试结果摘要 |
| P3.16-3.21 API + Store + 联调 | 前后端联调 |
| P3.22 E2E 测试 | 完整案例生命周期 |
| P3.23 Storybook | 组件文档 |

---

## 3. 技术债务记录

| ID | 描述 | 引入时间 | 计划解决 Sprint |
|----|------|----------|----------------|
| TD-1 | 当前认证使用简单本地认证，未使用 JWT | Sprint 0 | Sprint 1 |
| TD-2 | MongoDB 集合初始化分散在各模块，未统一 | Sprint 0 | Sprint 0 |
| TD-3 | frontend 使用模块级 ref 单例，未使用 Pinia | 已有 | 保持 |
| TD-4 | ScienceClaw 后端未按分层架构设计 | 已有 | 渐进重构 |
| TD-5 | docker-compose.yml 未区分 dev/prod 环境 | Sprint 0 | Sprint 1 |

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
