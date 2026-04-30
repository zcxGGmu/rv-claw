# ScienceClaw → rv-claw 迁移复制规则

> **版本**: v1.0  
> **日期**: 2026-04-29  
> **适用范围**: AI Agent 在迁移 ScienceClaw 代码到 rv-claw 时的决策依据  
> **目标**: 消除"复制还是重写"的决策模糊性，减少无意义的工作量

---

## 0. 核心原则

1. **功能不丢**——ScienceClaw 前端已暴露的全部能力必须在 rv-claw 中继续可用。
2. **后端重写**——后端不能沿用 ScienceClaw 旧实现，必须按 `design.md` 重构。
3. **复制不丢人**——如果 ScienceClaw 的前端代码已经验证过，**原样复制比重写更安全**。
4. **复制后必须适配**——不允许复制后不做任何修改直接提交。

---

## 1. 白名单：可直接复制（Verbatim Copy）

以下 ScienceClaw 文件/目录可以**原样复制**到 rv-claw，只需更新 import 路径（如有）。

### 1.1 前端组件（Vue）

| ScienceClaw 路径 | rv-claw 目标路径 | 说明 |
|------------------|------------------|------|
| `frontend/src/components/layout/MainLayout.vue` | `frontend/src/components/layout/MainLayout.vue` | 主布局，新增 Cases 入口即可 |
| `frontend/src/components/layout/LeftPanel.vue` | `frontend/src/components/layout/LeftPanel.vue` | 左侧导航，增量添加 Cases 路由 |
| `frontend/src/components/chat/ActivityPanel.vue` | `frontend/src/components/chat/ActivityPanel.vue` | 右侧活动流，Pipeline 事件可映射 |
| `frontend/src/components/chat/ToolPanel.vue` | `frontend/src/components/chat/ToolPanel.vue` | 工具面板，仅 Chat 使用 |
| `frontend/src/components/common/FilePreviewModal.vue` | `frontend/src/components/common/FilePreviewModal.vue` | 文件预览，Pipeline artifact 复用 |
| `frontend/src/components/common/MarkdownEnhancements.vue` | `frontend/src/components/common/MarkdownEnhancements.vue` | Markdown 渲染增强 |
| `frontend/src/components/settings/*.vue` | `frontend/src/components/settings/*.vue` | 全部设置子模块（12 个） |
| `frontend/src/components/ui/*.vue` | `frontend/src/components/ui/*.vue` | 基础 UI 组件库 |

### 1.2 前端页面（Views）

| ScienceClaw 路径 | rv-claw 目标路径 | 说明 |
|------------------|------------------|------|
| `frontend/src/views/HomePage.vue` | `frontend/src/views/HomePage.vue` | 首页 |
| `frontend/src/views/ChatPage.vue` | `frontend/src/views/ChatPage.vue` | 聊天页 |
| `frontend/src/views/TasksPage.vue` | `frontend/src/views/TasksPage.vue` | 定时任务 |
| `frontend/src/views/SharePage.vue` | `frontend/src/views/SharePage.vue` | 分享页 |
| `frontend/src/views/ToolsPage.vue` | `frontend/src/views/ToolsPage.vue` | 工具管理 |
| `frontend/src/views/SkillsPage.vue` | `frontend/src/views/SkillsPage.vue` | 技能管理 |

### 1.3 前端基础设施

| ScienceClaw 路径 | rv-claw 目标路径 | 说明 |
|------------------|------------------|------|
| `frontend/src/api/client.ts` | `frontend/src/api/client.ts` | Axios 实例配置 |
| `frontend/src/api/agent.ts` | `frontend/src/api/agent.ts` | Chat API 客户端 |
| `frontend/src/composables/useAuth.ts` | `frontend/src/composables/useAuth.ts` | 认证逻辑 |
| `frontend/src/composables/useSSE.ts` | `frontend/src/composables/useSSE.ts` | SSE 连接管理 |
| `frontend/src/utils/*.ts` | `frontend/src/utils/*.ts` | 通用工具函数 |
| `frontend/src/types/*.ts` | `frontend/src/types/*.ts` | TypeScript 类型定义 |
| `frontend/src/assets/*` | `frontend/src/assets/*` | 静态资源 |
| `frontend/src/i18n/*` | `frontend/src/i18n/*` | 国际化 |

### 1.4 前端配置

| ScienceClaw 路径 | rv-claw 目标路径 | 说明 |
|------------------|------------------|------|
| `frontend/package.json` | `frontend/package.json` | 依赖（新增 cases/pipeline 相关依赖） |
| `frontend/vite.config.ts` | `frontend/vite.config.ts` | 构建配置 |
| `frontend/tsconfig.json` | `frontend/tsconfig.json` | TypeScript 配置 |
| `frontend/tailwind.config.js` | `frontend/tailwind.config.js` | Tailwind 配置 |
| `frontend/.eslintrc.json` | `frontend/.eslintrc.json` | ESLint 配置 |

### 1.5 后端可直接复用的模块

| ScienceClaw 路径 | rv-claw 目标路径 | 说明 |
|------------------|------------------|------|
| `backend/im/*` | `backend/integrations/im/` | IM 集成（Lark/WeChat），包裹复用 |
| `backend/translations/*` | `backend/translations/` | i18n 翻译包 |
| `backend/scripts/*` | `backend/scripts/` | 实用脚本 |

---

## 2. 灰名单：复制后必须适配（Adapt）

以下文件可以复制，但必须做**字段映射、路径调整、或契约适配**。

### 2.1 前端 API 客户端

| ScienceClaw 路径 | 适配动作 |
|------------------|----------|
| `frontend/src/api/auth.ts` | 复制后适配：token 字段名可能从 `access_token` 改为 `accessToken`（依 JWT 实现而定） |
| `frontend/src/api/files.ts` | 复制后适配：确认文件上传路径是否变化 |
| `frontend/src/api/models.ts` | 复制后适配：确认模型配置接口是否新增 `mode` 字段 |
| `frontend/src/api/statistics.ts` | 复制后适配：新增 `mode=chat\|pipeline` 查询参数 |

### 2.2 前端路由

| ScienceClaw 路径 | 适配动作 |
|------------------|----------|
| `frontend/src/router/index.ts` | 复制后新增 `/cases` 和 `/cases/:id` 路由 |
| `frontend/src/main.ts` | 复制后确认全局插件、拦截器 |

### 2.3 后端认证

| ScienceClaw 路径 | 适配动作 |
|------------------|----------|
| `backend/user/models.py` | 复制后新增 `role` 字段（`admin`/`user`） |
| `backend/user/auth.py` | 重写为 JWT（保留路由契约） |

### 2.4 后端 Chat 兼容层

| ScienceClaw 路径 | 适配动作 |
|------------------|----------|
| `backend/route/sessions.py` | 复制后适配为 FastAPI 路由，内部调用 `chat/service.py` |
| `backend/route/chat.py` | 复制后适配：保持 `/api/v1/chat` 给 task-service 调用 |
| `backend/deepagent/*` | 通过 `chat/deepagents_bridge.py` 包裹复用，不直接暴露给 API |

### 2.5 后端文件服务

| ScienceClaw 路径 | 适配动作 |
|------------------|----------|
| `backend/route/files.py` | 复制后拆分：Chat 文件 vs Pipeline artifact 物理分目录 |

---

## 3. 黑名单：必须从零实现（Rewrite）

以下功能**禁止复制** ScienceClaw 代码，必须按 `design.md` 和 `refactor-plan-v3.md` 全新实现。

### 3.1 Pipeline 核心（100% 重写）

| 模块 | 理由 |
|------|------|
| `backend/pipeline/state.py` | ScienceClaw 无 PipelineState |
| `backend/pipeline/graph.py` | ScienceClaw 无 LangGraph |
| `backend/pipeline/nodes/*.py` | 5 阶段节点是 rv-claw 专属 |
| `backend/pipeline/adapters/*.py` | AgentAdapter 抽象层是新的 |
| `backend/pipeline/events.py` | Redis Pub/Sub + Stream 事件总线是新的 |
| `backend/pipeline/artifacts.py` | ArtifactManager 是新的 |
| `backend/pipeline/cost_guard.py` | CostCircuitBreaker 是新的 |
| `backend/pipeline/resources.py` | ResourceScheduler 是新的 |

### 3.2 Cases 领域（100% 重写）

| 模块 | 理由 |
|------|------|
| `backend/api/cases.py` | 全新路由 |
| `backend/services/reviews.py` | 全新服务 |
| `backend/db/collections.py` | 新增集合定义 |

### 3.3 前端 Cases 页面（100% 新建）

| 文件 | 理由 |
|------|------|
| `frontend/src/views/CaseListView.vue` | 全新页面 |
| `frontend/src/views/CaseDetailView.vue` | 全新页面 |
| `frontend/src/api/cases.ts` | 全新 API 客户端 |
| `frontend/src/composables/useCaseEvents.ts` | 全新 SSE 逻辑 |
| `frontend/src/components/pipeline/*.vue` | 全新组件 |
| `frontend/src/components/review/*.vue` | 全新组件 |

### 3.4 基础设施（部分重写）

| 模块 | 理由 |
|------|------|
| `backend/main.py` | 新后端入口，需同时挂载 Chat + Pipeline |
| `backend/config.py` | 新增 PG、Redis、JWT 等配置 |
| `backend/db/postgres.py` | 新增 PostgreSQL 连接层 |
| `backend/db/migrations.py` | 新增迁移脚本 |
| `docker-compose.yml` | 新增 PostgreSQL 服务 |

---

## 4. 文件级映射表（快速查询）

### 4.1 前端

```
ScienceClaw/frontend/src/                     →  rv-claw/frontend/src/
├── components/
│   ├── layout/                               →  白名单：原样复制
│   ├── chat/                                 →  白名单：原样复制
│   ├── common/                               →  白名单：原样复制
│   ├── settings/                             →  白名单：原样复制
│   ├── ui/                                   →  白名单：原样复制
│   ├── pipeline/                             →  黑名单：新建
│   └── review/                               →  黑名单：新建
├── views/                                    →  白名单：原样复制
│   ├── CaseListView.vue                      →  黑名单：新建
│   └── CaseDetailView.vue                    →  黑名单：新建
├── api/
│   ├── client.ts                             →  白名单
│   ├── agent.ts                              →  白名单
│   ├── auth.ts                               →  灰名单：适配 token 字段
│   ├── cases.ts                              →  黑名单：新建
│   └── ...                                   →  白名单/灰名单
├── composables/                              →  白名单：原样复制
│   └── useCaseEvents.ts                      →  黑名单：新建
├── router/                                   →  灰名单：新增路由
└── ...                                       →  白名单
```

### 4.2 后端

```
ScienceClaw/backend/                          →  rv-claw/backend/
├── main.py                                   →  黑名单：重写
├── config.py                                 →  黑名单：重写
├── route/                                    →  灰名单：适配为 FastAPI 路由
│   ├── auth.py                               →  灰名单：适配 JWT
│   ├── sessions.py                           →  灰名单：适配 Chat 兼容层
│   ├── chat.py                               →  灰名单：保持兼容
│   ├── files.py                              →  灰名单：拆分文件域
│   └── ...                                   →  灰名单
├── deepagent/                                →  灰名单：通过 bridge 复用
├── im/                                       →  灰名单：迁入 integrations/
├── user/                                     →  灰名单：适配 JWT + RBAC
├── mongodb/                                  →  灰名单：重构为 db/mongo.py
├── pipeline/                                 →  黑名单：新建
├── api/                                      →  黑名单：新建（FastAPI 路由）
├── services/                                 →  黑名单：新建
├── db/                                       →  黑名单：新建
├── integrations/                             →  灰名单：包裹现有 + 新增
└── ...                                       →  白名单
```

---

## 5. 迁移执行规则

### 5.1 复制前检查

1. **确认文件在白名单**——不在白名单中的文件，不得直接复制。
2. **确认文件未被修改过**——若 ScienceClaw 代码在本会话期间被修改，需重新评估。
3. **确认目标路径不存在**——若已存在，比较差异而非覆盖。

### 5.2 复制后必须做的适配

1. **更新 import 路径**——若目录结构变化，修正所有相对/绝对 import。
2. **更新类型定义**——若后端契约变化，同步前端 TypeScript 类型。
3. **运行 lint**——复制后立即运行 `eslint` / `ruff`，修复格式问题。
4. **运行类型检查**——`mypy` / `tsc --noEmit`，修复类型错误。

### 5.3 禁止的迁移捷径

| 禁止行为 | 理由 |
|----------|------|
| 复制黑名单文件后只做少量修改 | 黑名单文件需要全新设计，不是改几行能解决的 |
| 复制后不运行 lint/type check 直接提交 | 技术债 |
| 为"省事"把 Pipeline 逻辑塞进现有 Chat 文件 | 架构污染 |
| 复制前端代码但忽略后端契约变化 | 运行时错误 |
| 复制 ScienceClaw 的 `backend/main.py` 作为 rv-claw 入口 | 必须重写为双模式入口 |

---

## 6. 迁移验收检查清单

每次迁移一批文件后，必须验证：

```markdown
- [ ] 白名单文件复制后，lint/type check 通过
- [ ] 灰名单文件适配后，功能与原文件一致（或已记录差异）
- [ ] 黑名单文件从零实现，不引用 ScienceClaw 旧代码
- [ ] 新增文件已注册到正确的 index / router / main.py
- [ ] `docker compose up -d` 后服务 healthy
- [ ] 前端页面能正常加载（无 404 chunk）
```

---

> **本规则自 2026-04-29 起生效。所有迁移活动必须遵循本规则的白/灰/黑名单分类。**  
> **规则本身的修改需通过人类工程师审批。**
