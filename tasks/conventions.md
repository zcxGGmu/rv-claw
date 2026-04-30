# RV-Claw 编码规范

> **版本**: v1.0  
> **日期**: 2026-04-30  
> **适用范围**: 所有 AI Agent 在 rv-claw 仓库中的编码活动  
> **优先级**: 次于 `ai-behavior-contract.md`，高于一般工程实践

---

## 1. Python 编码规范

### 1.1 工具链

| 工具 | 用途 | 配置位置 |
|------|------|----------|
| `ruff` | Lint + Format | `pyproject.toml` |
| `mypy` | 类型检查 | `pyproject.toml` |
| `pytest` | 测试框架 | `pytest.ini` |
| `black` | 代码格式化（备用）| `pyproject.toml` |

### 1.2 ruff 规则集

```toml
[tool.ruff]
target-version = "py311"
line-length = 100
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # Pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "D",   # pydocstyle
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "SIM", # flake8-simplify
    "PTH", # flake8-use-pathlib
]
ignore = ["D100", "D104"]  # 允许模块级无 docstring（已有文件头注释）

[tool.ruff.pydocstyle]
convention = "google"
```

### 1.3 mypy 严格模式

```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
warn_redundant_casts = true
warn_unused_ignores = true
show_error_codes = true
```

### 1.4 类型注解强制要求

```python
# ✅ 正确 — 完整注解
async def create_case(
    db: AsyncIOMotorDatabase,
    data: CreateCaseRequest,
    user_id: str,
) -> Case:
    ...

# ❌ 错误 — 缺少参数/返回类型注解
async def create_case(db, data, user_id):
    ...

# ✅ 正确 — 使用 TypedDict / Pydantic
class PipelineState(TypedDict):
    case_id: str
    current_stage: Literal["explore", "plan", "develop", "review", "test"]

# ❌ 错误 — 使用裸 dict
state: dict  # 没有结构信息
```

### 1.5 错误处理规范

```python
# ✅ 正确 — 捕获具体异常
from backend.exceptions import StateTransitionError

try:
    result = await process_case(case_id, action)
except StateTransitionError as exc:
    logger.warning("Invalid state transition", case_id=case_id, error=str(exc))
    raise HTTPException(status_code=409, detail=str(exc))
except Exception as exc:
    logger.exception("Unexpected error processing case", case_id=case_id)
    raise HTTPException(status_code=500, detail="Internal server error")

# ❌ 错误 — 裸 except
try:
    result = await process_case(case_id, action)
except:  # 吞掉 KeyboardInterrupt!
    pass
```

### 1.6 异步代码规范

```python
# ✅ 正确 — 使用 asyncio 原生原语
await asyncio.gather(*tasks, return_exceptions=True)

# ✅ 正确 — 带超时的异步调用
async with asyncio.timeout(30):
    result = await adapter.execute(prompt, context)

# ❌ 错误 — 混用 sync / async
import requests  # 禁止在 async 代码中使用同步 HTTP 客户端
```

### 1.7 日志规范

```python
# ✅ 正确 — 结构化日志 + 上下文绑定
from structlog import get_logger

logger = get_logger("pipeline.explore")

logger.info(
    "Exploration started",
    case_id=state["case_id"],
    target_repo=state["target_repo"],
)

# ❌ 错误 — 字符串拼接
logger.info(f"Exploration started for case {case_id}")  # 不利于日志聚合
```

---

## 2. TypeScript / Vue 编码规范

### 2.1 工具链

| 工具 | 用途 | 配置位置 |
|------|------|----------|
| `eslint` | Lint | `.eslintrc.json` |
| `prettier` | Format | `prettier.config.js` |
| `vue-tsc` | 类型检查 | `tsconfig.json` |
| `vitest` | 单元测试 | `vitest.config.ts` |

### 2.2 ESLint 规则

```json
{
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:vue/vue3-recommended"
  ],
  "rules": {
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_" }],
    "vue/multi-word-component-names": "off"
  }
}
```

### 2.3 类型安全强制要求

```typescript
// ✅ 正确 — 完整的 Props / Emits 类型
const props = defineProps<{
  caseId: string;
  status: CaseStatus;
}>()

const emit = defineEmits<{
  (e: 'review', decision: ReviewDecision): void;
}>()

// ❌ 错误 — 使用 any
const props = defineProps<any>()

// ✅ 正确 — 函数返回类型显式声明
function useCaseStore(): {
  cases: Readonly<Ref<Case[]>>;
  loadCases: () => Promise<void>;
} {
  ...
}
```

### 2.4 Composable 规范

```typescript
// ✅ 正确 — 模块级 ref 单例（ScienceClaw 模式）
const cases = ref<Case[]>([])
const currentCase = ref<Case | null>(null)

export function useCaseStore() {
  async function loadCases() { /* ... */ }
  return {
    cases: readonly(cases),
    currentCase: readonly(currentCase),
    loadCases,
  }
}

// ❌ 错误 — 引入 Pinia（违反架构约束）
import { defineStore } from 'pinia'  // 禁止！
```

### 2.5 API 客户端规范

```typescript
// ✅ 正确 — 统一使用 api/client.ts
import { client } from '@/api/client'

export async function createCase(data: CreateCaseRequest): Promise<Case> {
  const response = await client.post<Case>('/api/v1/cases', data)
  return response.data
}

// ❌ 错误 — 直接创建 axios 实例
import axios from 'axios'
const client = axios.create({ baseURL: '/api/v1' })  // 禁止！
```

---

## 3. Git 规范

### 3.1 Commit Message 格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type 定义**:

| Type | 用途 |
|------|------|
| `feat` | 新功能 |
| `fix` | Bug 修复 |
| `refactor` | 重构（无功能变更）|
| `perf` | 性能优化 |
| `test` | 测试相关 |
| `docs` | 文档更新 |
| `chore` | 构建/工具/依赖更新 |
| `ci` | CI/CD 配置 |

**示例**:
```
feat(pipeline): 实现 explore_node 骨架 + Prompt 工程

- 定义 EXPLORER_SYSTEM_PROMPT（RISC-V 专用）
- 实现动态 prompt 构建（input_context + target_repo）
- Prompt 长度 >500 字符，包含 JSON Schema 示例

Closes P2.9.1
```

### 3.2 分支命名

```
feature/<phase>-<task-id>-<short-desc>
fix/<bug-desc>
refactor/<scope>-<desc>
```

**示例**:
```
feature/p0.2-init-backend-dirs
feature/p2.1-pipeline-state-model
```

---

## 4. API 设计规范

### 4.1 REST + SSE 规范

```python
# ✅ 正确 — REST 端点返回统一结构
@router.post("/cases", status_code=201)
async def create_case(data: CreateCaseRequest) -> CaseResponse:
    ...

# ✅ 正确 — SSE 端点使用 EventSourceResponse
@router.get("/cases/{case_id}/events")
async def case_events(case_id: str) -> EventSourceResponse:
    async def event_generator():
        ...
    return EventSourceResponse(event_generator())
```

### 4.2 错误响应规范

```json
{
  "detail": "Invalid state transition",
  "error_code": "INVALID_STATE_TRANSITION",
  "current_status": "exploring",
  "requested_action": "approve",
  "allowed_actions": ["wait"]
}
```

### 4.3 分页规范

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "pages": 5
}
```

---

## 5. 目录命名约定

```
backend/
  pipeline/          # Pipeline 引擎（小写）
  adapters/          # SDK 适配器（小写）
  datasources/       # 数据源（小写）
  contracts/         # 数据契约（小写）
  db/                # 数据库层（小写）
  route/             # API 路由（小写，单数）
  service/           # 业务逻辑（小写）
  config/            # 配置（小写）

frontend/src/
  views/             # 页面视图（小写）
  components/        # 组件（小写）
  composables/       # 组合式函数（小写）
  api/               # API 客户端（小写）
  types/             # 类型定义（小写）
  utils/             # 工具函数（小写）
```

---

## 6. 测试规范

### 6.1 命名规范

```python
# 后端
class TestPipelineState:
    def test_validate_missing_required_field_raises_error(self):
        ...

    def test_serialize_deserialize_roundtrip(self):
        ...

# 前端
function useCaseStore() {
  describe('loadCases', () => {
    it('should populate cases ref when API returns data', async () => {
      ...
    })
  })
}
```

### 6.2 目录结构

```
tests/
  unit/              # 单元测试
  integration/       # 集成测试
  e2e/               # 端到端测试
  fixtures/          # 测试数据工厂
  baseline/          # 回归基线
```

---

## 7. 配置规范

### 7.1 环境变量

```python
# ✅ 正确 — 统一通过 Settings 访问
from backend.config import settings

postgres_uri = settings.POSTGRES_URI

# ❌ 错误 — 业务代码中直接读取环境变量
import os
postgres_uri = os.getenv("POSTGRES_URI")  # 禁止！
```

### 7.2 Secrets 管理

```python
# ✅ 正确 — 生产环境敏感字段脱敏
class Settings(BaseSettings):
    CLAUDE_API_KEY: SecretStr

    @property
    def claude_api_key(self) -> str:
        return self.CLAUDE_API_KEY.get_secret_value()

# str(settings.CLAUDE_API_KEY) → "***"（生产环境）
```

---

> **本规范自 2026-04-30 起生效。所有 AI 编码活动必须遵守本规范。**
> **规范本身的修改需通过人类工程师审批。**
