# Phase 3: Notifications Spec

## Why
Phase 2 完成了管线编辑器，但任务协作过程中用户无法实时获知任务变更。Phase 3 实现 WebSocket 实时通知，让用户在任务被指派、信息变更、新增评论时立即收到推送。

## What Changes
- 新增 Notification 数据模型
- 新增通知 CRUD API（REST + WebSocket 推送）
- 新增 NotificationConsumer WebSocket 消费者
- 新增 NotificationBackend 适配器模式（WebSocketBackend 首期实现）
- 注册 ASGI WebSocket 路由
- tasks/signals.py 中 TaskLog→Notification 信号联动
- 前端 notifications store 新增 WebSocket 连接逻辑
- NotificationBell.vue 组件整合实时推送

## Impact
- Affected specs: tasks（信号联动）
- Affected code: [backend/apps/notifications/](file:///Users/zhaofuqing/Documents/Developer/Caduceus/backend/apps/notifications/), [backend/config/asgi.py](file:///Users/zhaofuqing/Documents/Developer/Caduceus/backend/config/asgi.py), [backend/config/urls.py](file:///Users/zhaofuqing/Documents/Developer/Caduceus/backend/config/urls.py), [backend/apps/tasks/signals.py](file:///Users/zhaofuqing/Documents/Developer/Caduceus/backend/apps/tasks/signals.py), [frontend/src/stores/notifications.js](file:///Users/zhaofuqing/Documents/Developer/Caduceus/frontend/src/stores/notifications.js), [frontend/src/components/NotificationBell.vue](file:///Users/zhaofuqing/Documents/Developer/Caduceus/frontend/src/components/NotificationBell.vue)

## ADDED Requirements

### Requirement: Notification Model
系统 SHALL 支持站内通知记录，每个通知关联一个接收者用户。

Notification SHALL 包含：
- `recipient`: FK → User（接收者）
- `type`: CharField（通知类型：task_assigned / task_updated / comment_added / stage_changed）
- `title`: CharField（通知标题）
- `content`: TextField（通知内容）
- `link`: CharField（点击跳转链接，指向具体任务）
- `is_read`: BooleanField（已读标记）
- `created_at`: DateTimeField（创建时间）

#### Scenario: 任务指派通知
- **WHEN** 管理员将任务指派给执行人
- **THEN** 系统自动创建 Notification（type=task_assigned, title="新任务指派", content 含任务标题），通过 WebSocket 推送给被指派人

#### Scenario: 任务信息变更通知
- **WHEN** 任务的关键字段（标题、状态等）被修改
- **THEN** 系统创建 Notification 并推送至所有任务参与者

### Requirement: Notification REST API
系统 SHALL 提供通知的 REST API 供前端列表查询和已读标记。

- GET /api/notifications/ — 当前用户的通知列表（按时间倒序）
- GET /api/notifications/unread_count/ — 未读通知数量
- PATCH /api/notifications/{id}/ — 标记单个通知已读
- POST /api/notifications/mark_all_read/ — 全部标记已读

#### Scenario: 获取未读计数
- **WHEN** 用户登录后请求 /api/notifications/unread_count/
- **THEN** 返回当前用户未读通知的计数

### Requirement: WebSocket Notification Push
系统 SHALL 通过 Django Channels WebSocket 实时推送通知。

- WebSocket 路径：`/ws/notifications/`
- 连接时基于用户身份进行认证，每个用户加入自己的通知组
- 通知创建时通过 WebSocketBackend 将消息推送到对应用户的 WebSocket
- 前端 WebSocket 连接在登录成功后建立，登出时断开

#### Scenario: 实时推送
- **WHEN** 后端创建一条 Notification 记录
- **THEN** 对应的接收者在前端立即收到通知（无需刷新页面），铃铛图标显示未读计数变化

### Requirement: NotificationBackend Adapter
系统 SHALL 使用适配器模式实现通知推送，预留 EmailBackend、WebhookBackend 等扩展。

- `NotificationBackend`（ABC 抽象基类）：定义 `send(notification)` 接口
- `WebSocketBackend`：首期实现，通过 Channels channel layer 发送消息

#### Scenario: 适配器调用
- **WHEN** 信号触发创建 Notification 后
- **THEN** 通过 WebSocketBackend.send() 推送，后续可通过配置切换不同推送渠道

### Requirement: Signal Integration
系统 SHALL 在 TaskLog 创建后自动生成通知。

- tasks/signals.py 监听 TaskLog post_save
- 根据 TaskLog.action 映射通知类型和标题
- 对任务相关参与人创建通知

#### Scenario: 评论通知
- **WHEN** 用户在任务下新增评论（TaskLog action=commented）
- **THEN** 所有任务参与者收到通知"xxx 评论了任务"

## MODIFIED Requirements

### Requirement: Frontend NotificationBell 实时更新
前端通知铃铛组件 SHALL 通过 WebSocket 接收实时推送，无需依赖轮询。

- notifications store 的 `connectWebSocket()` SHALL 建立 `/ws/notifications/` 连接
- 收到服务端消息时 SHALL 更新 notifications 列表和 unreadCount
- NotificationBell.vue 的 badge 实时响应 store 变化
