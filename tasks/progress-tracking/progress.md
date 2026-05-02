# ScienceClaw 重构进度跟踪 — DeepAgents → Claude Agent SDK

> **项目**: ScienceClaw Backend Agent 引擎重构
> **范围**: `ScienceClaw/backend/deepagent/` → `ScienceClaw/backend/clawagent/`
> **创建日期**: 2026-05-02
> **状态**: 📋 规划中（未开始开发）
> **负责人**: TBD

---

## 使用说明

### 任务状态标记

| 标记 | 含义 | 说明 |
|------|------|------|
| ⬜ | 未开始 | 尚未开始执行 |
| 🔄 | 进行中 | 正在开发/测试中 |
| ✅ | 已完成 | 通过验收标准 |
| ❌ | 阻塞 | 依赖前置任务或遇到技术障碍 |
| ⏸️ | 暂停 | 主动暂停，等待后续决策 |

### 工时记录

| 字段 | 说明 |
|------|------|
| **预估** | 计划工时（小时） |
| **实际** | 实际花费（小时），完成后填写 |
| **偏差** | 实际 - 预估，正值表示超时 |

### 扩展跟踪字段

| 字段 | 说明 |
|------|------|
| **依赖任务** | 前置任务 ID（如 `P2-T4-9`），明确阻塞关系 |
| **负责人** | 任务 owner，多人协作时必填 |
| **实际开始** | 实际启动日期，用于计算 Cycle Time |
| **阻塞原因** | `❌` 状态时记录具体技术/资源阻塞详情 |

### 里程碑检查点 (Go/No-Go)

| 检查点 | 时间 | 通过标准 | 失败处理 |
|--------|------|----------|----------|
| CP1 | W1 结束 | `clawagent/` 目录结构完整，可独立 import | 延期 2 天或调整范围 |
| CP2 | W2 结束 | `claw_agent()` 成功创建 SDK Client，工具列表正确 | 回退到 DeepAgents |
| CP3 | W3 结束 | 单次文本对话正常，SSE 事件与旧版一致 | 回退到 DeepAgents |
| CP4 | W4 结束 | 所有内置工具 + Skills + Sandbox 正常 | 延期修复或回退 |
| CP5 | W6 结束 | 测试覆盖率 > 80%，已知 Bug 清零 | 延期修复 |
| CP6 | W8 结束 | 灰度发布无异常 | 回滚到 DeepAgents |

---

## Current Focus（当前焦点）

> **本区域动态更新**：每轮开发开始时读取，每轮结束时更新。
> **用途**：防止 AI Agent 在多轮对话中丢失上下文，防止范围蔓延。

### 当前进行中

| 任务 ID | 任务名称 | 开始时间 | 预计完成 | 当前状态 |
|---------|---------|---------|---------|---------|
| — | — | — | — | 📋 未开始开发 |

### 下一步计划

| 优先级 | 任务 ID | 任务名称 | 阻塞条件 |
|--------|---------|---------|---------|
| P0 | — | — | — |

### 当前阻塞

| 任务 ID | 阻塞原因 | 升级计划 |
|---------|---------|---------|
| — | — | — |

### 本轮对话目标

<!-- 每轮对话开始时填写：本轮要解决的具体问题 -->
- 

---

## Quick Reference（快捷参考）

### 常用命令

```bash
# 验证 clawagent/ 模块可导入
docker exec backend python -c "import backend.clawagent"

# 运行单元测试
pytest ScienceClaw/backend/clawagent/tests/ -v --cov

# SSE 事件流对比测试
python scripts/compare_sse.py --old deep --new claw

# 切换引擎
./scripts/switch-agent.sh [claw|deep]

# 检查 deepagent/ 是否被意外修改
git diff --name-only | grep deepagent/

# 检查是否有残留的旧引用
grep -r "backend.deepagent" ScienceClaw/backend/ --include="*.py"
```

### 关键文件路径

| 文件 | 路径 |
|------|------|
| AgentEngine ABC | `ScienceClaw/backend/clawagent/engine_abc.py`（规划中） |
| claw_agent() 主函数 | `ScienceClaw/backend/clawagent/agent.py` |
| Runner 流式循环 | `ScienceClaw/backend/clawagent/runner.py` |
| 中间件基类 | `ScienceClaw/backend/clawagent/middleware_base.py` |
| Backend 协议 | `ScienceClaw/backend/clawagent/backend_protocol.py` |
| 工具转换器 | `ScienceClaw/backend/clawagent/tool_converter.py` |
| SSE 协议 | `ScienceClaw/backend/clawagent/sse_protocol.py` |

### 开发检查清单（每轮必做）

- [ ] 读取 `constraints.md` 确认行为边界
- [ ] 读取本区域（Current Focus）确认当前状态
- [ ] 完成任务代码后运行 `lsp_diagnostics`
- [ ] 运行相关单元测试
- [ ] 更新 `progress.md` 任务状态 + 实际工时
- [ ] 如产生技术债务，记录到本文档末尾 "技术债务" 章节

---

## Phase 0: 准备与环境搭建

> **目标**: 建立双目录并行结构，确保开发环境与生产环境隔离，保留回滚能力
> **时间**: Week 1 (Day 1-3)
> **前置条件**: 无

### P0-T1: 目录结构准备

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P0-T1-1 | ⬜ 创建 `clawagent/` 目录 | 未开始 | 目录存在且为空 | 0.5 | - | mkdir |
| P0-T1-2 | ⬜ 复制 `deepagent/` 所有文件到 `clawagent/` | 未开始 | 文件列表一致：`diff <(ls deepagent) <(ls clawagent)` | 0.5 | - | cp -r |
| P0-T1-3 | ⬜ 验证复制完整性 | 未开始 | 文件数量、大小、权限一致 | 0.5 | - | checksum |

**验收标准**: `clawagent/` 目录与 `deepagent/` 内容完全一致，可随时作为开发基线

---

### P0-T2: 全局 Import 路径迁移

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P0-T2-1 | ⬜ 全局替换 `backend.deepagent.` → `backend.clawagent.` | 未开始 | `grep -r "backend.deepagent" backend/ --include="*.py"` 无结果 | 2.0 | - | 可能触发 5-10 处循环 import |
| P0-T2-2 | ⬜ 验证 `backend/` 内无残留 `deepagent` 引用 | 未开始 | 同上 | 0.5 | - | grep |
| P0-T2-3 | ⬜ 检查 `route/` 层的 import 更新 | 未开始 | sessions.py, chat.py 等路由文件 import 正确 | 0.5 | - | 手动检查 |
| P0-T2-4 | ⬜ 检查 `task-service/` 的 import 更新 | 未开始 | task-service 调用 backend API 的路径正确 | 0.5 | - | 如有跨服务调用 |
| P0-T2-5 | ⬜ 检查 `builtin_skills/` 脚本的 import 更新 | 未开始 | skill-creator, tool-creator 等脚本 import 正确 | 0.5 | - | 全局搜索 |
| P0-T2-6 | ⬜ 修复因路径变更导致的循环 import | 未开始 | `python -c "import backend.clawagent.agent"` 成功 | 1.0 | - | 可能触发 |

**验收标准**: 所有 Python 文件中的 `backend.deepagent.` 已替换为 `backend.clawagent.`，无语法错误

---

### P0-T3: 依赖管理更新

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P0-T3-1 | ⬜ 备份 `requirements.txt` | 未开始 | `requirements.txt.bak` 存在 | 0.1 | - | cp |
| P0-T3-2 | ⬜ 移除 `deepagents==0.4.4` | 未开始 | 文件中无 deepagents 条目 | 0.1 | - | 编辑 |
| P0-T3-3 | ⬜ 移除 `langgraph==1.0.8` | 未开始 | 文件中无 langgraph 条目 | 0.1 | - | 编辑 |
| P0-T3-4 | ⬜ 移除 `langchain-community==0.4.1` | 未开始 | 文件中无 langchain-community 条目 | 0.1 | - | 编辑 |
| P0-T3-5 | ⬜ 移除 `langchain-mcp-adapters` | 未开始 | 文件中无 langchain-mcp-adapters 条目 | 0.1 | - | 编辑 |
| P0-T3-6 | ⬜ 添加 `claude-agent-sdk>=0.1.0` | 未开始 | 文件中包含 claude-agent-sdk 条目 | 0.1 | - | 编辑 |
| P0-T3-7 | ⬜ 锁定 `langchain-core` 版本 | 未开始 | 明确版本号（如 `langchain-core==0.3.15`） | 0.1 | - | 编辑 |
| P0-T3-8 | ⬜ 创建 `requirements-claw.txt`（新环境专用） | 未开始 | 新文件包含精简依赖列表 | 0.5 | - | 可选 |
| P0-T3-9 | ⬜ 本地安装新依赖并验证 | 未开始 | `pip install -r requirements.txt` 无冲突 | 1.0 | - | 可能耗时 |
| P0-T3-10 | ⬜ 验证 `deepagent/` 仍可用旧依赖运行 | 未开始 | 旧代码 import 不报错 | 0.5 | - | 回归测试 |

**验收标准**: `pip install` 成功，无依赖冲突；新旧代码均可正常 import

---

### P0-T4: 软链接切换机制

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P0-T4-1 | ⬜ 创建 `scripts/switch-agent.sh` 脚本 | 未开始 | 脚本可执行，接受 `claw`/`deep` 参数 | 1.0 | - | bash |
| P0-T4-2 | ⬜ 脚本实现软链接切换逻辑 | 未开始 | `ln -sfn clawagent backend/active_agent` | 0.5 | - | - |
| P0-T4-3 | ⬜ 脚本实现 Docker 服务重启 | 未开始 | 切换后自动 `docker compose restart backend` | 0.5 | - | - |
| P0-T4-4 | ⬜ 脚本实现健康检查 | 未开始 | 重启后 `curl localhost:8000/health` 返回 200 | 0.5 | - | - |
| P0-T4-5 | ⬜ 创建 `backend/active_agent` 软链接（初始指向 `clawagent/`） | 未开始 | `ls -l backend/active_agent` 显示指向 clawagent | 0.2 | - | - |
| P0-T4-6 | ⬜ 验证软链接切换后后端可启动 | 未开始 | `docker compose up -d backend` 成功，日志无报错 | 1.0 | - | - |
| P0-T4-7 | ⬜ 验证切换回 `deepagent/` 后后端可启动 | 未开始 | 同上，指向 deepagent 时正常 | 0.5 | - | 回滚测试 |
| P0-T4-8 | ⬜ 记录切换脚本使用说明到文档 | 未开始 | README 包含 `./scripts/switch-agent.sh [claw|deep]` 用法 | 0.5 | - | - |

**验收标准**: 通过脚本可在 30 秒内完成 `clawagent` ↔ `deepagent` 切换，切换后服务正常

---

### P0-T5: Docker 配置调整

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P0-T5-1 | ⬜ 更新 `backend/Dockerfile` 安装 claude-agent-sdk | 未开始 | Docker build 成功 | 0.5 | - | - |
| P0-T5-2 | ⬜ 更新 `docker-compose.yml` backend 服务配置 | 未开始 | `docker compose up -d --build` 成功 | 1.0 | - | - |
| P0-T5-3 | ⬜ 添加 `ANTHROPIC_API_KEY` 环境变量到 `.env.template` | 未开始 | `.env.template` 包含新变量 | 0.2 | - | - |
| P0-T5-4 | ⬜ 添加 `AGENT_IMPL` 环境变量到配置 | 未开始 | `config.py` 读取 `AGENT_IMPL` 环境变量 | 0.5 | - | - |
| P0-T5-5 | ⬜ 验证 Docker 构建成功 | 未开始 | `docker compose build backend` 无错误 | 2.0 | - | 可能耗时 |
| P0-T5-6 | ⬜ 验证容器内 `clawagent/` 模块可导入 | 未开始 | `docker exec backend python -c "import backend.clawagent"` | 0.5 | - | - |

### P0-T6: AgentEngine ABC 接口设计（混合架构奠基）

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P0-T6-1 | ⬜ 设计 `AgentEngine` 抽象基类 | 未开始 | 含 `create_agent()` / `stream()` / `get_tool_event_adapter()` 抽象方法 | 2.0 | - | 架构核心 |
| P0-T6-2 | ⬜ 实现 `DeepAgentEngine`（包装现有 `deep_agent()`） | 未开始 | 继承 AgentEngine，委托给现有 deepagent 代码 | 1.5 | - | 适配层 |
| P0-T6-3 | ⬜ 实现 `ClaudeAgentEngine`（桩实现） | 未开始 | 继承 AgentEngine，方法体留空（后续 Phase 填充） | 1.0 | - | 占位 |
| P0-T6-4 | ⬜ 编写 Engine 工厂 `get_agent_engine(impl: str)` | 未开始 | `get_agent_engine("claude")` / `get_agent_engine("deep")` 返回正确实例 | 1.0 | - | - |
| P0-T6-5 | ⬜ 单元测试：工厂路由正确 | 未开始 | pytest 通过 | 1.0 | - | - |

**验收标准**: `AgentEngine` ABC 定义清晰，`DeepAgentEngine` 可包装现有代码正常工作，`ClaudeAgentEngine` 桩可实例化

---

### P0-T7: 回滚演练与知识转移

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P0-T7-1 | ⬜ 团队 Claude SDK API 培训 | 未开始 | 团队成员完成 SDK 入门（预估 1 天 vs DeepAgents 5 天） | 4.0 | - | 减少后期学习成本 |
| P0-T7-2 | ⬜ 紧急回滚演练（模拟生产故障） | 未开始 | 5 分钟内通过 `switch-agent.sh deep` 恢复服务 | 1.0 | - | 验证灾备可用 |
| P0-T7-3 | ⬜ 编写 Phase 0 技术决策记录 | 未开始 | `docs/decisions/phase0.md` 记录关键选择 | 0.5 | - | ADR |

---

**Phase 0 验收**: 
- [ ] `clawagent/` 目录完整且可独立 import
- [ ] `AgentEngine` ABC 设计完成，`DeepAgentEngine` 可正常工作
- [ ] 软链接切换机制正常工作（双向）
- [ ] Docker 构建成功，容器可启动
- [ ] 全局 import 路径替换完成，无残留
- [ ] 依赖安装无冲突
- [ ] 紧急回滚演练通过（5 分钟内恢复）

---

### Phase 0 → Phase 1 过渡

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P0-CR | ⬜ Phase 0 Code Review | 未开始 | 审查清单全部通过（架构决策 + 接口设计 + 安全审查） | 2.0 | - | 阻塞项必须修复才能进入 P1 |
| P0-BUF | ⬜ Buffer Time（缓冲） | 未开始 | 处理 P0 遗留问题或提前开始 P1 | 4.0 | - | 约 P0 工时的 15% |

---

## Phase 1: 基础设施搭建

> **目标**: 建立自建的中间件基类和 Backend 协议，替换 DeepAgents/LangChain 的基类依赖
> **时间**: Week 1 (Day 4-7)
> **前置条件**: Phase 0 完成

### P1-T1: 自建中间件基础设施

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P1-T1-1 | ⬜ 创建 `clawagent/middleware_base.py` | 未开始 | 文件存在 | 0.2 | - | - |
| P1-T1-2 | ⬜ 实现 `ClawMiddleware` 抽象基类 | 未开始 | 类存在，含 `wrap_tool_call` / `awrap_tool_call` / `clear` 方法 | 0.5 | - | - |
| P1-T1-3 | ⬜ 实现 `MiddlewareStack` 类（同步版本） | 未开始 | `stack.run(request, handler)` 按顺序调用中间件 | 1.0 | - | 洋葱模型 |
| P1-T1-4 | ⬜ 实现 `MiddlewareStack` 类（异步版本 `arun`） | 未开始 | `await stack.arun(request, handler)` 工作正常 | 1.0 | - | - |
| P1-T1-5 | ⬜ 编写中间件基类单元测试 | 未开始 | pytest 通过，覆盖率 100% | 1.0 | - | - |
| P1-T1-6 | ⬜ 测试中间件链式调用顺序 | 未开始 | 3 个中间件按预期顺序执行 | 0.5 | - | - |
| P1-T1-7 | ⬜ 测试中间件异常透传 | 未开始 | 中间件抛出的异常正确向上传播 | 0.5 | - | - |

**验收标准**: `MiddlewareStack` 支持多个中间件顺序调用，同步/异步模式均正常工作

---

### P1-T2: 自建 Backend 协议

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P1-T2-1 | ⬜ 创建 `clawagent/backend_protocol.py` | 未开始 | 文件存在 | 0.2 | - | - |
| P1-T2-2 | ⬜ 定义 `FileOperation` 数据类族 | 未开始 | FileRead/FileWrite/FileEdit/FileList/FileGlob/FileGrep 均定义 | 0.5 | - | dataclass |
| P1-T2-3 | ⬜ 实现 `FilesystemBackend` 基类 | 未开始 | 含 read/write/edit/ls/glob/grep 方法 | 1.0 | - | - |
| P1-T2-4 | ⬜ 实现虚拟路径解析 (`_resolve_path`) | 未开始 | 路径逃逸检查正确 | 1.0 | - | 安全关键 |
| P1-T2-5 | ⬜ 实现 `CompositeBackend` 类 | 未开始 | 根据路径前缀路由到不同后端 | 1.0 | - | - |
| P1-T2-6 | ⬜ 编写 Backend 协议单元测试 | 未开始 | pytest 通过 | 1.5 | - | - |
| P1-T2-7 | ⬜ 测试路径逃逸防护 | 未开始 | `../../../etc/passwd` 被拦截 | 0.5 | - | 安全测试 |
| P1-T2-8 | ⬜ 测试 CompositeBackend 路由 | 未开始 | `/builtin-skills/` 和 `/skills/` 路由正确 | 0.5 | - | - |

**验收标准**: `FilesystemBackend` 和 `CompositeBackend` 通过全部单元测试，路径逃逸防护有效

---

### P1-T3: SSEMonitoringMiddleware 适配

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P1-T3-1 | ⬜ 修改 `sse_middleware.py` 继承 `ClawMiddleware` | 未开始 | `class SSEMonitoringMiddleware(ClawMiddleware)` | 0.2 | - | - |
| P1-T3-2 | ⬜ 移除 `super().__init__()` 调用 | 未开始 | 初始化不报错 | 0.2 | - | - |
| P1-T3-3 | ⬜ 保留 `_before_tool` / `_after_tool` 逻辑 | 未开始 | 方法实现与原版一致 | 0.2 | - | - |
| P1-T3-4 | ⬜ 保留 `wrap_tool_call` 逻辑 | 未开始 | 方法实现与原版一致 | 0.2 | - | - |
| P1-T3-5 | ⬜ 保留 `drain_events` 逻辑 | 未开始 | 事件队列轮询正常 | 0.2 | - | - |
| P1-T3-6 | ⬜ 保留统计字段 (total_tool_calls 等) | 未开始 | 统计正确累加 | 0.2 | - | - |
| P1-T3-7 | ⬜ 编写 SSEMonitoringMiddleware 单元测试 | 未开始 | mock 工具调用，验证事件生成 | 1.0 | - | - |
| P1-T3-8 | ⬜ 测试工具调用前后事件捕获 | 未开始 | `middleware_tool_start` / `middleware_tool_complete` 正确 | 0.5 | - | - |
| P1-T3-9 | ⬜ 测试 todolist 变化检测 | 未开始 | `write_todos` 触发 `middleware_todos_update` | 0.5 | - | - |
| P1-T3-10 | ⬜ 测试线程安全性 | 未开始 | 多线程并发添加事件不丢数据 | 0.5 | - | - |

**验收标准**: `SSEMonitoringMiddleware` 适配后功能与原版 100% 一致，单元测试全部通过

---

### P1-T4: ToolResultOffloadMiddleware 适配

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P1-T4-1 | ⬜ 修改 `offload_middleware.py` 继承 `ClawMiddleware` | 未开始 | 类声明更新 | 0.2 | - | - |
| P1-T4-2 | ⬜ 移除 `langchain.agents.middleware` import | 未开始 | 无 langchain import | 0.2 | - | - |
| P1-T4-3 | ⬜ 保留大结果判断逻辑 (`_should_offload`) | 未开始 | 逻辑与原版一致 | 0.2 | - | - |
| P1-T4-4 | ⬜ 保留文件写入逻辑 (`_offload_result`) | 未开始 | 逻辑与原版一致 | 0.2 | - | - |
| P1-T4-5 | ⬜ 保留同步/异步桥接逻辑 | 未开始 | sync/async 均正常工作 | 0.5 | - | 如需保留 |
| P1-T4-6 | ⬜ 编写 offload 中间件单元测试 | 未开始 | pytest 通过 | 0.5 | - | - |
| P1-T4-7 | ⬜ 测试阈值触发（>3000 字符落盘） | 未开始 | 大结果被写入文件 | 0.5 | - | - |
| P1-T4-8 | ⬜ 测试摘要生成 | 未开始 | 返回的摘要包含文件路径引用 | 0.5 | - | - |

**验收标准**: `ToolResultOffloadMiddleware` 适配后功能与原版一致

---

### P1-T5: FilteredFilesystemBackend 适配

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P1-T5-1 | ⬜ 修改 `filtered_backend.py` 继承自建 `FilesystemBackend` | 未开始 | 类声明更新 | 0.2 | - | - |
| P1-T5-2 | ⬜ 移除 `deepagents.backends.filesystem` import | 未开始 | 无 deepagents import | 0.2 | - | - |
| P1-T5-3 | ⬜ 保留 `blocked_skills` 过滤逻辑 | 未开始 | 被屏蔽的 skills 目录不可见 | 0.5 | - | - |
| P1-T5-4 | ⬜ 编写 filtered backend 单元测试 | 未开始 | pytest 通过 | 0.5 | - | - |
| P1-T5-5 | ⬜ 测试屏蔽功能 | 未开始 | `blocked_skills={"weather"}` 时 weather 不可见 | 0.5 | - | - |

**验收标准**: `FilteredFilesystemBackend` 屏蔽功能正常

---

### P1-T6: FullSandboxBackend 适配

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P1-T6-1 | ⬜ 修改 `full_sandbox_backend.py` 替换协议类型 | 未开始 | 使用自建 `FileOperation` 类型 | 0.5 | - | - |
| P1-T6-2 | ⬜ 移除 `deepagents.backends.protocol` import | 未开始 | 无 deepagents import | 0.2 | - | - |
| P1-T6-3 | ⬜ 保留 Sandbox HTTP API 调用逻辑 | 未开始 | 与原版一致 | 0.5 | - | - |
| P1-T6-4 | ⬜ 保留同步/异步桥接 (`_run_sync`) | 未开始 | 如保留，功能正常 | 0.5 | - | - |
| P1-T6-5 | ⬜ 编写 sandbox backend 单元测试 | 未开始 | pytest 通过（mock HTTP） | 1.0 | - | - |
| P1-T6-6 | ⬜ 测试文件读写通过 sandbox | 未开始 | mock 返回正确数据 | 0.5 | - | - |
| P1-T6-7 | ⬜ 测试命令执行通过 sandbox | 未开始 | mock 返回正确数据 | 0.5 | - | - |

**Phase 1 验收**:
- [ ] `middleware_base.py` 通过单元测试
- [ ] `backend_protocol.py` 通过单元测试，路径逃逸防护有效
- [ ] `sse_middleware.py` 适配后功能与原版一致
- [ ] `offload_middleware.py` 适配后功能与原版一致
- [ ] `filtered_backend.py` 适配后屏蔽功能正常
- [ ] `full_sandbox_backend.py` 适配后 sandbox 调用正常
- [ ] 所有基础设施代码可独立 import，无框架依赖

---

## Phase 2: Agent 核心重写

> **目标**: 将 `deep_agent()` 函数从 `create_deep_agent()` 迁移到 `ClaudeSDKClient`
> **时间**: Week 2 (Day 8-14)
> **前置条件**: Phase 1 完成

### P2-T1: 工具转换层

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P2-T1-1 | ⬜ 创建 `clawagent/tool_converter.py` | 未开始 | 文件存在 | 0.2 | - | - |
| P2-T1-2 | ⬜ 实现 `convert_langchain_tool_to_sdk()` | 未开始 | LangChain Tool → SDK Tool 转换 | 1.0 | - | - |
| P2-T1-3 | ⬜ 实现 `create_sdk_tool()` 工厂函数 | 未开始 | 直接创建 SDK Tool | 0.5 | - | - |
| P2-T1-4 | ⬜ 实现 JSON Schema 提取（从 LangChain tool） | 未开始 | `args_schema.model_json_schema()` 正确提取 | 1.0 | - | - |
| P2-T1-5 | ⬜ 编写工具转换单元测试 | 未开始 | pytest 通过 | 1.0 | - | - |
| P2-T1-6 | ⬜ 测试 web_search 工具转换 | 未开始 | 转换后的 SDK Tool 可调用 | 0.5 | - | - |
| P2-T1-7 | ⬜ 测试工具执行结果透传 | 未开始 | 原始工具返回值完整传递 | 0.5 | - | - |

---

### P2-T2: 工具包装（中间件注入）

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P2-T2-1 | ⬜ 实现 `_wrap_tool_with_middleware()` | 未开始 | 工具调用前后触发中间件 | 1.5 | - | 核心逻辑 |
| P2-T2-2 | ⬜ 包装 `_STATIC_TOOLS` 中的所有工具 | 未开始 | 每个工具都经过中间件 | 0.5 | - | - |
| P2-T2-3 | ⬜ 包装外部扩展工具（`reload_external_tools()`） | 未开始 | Tools/ 目录工具也包装 | 0.5 | - | - |
| P2-T2-4 | ⬜ 测试工具包装后的中间件触发 | 未开始 | 调用工具时 SSEMonitoringMiddleware 记录事件 | 1.0 | - | - |
| P2-T2-5 | ⬜ 测试大结果落盘中间件触发 | 未开始 | 大结果自动写入文件 | 0.5 | - | - |
| P2-T2-6 | ⬜ 性能测试：工具包装开销 | 未开始 | 单工具调用额外开销 < 5ms | 0.5 | - | - |

---

### P2-T3: 子 Agent 工具实现

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P2-T3-1 | ⬜ 实现 `_build_subagent_tools()` | 未开始 | 返回 SDK Task 工具 | 1.0 | - | - |
| P2-T3-2 | ⬜ 实现子 Agent handler（独立 Client） | 未开始 | 创建独立 `ClaudeSDKClient` | 1.0 | - | 上下文隔离 |
| P2-T3-3 | ⬜ 实现子 Agent 结果返回格式 | 未开始 | 结果可被父 Agent 消费 | 0.5 | - | - |
| P2-T3-4 | ⬜ 编写子 Agent 单元测试 | 未开始 | pytest 通过 | 1.0 | - | - |
| P2-T3-5 | ⬜ 测试子 Agent 独立上下文 | 未开始 | 子 Agent 的工具调用不污染父 Agent | 0.5 | - | - |
| P2-T3-6 | ⬜ 测试子 Agent 错误隔离 | 未开始 | 子 Agent 失败不影响父 Agent | 0.5 | - | - |

---

### P2-T4: `claw_agent()` 主函数实现

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P2-T4-1 | ⬜ 定义 `claw_agent()` 函数签名 | 未开始 | 与 `deep_agent()` 参数一致 | 0.2 | - | - |
| P2-T4-2 | ⬜ 集成模型创建（复用 `get_llm_model`） | 未开始 | 返回正确的模型实例 | 0.5 | - | - |
| P2-T4-3 | ⬜ 集成工具收集（复用 `_collect_tools`） | 未开始 | 内置 + 外部工具合并 | 0.5 | - | - |
| P2-T4-4 | ⬜ 集成系统提示词（复用 `get_system_prompt`） | 未开始 | prompt 格式正确 | 0.5 | - | - |
| P2-T4-5 | ⬜ 集成 Backend 组装（复用 `_build_backend`） | 未开始 | CompositeBackend 路由正确 | 0.5 | - | - |
| P2-T4-6 | ⬜ 集成中间件栈创建 | 未开始 | SSE + Offload 中间件正确组装 | 0.5 | - | - |
| P2-T4-7 | ⬜ 集成工具包装（中间件注入） | 未开始 | 所有工具经过中间件 | 0.5 | - | - |
| P2-T4-8 | ⬜ 集成子 Agent 工具 | 未开始 | Task 工具注册到 Client | 0.5 | - | - |
| P2-T4-9 | ⬜ 创建 `ClaudeSDKClient` | 未开始 | Client 初始化成功 | 1.0 | - | - |
| P2-T4-10 | ⬜ 注册所有工具到 Client | 未开始 | `client.register_tool()` 调用正确 | 0.5 | - | - |
| P2-T4-11 | ⬜ 集成诊断日志 | 未开始 | DiagnosticLogger 附加到中间件 | 0.5 | - | - |
| P2-T4-12 | ⬜ 实现 `claw_agent_eval()`（Eval 模式） | 未开始 | 类似 `claw_agent()` 但使用 eval prompt | 1.0 | - | - |
| P2-T4-13 | ⬜ 编写 `claw_agent()` 集成测试 | 未开始 | pytest 通过 | 3.0 | - | 需 mock SDK Client，复杂度较高 |
| P2-T4-14 | ⬜ 测试正常路径：Client + 中间件 + 工具 | 未开始 | 返回 (client, middleware, cw, diag) | 1.0 | - | - |
| P2-T4-15 | ⬜ 测试工具屏蔽路径 | 未开始 | blocked_tools 正确过滤 | 0.5 | - | - |
| P2-T4-16 | ⬜ 测试 Skills 屏蔽路径 | 未开始 | blocked_skills 正确过滤 | 0.5 | - | - |
| P2-T4-17 | ⬜ 测试外部工具热加载 | 未开始 | Tools/ 变更后重新加载 | 1.0 | - | - |

---

### P2-T5: 引擎切换机制（混合架构核心）

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P2-T5-1 | ⬜ 实现 `AGENT_IMPL` 环境变量读取 | 未开始 | `config.py` 读取并校验 `claude`/`deep` | 0.5 | - | - |
| P2-T5-2 | ⬜ 实现会话级引擎选择（覆盖全局配置） | 未开始 | `session.model_config` 可指定引擎 | 1.0 | - | 用户粒度的 A/B 测试基础 |
| P2-T5-3 | ⬜ 实现 `ClaudeAgentEngine.create_agent()`（填充桩） | 未开始 | 委托给 `claw_agent()`，返回符合 ABC 接口 | 1.0 | - | - |
| P2-T5-4 | ⬜ 实现 `ClaudeAgentEngine.stream()`（包装 runner） | 未开始 | 委托给 `arun_science_task_stream()`，SSE 事件格式一致 | 1.5 | - | 核心适配 |
| P2-T5-5 | ⬜ 实现 `DeepAgentEngine` 与 `ClaudeAgentEngine` 的统一事件适配 | 未开始 | 两种引擎输出的 SSE 事件 100% 格式一致 | 2.0 | - | 前端无感切换 |
| P2-T5-6 | ⬜ 编写引擎切换单元测试 | 未开始 | `get_agent_engine("claude")` 和 `get_agent_engine("deep")` 均通过 | 1.0 | - | - |
| P2-T5-7 | ⬜ 编写 A/B 测试基础设施（用户分流） | 未开始 | 按 user_id hash 分配引擎 | 1.0 | - | 为 P6 对比测试做准备 |

**验收标准**: 通过 `AGENT_IMPL` 或会话配置可在 `DeepAgentEngine` 与 `ClaudeAgentEngine` 间切换，前端 SSE 事件格式无差异

---

**Phase 2 验收**:
- [ ] `claw_agent()` 可成功创建 SDK Client
- [ ] `ClaudeAgentEngine` 实现完整，可通过工厂实例化
- [ ] 引擎切换机制工作正常（环境变量 + 会话级）
- [ ] 工具列表正确（内置 + 外部扩展）
- [ ] 中间件事件在工具调用前后触发
- [ ] 子 Agent 工具可调用
- [ ] 诊断日志正常附加
- [ ] 工具屏蔽和 Skills 屏蔽功能正常
- [ ] 单元测试覆盖率 > 80%

---

### Phase 2 → Phase 3 过渡

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P2-CR | ⬜ Phase 2 Code Review | 未开始 | 审查清单通过（引擎切换逻辑 + Client 组装 + 子 Agent 隔离） | 2.0 | - | - |
| P2-BUF | ⬜ Buffer Time（缓冲） | 未开始 | 处理 P2 遗留问题 | 6.0 | - | 约 P2 工时的 15% |

---

## Phase 3: Runner 流式循环重写

> **目标**: 将 `agent.astream()` 双模式循环替换为 `client.query()` 单模式循环
> **时间**: Week 3 (Day 15-21)
> **前置条件**: Phase 2 完成

### P3-T1: 流式循环骨架

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P3-T1-1 | ⬜ 保留现有初始事件序列代码 | 未开始 | thinking + step_start + plan_update 事件 | 0.2 | - | - |
| P3-T1-2 | ⬜ 保留 `_build_history_messages()` | 未开始 | 历史消息构建逻辑 | 0.2 | - | - |
| P3-T1-3 | ⬜ 保留 `_compute_history_token_budget()` | 未开始 | Token 预算计算 | 0.2 | - | - |
| P3-T1-4 | ⬜ 保留附件处理逻辑 | 未开始 | 附件路径注入 query | 0.2 | - | - |
| P3-T1-5 | ⬜ 保留超时处理逻辑 | 未开始 | `asyncio.timeout(STREAM_TIMEOUT)` | 0.2 | - | - |
| P3-T1-6 | ⬜ 调用 `claw_agent()` 替代 `deep_agent()` | 未开始 | 获取 client, middleware, context_window, diagnostic | 0.5 | - | - |
| P3-T1-7 | ⬜ 调用 `client.query()` 替代 `agent.astream()` | 未开始 | 返回流式消息 | 2.0 | - | 核心替换，流式行为可能与预期不符 |
| P3-T1-8 | ⬜ 移除 `stream_mode=["messages", "updates"]` | 未开始 | 无双模式参数 | 0.2 | - | - |
| P3-T1-9 | ⬜ 移除 `configurable={"thread_id": ...}` | 未开始 | 无 thread_id 配置 | 0.2 | - | - |

---

### P3-T2: SDK 消息类型处理

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P3-T2-1 | ⬜ 实现 `msg_type == "text"` 处理 | 未开始 | 生成 `thinking` SSE 事件 | 0.5 | - | - |
| P3-T2-2 | ⬜ 实现 `msg_type == "thinking"` 处理 | 未开始 | 提取 reasoning_content | 0.5 | - | - |
| P3-T2-3 | ⬜ 实现 `msg_type == "tool_use"` 处理 | 未开始 | 生成 `tool_call_start` SSE 事件 | 1.0 | - | - |
| P3-T2-4 | ⬜ 实现 `msg_type == "tool_result"` 处理 | 未开始 | 生成 `tool_call_end` SSE 事件 | 1.0 | - | - |
| P3-T2-5 | ⬜ 实现未知消息类型容错 | 未开始 | 不认识的 type 安全跳过 | 0.5 | - | - |
| P3-T2-6 | ⬜ 移除 `langgraph_node` metadata 检查 | 未开始 | 无 node_name 过滤 | 0.2 | - | - |
| P3-T2-7 | ⬜ 移除 `_chunks_had_reasoning` 状态标记 | 未开始 | 无重复发送防护状态机 | 0.2 | - | - |
| P3-T2-8 | ⬜ 移除 `_chunks_had_text` 状态标记 | 未开始 | 同上 | 0.2 | - | - |

---

### P3-T3: 中间件事件轮询集成

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P3-T3-1 | ⬜ 保留每次迭代轮询中间件事件 | 未开始 | `for mw_evt in middleware.drain_events()` | 0.2 | - | - |
| P3-T3-2 | ⬜ 保留中间件事件缓存 (`_mw_cache`) | 未开始 | tool_call_id 关联正确 | 0.2 | - | - |
| P3-T3-3 | ⬜ 保留 tool_start 事件增强 | 未开始 | tool_meta 注入 | 0.2 | - | - |
| P3-T3-4 | ⬜ 保留 tool_complete 事件增强 | 未开始 | duration_ms + tool_meta 注入 | 0.2 | - | - |
| P3-T3-5 | ⬜ 保留 todolist 变化检测 | 未开始 | `middleware_todos_update` → `plan_update` | 0.5 | - | - |
| P3-T3-6 | ⬜ 测试中间件事件与 SDK 事件合并 | 未开始 | 两种事件流正确交织 | 1.0 | - | - |

---

### P3-T4: 最终消息格式化

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P3-T4-1 | ⬜ 保留最终 `message` 事件生成 | 未开始 | 包含 content + thinking + token 统计 | 0.5 | - | - |
| P3-T4-2 | ⬜ 保留 `_extract_thinking()` 调用 | 未开始 | thinking 内容正确提取 | 0.2 | - | - |
| P3-T4-3 | ⬜ 保留 Token 统计字段 | 未开始 | input_tokens / output_tokens | 0.2 | - | - |
| P3-T4-4 | ⬜ 保留 Session 状态更新 | 未开始 | status / title / latest_message 更新 | 0.5 | - | - |
| P3-T4-5 | ⬜ 保留取消检查逻辑 | 未开始 | `session.is_cancelled()` 响应 | 0.2 | - | - |
| P3-T4-6 | ⬜ 保留错误处理（超时/异常） | 未开始 | error 事件格式 | 0.5 | - | - |
| P3-T4-7 | ⬜ 保留诊断日志保存 | 未开始 | `diagnostic.save()` 调用 | 0.2 | - | - |

---

### P3-T5: 流式输出测试

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P3-T5-1 | ⬜ 编写 runner 集成测试 | 未开始 | pytest 通过 | 2.0 | - | - |
| P3-T5-2 | ⬜ 测试纯文本对话流 | 未开始 | SSE 事件流正确 | 0.5 | - | - |
| P3-T5-3 | ⬜ 测试工具调用流 | 未开始 | tool_call_start + tool_call_end 成对出现 | 1.0 | - | - |
| P3-T5-4 | ⬜ 测试 thinking 内容提取 | 未开始 | reasoning_content 正确透传 | 0.5 | - | - |
| P3-T5-5 | ⬜ 测试取消功能 | 未开始 | 取消后 stream 立即停止 | 0.5 | - | - |
| P3-T5-6 | ⬜ 测试超时功能 | 未开始 | 超时后 error 事件 | 0.5 | - | - |
| P3-T5-7 | ⬜ 测试附件上传 | 未开始 | 附件路径正确注入 | 0.5 | - | - |
| P3-T5-8 | ⬜ SSE 事件流对比测试 | 未开始 | 新旧版本输出格式 100% 匹配 | 3.0 | - | 项目最关键回归测试 |
| P3-T5-9 | ⬜ 编写对比测试脚本 | 未开始 | 自动对比新旧版本 SSE 输出 | 1.0 | - | - |
| P3-T5-10 | ⬜ 运行对比测试并记录差异 | 未开始 | 差异清单（如有） | 1.0 | - | - |
| P3-T5-11 | ⬜ 修复对比测试发现的差异 | 未开始 | 所有差异修复或确认可接受 | 2.0 | - | - |

**Phase 3 验收**:
- [ ] 文本对话可正常输出（含 thinking）
- [ ] 工具调用前后 SSE 事件正确
- [ ] 最终 message 事件格式与旧版 100% 一致
- [ ] 取消功能正常
- [ ] SSE 对比测试通过
- [ ] 首 token 延迟不超过旧版 120%

---

## Phase 4: 工具与 Skills 适配

> **目标**: 验证所有内置工具、Skills、Sandbox、ToolUniverse 在新引擎下正常工作
> **时间**: Week 4 (Day 22-28)
> **前置条件**: Phase 3 完成

### P4-T1: 内置工具验证

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P4-T1-1 | ⬜ 测试 `web_search` | 未开始 | 返回搜索结果 | 0.5 | - | - |
| P4-T1-2 | ⬜ 测试 `web_crawl` | 未开始 | 返回网页内容 | 0.5 | - | - |
| P4-T1-3 | ⬜ 测试 `read_file` | 未开始 | 读取 workspace 文件 | 0.5 | - | - |
| P4-T1-4 | ⬜ 测试 `write_file` | 未开始 | 写入 workspace 文件 | 0.5 | - | - |
| P4-T1-5 | ⬜ 测试 `edit_file` | 未开始 | 修改文件内容 | 0.5 | - | - |
| P4-T1-6 | ⬜ 测试 `execute` / `bash` | 未开始 | 在 sandbox 执行命令 | 0.5 | - | - |
| P4-T1-7 | ⬜ 测试 `glob` | 未开始 | 文件搜索 | 0.5 | - | - |
| P4-T1-8 | ⬜ 测试 `grep` | 未开始 | 内容搜索 | 0.5 | - | - |
| P4-T1-9 | ⬜ 测试 `propose_skill_save` | 未开始 | Skill 提案生成 | 0.5 | - | - |
| P4-T1-10 | ⬜ 测试 `propose_tool_save` | 未开始 | Tool 提案生成 | 0.5 | - | - |
| P4-T1-11 | ⬜ 测试 `eval_skill` | 未开始 | Skill 评估 | 0.5 | - | - |
| P4-T1-12 | ⬜ 测试 `grade_eval` | 未开始 | 评分评估 | 0.5 | - | - |

---

### P4-T2: ToolUniverse 工具验证

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P4-T2-1 | ⬜ 测试 `tooluniverse_search` | 未开始 | 搜索科学工具 | 0.5 | - | - |
| P4-T2-2 | ⬜ 测试 `tooluniverse_info` | 未开始 | 获取工具信息 | 0.5 | - | - |
| P4-T2-3 | ⬜ 测试 `tooluniverse_run`（生物工具） | 未开始 | UniProt / PDB 等 | 1.5 | - | 依赖外部服务，网络不稳定 |
| P4-T2-4 | ⬜ 测试 `tooluniverse_run`（天文工具） | 未开始 | SIMBAD / SDSS 等 | 1.5 | - | 依赖外部服务，网络不稳定 |
| P4-T2-5 | ⬜ 测试 `tooluniverse_run`（化学工具） | 未开始 | COD / SMILES 等 | 1.5 | - | 依赖外部服务，网络不稳定 |
| P4-T2-6 | ⬜ 测试 `tooluniverse_run`（文献工具） | 未开始 | PubMed / arXiv 等 | 1.5 | - | 依赖外部服务，网络不稳定 |
| P4-T2-7 | ⬜ 编写 ToolUniverse 集成测试（抽样） | 未开始 | 每类学科至少测试 1 个工具 | 2.0 | - | - |

---

### P4-T3: Skills 系统验证

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P4-T3-1 | ⬜ 测试内置 Skills 加载 | 未开始 | `/app/builtin_skills/` 下的 Skills 可读 | 0.5 | - | - |
| P4-T3-2 | ⬜ 测试外置 Skills 加载 | 未开始 | `/app/Skills/` 下的 Skills 可读 | 0.5 | - | - |
| P4-T3-3 | ⬜ 测试 Skills 路由隔离 | 未开始 | builtin-skills/ 和 skills/ 路由正确 | 0.5 | - | - |
| P4-T3-4 | ⬜ 测试 Skills 屏蔽功能 | 未开始 | blocked_skills 生效 | 0.5 | - | - |
| P4-T3-5 | ⬜ 测试 Skills 注入 system prompt | 未开始 | Skill 内容出现在 prompt 中 | 1.0 | - | - |
| P4-T3-6 | ⬜ 测试 pdf Skill | 未开始 | PDF 生成正常 | 1.0 | - | - |
| P4-T3-7 | ⬜ 测试 docx Skill | 未开始 | DOCX 生成正常 | 1.0 | - | - |
| P4-T3-8 | ⬜ 测试 pptx Skill | 未开始 | PPTX 生成正常 | 1.0 | - | - |
| P4-T3-9 | ⬜ 测试 xlsx Skill | 未开始 | XLSX 生成正常 | 1.0 | - | - |
| P4-T3-10 | ⬜ 测试 deep-research Skill | 未开始 | 深度研究流程正常 | 1.0 | - | - |
| P4-T3-11 | ⬜ 测试 skill-creator Skill | 未开始 | Skill 创建流程正常 | 1.0 | - | - |
| P4-T3-12 | ⬜ 测试 tool-creator Skill | 未开始 | Tool 创建流程正常 | 1.0 | - | - |

---

### P4-T4: Sandbox 隔离验证

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P4-T4-1 | ⬜ 测试 Python 脚本执行 | 未开始 | `print("hello")` 返回正确 | 0.5 | - | - |
| P4-T4-2 | ⬜ 测试 Bash 脚本执行 | 未开始 | `ls -la` 返回正确 | 0.5 | - | - |
| P4-T4-3 | ⬜ 测试 JavaScript 脚本执行 | 未开始 | `console.log` 返回正确 | 0.5 | - | - |
| P4-T4-4 | ⬜ 测试文件系统隔离 | 未开始 | sandbox 内文件不影响宿主机 | 1.0 | - | 安全关键 |
| P4-T4-5 | ⬜ 测试网络访问限制 | 未开始 | 根据配置允许/拒绝网络 | 1.0 | - | 安全关键 |
| P4-T4-6 | ⬜ 测试超时限制 | 未开始 | 长时间执行被终止 | 0.5 | - | - |
| P4-T4-7 | ⬜ 测试内存限制 | 未开始 | 大内存申请被限制 | 0.5 | - | - |

**Phase 4 验收**:
- [ ] web_search / web_crawl / read_file / write_file / edit_file / execute 全部正常
- [ ] ToolUniverse 每类学科至少 1 个工具测试通过
- [ ] 所有内置 Skills（pdf/docx/pptx/xlsx/deep-research/skill-creator/tool-creator）正常
- [ ] Skills 路由隔离和屏蔽功能正常
- [ ] Sandbox 代码执行隔离有效
- [ ] 大结果自动落盘正常

---

### Phase 4 → Phase 5 过渡

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P4-CR | ⬜ Phase 4 Code Review | 未开始 | 审查清单通过（工具适配完整性 + Sandbox 安全性） | 2.0 | - | - |
| P4-BUF | ⬜ Buffer Time（缓冲） | 未开始 | 处理 P4 遗留问题 | 4.0 | - | 约 P4 工时的 15% |

---

## Phase 5: 功能补齐

> **目标**: 实现当前 DeepAgents 特有但 SDK 缺失的功能
> **时间**: Week 5 (Day 29-35)
> **前置条件**: Phase 4 完成

### P5-T1: 思考内容提取

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P5-T1-1 | ⬜ 保留 `_extract_thinking()` 函数 | 未开始 | 处理 DeepSeek/Claude/Qwen 格式 | 0.5 | - | - |
| P5-T1-2 | ⬜ 测试 DeepSeek reasoning_content 提取 | 未开始 | additional_kwargs 字段正确 | 0.5 | - | - |
| P5-T1-3 | ⬜ 测试 Claude content blocks 提取 | 未开始 | type="thinking" 块正确 | 0.5 | - | - |
| P5-T1-4 | ⬜ 测试 Qwen `<think>` 标签提取 | 未开始 | 正则匹配正确 | 0.5 | - | - |
| P5-T1-5 | ⬜ 思考内容透传到 SSE 事件 | 未开始 | `thinking` 事件格式正确 | 0.5 | - | - |
| P5-T1-6 | ⬜ 移除 engine.py 中的 monkey-patch（必做） | 未开始 | engine.py 中 70 行 patch 代码完全删除，thinking 提取改用 SDK 原生机制 | 1.0 | - | 痛点#3：当前 patch 依赖 langchain-openai 内部 API，任何版本更新都可能破坏 |

---

### P5-T2: Token 统计

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P5-T2-1 | ⬜ 保留 `_estimate_tokens()` 函数 | 未开始 | 字符到 token 估算 | 0.2 | - | - |
| P5-T2-2 | ⬜ 保留 `_extract_token_usage()` 函数 | 未开始 | 多格式 token 提取 | 0.5 | - | - |
| P5-T2-3 | ⬜ 集成 SDK 的 token 统计（如有） | 未开始 | 补充或替代估算 | 0.5 | - | - |
| P5-T2-4 | ⬜ 测试 input_tokens 统计准确性 | 未开始 | 误差 < 10% | 0.5 | - | - |
| P5-T2-5 | ⬜ 测试 output_tokens 统计准确性 | 未开始 | 误差 < 10% | 0.5 | - | - |
| P5-T2-6 | ⬜ 测试 thinking_tokens 统计 | 未开始 | 新增字段正确 | 0.5 | - | - |

---

### P5-T3: 历史消息压缩（替代 SummarizationMiddleware）

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P5-T3-1 | ⬜ 实现基于 token 计数的历史截断 | 未开始 | 超过 budget 时截断旧消息 | 1.0 | - | - |
| P5-T3-2 | ⬜ 保留 `_build_history_messages()` 截断逻辑 | 未开始 | max_rounds + max_tokens 限制 | 0.5 | - | - |
| P5-T3-3 | ⬜ 测试长历史会话（>10 轮） | 未开始 | 不触发上下文溢出 | 1.0 | - | - |
| P5-T3-4 | ⬜ 测试历史消息格式正确性 | 未开始 | 消息角色顺序正确 | 0.5 | - | - |
| P5-T3-5 | ⬜ 测试工具消息在历史中保留 | 未开始 | ToolMessage 不丢失 | 0.5 | - | - |

---

### P5-T4: 多模型支持

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P5-T4-1 | ⬜ 保留 `engine.py` 模型工厂 | 未开始 | 多模型配置解析正常 | 0.5 | - | - |
| P5-T4-2 | ⬜ 测试 Claude 模型通过 SDK 调用 | 未开始 | `claude-3-5-sonnet` 正常 | 0.5 | - | - |
| P5-T4-3 | ⬜ 测试 OpenAI 兼容模型通过 SDK base_url 调用 | 未开始 | `deepseek-chat` 正常 | 1.0 | - | - |
| P5-T4-4 | ⬜ 测试 Gemini 模型（如兼容） | 未开始 | 成功或友好提示不支持 | 0.5 | - | - |
| P5-T4-5 | ⬜ 实现非兼容模型的降级提示 | 未开始 | 提示用户切换到兼容模型 | 0.5 | - | - |
---

### P5-T5: 诊断日志集成

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P5-T5-1 | ⬜ 保留 `DiagnosticLogger` 初始化 | 未开始 | diagnostic 对象创建 | 0.2 | - | - |
| P5-T5-2 | ⬜ 集成诊断到 SSEMonitoringMiddleware | 未开始 | 中间件事件记录到诊断日志 | 0.5 | - | - |
| P5-T5-3 | ⬜ 保留 LLM 调用输入记录 | 未开始 | `save_initial_input()` 调用 | 0.2 | - | - |
| P5-T5-4 | ⬜ 保留诊断文件保存 | 未开始 | `diagnostic.save()` 生成文件 | 0.5 | - | - |
| P5-T5-5 | ⬜ 测试诊断模式（DIAGNOSTIC_ENABLED=1） | 未开始 | 诊断文件完整生成 | 0.5 | - | - |

---

### P5-T6: SDK Hooks 适配 — 危险命令拦截

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P5-T6-1 | ⬜ 设计 Hooks 配置 schema | 未开始 | `hooks_config.yaml` 定义拦截规则 | 1.0 | - | 架构设计 |
| P5-T6-2 | ⬜ 实现 `PreToolUse` Hook（危险命令拦截） | 未开始 | `rm -rf /` / `../../../etc/passwd` 被拦截 | 1.5 | - | 安全关键 |
| P5-T6-3 | ⬜ 实现 `PreToolUse` Hook（.env 文件保护） | 未开始 | 对 `.env` / `config.py` 的写操作被拒绝或重定向 | 1.0 | - | 安全关键 |
| P5-T6-4 | ⬜ 实现 `PreToolUse` Hook（输入参数消毒） | 未开始 | 特殊字符 / 命令注入被过滤 | 1.0 | - | 安全关键 |
| P5-T6-5 | ⬜ 编写 Hooks 单元测试 | 未开始 | pytest 通过，覆盖允许/拒绝/重定向三种决策 | 1.0 | - | - |

**验收标准**: `PreToolUse` Hook 三层安全检查（鉴权→消毒→审计）工作正常，危险操作被拦截

---

### P5-T7: SDK Hooks 适配 — 审计与通知

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P5-T7-1 | ⬜ 实现 `PostToolUse` Hook（审计日志） | 未开始 | 每个工具调用的输入/输出/耗时记录到日志 | 1.0 | - | 可观测性 |
| P5-T7-2 | ⬜ 实现 `PostToolUse` Hook（飞书通知触发） | 未开始 | 关键工具完成后调用飞书 webhook | 1.0 | - | 复用现有 IM 集成 |
| P5-T7-3 | ⬜ 实现 `Notification` Hook（SSE 转发） | 未开始 | SDK 状态消息自动转发到前端 SSE 流 | 1.0 | - | 前端无感 |
| P5-T7-4 | ⬜ 实现 `SessionStart/End` Hook（workspace 管理） | 未开始 | 会话开始时初始化目录，结束时清理临时文件 | 1.0 | - | 生命周期管理 |
| P5-T7-5 | ⬜ 将 `DiagnosticLogger` 从 LangChain callback 迁移到 Hooks | 未开始 | 诊断日志直接订阅 Hooks 事件，不再依赖 LangChain callback | 1.5 | - | 痛点#10：从间接拦截改为直接注入 |

---

### P5-T8: SDK Hooks 适配 — 子 Agent 与压缩

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P5-T8-1 | ⬜ 实现 `SubagentStart/Stop` Hook | 未开始 | 并行子 Agent 任务进度可跟踪 | 1.0 | - | 并行研究场景 |
| P5-T8-2 | ⬜ 实现 `PreCompact` Hook（上下文压缩前存档） | 未开始 | 压缩前完整对话记录存档到 MongoDB | 1.0 | - | 数据安全 |
| P5-T8-3 | ⬜ 测试 Hooks 链式执行顺序 | 未开始 | RateLimit → Auth → Sanitize → Audit 按序执行 | 0.5 | - | - |

---

### P5-T9: 同步/异步桥接统一（痛点#4）

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P5-T9-1 | ⬜ 分析现有 async bridge hack 代码（offload + sandbox） | 未开始 | 梳理 `offload_middleware.py` 和 `full_sandbox_backend.py` 中的 bridge 逻辑 | 0.5 | - | - |
| P5-T9-2 | ⬜ 统一为全异步架构（移除所有 `asyncio.run()` / `ThreadPoolExecutor` 桥接） | 未开始 | 无 `asyncio.run()` 在同步上下文中的调用 | 2.0 | - | SDK 全异步，彻底消除 hack |
| P5-T9-3 | ⬜ 验证高并发下无线程池耗尽风险 | 未开始 | 100 并发工具调用稳定 | 1.0 | - | 消除痛点#4的竞态风险 |

---

### P5-T10: 工具自注册机制重构（痛点#7）

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P5-T10-1 | ⬜ 设计 `@claw_tool` 装饰器（自带元数据） | 未开始 | 装饰器支持 `name`, `description`, `icon`, `category` 参数 | 1.0 | - | 替代 `@tool` + 手动注册 |
| P5-T10-2 | ⬜ 实现工具元数据自动提取 | 未开始 | `client.register_tool(tool)` 自动提取 icon/category | 1.0 | - | 消除 sse_protocol.py 手动注册 |
| P5-T10-3 | ⬜ 迁移现有工具到 `@claw_tool` | 未开始 | `tools.py` 中所有工具使用新装饰器 | 1.0 | - | 逐步迁移 |
| P5-T10-4 | ⬜ 验证 sse_protocol.py 注册表自动同步 | 未开始 | 添加新工具无需手动修改 `_initialize_default_tools()` | 0.5 | - | 痛点#7 根治 |
| P5-T10-5 | ⬜ 编写自注册单元测试 | 未开始 | pytest 通过 | 0.5 | - | - |

---

### P5-T11: 双层上下文管理统一（痛点#8）

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P5-T11-1 | ⬜ 移除 `SummarizationMiddleware` 依赖确认 | 未开始 | 确认 DeepAgents 的 SummarizationMiddleware 不再被调用 | 0.5 | - | - |
| P5-T11-2 | ⬜ 统一为 runner 层单点截断 | 未开始 | `_build_history_messages()` 是唯一历史截断点 | 1.0 | - | 避免重复截断 |
| P5-T11-3 | ⬜ 测试长历史会话（>20 轮）信息完整性 | 未开始 | 关键信息不因截断丢失 | 1.0 | - | - |

---

### P5-T12: Token 统计简化（痛点#9）

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P5-T12-1 | ⬜ 简化 `_extract_token_usage()`（SDK 原生优先） | 未开始 | 优先使用 SDK 返回的 token 统计，仅保留单 fallback | 1.0 | - | 从四重回退改为单层 |
| P5-T12-2 | ⬜ 测试非 Claude 模型的 token 统计兼容性 | 未开始 | DeepSeek / OpenAI 兼容端点正常 | 0.5 | - | - |

**Phase 5 验收**:
- [ ] 思考内容从多种格式正确提取
- [ ] engine.py monkey-patch 完全移除，SDK 原生 thinking 支持
- [ ] Token 统计与旧版误差 < 10%，四重回退简化为单层
- [ ] 长历史会话不触发上下文溢出，单点截断无重复
- [ ] 诊断日志完整生成，且已从 LangChain callback 迁移到 Hooks
- [ ] Claude 模型通过 SDK 正常调用
- [ ] OpenAI 兼容模型通过 SDK base_url 正常调用
- [ ] `PreToolUse` Hook 三层安全检查工作正常
- [ ] 工具自注册机制工作正常，新增工具无需修改 sse_protocol.py
- [ ] 全异步架构无 async bridge hack

---

### Phase 5 → Phase 6 过渡

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P5-CR | ⬜ Phase 5 Code Review | 未开始 | 审查清单通过（Hooks 安全性 + 异步架构 + 痛点修复验证） | 2.0 | - | - |
| P5-BUF | ⬜ Buffer Time（缓冲） | 未开始 | 处理 P5 遗留问题 | 5.0 | - | 约 P5 工时的 15% |

---

## Phase 6: 测试与回归

> **目标**: 建立完整测试套件，验证功能正确性和稳定性
> **时间**: Week 6 (Day 36-42)
> **前置条件**: Phase 5 完成

### P6-T1: 单元测试补齐

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P6-T1-1 | ⬜ 为 `middleware_base.py` 补测试 | 未开始 | 覆盖率 100% | 0.5 | - | - |
| P6-T1-2 | ⬜ 为 `backend_protocol.py` 补测试 | 未开始 | 覆盖率 100% | 1.0 | - | - |
| P6-T1-3 | ⬜ 为 `tool_converter.py` 补测试 | 未开始 | 覆盖率 100% | 0.5 | - | - |
| P6-T1-4 | ⬜ 为 `claw_agent()` 补测试 | 未开始 | 覆盖率 > 80% | 2.0 | - | - |
| P6-T1-5 | ⬜ 为 runner 核心循环补测试 | 未开始 | 覆盖率 > 80% | 2.0 | - | - |
| P6-T1-6 | ⬜ 运行 pytest 生成覆盖率报告 | 未开始 | `pytest --cov` 输出 | 0.5 | - | - |
| P6-T1-7 | ⬜ 确保整体覆盖率 > 80% | 未开始 | 报告数字达标 | 1.0 | - | - |

---

### P6-T2: 集成测试

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P6-T2-1 | ⬜ 编写端到端对话测试 | 未开始 | 完整对话流测试 | 1.0 | - | - |
| P6-T2-2 | ⬜ 编写工具调用链测试 | 未开始 | 多工具连续调用 | 1.0 | - | - |
| P6-T2-3 | ⬜ 编写 SSE 事件流测试 | 未开始 | 所有事件类型覆盖 | 1.0 | - | - |
| P6-T2-4 | ⬜ 编写会话生命周期测试 | 未开始 | 创建→聊天→删除 | 0.5 | - | - |
| P6-T2-5 | ⬜ 编写并发会话测试 | 未开始 | 10 并发无冲突 | 1.0 | - | - |
| P6-T2-6 | ⬜ 编写内存泄漏测试 | 未开始 | 长时间运行内存稳定 | 1.0 | - | - |

---

### P6-T3: 回归测试

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P6-T3-1 | ⬜ 编写 SSE 事件流对比脚本 | 未开始 | 新旧版本输出自动对比 | 1.0 | - | - |
| P6-T3-2 | ⬜ 运行对比测试（文本对话场景） | 未开始 | 事件序列一致 | 0.5 | - | - |
| P6-T3-3 | ⬜ 运行对比测试（工具调用场景） | 未开始 | 事件序列一致 | 0.5 | - | - |
| P6-T3-4 | ⬜ 运行对比测试（多轮对话场景） | 未开始 | 事件序列一致 | 0.5 | - | - |
| P6-T3-5 | ⬜ 记录并修复差异 | 未开始 | 差异清单清零 | 2.0 | - | - |
| P6-T3-6 | ⬜ 验证前端兼容性 | 未开始 | Vue 前端无需修改即可工作 | 1.0 | - | - |
| P6-T3-7 | ⬜ 验证飞书/IM 集成 | 未开始 | 消息推送正常 | 0.5 | - | - |
| P6-T3-8 | ⬜ 验证任务调度集成 | 未开始 | task-service 调用正常 | 0.5 | - | - |

---

### P6-T4: Bug 修复

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P6-T4-1 | ⬜ 汇总测试阶段发现的 Bug | 未开始 | Bug 清单文档 | 0.5 | - | - |
| P6-T4-2 | ⬜ 修复 P0 优先级 Bug（阻塞功能） | 未开始 | 全部修复 | 2.0 | - | - |
| P6-T4-3 | ⬜ 修复 P1 优先级 Bug（影响体验） | 未开始 | 全部修复 | 2.0 | - | - |
| P6-T4-4 | ⬜ 修复 P2 优先级 Bug（轻微问题） | 未开始 | 修复或记录为已知问题 | 1.0 | - | - |
| P6-T4-5 | ⬜ 回归验证修复未引入新问题 | 未开始 | 全量测试通过 | 1.0 | - | - |

**Phase 6 验收**:
- [ ] 单元测试覆盖率 > 80%
- [ ] 集成测试全部通过
- [ ] SSE 事件流与旧版对比无差异
- [ ] 前端无需修改即可工作
- [ ] 已知 Bug 清零（P0/P1）

---

## Phase 7: 性能优化

> **目标**: 确保新引擎性能不低于旧引擎 120%
> **时间**: Week 7 (Day 43-49)
> **前置条件**: Phase 6 完成

### P7-T1: 基准测试建立

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P7-T1-1 | ⬜ 编写首 token 延迟测试脚本 | 未开始 | 测量从请求到首 token 的时间 | 0.5 | - | - |
| P7-T1-2 | ⬜ 编写工具调用延迟测试脚本 | 未开始 | 测量单次工具调用耗时 | 0.5 | - | - |
| P7-T1-3 | ⬜ 编写内存占用测试脚本 | 未开始 | 测量单会话内存 | 0.5 | - | - |
| P7-T1-4 | ⬜ 编写并发压力测试脚本 | 未开始 | 测量多会话并发性能 | 0.5 | - | - |
| P7-T1-5 | ⬜ 运行旧引擎基准测试 | 未开始 | 记录基准数据 | 1.0 | - | - |
| P7-T1-6 | ⬜ 运行新引擎基准测试 | 未开始 | 记录对比数据 | 1.0 | - | - |
| P7-T1-7 | ⬜ 生成基准对比报告 | 未开始 | 包含延迟/内存/并发数据 | 0.5 | - | - |

---

### P7-T2: 性能优化

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P7-T2-1 | ⬜ 分析首 token 延迟瓶颈 | 未开始 | 定位耗时大户 | 1.0 | - | - |
| P7-T2-2 | ⬜ 优化 SSE 事件流延迟 | 未开始 | 首 token 延迟 < 旧版 120% | 2.0 | - | - |
| P7-T2-3 | ⬜ 优化工具调用延迟 | 未开始 | 工具调用延迟 < 旧版 120% | 2.0 | - | - |
| P7-T2-4 | ⬜ 优化内存占用 | 未开始 | 单会话内存 < 旧版 120% | 2.0 | - | - |
| P7-T2-5 | ⬜ 优化 MongoDB 查询 | 未开始 | 会话列表查询 < 100ms | 1.0 | - | - |
| P7-T2-6 | ⬜ 优化连接池（HTTP Client） | 未开始 | httpx 连接复用 | 1.0 | - | - |
| P7-T2-7 | ⬜ 优化工具结果缓存 | 未开始 | 重复工具调用结果缓存 | 1.0 | - | - |

---

### P7-T3: 验证

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P7-T3-1 | ⬜ 重新运行基准测试 | 未开始 | 优化后数据 | 1.0 | - | - |
| P7-T3-2 | ⬜ 验证性能达标 | 未开始 | 所有指标 < 旧版 120% | 0.5 | - | - |
| P7-T3-3 | ⬜ 生成性能优化报告 | 未开始 | 包含优化前后对比 | 0.5 | - | - |

**Phase 7 验收**:
- [ ] 首 token 延迟不超过旧版 120%
- [ ] 工具调用延迟不超过旧版 120%
- [ ] 内存占用不超过旧版 120%
- [ ] MongoDB 查询 < 100ms
- [ ] 性能基准报告完成

---

## Phase 8: 发布与文档

> **目标**: 完成文档更新、配置说明、灰度发布
> **时间**: Week 8 (Day 50-56)
> **前置条件**: Phase 7 完成

### P8-T1: 文档更新

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P8-T1-1 | ⬜ 更新 README.md（架构说明） | 未开始 | 包含新引擎说明 | 1.0 | - | - |
| P8-T1-2 | ⬜ 更新 README_zh.md | 未开始 | 中文版本同步 | 1.0 | - | - |
| P8-T1-3 | ⬜ 编写迁移指南 `docs/migration-guide.md` | 未开始 | 从 DeepAgents 迁移步骤 | 2.0 | - | - |
| P8-T1-4 | ⬜ 编写 Claude SDK 引擎使用手册 | 未开始 | 配置、使用、常见问题 | 2.0 | - | - |
| P8-T1-5 | ⬜ 更新 API 文档（如有变化） | 未开始 | Swagger/OpenAPI 正确 | 0.5 | - | - |
| P8-T1-6 | ⬜ 更新环境变量说明 | 未开始 | `.env.template` 注释完整 | 0.5 | - | - |
| P8-T1-7 | ⬜ 编写 Hooks 使用示例 | 未开始 | 3 个常见场景示例 | 1.0 | - | - |
| P8-T1-8 | ⬜ 编写 Sub-agents 使用示例 | 未开始 | 并行研究场景示例 | 1.0 | - | - |

---

### P8-T2: 配置与构建

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P8-T2-1 | ⬜ 更新 `docker-compose.yml` | 未开始 | 新环境变量配置 | 0.5 | - | - |
| P8-T2-2 | ⬜ 更新 `docker-compose-release.yml` | 未开始 | 发布镜像配置 | 0.5 | - | - |
| P8-T2-3 | ⬜ 更新 `docker-compose-china.yml` | 未开始 | 国内镜像加速配置 | 0.5 | - | - |
| P8-T2-4 | ⬜ 更新 `release.sh` | 未开始 | 包含新镜像构建 | 0.5 | - | - |
| P8-T2-5 | ⬜ 验证 Docker 全量构建 | 未开始 | `docker compose build` 成功 | 2.0 | - | - |
| P8-T2-6 | ⬜ 验证 Docker 发布构建 | 未开始 | `docker compose -f release.yml build` 成功 | 2.0 | - | - |

---

### P8-T3: 代码审查

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P8-T3-1 | ⬜ 自我代码审查（检查清单） | 未开始 | 审查清单全部通过 | 1.0 | - | - |
| P8-T3-2 | ⬜ 团队代码审查（如有） | 未开始 | Review 意见处理完毕 | 2.0 | - | - |
| P8-T3-3 | ⬜ 修复审查意见 | 未开始 | 所有阻塞意见修复 | 2.0 | - | - |
| P8-T3-4 | ⬜ 最终代码格式化 | 未开始 | 符合项目编码规范 | 0.5 | - | - |

---

### P8-T4: 灰度发布

| ID | 任务 | 状态 | 验收标准 | 预估(h) | 实际(h) | 备注 |
|----|------|------|----------|---------|---------|------|
| P8-T4-1 | ⬜ 配置灰度策略（10% 流量） | 未开始 | 按用户 ID hash 分配 | 0.5 | - | - |
| P8-T4-2 | ⬜ 部署到 staging 环境 | 未开始 | staging 服务正常 | 1.0 | - | - |
| P8-T4-3 | ⬜ Staging 环境功能验证 | 未开始 | 核心功能 checklist 通过 | 1.0 | - | - |
| P8-T4-4 | ⬜ 启动 10% 灰度流量 | 未开始 | 监控面板显示分流 | 0.5 | - | - |
| P8-T4-5 | ⬜ 监控错误率（24小时） | 未开始 | 错误率 < 1% | 2.0 | - | 被动等待 |
| P8-T4-6 | ⬜ 监控延迟变化（24小时） | 未开始 | P99 延迟 < 旧版 120% | 1.0 | - | 被动等待 |
| P8-T4-7 | ⬜ 收集用户反馈 | 未开始 | 反馈清单 | 1.0 | - | - |
| P8-T4-8 | ⬜ 根据反馈修复问题 | 未开始 | 问题修复 | 2.0 | - | - |
| P8-T4-9 | ⬜ 扩大灰度至 50% | 未开始 | 监控正常 | 0.5 | - | - |
| P8-T4-10 | ⬜ 扩大灰度至 100% | 未开始 | 监控正常 | 0.5 | - | - |
| P8-T4-11 | ⬜ 保留 `deepagent/` 至少 1 个月 | 未开始 | 目录保留 | 0.1 | - | - |
| P8-T4-12 | ⬜ 1 个月后确认移除 `deepagent/` | 未开始 | 团队确认无回滚需求 | 0.1 | - | - |

**Phase 8 验收**:
- [ ] 文档完整更新（中英文）
- [ ] Docker 构建成功（dev + release）
- [ ] 代码审查通过
- [ ] 灰度发布 10% 无异常（24 小时）
- [ ] 全量发布完成
- [ ] 回滚机制验证通过（紧急切换测试）

---

## 汇总统计

### 任务统计

| Phase | 任务数 | 预估总工时(h) | 状态分布 |
|-------|--------|--------------|----------|
| Phase 0: 准备 | 40 | ~25.0h | 全部 ⬜ |
| Phase 1: 基础设施 | 36 | ~20.5h | 全部 ⬜ |
| Phase 2: Agent核心 | 36 | ~29.0h | 全部 ⬜ |
| Phase 3: Runner重写 | 37 | ~25.5h | 全部 ⬜ |
| Phase 4: 工具适配 | 37 | ~26.0h | 全部 ⬜ |
| Phase 5: 功能补齐 | 52 | ~36.0h | 全部 ⬜ |
| Phase 6: 测试回归 | 28 | ~23.0h | 全部 ⬜ |
| Phase 7: 性能优化 | 20 | ~17.5h | 全部 ⬜ |
| Phase 8: 发布文档 | 31 | ~28.0h | 全部 ⬜ |
| Phase 间过渡 | 8 | ~17.0h | 全部 ⬜ |
| **总计** | **322** | **~247.5h (~31 工作日)** | - |

### 按角色分工建议

| 角色 | 负责 Phase | 任务数 | 预估工时 |
|------|-----------|--------|----------|
| **后端资深工程师** | P0-P3 | 157 | ~100.0h |
| **后端中级工程师** | P4-P5 | 89 | ~62.0h |
| **QA / 测试工程师** | P6 | 28 | ~23.0h |
| **性能工程师** | P7 | 20 | ~17.5h |
| **DevOps / 技术写作** | P8 | 31 | ~28.0h |

### 风险任务（建议重点关注）

| 任务 ID | 风险描述 | 缓解策略 |
|---------|---------|----------|
| P0-T3-9 | SDK 依赖安装冲突 | 提前在隔离环境测试 |
| P0-T6-2 | `DeepAgentEngine` 包装现有代码时出现循环依赖 | 分步验证，先确保 import 不报错再填充逻辑 |
| P2-T4-9 | ClaudeSDKClient 创建失败 | 确认 API Key 和 base_url 配置 |
| P2-T5-4 | 两种引擎 SSE 事件格式无法 100% 统一 | 前端预留兼容层，事件差异在允许范围内 |
| P3-T1-7 | `client.query()` 流式行为与预期不符 | 提前阅读 SDK 源码或文档 |
| P3-T5-8 | SSE 事件流与旧版不一致 | 预留充足时间修复差异 |
| P5-T4-3 | OpenAI 兼容端点不支持 | 准备降级方案（保留 DeepAgents） |
| P5-T9-2 | 移除 async bridge 后现有同步调用点崩溃 | 逐文件审计 `asyncio.run()` 调用，保留必要 shim |
| P6-T2-5 | 并发会话出现 race condition | 使用 asyncio.Lock 保护共享状态 |
| P8-T4-5 | 灰度期间错误率超标 | 准备一键回滚脚本 |

---

---

## 技术债务（Tech Debt）

> **定义**：故意选择的临时/次优方案，明知将来需要偿还。
> **规则**：每项技术债务必须记录产生原因、影响、偿还计划。禁止无记录的债务。

| ID | 债务描述 | 产生任务 | 产生原因 | 影响 | 偿还计划 | 状态 |
|----|---------|---------|---------|------|---------|------|
| — | — | — | — | — | — | — |

### 债务状态
- 🟢 **已识别**：已知，有计划偿还
- 🟡 **累积中**：短期可接受，长期有害
- 🔴 **危急**：已造成实际问题，必须立即偿还

---

## 已知问题（Known Issues）

> **定义**：已发现但尚未修复的问题。区别于风险（风险是尚未发生的可能问题）。
> **规则**：每个已知问题必须有关联任务 ID，修复后归档到"已修复"子章节。

### 活跃问题

| ID | 问题描述 | 发现任务 | 严重程度 | 影响范围 | 规避方案 | 修复任务 |
|----|---------|---------|---------|---------|---------|---------|
| — | — | — | — | — | — | — |

### 已修复问题（归档）

| ID | 问题描述 | 发现任务 | 修复任务 | 修复日期 | 根因 |
|----|---------|---------|---------|---------|------|
| — | — | — | — | — | — |

---

## 依赖关系矩阵

> **用途**：可视化任务间的前置依赖，防止并行开发时出现阻塞。
> **更新时机**：新增任务或发现新依赖时。

### 跨 Phase 关键依赖

```
P0-T6 (AgentEngine ABC)
    ├──→ P1-T1 (MiddlewareStack 需适配 ABC)
    ├──→ P1-T2 (Backend 需适配 ABC)
    ├──→ P2-T5 (引擎切换依赖 ABC)
    └──→ P0-T6-2 (DeepAgentEngine 包装)

P2-T4 (claw_agent() 实现)
    ├──→ P2-T1 (工具转换层)
    ├──→ P2-T2 (工具包装)
    ├──→ P2-T3 (子 Agent)
    └──→ P3-T1 (Runner 依赖 claw_agent())

P3-T1-7 (client.query())
    ├──→ P2-T4-9 (ClaudeSDKClient 创建)
    └──→ P3-T5-8 (SSE 对比依赖流式输出)

P5-T6 (Hooks)
    ├──→ P1-T1 (MiddlewareStack)
    └──→ P5-T7 (PostToolUse 依赖 PreToolUse)
```

### 强耦合任务组（必须顺序执行）

| 组名 | 任务序列 | 原因 |
|------|---------|------|
| 基础设施三部曲 | P1-T1 → P1-T2 → P1-T3/P1-T4/P1-T5/P1-T6 | 中间件和 Backend 是其他组件的基类 |
| Agent 核心链 | P2-T1 → P2-T2 → P2-T3 → P2-T4 | 工具转换→包装→子Agent→组装 |
| 引擎切换 | P0-T6 → P2-T5 | ABC 定义后才能实现切换 |
| Hooks 链 | P5-T6-1 (设计) → P5-T6~T8 (实现) | 配置 schema 冻结后才能实现 |

### 可并行任务组

| 组名 | 并行任务 | 前提 |
|------|---------|------|
| 目录准备 | P0-T1 + P0-T3-1~5 (备份/编辑 requirements) | 无前置 |
| 中间件适配 | P1-T3 + P1-T4 + P1-T5 + P1-T6 | P1-T1 和 P1-T2 完成后 |
| 工具验证 | P4-T1 + P4-T2 + P4-T3 + P4-T4 | Phase 3 完成后 |
| Hooks 实现 | P5-T6 + P5-T7 + P5-T8 | P5-T6-1 schema 完成后 |

---

## 上下文保持协议（AI Agent 专用）

> **用途**：确保 AI Agent 在多轮对话中不丢失关键上下文。
> **执行规则**：每轮对话开始时读取，每轮结束时更新。

### 本轮前必须读取的文件（按优先级）

1. `constraints.md` — 行为边界（30 秒）
2. 本文档 **Current Focus** 区域 — 当前状态（10 秒）
3. `adr.md` — 冻结决策（如有架构疑问）（2 分钟）
4. `acceptance.md` — 当前任务的验收标准（2 分钟）

### 本轮后必须更新的内容

1. **Current Focus** 区域：
   - 当前进行中任务的状态
   - 实际工时（如果任务完成）
   - 下一轮计划
   - 任何新阻塞

2. **技术债务** 章节（如产生临时方案）：
   - 债务 ID、描述、产生原因

3. **已知问题** 章节（如发现新问题）：
   - 问题 ID、描述、严重程度

4. **progress.md 任务表格**：
   - 状态标记（⬜→🔄→✅/❌）
   - 实际工时
   - 备注（如有偏差或阻塞原因）

### 禁止行为

- ❌ 不读取 Current Focus 直接开始编码
- ❌ 完成任务后不更新 progress.md
- ❌ 产生临时方案但不记录技术债务
- ❌ 发现阻塞但不标记任务为 ❌

---

## 更新记录

| 日期 | 版本 | 变更内容 | 作者 |
|------|------|----------|------|
| 2026-05-02 | v1.0 | 初始创建，包含 9 个 Phase 共 276 个原子任务 | Sisyphus |
| 2026-05-02 | v1.1 | 完善：混合架构任务（P0-T6/P2-T5）、Hooks 适配（P5-T6~T8）、痛点根治任务（P5-T9~T12）、流程过渡（Code Review + Buffer）、工时校准、扩展跟踪字段 | Sisyphus |
| 2026-05-02 | v1.2 | 增加：Current Focus 动态区域、Quick Reference 快捷参考、技术债务章节、已知问题章节、依赖关系矩阵、AI Agent 上下文保持协议 | Sisyphus |

---

> **使用方法**：每个任务完成后，将 `⬜ 未开始` 更新为 `✅ 已完成`，并在"实际工时"列填写实际花费时间。每日站会时更新此文档。
>
> **AI Agent 特别提醒**：每轮对话开始时，先读取 **Current Focus** 区域和 **constraints.md**，确认当前状态和边界后再开始工作。每轮结束时，更新 Current Focus、任务状态、技术债务（如适用）。
