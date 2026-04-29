# RV-Insights 分阶段开发任务清单 & 进度跟踪

> **版本**: v2.0  
> **日期**: 2026-04-29  
> **关联设计**: `tasks/design.md` + `tasks/ds/refactoring-plan.md` + `tasks/ds/conventions.md`  
> **状态图例**: `[ ]` 待开始 | `[~]` 进行中 | `[x]` 已完成 | `[!]` 阻塞 | `[-]` 已取消  
> **工作量**: S=Small(<2h) M=Medium(2h-1d) L=Large(1-3d) XL=ExtraLarge(3d+)

---

## 开发环境快速启动

```bash
# 1. 前置条件
docker --version       # ≥ 24.x
python --version       # = 3.12
node --version         # = 20.x

# 2. 克隆 + 安装
git clone git@github.com:zcxGGmu/rv-claw.git && cd rv-claw
cp .env.example .env  # 填写 CLAUDE_API_KEY / OPENAI_API_KEY

# 3. 启动全部服务（首次启动 5-10 分钟）
docker compose up -d --build
docker compose ps  # 确认 11 个服务全部 healthy

# 4. 验证
curl http://localhost:8000/health        # → {"status":"ok"}
curl http://localhost:5173               # → Vue SPA

# 5. 运行测试
docker compose exec backend pytest tests/ -v
```

---

## 全局进度概览

| Sprint | 名称 | 周数 | 任务 | 完成 | 进度 | 状态 | 开始 | 完成 |
|--------|------|------|------|------|------|------|------|------|
| S0 | 基础架构搭建 | 1 | 32 | 0 | 0% | ⬜ | — | — |
| S1 | 认证 + 用户系统 | 1 | 18 | 0 | 0% | ⬜ | — | — |
| S2 | Chat 模式 | 2 | 28 | 0 | 0% | ⬜ | — | — |
| S3 | Pipeline 引擎核心 | 2.5 | 36 | 0 | 0% | ⬜ | — | — |
| S4 | Agent 节点实现 | 2 | 32 | 0 | 0% | ⬜ | — | — |
| S5 | 前端 RV-Insights 页面 | 2 | 34 | 0 | 0% | ⬜ | — | — |
| S6 | 定时任务 + IM + 安全 | 1 | 18 | 0 | 0% | ⬜ | — | — |
| S7 | 测试 + 文档 + 部署 | 1 | 22 | 0 | 0% | ⬜ | — | — |
| **总计** | | **12.5** | **220** | **0** | **0%** | | | |

### Sprint 依赖关系

```
S0 ──┬── S1 ──┬── S2 ────────────────┬── S6
     │        │                      │
     │        └── S3 ── S4 ── S5 ────┘
     │                                 │
     └──────────────────────────────── S7
```

- S1 依赖 S0（需要数据库 + FastAPI 骨架）
- S2 依赖 S1（需要认证）
- S3 依赖 S1（需要认证），**可与 S2 并行**
- S4 依赖 S3（需要 StateGraph + Adapter 骨架）
- S5 依赖 S4（需要后端 API 就绪）
- S6 依赖 S2 + S5（需要 Chat API + 前端页面）
- S7 依赖所有 Sprint（最终验证）

---

## Sprint 0：基础架构搭建（1 周）

> **目标**: 项目骨架就位，Docker Compose 所有服务 healthy，前后端可启动  
> **前置条件**: 无（这是起点）  
> **验收**: `docker compose up -d` 全部 11 个服务 running → `curl /health` → `{"status":"ok"}`

### 0.1 项目骨架初始化
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 0.1.1 | 创建 `backend/` 目录结构（含所有 `__init__.py`） | `backend/**/__init__.py` ×30+ | M | `find backend -name "__init__.py" \| wc -l` ≥ 20 | [ ] | 对照 refactoring-plan §4.3 |
| 0.1.2 | 复制 `ScienceClaw/frontend/` → `web-console/` | `web-console/` | M | `ls web-console/src/main.ts` 存在 | [ ] | 直接 `cp -r` + git mv |
| 0.1.3 | 创建 `nginx/` 目录 + `nginx.conf` 骨架 | `nginx/nginx.conf` | S | 文件存在 | [ ] | 参考 refactoring-plan 附录 J |
| 0.1.4 | 创建 `tests/` 目录结构 | `tests/{unit,integration,e2e,eval}/` | S | `tree tests/` 含 4 个子目录 | [ ] | 含 conftest.py 骨架 |
| 0.1.5 | 初始化 `requirements.txt` | `requirements.txt` | M | `pip install -r requirements.txt --dry-run` 无错误 | [ ] | 含 langgraph, claude-agent-sdk, openai-agents-sdk, fastapi 等 |
| 0.1.6 | 初始化 `requirements-test.txt` | `requirements-test.txt` | S | 同上 | [ ] | pytest, pytest-asyncio, httpx, testcontainers |

### 0.2 FastAPI 入口 + 配置
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 0.2.1 | 实现 `config.py`（Pydantic Settings） | `backend/config.py` | L | `python -c "from backend.config import get_settings; print(get_settings().mongo_uri)"` | [ ] | 所有环境变量 + 默认值 |
| 0.2.2 | 实现 `create_app()` 工厂函数 | `backend/main.py` | L | `uvicorn backend.main:create_app --factory --port 8000` 启动成功 | [ ] | — |
| 0.2.3 | lifespan：启动 MongoDB/PostgreSQL/Redis 连接 | `backend/main.py` | L | 启动日志含 "mongodb connected" / "postgres connected" | [ ] | 连接失败 → 503 而非崩溃 |
| 0.2.4 | lifespan：bootstrap admin 创建 | `backend/main.py` | M | 首次启动后 MongoDB `users` 集合含 admin 文档 | [ ] | 密码用 bcrypt hash |
| 0.2.5 | lifespan：恢复未完成 Pipeline | `backend/main.py` | M | 启动日志含 "recovering N pending pipelines" | [ ] | Sprint 3 前可留空（pass） |
| 0.2.6 | shutdown：优雅关闭 | `backend/main.py` | M | `docker compose stop backend` 日志无报错 | [ ] | 确保 MongoDB/Redis 连接关闭 |
| 0.2.7 | `/health` 端点 | `backend/main.py` | S | `curl /health` → 200 `{"status":"ok"}` | [ ] | Docker healthcheck 使用 |
| 0.2.8 | `/ready` 端点 | `backend/main.py` | M | `curl /ready` → 200（全绿）或 503（含 checks 详情） | [ ] | 检查 MongoDB+PG+Redis+Sandbox |
| 0.2.9 | CORS 中间件 | `backend/main.py` | S | `curl -H "Origin: http://localhost:5173" /health` → 含 CORS 头 | [ ] | 开发环境允许 localhost |
| 0.2.10 | 安全响应头中间件 | `backend/main.py` | S | `curl -I /health` → 含 X-Content-Type-Options 等 | [ ] | — |

### 0.3 Docker Compose 编排
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 0.3.1 | 编写 `docker-compose.yml`（11 服务） | `docker-compose.yml` | L | `docker compose config` 无语法错误 | [ ] | 基于原 ScienceClaw 版本修改 |
| 0.3.2 | 配置 `postgres` 服务 | `docker-compose.yml` | S | `docker compose up -d postgres` → healthy | [ ] | image: postgres:16-alpine |
| 0.3.3 | 配置 `backend` 服务 | `docker-compose.yml` | M | 环境变量注入正确；`depends_on` 等待 healthy | [ ] | — |
| 0.3.4 | 编写 `backend/Dockerfile` | `backend/Dockerfile` | M | `docker build -t rv-backend ./backend` 成功 | [ ] | python:3.12-slim + 非 root |
| 0.3.5 | 编写 `nginx/Dockerfile` | `nginx/Dockerfile` | S | 生产用，暂不验证 | [ ] | 基于 nginx:alpine 复制 dist |
| 0.3.6 | 编写 `.env.example` | `.env.example` | M | 含所有必需变量（对照 config.py） | [ ] | CLAUDE_API_KEY 等敏感项留空 |
| 0.3.7 | 验证全部服务 healthy | — | M | `docker compose ps` 全部 "healthy" | [ ] | **关键验收节点** |
| 0.3.8 | 编写 `docker-compose.override.yml` | `docker-compose.override.yml` | S | `docker compose up -d` 后 backend 代码变更自动 reload | [ ] | volume 挂载 + uvicorn --reload |

### 0.4 数据库连接层
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 0.4.1 | Motor 异步客户端初始化 | `backend/db/mongo.py` | M | `await db.command("ping")` 返回成功 | [ ] | — |
| 0.4.2 | `get_db()` 依赖注入 | `backend/db/mongo.py` | S | FastAPI 路由中 `Depends(get_db)` 可获取 db | [ ] | — |
| 0.4.3 | 保留 ScienceClaw 集合 schema | `backend/db/collections.py` | L | `await db.list_collection_names()` 含 sessions/users/models 等 | [ ] | ⚠️ 14 个集合，勿遗漏 |
| 0.4.4 | 新增 RV-Insights 集合 | `backend/db/collections.py` | M | 含 contribution_cases/human_reviews/stage_outputs/audit_log | [ ] | 对照 refactoring-plan §6.1 |
| 0.4.5 | `AsyncPostgresSaver` 连接池 | `backend/db/postgres.py` | M | `await checkpointer.setup()` 创建 checkpoints 表 | [ ] | — |
| 0.4.6 | `setup()` 创建 checkpoints 表 | `backend/db/postgres.py` | S | `\dt` 含 checkpoints/checkpoint_blobs/checkpoint_writes | [ ] | LangGraph 自动管理 |
| 0.4.7 | MongoDB 索引创建脚本 | `backend/db/collections.py` | M | `db.contribution_cases.list_indexes()` 含 status+created_at 复合索引 | [ ] | 幂等（create_index 重复调用不报错） |
| 0.4.8 | 数据库迁移框架 | `backend/db/migrations.py` | L | `await run_migrations(db)` 幂等执行所有未应用迁移 | [ ] | 版本号单调递增 |

---

## Sprint 1：认证 + 用户系统（1 周）

> **目标**: JWT 认证完整可用，RBAC 生效  
> **前置条件**: S0 完成（数据库连接可用 + FastAPI 可启动）  
> **验收**: `scripts/test_auth.sh` 全部 6 个场景通过 → login/register/status/refresh/logout/403-forbidden

### 1.1 JWT Token 层
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 1.1.1 | JWT access_token 生成（HS256，24h TTL） | `backend/user/auth.py` | M | `python -c "from backend.user.auth import create_access_token; print(create_access_token({'sub':'test'}))"` 输出合法 JWT | [ ] | 用 `jwt.encode()` + settings.JWT_SECRET |
| 1.1.2 | JWT refresh_token 生成（7d TTL） | `backend/user/auth.py` | S | 同上，验证 `exp` claim 在 7 天后 | [ ] | 循环使用（refresh 后旧 token 失效） |
| 1.1.3 | JWT 验证 + 过期检测 | `backend/user/auth.py` | M | 正常 token → 返回 payload；过期 token → `ExpiredSignatureError` | [ ] | 伪造 token → `InvalidTokenError` |
| 1.1.4 | Token 刷新逻辑 | `backend/user/auth.py` | M | POST /auth/refresh → 新 access_token；旧 refresh_token 失效 | [ ] | 存储在 refresh_tokens 集合中 |

### 1.2 用户模型 + 存储
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 1.2.1 | User Pydantic 模型 | `backend/user/models.py` | M | `User.model_validate({...})` 合法/非法输入 | [ ] | id, username, email, role, is_active |
| 1.2.2 | bcrypt 密码哈希 + 验证 | `backend/user/models.py` | S | `hash_password("test") != "test"` 且 `verify_password("test", hash) == True` | [ ] | 用 `bcrypt` 库 |
| 1.2.3 | users 集合 schema | `backend/db/collections.py` | S | role 字段默认 "user"；username unique index | [ ] | 在 S0 基础上扩展 |
| 1.2.4 | refresh_tokens 集合 schema | `backend/db/collections.py` | S | token + user_id + expires_at + TTL index | [ ] | — |

### 1.3 认证 API
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 1.3.1 | `POST /auth/login` | `backend/route/auth.py` | L | `curl -X POST /api/v1/auth/login -d '{"username":"admin","password":"admin123"}'` → 200 + TokenResponse | [ ] | — |
| 1.3.2 | `POST /auth/register` | `backend/route/auth.py` | M | 注册 → 自动登录 → 返回 TokenResponse | [ ] | 用户名/邮箱唯一性检查 |
| 1.3.3 | `GET /auth/status` | `backend/route/auth.py` | S | 有 token → `{"authenticated":true,"user":{...}}`；无 token → `{"authenticated":false}` | [ ] | — |
| 1.3.4 | `POST /auth/refresh` | `backend/route/auth.py` | M | refresh_token → 新 access_token；过期 refresh_token → 401 | [ ] | — |
| 1.3.5 | `POST /auth/logout` | `backend/route/auth.py` | S | 清除 refresh_token → 后续 refresh 失败 | [ ] | — |
| 1.3.6 | `POST /auth/change-password` | `backend/route/auth.py` | M | 旧密码正确 → 更新 bcrypt hash；旧密码错误 → 400 | [ ] | — |

### 1.4 依赖注入 + RBAC
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 1.4.1 | `get_current_user()` | `backend/user/dependencies.py` | L | 有效 token → 注入 User；无效 token → 401 | [ ] | Bearer token 从 Authorization 头解析 |
| 1.4.2 | `require_role(*roles)` | `backend/user/dependencies.py` | M | admin 角色访问 admin 路由 → 200；user 角色 → 403 | [ ] | — |
| 1.4.3 | 401/403 统一错误响应 | `backend/user/dependencies.py` | S | 401: `{"detail":"Not authenticated"}`；403: `{"detail":"Insufficient permissions"}` | [ ] | — |

### 1.5 Bootstrap Admin
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 1.5.1 | admin 自动创建逻辑 | `backend/main.py` | M | 首次启动 → `users` 集合含 `{"username":"admin","role":"admin"}` | [ ] | 幂等（重复启动不重复创建） |
| 1.5.2 | `BOOTSTRAP_UPDATE_ADMIN_PASSWORD` | `backend/main.py` | S | 设为 true → 每次启动更新 admin 密码 | [ ] | 生产环境启用 |

---

## Sprint 2：Chat 模式（2 周）

> **目标**: Chat 模式完整可用，前端对话正常  
> **前置条件**: S1 完成（认证可用）  
> **并行组**: 
>   - 组 A (可并行): 2.1 ChatRunner + 2.2 会话管理  
>   - 组 B (依赖 A): 2.3 Chat API + 2.4 文件/模型/统计 API  
>   - 组 C (依赖 B): 2.5 前后端联调  
> **验收**: 前端 Chat 欢迎页 → 输入消息 → SEE 流式返回 → Markdown 渲染 → 工具调用可见

### 2.1 ChatRunner 引擎 [组 A]
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 2.1.1 | ChatRunner 类骨架 | `backend/chat/runner.py` | L | `runner = ChatRunner("sid","uid")` 不报错 | [ ] | session_id + asyncio.Queue + stop_event |
| 2.1.2 | `run()` 调用 DeepAgents → 推送事件 | `backend/chat/runner.py` | XL | Mock 消息进入 → queue 收到 thinking/message 事件 | [ ] | 复用 ScienceClaw deepagent 模块 |
| 2.1.3 | `stop()` 优雅停止 | `backend/chat/runner.py` | M | `runner.stop()` → task cancelled → queue 收到 "stopped" 事件 | [ ] | — |
| 2.1.4 | `event_stream()` SSE 生成器 | `backend/chat/runner.py` | M | 30s 无事件 → heartbeat；runner 结束 → 流关闭 | [ ] | — |
| 2.1.5 | 全局并发槽位 | `backend/chat/runner.py` | M | 11 个并发请求 → 第 11 个排队 → 超时 429 | [ ] | Semaphore(10) |
| 2.1.6 | 孤实例清理 | `backend/chat/runner.py` | S | 1h 无活动 runner → `cleanup_orphaned()` 回收 | [ ] | — |

### 2.2 会话管理 [组 A]
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 2.2.1 | 会话创建 | `backend/chat/sessions.py` | M | `PUT /sessions` → 201 + `{session_id, mode}` | [ ] | 生成 session_id + workspace 路径 |
| 2.2.2 | 会话列表查询 | `backend/chat/sessions.py` | M | `GET /sessions` → 按 updated_at 倒序 + 分页 | [ ] | — |
| 2.2.3 | 会话详情 | `backend/chat/sessions.py` | S | `GET /sessions/{id}` → 含 events、plan、status | [ ] | — |
| 2.2.4 | 会话删除（级联） | `backend/chat/sessions.py` | M | `DELETE /sessions/{id}` → 删除 MongoDB 文档 + workspace 目录 | [ ] | — |
| 2.2.5 | 分享/取消分享 | `backend/chat/sessions.py` | S | POST share → `is_shared=true`；DELETE share → `false` | [ ] | 分享页无需登录 |
| 2.2.6 | 标题更新/置顶 | `backend/chat/sessions.py` | S | PATCH title/pinned → 生效 | [ ] | — |

### 2.3 Chat API 端点 [组 B — 依赖 2.1+2.2]
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 2.3.1 | `PUT /api/v1/sessions` | `backend/route/sessions.py` | M | curl PUT → 201 | [ ] | — |
| 2.3.2 | `GET /api/v1/sessions` | `backend/route/sessions.py` | M | 分页 + 搜索正常 | [ ] | — |
| 2.3.3 | `GET /api/v1/sessions/{id}` | `backend/route/sessions.py` | S | 返回详情 | [ ] | — |
| 2.3.4 | `DELETE /api/v1/sessions/{id}` | `backend/route/sessions.py` | S | 删除成功 → 404 | [ ] | — |
| 2.3.5 | `POST /api/v1/sessions/{id}/chat` (SSE) | `backend/route/sessions.py` | L | `curl -N POST /sessions/{id}/chat -d '{"message":"hi"}'` → SSE 流 | [ ] | 对接 ChatRunner.event_stream() |
| 2.3.6 | `POST /api/v1/sessions/{id}/stop` | `backend/route/sessions.py` | S | 停止 → SSE 流收到 "stopped" 事件 | [ ] | — |
| 2.3.7 | share 端点 | `backend/route/sessions.py` | S | — | [ ] | — |

### 2.4 文件 + 模型 + 统计 API [组 B — 可与 2.3 并行]
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 2.4.1 | 文件上传 API | `backend/route/file.py` | M | 上传成功 → workspace 出现文件 | [ ] | 大小限制 100MB + 扩展名白名单 |
| 2.4.2 | 文件下载 API | `backend/route/file.py` | M | 路径遍历 `../../etc/passwd` → 403 | [ ] | allowed_prefixes 检查 |
| 2.4.3 | 文件列表 API | `backend/route/file.py` | S | 返回目录树 JSON | [ ] | — |
| 2.4.4 | 模型 CRUD API | `backend/route/models.py` | L | 系统模型不可删除；用户模型 CRUD 正常 | [ ] | 含 context_window 检测 |
| 2.4.5 | 统计汇总 API | `backend/route/statistics.py` | M | `?time_range=7days` 返回正确汇总 | [ ] | — |

### 2.5 前后端联调 [组 C — 依赖 2.3+2.4]
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 2.5.1 | HomePage — 输入消息 → 后端 → SSE → Markdown | — | L | 浏览器操作：输入 "Hello" → 看到回复 | [ ] | **关键验收节点** |
| 2.5.2 | ChatPage — 会话列表 + 消息 + 工具调用 + 文件 | — | L | 全部功能可用 | [ ] | — |
| 2.5.3 | ChatPage — 停止/分享/文件上传/深度研究 | — | M | 按钮功能正常 | [ ] | — |

---

## Sprint 3：Pipeline 引擎核心（2.5 周）

> **目标**: LangGraph StateGraph 完整定义，Human-in-the-Loop 审批门可用，Mock Agent 跑通全流程  
> **前置条件**: S1 完成（认证），**不依赖 S2**（可与 Chat 并行开发）  
> **并行组**:
>   - 组 A: 3.1 PipelineState + 3.2 StateGraph（核心，先做）
>   - 组 B: 3.3 路由函数 + 3.4 SDK Adapter（依赖 3.1 的模型定义，可与 3.2 并行）
>   - 组 C: 3.5 Mock Agent + 3.6 CRUD API（依赖 3.2 的图编译）
>   - 组 D: 3.7 审核 SSE + 3.8 事件系统（依赖 3.5+3.6）
> **验收**: `pytest tests/integration/test_pipeline_flow.py -v` → 全部通过（Mock Agent 完成 Created→Completed 全流程）

### 3.1 Pipeline 状态机 [组 A]
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 3.1.1 | PipelineState Pydantic 模型 | `backend/pipeline/state.py` | L | `PipelineState.model_validate({...})` 合法/非法 | [ ] | 对照 refactoring-plan §E.1 |
| 3.1.2 | StageStatus 枚举 + stage_statuses | `backend/pipeline/state.py` | S | 枚举值正确 | [ ] | — |
| 3.1.3 | 成本追踪字段 | `backend/pipeline/state.py` | S | total_input_tokens 等字段存在 | [ ] | — |
| 3.1.4 | 审核历史字段 | `backend/pipeline/state.py` | M | approval_history, review_history, review_score_history | [ ] | — |
| 3.1.5 | 单测: 模型验证 | `tests/unit/test_pipeline_state.py` | M | `pytest tests/unit/test_pipeline_state.py -v` 全绿 | [ ] | 至少 5 个 test case |
| 3.1.6 | 单测: JSON ↔ Pydantic 序列化 | `tests/unit/test_pipeline_state.py` | S | round-trip 前后一致 | [ ] | — |

### 3.2 StateGraph 图定义 [组 A]
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 3.2.1 | `build_pipeline_graph()` 节点注册 | `backend/pipeline/graph.py` | L | builder.add_node 调用 10 次 | [ ] | 10 节点：5 agent + 4 gate + 1 escalate |
| 3.2.2 | 线性边 | `backend/pipeline/graph.py` | M | explore→gate1→plan→gate2→develop→review | [ ] | — |
| 3.2.3 | 条件边 | `backend/pipeline/graph.py` | L | 4 个 gate + 1 个 review 的条件路由 | [ ] | 对照 refactoring-plan §5.2 |
| 3.2.4 | `compile_graph()` 注入 checkpointer + interrupt | `backend/pipeline/graph.py` | M | graph 编译成功 + checkpointer 关联 | [ ] | interrupt_before 含 4 个 gate |
| 3.2.5 | 验证: 图可渲染 | — | S | `graph.get_graph().draw_mermaid()` 输出合法 Mermaid | [ ] | 可选：保存为 .png |

### 3.3 条件边路由 [组 B — 可与 3.2 并行]
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 3.3.1 | `route_human_decision()` | `backend/pipeline/routes.py` | M | approve→前进, reject→回退, abandon→END | [ ] | — |
| 3.3.2 | `route_review_decision()` | `backend/pipeline/routes.py` | L | approve→gate3, reject→develop, escalate→escalate_node | [ ] | — |
| 3.3.3 | `compute_review_score()` 加权评分 | `backend/pipeline/routes.py` | M | critical=10, major=5, minor=1, suggestion=0 | [ ] | — |
| 3.3.4 | 收敛检测 | `backend/pipeline/routes.py` | M | ≥50% 重复 finding → escalate | [ ] | 基于 finding ID (file+line) 去重 |
| 3.3.5 | 单测: 6 个 case | `tests/unit/test_route_review.py` | L | `pytest tests/unit/test_route_review.py -v` → 6 passed | [ ] | approve/reject/under_max/escalate_max/escalate_convergence/escalate_repeated |

### 3.4 SDK 适配器层 [组 B — 可与 3.2 并行]
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 3.4.1 | `AgentAdapter` 抽象基类 + `AgentEvent` | `backend/adapters/base.py` | M | ABC 定义正确，AgentEvent 序列化正常 | [ ] | 对照 refactoring-plan §E.4 |
| 3.4.2 | ClaudeAgentAdapter 骨架 | `backend/adapters/claude_adapter.py` | L | `await adapter.execute("test")` 可调用 | [ ] | 子进程管理 |
| 3.4.3 | `execute()` 流式返回 | `backend/adapters/claude_adapter.py` | L | async for event in adapter.execute(...): ... | [ ] | — |
| 3.4.4 | `cancel()` 终止子进程 | `backend/adapters/claude_adapter.py` | M | cancel → task cancelled → 子进程 killed | [ ] | — |
| 3.4.5 | `_convert_message()` 统一格式 | `backend/adapters/claude_adapter.py` | M | Claude msg → AgentEvent 转换正确 | [ ] | — |
| 3.4.6 | OpenAIAgentAdapter | `backend/adapters/openai_adapter.py` | L | Runner.run 封装 + 结构化输出 | [ ] | — |
| 3.4.7 | Guardrail 集成 | `backend/adapters/openai_adapter.py` | M | InputGuardrail 拦截非法输入 | [ ] | — |
| 3.4.8 | 单测: Mock Adapter | `tests/unit/test_adapter.py` | M | `pytest tests/unit/test_adapter.py -v` 全绿 | [ ] | 流式输出 + cancel 中断 |

### 3.5 Agent 节点骨架（Mock 实现）[组 C — 依赖 3.2]
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 3.5.1 | Mock Explorer | `backend/pipeline/nodes/explore.py` | M | 返回固定 ExplorationResult（含 evidence） | [ ] | 后续 Sprint 4 替换为真实 |
| 3.5.2 | Mock Planner | `backend/pipeline/nodes/plan.py` | M | 返回固定 ExecutionPlan（含 3 steps + 2 tests） | [ ] | — |
| 3.5.3 | Mock Developer | `backend/pipeline/nodes/develop.py` | M | 生成固定 .patch 文件到 ArtifactManager | [ ] | — |
| 3.5.4 | Mock Reviewer | `backend/pipeline/nodes/review.py` | M | 第1轮 reject (3 findings)，第2轮 approve | [ ] | 模拟 Develop↔Review 迭代 |
| 3.5.5 | Mock Tester | `backend/pipeline/nodes/test.py` | M | 返回固定 TestResult (3/3 passed) | [ ] | — |
| 3.5.6 | Human Gate 节点 | `backend/pipeline/nodes/human_gate.py` | L | `interrupt({...})` 暂停执行 → `Command(resume={...})` 恢复 | [ ] | **关键技术点** |
| 3.5.7 | Escalate 节点 | `backend/pipeline/nodes/escalate.py` | S | 记录原因 → 转入 human_gate | [ ] | — |

### 3.6 案例 CRUD API [组 C — 依赖 3.2]
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 3.6.1 | `POST /api/v1/cases` | `backend/route/cases.py` | M | curl POST → 201 + case_id | [ ] | — |
| 3.6.2 | `GET /api/v1/cases` (列表+筛选) | `backend/route/cases.py` | M | `?status=exploring&target_repo=linux` 正确筛选 | [ ] | — |
| 3.6.3 | `GET /api/v1/cases/{id}` (详情) | `backend/route/cases.py` | M | 返回全部阶段产物（如有） | [ ] | — |
| 3.6.4 | `DELETE /api/v1/cases/{id}` | `backend/route/cases.py` | S | admin → 200；user → 403 | [ ] | — |
| 3.6.5 | `POST /api/v1/cases/{id}/start` | `backend/route/cases.py` | L | 创建 asyncio.Task → 状态变为 exploring | [ ] | 对照 refactoring-plan §E.5 |

### 3.7 审核 + SSE 端点 [组 D — 依赖 3.5+3.6]
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 3.7.1 | `POST /api/v1/cases/{id}/review` | `backend/route/reviews.py` | L | approve → Pipeline 前进；reject → 回退 | [ ] | 对照 refactoring-plan §E.6 |
| 3.7.2 | `GET /api/v1/cases/{id}/history` | `backend/route/reviews.py` | S | 返回审核历史列表 | [ ] | — |
| 3.7.3 | `GET /api/v1/cases/{id}/events` (SSE) | `backend/route/cases.py` | L | curl SSE → 收到 stage_change + agent_output 事件 | [ ] | Redis Pub/Sub + Stream 双通道 |
| 3.7.4 | SSE 重连恢复 | `backend/route/cases.py` | M | 断连 → 重连（Last-Event-ID）→ 收到丢失事件 | [ ] | Stream 补偿 |
| 3.7.5 | SSE 心跳 | `backend/route/cases.py` | S | 每 30s 收到 heartbeat 事件 | [ ] | — |

### 3.8 事件系统 [组 D — 可与 3.7 并行]
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 3.8.1 | PipelineEvent Pydantic 模型 | `backend/events/models.py` | M | 序列化/反序列化正确 | [ ] | seq, case_id, event_type, data, timestamp |
| 3.8.2 | EventPublisher (Pub/Sub + Stream) | `backend/events/publisher.py` | L | `publish()` → Redis 收到消息 + Stream 写入 | [ ] | 对照 refactoring-plan §E.3 |
| 3.8.3 | 便捷方法 | `backend/events/publisher.py` | M | publish_stage_change / publish_agent_output 等 | [ ] | — |
| 3.8.4 | 单测: 事件发布 | `tests/unit/test_event_publisher.py` | M | `pytest tests/unit/test_event_publisher.py -v` 全绿 | [ ] | 序列号递增 + Pub/Sub + Stream + 去重 |

---

## Sprint 4：Agent 节点实现（2 周）

> **目标**: 5 个 Agent 节点全部对接真实 LLM SDK，Pipeline 可端到端运行  
> **前置条件**: S3 完成（StateGraph + Adapter + Mock Agent 全部就位）  
> **并行组**: 4.1-4.5 五个 Agent 可独立并行开发（共享 adapter + contracts），4.6-4.7 可随时穿插  
> **验收**: 真实 LLM 调用完成一个 ISA 扩展案例的全流程 → `status=completed` + `POST /cases/{id}/start` 到 `completed` 耗时 < 15 分钟（Mock 降级）

### 4.1 Explorer Agent [可并行]
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 4.1.1 | EXPLORER_SYSTEM_PROMPT | `backend/pipeline/prompts/explorer.py` | M | Prompt 含三路探索策略 + JSON 输出格式 | [ ] | 对照 design.md §5.12 |
| 4.1.2 | Claude SDK 执行逻辑 | `backend/pipeline/nodes/explore.py` | L | 真实 LLM 调用 → 返回 ExplorationResult | [ ] | 替换 S3 的 Mock 实现 |
| 4.1.3 | 输出解析（JSON → ExplorationResult） | `backend/pipeline/nodes/explore.py` | M | 正常 JSON 解析成功；畸形 JSON 触发重试修正 | [ ] | — |
| 4.1.4 | 幻觉验证 | `backend/pipeline/nodes/explore.py` | L | URL 不可达 → 移除 evidence；ISA 扩展名不在已知列表 → 降分 | [ ] | 对照 design.md §5.3.1 verify_exploration_claims |
| 4.1.5 | 事件发布集成 | `backend/pipeline/nodes/explore.py` | M | thinking / tool_call / tool_result → EventPublisher | [ ] | — |

### 4.2 Planner Agent [可并行]
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 4.2.1 | PLANNER_SYSTEM_PROMPT | `backend/pipeline/prompts/planner.py` | M | Prompt 含开发步骤+测试方案设计 | [ ] | — |
| 4.2.2 | OpenAI SDK 执行（Manager + Handoff） | `backend/pipeline/nodes/plan.py` | L | DevPlanner + TestPlanner handoff 正确执行 | [ ] | — |
| 4.2.3 | InputGuardrail | `backend/pipeline/nodes/plan.py` | M | 缺 feasibility_score → tripwire_triggered | [ ] | — |
| 4.2.4 | Handoff 编排 | `backend/pipeline/nodes/plan.py` | M | Manager → DevPlanner → TestPlanner → 汇总 | [ ] | — |
| 4.2.5 | 结构化输出 | `backend/pipeline/nodes/plan.py` | M | `output_type=ExecutionPlan` 自动生成 JSON Schema | [ ] | — |

### 4.3 Developer Agent [可并行]
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 4.3.1 | Claude SDK 执行（Write/Edit/Bash） | `backend/pipeline/nodes/develop.py` | L | 根据 ExecutionPlan 修改文件 → 生成 .patch | [ ] | — |
| 4.3.2 | `canUseTool` 回调 | `backend/pipeline/nodes/develop.py` | M | 破坏性操作（rm -rf）→ 拦截拒绝 | [ ] | — |
| 4.3.3 | 迭代修复模式 | `backend/pipeline/nodes/develop.py` | L | 输入 ReviewVerdict + findings → 仅修复指定问题 | [ ] | 不超过 review 标记的范围 |
| 4.3.4 | 产物保存 | `backend/pipeline/nodes/develop.py` | M | patch 文件 → ArtifactManager.save_artifact() | [ ] | — |

### 4.4 Reviewer Agent [可并行]
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 4.4.1 | REVIEWER_SYSTEM_PROMPT | `backend/pipeline/prompts/reviewer.py` | M | 3 维度审核 + 输出格式 | [ ] | 对照 design.md §5.12 |
| 4.4.2 | 确定性工具审核 | `backend/pipeline/nodes/review.py` | L | checkpatch.pl 输出 → findings 列表；sparse 同理 | [ ] | 工具不存在时 graceful skip |
| 4.4.3 | OpenAI SDK Handoff（3 视角） | `backend/pipeline/nodes/review.py` | L | security→correctness→style handoff 正确 | [ ] | — |
| 4.4.4 | 结果合并 | `backend/pipeline/nodes/review.py` | M | 工具发现 + LLM 发现 → 去重 → ReviewVerdict | [ ] | — |
| 4.4.5 | 严重度判定 | `backend/pipeline/nodes/review.py` | M | critical/major → 强制 approved=false | [ ] | — |

### 4.5 Tester Agent [可并行]
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 4.5.1 | Claude SDK 执行（Bash/Grep） | `backend/pipeline/nodes/test.py` | L | 在 sandbox 中执行编译 + 测试 | [ ] | — |
| 4.5.2 | QEMU 环境搭建 | `backend/pipeline/nodes/test.py` | L | QEMU 启动 → /proc/cpuinfo 可读 | [ ] | 需要 riscv64 交叉编译工具链 |
| 4.5.3 | MVP 降级：编译验证 | `backend/pipeline/nodes/test.py` | M | 交叉编译通过 → passed=true | [ ] | QEMU 不可用时自动降级 |
| 4.5.4 | 日志收集 + TestResult | `backend/pipeline/nodes/test.py` | M | 测试日志 → 文件 + TestResult JSON | [ ] | — |

### 4.6 数据契约 + 产物管理 [可随时穿插]
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 4.6.1 | ExplorationResult 等 | `backend/contracts/exploration.py` | M | Pydantic 验证正常 + JSON Schema 可导出 | [ ] | 在 S3 Mock 中已使用，此处完善 |
| 4.6.2 | ExecutionPlan 等 | `backend/contracts/planning.py` | M | 同上 | [ ] | — |
| 4.6.3 | DevelopmentResult | `backend/contracts/development.py` | S | 同上 | [ ] | — |
| 4.6.4 | ReviewVerdict + ReviewFinding | `backend/contracts/review.py` | M | 同上 | [ ] | — |
| 4.6.5 | TestResult | `backend/contracts/testing.py` | S | 同上 | [ ] | — |
| 4.6.6 | ArtifactManager | `backend/artifacts/manager.py` | L | save → load → cleanup 全流程正确 | [ ] | 对照 design.md §2.7 |

### 4.7 其他模块 [可随时穿插]
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 4.7.1 | PatchworkClient | `backend/datasources/patchwork.py` | M | `get_recent_patches("linux-riscv")` → JSON 列表 | [ ] | — |
| 4.7.2 | MailingListClient | `backend/datasources/mailing_list.py` | M | lore.kernel.org 搜索 → 结果 | [ ] | — |
| 4.7.3 | GitHubClient | `backend/datasources/github_client.py` | M | OpenSBI/riscv-tests 仓库访问 | [ ] | — |
| 4.7.4 | ResourceScheduler | `backend/scheduler.py` | M | 3 个 Semaphore 并发控制 | [ ] | — |
| 4.7.5 | CostCircuitBreaker | `backend/pipeline/cost_guard.py` | M | 超 $10 → 熔断 → escalate | [ ] | 对照 design.md §5.4 |

---

## Sprint 5：前端 RV-Insights 页面（2 周）

> **目标**: 案例管理 + Pipeline 可视化 + 审核面板全部可用  
> **前置条件**: S4 完成（后端 API 就绪）+ S0 的 web-console 可用  
> **并行组**: 5.1+5.2 页面骨架 + 5.3+5.4+5.5 组件（8 个组件可独立并行） + 5.6 状态管理 + 5.7 i18n  
> **验收**: 浏览器操作：创建案例 → 启动 Pipeline → SSE 实时更新 PipelineView → 审核面板操作 → 完成

### 5.1 案例列表页
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 5.1.1 | 页面布局 | `web-console/src/views/CaseListView.vue` | L | TopBar + FilterBar + Table + Pagination 正常渲染 | [ ] | — |
| 5.1.2 | 状态筛选标签栏 | 同上 | M | 点击标签 → 列表筛选正确 | [ ] | 9 种状态 + 颜色映射 |
| 5.1.3 | 搜索 + 仓库筛选 | 同上 | M | 输入关键词 → 实时筛选 | [ ] | — |
| 5.1.4 | 案例表格 | 同上 | M | 标题、状态徽章、仓库、进度、时间 | [ ] | 复用 ScienceClaw 的 SessionItem 模式 |
| 5.1.5 | 新建案例对话框 | 同上 | L | 填写表单 → POST /cases → 列表刷新 | [ ] | — |
| 5.1.6 | 分页 + 排序 | 同上 | M | 翻页 + 点击表头排序 | [ ] | — |

### 5.2 案例详情页
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 5.2.1 | 三栏布局框架 | `web-console/src/views/CaseDetailView.vue` | L | LeftSidebar 200px + Main flex:1 + RightPanel 320px | [ ] | 对照 refactoring-plan §D.2 |
| 5.2.2 | 响应式设计 | 同上 | M | xl=三栏 / md=两栏 / sm=单栏 | [ ] | — |
| 5.2.3 | TopBar 组件 | 同上 | M | 标题 + 状态徽章 + 成本 + 操作按钮 | [ ] | Start/Abandon/Delete 按钮按状态显示 |
| 5.2.4 | 动态组件切换 | 同上 | M | 点击左侧 Pipeline 阶段 → 主内容区切换对应 Tab | [ ] | — |

### 5.3 Pipeline 可视化 [可并行]
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 5.3.1 | PipelineView 进度条 | `.../pipeline/PipelineView.vue` | L | 5 阶段图标 + 连接线 + 状态颜色正确 | [ ] | — |
| 5.3.2 | StageNode 单节点 | `.../pipeline/StageNode.vue` | M | 图标 + 名称 + 状态圆点 + 耗时 + Token | [ ] | — |
| 5.3.3 | HumanGate 审批门 | `.../pipeline/HumanGate.vue` | M | 激活状态高亮 + 决策结果显示 | [ ] | — |
| 5.3.4 | IterationBadge | `.../pipeline/IterationBadge.vue` | S | "第 N/3 轮" 标记 | [ ] | — |
| 5.3.5 | 阶段点击切换 | PipelineView.vue | M | emit('select-stage', stage) → CaseDetailView 响应 | [ ] | — |

### 5.4 审核相关 [可并行]
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 5.4.1 | ReviewPanel 布局 | `.../review/ReviewPanel.vue` | L | 产物摘要 + Approve/Reject/Abandon 按钮 | [ ] | — |
| 5.4.2 | 决策按钮 + 评论 | 同上 | M | approve → 绿色；reject → 红色弹出评论框 | [ ] | 驳回时评论必填 |
| 5.4.3 | 评论必填验证 | 同上 | S | reject 无评论 → 按钮 disabled + 提示 | [ ] | — |
| 5.4.4 | 历史审核列表 | 同上 | M | 折叠列表 + 每次审核的时间/人/决策 | [ ] | — |
| 5.4.5 | ReviewFinding 卡片 | `.../review/ReviewFinding.vue` | M | 严重度颜色 + 分类图标 + 描述 + 建议 | [ ] | critical=红, major=橙, minor=黄, suggestion=蓝 |
| 5.4.6 | DiffViewer (Monaco) | `.../review/DiffViewer.vue` | XL | Monaco Editor 正确渲染 diff + Finding 行高亮 | [ ] | 依赖 `monaco-editor` 0.52+ |

### 5.5 探索/测试 [可并行]
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 5.5.1 | ContributionCard | `.../exploration/ContributionCard.vue` | M | 类型图标 + 可行性评分 + 证据数 Badge | [ ] | — |
| 5.5.2 | EvidenceChain | `.../exploration/EvidenceChain.vue` | M | 来源 + URL（可点击）+ 内容摘要 | [ ] | — |
| 5.5.3 | TestResultSummary | `.../testing/TestResultSummary.vue` | M | 通过/失败/总计 + 进度条 + 覆盖率 | [ ] | — |
| 5.5.4 | TestLogViewer | `.../testing/TestLogViewer.vue` | M | 虚拟滚动 + 搜索 + 行号 | [ ] | — |

### 5.6 状态管理层
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 5.6.1 | cases REST API 封装 | `web-console/src/api/cases.ts` | M | create/list/get/delete/start/review 全部可用 | [ ] | 复用 ScienceClaw 的 client.ts |
| 5.6.2 | SSE 事件订阅封装 | `web-console/src/api/cases.ts` | M | fetchEventSource 封装 + 重连恢复 | [ ] | — |
| 5.6.3 | useCaseEvents (SSE 管理) | `web-console/src/composables/useCaseEvents.ts` | L | 连接/重连/heartbeat/dedup 逻辑正确 | [ ] | 对照 refactoring-plan §D.2 |
| 5.6.4 | 事件分发 | 同上 | M | stage_change → 更新 status；review_request → 弹出审核面板 | [ ] | — |
| 5.6.5 | useCaseStore (状态) | `web-console/src/composables/useCaseStore.ts` | L | module-level ref 模式，符合 ScienceClaw 惯例 | [ ] | 非 Pinia |
| 5.6.6 | TypeScript 类型: case | `web-console/src/types/case.ts` | M | Case, CaseStatus, PipelineStage | [ ] | 与后端 Pydantic 模型对齐 |
| 5.6.7 | TypeScript 类型: pipeline | `web-console/src/types/pipeline.ts` | M | PipelineEvent 等 | [ ] | — |
| 5.6.8 | TypeScript 类型: event | `web-console/src/types/event.ts` | S | SSE 事件类型 | [ ] | — |

### 5.7 i18n + 路由
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 5.7.1 | 中文翻译扩展 | `web-console/src/locales/zh.ts` | M | pipeline/case/review 相关翻译 | [ ] | — |
| 5.7.2 | 英文翻译扩展 | `web-console/src/locales/en.ts` | M | 对应英文 | [ ] | — |
| 5.7.3 | /cases 路由注册 | `web-console/src/router/index.ts` | S | `/cases` → CaseListView；`/cases/:id` → CaseDetailView | [ ] | — |

---

## Sprint 6：定时任务 + IM + 安全（1 周）

> **目标**: 定时任务对接新后端、IM 集成保留、安全加固就位  
> **前置条件**: S2（Chat API）+ S5（前端页面）  
> **验收**: 前端任务配置页 → 自然语言输入 → crontab 预览 → 保存 → 定时触发 → 结果通知

### 6.1 Task-Service 迁移
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 6.1.1 | scheduler_api → 新 backend:8000 | `ScienceClaw/task-service/` | S | `POST /api/v1/chat` 收到 scheduler 的请求 | [ ] | 修改环境变量 CHAT_SERVICE_URL |
| 6.1.2 | celery_worker API Key 配置 | `ScienceClaw/task-service/` | S | 认证通过 | [ ] | — |
| 6.1.3 | `/chat` 端点验证 | — | M | scheduler 触发 → backend 执行 → 返回结果 | [ ] | 端到端验证 |
| 6.1.4 | `/task/parse-schedule` 验证 | — | M | "每天上午9点" → `0 9 * * *` | [ ] | — |

### 6.2 IM 集成保留
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 6.2.1 | 迁移 `im/` 模块 | `backend/im/` | L | `from backend.im import ...` 可用 | [ ] | orchestrator + lark adapter + settings + binding |
| 6.2.2 | 迁移 `route/im.py` | `backend/route/im.py` | M | 飞书绑定/解绑/设置 API 正常 | [ ] | — |
| 6.2.3 | 端到端验证 | — | L | 飞书消息 → 创建会话 → Agent 执行 → 结果推送 | [ ] | **关键验收节点** |

### 6.3 安全加固
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 6.3.1 | Prompt 注入检测 | `backend/security/prompt_guard.py` | M | "ignore all instructions" → 检测成功 | [ ] | 5 种注入模式 |
| 6.3.2 | 用户输入清理 | `backend/security/prompt_guard.py` | S | 角色标记 `system:` → 移除；>10000 字符 → 截断 | [ ] | — |
| 6.3.3 | 速率限制 | `backend/middleware/rate_limit.py` | M | 100 req/min → 429；下分钟恢复 | [ ] | slowapi + Redis |
| 6.3.4 | 安全响应头 | `backend/middleware/security_headers.py` | S | 所有响应含 X-Content-Type-Options 等 | [ ] | — |
| 6.3.5 | 审计日志 | `backend/db/audit.py` | M | case_created/pipeline_started/stage_completed/review_submitted → audit_log | [ ] | append-only |

### 6.4 前后端联调
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 6.4.1 | 任务列表页 | — | M | 显示定时任务 + 执行历史 | [ ] | — |
| 6.4.2 | 任务配置页 | — | M | 自然语言 → crontab 预览 → 保存 | [ ] | — |
| 6.4.3 | 设置页 IM 绑定 | — | M | 飞书绑定状态显示 | [ ] | — |

---

## Sprint 7：测试 + 文档 + 部署（1 周）

> **目标**: 全部测试通过，生产部署配置就绪  
> **前置条件**: 所有 Sprint 完成  
> **验收**: `pytest tests/ -v` 全绿 + coverage ≥80% + `docker compose up -d` 生产模式可用

### 7.1 后端单元测试
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 7.1.1 | PipelineState 测试（≥95% cov） | `tests/unit/test_pipeline_state.py` | M | `pytest ... --cov=pipeline.state --cov-report=term` ≥95% | [ ] | — |
| 7.1.2 | route_review 测试（≥95%） | `tests/unit/test_route_review.py` | M | 6 个 case 全部通过 | [ ] | — |
| 7.1.3 | human_gate 路由测试（≥95%） | `tests/unit/test_route_human_gate.py` | M | 3 个 case | [ ] | — |
| 7.1.4 | EventPublisher 测试（≥90%） | `tests/unit/test_event_publisher.py` | M | 序列号/Pub/Sub/Stream/heartbeat | [ ] | — |
| 7.1.5 | Data Contracts 测试（≥95%） | `tests/unit/test_data_contracts.py` | M | 5 个 Pydantic 模型验证 + 非法值拒绝 | [ ] | — |
| 7.1.6 | Adapter 测试（≥90%） | `tests/unit/test_adapter.py` | M | 流式输出 + cancel 中断 | [ ] | — |
| 7.1.7 | ResourceScheduler 测试（≥90%） | `tests/unit/test_scheduler.py` | M | 并发控制 + 信号量管理 | [ ] | — |

### 7.2 集成测试
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 7.2.1 | Pipeline 全流程集成测试 | `tests/integration/test_pipeline_flow.py` | L | Mock Agent 完成 Created→Completed（含 4 个审批门） | [ ] | — |
| 7.2.2 | 审核幂等性测试 | 同上 | M | 相同 review_id 不重复处理 | [ ] | — |
| 7.2.3 | SSE 事件流完整性测试 | 同上 | L | 收到 stage_change + agent_output + review_request + completed | [ ] | — |
| 7.2.4 | Review 迭代升级测试 | 同上 | M | 3 轮 review reject → escalate | [ ] | — |
| 7.2.5 | Chat 流程集成测试 | `tests/integration/test_chat_flow.py` | M | 创建会话 → SSE 对话 → 消息验证 | [ ] | — |
| 7.2.6 | Auth 流程集成测试 | `tests/integration/test_auth.py` | M | 登录/注册/刷新/登出 全流程 | [ ] | — |
| 7.2.7 | testcontainers fixtures | `tests/integration/conftest.py` | L | 自动启停 MongoDB + PostgreSQL + Redis 容器 | [ ] | — |

### 7.3 E2E 测试
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 7.3.1 | 创建案例 + 启动 | `tests/e2e/case-workflow.spec.ts` | M | Playwright 录制回放通过 | [ ] | — |
| 7.3.2 | Pipeline 阶段导航 | 同上 | M | 点击各阶段 → 内容切换正确 | [ ] | — |
| 7.3.3 | 审核面板操作 | 同上 | M | Approve/Reject 后状态变更 | [ ] | — |
| 7.3.4 | Chat 流程 E2E | `tests/e2e/chat-workflow.spec.ts` | M | 对话 + 工具调用展示 | [ ] | — |

### 7.4 Agent 质量评估
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 7.4.1 | 评估数据集 | `tests/eval/eval_dataset.py` | M | ≥3 个标注 case | [ ] | isa_extension + bug_fix + cleanup |
| 7.4.2 | Explorer 评估 | `tests/eval/run_eval.py` | L | precision/recall 计算正确 | [ ] | — |
| 7.4.3 | Prompt 回归测试 | `tests/eval/test_prompt_regression.py` | M | golden case 回归通过 | [ ] | — |

### 7.5 部署配置
| # | 任务 | 产出文件 | 量 | 验证 | 状态 | 备注 |
|---|------|----------|----|------|------|------|
| 7.5.1 | nginx.conf 生产配置 | `nginx/nginx.conf` | M | SSE 代理 + Gzip + 静态资源缓存 | [ ] | 对照 refactoring-plan §J |
| 7.5.2 | 生产 Docker Compose 验证 | — | M | `docker compose up -d` → nginx:80 可访问 | [ ] | — |
| 7.5.3 | 部署文档 | `docs/deploy.md` | L | 含步骤 + 环境变量 + 健康检查 + 备份恢复 | [ ] | — |
| 7.5.4 | API 文档 | `docs/api.md` | L | 全部端点含请求/响应示例 | [ ] | — |

---

## 阻塞项 & 风险跟踪

| ID | 描述 | 影响 Sprint | 发现日期 | 状态 | 解决方案 |
|----|------|------------|----------|------|----------|
| — | 暂无 | — | — | — | — |

---

## 每日开发日志

| 日期 | Sprint | 完成任务 | 遇到问题 | 解决方案 | 备注 |
|------|--------|----------|----------|----------|------|
| — | — | — | — | — | — |

---

## 变更日志

| 日期 | 变更 | 影响 |
|------|------|------|
| 2026-04-29 v1.0 | 初始创建，220 项任务 | — |
| 2026-04-29 v2.0 | 添加：工作量估算、产出文件、验证命令、前置条件、并行组、依赖关系图、每日日志 | 全部任务增加元数据列 |
