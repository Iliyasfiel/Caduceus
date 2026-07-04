# Tasks

- [x] Task 1: 实现 Notification 模型
  - [x] 重写 [backend/apps/notifications/models.py](file:///Users/zhaofuqing/Documents/Developer/Caduceus/backend/apps/notifications/models.py)：创建 Notification 模型（recipient, type, title, content, link, is_read, created_at）
  - [x] 生成迁移并执行验证（0001_initial 迁移通过）

- [x] Task 2: 实现 Notification REST API
  - [x] 创建 [backend/apps/notifications/api/serializers.py](file:///Users/zhaofuqing/Documents/Developer/Caduceus/backend/apps/notifications/api/serializers.py)：NotificationSerializer
  - [x] 创建 [backend/apps/notifications/api/views.py](file:///Users/zhaofuqing/Documents/Developer/Caduceus/backend/apps/notifications/api/views.py)：NotificationViewSet（unread_count + mark_all_read）
  - [x] 创建 [backend/apps/notifications/api/urls.py](file:///Users/zhaofuqing/Documents/Developer/Caduceus/backend/apps/notifications/api/urls.py)
  - [x] 在 [backend/config/urls.py](file:///Users/zhaofuqing/Documents/Developer/Caduceus/backend/config/urls.py) 注册路由

- [x] Task 3: 实现 WebSocket Consumer + 适配器模式
  - [x] 创建 [backend/apps/notifications/consumers.py](file:///Users/zhaofuqing/Documents/Developer/Caduceus/backend/apps/notifications/consumers.py)：NotificationConsumer
  - [x] 创建 [backend/apps/notifications/backends.py](file:///Users/zhaofuqing/Documents/Developer/Caduceus/backend/apps/notifications/backends.py)：NotificationBackend(ABC) + WebSocketBackend
  - [x] 创建 [backend/apps/notifications/routing.py](file:///Users/zhaofuqing/Documents/Developer/Caduceus/backend/apps/notifications/routing.py)
  - [x] 修改 [backend/config/asgi.py](file:///Users/zhaofuqing/Documents/Developer/Caduceus/backend/config/asgi.py) 注册 WebSocket 路由

- [x] Task 4: 实现信号联动（TaskLog → Notification）
  - [x] 创建 [backend/apps/notifications/signals.py](file:///Users/zhaofuqing/Documents/Developer/Caduceus/backend/apps/notifications/signals.py)：TaskLog post_save → Notification + WebSocket push
  - [x] 修改 [backend/apps/notifications/apps.py](file:///Users/zhaofuqing/Documents/Developer/Caduceus/backend/apps/notifications/apps.py) ready() 注册信号

- [x] Task 5: 前端 WebSocket 连接 + 通知铃铛完善
  - [x] 完善 [frontend/src/stores/notifications.js](file:///Users/zhaofuqing/Documents/Developer/Caduceus/frontend/src/stores/notifications.js)：WebSocket 连接/断连/重连/标记已读
  - [x] 完善 [frontend/src/components/NotificationBell.vue](file:///Users/zhaofuqing/Documents/Developer/Caduceus/frontend/src/components/NotificationBell.vue)：点击跳转、外部关闭、相对时间
  - [x] 修改 [frontend/src/stores/auth.js](file:///Users/zhaofuqing/Documents/Developer/Caduceus/frontend/src/stores/auth.js)：login→connectWS, logout→disconnectWS

- [x] Task 6: 更新 README
  - [x] Phase 3 标记为 ✅，补充通知功能详细说明
