# ScienceClaw 后端知识库

> **范围**: `ScienceClaw/backend/`
> **技术栈**: FastAPI + Python 3.11 + MongoDB

---

## 目录结构

```
backend/
├── main.py                 # FastAPI 应用入口
├── config.py               # 全局配置（Pydantic Settings）
├── models.py               # Pydantic 数据模型
├── task_settings.py        # 任务配置模型
├── seekr_sdk.py            # Seekr SDK 集成
├── notifications.py        # 通知服务
├── deepagent/              # Agent 核心引擎（见子目录 AGENTS.md）
├── builtin_skills/         # 内置技能
│   ├── pdf/                # PDF 生成
│   ├── docx/               # Word 生成
│   ├── pptx/               # PPT 生成
│   ├── xlsx/               # Excel 生成
│   ├── deep-research/      # 深度研究流程
│   ├── skill-creator/      # 技能创建助手
│   ├── tool-creator/       # 工具创建助手
│   └── tooluniverse/       # 科学工具调用
├── route/                  # REST API 路由
│   ├── sessions.py         # 会话管理（最大文件：1984 行）
│   ├── chat.py             # 聊天接口
│   ├── auth.py             # 认证
│   ├── file.py             # 文件管理
│   └── ...
├── im/                     # IM 即时通讯集成
│   ├── orchestrator.py     # IM 消息编排（792 行）
│   ├── adapters/lark.py    # 飞书适配器
│   ├── wechat_bridge.py    # 微信桥接
│   └── session_manager.py  # IM 会话管理
├── mongodb/                # 数据库层
│   └── db.py               # MongoDB 连接
├── user/                   # 用户系统
│   ├── bootstrap.py        # 初始用户创建
│   └── dependencies.py     # 认证依赖
└── scripts/                # 工具脚本
    └── translate_tools.py  # 工具翻译
```

---

## 架构模式

### 请求流

```
Frontend (Vue)
    ↓ HTTP/WebSocket
FastAPI Router (route/)
    ↓
Session Manager (sessions.py)
    ↓
Agent Engine (deepagent/)
    ↓ SSE 流
Frontend 渲染
```

### 服务间通信

| 通信方式 | 场景 |
|---------|------|
| HTTP 内部调用 | Backend ↔ Sandbox, Backend ↔ WebSearch |
| MongoDB | 持久化会话、用户、任务数据 |
| SSE (Server-Sent Events) | Agent 流式输出到前端 |
| WebSocket | IM 长连接（飞书） |

---

## 约定

- **路由命名**: 使用名词复数，如 `/sessions`, `/files`
- **依赖注入**: 使用 FastAPI 的 `Depends()` 进行认证和数据库注入
- **异常处理**: 统一使用 HTTPException，状态码遵循 REST 语义
- **日志**: 使用 `loguru`，禁止 `print()`
- **异步优先**: 所有 IO 操作必须是 `async`，禁止同步阻塞调用
- **模型配置**: 环境变量通过 `config.py` 统一管理，`.env` 文件不提交 git

---

## 反模式

| 禁止行为 | 正确做法 |
|---------|---------|
| 在路由中直接操作 MongoDB | 通过 `mongodb/db.py` 封装层 |
| 在 `main.py` 中注册路由时硬编码路径 | 使用 `APIRouter` 前缀 |
| 同步调用外部 HTTP API | 使用 `httpx.AsyncClient` |
| 在全局作用域创建数据库连接 | 使用 FastAPI lifespan 事件管理 |

---

## 关键文件

| 文件 | 职责 | 注意 |
|------|------|------|
| `main.py` | FastAPI 应用创建、中间件、路由注册 | 新增路由必须在此注册 |
| `config.py` | 环境变量配置、Pydantic Settings | 新增配置项必须加默认值 |
| `route/sessions.py` | 会话 CRUD + SSE 流 endpoint | 1984 行，最复杂的路由 |
| `route/chat.py` | 聊天消息处理 | 调用 runner.py 的流式执行 |
| `im/orchestrator.py` | IM 消息路由 | 792 行，处理飞书/微信消息 |
| `models.py` | Pydantic 模型定义 | 前后端共享的数据结构 |
| `seekr_sdk.py` | Seekr SDK 封装 | ⚠️ 在 backend/sandbox/websearch 三处重复 |

---

## 已知代码重复

| 重复代码 | 位置 | 建议 |
|---------|------|------|
| `seekr_sdk.py` | `backend/`, `sandbox/`, `websearch/` | 提取为共享包 |
| `office/validators/` | `builtin_skills/{docx,pptx,xlsx}/scripts/office/` | 提取为 `builtin_skills/lib/office/` |
| `office/helpers/` | `builtin_skills/{docx,pptx,xlsx}/scripts/office/` | 同上 |

---

## 数据库

- **数据库**: MongoDB
- **ORM/驱动**: Motor (async MongoDB driver)
- **关键集合**: `sessions`, `users`, `tasks`, `evaluations`, `im_bindings`
- **连接**: `mongodb/db.py` 中创建，通过依赖注入使用

---

## 测试

```bash
# 后端测试（容器内）
pytest backend/ -v

# 覆盖率
pytest backend/ --cov=backend --cov-report=html
```

---

## 环境变量

| 变量 | 用途 | 默认值 |
|------|------|--------|
| `MONGODB_URL` | MongoDB 连接字符串 | `mongodb://localhost:27017` |
| `JWT_SECRET` | JWT 签名密钥 | 必须配置 |
| `OPENAI_API_KEY` | OpenAI API | 可选 |
| `ANTHROPIC_API_KEY` | Claude API | 目标引擎必需 |
| `AGENT_IMPL` | 引擎选择 (deep/claude) | `deep` |
| `WORKSPACE_DIR` | 用户工作目录 | `/home/scienceclaw` |

---

## IM 集成

支持飞书（Lark）和微信两种 IM 渠道：
- **飞书**: 通过 `adapters/lark.py` + `lark_long_connection.py` 长连接
- **微信**: 通过 `wechat_bridge.py` 桥接
- **消息编排**: `orchestrator.py` 负责消息路由和命令解析

---

## 技能系统

内置 8 个技能，每个技能是独立目录：
- 技能入口：`SKILL.md` 文件
- 技能脚本：`scripts/` 子目录
- 技能通过 `builtin_skills/` 目录加载
- 用户自定义技能放在项目根目录 `Skills/`

---

## 注意事项

- `route/sessions.py` 是最大路由文件（1984 行），包含会话管理和 SSE 流处理
- `im/orchestrator.py` 是 IM 核心，修改需谨慎
- 所有文件操作必须通过 `deepagent/` 的 Backend 协议，不能直接 `open()`
- 新增 API 路由需要在 `main.py` 注册，并更新前端 API 调用
