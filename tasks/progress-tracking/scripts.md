# ScienceClaw 重构 — 开发辅助脚本手册

> **用途**: 汇总开发、测试、调试所需的自定义脚本
> **存放路径**: `scripts/` 目录下

---

## 1. 已有脚本

### `scripts/switch-agent.sh`

用途: 在 deepagent/ 和 clawagent/ 之间切换软链接
用法: `./scripts/switch-agent.sh [claw|deep]`

---

## 2. 推荐新增脚本

### `scripts/dev-check.sh` — 开发环境健康检查

检查项:
- Docker 服务运行状态
- Backend 健康检查
- clawagent/ 模块可导入
- deepagent/ 模块可导入
- 软链接指向正确
- 环境变量配置

### `scripts/compare-sse.py` — SSE 事件流对比

用途: 对比新旧引擎的 SSE 输出格式
用法: `python scripts/compare-sse.py --old deep --new claw`

### `scripts/run-tests.sh` — 测试运行器

用法: `./scripts/run-tests.sh [unit|integration|all]`

### `scripts/check-constraints.sh` — 约束合规检查

检查项:
- deepagent/ 无修改
- frontend/ 无修改
- 无 as any / @ts-ignore
- 无删除测试

### `scripts/benchmark.sh` — 性能基准测试

测量项: 首token延迟、工具调用延迟、内存占用

### `scripts/generate-report.sh` — 进度报告生成

输出: 任务完成数、Phase进度、工时偏差、阻塞项

---

## 3. 脚本开发规范

1. Bash脚本: `#!/bin/bash` + `set -euo pipefail`
2. Python脚本: `#!/usr/bin/env python3`
3. 所有脚本支持 `--help`
4. 日志格式: `[INFO] ...` / `[ERROR] ...`
5. 不硬编码绝对路径

---

## 4. 快捷命令别名

推荐添加到 `.bashrc` / `.zshrc`:

```bash
alias sc-check="./scripts/dev-check.sh"
alias sc-test="./scripts/run-tests.sh"
alias sc-switch="./scripts/switch-agent.sh"
alias sc-constraints="./scripts/check-constraints.sh"
alias sc-benchmark="./scripts/benchmark.sh"
```

---

> 本文件为规划文档，脚本实际开发在对应Phase中完成
