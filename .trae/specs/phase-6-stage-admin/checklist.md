# Checklist

- [ ] Task.current_node 字段已迁移
- [ ] 创建绑定管线任务时 current_node 自动设为首节点 ID
- [ ] 无绑定管线任务 current_node 默认为空字符串
- [ ] TaskDetail 时间轴显示已完成/进行中/未开始三种状态
- [ ] 当前阶段有"标记完成"按钮
- [ ] 点击标记完成 PATCH current_node 到下一节点
- [ ] 最后阶段标记完成后 current_node = "completed"
- [ ] 标记完成不阻塞字段编辑
- [ ] 阶段完成时创建 Notification（type=stage_completed）
- [ ] AdminPanel 用户管理：列表/新建/编辑/禁用
- [ ] AdminPanel 角色管理：CRUD
- [ ] AdminPanel 组管理：CRUD + 主管设置
- [ ] 没有控制台 error
- [ ] README.md Phase 6 条目
