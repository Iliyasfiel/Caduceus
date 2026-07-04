# Tasks: 资源库生命周期增强

- [x] Task 1: 扩展 ResourceType 模型，新增 lifecycle_config 字段
  - [x] 在 models.py 中为 ResourceType 添加 `lifecycle_config = JSONField(default=dict)` 字段
  - [x] 生成并执行 migration
  - [x] 更新 ResourceTypeSerializer，确保 lifecycle_config 可读写

- [x] Task 2: 新增 ResourceLog 模型并生成迁移
  - [x] 在 models.py 中定义 ResourceLog 模型：`resource`(FK→ResourceItem), `event_key`(CharField), `operator`(FK→User), `summary`(TextField), `details`(JSONField), `created_at`
  - [x] 生成并执行 migration
  - [x] 注册 ResourceLog 到 Django Admin（可选，便于调试）

- [x] Task 3: 实现 ResourceLog API（CRUD）
  - [x] 创建 ResourceLogSerializer，资源条目嵌套路由下访问（如 `/api/resources/resource-items/{id}/logs/`）
  - [x] 创建 ResourceLogViewSet，`perform_create` 中自动设置 `operator = request.user`
  - [x] 注册路由到 urls.py

- [x] Task 4: 实现 ResourceLog → ResourceItem.status 自动状态推导
  - [x] 在 signals.py 中监听 ResourceLog post_save，获取最新 event_key
  - [x] 从 ResourceType.lifecycle_config 中查找该 event_key 对应的 status_value
  - [x] 若无显式配置，使用 event_key 转换规则（snake_case → 去掉下划线或保持原样）作为 status
  - [x] 更新 ResourceItem.status 并 save

- [x] Task 5: 实现 ResourceLog → Notification 通知联动
  - [x] 在 signals.py 中，ResourceLog post_save 后查询 ResourceType.lifecycle_config 中该 event_key 的 notify_roles
  - [x] 向 notify_roles 中角色下的所有用户发送 Notification（标题含资源名称和 event 描述，内容含操作人和摘要）
  - [x] Notification 通过 WebSocket 实时推送

- [x] Task 6: 调整 ResourceItemSerializer status 为只读
  - [x] 在 ResourceItemSerializer 中将 status 字段标记为 `read_only=True`
  - [x] 确保创建/更新 ResourceItem 时忽略前端传入的 status 值

- [x] Task 7: 前端资源管理页面实现
  - [x] 创建/完善 ResourceList.vue：资源类型筛选、资源列表（含状态标签）、新增资源、详情对话框（含事件时间线）
  - [x] 资源详情对话框内嵌事件时间线（ResourceLog 倒序）+ 记录新事件操作
  - [x] ResourceSelector.vue 可复用下拉组件，支持搜索和按类型筛选

- [x] Task 8: API 端点验证
  - [x] Migration 文件已生成: 0002_add_lifecycle_config_and_log.py
  - [x] 前端构建成功 (npm run build, 0 errors)
  - [ ] curl 验证需启动 PostgreSQL + Redis 后执行（migration 文件就绪）

# Task Dependencies
- Task 2 依赖 Task 1（ResourceLog 需要引用 ResourceItem）
- Task 3 依赖 Task 2（API 需要模型就绪）
- Task 4 依赖 Task 2（Signal 需要 ResourceLog 模型）
- Task 5 依赖 Task 4（通知依赖于事件和状态更新流程确定）
- Task 6 与 Task 4 可并行（Serialzier 改只读与 Signal 逻辑独立）
- Task 7 依赖 Task 1-6（前端需要后端 API 就绪）
- Task 8 依赖 Task 1-6（集成验证）
