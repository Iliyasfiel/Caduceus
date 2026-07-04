# Checklist: 资源库生命周期增强

- [x] ResourceType 模型包含 `lifecycle_config` JSONField，默认值为空 dict
- [x] ResourceTypeSerializer 可正确序列化/反序列化 lifecycle_config
- [x] ResourceType API 的 POST/PATCH 支持写入 lifecycle_config
- [x] ResourceLog 模型已创建并迁移，包含 resource(FK)、event_key、operator(FK)、summary、details(JSONField)、created_at 字段
- [x] ResourceLogViewSet 可正常 CRUD，创建时 operator 自动设为当前用户
- [x] ResourceLog 创建后 ResourceItem.status 自动更新为对应 status_value
- [x] ResourceItem.status 为生命周期配置中 event_key 映射的值，未配置时使用 event_key 自身作为 status
- [x] ResourceItemSerializer 的 status 字段为 read_only，不接受前端传入
- [x] ResourceLog 创建时，根据 lifecycle_config 的 notify_roles 自动生成 Notification
- [x] Notification 通过 WebSocket 实时推送给对应角色下的用户
- [x] 未配置 notify_roles 的事件不生成通知
- [x] ResourceItem 详情 API 返回关联的 ResourceLog 列表（按时间倒序）
- [x] 前端 ResourceList.vue 展示资源类型筛选、列表、状态标签
- [x] 前端资源详情对话框 + 事件时间线 + 记录新事件
- [x] 前端 ResourceSelector.vue 可嵌入 TaskDetail 关联资源
- [ ] 所有 API 端点 curl 验证通过（需启动 PostgreSQL + Redis 后执行，migration 文件已就绪）
