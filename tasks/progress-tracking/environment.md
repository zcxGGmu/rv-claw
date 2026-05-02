# ScienceClaw 重构 — 开发环境状态

> **用途**: 记录当前开发环境的关键状态，防止环境漂移，便于复现问题。
> **更新时机**: 环境变更后、问题复现前、新开发者加入时。

---

## 1. 项目路径

| 属性 | 值 |
|------|-----|
| **项目根目录** | `/Users/zq/Desktop/ai-projs/posp/rv-claw/` |
| **后端目录** | `ScienceClaw/backend/` |
| **旧引擎目录** | `ScienceClaw/backend/deepagent/` (冻结，只读) |
| **新引擎目录** | `ScienceClaw/backend/clawagent/` (开发中) |
| **软链接** | `ScienceClaw/backend/active_agent` → `clawagent/` (当前) |

---

## 2. Python 环境

| 属性 | 值 |
|------|-----|
| **Python 版本** | 3.11+ (待确认) |
| **虚拟环境** | 待创建 (`venv-claw` 推荐) |
| **包管理器** | pip |
| **主要依赖** | 见 `requirements.txt` |

### 关键依赖版本

| 包名 | 当前版本 | 目标版本 | 状态 |
|------|---------|---------|------|
| `deepagents` | 0.4.4 | — | 🟡 待移除 |
| `langgraph` | 1.0.8 | — | 🟡 待移除 |
| `langchain-core` | 0.3.15 (预估) | 锁定 | 🟢 保留 |
| `langchain-openai` | 1.1.8 (预估) | 锁定 | 🟢 保留 |
| `claude-agent-sdk` | — | >=0.1.0 | 🟡 待添加 |
| `fastapi` | — | 保留 | 🟢 不变 |
| `uvicorn` | — | 保留 | 🟢 不变 |

---

## 3. Docker 环境

| 属性 | 值 |
|------|-----|
| **Docker Compose 文件** | `docker-compose.yml`, `docker-compose-release.yml`, `docker-compose-china.yml` |
| **Backend 服务名** | `backend` |
| **Backend 暴露端口** | 8000 |
| **Frontend 暴露端口** | 5173 |

### 服务清单（10 个）

| 服务 | 状态 | 重构影响 |
|------|------|---------|
| backend | 🟢 运行中 | 🔴 直接修改 |
| frontend | 🟢 运行中 | 🟢 不修改 |
| sandbox | 🟢 运行中 | 🟡 可能调整配置 |
| websearch | 🟢 运行中 | 🟢 不修改（长期可能移除） |
| task-service | 🟢 运行中 | 🟢 不修改 |
| mongodb | 🟢 运行中 | 🟢 不修改 |
| searxng | 🟢 运行中 | 🟢 不修改 |
| crawl4ai | 🟢 运行中 | 🟢 不修改 |
| redis | 🟢 运行中 | 🟢 不修改 |
| nginx | 🟢 运行中 | 🟢 不修改 |

---

## 4. 环境变量

### 必须配置

| 变量名 | 用途 | 当前值 | 状态 |
|--------|------|--------|------|
| `ANTHROPIC_API_KEY` | Claude SDK 认证 | 未设置 | 🔴 必须配置 |
| `AGENT_IMPL` | 引擎选择 | 未设置 | 🟡 开发中新增 |
| `OPENAI_API_KEY` | OpenAI 兼容端点 | 可能已设置 | 🟢 如有则保留 |
| `DEEPSEEK_API_KEY` | DeepSeek 端点 | 可能已设置 | 🟢 如有则保留 |

### 路径变量

| 变量名 | 用途 | 当前值 |
|--------|------|--------|
| `BUILTIN_SKILLS_DIR` | 内置 Skills | `/app/builtin_skills` |
| `EXTERNAL_SKILLS_DIR` | 外置 Skills | `/app/Skills` |
| `WORKSPACE_DIR` | 工作空间 | `/home/scienceclaw` |

---

## 5. 数据库状态

| 属性 | 值 |
|------|-----|
| **数据库** | MongoDB |
| **连接字符串** | 见 `.env` 或 `config.py` |
| **关键集合** | sessions, users, tasks, evaluations |
| **数据结构变更** | 本重构不修改数据结构（100% 兼容） |

---

## 6. 网络配置

| 属性 | 值 |
|------|-----|
| **Backend API** | `http://localhost:8000` |
| **Health Check** | `http://localhost:8000/health` |
| **WebSocket/SSE** | `http://localhost:8000/sessions/{id}/stream` |

---

## 7. 已知环境限制

| # | 限制 | 影响 | 缓解方案 |
|---|------|------|---------|
| 1 | `claude-agent-sdk` 尚未发布稳定版 | 可能 API 变化 | 锁定版本，关注 changelog |
| 2 | Docker Desktop 内存限制（默认 2GB） | 构建可能 OOM | 增加至 4GB+ |
| 3 | 国内网络可能无法访问 Anthropic API | SDK 无法调用 | 使用代理或 base_url 指向国内端点 |

---

## 8. 环境变更记录

| 日期 | 变更 | 变更人 | 影响 |
|------|------|--------|------|
| — | — | — | — |

---

## 快速诊断

### 环境是否正常的检查流程

```bash
# 1. 检查 Docker 服务
docker compose ps

# 2. 检查 Backend 健康
curl http://localhost:8000/health

# 3. 检查 clawagent 模块可导入
docker exec backend python -c "import backend.clawagent"

# 4. 检查旧引擎未损坏
docker exec backend python -c "import backend.deepagent"

# 5. 检查软链接指向
ls -l ScienceClaw/backend/active_agent

# 6. 运行单元测试
pytest ScienceClaw/backend/clawagent/tests/ -v
```

---

> **更新规则**: 任何环境变更（依赖版本、Docker 配置、环境变量）必须记录到"环境变更记录"表中。
