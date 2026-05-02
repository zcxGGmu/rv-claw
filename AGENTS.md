# ScienceClaw 项目知识库

> **生成时间**: 2026-05-02
> **范围**: 全项目

---

## 项目概览

ScienceClaw 是一个面向科研人员的 AI 助手，基于 FastAPI + Vue 3 + Docker 构建。核心能力是通过 Agent 引擎（当前使用 DeepAgents/LangGraph）调用 1900+ 科学工具，生成多格式研究报告（PDF/DOCX/PPTX/XLSX）。

---

## 项目结构

```
ScienceClaw/
├── backend/                    # FastAPI 后端（Python）
│   ├── deepagent/              # Agent 核心引擎（正在重构）
│   ├── builtin_skills/         # 8 个内置技能（文档生成等）
│   ├── route/                  # REST API 路由
│   ├── im/                     # 飞书/微信 IM 集成
│   ├── mongodb/                # 数据库访问层
│   ├── user/                   # 用户管理
│   └── main.py                 # FastAPI 入口
├── frontend/                   # Vue 3 + Tailwind 前端
├── sandbox/                    # AIO Sandbox 隔离执行环境
├── task-service/               # 定时任务调度服务
└── websearch/                  # SearXNG + Crawl4AI 搜索服务

Tools/                          # 用户自定义工具（热加载）
Skills/                         # 用户自定义技能
workspace/                      # 用户工作目录
```

---

## 去哪里找

| 任务 | 位置 | 说明 |
|------|------|------|
| 修改 Agent 引擎 | `backend/deepagent/` | 核心引擎，当前正从 DeepAgents 迁移到 Claude SDK |
| 添加 API 接口 | `backend/route/` | FastAPI 路由定义 |
| 添加内置工具 | `backend/deepagent/tools.py` | `@tool` 装饰的函数 |
| 添加自定义工具 | `Tools/` 目录 | 热加载，无需重启 |
| 添加技能 | `Skills/` 目录 | 放置 SKILL.md 文件 |
| 修改前端页面 | `frontend/src/pages/` | Vue 页面组件 |
| 修改飞书集成 | `backend/im/` | IM 适配器和命令处理器 |
| 查看文档生成 | `backend/builtin_skills/` | pdf/docx/pptx/xlsx 生成逻辑 |

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Tailwind CSS + Vite |
| 后端 | FastAPI + Python 3.11 |
| Agent 引擎 | DeepAgents 0.4.4 + LangGraph 1.0.8（目标：Claude Agent SDK） |
| 数据库 | MongoDB |
| 搜索 | SearXNG + Crawl4AI |
| 沙箱 | AIO Sandbox (Docker 隔离) |
| 部署 | Docker Compose（10 个服务） |

---

## 常用命令

```bash
# 开发启动（全部服务）
docker compose up -d --build

# 生产启动（预构建镜像）
docker compose -f docker-compose-release.yml up -d --pull always

# 查看后端日志
docker compose logs -f backend

# 重启单个服务
docker compose restart backend

# 进入后端容器
docker exec -it scienceclaw-backend-1 bash

# 运行后端测试（容器内）
pytest backend/deepagent/tests/ -v
```

---

## 约定

- **只读禁区**: `backend/deepagent/` 当前正在重构为 `backend/clawagent/`，旧目录冻结不可改
- **前端零改动**: 后端重构期间前端代码不修改
- **热加载**: `Tools/` 和 `Skills/` 目录下的文件变更无需重启服务
- **Docker 优先**: 所有服务必须在 Docker 内运行，禁止本地直接启动依赖服务

---

## 反模式（本项目禁止）

| # | 禁止行为 | 原因 |
|---|---------|------|
| 1 | 修改 `backend/deepagent/` 任何文件 | 目录已冻结，保留作为后备引擎 |
| 2 | 使用 `asyncio.run()` 在同步上下文里 | 会导致线程池耗尽和竞态条件 |
| 3 | 模块级全局 dict 存储会话数据 | 多会话并发时互相污染 |
| 4 | 直接调用 `langchain-openai` 内部 API（下划线开头） | 版本升级会破环 monkey-patch |
| 5 | 新增工具时只改 `tools.py` | 必须同时在 `sse_protocol.py` 注册元数据 |
| 6 | 在前端代码中硬编码后端 URL | 使用环境变量或配置 |

---

## 注意事项

- `backend/deepagent/runner.py` 是项目最复杂的文件（891 行），处理 LangGraph 双流合并
- `backend/deepagent/engine.py` 包含 70 行 monkey-patch，用于支持 reasoning_content
- 重构期间使用 `scripts/switch-agent.sh [claw|deep]` 切换新旧引擎
- 所有技能生成的文档都在 `workspace/` 目录下
- **测试缺失**: 项目目前零测试（`tests/e2e/` 为空，无 pytest 配置）
- **CI/CD 缺失**: 无 GitHub Actions / GitLab CI，纯手动 `release.sh` 发布
- **Python 版本不一致**: backend 用 3.13，sandbox/websearch 用 3.12，task-service 用 3.11
- **代码重复**: `seekr_sdk.py` 在 backend/sandbox/websearch 三处重复；`builtin_skills/{docx,pptx,xlsx}/scripts/office/` 大量重复代码

---

## 安全风险（必须知晓）

| 问题 | 位置 | 风险等级 |
|------|------|---------|
| `.env` 包含真实 API Key 且被 git 跟踪 | 根目录 | 🔴 高 |
| 无 `.gitignore` | 根目录 | 🔴 高 |
| MongoDB 密码硬编码在 docker-compose 中 | `docker-compose*.yml` | 🟠 中 |
| WebSearch API Key 硬编码 | `docker-compose*.yml` | 🟠 中 |
| Sandbox `seccomp:unconfined` | `docker-compose.yml` | 🟡 低 |

---

## 入口文件

| 入口 | 文件 | 说明 |
|------|------|------|
| FastAPI 应用 | `backend/main.py` | 注册所有路由和中间件 |
| Agent 流式执行 | `backend/deepagent/runner.py` | SSE 流式响应核心 |
| Agent 组装 | `backend/deepagent/agent.py` | 创建 Agent + 工具 + 中间件 |
| 前端应用 | `frontend/src/main.ts` | Vue 应用入口 |

---

## 重构状态

当前正在进行从 DeepAgents 到 Claude Agent SDK 的迁移。
规划文档位于 `tasks/progress-tracking/` 目录。
新引擎代码写入 `backend/clawagent/`（开发中）。
