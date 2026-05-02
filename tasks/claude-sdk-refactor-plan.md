# ScienceClaw Claude Agent SDK 重构方案

> **版本**: v1.0
> **日期**: 2026-05-02
> **状态**: 设计方案
> **作者**: Sisyphus (AI Agent)

---

## 目录

- [1. 项目现状分析](#1-项目现状分析)
  - [1.1 整体架构](#11-整体架构)
  - [1.2 Agent 核心模块分析](#12-agent-核心模块分析)
  - [1.3 当前技术栈](#13-当前技术栈)
- [2. Claude Agent SDK 能力评估](#2-claude-agent-sdk-能力评估)
  - [2.1 SDK 核心特性](#21-sdk-核心特性)
  - [2.2 与 DeepAgents 能力对比](#22-与-deepagents-能力对比)
  - [2.3 关键差距与风险](#23-关键差距与风险)
- [3. 重构架构设计](#3-重构架构设计)
  - [3.1 设计原则](#31-设计原则)
  - [3.2 目标架构图](#32-目标架构图)
  - [3.3 Agent 引擎抽象层](#33-agent-引擎抽象层)
  - [3.4 双引擎共存策略](#34-双引擎共存策略)
  - [3.5 工具与 Skills 适配层](#35-工具与-skills-适配层)
  - [3.6 SSE 事件统一层](#36-sse-事件统一层)
- [4. 详细实施计划](#4-详细实施计划)
  - [4.1 Phase 1: 基础架构重构 (Week 1-3)](#41-phase-1-基础架构重构-week-1-3)
  - [4.2 Phase 2: Claude SDK 核心实现 (Week 4-7)](#42-phase-2-claude-sdk-核心实现-week-4-7)
  - [4.3 Phase 3: Skills 与 Sandbox 适配 (Week 8-10)](#43-phase-3-skills-与-sandbox-适配-week-8-10)
  - [4.4 Phase 4: 测试与优化 (Week 11-13)](#44-phase-4-测试与优化-week-11-13)
- [5. 核心模块重构设计](#5-核心模块重构设计)
  - [5.1 AgentEngine 抽象接口](#51-agentengine-抽象接口)
  - [5.2 DeepAgentEngine (现有引擎包装)](#52-deepagentengine-现有引擎包装)
  - [5.3 ClaudeAgentEngine (新增引擎)](#53-claudeagentengine-新增引擎)
  - [5.4 工具适配层](#54-工具适配层)
  - [5.5 Skills 适配层](#55-skills-适配层)
  - [5.6 SSE 事件转换器](#56-sse-事件转换器)
- [6. 代码示例](#6-代码示例)
  - [6.1 AgentEngine 接口定义](#61-agentengine-接口定义)
  - [6.2 DeepAgentEngine 实现](#62-deepagentengine-实现)
  - [6.3 ClaudeAgentEngine 实现](#63-claudeagentengine-实现)
  - [6.4 工具适配示例](#64-工具适配示例)
  - [6.5 路由层适配](#65-路由层适配)
- [7. 风险评估与缓解策略](#7-风险评估与缓解策略)
  - [7.1 技术风险](#71-技术风险)
  - [7.2 业务风险](#72-业务风险)
  - [7.3 缓解策略](#73-缓解策略)
- [8. 成本估算](#8-成本估算)
  - [8.1 开发成本](#81-开发成本)
  - [8.2 运行成本对比](#82-运行成本对比)
- [9. 成功标准](#9-成功标准)
- [10. 附录](#10-附录)
  - [10.1 术语表](#101-术语表)
  - [10.2 参考资源](#102-参考资源)

---

## 1. 项目现状分析

### 1.1 整体架构

ScienceClaw 是一个基于 Docker 容器化的个人研究助手，采用微服务架构：

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Vue 3)                      │
│                     http://localhost:5173                    │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP/SSE
┌───────────────────────────▼─────────────────────────────────┐
│                      Backend (FastAPI)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐ │
│  │  Auth    │  │ Sessions │  │  Chat    │  │   Science    │ │
│  │  Router  │  │  Router  │  │  Router  │  │   Router     │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┬───────┘ │
│       └─────────────┴─────────────┴─────────────────┘        │
│                            │                                 │
│  ┌─────────────────────────▼──────────────────────────────┐ │
│  │              DeepAgent Core (deepagent/)                │ │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────────────┐  │ │
│  │  │ engine │ │ agent  │ │ runner │ │ sessions       │  │ │
│  │  │ (450L) │ │ (586L) │ │ (891L) │ │ (343L)         │  │ │
│  │  └────────┘ └────────┘ └────────┘ └────────────────┘  │ │
│  │  ┌────────┐ ┌────────────┐ ┌────────────────────────┐ │ │
│  │  │ tools  │ │sse_middleware│ │full_sandbox_backend  │ │ │
│  │  │ (481L) │ │  (393L)    │ │  (576L)                │ │ │
│  │  └────────┘ └────────────┘ └────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│  ┌─────────────────────────▼──────────────────────────────┐ │
│  │              Infrastructure Layer                       │ │
│  │  MongoDB  │  Redis  │  Sandbox  │  WebSearch  │  IM   │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Agent 核心模块分析

当前 Agent 核心位于 `ScienceClaw/backend/deepagent/`，总计约 **4,767 行** Python 代码：

| 模块 | 行数 | 职责 | 复杂度 |
|------|------|------|--------|
| `runner.py` | 891 | SSE 流式执行器，合并中间件事件与流事件 | 高 |
| `agent.py` | 586 | DeepAgent 组装（模型+工具+Skills+中间件） | 高 |
| `engine.py` | 450 | 多模型工厂（OpenAI/Gemini/DeepSeek/Kimi/Claude） | 中 |
| `tools.py` | 481 | 内置工具（web_search, web_crawl, propose_skill_save 等） | 中 |
| `sse_middleware.py` | 393 | SSE 监控中间件，拦截工具执行前后 | 高 |
| `full_sandbox_backend.py` | 576 | 完整的 Sandbox 文件系统后端 | 高 |
| `sessions.py` | 343 | ScienceSession 会话管理与持久化 | 中 |
| `sse_protocol.py` | 239 | SSE 协议管理器 | 低 |
| `tooluniverse_tools.py` | 141 | ToolUniverse 1900+ 科学工具集成 | 低 |
| `offload_middleware.py` | 174 | 工具结果卸载中间件 | 中 |
| `filtered_backend.py` | 128 | 过滤文件系统后端 | 低 |
| `diagnostic.py` | 255 | 诊断日志 | 低 |
| `dir_watcher.py` | 72 | 目录监听器 | 低 |
| `plan_types.py` | 38 | 计划类型定义 | 低 |

**关键依赖：**
- `deepagents==0.4.4` — Agent 核心框架
- `langgraph==1.0.8` — 状态图编排
- `langchain-openai==1.1.8` — OpenAI 模型适配
- `langchain-google-genai` — Gemini 模型适配
- `langchain-mcp-adapters` — MCP 适配器

### 1.3 当前技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Tailwind CSS |
| 后端框架 | FastAPI + Uvicorn |
| Agent 框架 | LangChain + LangGraph + DeepAgents |
| 数据库 | MongoDB (motor) |
| 缓存 | Redis |
| 消息队列 | Redis Pub/Sub |
| 搜索 | SearXNG + Crawl4AI |
| 沙箱 | AIO Sandbox (Docker) |
| 部署 | Docker Compose |
| 任务调度 | APScheduler (task-service) |
| IM 集成 | 飞书 (lark-oapi) |

---

## 2. Claude Agent SDK 能力评估

### 2.1 SDK 核心特性

Claude Agent SDK 是 Anthropic 推出的编程式 Agent 框架，将 Claude Code 的能力封装为可编程库：

**核心模式：**
1. **`query()`** — 无状态单次任务，适合一次性操作
2. **`ClaudeSDKClient`** — 有状态多轮对话，适合复杂交互

**内置工具集：**

| 工具 | 能力 | 对应现有功能 |
|------|------|-------------|
| `Read` | 读取文件 | `read_file` |
| `Write` | 创建文件 | `write_file` |
| `Edit` | 精确编辑文件 | `edit_file` |
| `Bash` | 运行终端命令 | `execute` / `shell` |
| `Glob` | 基于模式的文件搜索 | `glob` |
| `Grep` | 正则内容搜索 | `grep` |
| `WebSearch` | 搜索网页 | `web_search` |
| `WebFetch` | 获取网页内容 | `web_crawl` |
| `Task` | 启动子 Agent | `subagent` |

**高级特性：**
- **Sub-agents**：并行化子任务，支持多 Agent 协作
- **MCP 集成**：通过 Model Context Protocol 连接外部服务
- **工具权限控制**：`allowed_tools` 最小权限原则
- **结果验证**：每次 Agent 执行后可验证输出

### 2.2 与 DeepAgents 能力对比

| 能力维度 | DeepAgents (当前) | Claude Agent SDK | 评估 |
|----------|------------------|-----------------|------|
| **多模型支持** | ✅ OpenAI, Gemini, DeepSeek, Kimi, Claude 等 | ⚠️ 主要面向 Claude，但可通过 API endpoint 配置支持其他模型 | SDK 支持自定义 base_url，理论上兼容 OpenAI 格式模型 |
| **文件系统操作** | ✅ CompositeBackend, 虚拟模式, 路由隔离 | ✅ Read/Write/Edit/Bash/Glob/Grep | 功能等价，但接口不同 |
| **Sandbox 执行** | ✅ FullSandboxBackend (Docker 隔离) | ✅ Bash 工具（需在 Docker 中运行） | 需要适配，功能等价 |
| **SSE 流式输出** | ✅ 成熟的 SSEMonitoringMiddleware | ❌ 无原生 SSE 中间件 | 需自行实现事件转换层 |
| **Skills 系统** | ✅ SKILL.md + 路由系统 + 自动匹配 | ❌ 无原生 Skills 支持 | 需自行实现 Skills 适配层 |
| **ToolUniverse** | ✅ 1900+ 科学工具集成 | ❌ 无原生支持 | 需迁移工具到 SDK 格式 |
| **子 Agent** | ✅ GENERAL_PURPOSE_SUBAGENT | ✅ Task 工具 | 功能等价 |
| **会话持久化** | ✅ ScienceSession + MongoDB | ❌ 无原生持久化 | 需自行实现 |
| **工具热加载** | ✅ Tools/ 目录自动扫描 | ❌ 无原生支持 | 需适配 |
| **中间件系统** | ✅ AgentMiddleware (wrap_tool_call) | ❌ 无原生中间件 | 需通过回调或包装实现 |
| **思考内容提取** | ✅ 支持 DeepSeek/Claude/Qwen 思考格式 | ❌ 需自行处理 | 需保留现有逻辑 |
| **Token 估算** | ✅ 多模型 Token 估算 | ❌ 需自行实现 | 需保留现有逻辑 |

### 2.3 关键差距与风险

**高风险项：**
1. **多模型兼容性**：Claude Agent SDK 主要面向 Claude 模型，虽然支持自定义 API endpoint，但其他模型（Gemini, DeepSeek）的兼容性未经验证
2. **SSE 事件系统**：当前前端重度依赖 SSE 事件流（工具前后事件、思考内容、Token 统计），SDK 无原生支持，需要完整重写事件层
3. **Skills 系统**：当前 Skills 系统（路由隔离、自动匹配、屏蔽管理）是核心功能，SDK 无对应概念

**中风险项：**
1. **ToolUniverse 迁移**：1900+ 工具需要适配到 SDK 工具格式
2. **Sandbox 集成**：当前 Sandbox 通过 Docker 共享卷 + 远程 API 实现，需要适配到 SDK 的 Bash 工具模式
3. **会话状态管理**：SDK 无持久化，需要将会话状态映射到 MongoDB

**低风险项：**
1. **文件操作工具**：功能等价，接口映射简单
2. **子 Agent**：SDK 的 Task 工具功能更强
3. **Web 搜索**：SDK 内置 WebSearch/WebFetch

---

## 3. 重构架构设计

### 3.1 设计原则

1. **渐进式重构**：不替换现有 DeepAgents，而是引入 Claude Agent SDK 作为可选引擎
2. **抽象隔离**：定义统一的 `AgentEngine` 接口，两种引擎实现同一接口
3. **零前端侵入**：前端无需感知后端引擎变化，SSE 事件格式保持一致
4. **配置化切换**：用户/管理员可在系统设置中切换 Agent 引擎
5. **功能对等**：Claude SDK 引擎应支持现有所有核心功能
6. **回滚安全**：任何时刻可回退到 DeepAgents 引擎

### 3.2 目标架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Frontend (Vue 3)                               │
│                    (无变化，SSE 事件格式保持一致)                          │
└───────────────────────────┬─────────────────────────────────────────────┘
                            │ HTTP/SSE
┌───────────────────────────▼─────────────────────────────────────────────┐
│                         Backend (FastAPI)                                │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                        Router Layer                               │   │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌──────────────┐  │   │
│  │  │  Auth  │  │Sessions│  │ Chat   │  │Science │  │ Task Settings│  │   │
│  │  │        │  │        │  │        │  │        │  │              │  │   │
│  │  └────────┘ └────────┘ └────────┘ └────────┘ └──────────────┘  │   │
│  └──────────────────────────┬──────────────────────────────────────┘   │
│                             │                                            │
│  ┌──────────────────────────▼──────────────────────────────────────┐   │
│  │                    Agent Orchestrator                            │   │
│  │         (引擎路由、会话管理、事件聚合、状态持久化)                  │   │
│  └──────────────────────────┬──────────────────────────────────────┘   │
│                             │                                            │
│  ┌──────────────────────────▼──────────────────────────────────────┐   │
│  │                   AgentEngine Interface                          │   │
│  │  ┌────────────────────┐            ┌────────────────────┐       │   │
│  │  │   DeepAgentEngine  │◄──────────►│  ClaudeAgentEngine │       │   │
│  │  │   (现有代码包装)    │   切换     │   (基于 SDK 新建)   │       │   │
│  │  └────────────────────┘            └────────────────────┘       │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    Shared Adapter Layer                           │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │   │
│  │  │ Tool Adapter │  │Skills Adapter│  │ SSE Event Converter  │   │   │
│  │  │ (工具统一接口) │  │(Skills 路由)  │  │ (事件格式转换)        │   │   │
│  │  └──────────────┘  └──────────────┘  └──────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                   Infrastructure Layer                            │   │
│  │  MongoDB  │  Redis  │  Sandbox  │  WebSearch  │  ToolUniverse  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.3 Agent 引擎抽象层

核心设计是定义 `AgentEngine` 抽象基类，所有 Agent 相关操作通过该接口进行：

```python
class AgentEngine(ABC):
    """Agent 引擎抽象接口 — 支持多种后端实现"""

    @abstractmethod
    async def create_session(self, session_id: str, config: dict) -> AgentSession:
        """创建会话"""

    @abstractmethod
    async def stream_chat(
        self,
        session: AgentSession,
        message: str,
        history: list[dict],
    ) -> AsyncGenerator[SSEEvent, None]:
        """流式对话，统一返回 SSE 事件"""

    @abstractmethod
    async def cancel_session(self, session_id: str) -> None:
        """取消会话"""

    @abstractmethod
    async def get_stats(self, session_id: str) -> AgentStats:
        """获取会话统计"""
```

### 3.4 双引擎共存策略

**配置项：**
```python
# config.py
class Settings(BaseSettings):
    # 引擎选择: "deepagents" | "claude_sdk" | "auto"
    AGENT_ENGINE: str = "deepagents"

    # Claude SDK 专属配置
    CLAUDE_SDK_MODEL: str = "claude-3-7-sonnet-20250219"
    CLAUDE_SDK_API_KEY: str = ""
    CLAUDE_SDK_BASE_URL: str = ""
    CLAUDE_SDK_MAX_TOKENS: int = 8192
    CLAUDE_SDK_ALLOWED_TOOLS: list[str] = []
```

**运行时引擎工厂：**
```python
# backend/agent_engine/factory.py
async def get_engine(engine_type: str | None = None) -> AgentEngine:
    """获取 Agent 引擎实例（单例）"""
    engine_type = engine_type or settings.AGENT_ENGINE
    if engine_type == "claude_sdk":
        return ClaudeAgentEngine()
    elif engine_type == "deepagents":
        return DeepAgentEngine()
    elif engine_type == "auto":
        # 根据模型自动选择
        return _auto_select_engine()
    else:
        raise ValueError(f"Unknown engine: {engine_type}")
```

**按会话切换：** 支持为每个会话单独选择引擎，实现 A/B 测试：
```python
# sessions.py
class ScienceSession:
    engine_type: str = "deepagents"  # 会话级引擎配置
```

### 3.5 工具与 Skills 适配层

**工具适配策略：**

现有工具分为三类，分别适配：

1. **SDK 原生替代**（无需适配）：
   - `web_search` → SDK `WebSearch`
   - `web_crawl` → SDK `WebFetch`
   - `read_file` → SDK `Read`
   - `write_file` → SDK `Write`
   - `edit_file` → SDK `Edit`
   - `execute` / `shell` → SDK `Bash`
   - `glob` → SDK `Glob`
   - `grep` → SDK `Grep`

2. **需要包装的工具**（SDK 不支持，需自定义）：
   - `propose_skill_save` — 保存 Skill 提案
   - `propose_tool_save` — 保存 Tool 提案
   - `eval_skill` — Skill 评估
   - `grade_eval` — 评分评估
   - `tooluniverse_search/info/run` — 1900+ 科学工具

3. **完全自定义工具**（需要完整实现）：
   - Sandbox 代码执行（复杂，需保留现有 Sandbox 后端）
   - Feishu/IM 集成工具

**Skills 适配策略：**

由于 SDK 无原生 Skills 概念，需要实现 Skills 适配器：

```python
# backend/agent_engine/skills_adapter.py
class SkillsAdapter:
    """将现有 Skills 系统适配到 Claude SDK"""

    def load_skills(self, session_id: str) -> list[dict]:
        """加载 Skills，转换为 SDK 可用的 system prompt 片段"""

    def build_system_prompt(self, base_prompt: str, skills: list) -> str:
        """将 Skills 内容注入到 system prompt"""
```

### 3.6 SSE 事件统一层

当前前端期望的 SSE 事件格式：

```json
{
  "event": "tool_call_start",
  "data": {
    "tool_name": "web_search",
    "tool_args": {"queries": "AI research"},
    "timestamp": 1234567890
  }
}
```

Claude SDK 输出的是消息流（文本 + 工具调用），需要通过 `SSEEventConverter` 转换为前端期望的格式：

```python
# backend/agent_engine/sse_converter.py
class SSEEventConverter:
    """将 Claude SDK 输出转换为统一 SSE 事件格式"""

    def convert_tool_call(self, tool_call: dict) -> SSEEvent:
        """工具调用开始事件"""

    def convert_tool_result(self, result: dict) -> SSEEvent:
        """工具调用结果事件"""

    def convert_thinking(self, content: str) -> SSEEvent:
        """思考内容事件"""

    def convert_message(self, content: str) -> SSEEvent:
        """AI 消息事件"""
```

---

## 4. 详细实施计划

### 4.1 Phase 1: 基础架构重构 (Week 1-3)

**目标**：建立抽象层，实现双引擎共存基础

**Week 1: 抽象接口设计**
- [ ] 定义 `AgentEngine` ABC 接口
- [ ] 定义 `AgentSession` 数据模型
- [ ] 定义 `SSEEvent` 统一事件模型
- [ ] 定义 `ToolAdapter` 接口
- [ ] 创建 `backend/agent_engine/` 目录结构

**Week 2: 现有代码迁移到 DeepAgentEngine**
- [ ] 将 `deepagent/` 代码重构为 `DeepAgentEngine` 类
- [ ] 实现 `AgentEngine` 的所有抽象方法
- [ ] 确保现有路由通过 `AgentEngine` 接口调用
- [ ] 保持 100% 向后兼容

**Week 3: 配置与路由适配**
- [ ] 添加 `AGENT_ENGINE` 配置项
- [ ] 实现引擎工厂 `get_engine()`
- [ ] 修改 `sessions.py` 路由支持引擎选择
- [ ] 添加管理 API：切换引擎、查看引擎状态
- [ ] 编写单元测试确保两种引擎 API 一致

**产出物：**
- `backend/agent_engine/__init__.py`
- `backend/agent_engine/base.py` (ABC)
- `backend/agent_engine/deepagents_engine.py`
- `backend/agent_engine/factory.py`
- 更新后的 `backend/route/sessions.py`
- 100% 向后兼容验证

### 4.2 Phase 2: Claude SDK 核心实现 (Week 4-7)

**目标**：实现基于 Claude Agent SDK 的完整 Agent 引擎

**Week 4: SDK 集成与基础对话**
- [ ] 安装 `claude-agent-sdk` 依赖
- [ ] 实现 `ClaudeAgentEngine` 骨架
- [ ] 实现基础 `stream_chat`（文本对话）
- [ ] 实现会话创建/取消/统计
- [ ] 集成现有 MongoDB 会话持久化

**Week 5: 工具适配**
- [ ] 实现 `ClaudeToolAdapter`：将现有工具转换为 SDK 工具格式
- [ ] 适配原生工具：web_search, web_crawl, read_file, write_file 等
- [ ] 适配自定义工具：propose_skill_save, propose_tool_save 等
- [ ] 适配 Sandbox 工具（Bash 包装）
- [ ] 工具权限控制（`allowed_tools`）

**Week 6: SSE 事件转换**
- [ ] 实现 `ClaudeSSEConverter`
- [ ] 拦截 SDK 工具调用 → 生成 `tool_call_start` 事件
- [ ] 拦截 SDK 工具结果 → 生成 `tool_call_end` 事件
- [ ] 提取思考内容 → 生成 `thinking` 事件
- [ ] Token 统计估算
- [ ] 事件合并与节流

**Week 7: 子 Agent 与高级功能**
- [ ] 实现子 Agent 调用（SDK Task 工具）
- [ ] 思考内容提取（DeepSeek/Claude 格式）
- [ ] 错误处理与降级策略
- [ ] 性能优化（连接池、缓存）

**产出物：**
- `backend/agent_engine/claude_engine.py`
- `backend/agent_engine/tool_adapter.py`
- `backend/agent_engine/sse_converter.py`
- `backend/agent_engine/skills_adapter.py`
- Claude SDK 引擎完整功能验证

### 4.3 Phase 3: Skills 与 Sandbox 适配 (Week 8-10)

**目标**：确保 Claude SDK 引擎支持所有现有核心功能

**Week 8: Skills 系统适配**
- [ ] 实现 Skills 加载器：读取 `builtin_skills/` 和 `Skills/`
- [ ] 将 Skills 内容注入 Claude SDK system prompt
- [ ] 支持 Skills 路由隔离（builtin-skills/ vs skills/）
- [ ] 支持 Skills 屏蔽/启用管理
- [ ] 验证所有内置 Skills 正常工作

**Week 9: Sandbox 集成**
- [ ] 将 Sandbox Bash 工具适配到 SDK 格式
- [ ] 保持 Docker 共享卷同步机制
- [ ] 支持文件读写通过 Sandbox 后端
- [ ] 支持代码执行隔离
- [ ] 安全限制（timeout, mem_limit, cpu_limit）

**Week 10: ToolUniverse 迁移**
- [ ] 将 ToolUniverse 1900+ 工具适配到 SDK 格式
- [ ] 实现工具动态发现与注册
- [ ] 保持工具元数据（描述、参数 schema）
- [ ] 性能优化：按需加载

**产出物：**
- Skills 适配层完整实现
- Sandbox 适配层完整实现
- ToolUniverse 适配层完整实现
- 端到端功能测试通过

### 4.4 Phase 4: 测试与优化 (Week 11-13)

**目标**：确保质量，性能优化，准备生产

**Week 11: 测试**
- [ ] 编写 Claude SDK 引擎单元测试（覆盖率 > 80%）
- [ ] 编写集成测试（SSE 事件、工具调用、Skills）
- [ ] A/B 测试：DeepAgents vs Claude SDK 效果对比
- [ ] 压力测试：并发会话、内存泄漏

**Week 12: 性能优化**
- [ ] 优化 SSE 事件流延迟
- [ ] 优化工具调用延迟
- [ ] 优化会话内存占用
- [ ] 优化 MongoDB 查询

**Week 13: 文档与发布**
- [ ] 更新架构文档
- [ ] 编写迁移指南
- [ ] 编写 Claude SDK 引擎使用手册
- [ ] 发布配置说明
- [ ] 代码审查与合并

**产出物：**
- 完整测试套件
- 性能基准报告
- 迁移文档
- 生产就绪的 Claude SDK 引擎

---

## 5. 核心模块重构设计

### 5.1 AgentEngine 抽象接口

```python
# backend/agent_engine/base.py
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class SSEEvent:
    """统一 SSE 事件模型 — 前端期望的格式"""
    event: str  # "message" | "tool_call_start" | "tool_call_end" | "thinking" | "plan_update" | "error" | "done"
    data: dict[str, Any]
    timestamp: float = field(default_factory=lambda: time.time())


@dataclass
class AgentSession:
    """统一会话模型"""
    session_id: str
    thread_id: str
    engine_type: str
    workspace_dir: str
    status: str = "pending"
    plan: list[dict] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentStats:
    """Agent 执行统计"""
    total_tool_calls: int = 0
    total_tool_duration_ms: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    thinking_tokens: int = 0


class AgentEngine(ABC):
    """Agent 引擎抽象基类"""

    name: str = "abstract"

    @abstractmethod
    async def create_session(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        model_config: Optional[dict] = None,
        mode: str = "deep",
    ) -> AgentSession:
        """创建新会话"""

    @abstractmethod
    async def stream_chat(
        self,
        session: AgentSession,
        message: str,
        history: list[dict],
        system_prompt: Optional[str] = None,
    ) -> AsyncGenerator[SSEEvent, None]:
        """执行流式对话，yield 统一 SSE 事件"""

    @abstractmethod
    async def cancel_session(self, session_id: str) -> None:
        """取消正在执行的会话"""

    @abstractmethod
    async def get_stats(self, session_id: str) -> AgentStats:
        """获取会话执行统计"""

    @abstractmethod
    async def list_tools(self) -> list[dict]:
        """列出当前引擎可用的工具"""

    @abstractmethod
    def supports_feature(self, feature: str) -> bool:
        """检查引擎是否支持特定功能"""
```

### 5.2 DeepAgentEngine (现有引擎包装)

```python
# backend/agent_engine/deepagents_engine.py
from backend.agent_engine.base import AgentEngine, AgentSession, SSEEvent, AgentStats
from backend.deepagent.agent import deep_agent, deep_agent_eval
from backend.deepagent.runner import arun_science_task_stream
from backend.deepagent.sessions import async_create_science_session, async_get_science_session
from backend.deepagent.sse_middleware import SSEMonitoringMiddleware


class DeepAgentEngine(AgentEngine):
    """基于现有 DeepAgents 的引擎实现 — 包装现有代码"""

    name = "deepagents"

    async def create_session(self, session_id: str, **kwargs) -> AgentSession:
        """包装现有 ScienceSession 创建逻辑"""
        science_session = await async_create_science_session(
            session_id=session_id,
            **kwargs
        )
        return AgentSession(
            session_id=science_session.session_id,
            thread_id=science_session.thread_id,
            engine_type=self.name,
            workspace_dir=str(science_session.vm_root_dir),
            status=science_session.status,
        )

    async def stream_chat(
        self,
        session: AgentSession,
        message: str,
        history: list[dict],
        system_prompt: Optional[str] = None,
    ) -> AsyncGenerator[SSEEvent, None]:
        """包装现有 runner.py 的 SSE 流"""
        science_session = await async_get_science_session(session.session_id)

        # 直接复用现有的 arun_science_task_stream
        async for event in arun_science_task_stream(
            session=science_session,
            message=message,
            history=history,
            system_prompt=system_prompt,
        ):
            # 现有事件已经是 SSEEvent 格式
            yield event

    async def cancel_session(self, session_id: str) -> None:
        """包装现有取消逻辑"""
        science_session = await async_get_science_session(session_id)
        if science_session:
            science_session.cancel()

    async def get_stats(self, session_id: str) -> AgentStats:
        """从现有中间件获取统计"""
        # 复用 sse_middleware 的统计
        ...

    async def list_tools(self) -> list[dict]:
        """返回 DeepAgents 可用工具"""
        ...

    def supports_feature(self, feature: str) -> bool:
        """DeepAgents 支持所有功能"""
        return True
```

### 5.3 ClaudeAgentEngine (新增引擎)

```python
# backend/agent_engine/claude_engine.py
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

from backend.agent_engine.base import AgentEngine, AgentSession, SSEEvent, AgentStats
from backend.agent_engine.tool_adapter import ClaudeToolAdapter
from backend.agent_engine.sse_converter import ClaudeSSEConverter
from backend.agent_engine.skills_adapter import SkillsAdapter


class ClaudeAgentEngine(AgentEngine):
    """基于 Claude Agent SDK 的引擎实现"""

    name = "claude_sdk"

    def __init__(self):
        self.tool_adapter = ClaudeToolAdapter()
        self.sse_converter = ClaudeSSEConverter()
        self.skills_adapter = SkillsAdapter()
        self._clients: dict[str, ClaudeSDKClient] = {}

    async def create_session(self, session_id: str, **kwargs) -> AgentSession:
        """创建 Claude SDK 会话"""
        # 创建 SDK Client
        client = ClaudeSDKClient(
            options=ClaudeAgentOptions(
                allowed_tools=self.tool_adapter.get_allowed_tools(),
                max_tokens=kwargs.get("max_tokens", 8192),
            )
        )
        self._clients[session_id] = client

        # 创建 workspace 目录
        workspace_dir = f"/home/scienceclaw/{session_id}"
        os.makedirs(workspace_dir, exist_ok=True)

        return AgentSession(
            session_id=session_id,
            thread_id=session_id,
            engine_type=self.name,
            workspace_dir=workspace_dir,
            status="ready",
        )

    async def stream_chat(
        self,
        session: AgentSession,
        message: str,
        history: list[dict],
        system_prompt: Optional[str] = None,
    ) -> AsyncGenerator[SSEEvent, None]:
        """使用 Claude SDK 执行流式对话"""
        client = self._clients.get(session.session_id)
        if not client:
            raise RuntimeError(f"Session {session.session_id} not found")

        # 构建 system prompt（注入 Skills）
        enhanced_prompt = self._build_system_prompt(system_prompt, session)

        # 构建消息历史
        messages = self._convert_history(history)

        # 调用 Claude SDK
        stream = await client.query(
            prompt=message,
            context={
                "system_prompt": enhanced_prompt,
                "history": messages,
                "workspace_dir": session.workspace_dir,
            }
        )

        # 转换 SDK 输出为统一 SSE 事件
        async for msg in stream:
            event = self.sse_converter.convert(msg)
            if event:
                yield event

    async def cancel_session(self, session_id: str) -> None:
        """取消 Claude SDK 会话"""
        client = self._clients.pop(session_id, None)
        if client:
            await client.close()

    async def get_stats(self, session_id: str) -> AgentStats:
        """获取 Claude SDK 会话统计"""
        # 从 SDK 或自行统计
        ...

    async def list_tools(self) -> list[dict]:
        """返回 Claude SDK 可用工具"""
        return self.tool_adapter.list_tools()

    def supports_feature(self, feature: str) -> bool:
        """Claude SDK 功能支持表"""
        supported = {
            "web_search", "web_crawl", "file_operations",
            "bash", "subagents", "thinking_extraction",
        }
        return feature in supported

    def _build_system_prompt(self, base_prompt: str | None, session: AgentSession) -> str:
        """构建增强 system prompt（含 Skills）"""
        parts = []
        if base_prompt:
            parts.append(base_prompt)

        # 注入 Skills
        skills = self.skills_adapter.load_skills(session.session_id)
        if skills:
            parts.append(self.skills_adapter.format_skills(skills))

        return "\n\n".join(parts)

    def _convert_history(self, history: list[dict]) -> list[dict]:
        """将现有消息格式转换为 Claude SDK 格式"""
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in history
        ]
```

### 5.4 工具适配层

```python
# backend/agent_engine/tool_adapter.py
from typing import Any, Callable
from claude_agent_sdk.tools import Tool

from backend.deepagent.tools import web_search, web_crawl, propose_skill_save
from backend.deepagent.tooluniverse_tools import tooluniverse_run


class ClaudeToolAdapter:
    """将现有工具适配到 Claude SDK 工具格式"""

    def __init__(self):
        self._tools: dict[str, Tool] = {}
        self._register_native_tools()
        self._register_custom_tools()

    def _register_native_tools(self):
        """注册 SDK 原生工具（直接使用）"""
        self._native_tools = {
            "read_file", "write_file", "edit_file",
            "bash", "glob", "grep",
            "web_search", "web_fetch",
        }

    def _register_custom_tools(self):
        """注册自定义工具（包装现有工具）"""
        # web_search 包装
        self._tools["web_search_scienceclaw"] = Tool(
            name="web_search_scienceclaw",
            description="Search the internet using ScienceClaw's web search service",
            handler=self._wrap_web_search,
            parameters={
                "type": "object",
                "properties": {
                    "queries": {"type": "string", "description": "Search queries separated by '|'"}
                },
                "required": ["queries"]
            }
        )

        # ToolUniverse 工具包装
        self._tools["tooluniverse_run"] = Tool(
            name="tooluniverse_run",
            description="Run a ToolUniverse scientific tool",
            handler=self._wrap_tooluniverse,
            parameters={
                "type": "object",
                "properties": {
                    "tool_name": {"type": "string"},
                    "arguments": {"type": "object"}
                },
                "required": ["tool_name", "arguments"]
            }
        )

        # Sandbox 执行包装
        self._tools["execute_sandbox"] = Tool(
            name="execute_sandbox",
            description="Execute code in isolated sandbox environment",
            handler=self._wrap_sandbox_execute,
            parameters={
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "language": {"type": "string", "enum": ["python", "bash", "javascript"]}
                },
                "required": ["code", "language"]
            }
        )

    def _wrap_web_search(self, queries: str) -> dict:
        """包装现有 web_search 工具"""
        return web_search.invoke({"queries": queries})

    def _wrap_tooluniverse(self, tool_name: str, arguments: dict) -> dict:
        """包装现有 ToolUniverse 工具"""
        return tooluniverse_run.invoke({
            "tool_name": tool_name,
            "arguments": arguments
        })

    def _wrap_sandbox_execute(self, code: str, language: str) -> dict:
        """包装 Sandbox 执行 — 调用现有 Sandbox 后端"""
        # 复用 full_sandbox_backend.py 的逻辑
        ...

    def get_allowed_tools(self) -> list[str]:
        """获取允许的工具列表"""
        return list(self._native_tools) + list(self._tools.keys())

    def list_tools(self) -> list[dict]:
        """列出所有可用工具"""
        return [
            {"name": name, "description": tool.description}
            for name, tool in self._tools.items()
        ]
```

### 5.5 Skills 适配层

```python
# backend/agent_engine/skills_adapter.py
import os
from pathlib import Path


class SkillsAdapter:
    """将现有 Skills 系统适配到 Claude SDK"""

    BUILTIN_SKILLS_DIR = "/app/builtin_skills"
    EXTERNAL_SKILLS_DIR = "/app/Skills"

    def load_skills(self, session_id: str, blocked_skills: set[str] | None = None) -> list[dict]:
        """加载所有可用 Skills"""
        skills = []

        # 加载内置 Skills
        if os.path.isdir(self.BUILTIN_SKILLS_DIR):
            for skill_dir in Path(self.BUILTIN_SKILLS_DIR).iterdir():
                if skill_dir.is_dir():
                    skill = self._load_skill(skill_dir)
                    if skill:
                        skills.append(skill)

        # 加载外置 Skills（过滤屏蔽项）
        if os.path.isdir(self.EXTERNAL_SKILLS_DIR):
            for skill_dir in Path(self.EXTERNAL_SKILLS_DIR).iterdir():
                if skill_dir.is_dir() and skill_dir.name not in (blocked_skills or set()):
                    skill = self._load_skill(skill_dir)
                    if skill:
                        skills.append(skill)

        return skills

    def _load_skill(self, skill_dir: Path) -> dict | None:
        """加载单个 Skill"""
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            return None

        content = skill_md.read_text(encoding="utf-8")
        return {
            "name": skill_dir.name,
            "path": str(skill_dir),
            "content": content,
        }

    def format_skills(self, skills: list[dict]) -> str:
        """将 Skills 格式化为 Claude SDK system prompt 片段"""
        parts = ["# Available Skills\n"]
        for skill in skills:
            parts.append(f"## Skill: {skill['name']}\n")
            parts.append(skill["content"])
            parts.append("")
        return "\n".join(parts)

    def build_system_prompt(self, base_prompt: str | None, skills: list[dict]) -> str:
        """构建完整 system prompt"""
        parts = []
        if base_prompt:
            parts.append(base_prompt)
        if skills:
            parts.append(self.format_skills(skills))
        return "\n\n".join(parts)
```

### 5.6 SSE 事件转换器

```python
# backend/agent_engine/sse_converter.py
import json
import time
from typing import Any

from backend.agent_engine.base import SSEEvent


class ClaudeSSEConverter:
    """将 Claude SDK 输出转换为前端期望的 SSE 事件格式"""

    def convert(self, msg: dict) -> SSEEvent | None:
        """转换单条 SDK 消息为 SSE 事件"""
        msg_type = msg.get("type")

        if msg_type == "text":
            return self._convert_text(msg)
        elif msg_type == "tool_use":
            return self._convert_tool_start(msg)
        elif msg_type == "tool_result":
            return self._convert_tool_end(msg)
        elif msg_type == "thinking":
            return self._convert_thinking(msg)
        elif msg_type == "error":
            return self._convert_error(msg)

        return None

    def _convert_text(self, msg: dict) -> SSEEvent:
        """转换文本消息"""
        return SSEEvent(
            event="message",
            data={
                "role": "assistant",
                "content": msg.get("content", ""),
                "timestamp": time.time(),
            }
        )

    def _convert_tool_start(self, msg: dict) -> SSEEvent:
        """转换工具调用开始"""
        return SSEEvent(
            event="tool_call_start",
            data={
                "tool_name": msg.get("name", ""),
                "tool_args": msg.get("input", {}),
                "tool_call_id": msg.get("id", ""),
                "timestamp": time.time(),
            }
        )

    def _convert_tool_end(self, msg: dict) -> SSEEvent:
        """转换工具调用结束"""
        return SSEEvent(
            event="tool_call_end",
            data={
                "tool_name": msg.get("name", ""),
                "tool_result": msg.get("output", {}),
                "tool_call_id": msg.get("id", ""),
                "duration_ms": msg.get("duration_ms", 0),
                "timestamp": time.time(),
            }
        )

    def _convert_thinking(self, msg: dict) -> SSEEvent:
        """转换思考内容"""
        return SSEEvent(
            event="thinking",
            data={
                "content": msg.get("thinking", ""),
                "timestamp": time.time(),
            }
        )

    def _convert_error(self, msg: dict) -> SSEEvent:
        """转换错误"""
        return SSEEvent(
            event="error",
            data={
                "error": msg.get("error", "Unknown error"),
                "timestamp": time.time(),
            }
        )
```

---

## 6. 代码示例

### 6.1 AgentEngine 接口定义

```python
# backend/agent_engine/base.py
"""Agent 引擎抽象层 — 统一 DeepAgents 和 Claude SDK 接口"""

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from typing import Any, Optional
import time


@dataclass
class SSEEvent:
    """统一 SSE 事件模型

    与前端期望的格式保持一致：
    {
      "event": "tool_call_start",
      "data": { ... },
    }
    """
    event: str
    data: dict[str, Any]
    timestamp: float = field(default_factory=lambda: time.time())


@dataclass
class AgentSession:
    """统一会话模型"""
    session_id: str
    thread_id: str
    engine_type: str
    workspace_dir: str
    status: str = "pending"
    plan: list[dict] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentStats:
    """Agent 执行统计"""
    total_tool_calls: int = 0
    total_tool_duration_ms: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    thinking_tokens: int = 0


class AgentEngine(ABC):
    """Agent 引擎抽象基类

    所有 Agent 引擎（DeepAgents, Claude SDK, 未来其他）必须实现此接口。
    这确保了前端路由层无需关心后端具体实现。
    """

    name: str = "abstract"

    @abstractmethod
    async def create_session(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        model_config: Optional[dict] = None,
        mode: str = "deep",
    ) -> AgentSession:
        """创建新会话

        Args:
            session_id: 会话唯一标识
            user_id: 用户 ID（可选）
            model_config: 模型配置（可选）
            mode: 会话模式（deep / chat）

        Returns:
            AgentSession 实例
        """

    @abstractmethod
    async def stream_chat(
        self,
        session: AgentSession,
        message: str,
        history: list[dict],
        system_prompt: Optional[str] = None,
    ) -> AsyncGenerator[SSEEvent, None]:
        """执行流式对话

        这是核心方法。引擎必须将内部输出转换为统一的 SSEEvent 格式。

        Args:
            session: 会话实例
            message: 用户消息
            history: 消息历史
            system_prompt: 系统提示词（可选）

        Yields:
            SSEEvent 事件流
        """

    @abstractmethod
    async def cancel_session(self, session_id: str) -> None:
        """取消正在执行的会话"""

    @abstractmethod
    async def get_stats(self, session_id: str) -> AgentStats:
        """获取会话执行统计"""

    @abstractmethod
    async def list_tools(self) -> list[dict]:
        """列出当前引擎可用的工具"""

    @abstractmethod
    def supports_feature(self, feature: str) -> bool:
        """检查引擎是否支持特定功能

        Features:
        - "web_search": 网页搜索
        - "web_crawl": 网页爬取
        - "file_operations": 文件读写
        - "bash": 命令执行
        - "subagents": 子 Agent
        - "thinking_extraction": 思考内容提取
        - "tooluniverse": ToolUniverse 集成
        - "skills": Skills 系统
        - "sandbox": Sandbox 隔离执行
        """
```

### 6.2 DeepAgentEngine 实现

```python
# backend/agent_engine/deepagents_engine.py
"""基于现有 DeepAgents 的引擎实现

此实现是对现有 `deepagent/` 代码的包装，确保：
1. 现有功能 100% 保留
2. 通过 AgentEngine 接口暴露
3. 零行为变更
"""

from typing import Optional

from backend.agent_engine.base import AgentEngine, AgentSession, SSEEvent, AgentStats
from backend.deepagent.agent import deep_agent
from backend.deepagent.runner import arun_science_task_stream
from backend.deepagent.sessions import (
    async_create_science_session,
    async_get_science_session,
    async_delete_science_session,
)


class DeepAgentEngine(AgentEngine):
    """DeepAgents 引擎 — 包装现有代码"""

    name = "deepagents"

    async def create_session(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        model_config: Optional[dict] = None,
        mode: str = "deep",
    ) -> AgentSession:
        """创建 DeepAgents 会话"""
        # 复用现有会话创建逻辑
        science_session = await async_create_science_session(
            session_id=session_id,
            user_id=user_id,
            model_config=model_config,
            mode=mode,
        )

        return AgentSession(
            session_id=science_session.session_id,
            thread_id=science_session.thread_id,
            engine_type=self.name,
            workspace_dir=str(science_session.vm_root_dir),
            status=science_session.status,
            plan=[step for step in science_session.plan],
        )

    async def stream_chat(
        self,
        session: AgentSession,
        message: str,
        history: list[dict],
        system_prompt: Optional[str] = None,
    ):
        """复用现有 runner 的 SSE 流"""
        science_session = await async_get_science_session(session.session_id)
        if not science_session:
            raise ValueError(f"Session {session.session_id} not found")

        # 直接调用现有流式执行器
        async for event in arun_science_task_stream(
            session=science_session,
            message=message,
            history=history,
            system_prompt=system_prompt,
        ):
            yield event

    async def cancel_session(self, session_id: str) -> None:
        """复用现有取消逻辑"""
        science_session = await async_get_science_session(session_id)
        if science_session:
            science_session.cancel()

    async def get_stats(self, session_id: str) -> AgentStats:
        """从现有中间件获取统计"""
        # TODO: 从 sse_middleware 获取统计
        return AgentStats()

    async def list_tools(self) -> list[dict]:
        """返回 DeepAgents 可用工具列表"""
        # TODO: 枚举现有工具
        return []

    def supports_feature(self, feature: str) -> bool:
        """DeepAgents 支持所有功能"""
        return True
```

### 6.3 ClaudeAgentEngine 实现

```python
# backend/agent_engine/claude_engine.py
"""基于 Claude Agent SDK 的引擎实现"""

import os
from typing import Optional

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

from backend.agent_engine.base import AgentEngine, AgentSession, SSEEvent, AgentStats
from backend.agent_engine.tool_adapter import ClaudeToolAdapter
from backend.agent_engine.sse_converter import ClaudeSSEConverter
from backend.agent_engine.skills_adapter import SkillsAdapter
from backend.config import settings


class ClaudeAgentEngine(AgentEngine):
    """Claude Agent SDK 引擎

    特点：
    - 基于 Claude Agent SDK 实现
    - 支持子 Agent 并行化
    - 工具权限最小化控制
    - 需要配置 ANTHROPIC_API_KEY
    """

    name = "claude_sdk"

    def __init__(self):
        self.tool_adapter = ClaudeToolAdapter()
        self.sse_converter = ClaudeSSEConverter()
        self.skills_adapter = SkillsAdapter()
        self._clients: dict[str, ClaudeSDKClient] = {}

    async def create_session(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        model_config: Optional[dict] = None,
        mode: str = "deep",
    ) -> AgentSession:
        """创建 Claude SDK 会话"""
        # 创建 SDK Client
        client = ClaudeSDKClient(
            options=ClaudeAgentOptions(
                allowed_tools=self.tool_adapter.get_allowed_tools(),
                max_tokens=model_config.get("max_tokens", 8192) if model_config else 8192,
            )
        )
        self._clients[session_id] = client

        # 创建工作区
        workspace_dir = f"/home/scienceclaw/{session_id}"
        os.makedirs(workspace_dir, exist_ok=True)

        return AgentSession(
            session_id=session_id,
            thread_id=session_id,
            engine_type=self.name,
            workspace_dir=workspace_dir,
            status="ready",
            metadata={
                "user_id": user_id,
                "mode": mode,
                "model_config": model_config or {},
            },
        )

    async def stream_chat(
        self,
        session: AgentSession,
        message: str,
        history: list[dict],
        system_prompt: Optional[str] = None,
    ):
        """使用 Claude SDK 执行流式对话"""
        client = self._clients.get(session.session_id)
        if not client:
            raise RuntimeError(f"Session {session.session_id} not found")

        # 构建增强 system prompt
        enhanced_prompt = self._build_system_prompt(system_prompt, session)

        # 转换消息历史
        messages = self._convert_history(history)

        # 调用 SDK
        stream = await client.query(
            prompt=message,
            context={
                "system_prompt": enhanced_prompt,
                "history": messages,
                "workspace_dir": session.workspace_dir,
            }
        )

        # 转换并 yield 事件
        async for msg in stream:
            event = self.sse_converter.convert(msg)
            if event:
                yield event

    async def cancel_session(self, session_id: str) -> None:
        """取消会话"""
        client = self._clients.pop(session_id, None)
        if client:
            await client.close()

    async def get_stats(self, session_id: str) -> AgentStats:
        """获取统计"""
        # TODO: 从 SDK 获取或自行统计
        return AgentStats()

    async def list_tools(self) -> list[dict]:
        """列出可用工具"""
        return self.tool_adapter.list_tools()

    def supports_feature(self, feature: str) -> bool:
        """功能支持表"""
        supported = {
            "web_search", "web_crawl", "file_operations",
            "bash", "subagents", "thinking_extraction",
        }
        return feature in supported

    def _build_system_prompt(
        self,
        base_prompt: Optional[str],
        session: AgentSession,
    ) -> str:
        """构建增强 system prompt"""
        parts = []

        if base_prompt:
            parts.append(base_prompt)

        # 注入 Skills
        skills = self.skills_adapter.load_skills(session.session_id)
        if skills:
            parts.append(self.skills_adapter.format_skills(skills))

        # 注入工具说明
        tools_text = self.tool_adapter.format_tools_for_prompt()
        if tools_text:
            parts.append(tools_text)

        return "\n\n".join(parts)

    def _convert_history(self, history: list[dict]) -> list[dict]:
        """转换消息格式"""
        converted = []
        for msg in history:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            # 处理工具消息
            if role == "tool":
                converted.append({
                    "role": "user",
                    "content": f"Tool result: {content}",
                })
            else:
                converted.append({
                    "role": role,
                    "content": content,
                })

        return converted
```

### 6.4 工具适配示例

```python
# backend/agent_engine/tool_adapter.py
"""工具适配层 — 将现有工具转换为 Claude SDK 工具格式"""

from typing import Any, Callable
import asyncio

from backend.deepagent.tools import web_search, web_crawl
from backend.deepagent.tooluniverse_tools import tooluniverse_run


class ClaudeToolAdapter:
    """工具适配器

    将 ScienceClaw 现有工具适配到 Claude SDK 的工具调用格式。
    分为三类：
    1. SDK 原生替代：直接使用 SDK 内置工具
    2. 包装工具：将现有工具包装为 SDK Tool 格式
    3. 自定义工具：完全自定义实现
    """

    # SDK 原生工具（直接使用，无需包装）
    NATIVE_TOOLS = {
        "read", "write", "edit", "bash",
        "glob", "grep", "web_search", "web_fetch",
    }

    def __init__(self):
        self._custom_tools: dict[str, dict] = {}
        self._register_custom_tools()

    def _register_custom_tools(self):
        """注册需要包装的自定义工具"""

        # 1. ScienceClaw Web Search（包装现有工具）
        self._custom_tools["web_search_scienceclaw"] = {
            "name": "web_search_scienceclaw",
            "description": (
                "Search the internet using ScienceClaw's advanced web search. "
                "Supports multiple queries separated by '|'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "queries": {
                        "type": "string",
                        "description": "One or more search queries separated by '|'"
                    }
                },
                "required": ["queries"]
            },
            "handler": self._handle_web_search,
        }

        # 2. ToolUniverse 科学工具
        self._custom_tools["tooluniverse_run"] = {
            "name": "tooluniverse_run",
            "description": (
                "Execute a ToolUniverse scientific tool. "
                "Available tools: uniprot, opentargets, pdb, faers, "
                "gwas, gtex, pubmed, arxiv, and 1900+ more."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "tool_name": {
                        "type": "string",
                        "description": "Name of the ToolUniverse tool"
                    },
                    "arguments": {
                        "type": "object",
                        "description": "Tool arguments"
                    }
                },
                "required": ["tool_name", "arguments"]
            },
            "handler": self._handle_tooluniverse,
        }

        # 3. Sandbox 代码执行
        self._custom_tools["execute_sandbox"] = {
            "name": "execute_sandbox",
            "description": (
                "Execute code in an isolated sandbox environment. "
                "Supports Python, Bash, and JavaScript. "
                "Files are persisted in the session workspace."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Code to execute"
                    },
                    "language": {
                        "type": "string",
                        "enum": ["python", "bash", "javascript"],
                        "description": "Programming language"
                    },
                    "timeout": {
                        "type": "integer",
                        "default": 60,
                        "description": "Execution timeout in seconds"
                    }
                },
                "required": ["code", "language"]
            },
            "handler": self._handle_sandbox_execute,
        }

    def _handle_web_search(self, queries: str) -> dict:
        """处理 web_search 工具调用"""
        try:
            # 调用现有工具（同步工具在异步上下文中运行）
            loop = asyncio.get_event_loop()
            result = web_search.invoke({"queries": queries})
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_tooluniverse(self, tool_name: str, arguments: dict) -> dict:
        """处理 ToolUniverse 工具调用"""
        try:
            result = tooluniverse_run.invoke({
                "tool_name": tool_name,
                "arguments": arguments
            })
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _handle_sandbox_execute(self, code: str, language: str, timeout: int = 60) -> dict:
        """处理 Sandbox 执行

        复用现有 full_sandbox_backend.py 的逻辑，
        通过 HTTP API 调用 Sandbox 服务。
        """
        # TODO: 调用 Sandbox API
        return {"success": True, "output": "Sandbox execution not yet implemented"}

    def get_allowed_tools(self) -> list[str]:
        """获取允许的工具列表（传递给 SDK）"""
        return list(self.NATIVE_TOOLS) + list(self._custom_tools.keys())

    def list_tools(self) -> list[dict]:
        """列出所有可用工具"""
        tools = []

        # SDK 原生工具
        for name in self.NATIVE_TOOLS:
            tools.append({
                "name": name,
                "type": "native",
                "description": f"Claude SDK built-in {name} tool"
            })

        # 自定义工具
        for name, tool in self._custom_tools.items():
            tools.append({
                "name": name,
                "type": "custom",
                "description": tool["description"],
            })

        return tools

    def format_tools_for_prompt(self) -> str:
        """将工具说明格式化为 prompt 片段"""
        lines = ["# Available Tools\n"]
        for name, tool in self._custom_tools.items():
            lines.append(f"## {name}")
            lines.append(tool["description"])
            lines.append("")
        return "\n".join(lines)

    def get_tool_handler(self, name: str) -> Callable | None:
        """获取工具处理函数"""
        tool = self._custom_tools.get(name)
        if tool:
            return tool["handler"]
        return None
```

### 6.5 路由层适配

```python
# backend/route/sessions.py (修改后)
"""Sessions 路由 — 支持双引擎切换"""

from fastapi import APIRouter, Depends, HTTPException
from sse_starlette.sse import EventSourceResponse

from backend.agent_engine.factory import get_engine
from backend.agent_engine.base import AgentEngine
from backend.user.dependencies import get_current_user

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/{session_id}/chat")
async def chat(
    session_id: str,
    request: ChatRequest,
    engine: AgentEngine = Depends(get_engine),  # 从工厂获取引擎
    user = Depends(get_current_user),
):
    """流式聊天 — 通过 AgentEngine 接口，无需关心具体实现"""

    # 获取或创建会话
    session = await engine.create_session(
        session_id=session_id,
        user_id=user.id,
        model_config=request.model_config,
    )

    # 构建消息历史
    history = request.messages[:-1] if request.messages else []
    message = request.messages[-1]["content"] if request.messages else ""

    # 执行流式对话
    async def event_generator():
        async for event in engine.stream_chat(
            session=session,
            message=message,
            history=history,
            system_prompt=request.system_prompt,
        ):
            yield {
                "event": event.event,
                "data": event.data,
            }

    return EventSourceResponse(event_generator())


@router.post("/{session_id}/stop")
async def stop_session(
    session_id: str,
    engine: AgentEngine = Depends(get_engine),
):
    """停止会话"""
    await engine.cancel_session(session_id)
    return {"code": 0, "msg": "ok"}
```

```python
# backend/agent_engine/factory.py
"""Agent 引擎工厂 — 根据配置创建引擎实例"""

from functools import lru_cache

from backend.config import settings
from backend.agent_engine.base import AgentEngine
from backend.agent_engine.deepagents_engine import DeepAgentEngine
from backend.agent_engine.claude_engine import ClaudeAgentEngine


@lru_cache(maxsize=1)
def _get_deepagents_engine() -> DeepAgentEngine:
    """DeepAgents 引擎单例"""
    return DeepAgentEngine()


@lru_cache(maxsize=1)
def _get_claude_engine() -> ClaudeAgentEngine:
    """Claude SDK 引擎单例"""
    return ClaudeAgentEngine()


async def get_engine(engine_type: str | None = None) -> AgentEngine:
    """获取 Agent 引擎实例

    优先级：
    1. 传入的 engine_type 参数
    2. 环境变量 AGENT_ENGINE
    3. 默认值 "deepagents"

    Args:
        engine_type: 引擎类型（"deepagents" | "claude_sdk" | "auto"）

    Returns:
        AgentEngine 实例
    """
    engine_type = engine_type or settings.AGENT_ENGINE

    if engine_type == "claude_sdk":
        return _get_claude_engine()
    elif engine_type == "deepagents":
        return _get_deepagents_engine()
    elif engine_type == "auto":
        # 自动选择：根据模型配置判断
        return _auto_select_engine()
    else:
        raise ValueError(
            f"Unknown engine type: {engine_type}. "
            f"Supported: deepagents, claude_sdk, auto"
        )


def _auto_select_engine() -> AgentEngine:
    """根据系统配置自动选择引擎"""
    # 如果有 Claude API Key，优先使用 Claude SDK
    if settings.CLAUDE_SDK_API_KEY:
        return _get_claude_engine()
    # 否则使用 DeepAgents
    return _get_deepagents_engine()


def get_engine_info() -> dict:
    """获取所有可用引擎信息"""
    return {
        "engines": [
            {
                "name": "deepagents",
                "display_name": "DeepAgents (Default)",
                "description": "LangChain + LangGraph + DeepAgents",
                "status": "active",
                "features": ["all"],
            },
            {
                "name": "claude_sdk",
                "display_name": "Claude Agent SDK",
                "description": "Anthropic Claude Agent SDK",
                "status": "beta" if settings.CLAUDE_SDK_API_KEY else "unconfigured",
                "features": [
                    "web_search", "web_crawl", "file_operations",
                    "bash", "subagents", "thinking_extraction"
                ],
            },
        ],
        "default": settings.AGENT_ENGINE,
    }
```

---

## 7. 风险评估与缓解策略

### 7.1 技术风险

| 风险 | 可能性 | 影响 | 缓解策略 |
|------|--------|------|----------|
| **Claude SDK 多模型兼容性** | 高 | 高 | 1. 保留 DeepAgents 作为后备<br>2. 仅对 Claude 模型启用 SDK 引擎<br>3. 充分测试 OpenAI 兼容模式 |
| **SSE 事件流不一致** | 中 | 高 | 1. 严格的 SSEEvent 格式定义<br>2. 端到端事件对比测试<br>3. 前端无需改动验证 |
| **Skills 系统不兼容** | 中 | 中 | 1. 保留现有 Skills 加载逻辑<br>2. 仅将 Skills 内容注入 prompt<br>3. 渐进式迁移 Skills |
| **性能下降** | 中 | 中 | 1. 基准测试对比<br>2. 连接池优化<br>3. 缓存策略 |
| **SDK 版本兼容性** | 低 | 高 | 1. 锁定 SDK 版本<br>2. 抽象层隔离变更<br>3. 持续集成测试 |
| **会话状态丢失** | 低 | 高 | 1. 双写会话状态到 MongoDB<br>2. 会话恢复机制<br>3. 健康检查 |

### 7.2 业务风险

| 风险 | 可能性 | 影响 | 缓解策略 |
|------|--------|------|----------|
| **用户体验不一致** | 中 | 高 | 1. A/B 测试验证效果<br>2. 默认保持 DeepAgents<br>3. 用户手动切换 |
| **功能缺失** | 中 | 中 | 1. 功能对照清单<br>2. 缺失功能阻断发布<br>3. 明确功能边界 |
| **运维复杂度增加** | 高 | 中 | 1. 统一监控和日志<br>2. 自动化测试覆盖<br>3. 文档完善 |

### 7.3 缓解策略

**技术缓解：**
1. **抽象层隔离**：通过 `AgentEngine` 接口隔离所有引擎差异，确保上层代码不依赖具体实现
2. **功能开关**：使用 Feature Flag 控制引擎切换，可随时回滚
3. **灰度发布**：先对 10% 用户启用 Claude SDK 引擎，逐步扩大
4. **双写持久化**：会话状态同时写入 MongoDB，确保数据安全

**业务缓解：**
1. **默认不变**：新版本默认仍使用 DeepAgents，Claude SDK 为可选
2. **明确边界**：在 UI 中标注 Claude SDK 引擎为 Beta，提示可能的功能差异
3. **快速回滚**：一键切换回 DeepAgents 的能力

---

## 8. 成本估算

### 8.1 开发成本

| 阶段 | 工作量 | 人员 | 时间 | 备注 |
|------|--------|------|------|------|
| Phase 1: 基础架构 | ~80 工时 | 1 后端资深 | 3 周 | 抽象层 + DeepAgents 包装 |
| Phase 2: SDK 核心 | ~120 工时 | 1 后端资深 | 4 周 | Claude SDK 实现 |
| Phase 3: 功能适配 | ~80 工时 | 1 后端中级 | 3 周 | Skills + Sandbox |
| Phase 4: 测试优化 | ~80 工时 | 1 测试 + 1 后端 | 3 周 | 测试 + 性能优化 |
| **总计** | **~360 工时** | **2-3 人** | **13 周** | **约 3 个月** |

### 8.2 运行成本对比

| 成本项 | DeepAgents | Claude SDK | 差异 |
|--------|-----------|-----------|------|
| API 调用费用 | 按模型计费 | 按模型计费 | 无差异（同一模型） |
| 计算资源 | 现有 Docker | 现有 Docker | 无差异 |
| 网络开销 | 中等 | 中等 | SDK 可能略高（额外封装） |
| 维护成本 | 低（稳定） | 中（新代码） | 增加 |

**结论**：运行成本无显著差异，主要成本在开发投入。

---

## 9. 成功标准

重构成功的定义：

1. **功能完整性**：Claude SDK 引擎支持现有所有核心功能（聊天、工具调用、Skills、Sandbox）
2. **接口一致性**：两种引擎的 `stream_chat` 输出事件格式 100% 一致
3. **性能基准**：Claude SDK 引擎延迟不超过 DeepAgents 引擎的 120%
4. **稳定性**：连续运行 7 天无崩溃，错误率 < 1%
5. **用户无感知切换**：前端无需任何改动即可切换引擎
6. **回滚能力**：任何时刻可在 5 分钟内回退到 DeepAgents 引擎
7. **测试覆盖**：Claude SDK 引擎代码测试覆盖率 > 80%
8. **文档完整**：所有新增代码均有文档和示例

---

## 10. 附录

### 10.1 术语表

| 术语 | 说明 |
|------|------|
| DeepAgents | LangChain 团队开发的 Agent 框架，当前项目核心依赖 |
| Claude Agent SDK | Anthropic 推出的编程式 Agent SDK |
| AgentEngine | 本项目定义的 Agent 引擎抽象接口 |
| SSE | Server-Sent Events，服务器推送事件 |
| Skills | 结构化指令文档（SKILL.md），指导 Agent 完成复杂任务 |
| ToolUniverse | 1900+ 科学工具的统合生态 |
| Sandbox | Docker 隔离的执行环境 |
| MCP | Model Context Protocol，模型上下文协议 |

### 10.2 参考资源

1. **Claude Agent SDK 文档**：官方 SDK 使用指南
2. **DeepAgents 文档**：`deepagents==0.4.4` 源码和文档
3. **ScienceClaw 现有代码**：`ScienceClaw/backend/deepagent/` 目录
4. **本项目 skills**：`claude-agent-sdk` skill（`/Users/zq/.claude/skills/claude-agent-sdk/`）
5. **LangGraph 文档**：状态图编排参考

---

> **文档维护**：本方案应随项目进展持续更新，每次重大决策和变更需记录在此文档中。
