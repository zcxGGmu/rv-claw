# ScienceClaw 重构 — 验收标准清单

> **用途**: 定义"完成"的精确标准，消除"差不多行了"的模糊性
> **关联文件**: `progress.md` (任务), `constraints.md` (行为边界), `adr.md` (决策)
> **验收层级**: 任务级 → Phase 级 → 里程碑级 → 项目级

---

## 1. 验收哲学

### 1.1 "完成"的定义

一个任务仅当满足以下 **全部条件** 时才能标记为 ✅：

1. **代码已提交**（或已保存到目标路径）
2. **测试通过**（单元测试 + 集成测试，无 skip）
3. **诊断清洁**（`lsp_diagnostics` 无 error，warning 需记录）
4. **文档已更新**（`progress.md` 状态 + 实际工时）
5. **对比无差异**（如涉及 SSE/接口，对比测试通过）

### 1.2 验收角色

| 角色 | 职责 |
|------|------|
| **执行者** | 完成任务并自测，确保 5 个条件满足 |
| **审查者** | 独立运行测试，验证验收标准 |
| **AI Agent** | 执行任务后主动验证，不依赖人工检查 |

---

## 2. 任务级验收标准

### 2.1 代码任务通用验收

| 检查项 | 通过标准 | 验证命令/方法 |
|--------|---------|--------------|
| 文件存在 | 目标路径有文件 | `ls -l <path>` |
| 语法正确 | `python -m py_compile` 通过 | `python -m py_compile <file>` |
| 可导入 | `import` 不抛异常 | `python -c "import module"` |
| 类型清洁 | `lsp_diagnostics` 无 error | 运行 diagnostics |
| 单测通过 | pytest 通过 | `pytest <test_file> -v` |
| 覆盖率达标 | >= 80%（新建 100%） | `pytest --cov` |

### 2.2 重构任务特别验收

重构类任务（如 P0-T2-1 import 替换）需额外验证：

| 检查项 | 通过标准 | 验证方法 |
|--------|---------|---------|
| 无残留旧引用 | `grep` 无结果 | `grep -r "backend.deepagent" --include="*.py"` |
| 无新增循环导入 | 所有模块可独立 import | 逐个 `python -c "import X"` |
| 功能等价 | 行为与重构前一致 | 回归测试通过 |

### 2.3 新增接口任务验收

| 检查项 | 通过标准 | 验证方法 |
|--------|---------|---------|
| 接口签名匹配 ABC | 参数/返回值与 `AgentEngine` 一致 | 静态检查 + 单元测试 |
| 文档完整 | 函数有 docstring，参数有类型注解 | 人工审查 |
| 调用方兼容 | 所有调用点无需修改即可工作 | 全局编译通过 |

---

## 3. Phase 级验收标准

### 3.1 Phase 0: 准备与环境搭建

**必须全部通过：**

| # | 验收项 | 通过标准 | 验证命令 |
|---|--------|---------|---------|
| 0.1 | 目录结构 | `clawagent/` 存在且文件列表与 `deepagent/` 一致 | `diff <(ls deepagent) <(ls clawagent)` |
| 0.2 | Import 替换 | `backend.deepagent` 全局无残留 | `grep -r "backend.deepagent" backend/ --include="*.py"` |
| 0.3 | 循环导入 | 所有模块可独立 import | `python -c "import backend.clawagent.agent"` |
| 0.4 | 依赖安装 | `pip install` 无冲突 | `pip install -r requirements.txt` |
| 0.5 | 软链接切换 | `claw` ↔ `deep` 双向切换 < 30 秒 | `./scripts/switch-agent.sh claw && ./scripts/switch-agent.sh deep` |
| 0.6 | Docker 构建 | `docker compose build backend` 成功 | `docker compose build backend` |
| 0.7 | AgentEngine ABC | `AgentEngine` / `DeepAgentEngine` / `ClaudeAgentEngine` 可实例化 | `pytest tests/test_engine_abc.py` |
| 0.8 | 回滚演练 | 5 分钟内恢复服务 | 计时演练 |

### 3.2 Phase 1: 基础设施搭建

| # | 验收项 | 通过标准 | 验证命令 |
|---|--------|---------|---------|
| 1.1 | 中间件基类 | `MiddlewareStack` 顺序执行正确 | `pytest tests/test_middleware_base.py` |
| 1.2 | Backend 协议 | `FilesystemBackend` + `CompositeBackend` 通过测试 | `pytest tests/test_backend_protocol.py` |
| 1.3 | 路径逃逸 | `../../../etc/passwd` 被拦截 | 单元测试断言 |
| 1.4 | SSE 中间件适配 | 事件捕获与原版一致 | mock 测试 + 手动对比 |
| 1.5 | Offload 中间件适配 | >3000 字符自动落盘 | 单元测试 |
| 1.6 | 无框架依赖 | `clawagent/` 内无 `deepagents` / `langgraph` import | `grep -r "deepagents\|langgraph" clawagent/` |

### 3.3 Phase 2: Agent 核心重写

| # | 验收项 | 通过标准 | 验证命令 |
|---|--------|---------|---------|
| 2.1 | `claw_agent()` 创建 | 返回 `(client, middleware, cw, diag)` 元组 | `pytest tests/test_claw_agent.py` |
| 2.2 | 工具转换 | LangChain `@tool` → SDK Tool 格式正确 | 调用 `convert_langchain_tool_to_sdk()` 验证 |
| 2.3 | 工具包装 | 中间件在工具调用前后触发 | mock 测试 |
| 2.4 | 子 Agent | 独立 `ClaudeSDKClient` 创建成功 | 单元测试 |
| 2.5 | 引擎切换 | `AGENT_IMPL=claude` 和 `AGENT_IMPL=deep` 均工作 | 环境变量切换 + 功能测试 |
| 2.6 | A/B 分流 | user_id hash 分配引擎正确 | 单元测试 |

### 3.4 Phase 3: Runner 流式循环重写

| # | 验收项 | 通过标准 | 验证命令 |
|---|--------|---------|---------|
| 3.1 | 文本对话 | 纯文本查询正常输出 | 端到端测试 |
| 3.2 | 工具调用 | `tool_call_start` + `tool_call_end` 成对出现 | 事件日志检查 |
| 3.3 | Thinking 提取 | reasoning_content 正确透传 | 多模型测试 |
| 3.4 | SSE 对比 | 新旧版本输出格式 100% 匹配 | `python scripts/compare_sse.py --old deep --new claw` |
| 3.5 | 取消功能 | 取消后 stream 立即停止 | 手动测试 + 单元测试 |
| 3.6 | 首 token 延迟 | 不超过旧版 120% | 基准测试脚本 |

### 3.5 Phase 4: 工具与 Skills 适配

| # | 验收项 | 通过标准 | 验证方法 |
|---|--------|---------|---------|
| 4.1 | 内置工具 | web_search / web_crawl / read_file / write_file / edit_file / execute 全部正常 | 逐个手动测试 |
| 4.2 | ToolUniverse | 每类学科至少 1 个工具测试通过 | 抽样测试 |
| 4.3 | Skills | pdf / docx / pptx / xlsx / deep-research / skill-creator / tool-creator 正常 | 手动测试 |
| 4.4 | Sandbox 隔离 | 代码执行不影响宿主机 | 安全测试 |

### 3.6 Phase 5: 功能补齐

| # | 验收项 | 通过标准 | 验证方法 |
|---|--------|---------|---------|
| 5.1 | Monkey-patch 移除 | `engine.py` 中无 patch 代码 | `grep "_convert_dict_to_message\|_patched" engine.py` 无结果 |
| 5.2 | Token 统计 | 误差 < 10% | 对比测试 |
| 5.3 | 历史压缩 | 长历史会话（>20 轮）不溢出 | 压力测试 |
| 5.4 | Hooks 拦截 | `rm -rf /` / `.env` 写操作被拦截 | Hooks 单元测试 |
| 5.5 | 诊断迁移 | 诊断日志完整，来源为 Hooks 而非 LangChain callback | 日志内容检查 |
| 5.6 | 工具自注册 | 新增工具无需修改 `sse_protocol.py` | 手动验证 |
| 5.7 | 全异步 | 无 `asyncio.run()` 在同步上下文中的调用 | `grep -r "asyncio.run" clawagent/` 无结果（测试文件除外） |

### 3.7 Phase 6: 测试与回归

| # | 验收项 | 通过标准 |
|---|--------|---------|
| 6.1 | 单元覆盖率 | >= 80%（整体），100%（新建文件） |
| 6.2 | 集成测试 | 端到端对话、工具调用链、会话生命周期全部通过 |
| 6.3 | 并发测试 | 10 并发会话无冲突 |
| 6.4 | SSE 对比 | 新旧版本输出无差异 |
| 6.5 | 前端兼容 | Vue 前端无需修改即可工作 |
| 6.6 | Bug 清零 | P0/P1 优先级 Bug 全部修复 |

### 3.8 Phase 7: 性能优化

| # | 验收项 | 通过标准 | 验证方法 |
|---|--------|---------|---------|
| 7.1 | 首 token 延迟 | < 旧版 120% | 基准测试 |
| 7.2 | 工具调用延迟 | < 旧版 120% | 基准测试 |
| 7.3 | 内存占用 | < 旧版 120% | 内存分析 |
| 7.4 | MongoDB 查询 | < 100ms | 查询计时 |

### 3.9 Phase 8: 发布与文档

| # | 验收项 | 通过标准 |
|---|--------|---------|
| 8.1 | 文档完整 | README 中英文更新，迁移指南、使用手册完成 |
| 8.2 | Docker 构建 | dev + release 均成功 |
| 8.3 | 灰度 10% | 24 小时错误率 < 1%，P99 延迟达标 |
| 8.4 | 全量发布 | 灰度扩大至 100% 无异常 |
| 8.5 | 回滚验证 | 紧急切换测试通过 |

---

## 4. 里程碑 Go/No-Go 检查表

### CP1: W1 结束

- [ ] Phase 0 全部验收项通过
- [ ] `clawagent/` 目录结构完整，可独立 import
- [ ] `AgentEngine` ABC 定义冻结
- [ ] 团队确认 ADR-001 ~ ADR-005
- **No-Go 处理**: 延期 2 天或调整范围

### CP2: W2 结束

- [ ] Phase 1 全部验收项通过
- [ ] 基础设施代码无框架依赖
- [ ] `DeepAgentEngine` 可正常工作（包装现有代码）
- **No-Go 处理**: 回退到 DeepAgents

### CP3: W3 结束

- [ ] Phase 2 全部验收项通过
- [ ] `claw_agent()` 成功创建 SDK Client
- [ ] 引擎切换机制工作正常
- **No-Go 处理**: 回退到 DeepAgents

### CP4: W4 结束

- [ ] Phase 3 全部验收项通过
- [ ] SSE 对比测试 100% 匹配
- [ ] 首 token 延迟达标
- **No-Go 处理**: 延期修复或回退

### CP5: W6 结束

- [ ] Phase 4 + Phase 5 全部验收项通过
- [ ] 所有内置工具 + Skills + Sandbox 正常
- [ ] Hooks 三层安全检查工作
- [ ] 痛点 #3/#4/#7/#8/#9 已根治
- **No-Go 处理**: 延期修复

### CP6: W8 结束

- [ ] Phase 6 + Phase 7 全部验收项通过
- [ ] 测试覆盖率 > 80%
- [ ] 性能指标达标
- [ ] 灰度发布 10% 无异常（24 小时）
- **No-Go 处理**: 回滚到 DeepAgents

---

## 5. 验收失败的升级流程

```
任务验收失败
    │
    ├── 执行者自检修复（1 次）
    │   └── 通过 → 重新提交审查
    │   └── 失败 →
    │
    ├── 升级至审查者协助（2 次）
    │   └── 通过 → 重新提交审查
    │   └── 失败 →
    │
    ├── 升级至团队技术讨论（3 次）
    │   └── 决策：调整范围 / 延期 / 回退
    │
    └── 记录至风险登记册
```

---

## 6. 验收记录模板

每次 Phase 验收完成后，在本文档末尾追加记录：

```markdown
### 验收记录 — Phase X

| 日期 | 执行者 | 审查者 | 结果 | 未通过项 | 处理措施 |
|------|--------|--------|------|---------|---------|
| YYYY-MM-DD | 姓名 | 姓名 | Pass/Fail | 如有 | 修复/延期/回退 |
```

---

## 更新记录

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-05-02 | v1.0 | 初始创建，包含 3 级验收（任务/Phase/里程碑） |
