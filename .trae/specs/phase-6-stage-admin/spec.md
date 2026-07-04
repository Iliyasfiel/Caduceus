# Phase 6: 管线阶段标记 + 管理面板 Spec

## Why
两个核心缺失功能：管线阶段标记完成使得任务进度可视化（当前时间轴仅展示结构，无交互），管理面板使得管理员可以管理用户/角色/组（当前 AdminPanel.vue 为占位）。

## What Changes

### Feature A: 管线阶段标记完成
- Task 模型新增 `current_node`（当前阶段节点 ID）字段
- TaskDetail.vue 时间轴支持点击标记阶段完成（高亮已完成 + 标记下一阶段为当前）
- 标记阶段不阻塞信息修改（软约束）
- 标记完成后通过 signal 向下一阶段角色创建通知

### Feature B: AdminPanel 管理面板
- 完善 AdminPanel.vue（Tab 切换：用户管理 / 角色管理 / 组管理）
- 用户管理：列表 + 新建/编辑/禁用 + 角色分配
- 角色管理：CRUD + 角色类型配置
- 组管理：CRUD + 设置主管

## Impact
- Affected specs: tasks（current_node 字段 + 阶段标记交互）, accounts（AdminPanel）
- Affected code: [backend/apps/tasks/models.py](file:///Users/zhaofuqing/Documents/Developer/Caduceus/backend/apps/tasks/models.py)（新增 current_node）, [frontend/src/views/TaskDetail.vue](file:///Users/zhaofuqing/Documents/Developer/Caduceus/frontend/src/views/TaskDetail.vue)（阶段标记交互）, [backend/apps/tasks/signals.py](file:///Users/zhaofuqing/Documents/Developer/Caduceus/backend/apps/tasks/signals.py)（完成通知）, [frontend/src/views/AdminPanel.vue](file:///Users/zhaofuqing/Documents/Developer/Caduceus/frontend/src/views/AdminPanel.vue)（管理面板）

## ADDED Requirements

### Requirement A1: Task.current_node 字段
系统 SHALL 在 Task 模型中新增 `current_node` 字段存储当前所在阶段的节点 ID。

- `current_node = models.CharField(max_length=50, blank=True, default='')`
- 创建绑定管线的任务时，默认值为管线第一个节点的 ID
- 无绑定管线时默认空字符串

#### Scenario: 创建带管线的任务
- **WHEN** 用户创建绑定管线的任务
- **THEN** current_node 自动设为管线 nodes 数组第一个节点 id

### Requirement A2: 阶段标记交互（TaskDetail.vue）
系统 SHALL 在任务详情页的管线阶段时间轴上支持标记阶段完成。

- 已完成阶段（小于 currentStageIndex）的节点显示"已完成"标记（实心圆点 + 绿色）
- 当前阶段显示为高亮的"进行中"（紫色圆点 + pulse 动画）
- 点击当前阶段右侧">"箭头按钮标记完成：
  - PATCH `/api/tasks/tasks/{id}/` { current_node: nextNodeId }
  - 标记后时间轴自动更新，当前阶段前进到下一节点
  - 最后一个节点标记完成后 current_node 设为 `completed`
- 已完成阶段的连线变为实线
- 不阻塞信息修改（任何阶段都可以编辑字段）

#### Scenario: 参与者标记阶段完成
- **WHEN** 参与者在阶段时间轴上点击当前阶段右侧的"标记完成"按钮
- **THEN** 该阶段圆点变为绿色已完成，下一阶段圆点高亮为进行中，保存后时间轴自动刷新

### Requirement A3: 阶段完成通知
系统 SHALL 在阶段被标记完成后，向下一阶段配置的角色用户发送通知。

- 修改 [tasks/signals.py](file:///Users/zhaofuqing/Documents/Developer/Caduceus/backend/apps/tasks/signals.py)：监听 TaskLog post_save，当 current_node 变更时
- 查找下一节点在管线 roles 中配置的角色
- 向这些角色的用户创建 Notification（type=stage_completed）

#### Scenario: 下游参与者收到通知
- **WHEN** 发起人标记"准备阶段"完成，下一阶段为"执行阶段"（配置角色为"讲解员"）
- **THEN** 拥有"讲解员"角色的所有用户收到"阶段已完成，可以开始了"通知

### Requirement B1: 管理面板用户管理
系统 SHALL 在 AdminPanel.vue 中提供用户管理功能。

- Tab 切换：用户管理 / 角色管理 / 组管理
- 用户列表表格：用户名、邮箱、是否启用、操作（编辑/禁用）
- 新建/编辑弹窗：用户名、密码、邮箱、is_active、角色分配（多选复选框）
- 创建用户调用 POST /api/accounts/users/，更新调用 PATCH /api/accounts/users/{id}/

### Requirement B2: 管理面板角色管理
系统 SHALL 在 AdminPanel.vue 中提供角色管理功能。

- 角色列表：名称、role_type（initiator/executor/admin）、描述、操作
- 新建/编辑弹窗：名称、role_type 下拉选择、描述
- CRUD 调用 /api/accounts/roles/

### Requirement B3: 管理面板组管理
系统 SHALL 在 AdminPanel.vue 中提供组管理功能。

- 组列表：名称、描述、主管（显示用户名）、操作
- 新建/编辑弹窗：名称、描述、主管选择（下拉选用户）
- CRUD 调用 /api/accounts/groups/

#### Scenario: 管理员新建角色
- **WHEN** 管理员在 AdminPanel 切换到"角色管理" Tab，点击"新建角色"
- **THEN** 弹出表单填写名称/类型/描述，提交后角色列表刷新
