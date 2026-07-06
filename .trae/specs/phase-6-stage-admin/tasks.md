# Tasks

- [ ] Task 1: Task 模型新增 current_node + 迁移
  - [ ] 修改 [backend/apps/tasks/models.py](file:///Users/zhaofuqing/Documents/Developer/Caduceus/backend/apps/tasks/models.py)：新增 `current_node = models.CharField(max_length=50, blank=True, default='')`
  - [ ] 修改 [backend/apps/tasks/api/serializers.py](file:///Users/zhaofuqing/Documents/Developer/Caduceus/backend/apps/tasks/api/serializers.py)：TaskCreateSerializer.create() 中如果绑定了管线且 current_node 为空，自动设为管线第一个节点 id
  - [ ] 迁移并验证

- [ ] Task 2: TaskDetail.vue 阶段标记交互
  - [ ] 时间轴当前阶段右侧显示"标记完成"箭头按钮
  - [ ] 点击后 PATCH task.current_node 为下一节点 id
  - [ ] 已完成的节点显示绿色实心圆点 + "已完成"标签
  - [ ] 最后一个节点标记完成后 current_node = "completed"
  - [ ] 任何阶段都可以编辑字段（软约束）

- [ ] Task 3: 阶段完成通知信号
  - [ ] 修改 [backend/apps/tasks/signals.py](file:///Users/zhaofuqing/Documents/Developer/Caduceus/backend/apps/tasks/signals.py)：监听 TaskLog post_save
  - [ ] 检测 current_node 变更 → 查找下一节点 roles → 创建 Notification（type=stage_completed）

- [ ] Task 4: AdminPanel.vue 完善
  - [ ] Tab 切换（用户管理 / 角色管理 / 组管理）
  - [ ] 用户管理：列表表格 + 新建/编辑弹窗（含角色多选）
  - [ ] 角色管理：列表表格 + 新建/编辑弹窗
  - [ ] 组管理：列表表格 + 新建/编辑弹窗（含主管选择）
  - [ ] API 调用使用已有的 adminClient（如无则从 client 新建，需管理员权限）

- [ ] Task 5: 更新 README Phase 6
  - [ ] 新增 Phase 6 条目，补充阶段标记 + 管理面板说明

# Task Dependencies
- Task 2 依赖 Task 1（需 current_node 字段）
- Task 3 依赖 Task 1
- Task 4 独立可并行
- Task 5 依赖 Task 1-4
