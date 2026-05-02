# ScienceClaw 重构 — 执行约束

> **用途**: 约束开发过程中的行为边界，防止子 Agent/开发者触碰禁区
> **适用对象**: 所有参与重构的开发者、AI Agent、自动化脚本
> **违反后果**: 代码审查必须打回，已合并的需 revert

---

## 1. 目录与文件约束

### 1.1 只读禁区（READ-ONLY）

以下文件/目录在重构期间 **绝对禁止修改内容**:

| 路径 | 冻结原因 | 解冻条件 |
|------|---------|---------|
| `ScienceClaw/backend/deepagent/*.py` | 保留原始引擎作为后备 | Phase 8 后团队确认删除 |
| `ScienceClaw/frontend/` | 前端零改动是硬性要求 | 项目完全结束且验收通过 |
| `ScienceClaw/backend/route/` | 路由层应通过软链接切换，不改代码 | 项目完全结束 |
| `ScienceClaw/backend/im/` | 飞书集成已工作，不碰 | 项目完全结束 |
| `ScienceClaw/backend/task-service/` | 调度服务应无感知切换 | 项目完全结束 |

### 1.2 写入唯一目标（WRITE-ONLY）

所有新代码、修改、测试 **只能** 写入以下路径：

```
ScienceClaw/backend/clawagent/          # 新引擎核心
ScienceClaw/backend/clawagent/tests/    # 新引擎测试
ScienceClaw/scripts/switch-agent.sh     # 切换脚本
docs/                                   # 文档
tasks/progress-tracking/                # 进度跟踪
```

### 1.3 修改前必须确认（ASK-FIRST）

以下文件如需修改，**必须先经用户/负责人确认**：

| 路径 | 修改影响 | 确认人 |
|------|---------|--------|
| `ScienceClaw/backend/config.py` | 全局配置，影响所有服务 | 架构负责人 |
| `ScienceClaw/docker-compose*.yml` | 部署拓扑变更 | DevOps |
| `ScienceClaw/requirements*.txt` | 依赖变更，可能引入冲突 | 后端负责人 |
| `ScienceClaw/backend/sessions.py` | 会话数据结构，影响数据持久化 | 后端负责人 |
| `ScienceClaw/backend/sse_protocol.py` | SSE 协议，影响前端 | 前端 + 后端负责人 |

---

## 2. 代码行为约束

### 2.1 禁止行为（FORBIDDEN）

以下行为在任何情况下都 **禁止**：

| # | 禁止行为 | 原因 | 替代方案 |
|---|---------|------|---------|
| F1 | 使用 `as any` / `@ts-ignore` / `@ts-expect-error` 抑制类型错误 | 隐藏真正的类型问题 | 修复类型定义或调整接口 |
| F2 | 删除失败的测试以"通过" | 自欺欺人 | 修复被测代码或修正测试 |
| F3 | 在 `deepagent/` 目录内修改任何文件 | 冻结规则 | 在 `clawagent/` 修改 |
| F4 | 修改前端代码以适应新引擎 | 前端零改动原则 | 调整后端 SSE 输出格式 |
| F5 | 引入新的重量级框架（>5MB） | 保持精简 | 优先使用标准库或 SDK 原生功能 |
| F6 | 使用全局可变状态（模块级 dict/list）存储会话数据 | 竞态条件（痛点#5） | 使用函数参数或类实例 |
| F7 | 在同步函数中调用 `asyncio.run()` | async bridge hack（痛点#4） | 统一为 async，或使用线程池（经审批） |
| F8 | 直接调用 `langchain-openai` 内部 API（下划线开头函数） | monkey-patch 风险（痛点#3） | 使用 SDK 原生机制或公开 API |

### 2.2 必须行为（REQUIRED）

以下行为在对应场景下 **必须执行**：

| # | 必须行为 | 触发场景 | 验证方式 |
|---|---------|---------|---------|
| R1 | 每次文件编辑后运行 `lsp_diagnostics` | 任何 `.py` 文件修改 | 无 error 才可标记完成 |
| R2 | 每次任务完成后更新 `progress.md` 状态 | 任何任务标记完成 | 实际工时字段非空 |
| R3 | 新建文件必须包含模块级 docstring | 任何 `.py` 新文件 | 代码审查检查 |
| R4 | 工具函数必须保留原有 `@tool` 装饰器（或迁移到 `@claw_tool`） | P5-T10 之前 | 装饰器存在 |
| R5 | `claw_agent()` 返回值必须保持 `(client, middleware, context_window, diagnostic)` 元组 | P2-T4 | 单元测试断言 |
| R6 | SSE 事件输出必须经过对比测试验证 | P3-T5-8 | 对比脚本通过 |
| R7 | 危险工具调用（Bash/Execute）必须经过 `PreToolUse` Hook | P5-T6 之后 | Hooks 单元测试 |

---

## 3. 接口契约约束

### 3.1 `AgentEngine` ABC（冻结）

```python
from abc import ABC, abstractmethod
from typing import AsyncIterator, Any, Tuple

class AgentEngine(ABC):
    """Agent 引擎抽象基类 — 所有实现必须遵循此契约。"""
    
    @abstractmethod
    async def create_agent(
        self,
        session_id: str,
        model_config: dict | None = None,
        user_id: str | None = None,
        task_settings: Any | None = None,
        diagnostic_enabled: bool = False,
        language: str | None = None,
    ) -> Tuple[Any, Any, int, Any]:
        """创建 Agent 实例。
        
        Returns:
            (agent_instance, middleware, context_window, diagnostic)
            agent_instance: 可调用流式执行的对象
            middleware: 事件监控中间件（含 drain_events）
            context_window: 模型上下文窗口大小（int）
            diagnostic: 诊断日志器或 None
        """
        ...
    
    @abstractmethod
    async def stream(
        self,
        session: Any,
        query: str,
        history: list | None = None,
        attachments: list | None = None,
    ) -> AsyncIterator[dict]:
        """SSE 流式执行。
        
        Yields:
            dict: {"event": str, "data": dict} — 格式必须与旧版 100% 一致
        """
        ...
    
    @abstractmethod
    def get_tool_event_adapter(self) -> Any:
        """返回工具事件适配器，用于统一不同引擎的事件格式。"""
        ...
```

### 3.2 契约变更流程

此契约 **冻结后不得修改**。如需变更：
1. 在 `adr.md` 中提交新的 ADR
2. 修改所有已实现引擎（`DeepAgentEngine` + `ClaudeAgentEngine`）
3. 更新本文件并标注变更版本

---

## 4. 测试约束

### 4.1 覆盖率红线

| 层级 | 最低覆盖率 | 测量工具 |
|------|-----------|---------|
| 单元测试 | 80% | pytest --cov |
| 新建文件 | 100% | pytest --cov |
| 引擎切换逻辑 | 100% | pytest --cov |
| SSE 事件对比 | 100% 场景覆盖 | 自定义对比脚本 |

### 4.2 测试必须覆盖的边界

以下场景 **必须有测试**，否则视为未完成任务：

- [ ] 空查询（query=""）
- [ ] 超长查询（>4000 字符）
- [ ] 工具调用失败（网络超时 / 参数错误）
- [ ] 工具调用返回空结果
- [ ] 会话中途取消
- [ ] 引擎切换过程中收到请求
- [ ] 并发 10+ 会话同时创建 Agent
- [ ] 历史消息超过 token budget

---

## 5. 提交与审查约束

### 5.1 提交信息规范

```
[<Phase>-<Task>] <type>: <description>

<body>

Refs: P2-T4-9, P3-T1-7
```

| Type | 用途 |
|------|------|
| `feat` | 新功能 |
| `refactor` | 重构（无功能变更） |
| `fix` | Bug 修复 |
| `test` | 测试补充 |
| `docs` | 文档更新 |
| `chore` | 配置/脚本调整 |

示例：
```
[P2-T4] feat: implement ClaudeSDKClient creation in claw_agent()

- Integrate tool converter for @tool → SDK format
- Attach SSEMonitoringMiddleware via MiddlewareStack
- Register all tools including subagent Task tools

Refs: P2-T4-9, P2-T2-1
```

### 5.2 审查清单（Reviewer 必须逐项勾选）

```markdown
## 审查清单

### 行为约束
- [ ] 未修改 `deepagent/` 任何文件
- [ ] 未修改 `frontend/` 任何文件
- [ ] 无 `as any` / `@ts-ignore` 类型压制
- [ ] 无删除测试以"通过"的行为
- [ ] 无全局可变状态（模块级 dict/list 存会话数据）

### 接口契约
- [ ] `AgentEngine` ABC 未被修改（除非有 ADR 变更）
- [ ] `claw_agent()` 返回值保持 `(client, middleware, cw, diag)` 元组
- [ ] SSE 事件格式与旧版一致（对比测试通过）

### 测试
- [ ] 新增文件覆盖率 >= 80%
- [ ] 所有边界场景有测试
- [ ] `lsp_diagnostics` 无 error

### 文档
- [ ] 复杂逻辑有注释说明
- [ ] `progress.md` 已更新（如适用）
```

---

## 6. 子 Agent / AI 开发特别约束

当本项目的开发工作由 AI Agent（如 Sisyphus）执行时，适用以下额外约束：

### 6.1 自主权限边界

| 操作 | 自主执行 | 需用户确认 |
|------|---------|-----------|
| 在 `clawagent/` 内新建文件 | ✅ | — |
| 在 `clawagent/` 内修改文件 | ✅ | — |
| 在 `clawagent/` 内删除文件 | ✅ | — |
| 运行测试 | ✅ | — |
| 修改 `progress.md` | ✅ | — |
| 修改 `deepagent/` | ❌ 绝对禁止 | N/A |
| 修改 `frontend/` | ❌ 绝对禁止 | N/A |
| 修改 `config.py` | ❌ | 必须确认 |
| 修改 `requirements.txt` | ❌ | 必须确认 |
| 执行 `git commit` | ❌ | 用户明确请求 |
| 执行 `git push` | ❌ | 用户明确请求 |
| 引入新依赖 | ❌ | 必须确认 |

### 6.2 上下文保持约束

AI Agent 在执行多步骤任务时：
- 必须在每轮对话开始时读取 `progress.md` 确认当前状态
- 必须读取 `constraints.md` 确认行为边界
- 遇到与已有 ADR 冲突的需求时，**停止执行并报告**，不得擅自修改 ADR

### 6.3 失败恢复约束

若 AI Agent 的修改导致测试失败或构建失败：
1. **立即停止**新增改动
2. 分析失败根因
3. 修复失败（优先）或回滚到上一已知可用状态
4. 在 `progress.md` 对应任务备注栏记录失败原因
5. 连续 3 次修复失败后，**必须停止并请求人类介入**

---

## 7. 约束版本

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-05-02 | 初始创建 |

---

> **使用方法**: 每位开发者在开始工作前阅读本文件。代码审查时审查者逐条核对。
