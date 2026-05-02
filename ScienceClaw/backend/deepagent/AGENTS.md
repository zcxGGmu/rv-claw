# ScienceClaw Agent 引擎知识库

> **范围**: `ScienceClaw/backend/deepagent/`
> **状态**: 正在重构（DeepAgents → Claude SDK）
> **规模**: 15 个文件，~4,767 行 Python

---

## 文件地图

| 文件 | 行数 | 职责 | 重构影响 |
|------|------|------|---------|
| `runner.py` | 891 | **流式执行器**：SSE 事件循环，LangGraph `astream()` 调用 | 🔴 重写核心循环 |
| `agent.py` | 586 | **Agent 组装器**：`deep_agent()` 创建模型+工具+中间件 | 🔴 重写为 `claw_agent()` |
| `engine.py` | 450 | **模型工厂**：多模型配置，含 70 行 monkey-patch | 🟡 保留逻辑，移除 patch |
| `tools.py` | 481 | **内置工具**：web_search, web_crawl, read_file, write_file... | 🟢 保留 `@tool` 装饰器 |
| `full_sandbox_backend.py` | 576 | **Sandbox 后端**：HTTP 调用 AIO Sandbox 执行代码 | 🟡 替换协议类型 |
| `sse_middleware.py` | 393 | **SSE 监控中间件**：拦截工具调用生成事件 | 🟡 更换基类 |
| `sse_protocol.py` | 239 | **SSE 协议**：事件格式定义，工具元数据注册 | 🟢 保留 |
| `sessions.py` | 343 | **会话管理**：Session 数据结构 | 🟢 保留 |
| `diagnostic.py` | 255 | **诊断日志**：LLM 调用记录 | 🟢 保留 |
| `offload_middleware.py` | 174 | **大结果落盘中间件**：>3000 字符写入文件 | 🟡 更换基类 |
| `tooluniverse_tools.py` | 141 | **科学工具**：ToolUniverse 1900+ 工具调用 | 🟢 保留 |
| `filtered_backend.py` | 128 | **过滤后端**：屏蔽特定 skills 目录 | 🟡 替换基类 |
| `plan_types.py` | 38 | **计划类型**：Pydantic 模型 | 🟢 保留 |
| `dir_watcher.py` | 72 | **目录监听**：监控 Tools/ 目录变化 | 🟢 保留 |

---

## Agent 生命周期

```
用户请求
    ↓
sessions.py 创建/获取 Session
    ↓
agent.py deep_agent() 组装 Agent
    ├── engine.py 创建模型
    ├── tools.py + tooluniverse_tools.py 收集工具
    ├── full_sandbox_backend.py 创建 Sandbox
    ├── filtered_backend.py 创建 Skills 路由
    ├── sse_middleware.py 创建监控
    └── offload_middleware.py 创建落盘
    ↓
runner.py arun_science_task_stream() 流式执行
    ├── 初始事件（thinking, step_start, plan_update）
    ├── agent.astream() 流式调用
    │   ├── messages 模式：逐 token 输出
    │   └── updates 模式：工具调用节点
    ├── 中间件事件轮询（drain_events）
    └── 最终 message 事件
    ↓
SSE 流返回前端
```

---

## SSE 事件类型（冻结格式）

以下事件格式**绝对不可更改**，前端依赖这些格式：

```python
{"event": "thinking", "data": {"content": str}}           # 思考内容/Token 流
{"event": "step_start", "data": {"step": dict}}            # 步骤开始
{"event": "plan_update", "data": {"plan": list}}           # 计划更新
{"event": "tool_call_start", "data": {"tool_call": dict}}  # 工具调用开始
{"event": "tool_call_end", "data": {"tool_call": dict, "result": dict}}  # 工具调用结束
{"event": "message", "data": {"role": "assistant", "content": str, ...}}  # 最终消息
{"event": "error", "data": {"message": str}}               # 错误
```

---

## 工具系统

### 内置工具（`tools.py`）

```python
@tool
def web_search(queries: str) -> dict: ...

def web_crawl(url: str) -> dict: ...
def read_file(file_path: str) -> str: ...
def write_file(file_path: str, content: str) -> str: ...
def edit_file(file_path: str, old_string: str, new_string: str) -> str: ...
def execute(code: str, language: str = "python") -> dict: ...
def propose_skill_save(...) -> dict: ...
def propose_tool_save(...) -> dict: ...
```

### 工具注册（三处分散 — 痛点）

1. `tools.py` — 实现工具函数
2. `agent.py` `_STATIC_TOOLS` — 加入工具列表
3. `sse_protocol.py` `_initialize_default_tools()` — 手动注册图标和分类

> ⚠️ 新增工具必须同时修改这三处！

---

## 中间件系统

当前中间件继承自 `langchain.agents.middleware.AgentMiddleware`：

```python
class SSEMonitoringMiddleware(AgentMiddleware):
    def wrap_tool_call(self, request, handler):
        # 工具调用前：记录 start 事件
        result = handler(request)
        # 工具调用后：记录 complete 事件
        return result
```

**目标重构**: 自定义 `ClawMiddleware` 基类 + `MiddlewareStack`

### 现有中间件

| 中间件 | 文件 | 职责 |
|--------|------|------|
| SSEMonitoringMiddleware | `sse_middleware.py` | 拦截工具调用，生成 SSE 事件 |
| ToolResultOffloadMiddleware | `offload_middleware.py` | 大结果（>3000 字符）自动写入文件 |

---

## Backend 文件系统

```
CompositeBackend
    ├── default: FullSandboxBackend  → AIO Sandbox HTTP API
    └── routes:
        ├── /builtin-skills/ → FilesystemBackend (/app/builtin_skills)
        └── /skills/ → FilteredFilesystemBackend (/app/Skills)
```

**虚拟路径规则**:
- `/home/scienceclaw/{session_id}/` → 用户 workspace
- `/builtin-skills/` → 内置技能只读
- `/skills/` → 用户技能（可过滤屏蔽）

---

## 反模式（核心引擎）

| # | 反模式 | 位置 | 重构方案 |
|---|--------|------|---------|
| 1 | **框架黑盒** `create_deep_agent()` | `agent.py` | 替换为 `ClaudeSDKClient` |
| 2 | **双流合并** `stream_mode=["messages","updates"]` | `runner.py` | 单模式 `client.query()` |
| 3 | **Monkey-patch** `_convert_dict_to_message` | `engine.py` | SDK 原生支持 |
| 4 | **Async bridge hack** `asyncio.run()` + `ThreadPoolExecutor` | `offload_middleware.py`, `full_sandbox_backend.py` | 统一全异步 |
| 5 | **全局状态竞态** `GENERAL_PURPOSE_SUBAGENT` 模块级 dict | `agent.py` | 会话级隔离 |
| 6 | **Thinking 格式碎片化** 三重判断 | `runner.py` | SDK 统一提取 |
| 7 | **工具注册三处分散** | `tools.py`+`agent.py`+`sse_protocol.py` | `@claw_tool` 自注册 |
| 8 | **双层上下文截断** Runner + SummarizationMiddleware | `runner.py` | 单点截断 |
| 9 | **Token 四重回退** | `runner.py` | SDK 原生统计 |
| 10 | **诊断间接拦截** LangChain callback | `diagnostic.py` | Hooks 直接注入 |

---

## 关键状态机

### runner.py 流式循环状态

```python
# 核心状态变量
final_content = ""           # 累积的文本输出
_current_todos = []          # 当前待办列表
_chunks_had_reasoning = False  # 是否已收到 reasoning_content
_chunks_had_text = False       # 是否已收到文本
_mw_cache = {}               # 中间件事件缓存（tool_call_id → event）
```

### 会话状态

```python
class Session:
    session_id: str
    status: str           # "active" | "completed" | "cancelled"
    title: str
    latest_message: str
    vm_root_dir: str      # /home/scienceclaw/{session_id}
    model_config: dict    # 模型配置
    thread_id: str        # LangGraph thread ID
```

---

## 子 Agent

当前通过 `GENERAL_PURPOSE_SUBAGENT` 字典配置：

```python
# ⚠️ 模块级全局变量 — 竞态风险！
GENERAL_PURPOSE_SUBAGENT["system_prompt"] = DEFAULT_SUBAGENT_PROMPT + policy
agent = create_deep_agent(...)
GENERAL_PURPOSE_SUBAGENT["system_prompt"] = DEFAULT_SUBAGENT_PROMPT  # 恢复
```

**目标**: SDK `Task` 工具，每个子 Agent 独立 `ClaudeSDKClient`

---

## 诊断模式

启用: `DIAGNOSTIC_ENABLED=1`

记录内容:
- LLM 输入消息（`save_initial_input`）
- 中间件事件（SSEMonitoringMiddleware 拦截）
- 工具调用结果
- Token 统计

输出: `diagnostics/{session_id}_{timestamp}.jsonl`

---

## 开发注意事项

1. **runner.py 是核心中的核心**: 任何修改必须保证 SSE 事件格式 100% 一致
2. **工具拦截不可丢失**: SSEMonitoringMiddleware 的事件生成逻辑必须完整保留
3. **Sandbox 路径安全**: 所有文件操作经过虚拟路径解析，禁止路径逃逸
4. **会话隔离**: 每个 Session 有独立的 workspace 目录，禁止跨会话访问
5. **流式超时**: `STREAM_TIMEOUT` 默认 300 秒，超时后发送 error 事件

---

## 重构目标文件（规划中）

```
clawagent/
├── middleware_base.py        # ClawMiddleware + MiddlewareStack（新建）
├── backend_protocol.py       # FileOperation + FilesystemBackend（新建）
├── tool_converter.py         # LangChain Tool → SDK Tool（新建）
├── agent.py                  # claw_agent()（重写）
├── runner.py                 # client.query() 循环（重写）
├── sse_middleware.py         # 更换基类（适配）
├── offload_middleware.py     # 更换基类（适配）
├── filtered_backend.py       # 更换基类（适配）
├── full_sandbox_backend.py   # 替换协议类型（适配）
└── engine.py                 # 移除 monkey-patch（适配）
```
