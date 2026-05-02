# ScienceClaw 前端知识库

> **范围**: `ScienceClaw/frontend/`
> **技术栈**: Vue 3 + TypeScript + Tailwind CSS + Vite

---

## 目录结构

```
frontend/
├── src/
│   ├── main.ts                 # Vue 应用入口
│   ├── App.vue                 # 根组件
│   ├── router/                 # Vue Router
│   ├── pages/                  # 页面级组件
│   │   ├── Home.vue
│   │   ├── Chat.vue            # 主聊天界面
│   │   ├── Sessions.vue        # 会话列表
│   │   └── Settings.vue        # 设置页
│   ├── components/             # 可复用组件
│   │   ├── chat/               # 聊天相关组件
│   │   ├── filePreviews/       # 文件预览组件
│   │   ├── settings/           # 设置表单组件
│   │   └── ui/                 # 基础 UI 组件（shadcn/vue）
│   ├── composables/            # Vue Composition 函数
│   ├── api/                    # API 调用封装
│   ├── types/                  # TypeScript 类型定义
│   └── utils/                  # 工具函数
├── public/                     # 静态资源
├── index.html                  # HTML 模板
├── vite.config.ts              # Vite 配置
├── tailwind.config.js          # Tailwind 配置
└── package.json
```

---

## 技术栈详情

| 类别 | 技术 | 版本 |
|------|------|------|
| 框架 | Vue 3 | ^3.4 |
| 语言 | TypeScript | ^5.3 |
| 样式 | Tailwind CSS | ^3.4 |
| 构建 | Vite | ^5.0 |
| 路由 | Vue Router | ^4.2 |
| 状态 | Pinia | — |
| UI 组件 | reka-ui (headless) + shadcn-vue | — |
| 图标 | lucide-vue-next | — |
| HTTP | axios | — |
| SSE | EventSource | — |
| 编辑器 | monaco-editor | — |
| 终端 | xterm.js | — |
| 远程桌面 | noVNC | — |

---

## 核心功能

### 聊天界面（pages/Chat.vue）

- **输入**: 文本 + 附件上传
- **输出**: SSE 流式渲染（thinking、tool_call、message 事件）
- **工具展示**: 工具调用开始/结束的状态卡片
- **文件管理**: 侧边栏展示 workspace 文件

### SSE 事件处理

前端通过 `EventSource` 连接后端 `/sessions/{id}/stream`：

```typescript
// 事件类型对应 UI 行为
"thinking"      → 打字机效果渲染文本
"tool_call_start" → 展开工具卡片，显示"执行中"
"tool_call_end"   → 更新工具卡片，显示结果/文件链接
"plan_update"     → 更新左侧计划面板
"message"         → 完成消息气泡
"error"           → 红色错误提示
```

### 会话管理（pages/Sessions.vue）

- 会话列表（标题、时间、状态）
- 新建会话
- 删除会话
- 搜索历史会话

---

## API 集成

API 封装在 `src/api/` 目录：

```typescript
// 典型 API 结构
api.sessions.create()        // POST /sessions
api.sessions.list()          // GET /sessions
api.sessions.delete(id)      // DELETE /sessions/{id}
api.chat.stream(sessionId)   // SSE /sessions/{id}/stream
api.files.list()             // GET /files
api.files.download(path)     // GET /files/download
```

---

## 约定

- **组件命名**: PascalCase，多词组件名（如 `ChatMessage.vue`）
- **组合式函数**: 使用 `useXxx` 命名，放在 `composables/` 目录
- **类型定义**: 接口用 `I` 前缀或纯 PascalCase，放在 `types/` 目录
- **样式**: 优先使用 Tailwind 工具类，复杂样式用 `<style scoped>`
- **图标**: 使用 `lucide-vue-next`（shadcn 标准）

---

## 反模式

| 禁止行为 | 正确做法 |
|---------|---------|
| 在组件中直接调用 `fetch()` | 使用 `api/` 封装的请求函数 |
| 硬编码后端 URL | 使用环境变量 `import.meta.env.VITE_API_BASE` |
| 在 `<script setup>` 中写复杂业务逻辑 | 提取到 `composables/` 中 |
| 使用 Options API（新项目） | 统一使用 Composition API + `<script setup>` |
| 忽略 TypeScript 类型 | 所有 API 响应定义接口 |

---

## 开发命令

```bash
# 安装依赖
npm install

# 开发服务器（Vite 代理：/api -> backend:12001, /task-service -> scheduler:12002）
npm run dev          # http://localhost:5173

# 构建（生产模式用 Nginx 静态服务）
npm run build        # 输出到 dist/

# 预览生产构建
npm run preview

# 类型检查
npx vue-tsc --noEmit
```

---

## 前端架构

```
frontend/src/
├── api/           # 12 个 API 客户端模块 (axios)
├── composables/   # 18 个 Vue composables (useAuth, useTool, useI18n...)
├── components/    # ~100 个组件
│   ├── chat/               # 聊天组件
│   ├── filePreviews/       # 文件预览
│   ├── settings/           # 设置表单
│   ├── toolViews/          # 工具视图
│   ├── login/              # 登录相关
│   ├── icons/              # 图标集合
│   └── ui/                 # reka-ui / shadcn 基础组件
├── pages/         # 14 个页面
├── types/         # TypeScript 类型定义
├── utils/         # 工具函数 (time, auth, toast, eventBus, markdown)
├── locales/       # i18n (zh.ts + en.ts)
├── constants/     # 常量 (event, tool)
└── lib/           # shadcn-vue 工具函数
```

---

## 环境变量

| 变量 | 用途 | 默认值 |
|------|------|--------|
| `VITE_API_BASE` | 后端 API 地址 | `http://localhost:8000` |
| `VITE_WS_BASE` | WebSocket 地址 | `ws://localhost:8000` |

---

## 注意事项

- **后端重构期间前端零改动**: 这是硬性约束，SSE 事件格式已冻结
- **文件上传**: 通过 `multipart/form-data` 发送到 `/files/upload`
- **文件预览**: 支持 PDF、图片、文本、Markdown 等格式
- **移动端适配**: 聊天界面需支持响应式布局
- **深色模式**: 通过 Tailwind `dark:` 变体实现

---

## 与后端的接口契约

前端与后端通过 REST API + SSE 通信，当前重构**不修改任何接口**：

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 创建会话 | POST | `/sessions` | |
| 获取会话 | GET | `/sessions/{id}` | |
| 聊天流 | SSE | `/sessions/{id}/stream` | 核心接口，格式冻结 |
| 上传文件 | POST | `/files/upload` | |
| 列出文件 | GET | `/files` | |
| 下载文件 | GET | `/files/download?path=` | |
| 获取设置 | GET | `/task-settings` | |
| 更新设置 | PUT | `/task-settings` | |

---

## 构建产物

- 生产构建输出到 `frontend/dist/`
- 静态文件由 Nginx 服务（Docker 中）
- API 请求通过 Nginx 反向代理到后端

---

## 状态管理

（推测使用 Pinia，需确认）

可能的 Store：
- `useSessionStore` — 当前会话状态
- `useChatStore` — 聊天消息、SSE 连接
- `useFileStore` — 文件列表、上传进度
- `useUserStore` — 用户信息、认证状态
