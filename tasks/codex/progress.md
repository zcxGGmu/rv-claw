# rv-claw 重构开发任务清单 & 进度跟踪

> **版本**: v1.0  
> **日期**: 2026-04-29  
> **关联文档**: `tasks/design.md` / `tasks/codex/rv-claw-refactor-plan.md` / `tasks/codex/development-rules.md` / `tasks/codex/compatibility-contracts.md` / `tasks/codex/release-gates.md` / `tasks/codex/decision-log.md` / `tasks/todo.md`  
> **状态图例**: `[ ]` 待开始 | `[~]` 进行中 | `[x]` 已完成 | `[!]` 阻塞 | `[-]` 已取消  
> **工作量**: S=Small(<2h) | M=Medium(2h-1d) | L=Large(1-3d) | XL=ExtraLarge(3d+)  
> **当前结论**: 规划阶段已完成，代码实现阶段尚未开始。

---

## 使用规则

### 更新规则

1. 每完成一个任务，立即修改对应状态。
2. 每完成一个阶段，更新“全局进度概览”和“当前焦点”。
3. 任何新增范围，必须先补到本文件再开始编码。
4. 如果任务被阻塞，状态改为 `[!]`，并在“阻塞与待决策”中记录原因。
5. 若任务被证明不再需要，状态改为 `[-]`，同时在备注中写清原因。

### 进度统计口径

- `规划任务` 计入当前真实进度。
- `实现任务` 未开始前不得预先标记。
- `完成度` 只按本文件勾选状态统计，不按主观估算。

### 进度展示口径

为避免“规划完成看起来像项目已实现 10%+”的误导，本文件固定使用两套口径：

| 口径 | 统计范围 | 当前值 | 说明 |
|------|----------|--------|------|
| 规划进度 | 仅 `G0` | 100% | 代表方案、范围、跟踪机制已齐备 |
| 实现进度 | `G1-G10` | 0% | 代表代码、联调、发布与验证的真实工程进度 |

约束：

1. 周报、里程碑汇报优先引用 `实现进度`。
2. 若引用 `全局进度概览`，必须同时说明 `G0` 属于规划阶段，不代表代码已落地。
3. Release A/B/C 的 readiness 只能由实现类任务决定，不能被 G0 拉高。

### 批量勾选规则

为避免纯脚手架任务过多制造“虚高进度”，以下任务允许在同一个 PR 中批量完成，但仍需逐项勾选：

- 建目录 / 建空文件 / 建 `__init__.py`
- 初始化配置文件骨架
- 创建测试目录与契约夹具目录

约束：

1. 批量完成不等于可以跳过验证。
2. 批量勾选前必须至少完成一个对应的验证动作。
3. XL 级集成任务不允许用“批量完成”方式一次性带过。

### 状态流转规则

任务状态只能按以下路径流转：

```text
[ ] -> [~] -> [x]
[ ] -> [!]
[~] -> [!]
[!] -> [~]
[ ]/[~] -> [-]
```

约束：

1. 未进入实际开发前，不得把任务从 `[ ]` 直接改为 `[x]`。
2. 一个任务若变成 `[!]`，必须同时在“阻塞与待决策”或任务备注里写清原因。
3. `[-]` 只能用于范围变化后确认不再需要的任务，不能用来规避未完成任务。

### Definition of Ready

任务从 `[ ]` 改成 `[~]` 前，至少要满足：

1. 前置依赖已完成，或已确认可以并行。
2. 若任务依赖 D1-D6 等决策项，该决策已关闭，或已明确按默认方案执行。
3. 已知道本任务主要会改哪些文件/目录。
4. 已知道本任务完成后至少要跑什么验证命令或冒烟动作。
5. 若任务涉及兼容接口，已识别是否需要同步更新 `compatibility-contracts.md` / contract fixtures。

### Definition of Done

任务从 `[~]` 改成 `[x]` 前，至少要满足：

1. 代码或文档改动已落地到正确目录。
2. 本任务声明的验证动作已执行。
3. 若涉及接口、事件流、发布 gate、关键决策，相关文档已同步更新。
4. 若任务属于里程碑关键路径，已有可展示证据。
5. `progress.md` 已更新状态，必要时 `todo.md` 已同步补记。

### 证据归档约定

为避免后续验收时找不到材料，建议所有开发期证据统一放在：

```text
tasks/codex/evidence/
├── release-a/
├── release-b/
└── release-c/
```

推荐归档内容：

- 冒烟记录
- 截图/录屏
- contract test 输出
- integration test 报告
- rollback drill 记录

命名建议：

```text
<milestone>-<task-or-gate>-<yyyymmdd>.md
<milestone>-<task-or-gate>-<yyyymmdd>.png
```

说明：

- 现在可以先不创建这些文件，但一旦进入实际开发，证据应尽量按此路径归档。

### 跨文档同步清单

遇到下列变更时，必须同步更新相应文件：

| 变更类型 | 必同步文件 |
|----------|------------|
| 新增/修改兼容 API | `compatibility-contracts.md`、对应 contract fixtures、`progress.md` |
| 新增/修改 Release 范围 | `release-gates.md`、`progress.md` |
| 新增/修改关键架构决策 | `decision-log.md`、`progress.md` |
| 调整开发边界/目录规则 | `development-rules.md`、`progress.md` |
| 发现范围外功能被纳入 | `progress.md` 的 `Deferred / Out of Scope` |

---

## 当前焦点

- 当前阶段：`G0 规划与治理` 已完成
- 当前规划进度：`100%`
- 当前实现进度：`0%`
- 当前目标：进入 `G1 基础骨架与兼容接管底座`
- 当前建议执行顺序：
  1. `G1.1` 新 backend 骨架与目录
  2. `G1.2` 配置 / 生命周期 / 数据库连接
  3. `G1.3` Compose / Docker / .env
  4. `G1.4` 契约冻结资产

### 当前推荐开发批次

为降低首轮实现风险，建议实际编码时按以下批次推进：

| 批次 | 对应任务 | 目标 |
|------|----------|------|
| Batch A | G1.1 + G1.2 | 新 backend 可启动 |
| Batch B | G1.3 + G1.4 + G2 | 新 backend 可登录并有契约基线 |
| Batch C | G3 | Chat 主链路跑通 |
| Batch D | G4 | 兼容接管收口，准备 Release A |

约束：

1. 首轮不要把 G1/G2 与 G5+ 混在一个开发批次里。
2. Chat 兼容批次不要夹带 Cases UI 改动。
3. Docker/infra 改动与大规模业务改动尽量分开提交。

---

## 全局进度概览

| 阶段 | 名称 | 目标 | 状态 | 完成度 | 备注 |
|------|------|------|------|--------|------|
| G0 | 规划与治理 | 明确重构边界、方案、跟踪机制 | 🟩 | 100% | 已完成 |
| G1 | 基础骨架与兼容底座 | 新 backend 可启动、可连 DB、可承接后续模块 | ⬜ | 0% | 未开始 |
| G2 | 认证与共享平台域 | JWT + RBAC + 用户基础能力 | ⬜ | 0% | 未开始 |
| G3 | Chat 兼容核心 | 新 backend 跑通 sessions/chat/sse/share | ⬜ | 0% | 未开始 |
| G4 | Chat 生态兼容 | files/models/memory/tools/skills/statistics/im/tasks | ⬜ | 0% | 未开始 |
| G5 | Cases 域与工作区 | case schema、artifact、repo worktree、manifest | ⬜ | 0% | 未开始 |
| G6 | Pipeline 引擎与控制面 | LangGraph/PG/Redis/gates/locks/flags | ⬜ | 0% | 未开始 |
| G7 | 五阶段 Agent 节点 | explore/plan/develop/review/test 真正落地 | ⬜ | 0% | 未开始 |
| G8 | Cases 前端与联调 | `/cases` 页面、SSE、审核面板、artifact 视图 | ⬜ | 0% | 未开始 |
| G9 | 统一统计/调度/通知 | usage ledger、task-service、IM、兼容矩阵闭环 | ⬜ | 0% | 未开始 |
| G10 | 验证、灰度、回滚 | contract/integration/e2e/perf/security/rollout | ⬜ | 0% | 未开始 |

---

## 发布波次

| 发布波次 | 目标 | 对应阶段 | Gate Check | Evidence | 状态 |
|----------|------|----------|------------|----------|------|
| Release A | 兼容接管版：新 backend 接住 ScienceClaw 现有前端 | G1-G4 | Chat/Files/Tools/Skills/Tasks/Statistics/IM 冒烟全通过 | contract tests + 冒烟记录 + demo 录屏 | ⬜ |
| Release B | Pipeline 内测版：Cases + 最小五阶段链路 | G5-G8 | Cases CRUD + gate pause/resume + 最小 case lifecycle 跑通 | integration tests + Cases E2E + case artifact 样例 | ⬜ |
| Release C | 生产增强版：QEMU、统一统计、灰度与回滚完备 | G9-G10 | usage ledger 全量接入 + 灰度发布/回滚演练通过 | perf/security/report + rollout checklist + 演练记录 | ⬜ |

---

## 关键任务前置依赖索引（机器可扫描）

> 说明：
>
> 1. 这里只列关键路径任务，不覆盖所有脚手架型 S 任务。
> 2. `depends_on` 使用 `|` 分隔多个前置任务 ID，便于后续脚本解析。
> 3. 若任务未出现在本节，默认以前文阶段顺序和同组小节顺序为准。

```csv
task_id,depends_on,kind,notes
G1.2.3,"G1.1.1|G1.1.2|G1.1.3|G1.1.4|G1.1.5|G1.1.7|G1.1.8",critical,"create_app 依赖核心目录骨架"
G1.3.4,"G1.3.1",critical,"collections 初始化依赖 mongo 封装"
G1.4.2,"G1.2.3|G1.3.1|G1.3.2|G1.3.3",critical,"compose 引入新 backend 前需有应用与 DB 封装"
G1.4.7,"G1.4.1|G1.4.2|G1.4.3|G1.4.4|G1.4.5|G1.2.11|G1.2.12",gate,"本地全量启动是 G1 的退出门"
G2.3.1,"G2.1.1|G2.1.2|G2.2.1|G2.2.2",critical,"login 依赖 token 生成与密码校验"
G2.4.1,"G2.1.3|G2.1.4",critical,"current_user 依赖 token 校验与用户模型"
G2.4.5,"D2|G2.3.1|G2.4.1",gate,"旧 token 切换策略必须在 auth 收口前落定"
G3.1.2,"D3",critical,"run_chat 的实现受 bridge 复用策略影响"
G3.2.2,"G3.1.2|G3.2.1",critical,"ChatRunner.run 依赖 deepagents bridge"
G3.3.2,"G3.3.1|G1.3.4",critical,"create session 依赖 session schema 与集合初始化"
G3.4.1,"G3.3.2|G2.4.1",critical,"创建会话 API 依赖 session service 与 auth 依赖"
G3.5.1,"G3.1.2|G3.2.2|G3.3.2|G2.4.1",gate,"chat SSE 是 Chat 核心链路"
G4.3.10,"G4.3.2",critical,"ToolUniverse API 依赖 tool registry/bridge"
G4.4.10,"G3.1.2",critical,"/api/v1/chat 兼容接口复用旧 chat 执行能力"
G4.4.12,"G4.4.10|G4.4.11",gate,"task-service 联调依赖 chat 与 parse-schedule 接口"
G4.5.5,"G4.5.1|G4.5.2|G4.5.3|G4.5.4",gate,"Release A 准入评审"
G5.2.5,"G1.4.7",critical,"RepoWorkspaceManager 依赖基础环境可启动"
G5.3.5,"G5.3.1|G2.4.1",critical,"create case API 依赖 case service 与 auth"
G6.2.1,"G6.1.1|G6.1.4",critical,"graph 构建依赖 state 与 contracts"
G6.3.4,"G6.3.1|G6.3.2|G6.3.3|G5.3.7",critical,"cases SSE endpoint 依赖事件总线与 case detail"
G6.4.2,"G1.3.3",critical,"case lock 依赖 redis 封装"
G6.5.1,"G6.2.1|G6.4.2|G6.4.3|G5.3.3",critical,"start case API 依赖 graph、锁、guards、case detail"
G6.5.4,"G6.2.5|G6.2.6|G5.1.3|G6.4.2|G6.4.3",critical,"review submit 依赖 routes、review schema、锁与 guards"
G7.1.2,"G7.1.1|G6.1.4",critical,"Claude adapter 依赖抽象接口与 contracts"
G7.1.3,"G7.1.1|G6.1.4",critical,"OpenAI adapter 依赖抽象接口与 contracts"
G7.2.2,"G7.2.1|G5.2.5",critical,"explore 集成依赖 repo workspace 能力"
G7.4.2,"G5.2.5|G7.4.1",critical,"develop 必须接入 worktree"
G7.5.4,"G7.5.1|G7.1.3",critical,"LLM review 聚合依赖 openai adapter"
G7.6.2,"D4|G7.6.1",critical,"Release B 的 test 降级策略受 D4 影响"
G7.6.3,"D5|G7.6.1",critical,"QEMU 真测实现受 D5 影响"
G7.7.3,"G7.2.1|G7.3.1|G7.4.1|G7.5.1|G7.6.1|G7.7.1|G6.5.1|G6.5.4",gate,"最小 case lifecycle 是 Release B 关键门"
G8.1.1,"G5.3.5|G6.5.1|G6.5.4",critical,"前端 cases api 依赖 cases backend 主接口"
G8.4.5,"G8.1.1|G8.2.1|G8.2.4|G8.3.1|G8.3.3|G8.3.4",gate,"Cases E2E 依赖页面与核心组件成型"
G9.1.4,"G9.1.1|G9.1.2|G9.1.3",critical,"统一统计聚合依赖 usage ledger 全路径接入"
G9.4.4,"G1.5.3|G10.1.1|G10.1.2|G10.1.3",gate,"兼容矩阵全绿依赖 contract 测试完成"
G10.1.1,"G1.5.1|G4.5.5",critical,"HTTP contract tests 依赖兼容资产与 Release A 可运行"
G10.1.5,"G6.2.1|G6.5.4|G7.7.3",critical,"核心 integration tests 依赖 graph 与 lifecycle 跑通"
G10.3.4,"G9.4.5|M5",gate,"回切演练依赖 kill switch 策略与最小 Pipeline 已可运行"
```

---

## 阻塞与待决策

> 只有真正阻塞执行的问题才写到这里。

| ID | 决策项 | 当前状态 | 影响阶段 | 建议默认方案 | Owner | 最晚关闭点 | 备注 |
|----|--------|----------|----------|--------------|-------|------------|------|
| D1 | 新 backend 是否与旧 backend 共用同一个 MongoDB database name | [ ] | G1-G4 | 先共用 DB，新增集合前缀清晰隔离 | Backend/Infra | G1.3 完成前 | 影响迁移与回滚策略 |
| D2 | 旧 `user_sessions` token 是否直接失效还是保留一版过渡验证器 | [ ] | G2-G3 | 切换窗口统一失效，要求重新登录 | Backend/Auth | G2.4 完成前 | 影响切换窗口与登录体验 |
| D3 | DeepAgents 通过 bridge import 旧模块，还是复制后维护新副本 | [ ] | G3 | 首版通过 bridge import 复用旧模块 | Backend/Chat | G3.1 完成前 | 影响长期维护成本 |
| D4 | Pipeline `test` 节点首版是否允许仅做编译验证 | [ ] | G7 | Release B 允许编译验证降级 | Backend/Pipeline | G7.6 开始前 | 影响 Release B 范围 |
| D5 | Pipeline 的 QEMU 环境复用现有 sandbox 还是新建专用 service | [ ] | G7-G10 | Release C 新建专用 service 更稳 | Backend/Infra | G7.6.3 开始前 | 影响部署复杂度 |
| D6 | Statistics UI 是否首版加入 `mode` 视图切换 | [ ] | G4/G9 | Release A 不做 UI 切换，Release C 再决定 | Frontend/Stats | G9.1.5 开始前 | 影响前端改动量 |

### 待决策关闭规则

1. `最晚关闭点` 到达前仍未决策的，按 `建议默认方案` 执行。
2. 真正被阻塞时，将该项状态改为 `[!]`，并在备注补充阻塞原因。
3. 关闭后在备注中写明最终决策与日期。

---

## G0：规划与治理（已完成）

> 目标：完成方案定义、范围收敛、文档落盘、跟踪机制建立。  
> 当前状态：已完成。

### G0.1 需求与基线审阅

| # | 任务 | 产出 | 量 | 验证 | 状态 | 备注 |
|---|------|------|----|------|------|------|
| G0.1.1 | 阅读 `tasks/design.md` 的 v4 说明、后端设计、数据设计、部署与测试章节 | 设计摘要 | M | 关键章节已提炼进方案 | [x] | 已完成 |
| G0.1.2 | 审阅 `tasks/ds/adr/*.md`，对齐 LangGraph / 双 SDK / Redis SSE / Chat 复用决策 | ADR 摘要 | M | 关键 ADR 已引用进方案 | [x] | 已完成 |
| G0.1.3 | 盘点当前仓库的 `docker-compose.yml` 服务构成 | 服务拓扑结论 | S | 已形成基线认知 | [x] | 已完成 |
| G0.1.4 | 盘点 ScienceClaw 前端真实路由与页面能力 | 功能清单 | M | 已写入主方案 | [x] | 已完成 |
| G0.1.5 | 盘点前端 API 客户端依赖的后端接口面 | 接口分组清单 | M | 已写入主方案 | [x] | 已完成 |
| G0.1.6 | 盘点旧 backend 真实路由、认证方式、统计/IM/task-service 依赖关系 | 兼容约束结论 | M | 已写入主方案 | [x] | 已完成 |

### G0.2 重构方案编写

| # | 任务 | 产出 | 量 | 验证 | 状态 | 备注 |
|---|------|------|----|------|------|------|
| G0.2.1 | 在 `tasks/codex` 下生成首版重构计划 | `rv-claw-refactor-plan.md` | L | 文件存在且覆盖双模式重构 | [x] | 已完成 |
| G0.2.2 | 第二轮增强：补充模块交付矩阵、schema、切换/回滚、验证矩阵 | 优化后的主方案 | L | 主方案新增详细章节 | [x] | 已完成 |
| G0.2.3 | 第三轮优化：补充发布波次、契约冻结层、反腐层、RepoWorkspaceManager、flags、usage ledger | 工程化优化章节 | L | 主方案新增第 12 节 | [x] | 已完成 |

### G0.3 跟踪机制建立

| # | 任务 | 产出 | 量 | 验证 | 状态 | 备注 |
|---|------|------|----|------|------|------|
| G0.3.1 | 创建 `tasks/todo.md` 作为当前任务清单 | `tasks/todo.md` | S | 文件存在 | [x] | 已完成 |
| G0.3.2 | 创建本文件 `tasks/codex/progress.md` 作为细粒度进度跟踪 | `tasks/codex/progress.md` | M | 文件存在 | [x] | 本任务完成后即成立 |
| G0.3.3 | 定义状态图例、更新规则、阶段划分、发布波次 | 进度管理规则 | S | 本文件头部已包含 | [x] | 已完成 |
| G0.3.4 | 创建 `tasks/codex/development-rules.md` 约束开发写入边界、分层职责与禁止事项 | `tasks/codex/development-rules.md` | M | 文件存在且规则可执行 | [x] | 已完成 |
| G0.3.5 | 创建 `tasks/codex/compatibility-contracts.md` 固化 HTTP/SSE 兼容基线 | `tasks/codex/compatibility-contracts.md` | M | 文件存在且覆盖关键契约 | [x] | 已完成 |
| G0.3.6 | 创建 `tasks/codex/release-gates.md` 固化 Release A/B/C 准入准出标准 | `tasks/codex/release-gates.md` | M | 文件存在且 gate 可核验 | [x] | 已完成 |
| G0.3.7 | 创建 `tasks/codex/decision-log.md` 收口关键架构决策与默认方案 | `tasks/codex/decision-log.md` | M | 文件存在且包含 D1-D6 | [x] | 已完成 |
| G0.3.8 | 在 `progress.md` 中补充 DoR/DoD、证据归档、跨文档同步清单、热点模块与 PR 约束 | `tasks/codex/progress.md` | M | 顶部执行约束已完善 | [x] | 已完成 |

---

## G1：基础骨架与兼容底座

> 目标：建立新的 `backend/` 骨架、基础配置、DB 连接、Compose 和契约冻结资产。  
> 发布归属：Release A。  
> 前置条件：G0 完成。

### G1.1 新 backend 目录与工程骨架

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G1.1.1 | 创建顶层 `backend/` 目录 | `backend/` | S | 目录存在 | [ ] | — |
| G1.1.2 | 创建 `backend/api/` 目录与 `__init__.py` | `backend/api/*` | S | 导入不报错 | [ ] | — |
| G1.1.3 | 创建 `backend/auth/` 目录与 `__init__.py` | `backend/auth/*` | S | 导入不报错 | [ ] | — |
| G1.1.4 | 创建 `backend/chat/` 目录与 `__init__.py` | `backend/chat/*` | S | 导入不报错 | [ ] | — |
| G1.1.5 | 创建 `backend/pipeline/` 目录与 `__init__.py` | `backend/pipeline/*` | S | 导入不报错 | [ ] | — |
| G1.1.6 | 创建 `backend/pipeline/adapters/` 与 `nodes/` | 目录骨架 | S | 目录存在 | [ ] | — |
| G1.1.7 | 创建 `backend/db/` 目录与连接层骨架 | `backend/db/*` | S | 目录存在 | [ ] | — |
| G1.1.8 | 创建 `backend/services/` 目录 | `backend/services/*` | S | 目录存在 | [ ] | — |
| G1.1.9 | 创建 `backend/integrations/` 目录 | `backend/integrations/*` | S | 目录存在 | [ ] | — |
| G1.1.10 | 创建 `backend/legacy_bridge/` 目录 | `backend/legacy_bridge/*` | S | 目录存在 | [ ] | 对应优化方案 |
| G1.1.11 | 创建 `tests/unit/` 目录 | `tests/unit/` | S | 目录存在 | [ ] | — |
| G1.1.12 | 创建 `tests/integration/` 目录 | `tests/integration/` | S | 目录存在 | [ ] | — |
| G1.1.13 | 创建 `tests/e2e/` 目录 | `tests/e2e/` | S | 目录存在 | [ ] | — |
| G1.1.14 | 创建 `tests/contracts/http/` 目录 | `tests/contracts/http/` | S | 目录存在 | [ ] | — |
| G1.1.15 | 创建 `tests/contracts/sse/chat/` 目录 | `tests/contracts/sse/chat/` | S | 目录存在 | [ ] | — |
| G1.1.16 | 创建 `tests/contracts/sse/cases/` 目录 | `tests/contracts/sse/cases/` | S | 目录存在 | [ ] | — |

### G1.2 应用工厂、配置与生命周期

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G1.2.1 | 实现 `backend/config.py` 的 settings 模型 | `backend/config.py` | L | `python -c` 可读取配置 | [ ] | — |
| G1.2.2 | 配置 LLM、Mongo、PG、Redis、Sandbox、Websearch、Feature Flags 环境变量 | `backend/config.py` | L | 默认值和必填项明确 | [ ] | — |
| G1.2.3 | 实现 `backend/main.py:create_app()` | `backend/main.py` | L | `uvicorn ... --factory` 启动 | [ ] | — |
| G1.2.4 | 注册基础中间件：CORS | `backend/main.py` | S | 浏览器跨域正常 | [ ] | — |
| G1.2.5 | 注册安全响应头中间件 | `backend/main.py` | S | `curl -I` 可见头 | [ ] | — |
| G1.2.6 | 实现 lifespan：初始化 Mongo | `backend/main.py` | M | 启动日志可见连接成功 | [ ] | — |
| G1.2.7 | 实现 lifespan：初始化 PostgreSQL checkpointer pool | `backend/main.py` | M | 启动日志可见 PG 成功 | [ ] | — |
| G1.2.8 | 实现 lifespan：初始化 Redis | `backend/main.py` | M | 启动日志可见 Redis 成功 | [ ] | — |
| G1.2.9 | 实现 lifespan：bootstrap admin 钩子 | `backend/main.py` | M | 首次启动有 admin | [ ] | — |
| G1.2.10 | 实现 lifespan：预留 pending pipeline 恢复钩子 | `backend/main.py` | M | 启动不报错 | [ ] | G6 后补实装 |
| G1.2.11 | 实现 `/health` | `backend/main.py` | S | 200 响应 | [ ] | — |
| G1.2.12 | 实现 `/ready` | `backend/main.py` | M | 检查 DB/Redis/依赖 | [ ] | — |
| G1.2.13 | 为 app.state 注入 db / redis / settings / event publisher 占位 | `backend/main.py` | M | 路由可读取 app.state | [ ] | — |

### G1.3 数据层基础设施

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G1.3.1 | 实现 `backend/db/mongo.py` | `backend/db/mongo.py` | M | `ping` 成功 | [ ] | — |
| G1.3.2 | 实现 `backend/db/postgres.py` | `backend/db/postgres.py` | M | pool 可建立 | [ ] | — |
| G1.3.3 | 实现 `backend/db/redis.py` 或等价封装 | `backend/db/redis.py` | S | `ping` 成功 | [ ] | — |
| G1.3.4 | 实现 `backend/db/collections.py` 的集合初始化 | `backend/db/collections.py` | L | 可创建所需集合 | [ ] | — |
| G1.3.5 | 实现 `backend/db/migrations.py` 框架 | `backend/db/migrations.py` | L | 幂等执行 | [ ] | — |
| G1.3.6 | 初始化通用集合索引 | `backend/db/collections.py` | M | index 可见 | [ ] | — |
| G1.3.7 | 初始化 pipeline 集合索引 | `backend/db/collections.py` | M | index 可见 | [ ] | — |
| G1.3.8 | 增加 TTL 索引创建逻辑 | `backend/db/collections.py` | M | TTL 生效 | [ ] | — |

### G1.4 Docker / Compose / 本地开发底座

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G1.4.1 | 编写新 `backend/Dockerfile` | `backend/Dockerfile` | M | 可 build | [ ] | — |
| G1.4.2 | 更新顶层 `docker-compose.yml`，引入新 backend 服务 | `docker-compose.yml` | L | `docker compose config` 通过 | [ ] | — |
| G1.4.3 | 新增 `postgres` 服务 | `docker-compose.yml` | S | healthy | [ ] | — |
| G1.4.4 | 保留 `sandbox/websearch/task-service/frontend` 服务联动 | `docker-compose.yml` | M | 所有服务仍可编排 | [ ] | — |
| G1.4.5 | 编写 `.env.example` | `.env.example` | M | 变量覆盖完整 | [ ] | — |
| G1.4.6 | 预留 feature flag 默认值 | `.env.example` | S | 配置可见 | [ ] | — |
| G1.4.7 | 验证本地全量 `compose up` | — | M | 服务 healthy | [ ] | — |

### G1.5 契约冻结与兼容资产

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G1.5.1 | 生成关键 HTTP 接口样本夹具 | `tests/contracts/http/*` | M | 样本存在 | [ ] | — |
| G1.5.2 | 生成 Chat SSE 样本夹具 | `tests/contracts/sse/chat/*` | M | 样本存在 | [ ] | — |
| G1.5.3 | 建立 `docs/compatibility-matrix.md` | `docs/compatibility-matrix.md` | M | 文件存在 | [ ] | — |
| G1.5.4 | 记录旧接口 -> 新模块映射 | `docs/compatibility-matrix.md` | M | 映射完整 | [ ] | — |

---

## G2：认证与共享平台域

> 目标：用 JWT + RBAC 接住前端登录链路与共享依赖。  
> 发布归属：Release A。  
> 前置条件：G1 完成。

### G2.1 Token 与认证模型

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G2.1.1 | 实现 access token 生成 | `backend/auth/jwt.py` | M | token 可生成 | [ ] | — |
| G2.1.2 | 实现 refresh token 生成 | `backend/auth/jwt.py` | M | token 可生成 | [ ] | — |
| G2.1.3 | 实现 token 校验与过期检测 | `backend/auth/jwt.py` | M | 正常/过期/伪造场景可区分 | [ ] | — |
| G2.1.4 | 设计 `User` / `CurrentUser` Pydantic 模型 | `backend/auth/models.py` | M | 校验正常 | [ ] | — |
| G2.1.5 | 设计 refresh token 持久化结构 | `backend/auth/models.py` / DB | S | schema 明确 | [ ] | — |

### G2.2 用户存储与 bootstrap

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G2.2.1 | 实现 bcrypt hash/verify | `backend/auth/passwords.py` 或等价 | S | 正反验证通过 | [ ] | — |
| G2.2.2 | 实现 admin bootstrap 逻辑 | `backend/auth/bootstrap.py` | M | 首次启动自动创建 | [ ] | — |
| G2.2.3 | 实现 `BOOTSTRAP_UPDATE_ADMIN_PASSWORD` 支持 | `backend/auth/bootstrap.py` | S | 开关生效 | [ ] | — |
| G2.2.4 | 为 `users` 集合创建 unique 索引 | DB | S | index 存在 | [ ] | — |
| G2.2.5 | 为 refresh token 创建 TTL / user 相关索引 | DB | S | index 存在 | [ ] | — |

### G2.3 认证 API

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G2.3.1 | 实现 `POST /api/v1/auth/login` | `backend/api/auth.py` | M | 登录成功 | [ ] | — |
| G2.3.2 | 实现 `POST /api/v1/auth/register` | `backend/api/auth.py` | M | 注册成功 | [ ] | — |
| G2.3.3 | 实现 `GET /api/v1/auth/status` | `backend/api/auth.py` | S | 有/无登录态正确 | [ ] | — |
| G2.3.4 | 实现 `GET /api/v1/auth/me` | `backend/api/auth.py` | S | 返回当前用户 | [ ] | — |
| G2.3.5 | 实现 `POST /api/v1/auth/refresh` | `backend/api/auth.py` | M | 刷新成功 | [ ] | — |
| G2.3.6 | 实现 `POST /api/v1/auth/logout` | `backend/api/auth.py` | S | token 失效 | [ ] | — |
| G2.3.7 | 实现 `POST /api/v1/auth/change-password` | `backend/api/auth.py` | M | 密码可修改 | [ ] | — |
| G2.3.8 | 实现 `POST /api/v1/auth/change-fullname` | `backend/api/auth.py` | S | 姓名可修改 | [ ] | — |
| G2.3.9 | 实现 `GET /api/v1/auth/check-default-password` | `backend/api/auth.py` | S | 正常返回 | [ ] | — |

### G2.4 RBAC 与依赖注入

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G2.4.1 | 实现 `get_current_user()` | `backend/auth/dependencies.py` | M | Bearer token 可解析 | [ ] | — |
| G2.4.2 | 实现 `require_user()` | `backend/auth/dependencies.py` | S | 未登录 401 | [ ] | — |
| G2.4.3 | 实现 `require_admin()` | `backend/auth/dependencies.py` | S | 普通用户 403 | [ ] | — |
| G2.4.4 | 统一 401/403 错误返回 | `backend/auth/dependencies.py` | S | 前端可兼容处理 | [ ] | — |
| G2.4.5 | 决定旧 token 切换策略并落实 | 文档 + 代码 | M | D2 关闭 | [ ] | 待决策 |

---

## G3：Chat 兼容核心

> 目标：新 backend 跑通会话、SSE、stop、share、title、pin 等核心 Chat 链路。  
> 发布归属：Release A。  
> 前置条件：G2 完成。

### G3.1 DeepAgents 反腐层

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G3.1.1 | 实现 `backend/legacy_bridge/deepagents.py` 骨架 | `backend/legacy_bridge/deepagents.py` | M | 可 import | [ ] | — |
| G3.1.2 | 封装 `run_chat()` | 同上 | L | 能拉起一次旧引擎执行 | [ ] | — |
| G3.1.3 | 封装 `stop_chat()` | 同上 | M | 可停止执行 | [ ] | — |
| G3.1.4 | 封装旧事件 -> 新 SSE payload 序列化 | 同上 | L | 前端可识别 | [ ] | — |
| G3.1.5 | 确认旧模块引用边界 | 代码注释 / 文档 | S | 不直接散落 import | [ ] | — |

### G3.2 ChatRunner 与并发控制

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G3.2.1 | 实现 `ChatRunner` 类骨架 | `backend/chat/runner.py` | M | 可实例化 | [ ] | — |
| G3.2.2 | 实现 `ChatRunner.run()` | 同上 | XL | 能接 bridge 推送事件 | [ ] | — |
| G3.2.3 | 实现 `ChatRunner.stop()` | 同上 | M | stop 生效 | [ ] | — |
| G3.2.4 | 实现 `event_stream()` | 同上 | M | SSE 可持续输出 | [ ] | — |
| G3.2.5 | 增加 Chat runner registry | `backend/chat/registry.py` 或等价 | M | 可按 session_id 查找 | [ ] | — |
| G3.2.6 | 增加 session 级锁 | `backend/chat/locks.py` 或等价 | M | 并发 chat 被限制 | [ ] | — |
| G3.2.7 | 增加 runner 清理机制 | `backend/chat/runner.py` | S | 孤儿 runner 可回收 | [ ] | — |

### G3.3 Session 数据模型与服务

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G3.3.1 | 实现 session 文档 schema | `backend/chat/models.py` | M | schema 明确 | [ ] | — |
| G3.3.2 | 实现 create session service | `backend/chat/service.py` | M | 可创建 session | [ ] | — |
| G3.3.3 | 实现 list sessions service | 同上 | M | 排序正确 | [ ] | — |
| G3.3.4 | 实现 get session detail service | 同上 | S | 返回详情 | [ ] | — |
| G3.3.5 | 实现 delete session service | 同上 | M | 级联删除 workspace | [ ] | — |
| G3.3.6 | 实现 update title service | 同上 | S | 标题更新 | [ ] | — |
| G3.3.7 | 实现 pin/unpin service | 同上 | S | 置顶更新 | [ ] | — |
| G3.3.8 | 实现 unread count clear service | 同上 | S | unread 清零 | [ ] | — |
| G3.3.9 | 实现 share/unshare service | 同上 | S | 状态变化正确 | [ ] | — |

### G3.4 Sessions API

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G3.4.1 | `PUT /api/v1/sessions` | `backend/api/sessions.py` | M | 创建成功 | [ ] | — |
| G3.4.2 | `GET /api/v1/sessions` | 同上 | M | 列表返回正常 | [ ] | — |
| G3.4.3 | `GET /api/v1/sessions/{id}` | 同上 | S | 详情正常 | [ ] | — |
| G3.4.4 | `DELETE /api/v1/sessions/{id}` | 同上 | S | 删除成功 | [ ] | — |
| G3.4.5 | `PATCH /api/v1/sessions/{id}/title` | 同上 | S | 标题更新 | [ ] | — |
| G3.4.6 | `PATCH /api/v1/sessions/{id}/pin` | 同上 | S | 置顶更新 | [ ] | — |
| G3.4.7 | `POST /api/v1/sessions/{id}/clear_unread_message_count` | 同上 | S | unread 清零 | [ ] | — |
| G3.4.8 | `POST /api/v1/sessions/{id}/share` | 同上 | S | 共享成功 | [ ] | — |
| G3.4.9 | `DELETE /api/v1/sessions/{id}/share` | 同上 | S | 取消共享 | [ ] | — |
| G3.4.10 | `GET /api/v1/sessions/shared/{id}` | 同上 | M | share 页可读 | [ ] | — |

### G3.5 Chat SSE / stop / 共享联调

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G3.5.1 | `POST /api/v1/sessions/{id}/chat` SSE | `backend/api/sessions.py` | L | curl 可见事件流 | [ ] | — |
| G3.5.2 | `POST /api/v1/sessions/{id}/stop` | 同上 | S | stop 生效 | [ ] | — |
| G3.5.3 | SSE heartbeat 机制 | 同上/runner | S | 长连接稳定 | [ ] | — |
| G3.5.4 | SSE error 终止语义与前端兼容 | 同上 | M | 前端不白屏 | [ ] | — |
| G3.5.5 | Chat contract golden fixture | `tests/contracts/sse/chat/*` | M | 样本齐全 | [ ] | — |

---

## G4：Chat 生态兼容

> 目标：补齐 files/models/memory/tools/skills/statistics/im/task-service 兼容能力。  
> 发布归属：Release A。  
> 前置条件：G3 完成。

### G4.1 文件系统与预览兼容

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G4.1.1 | 实现 upload API | `backend/api/files.py` 或 `sessions.py` | M | 上传成功 | [ ] | — |
| G4.1.2 | 实现 session files list API | `backend/api/sessions.py` | M | 文件列表正常 | [ ] | — |
| G4.1.3 | 实现 `GET /api/v1/files/{id}` 或等价信息接口 | `backend/api/files.py` | M | 元数据可读 | [ ] | — |
| G4.1.4 | 实现 download API | 同上 | M | 可下载 | [ ] | — |
| G4.1.5 | 实现 signed-url 或等价兼容逻辑 | 同上 | M | 预览正常 | [ ] | — |
| G4.1.6 | 实现 sandbox file read API | `backend/api/sessions.py` | M | 文件内容可读 | [ ] | — |
| G4.1.7 | 实现 sandbox file download API | 同上 | M | 下载成功 | [ ] | — |
| G4.1.8 | 加入 allowed prefixes/path traversal 防护 | `backend/services/files.py` | M | 非法路径被拒 | [ ] | — |

### G4.2 Models / Memory / Task Settings

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G4.2.1 | 实现 models schema/service | `backend/api/models.py` 等 | L | CRUD 正常 | [ ] | — |
| G4.2.2 | 实现系统模型初始化 | `backend/services/models.py` 或等价 | M | 首次启动有系统模型 | [ ] | — |
| G4.2.3 | 实现 `GET/PUT /api/v1/memory` | `backend/api/memory.py` | M | memory 可读写 | [ ] | — |
| G4.2.4 | 实现 `GET/PUT /api/v1/task-settings` | `backend/api/task_settings.py` | M | 设置可读写 | [ ] | — |

### G4.3 Skills / Tools / ToolUniverse

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G4.3.1 | 建立 skill registry bridge | `backend/legacy_bridge/skill_registry.py` | M | skills 可列出 | [ ] | — |
| G4.3.2 | 建立 tool registry bridge | `backend/legacy_bridge/tool_registry.py` | M | tools 可列出 | [ ] | — |
| G4.3.3 | 实现 sessions/skills list API | `backend/api/sessions.py` | M | 前端技能页正常 | [ ] | — |
| G4.3.4 | 实现 sessions/skills block API | 同上 | S | 屏蔽生效 | [ ] | — |
| G4.3.5 | 实现 sessions/skills delete API | 同上 | S | 删除生效 | [ ] | — |
| G4.3.6 | 实现 sessions/skills files/read/download API | 同上 | M | 详情页正常 | [ ] | — |
| G4.3.7 | 实现 sessions/{id}/skills/save API | 同上 | M | 可保存 skill | [ ] | — |
| G4.3.8 | 实现 sessions/tools list API | 同上 | M | 前端工具页正常 | [ ] | — |
| G4.3.9 | 实现 sessions/tools block/delete/read/save API | 同上 | M | 功能正常 | [ ] | — |
| G4.3.10 | 实现 ToolUniverse list/detail/run/categories API | `backend/api/tooluniverse.py` | L | 科研工具页正常 | [ ] | — |

### G4.4 Statistics / IM / task-service 兼容

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G4.4.1 | 实现 statistics service v1（先兼容 chat） | `backend/services/statistics.py` | L | summary/models/trends/sessions 正常 | [ ] | — |
| G4.4.2 | 实现 `GET /api/v1/statistics/summary` | `backend/api/statistics.py` | M | 返回正常 | [ ] | — |
| G4.4.3 | 实现 `GET /api/v1/statistics/models` | 同上 | M | 返回正常 | [ ] | — |
| G4.4.4 | 实现 `GET /api/v1/statistics/trends` | 同上 | M | 返回正常 | [ ] | — |
| G4.4.5 | 实现 `GET /api/v1/statistics/sessions` | 同上 | M | 返回正常 | [ ] | — |
| G4.4.6 | 建立 IM bridge | `backend/legacy_bridge/im.py` | M | 可调用旧 IM 能力 | [ ] | — |
| G4.4.7 | 实现 IM settings API | `backend/api/im.py` | M | settings 正常 | [ ] | — |
| G4.4.8 | 实现 Lark bind/status API | 同上 | M | 绑定页正常 | [ ] | — |
| G4.4.9 | 实现 WeChat bridge start/resume/stop/logout/status API | 同上 | L | 管理页正常 | [ ] | — |
| G4.4.10 | 实现 `/api/v1/chat` 兼容接口 | `backend/api/chat.py` | L | task-service 可调用 | [ ] | — |
| G4.4.11 | 实现 `/api/v1/task/parse-schedule` | `backend/api/chat.py` | M | 定时描述解析正常 | [ ] | — |
| G4.4.12 | 复核 task-service 与新 backend 联调 | `task-service` + backend | M | 创建任务后可执行 | [ ] | — |

### G4.5 Release A 验收

| # | 任务 | 产出 | 量 | 验证 | 状态 | 备注 |
|---|------|------|----|------|------|------|
| G4.5.1 | HomePage -> 新建 chat -> SSE 回复 | 冒烟记录 | M | 浏览器验证通过 | [ ] | — |
| G4.5.2 | ChatPage -> stop/share/file upload | 冒烟记录 | M | 浏览器验证通过 | [ ] | — |
| G4.5.3 | Tools/Skills/Statistics/Tasks/Settings 冒烟 | 冒烟记录 | M | 页面可用 | [ ] | — |
| G4.5.4 | SharePage 冒烟 | 冒烟记录 | S | 只读分享可看 | [ ] | — |
| G4.5.5 | Release A 准入评审 | 评审结论 | S | 通过后进入 G5 | [ ] | — |

---

## G5：Cases 域与工作区

> 目标：建立 case 领域模型、artifact 体系、repo cache/worktree/manifest。  
> 发布归属：Release B。  
> 前置条件：Release A 完成。

### G5.1 Cases 数据模型

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G5.1.1 | 定义 `contribution_cases` schema | `backend/pipeline/contracts.py` 或等价 | L | schema 明确 | [ ] | — |
| G5.1.2 | 定义 `stage_outputs` schema | 同上 | M | schema 明确 | [ ] | — |
| G5.1.3 | 定义 `human_reviews` schema | 同上 | M | schema 明确 | [ ] | — |
| G5.1.4 | 定义 `audit_log` schema | 同上 | M | schema 明确 | [ ] | — |
| G5.1.5 | 定义 `usage_ledger` schema | 同上 | M | schema 明确 | [ ] | 对应优化方案 |
| G5.1.6 | 创建相关集合与索引 | DB | M | index 存在 | [ ] | — |

### G5.2 Artifact / Manifest / Workspace 体系

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G5.2.1 | 实现 `ArtifactManager` | `backend/pipeline/artifacts.py` | L | 可保存/读取 artifact | [ ] | — |
| G5.2.2 | 实现 artifact 目录规则 | 文件系统 | M | 目录生成正确 | [ ] | — |
| G5.2.3 | 实现 stage manifest 写入 | `backend/pipeline/artifacts.py` | M | manifest 可见 | [ ] | — |
| G5.2.4 | 实现 stage manifest 读取 | 同上 | S | 可回放 | [ ] | — |
| G5.2.5 | 实现 `RepoWorkspaceManager` 骨架 | `backend/pipeline/repo_workspace.py` | L | 可实例化 | [ ] | — |
| G5.2.6 | 实现 repo-cache 目录管理 | 同上 | M | cache 目录生成 | [ ] | — |
| G5.2.7 | 实现 case worktree 创建 | 同上 | L | worktree 可创建 | [ ] | — |
| G5.2.8 | 实现 base branch / base commit 固化 | 同上 | M | metadata 写入正确 | [ ] | — |
| G5.2.9 | 实现 case 结束后的临时目录清理 | 同上 | M | 清理行为正确 | [ ] | — |

### G5.3 Cases CRUD API

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G5.3.1 | 实现 create case service | `backend/services/cases.py` 或等价 | M | case 可创建 | [ ] | — |
| G5.3.2 | 实现 list cases service | 同上 | M | 可分页/筛选 | [ ] | — |
| G5.3.3 | 实现 get case detail service | 同上 | M | 详情返回完整 | [ ] | — |
| G5.3.4 | 实现 delete case service | 同上 | M | 删除成功 | [ ] | — |
| G5.3.5 | 实现 `POST /api/v1/cases` | `backend/api/cases.py` | M | 创建成功 | [ ] | — |
| G5.3.6 | 实现 `GET /api/v1/cases` | 同上 | M | 列表成功 | [ ] | — |
| G5.3.7 | 实现 `GET /api/v1/cases/{id}` | 同上 | M | 详情成功 | [ ] | — |
| G5.3.8 | 实现 `DELETE /api/v1/cases/{id}` | 同上 | S | 删除成功 | [ ] | — |

---

## G6：Pipeline 引擎与控制面

> 目标：建立 LangGraph、PostgreSQL checkpoint、Redis 事件总线、状态卫兵、Feature Flags。  
> 发布归属：Release B。  
> 前置条件：G5 完成。

### G6.1 Pipeline 状态与契约

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G6.1.1 | 定义 `PipelineState` | `backend/pipeline/state.py` | L | 校验通过 | [ ] | — |
| G6.1.2 | 定义 stage/status 枚举 | 同上 | S | 枚举正确 | [ ] | — |
| G6.1.3 | 定义 review/cost/error 字段 | 同上 | M | 字段完整 | [ ] | — |
| G6.1.4 | 定义 Pydantic 合同对象（ExplorationResult 等） | `backend/pipeline/contracts.py` | L | model_validate 正常 | [ ] | — |

### G6.2 Graph / Checkpoint / Routes

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G6.2.1 | 实现 `build_pipeline_graph()` | `backend/pipeline/graph.py` | L | graph 可编译 | [ ] | — |
| G6.2.2 | 注册 explore/plan/develop/review/test/gate/escalate 节点 | 同上 | M | 节点齐全 | [ ] | — |
| G6.2.3 | 实现线性边与条件边 | 同上 | L | 路由正确 | [ ] | — |
| G6.2.4 | 实现 `AsyncPostgresSaver` 初始化 | `backend/db/postgres.py` / graph | M | checkpoints 表创建 | [ ] | — |
| G6.2.5 | 实现 `route_human_decision()` | `backend/pipeline/routes.py` | M | 路由正确 | [ ] | — |
| G6.2.6 | 实现 `route_review_decision()` | 同上 | M | 迭代路由正确 | [ ] | — |

### G6.3 Redis 事件总线与 Cases SSE

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G6.3.1 | 实现 `EventPublisher` | `backend/pipeline/events.py` | L | 可 publish | [ ] | — |
| G6.3.2 | 实现 Pub/Sub 实时推送 | 同上 | M | 消息可订阅 | [ ] | — |
| G6.3.3 | 实现 Redis Stream 重放 | 同上 | M | 可按 seq 补偿 | [ ] | — |
| G6.3.4 | 实现 cases SSE endpoint | `backend/api/cases.py` | L | SSE 正常 | [ ] | — |
| G6.3.5 | 增加 heartbeat 事件 | 同上 | S | 前端连接稳定 | [ ] | — |
| G6.3.6 | 生成 cases SSE 样本夹具 | `tests/contracts/sse/cases/*` | M | 样本存在 | [ ] | — |

### G6.4 控制面：锁、状态卫兵、Feature Flags

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G6.4.1 | 实现 session lock | `backend/chat/locks.py` | M | 并发请求受控 | [ ] | — |
| G6.4.2 | 实现 case lock | `backend/pipeline/locks.py` | M | 并发 start/review 受控 | [ ] | — |
| G6.4.3 | 实现 pipeline guards | `backend/pipeline/guards.py` | M | 非法状态转换被拒 | [ ] | — |
| G6.4.4 | 实现 feature flags 配置读取 | `backend/config.py` / `backend/services/flags.py` | M | flag 可读 | [ ] | — |
| G6.4.5 | 落地 `FEATURE_CASES_UI_ENABLED` | 配置 + 前后端 | M | 开关生效 | [ ] | — |
| G6.4.6 | 落地 `FEATURE_PIPELINE_EXECUTION_ENABLED` | 配置 + API | M | 开关生效 | [ ] | — |
| G6.4.7 | 落地 `FEATURE_PIPELINE_TEST_NODE_ENABLED` | 配置 + graph | M | 开关生效 | [ ] | — |

### G6.5 Cases 启动 / 停止 / 审核恢复 API

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G6.5.1 | 实现 `POST /api/v1/cases/{id}/start` | `backend/api/cases.py` | M | case 可启动 | [ ] | — |
| G6.5.2 | 实现启动幂等保护 | 同上 + locks | M | 重复 start 不重复执行 | [ ] | — |
| G6.5.3 | 实现 `POST /api/v1/cases/{id}/stop` | 同上 | M | 可停止 | [ ] | 如首版不支持，须显式说明 |
| G6.5.4 | 实现 `POST /api/v1/cases/{id}/review` | 同上 / services/reviews.py | L | 可恢复 graph | [ ] | — |
| G6.5.5 | 为 review 增加 `review_id` 幂等语义 | 同上 | M | 重复提交可去重 | [ ] | — |
| G6.5.6 | 实现 `GET /api/v1/cases/{id}/history` | 同上 | M | 历史可读 | [ ] | — |

---

## G7：五阶段 Agent 节点实现

> 目标：让 Pipeline 真正可执行，而不是只有 graph 空壳。  
> 发布归属：Release B。  
> 前置条件：G6 完成。

### G7.1 Adapter 与资源调度

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G7.1.1 | 定义 `AgentAdapter` 抽象基类 | `backend/pipeline/adapters/base.py` | M | 接口明确 | [ ] | — |
| G7.1.2 | 实现 `ClaudeAgentAdapter` | `backend/pipeline/adapters/claude.py` | L | 可执行 explore/develop/test | [ ] | — |
| G7.1.3 | 实现 `OpenAIAgentAdapter` | `backend/pipeline/adapters/openai.py` | L | 可执行 plan/review | [ ] | — |
| G7.1.4 | 实现 `ResourceScheduler` | `backend/pipeline/resources.py` | M | semaphore 正常 | [ ] | — |
| G7.1.5 | 实现 `CostCircuitBreaker` | `backend/pipeline/cost_guard.py` | M | 超额可熔断 | [ ] | — |
| G7.1.6 | 实现 `usage_ledger` 记录入口 | `backend/services/usage_ledger.py` | M | 可落账 | [ ] | — |

### G7.2 Explore 节点

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G7.2.1 | 实现 `explore_node` 骨架 | `backend/pipeline/nodes/explore.py` | L | 可执行 | [ ] | — |
| G7.2.2 | 接入 Patchwork / websearch / repo analysis | 同上 + integrations | XL | 能生成结果 | [ ] | — |
| G7.2.3 | 实现 evidence 校验与降置信逻辑 | 同上 | M | 幻觉声明被过滤 | [ ] | — |
| G7.2.4 | 保存 explore stage output + manifest | 同上 / artifacts | M | 输出可回读 | [ ] | — |

### G7.3 Plan 节点

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G7.3.1 | 实现 `plan_node` 骨架 | `backend/pipeline/nodes/plan.py` | L | 可执行 | [ ] | — |
| G7.3.2 | 接入 guardrail 校验 | 同上 | M | 非法输入被拒 | [ ] | — |
| G7.3.3 | 生成 dev/test plan 结构化输出 | 同上 | L | schema 验证通过 | [ ] | — |
| G7.3.4 | 保存 plan stage output + manifest | 同上 / artifacts | M | 输出可回读 | [ ] | — |

### G7.4 Develop 节点

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G7.4.1 | 实现 `develop_node` 骨架 | `backend/pipeline/nodes/develop.py` | L | 可执行 | [ ] | — |
| G7.4.2 | 接入 RepoWorkspaceManager worktree | 同上 / repo_workspace | L | 可在独立工作树改代码 | [ ] | — |
| G7.4.3 | 生成 patch / diff / changed_files | 同上 | L | patch 可读 | [ ] | — |
| G7.4.4 | 支持 review 反馈后的迭代修复 | 同上 | L | 第二轮可执行 | [ ] | — |
| G7.4.5 | 保存 develop stage output + manifest | 同上 / artifacts | M | 输出可回读 | [ ] | — |

### G7.5 Review 节点

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G7.5.1 | 实现 `review_node` 骨架 | `backend/pipeline/nodes/review.py` | L | 可执行 | [ ] | — |
| G7.5.2 | 接入 checkpatch.pl | 同上 | M | 风格问题可产出 | [ ] | — |
| G7.5.3 | 接入 sparse/smatch（如可用） | 同上 | M | 静态问题可产出 | [ ] | — |
| G7.5.4 | 实现 LLM 多视角审核聚合 | 同上 | XL | findings 结构化 | [ ] | — |
| G7.5.5 | 实现 severity 加权与收敛检测 | `backend/pipeline/routes.py` | M | review route 正确 | [ ] | — |
| G7.5.6 | 保存 review stage output + manifest | 同上 / artifacts | M | 输出可回读 | [ ] | — |

### G7.6 Test 节点

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G7.6.1 | 实现 `test_node` 骨架 | `backend/pipeline/nodes/test.py` | L | 可执行 | [ ] | — |
| G7.6.2 | 首版实现“编译验证模式” | 同上 | L | Release B 可用 | [ ] | 若 D4 决定降级 |
| G7.6.3 | 实现真实 QEMU 测试模式 | 同上 | XL | Release C | [ ] | 取决于 D5 |
| G7.6.4 | 保存 test logs / result / manifest | 同上 / artifacts | M | 输出可回读 | [ ] | — |

### G7.7 Gate / Escalate / End-to-End

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G7.7.1 | 实现 `human_gate_node` | `backend/pipeline/nodes/human_gate.py` | L | interrupt 正常 | [ ] | — |
| G7.7.2 | 实现 `escalate_node` | `backend/pipeline/nodes/escalate.py` | M | 可进入人工接管 | [ ] | — |
| G7.7.3 | 跑通最小 case 生命周期 | 集成测试 | XL | 从 start 到 completed | [ ] | Release B 关键节点 |

---

## G8：Cases 前端与联调

> 目标：让用户在当前 ScienceClaw 前端中真正看到 Cases 与 Pipeline。  
> 发布归属：Release B。  
> 前置条件：G6/G7 基本完成。

### G8.1 API 与路由接入

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G8.1.1 | 新增 `ScienceClaw/frontend/src/api/cases.ts` | API 客户端 | M | 可调用 CRUD/start/review | [ ] | 保持当前前端目录基线 |
| G8.1.2 | 新增 `ScienceClaw/frontend/src/api/artifacts.ts` | API 客户端 | S | 可拉 artifact | [ ] | 保持当前前端目录基线 |
| G8.1.3 | 新增 `ScienceClaw/frontend/src/composables/useCaseEvents.ts` | composable | M | SSE 正常 | [ ] | 保持当前前端目录基线 |
| G8.1.4 | 在 router 中新增 `/cases` 路由 | 前端路由 | S | 路由可访问 | [ ] | — |
| G8.1.5 | 在 router 中新增 `/cases/:id` 路由 | 前端路由 | S | 路由可访问 | [ ] | — |
| G8.1.6 | 在 `LeftPanel.vue` 中增加 Cases 入口 | UI 入口 | M | 可导航 | [ ] | — |

### G8.2 Cases 页面实现

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G8.2.1 | 实现 `ScienceClaw/frontend/src/pages/CaseListView.vue` 骨架 | 页面 | M | 页面可渲染 | [ ] | — |
| G8.2.2 | 实现 case 列表加载/分页/筛选 | 同上 | M | 列表正常 | [ ] | — |
| G8.2.3 | 实现创建 case 入口 | 同上 | M | 可创建 | [ ] | — |
| G8.2.4 | 实现 `ScienceClaw/frontend/src/pages/CaseDetailView.vue` 骨架 | 页面 | L | 页面可渲染 | [ ] | — |
| G8.2.5 | 实现左栏 case 元信息区 | 同上 | M | 信息显示正确 | [ ] | — |
| G8.2.6 | 实现中栏阶段详情区 | 同上 | L | 随阶段变化 | [ ] | — |
| G8.2.7 | 实现右栏事件流区 | 同上 | M | 实时事件正常 | [ ] | — |

### G8.3 Pipeline 组件

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G8.3.1 | 实现 `ScienceClaw/frontend/src/components/pipeline/PipelineView.vue` | 组件 | L | 可显示 5 阶段 | [ ] | — |
| G8.3.2 | 实现 `ScienceClaw/frontend/src/components/pipeline/StageNode.vue` | 组件 | M | 状态样式正确 | [ ] | — |
| G8.3.3 | 实现 `ScienceClaw/frontend/src/components/review/ReviewPanel.vue` | 组件 | L | 可提交审核 | [ ] | — |
| G8.3.4 | 实现 `ScienceClaw/frontend/src/components/review/DiffViewer.vue` | 组件 | L | patch 可读 | [ ] | — |
| G8.3.5 | 实现 artifact 列表与预览入口 | 组件 | M | preview 正常 | [ ] | — |
| G8.3.6 | 复用 `ActivityPanel.vue` 映射 pipeline 事件 | 组件集成 | M | 日志可看 | [ ] | — |

### G8.4 前后端联调与 E2E

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G8.4.1 | Cases 列表页联调 | 冒烟记录 | M | 列表正常 | [ ] | — |
| G8.4.2 | CaseDetail SSE 联调 | 冒烟记录 | M | 实时更新正常 | [ ] | — |
| G8.4.3 | 审核提交流程联调 | 冒烟记录 | M | approve/reject 生效 | [ ] | — |
| G8.4.4 | Artifact 预览联调 | 冒烟记录 | M | patch/log 可看 | [ ] | — |
| G8.4.5 | Cases E2E 脚本 | `tests/e2e/*` | L | 关键流程通过 | [ ] | — |

---

## G9：统一统计 / 调度 / 通知 / 功能开关闭环

> 目标：把双模式系统层真正打通。  
> 发布归属：Release C。  
> 前置条件：Release B 完成。

### G9.1 统一使用量与统计

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G9.1.1 | 实现 `usage_ledger` 写入服务 | `backend/services/usage_ledger.py` | M | chat/case 都可记账 | [ ] | — |
| G9.1.2 | Chat 路径接入 usage ledger | Chat 代码 | M | session 记账正常 | [ ] | — |
| G9.1.3 | Pipeline 路径接入 usage ledger | Pipeline 代码 | M | case 记账正常 | [ ] | — |
| G9.1.4 | statistics service 支持 `mode=chat|pipeline|all` | `backend/services/statistics.py` | L | 聚合正确 | [ ] | — |
| G9.1.5 | 前端统计 UI 增加 mode 视图（若 D6 决定需要） | 前端 | M | 可切换 | [ ] | 待决策 |

### G9.2 task-service 扩展

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G9.2.1 | 保持 task-service 驱动 Chat 稳定 | 集成结果 | M | 任务执行正常 | [ ] | — |
| G9.2.2 | 评估是否增加“定时创建 Case”模式 | 设计说明 | S | 明确是否纳入 | [ ] | 非首版阻塞项 |
| G9.2.3 | 若纳入，新增 case schedule 接口 | backend + task-service | L | 能创建 case | [ ] | 仅 Release C |

### G9.3 IM 与通知增强

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G9.3.1 | 为 pending review 增加 IM 通知策略 | `backend/api/im.py` / service | M | 触发通知 | [ ] | — |
| G9.3.2 | 增加 pipeline 进度消息模板 | IM 模板 | M | 文案可用 | [ ] | — |
| G9.3.3 | 加入 feature flag 控制 IM pipeline 通知 | flags | S | 开关可控 | [ ] | — |

### G9.4 Feature Flags / Kill Switch / 兼容矩阵闭环

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G9.4.1 | 落地 `FEATURE_NEW_AUTH_ENABLED` | config + logic | M | 可控切换 | [ ] | — |
| G9.4.2 | 落地 `FEATURE_NEW_STATISTICS_ENABLED` | config + logic | M | 可控切换 | [ ] | — |
| G9.4.3 | 落地 `FEATURE_IM_PIPELINE_NOTIFICATIONS_ENABLED` | config + logic | S | 可控切换 | [ ] | — |
| G9.4.4 | 更新 compatibility matrix 为“全绿” | `docs/compatibility-matrix.md` | M | 所有关键接口完成映射 | [ ] | — |
| G9.4.5 | 确认 kill switch 策略 | 文档 + 配置 | M | 可关闭 Cases/Pipeline/test node | [ ] | — |

---

## G10：验证、灰度、回滚

> 目标：证明系统可上线、可灰度、可回滚，而不是只在本地“能跑”。  
> 发布归属：Release C。  
> 前置条件：G9 完成。

### G10.1 合同测试 / 单元 / 集成 / E2E

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G10.1.1 | HTTP contract tests | `tests/contracts/http/*` | L | 关键接口通过 | [ ] | — |
| G10.1.2 | Chat SSE contract tests | `tests/contracts/sse/chat/*` | M | 事件序列稳定 | [ ] | — |
| G10.1.3 | Cases SSE contract tests | `tests/contracts/sse/cases/*` | M | 事件序列稳定 | [ ] | — |
| G10.1.4 | Auth / state / route 单元测试 | `tests/unit/*` | L | 单元全绿 | [ ] | — |
| G10.1.5 | DB / graph / review resume 集成测试 | `tests/integration/*` | XL | 集成全绿 | [ ] | — |
| G10.1.6 | Chat E2E | `tests/e2e/*` | L | 全链路通过 | [ ] | — |
| G10.1.7 | Cases E2E | `tests/e2e/*` | L | 全链路通过 | [ ] | — |

### G10.2 性能 / 安全 / 恢复

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G10.2.1 | 普通 API 压测 | 压测报告 | M | P95/P99 达标 | [ ] | — |
| G10.2.2 | SSE 并发压测 | 压测报告 | M | 100 SSE 连接稳定 | [ ] | — |
| G10.2.3 | Redis 故障恢复验证 | 测试报告 | M | Case SSE 可恢复 | [ ] | — |
| G10.2.4 | PG checkpoint 恢复验证 | 测试报告 | M | 中断 case 可恢复 | [ ] | — |
| G10.2.5 | 安全扫描 | 扫描报告 | M | 无高危漏洞 | [ ] | — |
| G10.2.6 | 路径遍历 / 权限校验专项测试 | 测试报告 | M | 文件接口安全 | [ ] | — |

### G10.3 灰度发布与回滚演练

| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| G10.3.1 | 设计灰度发布顺序（admin -> 内部用户 -> 全量） | 发布手册 | M | 流程清晰 | [ ] | — |
| G10.3.2 | 准备“重新登录一次”公告 | 发布材料 | S | 文案准备好 | [ ] | — |
| G10.3.3 | 预发布环境验收 | 验收记录 | M | 通过 | [ ] | — |
| G10.3.4 | 回切旧 backend 演练 | 演练记录 | M | 可回切 | [ ] | — |
| G10.3.5 | 隐藏 Cases 入口演练 | 演练记录 | S | UI kill switch 正常 | [ ] | — |
| G10.3.6 | 关闭 pipeline execution 演练 | 演练记录 | S | backend kill switch 正常 | [ ] | — |

---

## 里程碑验收点

| 里程碑 | 验收标准 | 必备证据 | 状态 |
|--------|----------|----------|------|
| M0 | 规划文档、todo、progress 三套文档齐全 | 文档文件存在且互相引用正确 | [x] |
| M1 | 新 backend 可启动，可连 Mongo/PG/Redis，可通过 `/health` `/ready` | `docker compose ps` + health/ready 输出截图或日志 | [ ] |
| M2 | 前端可通过新 backend 完成 chat/create/share/file 基线链路 | Chat contract tests + 冒烟录屏 | [ ] |
| M3 | Tools/Skills/Statistics/Tasks/IM 在新 backend 下可用 | 页面冒烟记录 + compatibility matrix 更新 | [ ] |
| M4 | Cases CRUD + graph skeleton + gate pause/resume 可用 | integration test 报告 + SSE 事件样例 | [ ] |
| M5 | 五阶段最小 Pipeline 跑通 | 最小 case lifecycle 测试报告 + artifact 样例 | [ ] |
| M6 | `/cases` 前端页面可创建/审核/查看 artifact | Cases E2E + UI 录屏 | [ ] |
| M7 | 统一统计、通知、灰度与回滚能力完成 | usage ledger 验证 + rollout/checklist + 回滚演练记录 | [ ] |

---

## Deferred / Out of Scope

> 这些事项不是当前执行面默认范围。若要纳入，必须先移动到对应阶段任务里再开始实施。

| ID | 事项 | 默认处理 | 最早纳入波次 | 备注 |
|----|------|----------|--------------|------|
| O1 | Pipeline 自动定时创建 case | 暂缓 | Release C | task-service 首版仅保障 Chat |
| O2 | Pipeline 富 IM 卡片通知 | 暂缓 | Release C | 先保普通通知或无通知 |
| O3 | 多目标仓库并行支持 | 暂缓 | Release C 之后 | 首版先确保单 case 单目标仓稳定 |
| O4 | Knowledge 前端页面 | 暂缓 | 另行立项 | schema 可预留，但 UI 不阻塞 |
| O5 | 复杂 QEMU 回归矩阵 | 暂缓 | Release C | Release B 允许编译验证降级 |
| O6 | 前端目录大搬家到顶层 `frontend/` | 暂缓 | 稳定后 | 当前以 `ScienceClaw/frontend` 为实现基线 |

---

## 任务粒度校准说明

> 本文件允许“脚手架细、集成任务粗”，但要控制在可执行范围内。

校准规则：

1. 纯脚手架任务可以细，但必须可在一个 PR 内批量完成。
2. 任何 XL 任务如果包含两个以上外部依赖，应优先拆成更小任务。
3. 若某个任务连续 2 次被标记为 `[~]` 仍无明确交付物，必须继续拆分。
4. 若多个 S 任务永远一起完成，可在下一轮维护时合并。

### 高风险热点模块

以下模块在后续开发中应视为“高风险触点”，改动前需要额外注意：

| 模块/文件 | 风险原因 |
|-----------|----------|
| `backend/api/auth.py` | 直接影响登录、token、切换窗口 |
| `backend/api/sessions.py` | 直接影响 Chat 主链路与分享能力 |
| `backend/api/chat.py` | 直接影响 task-service 兼容 |
| `backend/api/statistics.py` / `services/statistics.py` | 容易破坏 Settings 中统计页 |
| `backend/legacy_bridge/deepagents.py` | 直接影响 Chat 兼容核心 |
| `backend/pipeline/graph.py` | 一处错误会影响整个 Pipeline 路由 |
| `backend/pipeline/repo_workspace.py` | 直接影响代码树污染、artifact 可复现性 |
| `ScienceClaw/frontend/src/main.ts` | 路由入口，误改会影响全站 |
| `ScienceClaw/frontend/src/components/LeftPanel.vue` | 导航和主工作流入口 |
| `ScienceClaw/frontend/src/pages/ChatPage.vue` | Chat 可见行为核心页面 |
| `ScienceClaw/task-service/*` | 兼容联调失败会导致定时任务整体失效 |

### PR 范围控制建议

为提高 review 质量，建议遵守：

1. 一个 PR 最好只跨一个主域：`auth` / `chat` / `pipeline` / `frontend-cases` / `infra`
2. 不要在一个 PR 里同时大改 `sessions` 和 `cases`
3. 不要把“兼容接管”和“新能力扩展”混在同一个 PR
4. `legacy_bridge` 改动应尽量独立，方便回溯兼容问题
5. 任一 PR 若同时改动高风险热点模块超过 3 个，应考虑拆分

---

## 当前实际进展总结

### 已完成

- [x] 完成设计与现状阅读
- [x] 完成 ScienceClaw 前端/后端/compose/接口面盘点
- [x] 完成 `tasks/codex/rv-claw-refactor-plan.md`
- [x] 完成计划第二轮增强
- [x] 完成计划第三轮优化
- [x] 完成 `tasks/todo.md`
- [x] 完成本 `progress.md`

### 未开始

- [ ] 新 `backend/` 代码骨架
- [ ] 新 compose 切换
- [ ] JWT + RBAC
- [ ] Chat 兼容实现
- [ ] Cases / Pipeline 代码实现
- [ ] Cases 前端页面
- [ ] 验证、灰度、回滚

### 下一步建议

1. 从 `G1.1` 到 `G1.4` 开始落新 backend 基础骨架。
2. 先让 `G2 + G3` 跑通，尽快拿到 Release A 的兼容接管能力。
3. 再进入 `G5-G8`，避免一开始就把 Chat 与 Pipeline 混写。
