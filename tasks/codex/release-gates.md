# rv-claw Release Gates

> 目的：把 Release A / B / C 的准入、准出和证据要求固定下来，防止“代码差不多了”就进入下一波次。  
> 权威性：任何阶段切换都应以本文件为准。

---

## 1. 通用 gate 规则

所有 Release gate 都必须满足：

1. 对应 `progress.md` 阶段任务已更新状态
2. 对应的待决策项已关闭，或按默认方案落地
3. 必备证据可直接展示
4. 未知高风险项不能留白，必须进入阻塞或 deferred

禁止：

- 只靠口头说明进入下一 release
- 明知关键链路未验证仍宣称完成

---

## 2. Release A：兼容接管版

### 目标

新 backend 接住当前 ScienceClaw 前端，不要求 Cases / Pipeline 对外可用。

### 准入前置

- G1 已完成或基本完成
- G2 已完成
- G3 已完成
- G4 已完成
- D1-D3 已关闭或按默认方案执行

### 准出标准

必须全部满足：

1. 登录/刷新/登出正常
2. 创建 chat / 流式聊天 / 停止 / 分享正常
3. 文件上传/预览/下载正常
4. Tools / Skills / Statistics / Tasks / Settings / IM 页面无阻塞性错误
5. task-service 能继续驱动 `/api/v1/chat`
6. Chat SSE 契约与兼容夹具对齐

### 必备证据

- contract tests 结果
- Chat 主链路冒烟记录
- Share 页面冒烟记录
- task-service 联调记录
- 一段 demo 录屏或等价证据

### 不允许带着进入 Release B 的问题

- 无法登录
- chat 主链路不稳定
- task-service 已失效
- Share 页面失效
- IM / Statistics / Task Settings 整体不可用

---

## 3. Release B：Pipeline 内测版

### 目标

Cases 页面和最小五阶段流水线可供内部验证。

### 准入前置

- Release A 通过
- G5 已完成
- G6 已完成
- G7 已完成最小实现
- G8 已完成基本联调
- D4 已关闭或按默认方案执行

### 准出标准

必须全部满足：

1. Cases CRUD 正常
2. `start -> gate -> review -> resume` 正常
3. Redis SSE 能实时推送并支持重放
4. PostgreSQL checkpoint 恢复可用
5. 最小 case lifecycle 可以跑通
6. Cases 前端可查看状态、日志、审核面板和 artifact

### 必备证据

- integration tests 报告
- Cases SSE 样本
- 最小 case artifact 样例
- CaseDetail 页面录屏
- review submit / resume 证明

### 允许降级

- test 节点可只做编译验证
- QEMU 真测可后置到 Release C
- IM 的 pipeline 富通知可暂不开放

### 不允许带着进入 Release C 的问题

- case 无法恢复
- gate 审核不稳定
- 事件流丢失不可恢复
- 前端 Cases 页完全依赖手工刷新

---

## 4. Release C：生产增强版

### 目标

在双模式基础上完成统一统计、灰度、回滚、QEMU 与运维强化。

### 准入前置

- Release B 通过
- G9 已完成
- G10 已完成
- D5/D6 已关闭或按默认方案执行

### 准出标准

必须全部满足：

1. usage ledger 已接入 chat 与 pipeline
2. statistics 支持统一聚合
3. 灰度发布路径明确
4. 回滚策略已演练
5. 关键安全与恢复测试已通过
6. 如纳入 QEMU，则 QEMU 测试能力可用

### 必备证据

- usage ledger 对账结果
- perf/security 报告
- rollout checklist
- rollback drill 记录
- feature flags / kill switch 验证记录

---

## 5. Gate 评审模板

每次进入下一 release 前，建议至少回答：

1. 本 release 的目标是否全部满足？
2. 必备证据是否齐全？
3. 有哪些已知风险被接受？
4. 哪些能力被延期到下一 release？
5. 如果现在切换失败，回滚步骤是什么？

