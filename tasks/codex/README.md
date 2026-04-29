# tasks/codex 文档索引

> 用途：说明 `tasks/codex` 下各文档的职责，以及后续开发时的推荐使用顺序。

---

## 文件清单

| 文件 | 作用 |
|------|------|
| `rv-claw-refactor-plan.md` | 主方案文档，定义目标架构、重构策略、阶段划分、风险与优化方向 |
| `progress.md` | 开发任务主控表，定义阶段任务、依赖关系、里程碑、Release 波次与进度状态 |
| `development-rules.md` | 开发行为约束，定义目录写入边界、分层职责、禁止事项、DoR/DoD 等 |
| `compatibility-contracts.md` | 兼容契约基线，定义必须保持兼容的 HTTP/SSE/前端行为 |
| `release-gates.md` | 发布门禁文档，定义 Release A/B/C 的准入、准出和证据要求 |
| `decision-log.md` | 关键决策台账，记录默认方案、最终拍板结果与影响范围 |

---

## 推荐使用顺序

### 1. 第一次进入项目

推荐阅读顺序：

1. `rv-claw-refactor-plan.md`
2. `progress.md`
3. `development-rules.md`
4. `compatibility-contracts.md`
5. `release-gates.md`
6. `decision-log.md`

目的：

- 先理解“做什么”
- 再理解“先做什么”
- 最后理解“开发时不能怎么做”

### 2. 真正开始开发前

最少要看这 4 份：

1. `progress.md`
2. `development-rules.md`
3. `compatibility-contracts.md`
4. `decision-log.md`

检查点：

- 当前要做的任务是否已经在 `progress.md` 中
- 改动目录是否符合 `development-rules.md`
- 是否会影响兼容接口或 SSE 契约
- 是否命中了尚未关闭的关键决策项

### 3. 开发过程中

如果你正在：

- 改兼容接口：优先看 `compatibility-contracts.md`
- 改阶段顺序/范围：优先看 `progress.md`
- 改目录结构/模块边界：优先看 `development-rules.md`
- 准备进入下一个 release：优先看 `release-gates.md`
- 遇到架构分歧：优先看 `decision-log.md`

### 4. 发布或验收前

推荐顺序：

1. `progress.md`
2. `release-gates.md`
3. `compatibility-contracts.md`
4. `decision-log.md`

目的：

- 确认当前阶段是否真的完成
- 确认 release gate 是否具备证据
- 确认没有无意破坏兼容性
- 确认关键决策没有悬空

---

## 使用规则

1. 新增开发范围前，先更新 `progress.md`
2. 改兼容行为前，先看 `compatibility-contracts.md`
3. 改关键边界前，先看 `development-rules.md`
4. 改发布目标前，先更新 `release-gates.md`
5. 新出现的关键架构决策，先写入 `decision-log.md`

---

## 最小开发闭环

如果后续要开始写代码，推荐最小动作顺序：

1. 在 `progress.md` 里找到当前任务
2. 用 `development-rules.md` 确认写入边界
3. 用 `compatibility-contracts.md` 确认是否会影响旧前端
4. 若涉及未决问题，先检查 `decision-log.md`
5. 开发完成后回到 `progress.md` 更新状态

