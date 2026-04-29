# rv-claw Todo

> 当前任务：基于 `tasks/design.md` 和当前 ScienceClaw 基线，生成完整重构计划。

## Checklist

- [x] 阅读 `tasks/design.md` 的 v4 说明、后端设计、数据设计、部署与测试章节
- [x] 盘点当前仓库的前端路由、前端 API 客户端、后端路由、compose 服务
- [x] 确认 ScienceClaw 前端已暴露的功能边界，避免只围绕 Pipeline 写计划
- [x] 结合 ADR 与现有代码，明确双模式架构与兼容层策略
- [x] 生成详细计划到 `tasks/codex/rv-claw-refactor-plan.md`
- [x] 自查计划是否覆盖 Chat、Pipeline、任务调度、IM、统计、文件、认证、部署与验证
- [x] 对计划进行第二轮增强，补充模块交付矩阵、旧新接口映射、文档 schema、切换/回滚策略、验证矩阵和风险台账
- [x] 对现有方案做第三轮优化评估，补充发布波次、契约冻结层、反腐层、RepoWorkspaceManager、锁与幂等、Feature Flags、usage ledger、artifact manifest、灰度发布路径
- [x] 在 `tasks/codex` 下生成独立的 `progress.md`，细粒度拆分重构开发任务并标记当前规划阶段进度
- [x] 对 `tasks/codex/progress.md` 做第一轮结构优化：修正前端路径、拆分规划/实现进度口径、增强待决策表、补充里程碑证据和 Deferred 区域
- [x] 按需为 `progress.md` 增补关键任务前置依赖索引，支持后续关键路径排程与脚本扫描
- [x] 在 `tasks/codex` 下补齐 4 份执行约束文件：`development-rules.md`、`compatibility-contracts.md`、`release-gates.md`、`decision-log.md`
- [x] 继续增强 `progress.md`：补充 Definition of Ready/Done、证据归档规则、跨文档同步清单、热点模块和 PR 范围控制建议

## Review

- 已确认 `design.md` 的前端正文存在过时内容，计划以当前 ScienceClaw 前端真实行为作为保留边界。
- 已确认缺失 `chat-architecture.md`、`mvp-tasks.md`、`migration-map.md`、`api-contracts.md`，计划已对这些缺口做补完。
- 已确认主策略应为“前端保真 + 后端重构 + 兼容 API + 渐进切换”，而不是原地大改旧 `ScienceClaw/backend`。
- 已完成第二轮细化，当前计划已覆盖：路由与组件复用、Chat/Pipeline 双链路、Case/Session 数据结构、Phase 交付文件、验证场景、上线前 checklist。
- 已完成第三轮方案优化，当前计划已从“完整方案”提升为“可分波次发布、可灰度、可回滚、可契约验证”的工程方案。
- 已新增 `tasks/codex/progress.md`，当前可直接用作后续编码阶段的唯一进度跟踪清单。
- 已完成 `progress.md` 第一轮结构优化，当前更适合用于后续实施、周报与里程碑验收。
- 已补充 `progress.md` 的关键任务依赖索引，当前可以直接用于识别关键路径和安排实现顺序。
- 已补齐执行规则、兼容契约、release gate、决策日志，`tasks/codex` 现在已经具备比较完整的开发约束层。
- 已进一步把执行期最关键的 DoR/DoD、证据归档与跨文档同步规则补进 `progress.md`，现在更适合作为实际开发主控表。
