

---

## 7. 实施阶段规划（16周详细版）

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

### 7.1 Phase 0: 基础架构（2周）

**目标**: 搭建双模式开发基础，确保 ScienceClaw 功能无损

#### Week 1: 基础设施

| 任务 ID | 任务 | 详情 | 产出 | 负责人 | 阻塞项 |
|---------|------|------|------|--------|--------|
| P0.1 | 创建缺失设计文档 | `mvp-tasks.md`, `migration-map.md`, `chat-architecture.md`, `conventions.md` | 4 份文档 | Tech Lead | 无 |
| P0.2 | 初始化后端目录结构 | `backend/pipeline/`, `adapters/`, `datasources/`, `contracts/` | 目录框架 | Backend Dev | 无 |
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
- [ ] `docker compose up` 成功启动 10 个服务
- [ ] `pytest` 现有测试全部通过
- [ ] `pnpm build` 前端构建成功
- [ ] admin/user 双角色认证正常
- [ ] PostgreSQL checkpointer 表自动创建
- [ ] 所有新目录结构就绪

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
- [ ] 所有 ScienceClaw 页面可正常访问且功能完整
- [ ] 新增 `/cases` 路由可访问（空页面即可）
- [ ] 设置系统新增 PipelineSettings Tab
- [ ] 统计 API endpoint 迁移完成
- [ ] E2E 回归测试基线通过

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
- [ ] 可通过 API 创建案例并启动 Pipeline
- [ ] SSE 事件流正常推送阶段变更
- [ ] 人工审核门可暂停并恢复 Pipeline
- [ ] 产物文件正确写入文件系统
- [ ] 3 轮 Develop↔Review 迭代正常
- [ ] 成本熔断器在超限时报错
- [ ] 单元测试覆盖率 ≥ 70%

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
- [ ] 可从前端创建案例并启动 Pipeline
- [ ] Pipeline 可视化实时更新阶段状态
- [ ] 人工审核面板在 pending 状态时正确显示
- [ ] DiffViewer 正确渲染补丁和 findings 高亮
- [ ] AgentEventLog 实时显示 Agent 执行过程
- [ ] E2E 测试覆盖完整案例生命周期

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
- [ ] QEMU 沙箱可正确编译和运行 RISC-V 测试
- [ ] checkpatch.pl 和 sparse 在 Review 阶段自动运行
- [ ] API 速率限制生效
- [ ] 故障恢复测试通过（服务重启后 Pipeline 可恢复）
- [ ] 性能测试通过（50 并发 API, 100 SSE 连接）
- [ ] 安全扫描无高危漏洞

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
- [ ] 生产环境部署成功
- [ ] 所有文档完备
- [ ] 团队培训完成
- [ ] 上线检查清单全部通过

---

## 8. 测试策略（全面覆盖）

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

## 9. 监控与可观测性（生产级）

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

### 9.5 Grafana 仪表盘

```json
// 关键面板配置
{
  "dashboard": {
    "title": "RV-Claw Pipeline Overview",
    "panels": [
      {
        "title": "Active Pipelines",
        "type": "stat",
        "targets": [{
          "expr": "sum(rv_active_pipelines)"
        }]
      },
      {
        "title": "Pipeline Completion Rate",
        "type": "graph",
        "targets": [{
          "expr": "rate(rv_pipeline_completed_total[1h])"
        }]
      },
      {
        "title": "Stage Duration",
        "type": "heatmap",
        "targets": [{
          "expr": "rv_stage_duration_seconds_bucket"
        }]
      },
      {
        "title": "Cost Trend",
        "type": "graph",
        "targets": [{
          "expr": "sum(rv_cost_usd) by (stage)"
        }]
      }
    ]
  }
}
```

---

## 10. 风险与缓解（详细版）

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

## 11. 验收标准（最终版）

### 11.1 功能验收（Checklist）

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

### 11.2 性能验收

| 指标 | 目标 | 测试方法 |
|------|------|----------|
| API P99 | < 500ms | locust -u 50 -r 10 |
| SSE 延迟 | < 1s | WebSocket 测试工具 |
| 前端首屏 | < 2s | Lighthouse |
| 并发 Pipeline | 5 个无死锁 | 手动测试 |
| 内存使用 | < 4GB | docker stats |

### 11.3 质量验收

| 指标 | 目标 | 工具 |
|------|------|------|
| 单元测试覆盖率 | ≥ 85% | pytest-cov |
| E2E 测试通过率 | 100% | Playwright |
| 类型检查 | 0 errors | mypy --strict |
| 代码风格 | 0 warnings | ruff |
| 安全扫描 | 0 high | bandit, safety |

### 11.4 文档验收

| 文档 | 完备标准 |
|------|----------|
| API 文档 | OpenAPI 自动生成，所有端点有描述 |
| 部署文档 | 新成员可独立完成部署 |
| 运维手册 | 包含故障处理流程 |
| 用户手册 | 包含截图和操作步骤 |

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

*本文档为 rv-claw 项目重构的权威计划（优化版 v2.0），所有开发工作应以此为准。*

**文档历史**:
- v1.0 (2026-04-29): 初始版本
- v2.0 (2026-04-29): 优化版，基于 RV-Insights 实际进展补充细节
