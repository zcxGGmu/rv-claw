# ScienceClaw 重构 — 进度跟踪文档索引

> **用途**: 本目录下所有文件的导航和职责说明
> **必读顺序**: `README` → `constraints.md` → `adr.md` → `progress.md`

---

## 文件清单

| 文件 | 职责 | 谁需要读 | 更新频率 |
|------|------|---------|---------|
| **`README.md`** (本文件) | 目录导航、文件职责说明、阅读顺序 | 所有参与者 | 新增文件时 |
| **`progress.md`** | 322 个原子任务 + Current Focus + 技术债务 + 已知问题 + 依赖矩阵 | 所有开发者、AI Agent | 每轮对话 |
| **`constraints.md`** | 开发行为边界（禁止/必须/契约） | 所有开发者、AI Agent | 每 Phase 评审后 |
| **`adr.md`** | 架构决策记录（冻结后不可改） | 架构师、审查者 | 新决策时 |
| **`acceptance.md`** | 验收标准（消除"差不多行了"） | 执行者、审查者 | 每 Phase 验收时 |
| **`risk-register.md`** | 风险登记与缓解跟踪 | 项目经理、技术负责人 | 每日站会 |
| **`standup-template.md`** | 每日站会标准化模板 | 所有开发者 | 按需参考 |
| **`tech-debt.md`** | 技术债务详细跟踪（产生原因、影响、偿还计划） | 开发者、架构师 | 发现债务时 |
| **`environment.md`** | 开发环境状态快照（依赖、Docker、变量、限制） | 所有开发者 | 环境变更时 |
| **`scripts.md`** | 开发辅助脚本手册（用法、规范、别名） | 开发者 | 新增脚本时 |

---

## 阅读顺序（按角色）

### 新加入的开发者

1. 读 `constraints.md` — 知道什么能碰、什么不能碰
2. 读 `adr.md` — 理解架构决策背景
3. 读 `acceptance.md` — 理解"完成"的精确标准
4. 读 `progress.md` — 找到自己的任务
5. 参考 `standup-template.md` — 准备首次站会

### 代码审查者

1. 读 `constraints.md` — 逐条核对审查清单
2. 读 `acceptance.md` — 确认任务级验收标准
3. 读 `adr.md` — 确认无违背冻结决策
4. 查 `progress.md` — 确认任务状态更新

### AI Agent（如 Sisyphus）

1. **每次对话开始时必读**: `constraints.md`（行为边界）+ `progress.md` 的 **Current Focus** 区域（当前状态）
2. **开发中参考**: `scripts.md`（快捷命令）+ `environment.md`（环境状态）
3. **修改架构前必读**: `adr.md`（冻结决策）
4. **标记任务完成前必读**: `acceptance.md`（验收标准）+ `progress.md` 的 **开发检查清单**
5. **产生临时方案时**: 记录到 `progress.md` 技术债务章节 + `tech-debt.md`
6. **发现风险时**: 更新 `risk-register.md`

---

## 文件间的引用关系

```
progress.md (任务清单)
    ├── 引用 constraints.md → "按约束执行"
    ├── 引用 adr.md → "遵循已批准决策"
    ├── 引用 acceptance.md → "满足验收标准后标记完成"
    └── 引用 risk-register.md → "注意风险项"

constraints.md (行为边界)
    ├── 引用 adr.md → "ADR 冻结后不可改"
    └── 引用 acceptance.md → "审查清单"

adr.md (决策记录)
    └── 被 constraints.md / acceptance.md 引用

acceptance.md (验收标准)
    ├── 引用 progress.md → "Phase 验收项"
    └── 引用 constraints.md → "审查清单"

risk-register.md (风险)
    └── 引用 progress.md → "风险来源任务"

tech-debt.md (技术债务)
    └── 引用 progress.md → "债务产生任务"
    └── 被 risk-register.md 引用 → "债务可能演变为风险"

environment.md (环境状态)
    └── 被 scripts.md 引用 → "脚本依赖环境"
    └── 被 progress.md 引用 → "环境限制"

scripts.md (辅助脚本)
    └── 被 progress.md 引用 → "快捷命令参考"
```

---

## 快速导航

### 按开发阶段

| 阶段 | 相关文件 |
|------|---------|
| **开始前** | `constraints.md` + `adr.md` |
| **进行中** | `progress.md` (Current Focus) + `scripts.md` + `environment.md` |
| **完成后** | `acceptance.md` + 更新 `progress.md` 技术债务 |
| **每日** | `progress.md` + `standup-template.md` |
| **每周** | `risk-register.md`（深度评审）+ `tech-debt.md`（债务审查） |

### 按操作

| 操作 | 参考文件 |
|------|---------|
| 标记任务完成 | `progress.md` + `acceptance.md` |
| 代码审查 | `constraints.md` + `acceptance.md` |
| 发现新风险 | `risk-register.md` |
| 需要修改架构决策 | `adr.md`（提交新 ADR） |
| 遇到行为边界问题 | `constraints.md` |
| 环境异常 | `environment.md` + `scripts.md` (dev-check) |
| 发现临时方案 | `tech-debt.md` + `progress.md` 技术债务章节 |
| 需要快捷命令 | `scripts.md` |

---

## 版本管理

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-05-02 | 初始创建，7 个文件 |
| v1.1 | 2026-05-02 | 新增 progress.md 章节（Current Focus、技术债务、已知问题、依赖矩阵、AI上下文协议），新增 tech-debt.md、environment.md、scripts.md，共 10 个文件 |
