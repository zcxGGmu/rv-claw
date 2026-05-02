# ScienceClaw 重构 — 技术决策记录 (ADR)

> **范围**: DeepAgents → Claude Agent SDK 迁移期间的所有关键架构决策
> **更新规则**: 每个决策一旦记录，**冻结后不得修改**，只能追加"废止"记录
> **关联文件**: `constraints.md` (执行约束), `acceptance.md` (验收标准)

---

## ADR-001: 混合双引擎架构（已批准）

**状态**: ✅ 已批准  
**日期**: 2026-05-02  
**决策者**: Sisyphus (规划) / 待团队确认

### 上下文
完全替换 DeepAgents 会导致多模型支持（30+ 模型）丢失，这是 ScienceClaw 的核心竞争优势。

### 决策
采用 **"LangGraph 保留编排 + Claude SDK 接管执行"** 的混合架构：
- `DeepAgentEngine`: 包装现有 `deepagent/`，支持所有模型
- `ClaudeAgentEngine`: 使用 `clawagent/`，专注 Claude 模型 + 深度任务
- 通过 `AgentEngine` ABC 统一接口

### 后果
- ✅ 保留多模型兼容性
- ✅ SDK 优势（并行子 Agent、Hooks）在 Claude 场景可用
- ❌ 维护两套引擎，复杂度上升
- ❌ 引擎切换需保证 SSE 事件 100% 一致

### 约束衍生
- `deepagent/` 目录在整个重构期间 **只读**，任何修改必须经双审批
- `clawagent/` 是新代码唯一写入目标

---

## ADR-002: 保留 LangChain @tool 装饰器（已批准）

**状态**: ✅ 已批准  
**日期**: 2026-05-02

### 决策
保留 `langchain-core` + `langchain-openai`，继续使用 `@tool` 装饰器，通过 `tool_converter.py` 转换为 SDK 格式。

### 后果
- ✅ 现有 12+ 工具无需重写
- ✅ `langchain-openai` 的 `ChatOpenAI` 仍用于非 Claude 模型
- ❌ 仍需维护 LangChain 依赖（尽管已精简）

---

## ADR-003: 软链接切换机制（已批准）

**状态**: ✅ 已批准  
**日期**: 2026-05-02

### 决策
使用 `backend/active_agent` 软链接指向 `deepagent/` 或 `clawagent/`，配合 `scripts/switch-agent.sh` 实现秒级回滚。

### 后果
- ✅ 回滚时间 < 30 秒
- ✅ 无需修改路由层 import
- ❌ 软链接在 Windows 开发环境可能有兼容性问题（项目主要跑在 Docker/Linux）

---

## ADR-004: SSE 事件格式冻结（已批准）

**状态**: ✅ 已批准  
**日期**: 2026-05-02

### 决策
新旧引擎输出的 SSE 事件格式 **100% 冻结**，前端无需任何修改。这是重构的非功能性核心约束。

### 冻结格式清单
```python
# 必须完全一致的事件类型
{"event": "thinking", "data": {"content": str}}
{"event": "step_start", "data": {"step": dict}}
{"event": "plan_update", "data": {"plan": list}}
{"event": "tool_call_start", "data": {"tool_call": dict}}
{"event": "tool_call_end", "data": {"tool_call": dict, "result": dict}}
{"event": "message", "data": {"role": "assistant", "content": str, ...}}
{"event": "error", "data": {"message": str}}
```

### 后果
- ✅ 前端零改动
- ✅ IM 集成（飞书）零改动
- ❌ 新引擎的事件映射层必须精确匹配旧行为

---

## ADR-005: deepagent/ 目录冻结（待执行）

**状态**: ⏳ 待 Phase 0 完成时生效  
**日期**: 2026-05-02

### 决策
从 Phase 0 完成（`clawagent/` 目录创建且验证通过）起，`ScienceClaw/backend/deepagent/` 进入 **只读冻结状态**。

### 冻结规则
1. **禁止修改** `deepagent/` 内任何文件的内容
2. **禁止重命名** `deepagent/` 内的文件（保留历史一致性）
3. **允许复制** `deepagent/` → `clawagent/`（仅 Phase 0）
4. **允许删除** `deepagent/`（仅 Phase 8 灰度发布 1 个月后，经团队确认）

### 例外流程
若发现 `deepagent/` 存在阻塞生产环境的 Bug：
1. 在 `clawagent/` 修复
2. 如需紧急修复旧引擎，提交 PR 并标注 `HOTFIX-deepagent`
3. 需至少 1 名团队负责人审批

---

## ADR-006: Hooks 安全策略（规划中）

**状态**: 📋 规划中  
**目标日期**: Phase 5 开始前确定

### 待决策问题
1. Hooks 配置是静态 YAML 还是动态数据库配置？
2. `PreToolUse` Hook 的拒绝决策是否支持用户覆盖（"我确定要执行"）？
3. Hooks 性能开销上限（单工具调用 Hook 链耗时 < ?ms）？

### 建议方向
- 静态 YAML 为主（`config/hooks.yaml`），热重载为辅
- 危险操作支持 `confirm` 模式（先 ask，用户确认后 allow）
- 性能上限：Hook 链总耗时 < 10ms / 工具调用

---

## 决策变更记录

| ADR ID | 变更日期 | 变更类型 | 变更内容 | 变更人 |
|--------|---------|---------|---------|--------|
| — | — | — | — | — |

> **变更类型**: 批准 / 废止 / 修订
