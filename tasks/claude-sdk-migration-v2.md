# ScienceClaw 底层框架迁移方案：DeepAgents → Claude Agent SDK

> **版本**: v2.0（聚焦保留业务逻辑 + 替换底层框架）
> **日期**: 2026-05-02
> **状态**: 设计方案
> **范围**: `ScienceClaw/backend/deepagent/` → `ScienceClaw/backend/clawagent/`

---

## 核心决策

| 决策项 | 结论 |
|--------|------|
| **底层框架** | `deepagents==0.4.4` + `langgraph==1.0.8` → `claude-agent-sdk` |
| **业务逻辑** | **保留**：runner 流式架构、SSE 事件格式、Sessions、Tools、Skills、Sandbox |
| **目录重命名** | `deepagent/` → **`clawagent/`** |
| **模块重命名** | `backend.deepagent.*` → `backend.clawagent.*` |
| **多模型支持** | 保留 `engine.py` 模型工厂，Claude SDK 通过自定义 base_url 支持 OpenAI 兼容模型 |
| **LangChain 工具** | `@tool` 装饰器保留（独立于 LangGraph），或迁移为 SDK 原生工具格式 |

---

## 1. 依赖范围精确分析

### 1.1 deepagents / langgraph 直接引用清单

在 `ScienceClaw/backend/` 中，`deepagents` 和 `langgraph` 的直接引用共 **12 处**，分布在 **6 个文件**中：

```
ScienceClaw/backend/
├── requirements.txt                          # 2 处：deepagents==0.4.4, langgraph==1.0.8
├── deepagent/
│   ├── agent.py                              # 4 处：create_deep_agent, CompositeBackend, FilesystemBackend, GENERAL_PURPOSE_SUBAGENT
│   ├── runner.py                             # 2 处：agent.astream(), langgraph_node metadata
│   ├── sse_middleware.py                     # 1 处：AgentMiddleware (langchain.agents.middleware)
│   ├── offload_middleware.py                 # 1 处：AgentMiddleware (langchain.agents.middleware)
│   ├── filtered_backend.py                   # 1 处：FilesystemBackend (deepagents.backends)
│   └── full_sandbox_backend.py               # 1 处：FileOperation (deepagents.backends.protocol)
```

**零引用的文件**（完全无需改动，仅重命名 import）：
- `engine.py` — 模型工厂，仅使用 `langchain_openai.ChatOpenAI`，不依赖 LangGraph
- `tools.py` — 工具定义，使用 `langchain_core.tools.tool`，不依赖 DeepAgents
- `tooluniverse_tools.py` — 同样的 `@tool` 装饰器
- `sessions.py` — 纯业务逻辑，零框架依赖
- `sse_protocol.py` — 协议定义，零框架依赖
- `diagnostic.py` — 诊断日志，仅依赖 `langchain_core.messages`
- `dir_watcher.py` — 目录监听，零框架依赖
- `plan_types.py` — 类型定义，零框架依赖

### 1.2 依赖类型分类

| 类型 | 说明 | 涉及文件 | 处理策略 |
|------|------|----------|----------|
| **Agent 工厂** | `create_deep_agent()` 组装模型+工具+中间件 | `agent.py` | **重写**：用 `ClaudeSDKClient` 替代 |
| **流式执行** | `agent.astream(stream_mode=["messages", "updates"])` | `runner.py` | **重写**：适配 SDK 流式输出 |
| **中间件基类** | `AgentMiddleware` 提供 `wrap_tool_call` 钩子 | `sse_middleware.py`, `offload_middleware.py` | **替换**：自定义中间件基类 |
| **Backend 基类** | `FilesystemBackend`, `CompositeBackend` | `filtered_backend.py`, `full_sandbox_backend.py`, `agent.py` | **保留逻辑**：替换基类为自建类 |
| **协议类型** | `FileOperation` 等类型定义 | `full_sandbox_backend.py` | **内联**：复制类型定义 |
| **子 Agent** | `GENERAL_PURPOSE_SUBAGENT`, `DEFAULT_SUBAGENT_PROMPT` | `agent.py` | **替换**：SDK `Task` 工具 |

---

## 2. 文件级迁移策略

### 2.1 保留级（重命名 import 即可）

这些文件的业务逻辑完全独立于 DeepAgents/LangGraph，只需更新 import 路径。

| 文件 | 行数 | 当前 import 路径 | 新 import 路径 |
|------|------|-----------------|---------------|
| `engine.py` | 450 | `backend.deepagent.engine` | `backend.clawagent.engine` |
| `tools.py` | 481 | `backend.deepagent.tools` | `backend.clawagent.tools` |
| `tooluniverse_tools.py` | 141 | `backend.deepagent.tooluniverse_tools` | `backend.clawagent.tooluniverse_tools` |
| `sessions.py` | 343 | `backend.deepagent.sessions` | `backend.clawagent.sessions` |
| `sse_protocol.py` | 239 | `backend.deepagent.sse_protocol` | `backend.clawagent.sse_protocol` |
| `diagnostic.py` | 255 | `backend.deepagent.diagnostic` | `backend.clawagent.diagnostic` |
| `dir_watcher.py` | 72 | `backend.deepagent.dir_watcher` | `backend.clawagent.dir_watcher` |
| `plan_types.py` | 38 | `backend.deepagent.plan_types` | `backend.clawagent.plan_types` |

**全局替换命令：**
```bash
find ScienceClaw/backend -type f -name "*.py" -exec \
  sed -i '' 's/backend\.deepagent\./backend.clawagent./g' {} +
```

### 2.2 适配级（中等改动）

| 文件 | 改动点 | 策略 |
|------|--------|------|
| `engine.py` | `langchain_openai.ChatOpenAI` 保留可用，但需确认 SDK 的模型创建方式 | 保留现有模型工厂，Claude SDK 通过 `base_url` 使用兼容模型 |
| `runner.py` | `agent.astream()` 循环 → SDK 流式输出；`langgraph_node` metadata 移除 | 重写流式循环，保持 SSE 事件生成逻辑不变 |
| `tools.py` | `langchain_core.tools.tool` 装饰器 | 可选保留（与 SDK 工具格式不冲突），或迁移为纯函数工具 |

### 2.3 重写级（核心改动）

| 文件 | 行数 | 重写范围 | 估计工作量 |
|------|------|----------|-----------|
| `agent.py` | 586 | `create_deep_agent()` → `ClaudeSDKClient`；Backend 组装逻辑 | 高 |
| `sse_middleware.py` | 393 | 移除 `AgentMiddleware` 继承，保留 `wrap_tool_call` 机制 | 中 |
| `offload_middleware.py` | 174 | 同上 | 低 |
| `filtered_backend.py` | 128 | 替换 `FilesystemBackend` 基类 | 中 |
| `full_sandbox_backend.py` | 576 | 替换 `FileOperation` 协议类型 | 中 |

---

## 3. 核心模块重写设计

### 3.1 agent.py — Agent 组装器重写

**当前核心逻辑（需替换）：**
```python
# 当前：deepagents 入口
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, FilesystemBackend

agent = create_deep_agent(
    model=model,
    tools=tools,
    middleware=[sse_middleware, offload_middleware],
    system_prompt=system_prompt,
)
```

**新设计：ClaudeSDKClient 组装器**
```python
# backend/clawagent/agent.py
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

async def claw_agent(
    session_id: str,
    model_config: dict | None = None,
    user_id: str | None = None,
    task_settings: TaskSettings | None = None,
    diagnostic_enabled: bool = False,
    language: str | None = None,
):
    """组装 ClawAgent：模型 + 工具 + 中间件 + Skills。

    职责与原来的 deep_agent() 完全一致：
      1. 根据 model_config 创建 LLM 模型（复用 engine.py）
      2. 收集所有工具（内置 + 外部扩展）
      3. 组装 Backend（Sandbox + Skills 路由）
      4. 创建 SSEMonitoringMiddleware（工具拦截）
      5. 创建 ToolResultOffloadMiddleware（大结果落盘）
      6. 返回 (client, middleware, context_window, diagnostic)
    """
    # 1. 模型（复用现有 engine.py）
    model = get_llm_model(model_config)
    context_window = _get_context_window(model_config)

    # 2. 工具（复用现有 _collect_tools）
    blocked_tools = await get_blocked_tools(user_id) if user_id else set()
    tools = _collect_tools(blocked_tools)

    # 3. 系统提示词（复用现有 get_system_prompt）
    workspace_dir = f"/home/scienceclaw/{session_id}"
    system_prompt = get_system_prompt(workspace_dir, language=language)

    # 4. Backend（替换 CompositeBackend，保留路由逻辑）
    sandbox = FullSandboxBackend(workspace_dir=workspace_dir)
    backend = _build_backend(session_id, sandbox, blocked_skills=...)

    # 5. 中间件（替换 AgentMiddleware 基类）
    sse_middleware = SSEMonitoringMiddleware(agent_name="ClawAgent")
    offload_middleware = ToolResultOffloadMiddleware(workspace_dir, backend)

    # 6. 创建 Claude SDK Client
    # 关键：将 tools 转换为 SDK 工具格式
    sdk_tools = _convert_to_sdk_tools(tools, backend, sse_middleware, offload_middleware)

    client = ClaudeSDKClient(
        options=ClaudeAgentOptions(
            allowed_tools=[t.name for t in sdk_tools],
            max_tokens=task_settings.max_tokens if task_settings else 8192,
        )
    )

    # 7. 诊断（复用现有）
    diagnostic = DiagnosticLogger(session_id) if diagnostic_enabled else None

    return client, sse_middleware, context_window, diagnostic
```

**关键变化说明：**

| 原实现 | 新实现 | 说明 |
|--------|--------|------|
| `create_deep_agent(model, tools, middleware, system_prompt)` | `ClaudeSDKClient(options=...)` | SDK 不直接接受模型实例，而是内部管理 |
| `middleware=[...]` 注入 | 工具包装器模式 | SDK 无原生中间件，通过包装工具函数实现拦截 |
| `CompositeBackend` | 自定义 `_build_backend` | 保留路由逻辑，移除 deepagents 基类依赖 |
| `GENERAL_PURPOSE_SUBAGENT` | SDK `Task` 工具 | 功能等价 |

### 3.2 runner.py — 流式执行器重写给

**当前核心循环（需替换）：**
```python
# 当前：LangGraph astream
async for stream_event in agent.astream(
    input_messages,
    stream_mode=["messages", "updates"],
    config={"configurable": {"thread_id": session.thread_id}},
):
    stream_type, stream_data = stream_event
    # messages 模式：逐 token 输出
    # updates 模式：完整节点输出（工具调用）
```

**新设计：SDK 流式循环**
```python
# backend/clawagent/runner.py
async def arun_science_task_stream(session, query, history, ...):
    """SSE 流式执行器 — 保持与当前完全相同的 SSE 事件输出格式。

    仅底层执行从 LangGraph astream 替换为 Claude SDK 流式调用。
    """
    client, middleware, context_window, diagnostic = await claw_agent(...)
    middleware.clear()

    # ---- 保持完全相同的初始事件序列 ----
    yield {"event": "thinking", "data": {"content": ""}}
    plan = _build_plan(query[:200])
    step = plan[0]
    yield {"event": "step_start", "data": {"step": step}}
    plan = normalize_plan_steps([{**step, "status": "in_progress"}])
    yield {"event": "plan_update", "data": {"plan": _plan_for_frontend(plan)}}

    # ---- 构建消息（与当前完全一致）----
    history_messages = _build_history_messages(session, current_query=query, ...)
    input_messages = history_messages + [{"role": "user", "content": enriched_query}]

    # ---- 流式执行（核心替换点）----
    # 原：LangGraph astream
    # 新：Claude SDK query with streaming
    try:
        async with asyncio.timeout(STREAM_TIMEOUT):
            # SDK 流式调用
            stream = await client.query(
                prompt=enriched_query,
                context={
                    "system_prompt": system_prompt,
                    "history": input_messages,
                    "workspace_dir": session.vm_root_dir,
                }
            )

            final_content = ""
            _current_todos = []

            async for msg in stream:
                # ── 每次迭代轮询中间件事件（保持现有逻辑）──
                for mw_evt in middleware.drain_events():
                    # ... 与当前 runner.py 完全相同的处理逻辑 ...
                    yield mw_evt

                # ── 处理 SDK 消息类型 ──
                msg_type = msg.get("type")

                if msg_type == "text":
                    # 对应原 messages 模式的 AIMessageChunk
                    token_text = msg.get("content", "")
                    if token_text:
                        final_content += token_text
                        yield {"event": "thinking", "data": {"content": token_text}}

                elif msg_type == "tool_use":
                    # 对应原 updates 模式的 tool_calls
                    tool_name = msg.get("name", "")
                    tool_args = msg.get("input", {})
                    tool_call_id = msg.get("id", "")

                    # 触发中间件 start 事件
                    middleware._before_tool({
                        "tool_call": {"name": tool_name, "id": tool_call_id, "arguments": tool_args}
                    })

                    # 执行工具（SDK 内部执行，但我们需要拦截）
                    # ...

                    # 触发中间件 complete 事件
                    middleware._after_tool(result, tool_name, tool_args, tool_call_id, start_time, tool_meta)

                elif msg_type == "thinking":
                    # 对应原 reasoning_content
                    yield {"event": "thinking", "data": {"content": msg.get("thinking", "")}}

            # ---- 发送最终消息（与当前完全一致）----
            yield {
                "event": "message",
                "data": {
                    "role": "assistant",
                    "content": final_content,
                    # ... 保持与当前相同的字段
                },
            }

    except asyncio.TimeoutError:
        yield {"event": "error", "data": {"message": "Agent stream timeout"}}
```

**runner.py 改动范围评估：**
- 保留（无需改动）：`~60%`
  - 初始事件序列（thinking, step_start, plan_update）
  - 历史消息构建（`_build_history_messages`）
  - 附件处理
  - Token 预算计算
  - 超时处理
  - 最终消息格式化
  - Session 状态更新
- 重写（核心替换）：`~30%`
  - `agent.astream()` → `client.query()` 流式调用
  - `stream_type == "messages"` → `msg_type == "text"`
  - `stream_type == "updates"` → `msg_type == "tool_use"`
  - `AIMessageChunk` 处理 → SDK message 处理
- 移除（LangGraph 特有）：`~10%`
  - `langgraph_node` metadata 检查
  - `stream_mode=["messages", "updates"]` 双模式逻辑
  - `configurable={"thread_id": ...}` 配置

### 3.3 中间件重写 — 移除 AgentMiddleware 基类

**当前问题：**
```python
from langchain.agents.middleware import AgentMiddleware

class SSEMonitoringMiddleware(AgentMiddleware):
    def wrap_tool_call(self, request, handler):
        # ...
```

**新设计：自定义中间件基类**
```python
# backend/clawagent/middleware_base.py
"""自定义中间件基类 — 替代 langchain.agents.middleware.AgentMiddleware

职责与 AgentMiddleware 完全一致：
  - 提供 wrap_tool_call 钩子，拦截工具执行前后
  - 支持 sync / async 两种模式

区别：
  - 不依赖任何外部框架
  - 纯 Python 实现
"""
from typing import Any, Callable


class ClawMiddleware:
    """中间件基类 — 工具调用拦截"""

    def wrap_tool_call(self, request: Any, handler: Callable[[Any], Any]) -> Any:
        """同步工具拦截（默认直接透传）"""
        return handler(request)

    async def awrap_tool_call(self, request: Any, handler: Callable[[Any], Any]) -> Any:
        """异步工具拦截（默认直接透传）"""
        return await handler(request)


class MiddlewareStack:
    """中间件栈 — 依次调用多个中间件"""

    def __init__(self, middlewares: list[ClawMiddleware]):
        self.middlewares = middlewares

    def run(self, request: Any, final_handler: Callable) -> Any:
        """按顺序执行中间件链"""
        handler = final_handler
        for mw in reversed(self.middlewares):
            handler = lambda req, h=handler, m=mw: m.wrap_tool_call(req, h)
        return handler(request)
```

**SSEMonitoringMiddleware 迁移：**
```python
# backend/clawagent/sse_middleware.py
from backend.clawagent.middleware_base import ClawMiddleware

class SSEMonitoringMiddleware(ClawMiddleware):
    """SSE 监控中间件 — 与当前实现 95% 相同，仅基类变更"""

    def __init__(self, agent_name: str = "agent", ...):
        # 不需要 super().__init__()（AgentMiddleware 的初始化）
        self.agent_name = agent_name
        # ... 其余与当前完全一致 ...

    def wrap_tool_call(self, request, handler):
        """与当前实现完全一致"""
        tool_name, tool_args, tool_call_id, start_time, tool_meta = self._before_tool(request)
        result = handler(request)
        return self._after_tool(result, tool_name, tool_args, tool_call_id, start_time, tool_meta)
```

**改动量评估：**
- `sse_middleware.py`：仅 import 和 class 声明变更（`AgentMiddleware` → `ClawMiddleware`），业务逻辑 100% 保留
- `offload_middleware.py`：同上

### 3.4 Backend 重写 — 移除 deepagents 基类

**当前依赖：**
```python
from deepagents.backends.filesystem import FilesystemBackend
from deepagents.backends.protocol import FileOperation, FileRead, FileWrite, ...
```

**新设计：自建 Backend 协议**
```python
# backend/clawagent/backend_protocol.py
"""文件系统操作协议 — 替代 deepagents.backends.protocol"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class FileOperation:
    path: str
    content: Optional[str] = None

@dataclass
class FileRead(FileOperation):
    pass

@dataclass
class FileWrite(FileOperation):
    pass

@dataclass
class FileEdit(FileOperation):
    old_string: Optional[str] = None
    new_string: Optional[str] = None

@dataclass
class FileList(FileOperation):
    recursive: bool = False

@dataclass
class FileGlob(FileOperation):
    pattern: str = ""

@dataclass
class FileGrep(FileOperation):
    pattern: str = ""


class FilesystemBackend:
    """文件系统后端 — 替代 deepagents.backends.filesystem.FilesystemBackend

    保留所有方法签名与当前一致，内部实现直接调用 os/pathlib。
    """
    def __init__(self, root_dir: str, virtual_mode: bool = True):
        self.root_dir = root_dir
        self.virtual_mode = virtual_mode

    def read(self, op: FileRead) -> str:
        ...

    def write(self, op: FileWrite) -> None:
        ...

    def edit(self, op: FileEdit) -> None:
        ...

    def ls(self, op: FileList) -> list[dict]:
        ...

    def glob(self, op: FileGlob) -> list[str]:
        ...

    def grep(self, op: FileGrep) -> list[dict]:
        ...
```

**改动量评估：**
- `filtered_backend.py`：仅 import 变更，`FilesystemBackend` 基类替换为自建类
- `full_sandbox_backend.py`：移除 `FileOperation` 等类型的 deepagents import，使用自建协议
- `agent.py` 中的 `CompositeBackend`：保留路由逻辑，用自建类替代

---

## 4. 工具迁移策略

### 4.1 当前工具格式

当前工具使用 `langchain_core.tools.tool` 装饰器：
```python
from langchain_core.tools import tool

@tool
def web_search(queries: str) -> dict:
    """Search the internet..."""
    ...
```

这**不依赖** DeepAgents 或 LangGraph，仅依赖 `langchain-core`。有两种策略：

**策略 A：保留 LangChain @tool（推荐）**
- 保留 `langchain-core` 作为依赖（轻量级）
- `@tool` 装饰器提供 schema 提取和类型验证
- 在 agent.py 中将 LangChain 工具转换为 Claude SDK 工具格式

**策略 B：迁移为纯函数**
- 移除 `langchain-core` 依赖
- 工具改为普通函数
- 手动维护参数 schema（JSON Schema）

### 4.2 工具转换层

```python
# backend/clawagent/tool_converter.py
from langchain_core.tools import BaseTool
from claude_agent_sdk.tools import Tool as SDKTool

def convert_langchain_tool_to_sdk(lc_tool: BaseTool) -> SDKTool:
    """将 LangChain 工具转换为 Claude SDK 工具格式"""
    return SDKTool(
        name=lc_tool.name,
        description=lc_tool.description,
        parameters=lc_tool.args_schema.model_json_schema() if lc_tool.args_schema else {},
        handler=lambda **kwargs: lc_tool.invoke(kwargs),
    )
```

---

## 5. 详细实施计划（聚焦框架替换）

### Phase 0: 准备工作（Week 1）

- [ ] 全局替换 `backend.deepagent.` → `backend.clawagent.`（所有 import 路径）
- [ ] 重命名目录 `deepagent/` → `clawagent/`
- [ ] 更新 `requirements.txt`：移除 `deepagents`, `langgraph`；添加 `claude-agent-sdk`
- [ ] 验证后端能正常启动（此时仍使用 DeepAgents，因为 agent.py 尚未重写）

### Phase 1: 基础设施（Week 1-2）

- [ ] 创建 `middleware_base.py` — 自建中间件基类
- [ ] 创建 `backend_protocol.py` — 自建文件系统协议
- [ ] 重写 `filtered_backend.py` — 替换 `FilesystemBackend` 基类
- [ ] 重写 `full_sandbox_backend.py` — 替换协议类型 import
- [ ] 适配 `sse_middleware.py` — 更换基类，验证工具拦截正常
- [ ] 适配 `offload_middleware.py` — 更换基类，验证大结果落盘正常

### Phase 2: Agent 核心重写（Week 3-4）

- [ ] 重写 `agent.py`：
  - [ ] 移除 `create_deep_agent` → `ClaudeSDKClient`
  - [ ] 移除 `CompositeBackend` → 自定义 Backend 组装
  - [ ] 移除 `GENERAL_PURPOSE_SUBAGENT` → SDK `Task` 工具
  - [ ] 工具转换层：`@tool` → SDK Tool 格式
  - [ ] 保持 `_collect_tools`, `get_system_prompt` 等逻辑不变
- [ ] 重写 `runner.py` 核心循环：
  - [ ] `agent.astream()` → `client.query()` 流式调用
  - [ ] 适配 SDK 消息类型到现有 SSE 事件格式
  - [ ] 保持所有现有事件类型：`thinking`, `tool_call_start`, `tool_call_end`, `plan_update`, `message`, `error`
- [ ] 验证单次对话正常（文本输出 + 工具调用）

### Phase 3: 功能补齐（Week 5-6）

- [ ] 子 Agent 支持（SDK `Task` 工具）
- [ ] 思考内容提取（DeepSeek/Claude 格式）
- [ ] Token 统计（输入/输出/思考）
- [ ] 历史消息压缩（替代 SummarizationMiddleware）
- [ ] 多模型支持（通过 SDK `base_url` 配置）
- [ ] 诊断日志集成

### Phase 4: 回归测试（Week 7-8）

- [ ] 所有内置工具功能验证
- [ ] Skills 系统验证（内置 + 外置）
- [ ] ToolUniverse 1900+ 工具验证
- [ ] Sandbox 代码执行验证
- [ ] SSE 事件流对比测试（与旧版本输出一致）
- [ ] 压力测试（并发会话）
- [ ] 飞书/IM 集成验证

---

## 6. 风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| **SDK 流式输出格式不稳定** | 高 | 抽象 `SDKMessageAdapter` 隔离格式差异 |
| **SummarizationMiddleware 缺失** | 中 | 自行实现历史压缩（基于 token 计数）或保留 langchain-core 的 token 计算 |
| **工具拦截机制差异** | 中 | 通过 `ClawMiddleware` 基类统一拦截，SDK 工具执行前后插入钩子 |
| **多模型兼容性** | 中 | Claude SDK 支持自定义 `base_url`，可对接 OpenAI 兼容模型；非兼容模型回退到现有 engine |
| **Sub-agent 行为差异** | 低 | SDK `Task` 工具功能更强，可能超越而非缺失 |
| **性能回退** | 中 | 基准测试对比，必要时优化连接池和缓存 |

---

## 7. 成本估算

| 阶段 | 工时 | 说明 |
|------|------|------|
| Phase 0: 准备 | 8h | 全局重命名 + 目录迁移 + requirements 更新 |
| Phase 1: 基础设施 | 24h | 中间件基类 + Backend 协议 + 现有文件适配 |
| Phase 2: Agent 核心 | 40h | agent.py + runner.py 重写（核心工作量） |
| Phase 3: 功能补齐 | 24h | 子 Agent + 思考提取 + 历史压缩 |
| Phase 4: 回归测试 | 24h | 全功能验证 + 性能对比 |
| **总计** | **~120h** | **约 3 周（1 人全职）** |

相比 v1.0 方案（13 周/360h），v2.0 聚焦框架替换，**工作量减少约 67%**，因为业务逻辑层（sessions, tools, protocol, diagnostic）几乎无需改动。

---

## 8. 新旧架构对比

```
当前架构（DeepAgents）                        目标架构（Claude SDK）
┌─────────────────────────┐                 ┌─────────────────────────┐
│  create_deep_agent()    │                 │  ClaudeSDKClient()      │
│  ├─ model (LangChain)   │                 │  ├─ model via API       │
│  ├─ tools (@tool)       │    ────►        │  ├─ tools (SDK format)  │
│  ├─ middleware [...]    │                 │  ├─ middleware [...]    │
│  └─ system_prompt       │                 │  └─ system_prompt       │
├─────────────────────────┤                 ├─────────────────────────┤
│  agent.astream()        │                 │  client.query()         │
│  ├─ stream_mode=messages│    ────►        │  ├─ streaming text      │
│  ├─ stream_mode=updates │                 │  ├─ tool_use events     │
│  └─ config=thread_id    │                 │  └─ thinking blocks     │
├─────────────────────────┤                 ├─────────────────────────┤
│  AgentMiddleware        │                 │  ClawMiddleware         │
│  (langchain.agents)     │    ────►        │  (自建，无外部依赖)      │
│  └─ wrap_tool_call()    │                 │  └─ wrap_tool_call()    │
├─────────────────────────┤                 ├─────────────────────────┤
│  CompositeBackend       │                 │  _build_backend()       │
│  (deepagents.backends)  │    ────►        │  (自建，保留路由逻辑)     │
│  ├─ default=sandbox     │                 │  ├─ default=sandbox     │
│  └─ routes=skills       │                 │  └─ routes=skills       │
├─────────────────────────┤                 ├─────────────────────────┤
│  Sessions               │                 │  Sessions               │
│  Tools                  │    ────►        │  Tools                  │
│  SSE Protocol           │    保留         │  SSE Protocol           │
│  Diagnostic             │                 │  Diagnostic             │
└─────────────────────────┘                 └─────────────────────────┘
```

**关键结论：**
- **上层业务逻辑 100% 保留**（Sessions, Tools, Protocol, Diagnostic, 路由层）
- **中层执行框架 100% 替换**（Agent 工厂 + 流式循环）
- **底层基础设施 90% 保留**（Backend 路由逻辑、中间件拦截逻辑、文件系统操作）
- **仅基类/协议层 10% 重写**（移除 deepagents 基类依赖，替换为自建实现）

---

## 9. 迁移检查清单

### 代码迁移
- [ ] 全局替换 `backend.deepagent.` → `backend.clawagent.`
- [ ] 重命名目录 `deepagent/` → `clawagent/`
- [ ] 更新 `requirements.txt`
- [ ] 创建 `middleware_base.py`
- [ ] 创建 `backend_protocol.py`
- [ ] 重写 `agent.py`（`create_deep_agent` → `ClaudeSDKClient`）
- [ ] 重写 `runner.py` 核心流式循环
- [ ] 适配 `sse_middleware.py` 基类
- [ ] 适配 `offload_middleware.py` 基类
- [ ] 适配 `filtered_backend.py` 基类
- [ ] 适配 `full_sandbox_backend.py` 协议类型

### 功能验证
- [ ] 文本对话正常输出
- [ ] 工具调用前后事件正确（SSE）
- [ ] web_search / web_crawl 正常
- [ ] read_file / write_file / edit_file 正常
- [ ] execute / bash 正常
- [ ] ToolUniverse 工具正常
- [ ] Skills 加载与执行正常
- [ ] Sandbox 隔离执行正常
- [ ] 子 Agent 调用正常
- [ ] 思考内容提取正常
- [ ] Token 统计正常
- [ ] 大结果自动落盘正常
- [ ] 会话持久化正常
- [ ] 飞书/IM 集成正常

---

---

## 附录 A：单个文件伪代码详细设计

> 以下伪代码仅用于规划阶段，描述目标状态，**不修改实际仓库代码**。

### A.1 agent.py — Agent 组装器

**当前核心结构（需保留的业务逻辑）：**
```python
# 保留（零改动）：
# - _SYSTEM_PROMPT_TEMPLATE / _EVAL_SYSTEM_PROMPT_TEMPLATE
# - get_system_prompt() / _get_eval_system_prompt()
# - _LANGUAGE_MAP
# - _collect_tools() — 工具收集
# - get_blocked_skills() / get_blocked_tools() — MongoDB 查询
# - _build_backend() — Backend 路由组装

# 重写（框架替换）：
# - deep_agent() 函数 — 组装 Agent
# - deep_agent_eval() 函数 — Eval Agent
```

**目标伪代码：**
```python
# backend/clawagent/agent.py
"""组装 ClawAgent：系统提示词 + 模型 + 工具 + Skills + 监控中间件。

与原来 deepagents 版本职责完全一致，仅底层框架替换为 Claude SDK。
"""
from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from loguru import logger
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

from backend.clawagent.engine import get_llm_model
from backend.clawagent.tools import web_search, web_crawl, propose_skill_save, propose_tool_save, eval_skill, grade_eval
from backend.clawagent.tooluniverse_tools import tooluniverse_search, tooluniverse_info, tooluniverse_run
from backend.clawagent.full_sandbox_backend import FullSandboxBackend
from backend.clawagent.filtered_backend import FilteredFilesystemBackend
from backend.clawagent.sse_middleware import SSEMonitoringMiddleware
from backend.clawagent.offload_middleware import ToolResultOffloadMiddleware
from backend.clawagent.diagnostic import DIAGNOSTIC_ENABLED, DiagnosticLogger
from backend.clawagent.dir_watcher import watcher as _dir_watcher
from backend.clawagent.middleware_base import MiddlewareStack
from backend.clawagent.backend_protocol import CompositeBackend
from backend.config import settings
from backend.task_settings import TaskSettings

# ── 外部扩展工具（完全保留）──
try:
    from Tools import reload_external_tools
    _initial = reload_external_tools(force=True)
    logger.info(f"[Agent] Loaded {len(_initial)} external tools: {[t.name for t in _initial]}")
    from backend.clawagent.sse_protocol import get_protocol_manager as _get_proto
    _proto = _get_proto()
    for _t in _initial:
        _proto.register_sandbox_tool(_t.name, _t.description[:80])
except ImportError:
    reload_external_tools = None
    logger.warning("[Agent] No Tools package found, skipping external tools")

# ── 路径配置（完全保留）──
_BUILTIN_SKILLS_DIR = os.environ.get("BUILTIN_SKILLS_DIR", "/app/builtin_skills")
_EXTERNAL_SKILLS_DIR = os.environ.get("EXTERNAL_SKILLS_DIR", "/app/Skills")
_WORKSPACE_DIR = os.environ.get("WORKSPACE_DIR", "/home/scienceclaw")

# ── 系统提示词（完全保留）──
_SYSTEM_PROMPT_TEMPLATE = """You are ScienceClaw, ..."""
_EVAL_SYSTEM_PROMPT_TEMPLATE = """You are ScienceClaw, ..."""
_LANGUAGE_MAP = {...}

def get_system_prompt(workspace_dir: str, ...) -> str:
    """完全保留现有实现"""
    ...

# ── 工具收集（完全保留）──
_STATIC_TOOLS = [web_search, web_crawl, ...]

def _collect_tools(blocked_tools: Set[str] | None = None) -> List:
    """完全保留现有实现"""
    ...

# ── 屏蔽查询（完全保留）──
async def get_blocked_skills(user_id: str) -> Set[str]:
    """完全保留现有实现"""
    ...

async def get_blocked_tools(user_id: str) -> Set[str]:
    """完全保留现有实现"""
    ...

# ── Backend 构建（保留逻辑，替换基类）──
def _build_backend(session_id: str, sandbox: FullSandboxBackend, ...):
    """CompositeBackend 路由组装 — 逻辑完全保留，仅替换 CompositeBackend 来源"""
    routes = {}
    if os.path.isdir(_BUILTIN_SKILLS_DIR):
        routes["/builtin-skills/"] = FilesystemBackend(
            root_dir=_BUILTIN_SKILLS_DIR, virtual_mode=True
        )
    if os.path.isdir(_EXTERNAL_SKILLS_DIR):
        routes["/skills/"] = FilteredFilesystemBackend(
            root_dir=_EXTERNAL_SKILLS_DIR, virtual_mode=True, blocked_skills=...
        )
    if routes:
        return CompositeBackend(default=sandbox, routes=routes)
    return sandbox

# ═══════════════════════════════════════════════════════════════════
# 核心重写：claw_agent() — 替代 deep_agent()
# ═══════════════════════════════════════════════════════════════════

async def claw_agent(
    session_id: str,
    model_config: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    task_settings: Optional[TaskSettings] = None,
    diagnostic_enabled: bool = False,
    language: Optional[str] = None,
    eval_mode: bool = False,
) -> tuple[ClaudeSDKClient, SSEMonitoringMiddleware, int, Optional[DiagnosticLogger]]:
    """组装 ClawAgent — 替代原来的 deep_agent()。

    Returns:
        (sdk_client, sse_middleware, context_window, diagnostic)
    """
    # 1. 模型（复用 engine.py）
    model = get_llm_model(model_config)
    context_window = _get_context_window(model_config)

    # 2. 工具
    blocked_tools = await get_blocked_tools(user_id) if user_id else set()
    tools = _collect_tools(blocked_tools)

    # 3. 系统提示词
    workspace_dir = f"{_WORKSPACE_DIR}/{session_id}"
    system_prompt = get_system_prompt(workspace_dir, language=language)

    # 4. Sandbox + Backend
    sandbox = FullSandboxBackend(workspace_dir=workspace_dir)
    blocked_skills = await get_blocked_skills(user_id) if user_id else set()
    backend = _build_backend(session_id, sandbox, blocked_skills=blocked_skills)

    # 5. 中间件栈（自建 MiddlewareStack）
    sse_middleware = SSEMonitoringMiddleware(agent_name="ClawAgent")
    offload_middleware = ToolResultOffloadMiddleware(workspace_dir, backend)
    middleware_stack = MiddlewareStack([sse_middleware, offload_middleware])

    # 6. 工具包装 — 将中间件注入到每个工具的执行链路
    wrapped_tools = []
    for tool in tools:
        wrapped_tool = _wrap_tool_with_middleware(tool, middleware_stack, backend)
        wrapped_tools.append(wrapped_tool)

    # 7. 子 Agent 配置（替代 GENERAL_PURPOSE_SUBAGENT）
    subagent_tools = _build_subagent_tools(model_config, system_prompt)
    wrapped_tools.extend(subagent_tools)

    # 8. 诊断
    diagnostic = DiagnosticLogger(session_id) if diagnostic_enabled else None
    if diagnostic:
        diagnostic.attach_to(sse_middleware)

    # 9. 创建 Claude SDK Client
    sdk_client = ClaudeSDKClient(
        options=ClaudeAgentOptions(
            allowed_tools=[t.name for t in wrapped_tools],
            max_tokens=task_settings.max_tokens if task_settings else 8192,
            system_prompt=system_prompt,
        )
    )

    # 10. 注册工具到 SDK Client
    for tool in wrapped_tools:
        sdk_client.register_tool(tool)

    logger.info(
        f"[ClawAgent] session={session_id} tools={len(wrapped_tools)} "
        f"model={model_config.get('model_name', 'default')} cw={context_window}"
    )

    return sdk_client, sse_middleware, context_window, diagnostic


def _wrap_tool_with_middleware(tool, middleware_stack, backend):
    """包装工具函数 — 在执行前后插入中间件拦截。

    这是替代 deepagents AgentMiddleware.wrap_tool_call 的核心机制。
    """
    original_handler = tool.handler if hasattr(tool, 'handler') else tool.func

    def wrapped_handler(request):
        # 注入 backend 上下文（供工具使用）
        request._backend = backend
        # 通过中间件栈执行
        return middleware_stack.run(request, original_handler)

    # 创建新的工具实例，替换 handler
    from backend.clawagent.tool_converter import create_sdk_tool
    return create_sdk_tool(
        name=tool.name,
        description=tool.description,
        parameters=tool.parameters if hasattr(tool, 'parameters') else tool.args,
        handler=wrapped_handler,
    )


def _build_subagent_tools(model_config, system_prompt):
    """构建子 Agent 工具 — 替代 GENERAL_PURPOSE_SUBAGENT。

    使用 Claude SDK 的 Task 工具实现子 Agent 调用。
    """
    from claude_agent_sdk.tools import Task

    async def subagent_handler(prompt: str, context: dict) -> dict:
        """子 Agent 执行器"""
        # 创建独立的子 Agent Client
        sub_client = ClaudeSDKClient(
            options=ClaudeAgentOptions(
                allowed_tools=["read", "write", "edit", "bash", "web_search"],
                max_tokens=4096,
                system_prompt=system_prompt + "\n\nYou are a sub-agent...",
            )
        )
        result = await sub_client.query(prompt=prompt, context=context)
        return {"result": result}

    return [Task(
        name="subagent",
        description="Delegate a task to a sub-agent for parallel execution",
        handler=subagent_handler,
    )]
```

### A.2 runner.py — 流式执行器重写给

**当前核心结构（需保留）：**
```python
# 保留（~60%）：
# - _build_plan(), _plan_for_frontend()
# - _build_history_messages()
# - _compute_history_token_budget()
# - _extract_thinking(), _estimate_tokens()
# - 初始事件序列（thinking, step_start, plan_update）
# - 超时处理
# - 最终消息格式化
# - Session 状态更新

# 重写（~30%）：
# - agent.astream() 循环 → SDK query() 流式调用
# - messages/updates 双模式处理 → SDK 消息类型处理

# 移除（~10%）：
# - langgraph_node metadata 检查
# - stream_mode=["messages", "updates"]
# - thread_id configurable
```

**目标伪代码（仅核心循环部分）：**
```python
# backend/clawagent/runner.py
async def arun_science_task_stream(session, query, attachments=None, ...):
    """SSE 流式执行器 — 保持与当前完全相同的 SSE 事件输出格式。"""

    # ==== 准备阶段（完全保留）====
    task_cfg = await get_task_settings(user_id) if user_id else TaskSettings()
    client, middleware, context_window, diagnostic = await claw_agent(
        session_id=session.session_id,
        model_config=getattr(session, "model_config", None),
        ...
    )
    middleware.clear()

    # 初始事件序列（完全保留）
    yield {"event": "thinking", "data": {"content": ""}}
    plan = _build_plan(query[:200])
    step = plan[0]
    yield {"event": "step_start", "data": {"step": step}}
    ...

    # 历史消息构建（完全保留）
    history_messages = _build_history_messages(session, current_query=query, ...)
    enriched_query = _enrich_with_attachments(query, attachments)

    # ==== 流式执行阶段（核心重写）====
    try:
        final_content = ""
        _current_todos = []
        STREAM_TIMEOUT = task_cfg.agent_stream_timeout

        async with asyncio.timeout(STREAM_TIMEOUT):
            # 原：agent.astream(input_messages, stream_mode=["messages", "updates"], config=...)
            # 新：client.query(prompt, context)
            stream = await client.query(
                prompt=enriched_query,
                context={
                    "system_prompt": system_prompt,  # 已在 agent.py 注入，可省略
                    "history": history_messages,
                    "workspace_dir": session.vm_root_dir,
                }
            )

            for msg in stream:
                # ── 轮询中间件事件（完全保留现有逻辑）──
                for mw_evt in middleware.drain_events():
                    yield _convert_mw_event(mw_evt)

                # ── 处理 SDK 消息类型（替代 messages/updates 双模式）──
                msg_type = msg.get("type")

                if msg_type == "text":
                    # 替代原 messages 模式的 AIMessageChunk
                    token_text = msg.get("content", "")
                    if token_text:
                        final_content += token_text
                        # 保持与当前完全相同的 yield 格式
                        yield {"event": "thinking", "data": {"content": token_text}}

                elif msg_type == "tool_use":
                    # 替代原 updates 模式的 tool_calls
                    tool_name = msg.get("name", "")
                    tool_args = msg.get("input", {})
                    tool_call_id = msg.get("id", "")

                    # 触发工具调用 start 事件（SDK 内部已触发中间件，这里只需 yield）
                    yield {
                        "event": "tool_call_start",
                        "data": {
                            "tool_name": tool_name,
                            "tool_args": tool_args,
                            "tool_call_id": tool_call_id,
                        }
                    }

                    # SDK 内部执行工具并返回结果
                    # 结果通过中间件 _after_tool 已生成 complete 事件
                    # 在下一次 drain_events() 中 yield

                elif msg_type == "tool_result":
                    # 工具执行完成
                    yield {
                        "event": "tool_call_end",
                        "data": {
                            "tool_name": msg.get("name", ""),
                            "tool_result": msg.get("output", {}),
                            "tool_call_id": msg.get("id", ""),
                            "duration_ms": msg.get("duration_ms", 0),
                        }
                    }

                elif msg_type == "thinking":
                    # 替代原 reasoning_content
                    yield {
                        "event": "thinking",
                        "data": {"content": msg.get("thinking", "")}
                    }

                # 检查取消（完全保留）
                if session.is_cancelled():
                    yield {"event": "error", "data": {"message": "Session stopped by user"}}
                    return

        # 发送最终消息（完全保留现有格式）
        thinking, clean_text = _extract_thinking_from_content(final_content)
        yield {
            "event": "message",
            "data": {
                "role": "assistant",
                "content": clean_text,
                "thinking": thinking,
                "input_tokens": middleware.input_tokens,
                "output_tokens": middleware.output_tokens,
            }
        }

    except asyncio.TimeoutError:
        yield {"event": "error", "data": {"message": "Agent stream timeout"}}
```

### A.3 middleware_base.py — 自建中间件基类

```python
# backend/clawagent/middleware_base.py
"""自建中间件基础设施 — 替代 langchain.agents.middleware.AgentMiddleware。

设计目标：
  1. 与 AgentMiddleware API 兼容（wrap_tool_call / awrap_tool_call）
  2. 零外部依赖
  3. 支持 sync / async 两种模式
  4. 支持中间件栈（多个中间件顺序执行）
"""
from typing import Any, Callable
from functools import wraps


class ClawMiddleware:
    """中间件基类 — 与 AgentMiddleware 接口兼容。

    子类只需重写 wrap_tool_call() 或 awrap_tool_call()。
    """

    def wrap_tool_call(
        self,
        request: Any,
        handler: Callable[[Any], Any],
    ) -> Any:
        """同步工具拦截（默认透传）。

        Args:
            request: 工具调用请求（含 tool_call 字典）
            handler: 实际工具执行函数

        Returns:
            工具执行结果
        """
        return handler(request)

    async def awrap_tool_call(
        self,
        request: Any,
        handler: Callable[[Any], Any],
    ) -> Any:
        """异步工具拦截（默认透传）。"""
        return await handler(request)

    def clear(self) -> None:
        """重置中间件状态（在每次会话开始时调用）。"""
        pass


class MiddlewareStack:
    """中间件栈 — 依次调用多个中间件形成调用链。

    与 Express / Koa 的中间件机制类似。
    """

    def __init__(self, middlewares: list[ClawMiddleware]):
        self.middlewares = middlewares

    def run(self, request: Any, final_handler: Callable) -> Any:
        """按顺序执行中间件链，最终调用实际工具。"""
        # 从最后一个中间件开始包装，形成洋葱模型
        handler = final_handler
        for mw in reversed(self.middlewares):
            handler = _make_wrapper(mw, handler)
        return handler(request)

    async def arun(self, request: Any, final_handler: Callable) -> Any:
        """异步版本。"""
        handler = final_handler
        for mw in reversed(self.middlewares):
            handler = _make_async_wrapper(mw, handler)
        return await handler(request)


def _make_wrapper(mw: ClawMiddleware, next_handler: Callable):
    """创建同步包装函数。"""
    @wraps(next_handler)
    def wrapper(request):
        return mw.wrap_tool_call(request, next_handler)
    return wrapper


def _make_async_wrapper(mw: ClawMiddleware, next_handler: Callable):
    """创建异步包装函数。"""
    @wraps(next_handler)
    async def async_wrapper(request):
        return await mw.awrap_tool_call(request, next_handler)
    return async_wrapper
```

### A.4 sse_middleware.py — 迁移后版本

```python
# backend/clawagent/sse_middleware.py
"""SSE 监控中间件 — 与当前实现 99% 相同，仅基类变更。

当前实现可直接复用，只需：
  1. from langchain.agents.middleware import AgentMiddleware → from backend.clawagent.middleware_base import ClawMiddleware
  2. class SSEMonitoringMiddleware(AgentMiddleware) → class SSEMonitoringMiddleware(ClawMiddleware)
  3. 移除 super().__init__() 调用（ClawMiddleware.__init__ 为空）

其余 _before_tool(), _after_tool(), wrap_tool_call(), drain_events() 等方法完全保留。
"""
from backend.clawagent.middleware_base import ClawMiddleware

class SSEMonitoringMiddleware(ClawMiddleware):
    """SSE 监控中间件 — 拦截工具执行前后的参数和结果。"""

    def __init__(self, agent_name: str = "agent", parent_agent: Optional[str] = None, verbose: bool = False):
        # 原：super().__init__() — AgentMiddleware 的初始化
        # 新：无需调用 super（ClawMiddleware.__init__ 为空）
        self.agent_name = agent_name
        self.parent_agent = parent_agent
        self.verbose = verbose
        self._events_lock = threading.Lock()
        self.sse_events: List[MiddlewareEvent] = []
        # ... 其余与当前完全一致 ...

    def _before_tool(self, request: Any):
        """完全保留当前实现"""
        ...

    def _after_tool(self, result: Any, tool_name, tool_args, tool_call_id, start_time, tool_meta):
        """完全保留当前实现"""
        ...

    def wrap_tool_call(self, request, handler):
        """完全保留当前实现"""
        tool_name, tool_args, tool_call_id, start_time, tool_meta = self._before_tool(request)
        result = handler(request)
        return self._after_tool(result, tool_name, tool_args, tool_call_id, start_time, tool_meta)

    def drain_events(self) -> List[Dict[str, Any]]:
        """完全保留当前实现"""
        ...

    def clear(self):
        """完全保留当前实现"""
        ...
```

### A.5 backend_protocol.py — 自建文件系统协议

```python
# backend/clawagent/backend_protocol.py
"""文件系统操作协议 — 替代 deepagents.backends.protocol 和 deepagents.backends.filesystem。

将 deepagents 的 Backend 抽象拆分为：
  1. 数据类型（FileOperation 族）
  2. 协议接口（FilesystemBackend 基类）
  3. 组合路由（CompositeBackend）
"""
from dataclasses import dataclass, field
from typing import Optional, Protocol
from pathlib import Path


# ═══════════════════════════════════════════════════════════════════
# 数据类型（替代 deepagents.backends.protocol）
# ═══════════════════════════════════════════════════════════════════

@dataclass
class FileOperation:
    path: str
    content: Optional[str] = None

@dataclass
class FileRead(FileOperation):
    pass

@dataclass
class FileWrite(FileOperation):
    pass

@dataclass
class FileEdit(FileOperation):
    old_string: Optional[str] = None
    new_string: Optional[str] = None

@dataclass
class FileList(FileOperation):
    recursive: bool = False

@dataclass
class FileGlob(FileOperation):
    pattern: str = ""

@dataclass
class FileGrep(FileOperation):
    pattern: str = ""


# ═══════════════════════════════════════════════════════════════════
# 协议接口（替代 deepagents.backends.filesystem.FilesystemBackend）
# ═══════════════════════════════════════════════════════════════════

class FilesystemBackend:
    """文件系统后端 — 与 deepagents 版本接口兼容。

    方法签名保持不变，内部实现直接调用 os/pathlib。
    """

    def __init__(self, root_dir: str, virtual_mode: bool = True):
        self.root_dir = Path(root_dir)
        self.virtual_mode = virtual_mode

    def read(self, op: FileRead) -> str:
        path = self._resolve_path(op.path)
        return path.read_text(encoding="utf-8")

    def write(self, op: FileWrite) -> None:
        path = self._resolve_path(op.path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(op.content or "", encoding="utf-8")

    def edit(self, op: FileEdit) -> None:
        path = self._resolve_path(op.path)
        content = path.read_text(encoding="utf-8")
        if op.old_string and op.new_string is not None:
            content = content.replace(op.old_string, op.new_string, 1)
        path.write_text(content, encoding="utf-8")

    def ls(self, op: FileList) -> list[dict]:
        path = self._resolve_path(op.path)
        items = []
        for item in path.iterdir():
            stat = item.stat()
            items.append({
                "name": item.name,
                "type": "directory" if item.is_dir() else "file",
                "size": stat.st_size,
                "modified": stat.st_mtime,
            })
        return items

    def glob(self, op: FileGlob) -> list[str]:
        path = self._resolve_path(op.path)
        return [str(p) for p in path.glob(op.pattern)]

    def grep(self, op: FileGrep) -> list[dict]:
        import re
        path = self._resolve_path(op.path)
        pattern = re.compile(op.pattern)
        results = []
        for file_path in path.rglob("*"):
            if file_path.is_file():
                try:
                    text = file_path.read_text(encoding="utf-8")
                    for i, line in enumerate(text.splitlines(), 1):
                        if pattern.search(line):
                            results.append({
                                "file": str(file_path),
                                "line": i,
                                "content": line.strip(),
                            })
                except UnicodeDecodeError:
                    continue
        return results

    def _resolve_path(self, path: str) -> Path:
        """解析路径 — virtual_mode 下限制在 root_dir 内。"""
        target = Path(path)
        if self.virtual_mode:
            # 确保路径在 root_dir 内（防止目录遍历）
            target = self.root_dir / target.relative_to(target.anchor) if target.is_absolute() else self.root_dir / target
            target = target.resolve()
            if not str(target).startswith(str(self.root_dir.resolve())):
                raise ValueError(f"Path escapes root directory: {path}")
        return target


class CompositeBackend:
    """组合后端 — 根据路径前缀路由到不同后端。

    与 deepagents 版本逻辑一致：
      - 默认后端处理所有请求
      - 特定路径前缀路由到对应后端
    """

    def __init__(self, default: FilesystemBackend, routes: dict[str, FilesystemBackend]):
        self.default = default
        self.routes = routes

    def _route(self, path: str) -> FilesystemBackend:
        for prefix, backend in self.routes.items():
            if path.startswith(prefix):
                return backend
        return self.default

    def read(self, op: FileRead) -> str:
        return self._route(op.path).read(op)

    def write(self, op: FileWrite) -> None:
        return self._route(op.path).write(op)

    def edit(self, op: FileEdit) -> None:
        return self._route(op.path).edit(op)

    def ls(self, op: FileList) -> list[dict]:
        return self._route(op.path).ls(op)

    def glob(self, op: FileGlob) -> list[str]:
        return self._route(op.path).glob(op)

    def grep(self, op: FileGrep) -> list[dict]:
        return self._route(op.path).grep(op)
```

### A.6 tool_converter.py — 工具转换层

```python
# backend/clawagent/tool_converter.py
"""工具格式转换 — LangChain Tool ↔ Claude SDK Tool。

如果决定保留 LangChain @tool（推荐），则需要此转换层。
如果决定移除 LangChain，则此文件不需要，工具直接定义为 SDK Tool。
"""
from typing import Callable
from claude_agent_sdk.tools import Tool as SDKTool

try:
    from langchain_core.tools import BaseTool
    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False


def convert_langchain_tool_to_sdk(lc_tool: "BaseTool") -> SDKTool:
    """将 LangChain 工具转换为 Claude SDK 工具格式。

    保留 LangChain 工具的所有元数据（名称、描述、参数 schema）。
    """
    # 提取参数 schema
    if lc_tool.args_schema:
        parameters = lc_tool.args_schema.model_json_schema()
    else:
        parameters = {"type": "object", "properties": {}, "required": []}

    # 创建 SDK 工具
    return SDKTool(
        name=lc_tool.name,
        description=lc_tool.description,
        parameters=parameters,
        handler=lambda **kwargs: lc_tool.invoke(kwargs),
    )


def create_sdk_tool(
    name: str,
    description: str,
    parameters: dict,
    handler: Callable,
) -> SDKTool:
    """直接创建 Claude SDK 工具（无需 LangChain）。"""
    return SDKTool(
        name=name,
        description=description,
        parameters=parameters,
        handler=handler,
    )
```

---

## 附录 B：技术选型确认

### B.1 决策矩阵

| 决策项 | 选项 A（推荐） | 选项 B | 决策 |
|--------|--------------|--------|------|
| **@tool 装饰器** | 保留 `langchain-core` | 移除，纯函数工具 | **保留** |
| **LangChain 依赖范围** | 仅 `langchain-core` + `langchain-openai` | 全部移除 | **精简保留** |
| **模型适配** | Claude SDK + OpenAI 兼容端点 | 多 SDK 并行 | **Claude SDK 统一** |
| **SSE 中间件** | 自建 `ClawMiddleware` | 寻找第三方替代 | **自建** |
| **Backend 协议** | 自建 `FilesystemBackend` | 使用 `aiofiles` 等 | **自建** |
| **历史压缩** | 基于 token 计数的简单截断 | 保留 SummarizationMiddleware | **简单截断** |

### B.2 @tool 保留方案详细论证

**保留理由：**
1. `langchain-core` 仅依赖 `pydantic` + `tenacity`，轻量级（~2MB）
2. `@tool` 装饰器自动生成 JSON Schema，减少手写 schema 的错误
3. 现有 15+ 工具使用 `@tool`，迁移为纯函数需重写所有参数定义
4. `langchain-core` 与 LangGraph 解耦，保留它不意味着保留 LangGraph

**风险：**
- `langchain-core` 版本更新可能带来 Breaking Change
- 团队可能误解为"仍然依赖 LangChain"

**缓解：**
- 锁定 `langchain-core==0.3.x` 版本
- 文档明确说明：仅使用 `@tool` 装饰器，不使用 LangChain 的 Agent/Chain/LCEL
- 未来可平滑迁移为纯函数（转换层已隔离）

### B.3 最终依赖清单

```text
# requirements.txt（目标状态）

# ==== Web Framework ====
fastapi==0.128.7
uvicorn[standard]==0.40.0
sse-starlette==3.2.0

# ==== Data & Config ====
pydantic==2.12.5
pydantic-settings==2.12.0
python-dotenv==1.2.1
pyyaml>=6.0

# ==== Database & Cache ====
motor==3.7.1  # MongoDB
httpx==0.28.1  # HTTP client

# ==== Logging ====
loguru==0.7.3
python-json-logger==4.0.0

# ==== Auth ====
bcrypt==5.0.0
shortuuid==1.0.13

# ==== NEW: Claude Agent SDK ====
claude-agent-sdk>=0.1.0  # 主框架

# ==== 精简保留: LangChain Core（仅 @tool）====
langchain-core==0.3.15      # @tool 装饰器 + BaseMessage 类型
langchain-openai==1.1.8     # ChatOpenAI（engine.py 复用）

# ==== 可选: 其他模型适配（按需保留）====
# langchain-google-genai    # Gemini（如需通过 engine.py 支持）

# ==== 移除 ====
# deepagents==0.4.4         # 被 claude-agent-sdk 替代
# langgraph==1.0.8          # 被 claude-agent-sdk 替代
# langchain-community==0.4.1 # 未使用
# langchain-mcp-adapters    # 暂不迁移

# ==== 其他保留 ====
tavily-python==0.7.21       # web_search fallback
lark-oapi                   # 飞书
qrcode>=8.0
tooluniverse                # 科学工具
```

### B.4 模型适配方案

```
┌─────────────────────────────────────────────────────────────┐
│                      模型选择流程                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  User Request                                               │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────┐    Claude 模型?    ┌──────────────────┐   │
│  │ model_config│ ─────────────────► │ Claude SDK Engine │   │
│  │             │    (claude-3-*)    │ (主路径)          │   │
│  └─────────────┘                    └──────────────────┘   │
│       │                                                     │
│       │ OpenAI 兼容?                                         │
│       ▼                                                     │
│  ┌─────────────┐    设置 base_url    ┌──────────────────┐   │
│  │ engine.py   │ ─────────────────► │ Claude SDK Engine │   │
│  │ (兼容模式)   │    复用 API Key     │ (通过兼容端点)    │   │
│  └─────────────┘                    └──────────────────┘   │
│       │                                                     │
│       │ 非兼容模型（Gemini等）                                │
│       ▼                                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 不支持 — 提示用户切换到 Claude 或 OpenAI 兼容模型    │   │
│  │ （或保留 DeepAgents 作为后备，见回滚策略）           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Claude SDK 的 OpenAI 兼容支持：**
```python
# Claude SDK 支持自定义 API endpoint
client = ClaudeSDKClient(
    options=ClaudeAgentOptions(
        base_url="https://api.deepseek.com/v1",  # 或其他兼容端点
        api_key="sk-...",
        model="deepseek-chat",  # 或其他兼容模型
    )
)
```

---

## 附录 C：回滚策略设计

### C.1 双目录并行方案（推荐）

**策略**：不直接重命名 `deepagent/`，而是先创建 `clawagent/`，开发完成后通过软链接切换。

```
ScienceClaw/backend/
├── deepagent/              # 原始目录（冻结，作为后备）
│   ├── agent.py            # DeepAgents 版本（保留）
│   ├── runner.py           # DeepAgents 版本（保留）
│   └── ...                 # 所有原始文件
│
├── clawagent/              # 新目录（Claude SDK 版本）
│   ├── agent.py            # SDK 版本（新开发）
│   ├── runner.py           # SDK 版本（新开发）
│   ├── middleware_base.py  # 新增
│   ├── backend_protocol.py # 新增
│   └── ...                 # 其余从 deepagent/ 复制后适配
│
└── active_agent/ -> symlink # 激活的 Agent 目录
    └── -> clawagent/       # 开发期指向 clawagent/
    # 或 -> deepagent/      # 回滚时指向 deepagent/
```

**import 路径统一化：**
```python
# 所有路由文件统一从 active_agent 导入
# 不直接导入 deepagent 或 clawagent

# backend/main.py
# from backend.deepagent.sessions import ...  # 不要这样
# from backend.clawagent.sessions import ...  # 不要这样
from backend.active_agent.sessions import ...  # 统一这样
```

**切换脚本：**
```bash
#!/bin/bash
# scripts/switch-agent.sh

AGENT_TYPE=${1:-claw}

if [ "$AGENT_TYPE" == "claw" ]; then
    ln -sfn clawagent ScienceClaw/backend/active_agent
    echo "Switched to clawagent (Claude SDK)"
elif [ "$AGENT_TYPE" == "deep" ]; then
    ln -sfn deepagent ScienceClaw/backend/active_agent
    echo "Switched to deepagent (DeepAgents)"
else
    echo "Usage: switch-agent.sh [claw|deep]"
    exit 1
fi

# 重启 backend 服务
docker compose restart backend
```

### C.2 配置级切换方案（备选）

如果不使用软链接，可在代码层面通过配置切换：

```python
# backend/config.py
class Settings(BaseSettings):
    AGENT_IMPL: str = "clawagent"  # "deepagent" | "clawagent"

# backend/agent_loader.py
import importlib

def get_agent_module(module_name: str):
    """动态加载 Agent 模块"""
    impl = settings.AGENT_IMPL
    return importlib.import_module(f"backend.{impl}.{module_name}")

# 使用示例
sessions = get_agent_module("sessions")
runner = get_agent_module("runner")
```

### C.3 数据兼容性保证

**必须保证兼容的数据：**

| 数据类型 | 兼容性 | 措施 |
|----------|--------|------|
| MongoDB sessions 集合 | ✅ 完全兼容 | 两种引擎使用相同的 sessions.py |
| MongoDB messages 集合 | ✅ 完全兼容 | SSE 事件格式不变 |
| Workspace 文件 | ✅ 完全兼容 | 相同的目录结构 |
| 环境变量 | ⚠️ 部分变更 | Claude SDK 新增 `ANTHROPIC_API_KEY` |
| `.env` 配置 | ⚠️ 新增配置项 | `AGENT_IMPL`, `CLAUDE_SDK_*` |

**回滚检查清单：**
```bash
# 紧急回滚到 DeepAgents
./scripts/switch-agent.sh deep

# 验证回滚成功
curl http://localhost:8000/api/v1/health  # 健康检查
curl http://localhost:8000/api/v1/sessions  # 会话列表正常
curl -N -X POST http://localhost:8000/api/v1/sessions/test/chat  # 对话正常
```

### C.4 灰度发布策略

```
Phase 1: 开发环境（100% clawagent）
  └─ 开发者本地测试

Phase 2: 内部测试（clawagent 50% / deepagent 50%）
  └─ 通过 session 级配置随机分配
  └─ 对比两种引擎的 SSE 输出一致性

Phase 3: Beta 用户（clawagent 10%）
  └─ 通过用户 ID hash 分配
  └─ 监控错误率和性能

Phase 4: 全量发布（clawagent 100%）
  └─ 保留 deepagent 目录至少 1 个月
  └─ 1 个月后确认无回滚需求，可移除 deepagent
```

---

## 附录 D：细粒度里程碑拆解

### D.1 总体时间线（8 周）

```
Week 1    Week 2    Week 3    Week 4    Week 5    Week 6    Week 7    Week 8
[准备+基建] [Agent核心] [Runner重写] [工具+Skills] [测试] [修复] [优化] [发布]
```

### D.2 每日/每周交付点

#### Week 1: 准备与基础设施

| 天 | 任务 | 交付物 | 验证标准 |
|----|------|--------|----------|
| **D1** | 创建 `clawagent/` 目录；复制 `deepagent/` 所有文件 | `clawagent/` 目录结构与 `deepagent/` 一致 | `ls clawagent/` 与 `ls deepagent/` 文件列表相同 |
| **D2** | 全局替换 `backend.deepagent.` → `backend.clawagent.` | 所有 import 路径更新 | `grep -r "deepagent" clawagent/` 无结果 |
| **D3** | 创建 `middleware_base.py`；适配 `sse_middleware.py` | `SSEMonitoringMiddleware` 继承 `ClawMiddleware` | 单元测试：工具拦截前后事件正确 |
| **D4** | 创建 `backend_protocol.py`；适配 `filtered_backend.py` | `FilesystemBackend` 基类替换完成 | 单元测试：read/write/edit/ls/glob/grep 正常 |
| **D5** | 适配 `full_sandbox_backend.py`；适配 `offload_middleware.py` | 所有 Backend 相关文件适配完成 | 集成测试：Sandbox 文件操作正常 |
| **Weekend** | Code Review；修复 D1-D5 问题 | PR Ready | CI 通过（如有） |

**Week 1 验收标准：**
- [ ] `clawagent/` 目录可独立 import，无 `deepagent` 残留引用
- [ ] `sse_middleware.py` 工具拦截单元测试通过
- [ ] `filtered_backend.py` + `full_sandbox_backend.py` 文件操作测试通过
- [ ] 代码审查通过

#### Week 2: Agent 核心重写

| 天 | 任务 | 交付物 | 验证标准 |
|----|------|--------|----------|
| **D8** | 设计 `claw_agent()` 函数签名；实现模型+工具收集 | `agent.py` 骨架完成 | `python -c "from backend.clawagent.agent import claw_agent"` 成功 |
| **D9** | 实现 Backend + 中间件栈组装 | `_build_backend()` + `MiddlewareStack` 集成 | 单元测试：Backend 路由正确 |
| **D10** | 实现工具包装（中间件注入） | `_wrap_tool_with_middleware()` 完成 | 单元测试：工具执行触发中间件事件 |
| **D11** | 创建 `ClaudeSDKClient`；注册工具 | SDK Client 初始化成功 | `claw_agent()` 返回 (client, middleware, cw, diag) |
| **D12** | 实现子 Agent 工具（`Task`） | `_build_subagent_tools()` 完成 | 单元测试：子 Agent 调用返回结果 |
| **Weekend** | 集成测试 agent.py | PR Ready | agent.py 所有路径可正常执行（不报错） |

**Week 2 验收标准：**
- [ ] `claw_agent()` 可成功创建 SDK Client
- [ ] 工具列表正确（内置 + 外部扩展）
- [ ] 中间件事件在工具调用前后触发
- [ ] 子 Agent 工具可调用

#### Week 3: Runner 流式循环重写

| 天 | 任务 | 交付物 | 验证标准 |
|----|------|--------|----------|
| **D15** | 重写流式循环骨架；适配 SDK `query()` 调用 | `runner.py` 核心循环可运行 | SDK query() 返回流式结果 |
| **D16** | 实现 text/thinking 消息处理 | 文本输出事件正确 | SSE 事件流包含 thinking + message |
| **D17** | 实现 tool_use/tool_result 消息处理 | 工具调用事件正确 | SSE 事件流包含 tool_call_start/end |
| **D18** | 集成中间件事件轮询 | 中间件事件与 SDK 事件合并 | 工具耗时统计正确 |
| **D19** | 实现最终消息格式化；Token 统计 | 最终 message 事件格式与旧版一致 | 对比新旧版本的 SSE 输出 |
| **Weekend** | 端到端测试：单次完整对话 | PR Ready | 一次对话从创建会话到收到最终 message |

**Week 3 验收标准：**
- [ ] 文本对话可正常输出（含 thinking）
- [ ] 工具调用前后 SSE 事件正确
- [ ] 最终 message 事件格式与旧版 100% 一致
- [ ] 取消功能正常

#### Week 4: 工具、Skills、Sandbox 集成

| 天 | 任务 | 交付物 | 验证标准 |
|----|------|--------|----------|
| **D22** | 迁移 web_search / web_crawl | 搜索工具正常 | web_search 返回结果 |
| **D23** | 迁移文件操作工具（read/write/edit） | 文件工具正常 | write_file → read_file 一致性 |
| **D24** | 迁移 execute / bash（Sandbox） | 执行工具正常 | Python 脚本在 Sandbox 中执行 |
| **D25** | 迁移 ToolUniverse 工具 | 1900+ 工具可用 | tooluniverse_run 返回结果 |
| **D26** | 迁移 Skills 加载（builtin + external） | Skills 注入 system prompt | 含 Skills 的对话行为正确 |
| **Weekend** | 全工具集成测试 | PR Ready | 所有内置工具通过测试 |

**Week 4 验收标准：**
- [ ] web_search / web_crawl / read_file / write_file / edit_file / execute 全部正常
- [ ] ToolUniverse 工具调用正常
- [ ] Skills 加载并注入 prompt 正常
- [ ] Sandbox 隔离执行正常

#### Week 5: 功能补齐

| 天 | 任务 | 交付物 | 验证标准 |
|----|------|--------|----------|
| **D29** | 思考内容提取（DeepSeek/Claude 格式） | `_extract_thinking()` 适配 | reasoning_content 正确提取 |
| **D30** | Token 统计（input/output/thinking） | Token 估算正常 | 统计值合理 |
| **D31** | 历史消息压缩（替代 SummarizationMiddleware） | `_build_history_messages()` 适配 | 长历史不超限 |
| **D32** | 诊断日志集成 | `diagnostic.py` 适配 | 诊断文件生成 |
| **D33** | 多模型支持（通过 base_url） | engine.py 适配 | 非 Claude 模型可调用 |
| **Weekend** | 功能回归测试 | PR Ready | 所有功能点 checklist 通过 |

**Week 5 验收标准：**
- [ ] 思考内容从多种格式正确提取
- [ ] Token 统计与旧版误差 < 10%
- [ ] 长历史会话不触发上下文溢出
- [ ] 诊断日志完整生成

#### Week 6: 测试与修复

| 天 | 任务 | 交付物 | 验证标准 |
|----|------|--------|----------|
| **D36** | 编写单元测试（目标 80% 覆盖） | `tests/` 目录 | pytest 覆盖率报告 |
| **D37** | SSE 事件流对比测试 | 对比脚本 | 新旧版本 SSE 事件 100% 匹配 |
| **D38** | 并发压力测试 | 压力测试脚本 | 10 并发会话无崩溃 |
| **D39** | Bug 修复（Round 1） | 修复 PR | 已知问题清零 |
| **D40** | Bug 修复（Round 2） | 修复 PR | 回归测试通过 |
| **Weekend** | 测试报告 | 测试报告文档 | 所有测试通过 |

**Week 6 验收标准：**
- [ ] 单元测试覆盖率 > 80%
- [ ] SSE 事件流与旧版对比无差异
- [ ] 10 并发会话稳定运行
- [ ] 已知 Bug 清零

#### Week 7: 性能优化

| 天 | 任务 | 交付物 | 验证标准 |
|----|------|--------|----------|
| **D43** | SSE 延迟优化 | 优化 PR | 首 token 延迟 < 旧版 120% |
| **D44** | 工具调用延迟优化 | 优化 PR | 工具调用延迟 < 旧版 120% |
| **D45** | 内存占用优化 | 优化 PR | 单会话内存 < 旧版 120% |
| **D46** | MongoDB 查询优化 | 优化 PR | 会话列表查询 < 100ms |
| **D47** | 最终回归测试 | 测试报告 | 全量测试通过 |
| **Weekend** | 性能基准报告 | 报告文档 | 性能达标 |

**Week 7 验收标准：**
- [ ] 首 token 延迟不超过旧版 120%
- [ ] 工具调用延迟不超过旧版 120%
- [ ] 内存占用不超过旧版 120%

#### Week 8: 发布准备

| 天 | 任务 | 交付物 | 验证标准 |
|----|------|--------|----------|
| **D50** | 更新 README / 部署文档 | 文档 PR | 文档准确 |
| **D51** | 编写迁移指南 | `docs/migration-guide.md` | 迁移步骤清晰 |
| **D52** | 更新 docker-compose / Dockerfile | 配置 PR | 构建成功 |
| **D53** | 最终 Code Review | Review 完成 | 无阻塞问题 |
| **D54** | 合并到主分支 | Merge Commit | CI 通过 |
| **D55** | 灰度发布（10%） | 监控面板 | 错误率 < 1% |

**Week 8 验收标准：**
- [ ] 文档完整更新
- [ ] Docker 构建成功
- [ ] 灰度发布无异常

### D.3 关键检查点（Go/No-Go）

| 检查点 | 时间 | 标准 | 失败处理 |
|--------|------|------|----------|
| **CP1** | Week 1 结束 | `clawagent/` 目录结构完整，可独立 import | 延期 2 天或调整范围 |
| **CP2** | Week 2 结束 | `claw_agent()` 可创建 SDK Client，工具列表正确 | 回退到 DeepAgents |
| **CP3** | Week 3 结束 | 单次文本对话正常，SSE 事件格式与旧版一致 | 回退到 DeepAgents |
| **CP4** | Week 4 结束 | 所有内置工具 + Skills + Sandbox 正常 | 延期修复或回退 |
| **CP5** | Week 6 结束 | 测试覆盖率 > 80%，已知 Bug 清零 | 延期修复 |
| **CP6** | Week 8 结束 | 灰度发布无异常 | 回滚到 DeepAgents |

### D.4 每日站立会议（建议）

```
时间：每天 10:00（15 分钟）
参与者：后端开发 + 技术负责人

议程：
  1. 昨天完成了什么？（对照里程碑 checklist）
  2. 今天计划做什么？
  3. 有什么阻塞？（技术难点、依赖等待）

产出：
  - 阻塞项立即升级（技术负责人介入）
  - 偏离里程碑 > 1 天，触发范围调整讨论
```

---

> **文档维护**：本方案是 `claude-sdk-refactor-plan.md` v1.0 的聚焦版 + 4 个深化方向。
> 规划阶段产物，**不修改实际仓库代码**。
