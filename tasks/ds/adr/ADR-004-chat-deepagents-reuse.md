# ADR-004: Chat 模式复用 ScienceClaw DeepAgents 引擎

**日期**: 2026-04-29
**状态**: accepted
**决策者**: RV-Insights Team

## 背景

RV-Insights 需要同时支持两种交互模式：

1. **Chat 模式**：通用对话（自由交互、工具调用、文件生成），与 ScienceClaw 现有功能完全一致
2. **Pipeline 模式**：结构化 5 阶段 RISC-V 贡献流水线

Chat 模式有大量 ScienceClaw 已验证的功能需要保留：技能系统、工具生态、文件管理、IM 集成、任务调度等。

## 决策

Chat 模式**复用 ScienceClaw 的 DeepAgents 引擎**，而非重写到 LangGraph。

实现方式：
- `chat/runner.py` 中的 `ChatRunner` 封装 DeepAgents 调用
- 通过 `asyncio.Queue` 桥接 Agent 执行事件到 SSE 端点
- 保留 ScienceClaw 的全部内置技能（xlsx/pdf/docx/pptx 等）
- 保留 ToolUniverse 1900+ 科研工具集成

Pipeline 模式使用 LangGraph（ADR-001），两个模式在 FastAPI 中并存但独立。

## 考虑的替代方案

1. **LangGraph create_react_agent 重写 Chat** — 优点：统一架构，减少认知负担；缺点：需重写整个技能系统、工具生态、IM 集成（~8000 行已验证代码），风险极高
2. **两个独立后端服务** — 优点：完全隔离；缺点：运维复杂度翻倍，用户系统需共享

## 后果

### 正面影响
- ScienceClaw 的全部功能零成本保留
- Chat 模式开发时间从 4 周降至 2 周
- DeepAgents 引擎已经在 ScienceClaw 生产环境验证过

### 负面影响
- 项目包含两套 Agent 引擎（DeepAgents + LangGraph），认知负担增加
- DeepAgents 与 LangGraph 的 LLM 调用配额需统一管理
- 长期可能需将 Chat 迁移到 LangGraph（当 DeepAgents 不再维护时）

## 相关
- refactoring-plan.md §8 Chat 模式实现方案
- refactoring-plan.md 附录 P Chat 模式完整实现方案
- conventions.md §6.2 Chat/Pipeline 资源共享
