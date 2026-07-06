# Phase 5: Dashboard + 任务合并 + 公开分享 Spec

## Why
Phase 0-3 完成了账户体系、任务协作、管线编辑器和实时通知。Phase 5 补齐三个用户可感知的完整体验：首页仪表盘（数据总览）、角色级任务合并展示、公开分享页面。

## What Changes
- 新增 Dashboard 聚合统计 API
- 完善 Dashboard.vue 仪表盘页面（统计卡片 + 最新任务列表）
- 新增 TaskMergeGroup.vue 任务合并展示组件
- 创建 SharePage.vue 公开分享页面（无需登录）
- 任务详情页支持生成分享链接

## Impact
- Affected specs: dashboard（新增）, tasks（合并展示、分享）
- Affected code: [backend/apps/dashboard/](file:///Users/zhaofuqing/Documents/Developer/Caduceus/backend/apps/dashboard/)（新建 API）, [backend/config/urls.py](file:///Users/zhaofuqing/Documents/Developer/Caduceus/backend/config/urls.py)（激活路由）, [frontend/src/views/Dashboard.vue](file:///Users/zhaofuqing/Documents/Developer/Caduceus/frontend/src/views/Dashboard.vue)（完善）, [frontend/src/views/TaskDetail.vue](file:///Users/zhaofuqing/Documents/Developer/Caduceus/frontend/src/views/TaskDetail.vue)（分享链接）, [frontend/src/views/SharePage.vue](file:///Users/zhaofuqing/Documents/Developer/Caduceus/frontend/src/views/SharePage.vue)（新建）, [frontend/src/views/TaskList.vue](file:///Users/zhaofuqing/Documents/Developer/Caduceus/frontend/src/views/TaskList.vue)（合并展示）, [frontend/src/components/TaskMergeGroup.vue](file:///Users/zhaofuqing/Documents/Developer/Caduceus/frontend/src/components/TaskMergeGroup.vue)（新建）

## ADDED Requirements

### Requirement: Dashboard Stats API
系统 SHALL 提供仪表盘聚合统计 API，返回用户可感知的数据概览。

Dashboard 聚合指标：
- `total_tasks`：本月任务总数
- `completed_tasks`：本月已完成数
- `completion_rate`：完成率（百分比）
- `in_progress_tasks`：进行中任务数
- `resource_usage_count`：本月资源调用次数
- `recent_tasks`：最近 5 条任务摘要

#### Scenario: 管理员查看仪表盘
- **WHEN** 管理员登录后访问首页（Dashboard）
- **THEN** 显示 4 个统计卡片（任务总数、已完成、完成率、进行中）+ 最近 5 条任务列表

### Requirement: Dashboard Frontend
系统 SHALL 在首页展示统计卡片和最新任务列表。

- 卡片区：4 个卡片网格（任务总数 / 已完成 / 完成率 / 进行中），带 loading 占位动画
- 任务列表区：最近 5 条任务卡片，点击跳转 TaskDetail
- 数据来自 `/api/dashboard/stats/` 聚合接口

#### Scenario: 仪表盘数据加载
- **WHEN** 用户进入 Dashboard 页面
- **THEN** 自动调用 `/api/dashboard/stats/` 获取数据，展示统计卡片和任务列表

### Requirement: Task Merge Group Display
系统 SHALL 在任务列表页支持同一管线下关联任务的角色级合并展示。

- 在 TaskList.vue 中，当同一管线下存在关联任务（`related_tasks` 非空）时，可折叠为一个合并组
- 合并组展示管线名称 + 关联任务数量标签
- 展开后显示组内所有子任务卡片
- TaskMergeGroup.vue 组件负责合并组的渲染
- 合并为可选视图模式，不强制（用户可手动切换）

#### Scenario: 关联任务合并展示
- **WHEN** 两个及以上任务在管线配置的角色合并规则下被关联（related_tasks 非空）
- **THEN** 任务列表中以合并组形式展示，组头部显示"管线名称 + N 个任务"，可展开查看子任务

### Requirement: Public Share Page
系统 SHALL 支持通过 UUID 令牌公开分享任务进度信息，无需登录。

- 路由 `/share/:token` 不需要认证
- 后端提供公开查看接口：获取 share_token 对应任务的基本信息和公开字段
- SharePage.vue 展示管线进度、公开字段（`is_public: true`）、任务状态
- 过期检查：share_expires_at 超期时显示"分享已过期"

#### Scenario: 外部用户查看分享页
- **WHEN** 外部用户访问 `/share/:token` 链接
- **THEN** 无需登录即可看到任务的基本进度和公开字段

### Requirement: Share Link Generation
系统 SHALL 允许任务发起人和管理员在任务详情页生成/复制分享链接。

- TaskDetail.vue 顶部工具栏新增"分享"按钮
- 点击后调用 `POST /api/tasks/{id}/share/` 生成 share_token（如已有则复用）
- 弹出对话框显示完整链接 `http://domain/share/{token}`
- 支持一键复制链接 + 设置过期时间

#### Scenario: 生成分享链接
- **WHEN** 任务发起人在详情页点击"分享"按钮
- **THEN** 弹出分享对话框，显示生成的公开链接和过期时间设置
