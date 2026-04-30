# ScienceClaw → rv-claw 文件迁移映射

> **版本**: v1.0  
> **日期**: 2026-04-30  
> **关联文档**: [migration-rules.md](./migration-rules.md), [refactor-plan-v3.md](./refactor-plan.md)

---

## 1. 前端组件迁移矩阵

### 1.1 布局组件（白名单：原样复制）

| ScienceClaw 路径 | rv-claw 目标路径 | 操作 | 说明 |
|------------------|------------------|------|------|
| `frontend/src/components/layout/MainLayout.vue` | `frontend/src/components/layout/MainLayout.vue` | 复制 + 适配 | 新增 Cases 入口 |
| `frontend/src/components/layout/LeftPanel.vue` | `frontend/src/components/layout/LeftPanel.vue` | 复制 + 适配 | 新增 Cases 路由 |
| `frontend/src/components/layout/AppHeader.vue` | `frontend/src/components/layout/AppHeader.vue` | 复制 | 无变更 |

### 1.2 Chat 组件（白名单：原样复制）

| ScienceClaw 路径 | rv-claw 目标路径 | 操作 | 说明 |
|------------------|------------------|------|------|
| `frontend/src/components/chat/ChatBox.vue` | `frontend/src/components/chat/ChatBox.vue` | 复制 | 无变更 |
| `frontend/src/components/chat/ChatMessage.vue` | `frontend/src/components/chat/ChatMessage.vue` | 复制 | 无变更 |
| `frontend/src/components/chat/ProcessMessage.vue` | `frontend/src/components/chat/ProcessMessage.vue` | 复制 | 无变更 |
| `frontend/src/components/chat/StepMessage.vue` | `frontend/src/components/chat/StepMessage.vue` | 复制 | 无变更 |
| `frontend/src/components/chat/ActivityPanel.vue` | `frontend/src/components/chat/ActivityPanel.vue` | 复制 | 无变更 |
| `frontend/src/components/chat/PlanPanel.vue` | `frontend/src/components/chat/PlanPanel.vue` | 复制 | 无变更 |
| `frontend/src/components/chat/ToolUse.vue` | `frontend/src/components/chat/ToolUse.vue` | 复制 | 无变更 |
| `frontend/src/components/chat/TakeOverView.vue` | `frontend/src/components/chat/TakeOverView.vue` | 复制 | 无变更 |
| `frontend/src/components/chat/SuggestedQuestions.vue` | `frontend/src/components/chat/SuggestedQuestions.vue` | 复制 | 无变更 |
| `frontend/src/components/chat/AttachmentsMessage.vue` | `frontend/src/components/chat/AttachmentsMessage.vue` | 复制 | 无变更 |
| `frontend/src/components/chat/ChatBoxFiles.vue` | `frontend/src/components/chat/ChatBoxFiles.vue` | 复制 | 无变更 |
| `frontend/src/components/chat/toolViews/*.vue` | `frontend/src/components/chat/toolViews/*.vue` | 复制 | 无变更 |

### 1.3 文件系统组件（白名单：原样复制）

| ScienceClaw 路径 | rv-claw 目标路径 | 操作 | 说明 |
|------------------|------------------|------|------|
| `frontend/src/components/common/FilePreviewModal.vue` | `frontend/src/components/common/FilePreviewModal.vue` | 复制 | 无变更 |
| `frontend/src/components/common/FileViewer.vue` | `frontend/src/components/common/FileViewer.vue` | 复制 | 无变更 |
| `frontend/src/components/common/HtmlViewer.vue` | `frontend/src/components/common/HtmlViewer.vue` | 复制 | 无变更 |
| `frontend/src/components/common/ImageViewer.vue` | `frontend/src/components/common/ImageViewer.vue` | 复制 | 无变更 |
| `frontend/src/components/common/VNCViewer.vue` | `frontend/src/components/common/VNCViewer.vue` | 复制 | 无变更 |
| `frontend/src/components/common/MoleculeViewer.vue` | `frontend/src/components/common/MoleculeViewer.vue` | 复制 | 无变更 |
| `frontend/src/components/common/RoundFilesPopover.vue` | `frontend/src/components/common/RoundFilesPopover.vue` | 复制 | 无变更 |
| `frontend/src/components/common/filePreviews/*.vue` | `frontend/src/components/common/filePreviews/*.vue` | 复制 | 无变更 |

### 1.4 设置组件（白名单：原样复制 + 新增）

| ScienceClaw 路径 | rv-claw 目标路径 | 操作 | 说明 |
|------------------|------------------|------|------|
| `frontend/src/components/settings/SettingsDialog.vue` | `frontend/src/components/settings/SettingsDialog.vue` | 复制 | 无变更 |
| `frontend/src/components/settings/SettingsTabs.vue` | `frontend/src/components/settings/SettingsTabs.vue` | 复制 + 适配 | 新增 Pipeline Tab |
| `frontend/src/components/settings/AccountSettings.vue` | `frontend/src/components/settings/AccountSettings.vue` | 复制 | 无变更 |
| `frontend/src/components/settings/ProfileSettings.vue` | `frontend/src/components/settings/ProfileSettings.vue` | 复制 | 无变更 |
| `frontend/src/components/settings/GeneralSettings.vue` | `frontend/src/components/settings/GeneralSettings.vue` | 复制 | 无变更 |
| `frontend/src/components/settings/PersonalizationSettings.vue` | `frontend/src/components/settings/PersonalizationSettings.vue` | 复制 | 无变更 |
| `frontend/src/components/settings/ModelSettings.vue` | `frontend/src/components/settings/ModelSettings.vue` | 复制 | 无变更 |
| `frontend/src/components/settings/NotificationSettings.vue` | `frontend/src/components/settings/NotificationSettings.vue` | 复制 | 无变更 |
| `frontend/src/components/settings/TaskSettings.vue` | `frontend/src/components/settings/TaskSettings.vue` | 复制 | 无变更 |
| `frontend/src/components/settings/TokenStatistics.vue` | `frontend/src/components/settings/TokenStatistics.vue` | 复制 + 适配 | 增加 Pipeline Token 统计 |
| `frontend/src/components/settings/IMSystemSettings.vue` | `frontend/src/components/settings/IMSystemSettings.vue` | 复制 | 无变更 |
| `frontend/src/components/settings/LarkBindingSettings.vue` | `frontend/src/components/settings/LarkBindingSettings.vue` | 复制 | 无变更 |
| `frontend/src/components/settings/WeChatClawBotSettings.vue` | `frontend/src/components/settings/WeChatClawBotSettings.vue` | 复制 | 无变更 |
| `frontend/src/components/settings/ChangePasswordDialog.vue` | `frontend/src/components/settings/ChangePasswordDialog.vue` | 复制 | 无变更 |
| — | `frontend/src/components/settings/PipelineSettings.vue` | 新建 | Pipeline 默认配置 |

### 1.5 Pipeline 组件（黑名单：新建）

| 文件 | 说明 |
|------|------|
| `frontend/src/components/pipeline/PipelineView.vue` | 5 阶段流水线可视化 |
| `frontend/src/components/pipeline/StageNode.vue` | 单阶段节点 |
| `frontend/src/components/pipeline/StageConnector.vue` | 阶段连接线（带状态动画）|
| `frontend/src/components/pipeline/HumanGate.vue` | 人工审核门禁 UI |
| `frontend/src/components/pipeline/IterationBadge.vue` | 迭代轮次标记 |
| `frontend/src/components/pipeline/CostIndicator.vue` | 成本指示器 |
| `frontend/src/components/pipeline/PipelineTimeline.vue` | 时间线视图 |

### 1.6 Review 组件（黑名单：新建）

| 文件 | 说明 |
|------|------|
| `frontend/src/components/review/ReviewPanel.vue` | 审核决策面板 |
| `frontend/src/components/review/ReviewFinding.vue` | 单条审核发现 |
| `frontend/src/components/review/ReviewFindingList.vue` | 审核发现列表 |
| `frontend/src/components/review/DiffViewer.vue` | 基于 Monaco 的 Diff |
| `frontend/src/components/review/ReviewHistory.vue` | 历史审核记录 |

### 1.7 Exploration 组件（黑名单：新建）

| 文件 | 说明 |
|------|------|
| `frontend/src/components/exploration/ContributionCard.vue` | 贡献机会卡片 |
| `frontend/src/components/exploration/EvidenceChain.vue` | 证据链展示 |
| `frontend/src/components/exploration/EvidenceItem.vue` | 单条证据 |
| `frontend/src/components/exploration/FeasibilityBadge.vue` | 可行性评分徽章 |

### 1.8 Planning 组件（黑名单：新建）

| 文件 | 说明 |
|------|------|
| `frontend/src/components/planning/ExecutionPlanTree.vue` | 执行计划树 |
| `frontend/src/components/planning/DevStepCard.vue` | 开发步骤卡片 |
| `frontend/src/components/planning/TestCaseList.vue` | 测试用例列表 |
| `frontend/src/components/planning/RiskBadge.vue` | 风险等级徽章 |

### 1.9 Testing 组件（黑名单：新建）

| 文件 | 说明 |
|------|------|
| `frontend/src/components/testing/TestResultSummary.vue` | 测试结果摘要 |
| `frontend/src/components/testing/TestLogViewer.vue` | 测试日志查看器 |
| `frontend/src/components/testing/QemuStatus.vue` | QEMU 环境状态 |
| `frontend/src/components/testing/CoverageBadge.vue` | 覆盖率徽章 |

### 1.10 Shared 组件（黑名单：新建）

| 文件 | 说明 |
|------|------|
| `frontend/src/components/shared/AgentEventLog.vue` | Agent 实时事件日志 |
| `frontend/src/components/shared/ThinkingBlock.vue` | Agent 思考过程（可折叠）|
| `frontend/src/components/shared/ToolCallView.vue` | 工具调用可视化 |
| `frontend/src/components/shared/ArtifactViewer.vue` | 产物查看器 |

---

## 2. 前端页面迁移矩阵

### 2.1 现有页面（白名单：原样复制）

| ScienceClaw 路径 | rv-claw 目标路径 | 操作 | 说明 |
|------------------|------------------|------|------|
| `frontend/src/views/HomePage.vue` | `frontend/src/views/HomePage.vue` | 复制 | 无变更 |
| `frontend/src/views/ChatPage.vue` | `frontend/src/views/ChatPage.vue` | 复制 | 无变更 |
| `frontend/src/views/TasksPage.vue` | `frontend/src/views/TasksPage.vue` | 复制 | 无变更 |
| `frontend/src/views/TasksListPage.vue` | `frontend/src/views/TasksListPage.vue` | 复制 | 无变更 |
| `frontend/src/views/TaskConfigPage.vue` | `frontend/src/views/TaskConfigPage.vue` | 复制 | 无变更 |
| `frontend/src/views/SharePage.vue` | `frontend/src/views/SharePage.vue` | 复制 | 无变更 |
| `frontend/src/views/ShareLayout.vue` | `frontend/src/views/ShareLayout.vue` | 复制 | 无变更 |
| `frontend/src/views/ToolsPage.vue` | `frontend/src/views/ToolsPage.vue` | 复制 | 无变更 |
| `frontend/src/views/ToolDetailPage.vue` | `frontend/src/views/ToolDetailPage.vue` | 复制 | 无变更 |
| `frontend/src/views/SkillsPage.vue` | `frontend/src/views/SkillsPage.vue` | 复制 | 无变更 |
| `frontend/src/views/SkillDetailPage.vue` | `frontend/src/views/SkillDetailPage.vue` | 复制 | 无变更 |
| `frontend/src/views/ScienceToolDetail.vue` | `frontend/src/views/ScienceToolDetail.vue` | 复制 | 无变更 |
| `frontend/src/views/LoginPage.vue` | `frontend/src/views/LoginPage.vue` | 复制 | 无变更 |

### 2.2 新增页面（黑名单：新建）

| 文件 | 说明 |
|------|------|
| `frontend/src/views/CaseListView.vue` | 案例列表 |
| `frontend/src/views/CaseDetailView.vue` | 案例详情（核心页面）|
| `frontend/src/views/StatisticsPage.vue` | 统计页（替代 MetricsView）|

### 2.3 废弃页面

| ScienceClaw 路径 | 处理方式 | 说明 |
|------------------|----------|------|
| `frontend/src/views/MetricsView.vue` | 删除 | 被 StatisticsPage 替代 |

---

## 3. 前端 API 客户端迁移矩阵

### 3.1 保留的 API（白名单：原样复制）

| ScienceClaw 路径 | rv-claw 目标路径 | 操作 | 说明 |
|------------------|------------------|------|------|
| `frontend/src/api/client.ts` | `frontend/src/api/client.ts` | 复制 | 无变更 |
| `frontend/src/api/agent.ts` | `frontend/src/api/agent.ts` | 复制 | 无变更 |
| `frontend/src/api/files.ts` | `frontend/src/api/files.ts` | 复制 | 无变更 |
| `frontend/src/api/im.ts` | `frontend/src/api/im.ts` | 复制 | 无变更 |
| `frontend/src/api/memory.ts` | `frontend/src/api/memory.ts` | 复制 | 无变更 |
| `frontend/src/api/models.ts` | `frontend/src/api/models.ts` | 复制 | 无变更 |
| `frontend/src/api/webhooks.ts` | `frontend/src/api/webhooks.ts` | 复制 | 无变更 |

### 3.2 适配的 API（灰名单：复制 + 适配）

| ScienceClaw 路径 | 操作 | 说明 |
|------------------|------|------|
| `frontend/src/api/auth.ts` | 复制 + 适配 | 返回 role 信息 |
| `frontend/src/api/statistics.ts` | 复制 + 适配 | endpoint 改为 /statistics |

### 3.3 新增的 API（黑名单：新建）

| 文件 | 说明 |
|------|------|
| `frontend/src/api/cases.ts` | 案例 CRUD + SSE |
| `frontend/src/api/reviews.ts` | 审核 API |
| `frontend/src/api/artifacts.ts` | 产物 API |

---

## 4. 前端 Composable 迁移矩阵

### 4.1 保留的 Composable（白名单：原样复制）

| ScienceClaw 路径 | rv-claw 目标路径 | 操作 |
|------------------|------------------|------|
| `frontend/src/composables/useAuth.ts` | `frontend/src/composables/useAuth.ts` | 复制 + 适配 |
| `frontend/src/composables/usePendingChat.ts` | `frontend/src/composables/usePendingChat.ts` | 复制 |
| `frontend/src/composables/useMessageGrouper.ts` | `frontend/src/composables/useMessageGrouper.ts` | 复制 |
| `frontend/src/composables/useLeftPanel.ts` | `frontend/src/composables/useLeftPanel.ts` | 复制 |
| `frontend/src/composables/useSessionGrouping.ts` | `frontend/src/composables/useSessionGrouping.ts` | 复制 |
| `frontend/src/composables/useSessionListUpdate.ts` | `frontend/src/composables/useSessionListUpdate.ts` | 复制 |
| `frontend/src/composables/useSessionNotifications.ts` | `frontend/src/composables/useSessionNotifications.ts` | 复制 |
| `frontend/src/composables/useSessionFileList.ts` | `frontend/src/composables/useSessionFileList.ts` | 复制 |
| `frontend/src/composables/useFilePanel.ts` | `frontend/src/composables/useFilePanel.ts` | 复制 |
| `frontend/src/composables/useRightPanel.ts` | `frontend/src/composables/useRightPanel.ts` | 复制 |
| `frontend/src/composables/useTool.ts` | `frontend/src/composables/useTool.ts` | 复制 |
| `frontend/src/composables/useTime.ts` | `frontend/src/composables/useTime.ts` | 复制 |
| `frontend/src/composables/useI18n.ts` | `frontend/src/composables/useI18n.ts` | 复制 |
| `frontend/src/composables/useTheme.ts` | `frontend/src/composables/useTheme.ts` | 复制 |
| `frontend/src/composables/useResizeObserver.ts` | `frontend/src/composables/useResizeObserver.ts` | 复制 |
| `frontend/src/composables/useDialog.ts` | `frontend/src/composables/useDialog.ts` | 复制 |
| `frontend/src/composables/useContextMenu.ts` | `frontend/src/composables/useContextMenu.ts` | 复制 |
| `frontend/src/composables/useSettingsDialog.ts` | `frontend/src/composables/useSettingsDialog.ts` | 复制 |

### 4.2 新增的 Composable（黑名单：新建）

| 文件 | 说明 |
|------|------|
| `frontend/src/composables/useCaseEvents.ts` | SSE 事件流管理 |
| `frontend/src/composables/usePipeline.ts` | Pipeline 状态追踪 |
| `frontend/src/composables/useReview.ts` | 审核操作封装 |
| `frontend/src/composables/useCaseStore.ts` | 案例状态管理 |
| `frontend/src/composables/usePipelineStore.ts` | Pipeline 运行状态 |
| `frontend/src/composables/useReviewStore.ts` | 审核状态 |

---

## 5. 后端文件迁移矩阵

### 5.1 保留的后端模块（白名单/灰名单）

| ScienceClaw 路径 | rv-claw 目标路径 | 操作 | 说明 |
|------------------|------------------|------|------|
| `backend/im/*` | `backend/integrations/im/` | 复制 + 适配 | 包裹复用 |
| `backend/translations/*` | `backend/translations/` | 复制 | 无变更 |
| `backend/scripts/*` | `backend/scripts/` | 复制 | 无变更 |

### 5.2 适配的后端模块（灰名单）

| ScienceClaw 路径 | rv-claw 目标路径 | 操作 | 说明 |
|------------------|------------------|------|------|
| `backend/route/auth.py` | `backend/route/auth.py` | 复制 + 适配 | 适配 JWT + RBAC |
| `backend/route/sessions.py` | `backend/route/sessions.py` | 复制 + 适配 | 适配 Chat 兼容层 |
| `backend/route/chat.py` | `backend/route/chat.py` | 复制 + 适配 | 保持兼容 |
| `backend/route/files.py` | `backend/route/files.py` | 复制 + 适配 | 拆分文件域 |
| `backend/route/models.py` | `backend/route/models.py` | 复制 | 无变更 |
| `backend/route/tooluniverse.py` | `backend/route/tooluniverse.py` | 复制 | 无变更 |
| `backend/route/task_settings.py` | `backend/route/task_settings.py` | 复制 | 无变更 |
| `backend/route/memory.py` | `backend/route/memory.py` | 复制 | 无变更 |
| `backend/route/science.py` | `backend/route/science.py` | 复制 | 无变更 |
| `backend/route/statistics.py` | `backend/route/statistics.py` | 复制 + 适配 | endpoint 改为 /statistics |
| `backend/route/im.py` | `backend/route/im.py` | 复制 | 无变更 |
| `backend/user/models.py` | `backend/user/models.py` | 复制 + 适配 | 新增 role 字段 |
| `backend/user/auth.py` | `backend/user/auth.py` | 复制 + 适配 | 重写为 JWT |
| `backend/user/bootstrap.py` | `backend/user/bootstrap.py` | 复制 + 适配 | 确保 admin role |
| `backend/mongodb/db.py` | `backend/db/mongo.py` | 复制 + 适配 | 重构为 db/mongo.py |
| `backend/deepagent/*` | `backend/chat/deepagents_bridge.py` | 复制 + 适配 | 通过 bridge 复用 |

### 5.3 新建的后端模块（黑名单）

| 文件 | 说明 |
|------|------|
| `backend/main.py` | 新后端入口（双模式）|
| `backend/config.py` | 新增 PG、Redis、JWT 配置 |
| `backend/pipeline/` | Pipeline 引擎目录 |
| `backend/adapters/` | SDK 适配器目录 |
| `backend/datasources/` | 数据源目录 |
| `backend/contracts/` | 数据契约目录 |
| `backend/db/postgres.py` | PostgreSQL 连接层 |
| `backend/db/collections.py` | 集合初始化与索引 |
| `backend/db/audit.py` | 审计日志写入 |
| `backend/db/migrations/` | 迁移脚本 |
| `backend/route/cases.py` | 案例 CRUD |
| `backend/route/reviews.py` | 人工审核 |
| `backend/route/artifacts.py` | 产物管理 |
| `backend/route/pipeline.py` | Pipeline 控制 |
| `backend/config/secrets.py` | Secrets 管理 |
| `backend/config/features.py` | Feature Flag |
| `backend/scheduler.py` | 资源调度器 |

---

## 6. 文件重命名/路径变更清单

| 原路径 | 新路径 | 变更原因 |
|--------|--------|----------|
| `backend/mongodb/db.py` | `backend/db/mongo.py` | 统一数据库层命名 |
| `backend/mongodb/` | `backend/db/` | 合并 MongoDB + PostgreSQL |
| `backend/deepagent/` | `backend/chat/deepagents_bridge.py` | 通过 bridge 复用 |
| `frontend/src/views/MetricsView.vue` | `frontend/src/views/StatisticsPage.vue` | 重命名 |
| `frontend/src/api/statistics.ts` | `frontend/src/api/statistics.ts` | 路径不变，endpoint 变更 |

---

## 7. 废弃 API 清单

| 方法 | 原路径 | 处理方式 | 替代路径 |
|------|--------|----------|----------|
| GET | `/api/v1/metrics/overview` | 废弃/重定向 | `/api/v1/statistics/summary` |
| GET | `/api/v1/metrics/costs` | 废弃/重定向 | `/api/v1/statistics/costs` |
| GET | `/api/v1/metrics/models` | 废弃/重定向 | `/api/v1/statistics/models` |
| GET | `/api/v1/metrics/trends` | 废弃/重定向 | `/api/v1/statistics/trends` |
| GET | `/api/v1/metrics/sessions` | 废弃/重定向 | `/api/v1/statistics/sessions` |

---

> **本文档自 2026-04-30 起生效。所有迁移活动必须遵循本文档的映射关系。**
> **映射变更需通过人类工程师审批。**
