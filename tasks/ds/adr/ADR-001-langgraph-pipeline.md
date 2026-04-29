# ADR-001: 使用 LangGraph StateGraph 作为 Pipeline 编排引擎

**日期**: 2026-04-25
**状态**: accepted
**决策者**: RV-Insights Team

## 背景

RV-Insights 需要一个 Pipeline 编排引擎来管理 5 阶段 RISC-V 贡献流水线（Explore → Plan → Develop ↔ Review → Test）。核心需求包括：

1. 阶段间有条件路由（审核通过/驳回/放弃）
2. Develop ↔ Review 迭代循环（最多 3 轮，含收敛检测）
3. Human-in-the-Loop 审批门（每个阶段完成后暂停等待人工决策）
4. 检查点持久化（服务重启后恢复未完成的 Pipeline）
5. 与两个 Agent SDK（Claude + OpenAI）集成

## 决策

使用 **LangGraph StateGraph** 作为 Pipeline 编排引擎。

关键实现：
- `StateGraph(PipelineState)` 定义 10 个节点 + 条件边
- `AsyncPostgresSaver` 持久化检查点到 PostgreSQL
- `interrupt()` 机制实现 Human-in-the-Loop
- `Command(resume=...)` 恢复暂停的执行
- 每个 Agent 节点封装为 LangGraph 节点函数

## 考虑的替代方案

1. **Celery Canvas (chain/group/chord)** — 优点：成熟的任务队列；缺点：无法表达循环（review 迭代），checkpoint 需要自建
2. **自研状态机** — 优点：完全控制；缺点：重复造轮子，需要自建持久化、恢复、并发控制
3. **Temporal** — 优点：企业级工作流引擎；缺点：引入重量级外部依赖，学习曲线陡峭

## 后果

### 正面影响
- 内置 checkpoint + 恢复，服务重启不丢 Pipeline 状态
- `interrupt()` 天然支持 Human-in-the-Loop
- 条件边完美建模 review 迭代 + 审批路由
- Python 生态原生，与 FastAPI 无缝集成

### 负面影响
- LangGraph API 仍在快速迭代（0.3.x），可能有 Breaking Changes
- 调试状态机比线性代码困难
- 所有 Agent 节点运行在同一进程（需 ResourceScheduler 控制并发）

## 相关
- design.md §5.2 LangGraph StateGraph 状态机
- design.md §5.4 Human-in-the-Loop 审批门
- refactoring-plan.md §3 (Sprint 3: Pipeline Engine Core)
