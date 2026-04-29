# AI 开发者行为契约

> **版本**: v1.0  
> **日期**: 2026-04-29  
> **适用范围**: 所有 AI Agent（Sisyphus 及其子代理）在 rv-claw 仓库中的编码活动  
> **优先级**: 高于一般工程规范——本契约的条款为**不可协商**（non-negotiable）

---

## 0. 核心原则

1. **代码必须能通过资深工程师的代码审查**——不能因为它是 AI 写的就降低标准。
2. **先验证，后声称完成**——没有运行过测试、lint、类型检查的代码不算完成。
3. **最小惊讶原则**——我的代码行为必须与已有代码库的风格和模式一致。
4. **宁缺毋滥**——宁可少提交一个文件，也不提交一个有类型错误或裸 except 的文件。

---

## 1. 绝对禁止项（零容忍）

以下行为一旦发现，**立即回滚**相关修改，无论功能是否正确。

### 1.1 类型安全

| 禁止行为 | 替代方案 | 理由 |
|----------|----------|------|
| `as any` (TypeScript) | `unknown` + 类型守卫 | 破坏类型系统 |
| `@ts-ignore` / `@ts-expect-error` | 修复底层类型问题 | 隐藏真实问题 |
| `# type: ignore` (Python) | 修复 mypy 报错原因 | 同左 |
| `dict` / `list` 替代 `TypedDict` / `Pydantic` | 使用 `BaseModel` 或 `TypedDict` | 失去结构验证 |
| 函数参数/返回值无类型注解 | 补全 `-> dict[str, Any]` 等 | Python 后端强制要求 |

### 1.2 错误处理

| 禁止行为 | 替代方案 | 理由 |
|----------|----------|------|
| `except:` 裸捕获 | `except Exception:` 或更具体的异常 | 吞掉系统异常（如 KeyboardInterrupt） |
| `catch (e) {}` 空块 | 至少 `logger.error(..., exc_info=True)` | 静默失败无法排查 |
| 吞掉异常后返回 `None` | 抛出异常或返回 `Result` 类型 | 调用方无法区分成功与失败 |

### 1.3 测试

| 禁止行为 | 替代方案 | 理由 |
|----------|----------|------|
| 删除失败测试来"通过"CI | 修复测试或修复被测代码 | 自欺欺人 |
| 提交无测试的新功能 | 遵循 TDD 协议（见第 4 节） | 回归风险 |
| Mock 不验证调用参数 | 用 `assert_called_with` 验证 | 假阳性通过 |

### 1.4 安全

| 禁止行为 | 替代方案 | 理由 |
|----------|----------|------|
| 硬编码密钥、API Key、密码 | 通过 `config.py` / 环境变量注入 | 泄露风险 |
| 用户输入直接拼接进 shell/SQL | 参数化查询或白名单校验 | 注入攻击 |
| 用户输入直接用于文件路径 | 校验 `..` 遍历、限制 allowed_prefixes | 路径遍历 |
| 在日志中记录 token / api_key / 密码 | 记录 `key_prefix` 或 `user_id` | 敏感信息泄露 |
| 返回堆栈跟踪给客户端 | 返回通用错误消息，日志记录详情 | 信息泄露 |

### 1.5 配置与耦合

| 禁止行为 | 替代方案 | 理由 |
|----------|----------|------|
| 业务代码中直接 `os.getenv()` | 统一通过 `config.py::Settings` 访问 | 配置分散、难以审计 |
| 硬编码路径、URL、端口号 | 提取为配置项或常量 | 环境差异 |
| 在 API 路由中写长业务逻辑 | 委托给 `service/` 或 `domain/` 层 | 职责分离 |

---

## 2. 必须遵守的强制性规范

### 2.1 文档化要求

- **每个函数**必须有 docstring（至少一行说明用途）。
- **每个 Pydantic 字段**必须有 `Field(description="...")`。
- **复杂逻辑**必须有行内注释解释 **why**（不是 what）。
- **TODO / FIXME** 不允许残留，除非在 `progress.md` 阻塞项中跟踪。

### 2.2 修改后强制验证清单

每次提交代码前，必须完成以下检查：

```markdown
- [ ] `ruff check .` 全部通过（Python 后端）
- [ ] `mypy .` 全部通过（Python 后端）
- [ ] `eslint --ext .ts,.vue src/` 无 error（前端）
- [ ] 新增/修改的 API 已同步更新前端 TypeScript 类型
- [ ] 新增依赖已在 `requirements.txt` / `package.json` 中锁定版本
- [ ] 本地 `docker compose up -d` 验证通过（服务 healthy + 功能可用）
- [ ] 无 `TODO` / `FIXME` 残留（除非已在 progress.md 中跟踪）
```

### 2.3 API 变更同步

- **后端新增/修改 Pydantic 模型** → 必须在 `frontend/src/api/types.ts`（或等价位置）同步类型。
- **新增 SSE 事件类型** → 必须在 `frontend/src/composables/useSSE.ts` 中注册事件名。
- **修改 URL 路径** → 必须检查所有 `api/*.ts` 文件中的调用点。
- **删除字段** → 禁止。可标记为 deprecated，至少保留 1 个 Sprint。

### 2.4 日志与可观测性

- 关键业务事件必须记录 `INFO` 日志（如 Pipeline 启动、阶段完成）。
- 错误路径必须记录 `ERROR` 日志，且含 `exc_info=True`。
- 性能敏感操作（LLM 调用、DB 查询）必须记录耗时（`duration_ms`）。
- 日志中必须绑定上下文标识符（`case_id`, `session_id`, `user_id`）。

---

## 3. 架构与模式约束

### 3.1 后端分层

```
api/route/       → 只做：参数校验、response 组装、调用 service
service/         → 只做：业务逻辑编排、跨域协调
domain/          → 只做：纯业务规则、状态机转换、值对象
integrations/    → 只做：外部 SDK 封装（Claude/OpenAI/Sandbox）
db/              → 只做：数据库连接、索引、迁移
```

**禁止**：
- API 路由直接操作数据库
- API 路由直接调用外部 SDK
- Service 层持有 HTTP 请求对象

### 3.2 前端组件约束

- **状态管理**：使用 Composable 模块级 `ref` 单例（延续 ScienceClaw 模式），**禁止引入 Pinia/Vuex**。
- **API 客户端**：统一使用 `api/client.ts` 导出的 `client` 实例，**禁止直接 `axios.create()`**。
- **SSE 连接**：统一使用 `createSSEConnection()` 工具函数，**禁止直接 `new EventSource()`**。
- **Props 类型**：必须用 `defineProps<{ ... }>()`，禁止 `any`。

### 3.3 Pipeline 节点约束

- 每个节点只关心**本阶段输入输出**，不直接操作 HTTP 对象。
- 节点间数据传递必须通过 `PipelineState`（Pydantic 模型）。
- 节点不允许直接读写 MongoDB——必须通过 `ArtifactManager` / `ReviewService`。
- 节点必须定义：输入契约、输出契约、允许的工具范围、超时与重试策略、产物写入位置、SSE 事件。

---

## 4. TDD 执行协议

### 4.1 后端逻辑

- **必须先写 `test_*.py` 中的失败测试**，才能写 `.py` 实现。
- 测试函数命名：`test_{被测行为}_{条件}_{期望结果}`。
- 单元测试不访问网络、文件系统、数据库（Mock 外部依赖）。
- 集成测试使用 testcontainers 启停真实数据库（不 Mock Mongo/Redis）。

### 4.2 API 端点

- **必须先写 FastAPI `TestClient` 测试**，才能写 `api/*.py` 路由。
- 测试必须覆盖：成功路径、400/401/403/404/409、SSE 事件流。

### 4.3 前端组件

- **复杂组件**必须先写 Vitest/Storybook 测试，才能写 `.vue`。
- Composable 必须先写测试，验证 ref 状态变化逻辑。

### 4.4 重构

- **必须先有覆盖现有行为的测试**，才能改实现。
- 重构 PR 中必须说明：测试如何证明行为未变。

### 4.5 提交前检查

```bash
# Python
ruff check backend/ && mypy backend/ && pytest tests/unit/ -v

# TypeScript/Vue
cd frontend && eslint --ext .ts,.vue src/ && vitest run

# 端到端（若涉及 API 变更）
pytest tests/integration/ -v
```

---

## 5. 与现有规范的优先级关系

```
本 AI 行为契约 > conventions.md > refactor-plan-v3.md > design.md
```

- 若本契约与 `conventions.md` 冲突，以本契约为准（本契约更严格）。
- 若本契约未覆盖，遵循 `conventions.md`。
- 若三者都未覆盖，遵循 `refactor-plan-v3.md`。
- 若都未覆盖，咨询用户或 Oracle。

---

## 6. 违反后果

| 违反级别 | 处理方式 |
|----------|----------|
| 零容忍项（第 1 节） | 立即回滚修改，重新实现 |
| 强制规范未满足（第 2 节） | 标记任务为未完成，补充后重新验收 |
| 架构约束违反（第 3 节） | 要求重构到正确分层 |
| TDD 协议违反（第 4 节） | 补写测试，覆盖率达标后才算完成 |

---

> **本契约自 2026-04-29 起生效。所有 AI 编码活动必须在遵守本契约的前提下进行。**  
> **契约本身的修改需通过人类工程师审批。**
