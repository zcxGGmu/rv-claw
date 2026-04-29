# rv-claw 开发约束

> 目的：把 `tasks/codex` 中的方案、进度和约束真正变成开发时必须遵守的执行规则。  
> 适用范围：rv-claw 当前全部重构开发工作。  
> 权威性：若与临时实现习惯冲突，以本文件为准；若与用户明确要求冲突，以用户要求为准。

---

## 1. 规则优先级

开发时的判断顺序固定如下：

1. 用户当前回合的明确要求
2. `tasks/design.md`
3. `tasks/codex/rv-claw-refactor-plan.md`
4. `tasks/codex/progress.md`
5. 本文件
6. 旧 ScienceClaw 实现细节

说明：

- 旧 ScienceClaw 代码只提供“兼容基线”和“可复用实现”，不是新的架构权威。
- 当旧实现与新方案冲突时，优先保持前端兼容，再重构内部实现。

---

## 2. 写入边界

### 2.1 允许主动开发的目录

| 目录 | 允许程度 | 说明 |
|------|----------|------|
| `backend/` | 必须 | 新后端主实现目录 |
| `tests/` | 必须 | 单元、集成、E2E、contract tests |
| `tasks/codex/` | 必须 | 计划、进度、约束、决策文档 |
| `ScienceClaw/frontend/` | 允许 | 当前前端实现基线，Release A/B 在此基础上增量改造 |
| `ScienceClaw/task-service/` | 受限允许 | 仅做兼容联调所必需的最小修改 |
| `docker-compose.yml` / `.env.example` / Dockerfile / nginx 配置 | 允许 | 基础设施与发布相关改动 |

### 2.2 不允许无计划侵入的目录

| 目录 | 规则 |
|------|------|
| `ScienceClaw/backend/route/*` | 不允许直接在这里继续扩展新业务实现 |
| `ScienceClaw/backend/deepagent/*` | 不允许散落式改造；如需复用，必须通过 `backend/legacy_bridge/*` |
| `ScienceClaw/sandbox/` | 非 QEMU / 接口阻塞问题，不主动修改 |
| `ScienceClaw/websearch/` | 非集成接口阻塞问题，不主动修改 |
| `Skills/` / `Tools/` | 非兼容性问题，不主动修改内容本身 |

### 2.3 前端目录规则

当前重构阶段，前端实现基线固定为：

- `ScienceClaw/frontend/`

禁止：

- 在尚未完成重构前同时新建顶层 `frontend/` 并双轨开发
- 把 Cases 页面写到与当前前端无关的新目录中

若未来要做前端目录搬迁，必须先满足：

1. Release A 稳定
2. `progress.md` 中新增单独任务
3. 明确迁移收益与回滚策略

---

## 3. 分层职责约束

### 3.1 API 层

目录：

- `backend/api/*`

职责：

- 参数校验
- 认证依赖注入
- 调用 service / domain
- 组装 response
- 流式响应封装

禁止：

- 在 API 函数里写长业务逻辑
- 在 API 层直接编排 LangGraph
- 在 API 层直接操作 repo worktree 或 artifact 文件树

### 3.2 Service / Domain 层

目录：

- `backend/services/*`
- `backend/chat/*`
- `backend/pipeline/*`

职责：

- 业务编排
- 锁与幂等
- DB 读写协调
- artifact / usage ledger / review history 写入

要求：

- service 层是 API 与底层实现之间的主协调面
- 尽量把可测试逻辑放在这里，而不是埋进路由函数

### 3.3 Pipeline 节点层

目录：

- `backend/pipeline/nodes/*`

职责：

- 单阶段输入 -> 单阶段输出
- 通过 adapter 执行 LLM / 工具
- 写入阶段产物
- 发送阶段事件

禁止：

- 直接依赖 FastAPI request/response
- 直接读写前端状态
- 在节点内部埋大量认证/鉴权逻辑

### 3.4 Legacy Bridge 层

目录：

- `backend/legacy_bridge/*`

职责：

- 包裹旧 ScienceClaw 实现
- 暴露稳定的 bridge 接口给新 backend 使用

强约束：

- 新代码不得在 bridge 之外直接 import `ScienceClaw/backend/route/*`
- 新代码尽量不要直接依赖旧 Mongo 文档细节

---

## 4. 数据与文件边界

### 4.1 Chat 与 Pipeline 必须隔离

不允许：

- 把 pipeline 状态塞进 `sessions`
- 把 chat 工作区和 case 工作区混用

必须：

- Chat 使用 `workspace/chat/{session_id}`
- Pipeline 使用 `workspace/cases/{case_id}`

### 4.2 大对象存储规则

以下内容不允许长驻 MongoDB 大文档：

- patch
- build log
- test log
- diff 大文本
- 二进制产物

规则：

- 小型结构化对象进 Mongo
- 中大型文本和二进制进文件系统
- Mongo 只保存引用、摘要和索引字段

### 4.3 统一用量账本

所有 token/cost/duration 统计必须逐步收口到：

- `usage_ledger`

禁止：

- session 统计一套
- case 统计一套
- statistics service 再猜一套

---

## 5. 兼容性变更规则

任何涉及以下对象的修改，必须同步更新 `tasks/codex/compatibility-contracts.md`：

- `/api/v1/auth/*`
- `/api/v1/sessions/*`
- `/api/v1/chat`
- `/api/v1/task/parse-schedule`
- `/api/v1/files/*`
- `/api/v1/statistics/*`
- Chat SSE 事件名或字段

任何涉及以下对象的修改，必须同步更新 `tasks/codex/release-gates.md`：

- Release A/B/C 的准入准出条件
- gate check
- evidence 要求

任何涉及以下对象的修改，必须同步更新 `tasks/codex/decision-log.md`：

- D1-D6
- 新增的架构决策
- 默认方案变化

---

## 6. 进度与范围控制规则

### 6.1 开发前

如果要开始一个未在 `progress.md` 中出现的任务，必须先做其一：

1. 将任务补到 `progress.md`
2. 明确它只是某个现有任务的实现子步骤

### 6.2 开发中

如果发现任务范围明显超出原定义：

1. 暂停继续扩写
2. 更新 `progress.md` / `decision-log.md`
3. 再继续实现

### 6.3 标记完成前

不得只因为“代码写完”就勾选完成。至少需要：

1. 对应验证动作已执行
2. 若涉及接口兼容，contract fixtures 或契约文档已更新
3. 若涉及发布条件，release gate 证据可给出

---

## 7. 测试约束

### 7.1 必须补测试的场景

| 变更类型 | 最低要求 |
|----------|----------|
| 新增 API 路由 | 单元/集成至少其一 |
| 改动兼容接口 | contract fixture 或等价回归验证 |
| 改动 chat SSE | SSE 样例或 contract test 更新 |
| 改动 pipeline 状态机 | 路由/状态测试 |
| 改动 review 提交逻辑 | 幂等/状态卫兵测试 |

### 7.2 不允许的行为

- 不补任何验证就勾选完成
- 明知破坏兼容性但不更新契约文档
- 把“手工本地看过一次”当成所有测试的替代品

---

## 8. 禁止事项

以下行为默认禁止：

1. 原地继续扩写 `ScienceClaw/backend/route/*` 作为新架构主实现
2. 在多个位置重复记录同一份统计口径
3. 前端同时维护两套并行目录进行功能开发
4. 未经过 bridge 直接耦合旧 backend 模块
5. 未更新 `progress.md` 就扩大范围
6. 未经过验证就把任务标记完成
7. 在未有明确任务时修改 sandbox/websearch/Skills/Tools 内容本体

---

## 9. 开发完成判断

只有满足以下条件，某项开发任务才能视为真正完成：

1. 代码落在正确目录
2. 分层职责未被破坏
3. 兼容契约未被无意打破
4. 进度文档状态已更新
5. 对应验证动作已执行

