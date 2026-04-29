# ADR-003: Redis Pub/Sub + Stream 作为 Pipeline SSE 事件总线

**日期**: 2026-04-25
**状态**: accepted
**决策者**: RV-Insights Team

## 背景

Pipeline 执行过程中需要实时向 Web 前端推送事件（阶段变更、Agent 输出、审核请求等）。核心需求：

1. **实时推送**：Agent 节点产生的事件需立即到达前端
2. **断线重连恢复**：前端 SSE 连接断开后，重连时应收到断连期间丢失的事件
3. **多实例兼容**：未来水平扩展时，事件需跨进程/跨主机广播
4. **解耦**：Agent 节点不应感知前端的连接状态

## 决策

使用 **Redis Pub/Sub + Stream 双通道** 作为 Pipeline SSE 事件总线。

架构：
```
Agent Node → EventPublisher.publish()
              ├── Redis Pub/Sub (case:{id}:events)  → 实时推送到在线客户端
              └── Redis Stream (case:{id}:stream)    → 持久化事件（maxlen=500），用于断线重连恢复

SSE Endpoint:
  1. 订阅 Redis Pub/Sub → 实时转发事件到前端
  2. 重连时：读取 Last-Event-ID → 从 Redis Stream 补偿丢失的事件
  3. 心跳：每 30s 发送 keepalive（不写入 Stream）
```

Chat 模式不使用 Redis，而是使用进程内的 `asyncio.Queue`（Chat 模式不需要跨进程广播）。

## 考虑的替代方案

1. **进程内 asyncio.Queue** — 优点：简单；缺点：不支持跨进程/跨主机，无法断线恢复
2. **直接 SSE（无中间层）** — 优点：零额外依赖；缺点：Agent 节点需持有 SSE 连接引用，紧耦合；无断线恢复
3. **Kafka** — 优点：企业级消息队列；缺点：对 MVP 过于重量级
4. **Redis Stream 单独使用** — 优点：持久化 + 消费组；缺点：实时推送轮询效率不如 Pub/Sub

## 后果

### 正面影响
- Pub/Sub 保证实时性，Stream 保证可靠性
- 双通道透明切换，Pub/Sub 故障时自动降级到 Stream 轮询
- Redis 已在技术栈中（Celery 任务队列），无新增依赖
- Stream maxlen 自动淘汰，无需手动清理

### 负面影响
- 两个通道增加了实现复杂度和测试用例
- Redis 成为 Pipeline SSE 的单点故障（需 Redis 高可用）
- Pub/Sub 消息不持久化，Redis 重启期间事件丢失（由 Stream 补偿）

## 相关
- design.md §2.8 SSE 事件总线
- refactoring-plan.md 附录 E.3 EventPublisher 实现
