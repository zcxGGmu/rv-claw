# rv-claw 兼容契约基线

> 目的：在重构过程中，明确哪些 HTTP/SSE/前端行为必须保持与当前 ScienceClaw 基线兼容。  
> 适用阶段：至少覆盖 Release A；Release B/C 在不破坏既有契约的前提下扩展。  
> 权威性：若实现与本文件冲突，优先修实现；如确需改契约，必须先更新本文件和对应 tests。

---

## 1. 契约范围

当前必须受保护的兼容对象：

1. 认证接口
2. sessions/chat/share/files 相关接口
3. `/api/v1/chat`
4. `/api/v1/task/parse-schedule`
5. statistics/task-settings/memory/models/im
6. Chat SSE 事件
7. Share 页面依赖的只读行为
8. 当前前端路由基线

---

## 2. 顶层不变量

### 2.1 HTTP 前缀

- 兼容接口继续使用 `/api/v1/*`

### 2.2 前端基线

当前前端基线固定为：

- `ScienceClaw/frontend/`

必须继续可用的主路由：

- `/`
- `/chat/:sessionId`
- `/chat/skills`
- `/chat/skills/:skillName`
- `/chat/tools`
- `/chat/tools/:toolName`
- `/chat/science-tools/:toolName`
- `/chat/tasks`
- `/share/:sessionId`
- `/login`

新增允许：

- `/cases`
- `/cases/:id`

禁止：

- 因重构删除上述既有入口
- 未完成 Release A 就迁移到另一套前端目录

### 2.3 认证方式

- 前端继续通过 Bearer token 调用新 backend
- 是否兼容旧 token 由 `decision-log.md` 中 D2 决定

---

## 3. HTTP 契约

## 3.1 Auth

### 必保留接口

- `GET /api/v1/auth/check-default-password`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/register`
- `GET /api/v1/auth/status`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/change-password`
- `POST /api/v1/auth/change-fullname`
- `POST /api/v1/auth/logout`

### 必保留行为

| 接口 | 契约要求 |
|------|----------|
| `/auth/login` | 返回 user + access_token + refresh_token + token_type |
| `/auth/status` | 未登录返回 `authenticated=false`，已登录返回 user |
| `/auth/me` | 返回当前用户结构 |
| `/auth/refresh` | 成功时返回新 access_token |
| `/auth/logout` | 前端能够据此清理本地登录态 |

### 允许变化

- token 的内部实现可从 session id 切换到 JWT
- refresh token 的持久化结构可变化

### 不允许变化

- 前端需要额外引入第二套认证流程
- `/auth/status` 改成前端无法直接判断登录态的返回格式

## 3.2 Sessions / Chat

### 必保留接口

- `PUT /api/v1/sessions`
- `GET /api/v1/sessions`
- `GET /api/v1/sessions/{id}`
- `DELETE /api/v1/sessions/{id}`
- `PATCH /api/v1/sessions/{id}/pin`
- `PATCH /api/v1/sessions/{id}/title`
- `POST /api/v1/sessions/{id}/chat`
- `POST /api/v1/sessions/{id}/stop`
- `POST /api/v1/sessions/{id}/share`
- `DELETE /api/v1/sessions/{id}/share`
- `GET /api/v1/sessions/shared/{id}`
- `POST /api/v1/sessions/{id}/clear_unread_message_count`
- `GET /api/v1/sessions/{id}/files`
- `GET /api/v1/sessions/{id}/sandbox-file`
- `GET /api/v1/sessions/{id}/sandbox-file/download`

### 必保留行为

| 接口 | 契约要求 |
|------|----------|
| `PUT /sessions` | 创建新会话并返回 `session_id` |
| `GET /sessions` | 返回前端会话列表可直接消费的数据 |
| `GET /sessions/{id}` | 返回包含事件流、状态、标题、共享状态的详情 |
| `POST /sessions/{id}/chat` | SSE 流式返回事件 |
| `POST /sessions/{id}/stop` | 运行中的会话可被停止 |
| `share/unshare` | share 页面可继续访问对应只读会话 |

### 允许变化

- session 文档内部结构
- chat runner 内部实现
- stop 的内部中断方式

### 不允许变化

- 改掉现有前端必须依赖的路径
- 把 Chat 改成需要前端切换到另一套事件协议

## 3.3 Files

### 必保留接口族

- `/api/v1/files/*`
- `/api/v1/sessions/{id}/upload`
- `/api/v1/sessions/{id}/files`
- `/api/v1/sessions/{id}/sandbox-file*`

### 必保留行为

- 文件上传成功后前端附件与文件面板能正常工作
- 下载接口对前端预览链路可用
- sandbox 文件读取受白名单保护

## 3.4 Models / Memory / Task Settings / Statistics / IM

### 必保留接口族

- `/api/v1/models/*`
- `/api/v1/memory`
- `/api/v1/task-settings`
- `/api/v1/statistics/*`
- `/api/v1/im/*`

### 必保留行为

- Settings 对应 tab 能正常读取和保存
- Statistics 相关接口至少能支撑当前 chat 统计视图
- IM 设置与绑定页不因后端切换失效

## 3.5 Scheduler Compatibility

### 必保留接口

- `POST /api/v1/chat`
- `POST /api/v1/task/parse-schedule`

### 必保留行为

- task-service 能继续触发一次 Chat 执行
- schedule 文本仍可转换为 crontab 或合理报错

---

## 4. Chat SSE 契约

### 必保留事件名

- `tool`
- `step`
- `message`
- `error`
- `done`
- `title`
- `wait`
- `plan`
- `attachments`
- `thinking`

### 必保留共性字段

- `event_id`
- `timestamp`

### 关键语义

| 事件 | 契约 |
|------|------|
| `message` | 必须可被前端消息渲染组件直接消费 |
| `tool` | 前端工具视图和右侧面板可识别 |
| `plan` | 前端计划面板可识别 |
| `done` | 可选统计信息和 round files 继续支持 |
| `error` | 前端不会因异常事件白屏 |

### 允许变化

- 内部 runner 如何生产这些事件
- 字段计算来源

### 不允许变化

- 改名
- 删除前端已依赖字段
- 把一次 chat 改成非流式轮询协议

---

## 5. Share 契约

必须继续满足：

1. `SharePage` 无需登录即可查看共享会话
2. 共享会话的消息内容可读
3. 共享会话关联文件可读/下载（在既有安全约束下）

不允许：

- 因认证改造导致旧的 share 行为整体失效

---

## 6. Release A 的兼容判定标准

只有同时满足以下条件，才可以声称“兼容接管版完成”：

1. 现有前端无需切换到第二套目录或协议
2. 现有 Chat 主链路可工作
3. Tools/Skills/Statistics/Tasks/IM 不报致命错误
4. Share 页面可用
5. task-service 可继续驱动 Chat

---

## 7. 契约变更流程

若必须修改兼容契约，必须同步做 4 件事：

1. 更新本文件
2. 更新 `progress.md`
3. 更新相关 contract fixtures / tests
4. 在 `decision-log.md` 写明原因

没有完成这 4 步，不得把兼容变化视为已接受。

