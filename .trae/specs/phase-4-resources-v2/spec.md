# Phase 4: Resources 前端开发 Spec

## Why
后端 API（ResourceType/ResourceItem/ResourceLog）和数据模型（含 lifecycle_config + 生命周期事件日志）已在另一个任务中完成升级，但前端仅搭建了 API 调用层，ResourceList.vue 仍为占位页面，ResourceSelector.vue 未创建，任务详情页未集成资源关联功能。

## What Changes
- 完善 ResourceList.vue（资源类型管理 + 资源条目 CRUD + 生命周期日志查看）
- 新建 ResourceSelector.vue（嵌入 TaskDetail 关联资源）
- 修改 TaskDetail.vue 右侧面板集成 ResourceSelector + 已关联资源列表
- 后端 api/urls 无需修改（已就绪）

## Impact
- Affected code: [frontend/src/views/ResourceList.vue](file:///Users/zhaofuqing/Documents/Developer/Caduceus/frontend/src/views/ResourceList.vue), [frontend/src/components/ResourceSelector.vue](file:///Users/zhaofuqing/Documents/Developer/Caduceus/frontend/src/components/ResourceSelector.vue)（新建）, [frontend/src/views/TaskDetail.vue](file:///Users/zhaofuqing/Documents/Developer/Caduceus/frontend/src/views/TaskDetail.vue)

## ADDED Requirements

### Requirement: ResourceList 管理页面
系统 SHALL 提供资源库管理页面，支持资源类型管理与资源条目 CRUD。

- 顶部：Tab 切换"资源条目管理"/"资源类型管理"
- 资源类型管理 Tab：列表展示（名称、描述、图标、字段数量、是否启用），支持新建/编辑弹窗
- 资源条目管理 Tab：左侧类型列表 + 右侧选中类型下条目表格（名称、状态、字段值摘要），支持新建/编辑/删除 + 操作日志入口

#### Scenario: 管理员管理资源类型
- **WHEN** 管理员进入资源库，切换到"资源类型管理" Tab
- **THEN** 显示已有资源类型列表，可新建"车辆"类型并定义图标

#### Scenario: 管理员管理资源条目
- **WHEN** 管理员在"资源条目管理"中选中"酒店"类型
- **THEN** 右侧展示所有酒店资源，可新建"XX大酒店"并填写 field_schema 对应的字段值

### Requirement: ResourceSelector 组件
系统 SHALL 在任务详情页提供资源关联选择器。

- 下拉选择资源类型筛选可用资源条目
- 支持多选资源条目，已关联的标记"已关联"
- 展示当前任务已关联资源列表（名称 + 类型 + 状态标签）

#### Scenario: 任务关联资源
- **WHEN** 用户在任务详情页 ResourceSelector 中选中"酒店"类型下的"XX大酒店"并确认
- **THEN** 资源条目出现在任务关联列表中，调用 PATCH /api/tasks/tasks/{id}/ 关联资源

### Requirement: TaskDetail 集成 ResourceSelector
系统 SHALL 在任务详情页右侧面板显示已关联资源 + 资源选择器入口。

- 右侧面板新增"关联资源"区域
- 已关联资源列表展示（名称 + 类型 + 状态）
- 点击"+ 关联资源"弹出 ResourceSelector 模态选择器
