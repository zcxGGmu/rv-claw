# ADR-002: 双 SDK 架构 — Claude Agent SDK + OpenAI Agents SDK

**日期**: 2026-04-25
**状态**: accepted
**决策者**: RV-Insights Team

## 背景

RV-Insights 的 5 个 Pipeline 阶段对 Agent 能力有本质不同的需求：

- **Explore / Develop / Test**：需要深度文件操作（Read/Write/Edit/Bash）、代码库导航、命令执行
- **Plan / Review**：需要多视角推理、Guardrail 验证、Handoff 编排

使用单一 SDK 无法同时满足两类需求。

## 决策

采用双 SDK 架构：

| 阶段 | SDK | 关键理由 |
|------|-----|----------|
| Explore | Claude Agent SDK | 内置 Read/Grep/Glob/WebSearch/Bash，开箱即用 |
| Plan | OpenAI Agents SDK | 纯推理任务，Guardrails 验证方案完整性，Handoff 编排子 Agent |
| Develop | Claude Agent SDK | Write/Edit/Bash 核心优势，`canUseTool` 审批回调 |
| Review | OpenAI Agents SDK | Handoff 分发 security/correctness/style 三视角审核 |
| Test | Claude Agent SDK | Bash 执行测试套件，Read 解析日志 |

两个 SDK 通过 `AgentAdapter` 抽象层隔离，不直接交互。数据通过 LangGraph `PipelineState` 的共享状态（Pydantic 模型 JSON 序列化）传递。

## 考虑的替代方案

1. **单一 Claude Agent SDK** — 优点：架构简单；缺点：缺乏 Handoff/Guardrail 能力，审核阶段无法编排多视角
2. **单一 OpenAI Agents SDK** — 优点：编排能力强；缺点：无内置文件操作工具，需自行实现 ~10 个工具
3. **LangChain 自定义 Agent** — 优点：完全控制；缺点：开发成本极高，需要维护工具实现

## 后果

### 正面影响
- 每个阶段使用最适合的 SDK，开发效率最大化
- Adapter 抽象层隔离 SDK 变更风险
- OpenAI Handoff 天然支持多视角审核策略

### 负面影响
- 两个 SDK 的版本升级需分别跟踪
- Adapter 层增加了一层间接性，调试更复杂
- 团队需要掌握两种 SDK 的使用方式

## 相关
- design.md §3 SDK 选型分析与依据
- design.md §2.6 跨 SDK 适配器层
- refactoring-plan.md §7.2 SDK 分配
