# RV-Insights 工程规范与开发约束

> **版本**: v1.0  
> **日期**: 2026-04-29  
> **适用范围**: 所有 Sprint、所有开发者、所有代码提交  
> **强制执行**: CI 检查 + Code Review 卡点

---

## 目录

- [1. Git 工作流与分支规范](#1-git-工作流与分支规范)
- [2. Commit Message 规范](#2-commit-message-规范)
- [3. 代码风格规范](#3-代码风格规范)
- [4. 命名规范](#4-命名规范)
- [5. Definition of Done（完成标准）](#5-definition-of-done完成标准)
- [6. 测试标准](#6-测试标准)
- [7. API 设计规范](#7-api-设计规范)
- [8. 错误处理规范](#8-错误处理规范)
- [9. 日志规范](#9-日志规范)
- [10. Code Review 检查清单](#10-code-review-检查清单)
- [11. 架构决策记录 (ADR)](#11-架构决策记录-adr)
- [12. PR 模板](#12-pr-模板)

---

## 1. Git 工作流与分支规范

### 1.1 分支策略

```
main ──────────────────────────────────────────────→ 生产就绪
  │
  ├── feature/s0-infra-setup ─────→ PR → main       Sprint 0
  ├── feature/s1-jwt-auth ────────→ PR → main       Sprint 1
  ├── feature/s2-chat-mode ───────→ PR → main       Sprint 2
  ├── feature/s3-pipeline-core ───→ PR → main       Sprint 3
  └── ...
```

**规则**：
- `main` 分支永远可部署（通过 CI 的全部检查）
- 每个 Sprint = 一个 `feature/s{编号}-{简短描述}` 分支
- 禁止直接 push 到 `main`，所有变更通过 PR 合并
- PR 合并策略：**Squash and merge**（保持 main 历史线性、干净）

### 1.2 分支命名

```
feature/s{编号}-{2-4个词描述}    # 功能开发
fix/s{编号}-{问题描述}            # Bug 修复
hotfix/{紧急描述}                # 生产环境紧急修复（从 main 拉，合并回 main）
```

**示例**：
```
feature/s0-infra-setup
feature/s3-pipeline-core
fix/s4-explorer-hallucination
hotfix/jwt-expiry-overflow
```

### 1.3 禁止操作

- ❌ `git push --force` 到 `main`
- ❌ `git commit --amend` 已推送的 commit
- ❌ 合并未通过 CI 的 PR
- ❌ 跳过 pre-commit hook（`--no-verify`）

---

## 2. Commit Message 规范

### 2.1 格式

```
<type>(<scope>): <简短描述>

[可选的详细描述 — 解释 why，而非 what]

[关联 issue/task 编号]
```

### 2.2 Type 定义

| Type | 用途 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(pipeline): add explore node with Claude SDK adapter` |
| `fix` | Bug 修复 | `fix(sse): prevent duplicate events on reconnect` |
| `refactor` | 重构（不改变行为） | `refactor(adapter): extract base AgentAdapter class` |
| `test` | 添加测试 | `test(contracts): add ExplorationResult validation tests` |
| `docs` | 文档变更 | `docs(api): add OpenAPI spec for cases endpoints` |
| `chore` | 杂项（依赖更新、配置调整） | `chore(deps): pin langgraph to 0.3.x` |
| `perf` | 性能优化 | `perf(db): add compound index for case queries` |
| `security` | 安全修复 | `security(input): add prompt injection detection` |

### 2.3 Scope 定义

```
auth, user, chat, pipeline, sse, db, api, frontend,
cases, review, adapter, contract, sandbox, deploy, ci, docs
```

### 2.4 示例

```
feat(pipeline): implement LangGraph StateGraph with 10 nodes

Built the complete 5-stage pipeline state machine:
- 5 agent nodes (explore/plan/develop/review/test)
- 4 human gate nodes (interrupt-based approval)
- 1 escalate node
- Conditional edges for review iteration + human decision routing

Closes: S3-T3.2
```

---

## 3. 代码风格规范

### 3.1 Python 后端

**工具链**：`ruff` (lint + format) + `mypy` (type check)

```ini
# pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "C4", "SIM"]

[tool.ruff.format]
quote-style = "double"

[tool.mypy]
strict = true
python_version = "3.12"
```

**强制规则**：

| 规则 | 说明 |
|------|------|
| 所有函数声明类型注解（参数 + 返回值） | `async def explore_node(state: PipelineState) -> dict:` |
| 所有 Pydantic 模型用 `model_validate` 而非 `parse_raw` | 使用 v2 API |
| 禁止 `except:` 裸捕获 | 必须指定异常类型，至少 `except Exception` |
| 禁止 `as any` / `# type: ignore` | 除非有充分理由并在 PR 中说明 |
| 异步函数用 `async def` 不用 `@asyncio.coroutine` | — |
| 字符串格式化用 f-string | 不用 `%` 或 `.format()` |
| 导入顺序：标准库 → 第三方 → 本地模块 | 由 ruff I 规则强制 |
| 环境变量通过 `config.py` 的 `Settings` 类访问 | 禁止在业务代码中直接 `os.getenv()` |

### 3.2 TypeScript / Vue 前端

**工具链**：`eslint` + `prettier`

```json
// .eslintrc.json
{
  "extends": ["@vue/typescript/recommended", "prettier"],
  "rules": {
    "@typescript-eslint/no-explicit-any": "warn",
    "@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_" }],
    "vue/multi-word-component-names": "off"
  }
}
```

**强制规则**：

| 规则 | 说明 |
|------|------|
| 组件命名：PascalCase 多词（`CaseListView.vue`，而非 `Case.vue`） | Vue 官方风格指南 |
| Composable 命名：`use` 前缀 + camelCase（`useCaseEvents.ts`） | 遵循 ScienceClaw 惯例 |
| 类型文件命名：领域名 + `.ts`（`case.ts`，而非 `caseTypes.ts`） | — |
| Props 必须有类型声明 | `defineProps<{ caseId: string }>()` |
| 禁止 `any` 类型（使用 `unknown` + 类型守卫） | CI 中 eslint warning 视为 error |
| API 客户端统一使用 `api/client.ts` 导出的 `client` 实例 | 禁止直接 `axios.create()` |
| SSE 连接统一使用 `createSSEConnection()` | 禁止直接 `EventSource` |

---

## 4. 命名规范

### 4.1 Python

| 元素 | 规范 | 示例 |
|------|------|------|
| 模块/文件 | snake_case | `pipeline_state.py`, `claude_adapter.py` |
| 类 | PascalCase | `PipelineState`, `EventPublisher` |
| 函数/方法 | snake_case | `route_review_decision()`, `publish_event()` |
| 变量 | snake_case | `case_id`, `max_retries` |
| 常量 | UPPER_SNAKE_CASE | `MAX_REVIEW_ITERATIONS`, `CLAUDE_TIMEOUT_SECONDS` |
| 私有函数 | `_` 前缀 | `_convert_message()`, `_estimate_cost()` |
| Pydantic 模型字段 | snake_case | `case_id`, `review_iterations` |

### 4.2 TypeScript / Vue

| 元素 | 规范 | 示例 |
|------|------|------|
| Vue 组件文件 | PascalCase | `CaseDetailView.vue`, `StageNode.vue` |
| Composable 文件 | camelCase + `use` 前缀 | `useCaseEvents.ts`, `useAuth.ts` |
| 类型文件 | camelCase | `case.ts`, `pipeline.ts` |
| 接口/类型 | PascalCase | `CaseDetail`, `PipelineEvent` |
| 变量/函数 | camelCase | `caseId`, `subscribeCaseEvents()` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RECONNECT_ATTEMPTS` |
| API 函数 | camelCase | `casesApi.create()`, `fetchCaseDetail()` |

### 4.3 通用

| 元素 | 规范 | 示例 |
|------|------|------|
| MongoDB 集合 | snake_case 复数 | `contribution_cases`, `human_reviews` |
| MongoDB 字段 | snake_case | `case_id`, `created_at` |
| Redis Key | `:` 分隔 | `case:abc123:events`, `session:xyz:lock` |
| 环境变量 | UPPER_SNAKE_CASE | `CLAUDE_API_KEY`, `POSTGRES_URI` |

---

## 5. Definition of Done（完成标准）

### 5.1 任务级 DoD（progress.md 中每项勾选前必须满足）

- [ ] 代码实现完成，通过 `ruff check` + `mypy` (Python) 或 `eslint` (Vue)
- [ ] 相关单元测试已编写并通过（仅限后端逻辑/数据模型）
- [ ] 如果涉及 API 变更，前端对应的 TypeScript 类型已同步更新
- [ ] 如果涉及新依赖，已在 `requirements.txt` 或 `package.json` 中锁定版本
- [ ] 无 `TODO` 或 `FIXME` 残留（除非在 progress.md 阻塞项中跟踪）
- [ ] 本地 `docker compose up -d` 验证通过（服务 healthy + 功能可用）
- [ ] 关联的 progress.md 任务勾选为 `[x]`

### 5.2 Sprint 级 DoD（Sprint 结束时必须满足）

- [ ] Sprint 内全部 P0 任务（progress.md 中标记优先级 P0）已完成
- [ ] P1 任务完成率 ≥ 80%
- [ ] `pytest tests/unit/ -v` 全部通过，无失败
- [ ] `pytest tests/integration/ -v` 全部通过（如果 Sprint 含集成测试）
- [ ] CI 流水线全部绿色（lint → unit test → integration test → build）
- [ ] Code Review 已完成（至少 1 位 reviewer approve）
- [ ] PR 已 Squash merge 到 `main`
- [ ] `tasks/ds/progress.md` 中 Sprint 进度行已更新为 100%
- [ ] 无已知 P0 Bug

### 5.3 代码级 DoD（每个文件提交前自检）

- [ ] 函数/方法有 docstring（至少一行说明用途）
- [ ] Pydantic 模型有 `Field(description="...")` 说明
- [ ] 复杂逻辑有行内注释解释 why，不是 what
- [ ] 无硬编码的魔法数字（提取为常量或配置项）
- [ ] 无注释掉的代码（删除，git 历史可以找回）
- [ ] 错误路径有日志记录（`logger.error(...)` 含 `exc_info=True`）

---

## 6. 测试标准

### 6.1 覆盖率要求

| 模块 | 最低行覆盖率 | 最低分支覆盖率 |
|------|------------|--------------|
| `contracts/` (Pydantic 数据模型) | 95% | 90% |
| `pipeline/routes.py` (条件边路由) | 95% | 95% |
| `adapters/` (SDK 适配器) | 85% | 80% |
| `route/` (API 端点) | 80% | 75% |
| `pipeline/nodes/` (Agent 节点) | 70% | 60% |
| `events/` (事件系统) | 85% | 80% |

### 6.2 测试命名

```
tests/unit/test_{模块名}.py       # 单元测试
tests/integration/test_{场景}.py  # 集成测试
tests/e2e/{场景}.spec.ts          # E2E 测试
tests/eval/test_{agent}_prompt.py # Prompt 评估

# 测试函数命名
def test_{被测行为}_{条件}_{期望结果}():
    ...

# 示例
def test_route_review_decision_under_max_iterations_returns_reject():
def test_pipeline_state_invalid_target_repo_raises_validation_error():
```

### 6.3 Mock 策略

| 测试层级 | Mock 对象 | 不 Mock 的对象 |
|----------|----------|---------------|
| 单元测试 | 外部 API（Claude SDK、OpenAI SDK）、数据库连接、Redis | Pydantic 模型、纯函数、路由逻辑 |
| 集成测试 | 外部 LLM API（用 Mock Agent 替换） | MongoDB、PostgreSQL（testcontainers 真实实例）、Redis |
| E2E 测试 | 无（全部真实环境） | — |

**原则**：
- 单元测试不访问网络、文件系统、数据库
- 集成测试使用 testcontainers 启停真实数据库（不 mock）
- Mock 必须验证调用参数，不只是 `return_value`

### 6.4 必须测试的边界条件

- 空输入 / null / undefined
- 超长输入（> 10000 字符）
- 并发冲突（两个请求同时修改同一资源）
- 超时场景（LLM API 超时、数据库连接超时）
- 认证失败（无 token / 过期 token / 伪造 token）
- 权限不足（user 角色尝试 admin 操作）

---

## 7. API 设计规范

### 7.1 REST API 约定

| 约定 | 规则 | 示例 |
|------|------|------|
| URL 前缀 | `/api/v1/` | `/api/v1/cases` |
| 资源名 | 小写复数 | `/cases` 而非 `/case` |
| 嵌套资源 | `/cases/{id}/reviews` | 审核是案例的子资源 |
| HTTP 方法 | 标准 CRUD 映射 | `GET` 查询, `POST` 创建, `PUT` 全量更新, `PATCH` 部分更新, `DELETE` 删除 |
| 创建成功 | 201 + 返回创建的资源 | `POST /cases` → 201 + `{id, ...}` |
| 分页 | `?page=1&page_size=20` | 返回 `{items, total, page, page_size, total_pages}` |
| 筛选 | 查询参数 | `?status=exploring&target_repo=linux` |
| 排序 | `?sort_by=created_at&sort_order=desc` | — |

### 7.2 响应格式

**成功响应**：
```json
// 单资源
{ "id": "...", "title": "...", ... }

// 列表
{ "items": [...], "total": 42, "page": 1, "page_size": 20, "total_pages": 3 }

// 操作
{ "status": "ok", "message": "Pipeline started" }
```

**错误响应**：
```json
{
  "detail": "人类可读的错误描述",
  "error_code": "CASE_NOT_FOUND",    // 可选，机器可读的错误码
  "field": "target_repo",            // 可选，字段级错误时包含
  "suggestion": "Valid values: linux, qemu, opensbi, gcc, llvm"  // 可选，修复建议
}
```

### 7.3 HTTP 状态码使用

| 状态码 | 场景 |
|--------|------|
| 200 | 查询成功、操作成功 |
| 201 | 资源创建成功 |
| 204 | 删除成功（无 body） |
| 400 | 请求参数错误（Pydantic 验证失败） |
| 401 | 未认证（无 token 或 token 无效） |
| 403 | 已认证但权限不足 |
| 404 | 资源不存在 |
| 409 | 状态冲突（如对非 created 状态的 case 调用 start） |
| 422 | 请求格式正确但语义错误 |
| 429 | 速率限制 |
| 500 | 服务器内部错误（不应该暴露细节） |
| 503 | 服务依赖不可用（数据库/sandbox 不健康） |

### 7.4 Pydantic 模型规范

```python
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class CreateCaseRequest(BaseModel):
    """创建案例请求"""
    title: str = Field(
        ..., min_length=1, max_length=200,
        description="案例标题",
        examples=["Add Zicfiss support to Linux kernel"],
    )
    target_repo: Literal["linux", "qemu", "opensbi", "gcc", "llvm"] = Field(
        ..., description="目标 RISC-V 仓库",
    )
    input_context: dict = Field(
        default_factory=dict,
        description="用户提示和上下文信息",
    )

class CaseResponse(BaseModel):
    """案例响应"""
    id: str = Field(..., description="案例唯一标识")
    title: str
    status: str
    target_repo: str
    cost: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
```

---

## 8. 错误处理规范

### 8.1 异常分类与处理策略

```
错误分类树：
├── TransientError (可重试)
│   ├── LLM API Timeout (3次指数退避)
│   ├── Network Jitter (3次指数退避)
│   ├── Rate Limit 429 (等待Retry-After)
│   └── Database Connection Reset (5次快速重试)
│
├── ModelError (降级)
│   ├── Claude API 不可用 → 切换到 claude-haiku-4
│   ├── GPT-4o 不可用 → 切换到 gpt-4o-mini
│   └── Codex 不可用 → 切换到 gpt-4o
│
├── LogicError (记录+升级)
│   ├── Agent 输出 JSON 解析失败 (2次修正重试→升级)
│   ├── ExplorationResult 证据不足 (降低可行性评分)
│   └── Pipeline 状态不一致 (升级到 human_gate)
│
├── ResourceError (等待+重试)
│   ├── QEMU 沙箱不可用 (等待300s)
│   ├── PostgreSQL 连接池耗尽 (等待60s)
│   └── 磁盘空间不足 (告警+拒绝新case)
│
└── FatalError (标记失败)
    ├── API Key 无效 (拒绝启动)
    ├── 目标仓库不存在 (case标记failed)
    └── 数据损坏 (从备份恢复)
```

### 8.2 异常处理代码模式

```python
# ✅ 正确：具体异常类型 + 日志 + 上下文
try:
    result = await call_llm_api(prompt)
except httpx.TimeoutException:
    logger.warning("llm_timeout", case_id=case_id, attempt=attempt)
    raise  # 由 tenacity 装饰器处理重试
except httpx.HTTPStatusError as e:
    if e.response.status_code == 429:
        retry_after = int(e.response.headers.get("Retry-After", 60))
        logger.warning("llm_rate_limited", case_id=case_id, retry_after=retry_after)
        await asyncio.sleep(retry_after)
        raise  # 触发重试
    else:
        logger.error("llm_api_error", case_id=case_id, status=e.response.status_code)
        raise

# ❌ 错误：裸捕获 + 无日志
try:
    result = await call_llm_api(prompt)
except:
    pass
```

### 8.3 用户可见错误消息

| 场景 | HTTP 响应 | 消息 |
|------|----------|------|
| 资源不存在 | 404 | `{"detail": "Case not found"}` |
| 状态冲突 | 409 | `{"detail": "Case is not in 'created' status", "current_status": "exploring"}` |
| 权限不足 | 403 | `{"detail": "Insufficient permissions", "required_role": "admin"}` |
| 参数错误 | 422 | `{"detail": "Invalid target_repo", "valid_values": ["linux","qemu","opensbi","gcc","llvm"]}` |
| 服务不可用 | 503 | `{"detail": "Service temporarily unavailable", "retry_after_seconds": 60}` |

**攻击者不应看到的信息**（永远不返回给客户端）：
- 堆栈跟踪
- 数据库连接字符串
- API Key 前缀
- 内部 IP 地址
- 文件系统路径

---

## 9. 日志规范

### 9.1 日志级别使用

| 级别 | 场景 | 示例 |
|------|------|------|
| `DEBUG` | 开发调试细节（默认生产环境关闭） | LLM 请求完整 payload |
| `INFO` | 关键业务事件 | Pipeline 启动/阶段完成/case 创建 |
| `WARNING` | 可恢复的异常 | LLM API 超时重试、速率限制触发 |
| `ERROR` | 需要人工关注的失败 | Agent 执行失败、数据库写入失败 |
| `CRITICAL` | 系统级故障 | PostgreSQL 连接断开、磁盘满 |

### 9.2 日志字段规范

```python
# ✅ 始终绑定上下文标识符
log = logger.bind(case_id=case_id, stage="explore")

# ✅ 关键操作记录 before/after
log.info("explore_started", target_repo=state["target_repo"])
log.info("explore_completed", feasibility=0.85, evidence_count=3, duration_ms=45200)

# ✅ 错误日志含 exc_info
log.error("explore_failed", error=str(e), exc_info=True)

# ❌ 禁止日志中包含敏感信息
log.info("api_key_used", key=settings.claude_api_key)  # 绝对禁止！
log.info("user_login", username=user, password=password)  # 绝对禁止！
```

### 9.3 性能相关日志

```python
# 每个 LLM 调用记录耗时
start = time.monotonic()
result = await call_llm(prompt)
duration_ms = (time.monotonic() - start) * 1000
log.info("llm_call", model=model, input_tokens=n_input, output_tokens=n_output, duration_ms=duration_ms)
```

---

## 10. Code Review 检查清单

### 10.1 Reviewer 必须检查的项

| # | 检查项 | 说明 |
|---|--------|------|
| 1 | **类型安全** | 无 `as any`、`# type: ignore`、`@ts-ignore`（除非有充分注释说明） |
| 2 | **错误处理** | 无裸 `except:` 或 `catch(e) {}`，所有错误路径有日志 |
| 3 | **API 契约** | 请求/响应 schema 与设计文档一致，字段名无拼写错误 |
| 4 | **测试覆盖** | 新增逻辑有对应测试；边界条件已覆盖 |
| 5 | **安全** | 无硬编码密钥；用户输入经过验证/清理；SSRF/注入风险检查 |
| 6 | **性能** | 无 N+1 查询；大数据量有分页；SSE 连接不泄漏 |
| 7 | **命名** | 符合第 4 节命名规范，变量名自解释 |
| 8 | **日志** | 关键路径有 info 日志，错误路径有 error+exc_info |
| 9 | **依赖** | 新增依赖有必要性说明；版本已锁定 |
| 10 | **迁移** | 数据库 schema 变更含迁移脚本；可回滚 |

### 10.2 Review 流程

```
1. Author 创建 PR（填写 PR 模板）
2. 自动检查：CI (lint + test) 必须全部通过
3. Reviewer 按检查清单逐项审查
4. 发现问题 → 行级评论 + Request Changes
5. Author 修复 → 推送新 commit → 重新触发 CI
6. Reviewer 确认修复 → Approve
7. Author Squash merge 到 main
```

### 10.3 Review 时间承诺

- PR < 200 行：24 小时内完成 review
- PR 200-500 行：48 小时内
- PR > 500 行：要求 Author 拆分为多个小 PR

---

## 11. 架构决策记录 (ADR)

所有重要架构决策必须记录在 `tasks/ds/adr/` 目录下。使用以下模板：

```markdown
# ADR-{编号}: {决策标题}

**日期**: YYYY-MM-DD
**状态**: proposed | accepted | deprecated | superseded
**决策者**: {姓名}

## 背景
{为什么需要做这个决策？上下文是什么？}

## 决策
{我们决定做什么？}

## 考虑的替代方案
1. **方案 A**: {描述} — 优点/缺点
2. **方案 B**: {描述} — 优点/缺点

## 后果
{这个决策会带来什么影响？}

### 正面影响
- ...

### 负面影响
- ...

## 相关
- 关联的设计文档或 ADR 编号
```

### 11.1 已有决策（应补录为 ADR）

| ADR | 决策 | 来源 |
|-----|------|------|
| ADR-001 | 使用 LangGraph StateGraph 作为 Pipeline 编排引擎 | design.md §5.2 |
| ADR-002 | Claude Agent SDK 用于执行密集型任务（Explore/Develop/Test） | design.md §3.5 |
| ADR-003 | OpenAI Agents SDK 用于推理判断型任务（Plan/Review） | design.md §3.5 |
| ADR-004 | Redis Pub/Sub + Stream 作为 Pipeline SSE 事件总线 | design.md §2.8 |
| ADR-005 | PostgreSQL 作为 LangGraph Checkpointer（非 MongoDB） | design.md §6.2 |
| ADR-006 | JWT 替代 ScienceClaw 的 Session Token 认证 | refactoring-plan.md §C.1 |
| ADR-007 | Chat 模式复用 DeepAgents 引擎，Pipeline 模式使用 LangGraph | refactoring-plan.md §C.1 |
| ADR-008 | 前端使用 Composable 模式（非 Pinia）保持与 ScienceClaw 一致 | refactoring-plan.md §C.1 |

---

## 12. PR 模板

```markdown
## 概述
<!-- 一句话描述这个 PR 做了什么 -->

## 关联任务
<!-- 关联的 progress.md 任务编号，如 S3-T3.2 -->

## 变更类型
- [ ] 新功能 (feat)
- [ ] Bug 修复 (fix)
- [ ] 重构 (refactor)
- [ ] 测试 (test)
- [ ] 文档 (docs)
- [ ] 其他

## 变更文件清单
<!-- 列出所有被修改/新增的文件 -->

## 测试
- [ ] 单元测试已添加/更新
- [ ] 集成测试已添加/更新（如果涉及 API 变更）
- [ ] 本地 `docker compose up -d` 验证通过
- [ ] `pytest` 全部通过

## 自查清单（Author 提交前自检）
- [ ] 代码通过 `ruff check` + `mypy` (Python) 或 `eslint` (Vue)
- [ ] 函数有 docstring / 复杂逻辑有注释
- [ ] 无硬编码密钥、无调试代码残留
- [ ] API 变更已同步更新前端 TypeScript 类型
- [ ] 无新增 `TODO` 或 `FIXME`（或在阻塞项中记录）

## Reviewer 检查清单
- [ ] 类型安全：无 `as any` / `# type: ignore`
- [ ] 错误处理：无裸 except，错误路径有日志
- [ ] API 契约：请求/响应与设计一致
- [ ] 测试覆盖：新增逻辑有对应测试
- [ ] 安全：无密钥泄露，输入已验证
- [ ] 性能：无 N+1 查询，SSE 连接不泄漏
```

---

> **本规范自 2026-04-29 起生效。所有违反规范的代码不得合并到 main 分支。**
> **规范本身的修改需要通过 PR + Review 流程，不得直接编辑。**
