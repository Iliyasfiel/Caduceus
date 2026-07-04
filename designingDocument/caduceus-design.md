# Caduceus 设计文档

> 项目名称：Caduceus
> 日期：2026-06-30（V2 更新）
> 状态：设计稿

---

## 一、愿景

轻量级、开源的协同工作信息枢纽。聚焦角色间的信息流转与共享，以可视化管线编辑器为核心特色，让管理员能够在线创建和修改流程而无需二次开发。

**核心理念：**
- 流程是协作的加速器，而非限制协作的锁链
- **信息全透明，操作有边界** — 所有协作者可查看任务的全部信息，但谁能执行什么操作由角色和权限控制
- 系统服务于协作，而非用流程锁死团队

## 二、目标场景

首期对标 **50 人以内的小团队**，覆盖行政接待、活动管理、会议协调等多角色分工协作场景。

典型场景特征：
- 信息渐进式明确（发起时信息不全，后续补充）
- 频繁的中途变更（行程调整、人员增减）
- 变更需要即时传达给所有相关角色
- 资源（酒店、餐厅、车辆等）与任务联动
- 多角色并行协作（讲解员、接待、会务、司机等）

## 三、技术栈

| 层级 | 选型 | 说明 |
|------|------|------|
| 前端框架 | Vue 3 + Composition API | SPA 单页应用 |
| 构建工具 | Vite | 开发/生产构建 |
| 状态管理 | Pinia | 前端状态管理 |
| 管线编辑器 | Vue Flow | 基于 Vue 3 的节点编辑器 |
| 后端框架 | Django 5 | Python Web 框架 |
| REST API | Django REST Framework | API 层 |
| 实时通信 | Django Channels + WebSocket | 实时推送 |
| 数据库 | PostgreSQL 16 | JSONB 支撑灵活字段 |
| 消息/缓存 | Redis 7 | Channels channel layer + 缓存 |
| 部署 | Docker Compose | Nginx + Django + PG + Redis |

消息队列：首期不引入。未来需要时通过 django-rq 基于已有 Redis 扩展。

## 四、系统架构

### 4.1 整体架构

前后端分离架构。

- **Vue 3 SPA** 作为前端，通过 REST API 和 WebSocket 与后端通信
- **Django** 提供 REST API（DRF）+ WebSocket（Channels）
- **PostgreSQL** 存储数据，JSONB 字段支撑灵活字段和自定义配置
- **Redis** 作为 Channels 的 channel layer 和缓存层

数据流：
```
用户浏览器 ←→ REST API (HTTP) ←→ Django ←→ PostgreSQL
用户浏览器 ←→ WebSocket ←→ Django Channels ←→ Redis
```

### 4.2 项目结构（Monorepo）

```
caduceus/
├── backend/                    # Django 项目根目录
│   ├── config/                 # Django settings
│   ├── apps/
│   │   ├── accounts/           # 用户/角色/权限
│   │   ├── tasks/              # 任务协作模块
│   │   ├── pipeline/           # 管线编辑器引擎
│   │   ├── resources/          # 资源库模块
│   │   ├── notifications/      # 站内通知
│   │   └── dashboard/          # 基础数据统计
│   ├── docker/                 # Docker 配置
│   └── requirements.txt
├── frontend/                   # Vue 3 项目
│   ├── src/
│   │   ├── views/              # 页面级组件
│   │   ├── components/         # 通用组件
│   │   ├── stores/             # Pinia 状态管理
│   │   └── api/                # API 调用层
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 五、模块详细设计

### 5.1 accounts — 用户/角色/权限

**设计理念：** 从固定的三类角色（发起人/执行人/管理员）升级为灵活的角色分配体系。

**User**（Django AbstractUser 扩展）
- `username` / `email` / `password`
- `profile: JSON` — 扩展信息（联系方式等）

**Role**（角色定义，由超级管理员预设）
- `name: str` — 角色名称（如"讲解员"、"接待员"、"会务"、"司机"）
- `role_type: str` — `initiator` / `executor` / `admin`
- `description: str`

**RoleAssignment**（用户-角色关联）
- `user: FK → User`
- `role: FK → Role`
- `group: FK → Group`（所属组，可选）
- `is_supervisor: boolean` — 是否是该组的 Supervisor（主管）

**Group**（组/业务小组）
- `name: str` — 如"讲解组"、"接待组"、"会务组"、"车队"
- `description: str`

**权限边界：**

| 操作 | 发起人权限 | 执行人 | 主管（本组） | 管理员 |
|------|-----------|--------|------------|--------|
| 查看任务全部信息 | ✅ | ✅ | ✅ | ✅ |
| 编辑任务信息 | ✅ 自己发起 | ✅ 反馈进度 | ✅ 本组任务 | ✅ 全部 |
| 分配/改派执行人 | ✅ 自己发起 | 🚫 | ✅ 本组任务 | ✅ 全部 |
| 确认完成任务 | ✅ 自己发起 | ✅ 自己的 | ✅ 本组任务 | ✅ 全部 |
| 关闭/取消任务 | ✅ 自己发起 | 🚫 | ✅ 本组任务 | ✅ 全部 |
| 创建/修改管线 | 🚫 | 🚫 | 🚫 | ✅ |
| 管理用户/角色 | 🚫 | 🚫 | 🚫 | ✅ |

关键规则：
- 一个用户可以拥有多个角色权限（如同时拥有发起权限 + 司机执行人角色）
- 信息对协作者全透明，操作权限由角色控制
- 主管只能管理自己组成员的任务分配，不能干涉其他组

### 5.2 tasks — 任务协作（核心模块）

**Task**
- `title` / `description`
- `status: str` — `draft` / `pending` / `in_progress` / `completed` / `cancelled`
- `creator: FK → User`（发起人/创建者）
- `assignee_type: str` — `direct`（指定执行人）/ `pool`（任务池抢单制）
- `assignee: FK → User`（指定执行人，当 assignee_type=direct 时）
- `pipeline: FK → Pipeline`（关联的管线，可选）
- `fields: JSONB` — 灵活字段，每个字段可以标记优先级角色
  - 例：`[{"key":"pickup_location","label":"上车地点","value":"A大厦","priority_roles":["司机"]}, {"key":"tour_duration","label":"参观时长","value":"1小时","priority_roles":["讲解员"]}]`
- `resources: M2M → ResourceItem` — 关联的资源库条目
- `tags: JSON` — 任务标签（如["接待","紧急"]），可选
- `related_tasks: M2M → Task` — 关联任务（多个任务之间可建立关联关系，用于角色级合并展示）
- `merged_groups: JSONB` — 当前用户的合并展示配置（按角色保存用户自选的聚合设置）
- `share_token: UUID` — 公开分享的令牌，可选
- `share_fields: JSON` — 公开分享时展示哪些字段，可选
- `share_expires_at: datetime` — 分享链接过期时间，可选
- `created_at` / `updated_at`

**TaskAssignment**（任务执行人关联，支持多种分配模式）
- `task: FK → Task`
- `user: FK → User`
- `role: FK → Role`（该执行人以什么角色参与此任务）
- `status: str` — `pending` / `accepted` / `completed`
- `accepted_at: datetime`（抢单任务的接取时间）

**TaskComment**（协作评论）
- `task: FK → Task`
- `author: FK → User`
- `content: text`
- `attachments: File[]`
- `created_at`

**TaskLog**（变更历史）
- `task: FK → Task`
- `operator: FK → User`
- `action: str` — `created` / `updated` / `status_changed` / `assigned` / ...
- `changes: JSONB` — 变更详情（旧值→新值的 diff）
- `created_at`

#### 角色感知展示

任务详情页采用**共用结构 + 字段按角色优先级排序**的方式展示信息：
- 所有参与角色共享同页面结构
- 标记了"优先级角色"的字段，对该角色使用者置顶展示
- 例如司机角色访问任务时，车辆信息和派车时间显示在页面最上方

任务列表页支持"只看与我相关"的过滤选项。

#### 角色级任务聚合（合并展示）

**问题场景：** 同一执行角色（如讲解员）同时段承接多个任务，在角色视角下希望合并为一个工作单元；但其他角色（如保安）不受影响，仍看到独立任务。

**实现方式：**
- 任务之间可建立**关联关系**（related_tasks M2M 字段），由执行人在任务详情页中手动发起关联
- 关联条件：两个任务绑定同一管线类型，且当前执行人以同一角色参与两个任务
- 发起关联后，该执行人可在任务列表中**选择合并展示**——将他负责的多个关联任务聚合为一个条目，展开可查看子任务详情
- 合并展示仅影响该执行人的个人视图，不影响其他角色的任务列表
- 不同管线的任务之间不产生关联需求（如接待管线与保洁管线的任务无需关联）

**配置位置：** 合并展示的默认规则在**管线编辑器的角色配置**中设定，同类管线的任务在同类角色视角上应有类似的视图需求。

#### 公开分享页面

通过生成 UUID 令牌的方式创建公开分享链接：
- 链接格式：`https://caduceus.example.com/share/<uuid>`
- 无需登录即可访问
- 只展示预设字段和进度信息
- 支持设置过期时间

### 5.3 pipeline — 可视化管线编辑器

**设计理念：管线定义的是信息流，而非工作流。**

传统工作流引擎（如 n8n、Activiti）关注的是"数据按节点顺序流转、任务自动执行"——这适合自动化场景。
Caduceus 的管线关注的是"信息如何结构化、谁在什么时候需要什么信息"——这适合**人**协作的场景。

关键原则：
- 管线是**结构指引**而非**执行锁链** — 不会因为流程而未完成而阻塞信息修改
- 信息始终**实时共享** — 任何角色对任务信息的修改即时同步给所有参与者
- 节点顺序是**信息依赖的软提示**而非硬约束 — 如"建议先确认人数再安排车辆"，但修改人数时车辆安排不受影响

#### 管线组成

画布上只有一种视觉元素——**任务节点**。每个任务节点代表任务的一个阶段，其内部配置了该阶段涉及的角色、字段和资源。节点之间通过连线表达阶段推进关系。

```
管线示意图："客户接待"

┌─ 节点A: 前期准备 ──────────┐    ┌─ 节点B: 现场接待 ──────────┐
│  字段：客户信息（公共）      │───→│  字段：派车信息（司机优先）  │
│  角色：发起人              │    │       参观路线（讲解员优先）  │
│  资源：（无）              │    │  角色：讲解员、司机         │
└────────────────────────────┘    │  资源：酒店、车辆          │
                                   └────────────────────────────┘
```

#### Pipeline（管线/流程模板）

- `name` / `description`
- `nodes: JSONB` — 任务节点数组，每个节点包含：
  - `id` — 节点标识
  - `label` — 节点名称（如"前期准备"、"现场接待"）
  - `fields_config` — 该阶段涉及的字段定义，每个字段可标记 `priority_roles:[]`（对该角色优先展示）
  - `roles` — 该阶段参与的角色列表，每个角色的配置可包含：
    - `role_id` — 引用的角色 ID
    - `merge_default` — 该角色在任务列表中是否默认合并展示关联任务
    - `merge_time_window` — 合并展示的时间窗口（如 30 分钟内到达的关联任务自动建议合并）
  - `resource_types` — 该阶段需要关联的资源类型列表
- `edges: JSONB` — 节点间连线（表达阶段推进方向）
- `created_by: FK → User`

**PipelineInstance**（管线运行实例）
- `pipeline: FK → Pipeline`
- `task: FK → Task`（一对一关联）
- `current_node: str` — 当前所处的节点 ID（参考性标记，不锁定其他节点）
- `status: str` — `running` / `completed`

#### 字段共享规则

在管线中定义的字段归属于**任务本身**，而非某个节点：
- 一个字段可以在多个节点中引用
- 字段值全局唯一，任何节点中修改立即同步到所有节点
- 字段可标记 `priority_roles`，表示该字段对哪些角色优先展示
- 部分字段可选择不关联任何角色，即**公共字段**，对所有参与者平等展示

#### 节点连接与阶段推进

- 连线表达"阶段推进方向"——提供一个时间轴式的进度参考
- 当一个节点中的主要工作时长完成时，参与者可手动标记该阶段完成
- 标记完成后，下游节点的参与者收到提示"可以开始了"
- **标记阶段完成不阻塞信息修改**——即使标记了"完成"，信息仍然可以被修改并同步

#### 节点类型

画布上只有"任务节点"一种类型，但配置不同的节点可起到不同作用：

| 概念 | 对应配置方式 |
|------|------------|
| 发起阶段 | 第一个节点，配置发起人角色和初始字段 |
| 执行阶段 | 中间节点，配置执行人角色和所需字段/资源 |
| 确认/完成 | 最后一个节点，确认者标记完成 |

管线模板与任务实例分离：管理员编辑模板不影响正在运行的任务实例。

### 5.4 resources — 资源库

设计理念：资源库延续管线编辑的用户自定义思想——管理员不仅定义字段结构，还定义生命周期事件类型。资源状态由事件日志自动推导，事件与通知系统联动。不预置固定业务字段（如"入库时间"、"使用寿命"），而是让用户通过自定义字段和自定义事件自由建模。

**ResourceType**（资源类型，由管理员定义）
- `name: str` — 如"酒店"、"餐厅"、"车辆"、"灯具"
- `icon: str` — 前端展示图标
- `field_schema: JSONB` — 定义该资源类型的标准字段结构
  - 例：`[{"key":"power","label":"功率(W)","type":"number"}, {"key":"brand","label":"品牌","type":"text"}]`
- `lifecycle_config: JSONB` — 定义该资源类型的生命周期事件及通知规则
  - 例：
    ```json
    {
      "events": [
        {"key": "purchase", "label": "入库", "notify_roles": ["管理员"]},
        {"key": "lend_out", "label": "外借", "notify_roles": ["管理员", "检修人员"]},
        {"key": "return", "label": "归还", "notify_roles": ["管理员"]},
        {"key": "maintenance", "label": "检修", "notify_roles": ["管理员", "检修人员"]},
        {"key": "scrap", "label": "报废", "notify_roles": ["管理员"]}
      ]
    }
    ```
  - 每个 event 可配置 `status_value`（可选，不配则用 event_key 自身作为 status 值）
- `is_active: boolean`

**ResourceItem**（资源条目）
- `resource_type: FK → ResourceType`
- `name: str`
- `field_values: JSONB` — 根据 field_schema 存储的字段值
  - 例：`{"power": 200, "brand": "雅江光电"}`
- `status: str` — 由最新 ResourceLog.event_key 自动推导，只读
  - 如 latest event_key="lend_out" → status="lent_out"
  - 管理员可通过 lifecycle_config 自定义 status_value 映射
- `location: str` — 位置（可选）
- `creator: FK → User`

**ResourceLog**（资源事件日志，新增）
- `resource: FK → ResourceItem`（关联资源）
- `event_key: str` — 对应 lifecycle_config 中的事件 key（如 "lend_out"）
- `operator: FK → User`（操作人）
- `summary: str` — 事件摘要（如"借给活动组用于年会"）
- `details: JSONB` — 自由扩展详情（如 `{"借用人":"张三","预计归还":"2026-07-10"}`）
- `created_at`

创建 ResourceLog 后自动：
1. 更新 `ResourceItem.status` 为该 event_key 对应的状态
2. 查询 `lifecycle_config` 中该事件的 `notify_roles`，向对应角色用户发送 Notification

**ResourceBooking**（资源预约/占用，后续实现）
- `resource: FK → ResourceItem`
- `task: FK → Task`
- `start_time` / `end_time`
- `status: str` — `pending` / `confirmed` / `released`

资源字段类型可扩展：首批支持 text、textarea、number、select、multi_select、date、phone、url、image、file、boolean。

### 5.5 notifications — 站内通知

**Notification**
- `recipient: FK → User`
- `type: str` — `task_assigned` / `task_updated` / `resource_changed` / `comment_added` / `task_overtime` / ...
- `title` / `content`
- `link: str` — 点击跳转链接
- `is_read: boolean`
- `created_at`

通知触发场景：
- 任务创建/变更 → 通知相关参与人
- 任务被指派 → 通知执行人
- 任务池长时间无人接取 → 通知主管/管理员
- 有新的评论 → 通知任务参与人
- 资源状态变化 → 通知相关任务参与人

采用适配器模式预留扩展：`NotificationBackend` 抽象基类，首期实现 WebSocketBackend，预留 EmailBackend 和 WebhookBackend。

### 5.6 dashboard — 基础数据统计

首期只做基础统计卡片（聚合查询）：
- 本月任务总数 / 已完成数 / 完成率
- 资源调用次数
- 进行中的任务数
- 各角色组的任务量统计
- 超时任务数

未来可扩展自定义看板配置。

## 六、部署方案

### Docker Compose 服务拓扑

```
services:
  nginx:       反向代理（前端静态资源 + API 路由）
  backend:     Django (Gunicorn REST + Daphne WebSocket)
  frontend:    Vue 3 构建产物（Nginx 静态服务）
  postgres:    PostgreSQL 16
  redis:       Redis 7（Channels + 缓存）
```

启动方式：
```bash
# 开发
docker compose up -d postgres redis

# 生产（一键部署）
docker compose -f docker-compose.prod.yml up -d
```

## 七、性能评估

对标峰值：日任务 200 个、日变更操作 500 次、50 人同时在线。

| 维度 | 评估 | 说明 |
|------|------|------|
| 数据库写入 | 🟢 无压力 | PG 每秒可处理数千次写入 |
| JSONB 查询 | 🟢 无压力 | GIN 索引支撑高效查询 |
| WebSocket 推送 | 🟢 无压力 | Channels + Redis 成熟方案 |
| 管线编辑器 | 🟢 无压力 | 典型流程 < 10 节点 |
| 年数据量 | 🟢 无压力 | ~3GB / 年，PG 轻松承载 |

首期无需任何特殊性能优化。

## 八、尚未纳入但已考虑的方向

以下功能在讨论中被提及，但首期不纳入，留待后续版本：

| 方向 | 说明 |
|------|------|
| 外部 API 对接 | 首期保留 REST API 可用性，但外部系统集成在后续版本实现 |
| 任务分组/标签 | 基础 tags 字段已预留，但标签管理和筛选在后续版本完善 |
| 通知渠道扩展 | 适配器模式已预留，微信/邮件等通知在后续版本接入 |
| 公开分享页自定义 | 分享页的基础机制已设计，丰富程度在后续版本增强 |

## 九、AI 辅助开发优化

### 9.1 项目规范文件

在项目根目录创建 `.trae/rules/project_rules.md`，记录全局约定：
- 技术栈：Django 5 + DRF + Vue 3 (Composition API + `<script setup>`) + PostgreSQL 16
- 后端使用 Django ORM、DRF ViewSet + Serializer 模式
- 前端使用 Pinia 状态管理、Axios HTTP 调用
- 数据库迁移使用 `makemigrations` / `migrate`
- 命名规范、代码风格、目录结构等

### 9.2 代码注释规范

为确保代码的可维护性和 AI 协作的连续性，所有代码文件必须遵循以下注释规范：

- **每个文件头部**必须包含简短的注释，说明该文件的用途、所属模块和核心职责
- **每个核心代码段**（函数、类方法、关键逻辑分支）必须添加中文注释，解释其作用
- 注释应说明"为什么这么做"而非"做了什么"（代码本身应能表达"做了什么"）

示例：
```python
# apps/tasks/models.py
# 任务协作模块 - 核心数据模型
# 定义任务、评论、变更日志等核心业务实体

class Task(models.Model):
    """任务 - 协同工作的基本单元"""
    # ...

    def perform_update(self, serializer):
        # 更新任务时自动记录变更日志，方便追溯
        # 因接待场景需要频繁变更，需记录每次修改的详情
        old = self.get_object()
        task = serializer.save()
        # ...
```

```vue
<!-- frontend/src/views/TaskDetail.vue -->
<!-- 任务详情页 - 根据当前用户角色展示字段优先级和操作按钮 -->
```

### 9.3 App 内部职责分层

每个 Django App 内部按职责拆分文件：

```
backend/apps/tasks/
├── api/              # DRF ViewSet + Serializer
│   ├── views.py
│   ├── serializers.py
│   └── urls.py
├── models.py         # 数据模型
├── signals.py        # Django Signal
├── consumers.py      # WebSocket consumer
└── tests/            # 单元测试
```

### 9.3 接口先行的实现工作流

1. 定义 Model → 生成 Migration → 验证迁移通过
2. 定义 Serializer（明确输入输出字段）
3. 实现 ViewSet + URL 注册
4. 测试 API 可调用
5. 实现前端页面

### 9.4 分阶段实施计划

| 阶段 | 内容 | 验证标准 |
|------|------|---------|
| **Phase 0** | 项目脚手架、Django + Vue + Docker 搭建 | `docker compose up` 能正常启动 |
| **Phase 1** | accounts（角色体系 + 权限）+ tasks 基础版 | 能创建任务、分配执行人、设置角色 |
| **Phase 2** | tasks 完整版（多执行人、任务池、角色感知字段） | 支持指定/抢单两种分配，字段按角色置顶 |
| **Phase 3** | notifications（站内通知 + WebSocket） | 任务变更时右上角实时通知 |
| **Phase 4** | resources（资源库 + 任务联动 + 预约） | 任务中能关联/预约/释放资源 |
| **Phase 5** | pipeline（管线编辑器引擎 + Vue Flow 前端） | 管理员能拖拽创建管线，任务能绑定管线运行 |
| **Phase 6** | dashboard + 公开分享 + 分享页 | 看板展示统计数据，分享链接可公开访问 |

### 9.5 settings.py 预设

开发环境默认使用 PostgreSQL，避免 SQLite 与 PG 的类型差异问题（特别是 JSONB 字段）。
预设关键依赖：`channels`、`rest_framework`、`corsheaders`。

## 十、开源计划

- 仓库结构：Monorepo
- 许可证：Apache 2.0
- 贡献指南、代码规范等在实现阶段补充