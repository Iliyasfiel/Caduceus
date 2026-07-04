# Phase 2: Pipeline Editor Spec

## Why
Phase 1 完成了用户/角色体系与任务协作基础功能，但管理员还无法在线定义任务的信息流结构。管线编辑器是 Caduceus 的核心差异化功能——让管理员通过拖拽可视化编排来定义"谁在什么阶段需要什么信息"，无需二次开发即可适应不同协作场景。

## What Changes
- **BREAKING**: Pipeline 模型从占位结构重构为 V2 设计：`definition` 字段替换为 `nodes` + `edges` JSON 结构
- **BREAKING**: PipelineInstance 模型从占位结构重构，移除 `execution_history`，status choices 简化为 `running` / `completed`
- 新增 Pipeline API（serializer + ViewSet + 路由）
- 新增 PipelineCanvas.vue（Vue Flow 画布组件，单一节点类型）
- 重构 PipelineEditor.vue 为完整管线编辑器页面
- 前端 pipeline.js API 层适配新的后端模型结构

## Impact
- Affected specs: accounts, tasks（已有 FK 引用 pipeline）
- Affected code: [backend/apps/pipeline/models.py](file:///Users/zhaofuqing/Documents/Developer/Caduceus/backend/apps/pipeline/models.py), [backend/apps/pipeline/api/](file:///Users/zhaofuqing/Documents/Developer/Caduceus/backend/apps/pipeline/api/), [frontend/src/views/PipelineEditor.vue](file:///Users/zhaofuqing/Documents/Developer/Caduceus/frontend/src/views/PipelineEditor.vue), [frontend/src/api/pipeline.js](file:///Users/zhaofuqing/Documents/Developer/Caduceus/frontend/src/api/pipeline.js)

## ADDED Requirements

### Requirement: Pipeline Model V2
系统 SHALL 支持管线模板，定义信息流结构。管线画布只有一种视觉元素——任务节点，每个节点内部配置该阶段的字段、参与角色和资源类型。

Pipeline SHALL 包含：
- `name`, `description`: 文本字段
- `nodes`: JSONB 数组，每个节点包含 `id`, `label`, `fields_config`, `roles`, `resource_types`
- `edges`: JSONB 数组，表达阶段推进方向
- `created_by`: FK → User
- `created_at`, `updated_at`: 时间戳

#### Scenario: 创建管线
- **WHEN** 管理员在管线编辑器创建新管线
- **THEN** POST /api/pipelines/ 保存管线，nodes/edges 持久化为 JSONB

#### Scenario: 节点配置
- **WHEN** 管理员拖入任务节点并配置字段、角色、资源类型
- **THEN** nodes[].fields_config 包含字段定义（key, label, type, priority_roles, is_public），nodes[].roles 包含参与角色及合并配置，nodes[].resource_types 包含关联资源类型 ID 列表

### Requirement: PipelineInstance Model
系统 SHALL 支持管线运行实例，与任务一对一关联。

PipelineInstance SHALL 包含：
- `pipeline`: FK → Pipeline
- `task`: OneToOne → Task
- `current_node`: 当前阶段节点 ID（参考标记，不锁定）
- `status`: running / completed
- `created_at`, `updated_at`: 时间戳

#### Scenario: 任务绑定管线
- **WHEN** 创建任务时选择绑定一个管线
- **THEN** 自动创建对应的 PipelineInstance，status=running，current_node 指向第一个节点

### Requirement: Pipeline CRUD API
系统 SHALL 提供管线模板的完整 CRUD API。

- GET /api/pipelines/ — 管线列表
- POST /api/pipelines/ — 创建管线
- GET /api/pipelines/{id}/ — 管线详情
- PUT/PATCH /api/pipelines/{id}/ — 更新管线
- DELETE /api/pipelines/{id}/ — 删除管线（仅创建者或管理员）

#### Scenario: 管理员创建管线
- **WHEN** 管理员 POST 包含 nodes 和 edges 的完整管线数据
- **THEN** 返回 201，Pipeline 记录创建成功

### Requirement: Vue Flow Pipeline Canvas
系统 SHALL 提供可视化管线编辑器画布。画布上只有"任务节点"一种视觉元素，左侧面板显示节点配置选项（无需节点类型选择），右侧面板编辑选中节点的字段、角色、资源类型。

#### Scenario: 添加节点
- **WHEN** 用户从左侧面板点击"添加任务节点"
- **THEN** 画布中出现新的任务节点，右侧面板显示该节点的配置表单

#### Scenario: 连接节点
- **WHEN** 用户从一个节点的输出端口拖线到另一个节点的输入端口
- **THEN** 建立连线，edges 数组新增一条连接记录

#### Scenario: 编辑节点字段配置
- **WHEN** 用户在右侧面板添加字段定义（key, label, type, priority_roles, is_public）
- **THEN** 对应节点的 fields_config 更新，字段仅归属于任务而非节点

### Requirement: Pipeline Editor Page
系统 SHALL 提供完整的管线编辑器页面，支持保存和加载管线。

#### Scenario: 保存管线
- **WHEN** 用户在编辑器中完成管线配置并点击保存
- **THEN** PUT/PATCH 到后端 API，前端显示保存成功提示

#### Scenario: 加载已有管线
- **WHEN** 用户从管线列表进入编辑已有管线
- **THEN** GET 管线数据后，画布渲染 nodes 对应节点和 edges 对应连线

## REMOVED Requirements

### Requirement: Old Pipeline definition field
**Reason**: V2 设计用 `nodes` + `edges` 替代旧的 `definition` 单一 JSONB 字段，结构更清晰
**Migration**: 迁移脚本将删除 `definition` 字段，新增 `nodes` 和 `edges` 字段

### Requirement: Old PipelineInstance execution_history
**Reason**: V2 设计中实例仅作运行标记，不需要执行历史（任务已有 TaskLog）
**Migration**: 迁移脚本将删除 `execution_history` 字段，简化 status choices
