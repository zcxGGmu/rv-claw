# rv-claw 决策记录

> 目的：把当前重构开发中的关键决策集中收口，避免只在 `progress.md` 里悬挂问题而没有正式结论。  
> 规则：`progress.md` 的 D1-D6 是执行索引，本文件是决策正文与历史记录的权威来源。

---

## 1. 状态定义

| 状态 | 含义 |
|------|------|
| `open` | 尚未定案 |
| `default-applied` | 到达最晚关闭点，按默认方案执行 |
| `decided` | 已明确拍板 |
| `deferred` | 延后处理，不阻塞当前阶段 |
| `superseded` | 被后续决策替换 |

---

## 2. 更新规则

1. 新的关键决策必须先写入本文件，再反映到 `progress.md`
2. 一旦拍板，必须写明：
   - 决策日期
   - 最终方案
   - 影响范围
3. 若按默认方案执行，也要写清执行日期

---

## 3. 当前关键决策总览

| ID | 标题 | 当前状态 | 推荐默认方案 | 最晚关闭点 |
|----|------|----------|--------------|------------|
| D1 | 新 backend 是否与旧 backend 共用 MongoDB database name | open | 先共用 DB，按集合职责隔离 | G1.3 完成前 |
| D2 | 旧 `user_sessions` token 是否保留过渡兼容 | open | 切换窗口统一失效，要求重新登录 | G2.4 完成前 |
| D3 | DeepAgents 复用方式 | open | 通过 `backend/legacy_bridge` import 旧模块 | G3.1 完成前 |
| D4 | Pipeline test 节点首版是否允许仅做编译验证 | open | Release B 允许降级到编译验证 | G7.6 开始前 |
| D5 | QEMU 环境复用 sandbox 还是新建专用 service | open | Release C 新建专用 service | G7.6.3 开始前 |
| D6 | Statistics UI 是否首版加入 `mode` 切换 | open | Release A 不做，Release C 再决定 | G9.1.5 开始前 |

---

## 4. 决策正文

## D1 新 backend 是否与旧 backend 共用 MongoDB database name

- 状态：`open`
- 默认方案：先共用同一个 database name，通过新增集合隔离新域
- 最晚关闭点：G1.3 完成前
- 背景：
  - 过早拆成双 DB 会增加迁移与联调复杂度
  - 共用 DB 更利于 Release A 快速接管
- 影响范围：
  - DB 初始化
  - 回滚策略
  - 迁移脚本
- 最终决策：
  - 待填写

## D2 旧 `user_sessions` token 是否保留过渡兼容

- 状态：`open`
- 默认方案：切换窗口统一失效旧 token，要求重新登录
- 最晚关闭点：G2.4 完成前
- 背景：
  - 旧 token 实质是 session id
  - 新后端目标是 JWT
  - 双 token 过渡会显著增加认证复杂度
- 影响范围：
  - auth
  - 登录体验
  - 发布公告
- 最终决策：
  - 待填写

## D3 DeepAgents 复用方式

- 状态：`open`
- 默认方案：通过 `backend/legacy_bridge/deepagents.py` import 旧模块
- 最晚关闭点：G3.1 完成前
- 背景：
  - 直接复制旧模块会带来长期双副本维护成本
  - 直接散落 import 又会污染新架构边界
- 影响范围：
  - Chat 兼容实现
  - 后续清理旧 backend 的难度
- 最终决策：
  - 待填写

## D4 Pipeline test 节点首版是否允许仅做编译验证

- 状态：`open`
- 默认方案：Release B 允许，仅要求结构和状态机完整
- 最晚关闭点：G7.6 开始前
- 背景：
  - QEMU 真测环境的稳定性与搭建成本更高
  - 如果把它当作 Release B 阻塞项，会延误最小 pipeline 验证
- 影响范围：
  - Release B 范围
  - Release C 强化范围
- 最终决策：
  - 待填写

## D5 QEMU 环境复用 sandbox 还是新建专用 service

- 状态：`open`
- 默认方案：Release C 新建专用 service
- 最晚关闭点：G7.6.3 开始前
- 背景：
  - 现有 sandbox 主要服务通用 chat/code 执行
  - QEMU 与交叉编译链更可能需要单独资源和镜像策略
- 影响范围：
  - compose
  - docker image
  - 资源调度
- 最终决策：
  - 待填写

## D6 Statistics UI 是否首版加入 `mode` 切换

- 状态：`open`
- 默认方案：Release A 不加，Release C 再决定
- 最晚关闭点：G9.1.5 开始前
- 背景：
  - Release A 的核心是兼容接管
  - 统计 UI 的模式切换属于增强功能，不该阻塞接管
- 影响范围：
  - 前端统计 tab
  - usage ledger 聚合展示
- 最终决策：
  - 待填写

