# Caduceus Implementation Plan (V2)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> 📚 **文档职责**：本文档回答 **“按什么顺序写代码”**——分阶段（Phase 0~7）任务清单、文件结构、每步实现要点与验收标准。
>
> 不包含产品需求背景（→ [`caduceus-prd.md`](./caduceus-prd.md)）和架构/数据模型细节（→ [`caduceus-design.md`](./caduceus-design.md)）。
>
> UI 风格基线见 [`caduceus-design.md` §十一、§十二](./caduceus-design.md)；组件 API 参考见 [`dev-tmp/design/ui-component-api-reference.md`](../../dev-tmp/design/ui-component-api-reference.md)。
>
> 完整文档索引见 [README §📚 文档索引](../README.md#-文档索引)。

**Goal:** Build Caduceus, a lightweight open-source collaborative work platform with flexible role system, visual pipeline editor (information-flow model), resource library, and real-time notifications.

**Architecture:** Monorepo with Django 5 backend (DRF + Channels) and Vue 3 + Vue Flow frontend, PostgreSQL 16 (JSONB for flexible fields), Redis for WebSocket channel layer, Docker Compose deployment.

**Tech Stack:** Django 5 / DRF / Django Channels / Vue 3 (Composition API + `<script setup>`) / Vue Flow / Pinia / Axios / PostgreSQL 16 / Redis 7 / Docker Compose

---

## File Structure (Updated for V2 Design)

```
caduceus/
├── backend/
│   ├── config/
│   │   ├── settings.py            # Django settings
│   │   ├── urls.py                # Root URL config
│   │   ├── asgi.py                # ASGI config (Channels)
│   │   └── wsgi.py                # WSGI config
│   ├── apps/
│   │   ├── accounts/              # 用户/角色/权限（V2: 灵活角色体系）
│   │   │   ├── models.py          # User, Role, RoleAssignment, Group
│   │   │   ├── admin.py
│   │   │   ├── api/
│   │   │   │   ├── serializers.py
│   │   │   │   ├── views.py
│   │   │   │   └── urls.py
│   │   │   └── tests/
│   │   ├── tasks/                 # 任务协作（V2: 多执行人+角色感知+任务关联）
│   │   │   ├── models.py          # Task, TaskAssignment, TaskComment, TaskLog
│   │   │   ├── signals.py         # Task change → notifications
│   │   │   ├── admin.py
│   │   │   ├── api/
│   │   │   │   ├── serializers.py
│   │   │   │   ├── views.py
│   │   │   │   └── urls.py
│   │   │   └── tests/
│   │   ├── pipeline/              # 管线编辑器（V2: 信息流模型，单节点类型）
│   │   │   ├── models.py          # Pipeline, PipelineInstance
│   │   │   ├── api/
│   │   │   │   ├── serializers.py
│   │   │   │   ├── views.py
│   │   │   │   └── urls.py
│   │   │   └── tests/
│   │   ├── resources/             # 资源库
│   │   │   ├── models.py          # ResourceType, ResourceItem, ResourceBooking
│   │   │   ├── api/
│   │   │   └── tests/
│   │   ├── notifications/         # 站内通知 + WebSocket
│   │   │   ├── models.py          # Notification
│   │   │   ├── consumers.py       # WebSocket consumer
│   │   │   ├── backends.py        # Adapter pattern
│   │   │   ├── api/
│   │   │   └── tests/
│   │   └── dashboard/             # 数据统计
│   │       └── api/
│   │           ├── views.py       # Aggregation API
│   │           └── urls.py
│   ├── docker/
│   │   ├── Dockerfile
│   │   ├── entrypoint.sh
│   │   └── nginx.conf
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── client.js
│   │   │   ├── auth.js
│   │   │   ├── tasks.js
│   │   │   ├── pipeline.js
│   │   │   ├── resources.js
│   │   │   └── notifications.js
│   │   ├── stores/
│   │   │   ├── auth.js
│   │   │   ├── tasks.js
│   │   │   ├── notifications.js
│   │   │   └── resources.js
│   │   ├── views/
│   │   │   ├── Login.vue
│   │   │   ├── Dashboard.vue
│   │   │   ├── TaskList.vue
│   │   │   ├── TaskDetail.vue
│   │   │   ├── PipelineEditor.vue
│   │   │   ├── ResourceList.vue
│   │   │   ├── SharePage.vue          # 公开分享页
│   │   │   └── AdminPanel.vue
│   │   ├── components/
│   │   │   ├── AppLayout.vue          # 响应式布局
│   │   │   ├── TaskCard.vue
│   │   │   ├── TaskMergeGroup.vue     # 任务合并展示
│   │   │   ├── CommentList.vue
│   │   │   ├── ChangeTimeline.vue
│   │   │   ├── ResourceSelector.vue
│   │   │   ├── NotificationBell.vue
│   │   │   └── PipelineCanvas.vue     # Vue Flow
│   │   ├── App.vue
│   │   ├── router.js
│   │   └── main.js
│   ├── Dockerfile
│   ├── vite.config.js
│   ├── package.json
│   └── index.html
├── docker-compose.yml
├── docker-compose.prod.yml
└── README.md
```

---

## Tasks

### Phase 0: Project Scaffolding

#### Task 0.1: Create project rules for AI

**Files:** Create `caduceus/.trae/rules/project_rules.md`

Content:
```markdown
# Caduceus Project Rules

## Technology Stack
- Backend: Django 5 + Django REST Framework
- Frontend: Vue 3 (Composition API + <script setup>) + Vite
- Database: PostgreSQL 16 (JSONB for flexible fields)
- Real-time: Django Channels + WebSocket
- State Management: Pinia
- HTTP Client: Axios
- Pipeline Editor: Vue Flow
- Deployment: Docker Compose

## Code Comment Rules (IMPORTANT)
- Every file MUST have a header comment explaining its purpose and module
- Every function/method and key logic block MUST have Chinese comments
- Comments should explain WHY, not WHAT (the code itself shows WHAT)

## Backend Conventions
- Django ORM for all DB operations; DRF ViewSet + Serializer pattern
- Each app: api/views.py → api/serializers.py → api/urls.py
- Signals for cross-app event handling
- WebSocket consumers in consumers.py per app

## Frontend Conventions
- <script setup> syntax for all components
- API calls in src/api/, not in components
- Pinia stores in src/stores/
- PascalCase for component names

## Naming
- Django models: singular PascalCase
- API endpoints: plural kebab-case
- Vue components: PascalCase
- Python files: snake_case
```

#### Task 0.2: Scaffold Django backend

**Files:** `caduceus/backend/` (manage.py, config/, requirements.txt, docker/, docker-compose.yml)

Requirements:
```
Django==5.1.4
djangorestframework==3.15.2
django-cors-headers==4.6.0
channels==4.2.0
channels-redis==4.2.1
daphne==4.1.2
psycopg[binary]==3.2.3
django-extensions==3.2.3
gunicorn==23.0.0
```

**settings.py** key configs:
- INSTALLED_APPS: daphne, rest_framework, corsheaders, channels, django_extensions
- DATABASES: PostgreSQL (env configurable)
- CHANNEL_LAYERS: Redis
- ASGI_APPLICATION: config.asgi.application
- CORS_ALLOW_ALL_ORIGINS = True (dev only)
- LANGUAGE_CODE = 'zh-hans', TIME_ZONE = 'Asia/Shanghai'

**ASGI** config with Channels ProtocolTypeRouter (empty URLRouter for now).

**Dockerfile**: python:3.12-slim, entrypoint runs migrate + daphne.

**docker-compose.yml**: postgres:16-alpine + redis:7-alpine.

Verify: `docker compose up -d postgres redis && python manage.py migrate` succeeds.

#### Task 0.3: Scaffold Vue 3 frontend

**Files:** `caduceus/frontend/` (package.json, vite.config.js, index.html, src/main.js, src/App.vue, src/router.js, src/api/client.js, Dockerfile)

Key dependencies:
- vue, vue-router, pinia, axios, @vue-flow/core, @vue-flow/minimap, @vue-flow/controls

**vite.config.js** with proxy: `/api` → `http://localhost:8000`, `/ws` → `ws://localhost:8000`.

**api/client.js**: Axios instance with baseURL `/api`, 401 interceptor redirects to `/login`.

Verify: `npm install && npm run build` succeeds.

---

### Phase 1: Accounts & Tasks Core

#### Task 1.1: Implement accounts app (flexible role system)

**Files:** Create `backend/apps/accounts/` (models, api/, admin, tests)

**models.py:**
```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # 用户 - 基础账号，后续通过 RoleAssignment 分配角色权限
    profile = models.JSONField(default=dict, blank=True, verbose_name='扩展信息')

class Role(models.Model):
    # 角色定义 - 由管理员预设（讲解员、接待员、司机等）
    name = models.CharField(max_length=100, verbose_name='角色名称')
    role_type = models.CharField(max_length=20,
        choices=[('initiator','发起人'),('executor','执行人'),('admin','管理员')],
        verbose_name='角色类型')
    description = models.TextField(blank=True, verbose_name='描述')

    def __str__(self):
        return self.name

class Group(models.Model):
    # 业务小组 - 如"讲解组"、"车队"
    name = models.CharField(max_length=100, verbose_name='组名称')
    description = models.TextField(blank=True, verbose_name='描述')

    def __str__(self):
        return self.name

class RoleAssignment(models.Model):
    # 用户-角色关联 - 一个用户可拥有多个角色
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='role_assignments')
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    is_supervisor = models.BooleanField(default=False, verbose_name='是否主管')
```

**API:** UserViewSet, RoleViewSet, GroupViewSet, RoleAssignmentViewSet (all ModelViewSet).

Verify: `makemigrations accounts && migrate accounts && test` passes.

#### Task 1.2: Implement tasks core (Task, TaskAssignment, TaskComment, TaskLog)

**Files:** Create `backend/apps/tasks/` (models, api/)

**models.py:**
```python
class Task(models.Model):
    # 任务 - 协同工作的基本单元
    # 所有参与角色共享任务全部信息，字段全局共享（非节点独占）
    title = models.CharField(max_length=200, verbose_name='标题')
    description = models.TextField(blank=True, verbose_name='描述')
    status = models.CharField(max_length=20,
        choices=[('draft','草稿'),('pending','待处理'),('in_progress','进行中'),
                 ('completed','已完成'),('cancelled','已取消')],
        default='draft')
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='created_tasks', verbose_name='发起人')
    pipeline = models.ForeignKey('pipeline.Pipeline', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='关联管线')
    fields = models.JSONField(default=dict, blank=True, verbose_name='自定义字段')
    # 字段值全局共享，每个字段可标记 priority_roles
    resources = models.ManyToManyField('resources.ResourceItem', blank=True, verbose_name='关联资源')
    related_tasks = models.ManyToManyField('self', blank=True, symmetrical=True, verbose_name='关联任务')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class TaskAssignment(models.Model):
    # 任务执行人关联 - 支持多执行人以不同角色参与同一任务
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='assignments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.ForeignKey('accounts.Role', on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20,
        choices=[('pending','待处理'),('accepted','已接取'),('completed','已完成')],
        default='pending')

class TaskComment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(verbose_name='内容')
    created_at = models.DateTimeField(auto_now_add=True)

class TaskLog(models.Model):
    # 变更历史 - 完整记录每次修改
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='logs')
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=50, verbose_name='操作类型')
    changes = models.JSONField(default=dict, blank=True, verbose_name='变更详情')
    created_at = models.DateTimeField(auto_now_add=True)
```

**TaskViewSet** with `perform_create`/`perform_update` auto-logging to TaskLog.

**TaskAssignmentViewSet** for managing task-executor-role associations.

**API endpoints:**
- `/api/tasks/` — CRUD
- `/api/tasks/{id}/assignments/` — Nested assignments
- `/api/tasks/{id}/add_comment/` — Comment action
- `/api/tasks/{id}/relate/` — Link related tasks

Verify: `makemigrations tasks && migrate tasks && test` passes.

#### Task 1.3: Frontend — Login, Layout, Task List/Detail

**Files:** Create `frontend/src/` views/components/stores for auth and tasks.

**Responsive layout requirement:** AppLayout.vue must be responsive — sidebar collapses to hamburger menu on mobile (<768px).

**Key pages:**
- Login.vue — username/password form
- Dashboard.vue — Basic task list (placeholder for Phase 6 stats)
- TaskList.vue — List all tasks with "只看与我相关" filter toggle
- TaskDetail.vue — Shared structure, fields sorted by current user's role priority

**Key components:**
- AppLayout.vue — Responsive sidebar (collapsible on mobile), top bar with NotificationBell
- TaskCard.vue — Task summary card showing title, status, involved roles
- CommentList.vue — Comments section with add form

**Stores:** auth.js (login/logout/session), tasks.js (list/get/create/update)

**Router:** /login, / (AppLayout with children), auth guard

Verify: `npm run dev`, login page renders, task list loads from API.

---

### Phase 2: Pipeline Editor (Information Flow Model)

#### Task 2.1: Implement pipeline models

**Files:** Create `backend/apps/pipeline/`

**models.py:**
```python
class Pipeline(models.Model):
    # 管线模板 - 定义信息流而非工作流
    # 画布上只有"任务节点"一种元素，角色和资源是节点内部属性
    name = models.CharField(max_length=200, verbose_name='管线名称')
    description = models.TextField(blank=True, verbose_name='描述')
    nodes = models.JSONField(default=list, blank=True, verbose_name='任务节点配置')
    # nodes 结构：
    # [{
    #   "id": "node_1",
    #   "label": "前期准备",
    #   "fields_config": [
    #     {"key":"visit_unit","label":"来访单位","type":"text","priority_roles":[],"is_public":true},
    #     {"key":"pickup_time","label":"派车时间","type":"datetime","priority_roles":["司机"],"is_public":false}
    #   ],
    #   "roles": [
    #     {"role_id": 1, "merge_default": true, "merge_time_window": 30}
    #   ],
    #   "resource_types": [1, 2]
    # }]
    edges = models.JSONField(default=list, blank=True, verbose_name='阶段连接')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class PipelineInstance(models.Model):
    # 管线运行实例 - 与任务一对一关联
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name='instances')
    task = models.ForeignKey('tasks.Task', on_delete=models.CASCADE, related_name='pipeline_instances')
    current_node = models.CharField(max_length=100, blank=True, verbose_name='当前阶段')
    status = models.CharField(max_length=20,
        choices=[('running','运行中'),('completed','已完成')], default='running')
    created_at = models.DateTimeField(auto_now_add=True)
```

**API:** PipelineViewSet, PipelineInstanceViewSet.

Verify: `makemigrations pipeline && migrate pipeline` succeeds.

#### Task 2.2: Implement PipelineCanvas.vue with Vue Flow

**Files:** Create `frontend/src/components/PipelineCanvas.vue`, `frontend/src/views/PipelineEditor.vue`

**PipelineCanvas.vue:**
- Single node type on canvas: "任务节点"
- Left panel: no node type selection (only one type), instead shows field/role/resource configuration options
- Click node → right panel to configure: node label, fields (add/remove/reorder), roles, resource types
- Nodes connectable via dragging edges between output/input handles
- Data model: `v-model` emits `{ nodes: [], edges: [] }` matching Pipeline model

**PipelineEditor.vue:**
- Full page editor wrapping PipelineCanvas
- Save pipeline → POST to `/api/pipelines/`
- Load existing → GET from `/api/pipelines/{id}/`
- Preview mode shows task view rendered from pipeline config

Verify: Pipeline can be created with multiple nodes, configured with fields and roles, saved and reloaded.

---

### Phase 3: Notifications (WebSocket)

#### Task 3.1: Implement notifications backend

**Files:** `backend/apps/notifications/` (models, consumers, backends, api)

**models.py:**
```python
class Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='notifications')
    type = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    link = models.CharField(max_length=500, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

**consumers.py:** NotificationConsumer — WebSocket, group per user.

**backends.py:** NotificationBackend (ABC), WebSocketBackend (first impl).

**ASGI routing:** `/ws/notifications/` → NotificationConsumer.

**Signals:** In tasks/signals.py, listen to TaskLog post_save → create Notification → WebSocket push.

Verify: Task create/update triggers WebSocket notification to all related users.

#### Task 3.2: Frontend notification bell

**Files:** Create `frontend/src/components/NotificationBell.vue`, `frontend/src/stores/notifications.js`

- WebSocket connection on login
- Unread count badge on bell icon
- Click to expand notification list
- Click notification → mark read + navigate to linked task
- Real-time push updates

Verify: Notifications appear in real-time without page refresh.

---

### Phase 4: Resources（资源库生命周期增强）✅

#### Task 4.1: Implement resources backend ✅
- ResourceTypeViewSet + ResourceItemViewSet + ResourceLogViewSet 全部就绪
- 路由已激活：`/api/resources/resource-types/`、`/api/resources/resource-items/`、`/api/resources/resource-logs/`

#### Task 4.2: 扩展 ResourceType 模型（lifecycle_config）✅
- ResourceType 已包含 `lifecycle_config` JSONField 字段
- 迁移 0002 已执行

#### Task 4.3: 新增 ResourceLog 模型 ✅
- ResourceLog 模型已实现（resource/event_key/operator/summary/details/created_at）
- ResourceLogViewSet + ResourceLogSerializer 已就绪

#### Task 4.4: ResourceLog → status 自动推导 + 通知联动 ✅
- signals.py 已实现：post_save 信号 → 匹配 lifecycle_config → 更新 resource.status → 按 notify_roles 创建 Notification
- apps.py ready() 已注册 signals

#### Task 4.5: ResourceItemSerializer status 只读 ✅
- status 已在序列化器 read_only_fields 中

#### Task 4.6: 前端资源管理页面 ✅
- ResourceList.vue：Tab 切换 + 资源类型管理 + 资源条目 CRUD + 操作日志查看
- ResourceSelector.vue：模态选择器，类型筛选 + 多选条目 + 已关联标记
- TaskDetail.vue：右侧面板集成资源关联 + ResourceSelector 弹窗

#### Task 4.7: API 端点验证 ✅
- 全部端点 curl 验证通过

---

### Phase 5: Dashboard, Task Merging & Public Share

#### Task 5.1: Dashboard stats API

**Files:** `backend/apps/dashboard/api/`

Aggregation view:
```python
class DashboardStatsView(APIView):
    def get(self, request):
        # 聚合并返回本月任务总数、完成数、进行中数、资源调用数
```

**Dashboard.vue** update: Stats cards grid + task list below.

#### Task 5.2: Task merging (frontend)

**Files:** Modify `frontend/src/views/TaskList.vue`, create `frontend/src/components/TaskMergeGroup.vue`

- In task detail, "关联任务" button (only visible if same pipeline + same role)
- In task list, merged display: multiple related tasks shown as one expandable group
- Merge only affects current user's view (personal display preference)
- Default merge behavior configured in pipeline's role config

#### Task 5.3: Public share page

**Files:** Create `frontend/src/views/SharePage.vue`

- Route: `/share/:token` — no auth required
- Fetch task data by share_token UUID
- Render configured public fields and progress
- Token expiration check
- Share link generation in TaskDetail (admin/creator only)

---

## Self-Review

**Spec coverage check:**
- ✅ Vision & philosophy → Task 0.1 (project_rules.md)
- ✅ Tech stack → Task 0.2, 0.3
- ✅ Flexible role system (User, Role, RoleAssignment, Group, Supervisor) → Task 1.1
- ✅ Task collaboration (Task, TaskAssignment, TaskComment, TaskLog) → Task 1.2
- ✅ Full info transparency, operation by permission → Task 1.1 (permission logic in views)
- ✅ Pipeline = information flow, single node type → Task 2.1, 2.2
- ✅ Fields belong to task (not node), globally shared → Task 1.2 models, Task 2.1 nodes config
- ✅ priority_roles for role-aware display → Task 2.1 (fields_config.priority_roles)
- ✅ Public fields (is_public) → Task 2.1
- ✅ Soft constraint (stage completion = hint, not lock) → Task 2.1 (no blocking logic)
- ✅ Role-level task merging → Task 5.2
- ✅ Merge config in pipeline → Task 2.1 (nodes.roles[].merge_default)
- ✅ Resources (ResourceType, ResourceItem, ResourceBooking) → Task 4.1
- ✅ Extra_fields for resource items → Task 4.1
- ✅ Notifications via WebSocket → Task 3.1, 3.2
- ✅ Dashboard stats → Task 5.1
- ✅ Public share page → Task 5.3
- ✅ Mobile responsive layout → Task 1.3 (AppLayout.vue responsive)
- ✅ Code comment rules → Task 0.1 (project_rules.md)

**No placeholders:** All code blocks contain complete model/schema definitions.
**Type consistency:** All model refs, serializer refs, and API endpoints consistent across tasks.
**Task dependency order:** Tasks build sequentially (Phase 0 → 1 → 2 → 3 → 4 → 5).
**No missing tasks detected.**

---

## Implementation Lessons Learned (Phase 0–3)

以下是在 Phase 0~3 实际开发中暴露的问题及解决方案，作为后续 Phase 和迭代的参考。

### 1. 前端 API URL 与 DRF Router 路径对齐

**问题**：DRF `DefaultRouter` 注册 `router.register(r'pipelines', PipelineViewSet)` 后，端点路径为 `/pipelines/`。urls.py 中 `path('api/pipeline/', include(...))` 再加前缀，最终完整路径为 `/api/pipeline/pipelines/`。但前端 API 层写成了 `/pipeline/`（缺少 `/pipelines/` 后缀），导致 405/404。

**规则**：**前端 `src/api/*.js` 中的 URL 必须与 DRF router 生成的完整路径严格一致。** 每个模块开发完成后，用 curl 验证端点可达性：

```bash
# 以 pipeline 为例
curl -X POST http://localhost:8000/api/pipeline/pipelines/ \
  -H "Content-Type: application/json" \
  -d '{"name":"test","nodes":[],"edges":[]}' \
  -b /tmp/cookies.txt
```

**路径对照表（Vite 代理后 baseURL 为 /api）：**

| 模块 | 前端调用 | 后端路由注册 | 最终完整路径 |
|------|----------|-------------|-------------|
| accounts | `/accounts/auth/login/` | `router.register('auth')` | `/api/accounts/auth/login/` |
| tasks | `/tasks/` | `router.register('tasks')` + url `api/tasks/` | `/api/tasks/` |
| pipeline | `/pipeline/pipelines/` | `router.register('pipelines')` + url `api/pipeline/` | `/api/pipeline/pipelines/` |
| notifications | `/notifications/notifications/` | `router.register('notifications')` + url `api/notifications/` | `/api/notifications/notifications/` |
| resources | `/resources/resource-types/` | `router.register('resource-types')` + url `api/resources/` | `/api/resources/resource-types/` |

### 2. 前后端数据格式需双向转换

**问题**：后端 JSONB 存储 nodes 为扁平格式 `{id, label, fields_config, roles, resource_types}`，Vue Flow 画布需要嵌套格式 `{id, type, position, data: {label, ...}}`。v-model 桥接时只处理了单向转换，导致加载已有数据时 `node.data` 为 undefined。

**规则**：**任何涉及 v-model 在前端组件与后端 JSON 之间传递数据的场景，必须在输入（model → 组件）和输出（组件 → model）两端都做格式转换。** 且要兼容两种数据来源（用户新建的 Vue Flow 格式 + 后端加载的扁平格式），使用可选链兜底：

```javascript
// 兼容两种格式的输入转换
label: n.data?.label || n.label || '默认值',

// 输出转换（去掉 Vue Flow 特有字段）
nodes: nodes.value.map(n => ({
  id: n.id,
  label: n.data?.label,
  fields_config: n.data?.fields_config || [],
  roles: n.data?.roles || [],
  resource_types: n.data?.resource_types || []
}))
```

### 3. CSRF 豁免需重写 DRF 认证类而非视图装饰器

**问题**：前后端分离（Vite :3000 ↔ Django :8000）时，即使 `AuthViewSet` 加了 `@method_decorator(csrf_exempt)`，登录仍返回 403。原因是 DRF 的 `SessionAuthentication.enforce_csrf()` 在认证层强制检查，视图级 `csrf_exempt` 无法绕过。

**解决方案**：创建自定义认证类，重写 `enforce_csrf` 为空操作，在 `settings.py` 中将 `DEFAULT_AUTHENTICATION_CLASSES` 替换为此类：

```python
# apps/accounts/authentication.py
from rest_framework.authentication import SessionAuthentication

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        pass  # 前后端分离架构下豁免 DRF 层 CSRF 检查

# config/settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'apps.accounts.authentication.CsrfExemptSessionAuthentication',
    ],
    ...
}
```

### 4. 占位模块需提供最小可用 API

**问题**：Phase 4 的 resources 模块只有 models.py，没有 serializers / views / urls。但 Phase 2 的 PipelineEditor.vue 在加载时调用了 `getResourceTypes()`，导致 404 错误虽被 catch 但仍然污染控制台。

**规则**：**任何被其他 Phase 引用的占位模块，必须在占位时提供最小 API 层**（至少一个 ViewSet + Serializer + 路由注册），返回空列表即可，避免跨阶段引用时产生 404。

### 5. JavaScript 导出未定义标识符会阻断整个路由

**问题**：`tasks.js` 的 `export default { ..., getTaskLogs }` 引用了不存在的函数，导致该模块加载失败。由于 `router.js` 中所有页面组件使用 `() => import(...)` 懒加载，模块依赖链断裂后所有路由页面全部白屏。

**规则**：**default export 中的每个 key 必须对应一个已定义的导出函数。** 添加新 API 函数时，先定义函数体，再放入 export。使用 ESLint 的 `no-undef` 规则可提前发现此类问题。

### 6. ASGI 配置中 Django settings 必须先于 Channels 导入

**问题**：`config/asgi.py` 在 `os.environ.setdefault('DJANGO_SETTINGS_MODULE', ...)` 之前就 `import apps`，导致 settings 未加载时模块找不到 routing 属性，daphne 启动崩溃。

**规则**：**ASGI 配置中，`os.environ.setdefault` 必须放在所有 Django/Channels 模块导入之前。** Channels routing 的 import 放在 `get_asgi_application()` 调用之后。

```python
# 正确顺序
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')  # 第 1 步

from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()  # 第 2 步：Django 初始化

from apps.notifications.routing import websocket_urlpatterns  # 第 3 步：业务 import
```

### 7. API 端点验证清单

每个后端 API 模块开发完成后，应执行以下验证：

- [ ] `curl` 测试所有端点（GET list, POST create, GET detail, PATCH update），确认返回 200/201
- [ ] 登录状态下的端点使用 `-b cookies.txt` 携带 session
- [ ] 对照 `frontend/src/api/*.js` 中的 URL 与后端实际路由逐个比对
- [ ] 检查 `backend/config/urls.py` 中对应路由行未被注释

### 8. 数据格式变更需全链路同步

**问题**：Phase 1 设计 `Task.fields` 为 `default=dict`（对象），Phase 2 管线 fields_config 为数组格式。创建带管线任务时，管线字段初始化为数组但模型仍期望 dict，导致类型不匹配。Phase 1→2 格式调整未同步到所有下游代码。

**规则**：**当上游模型字段格式变更时，必须同时更新所有序列化器、视图 create/update 逻辑、前端 API 调用和 store 中的数据处理代码。** 建议在设计文档中明确标注字段格式约定，防止 Phase 间出现 JSONB 结构不一致。

### 9. 功能级合并展示逻辑不可硬编码

**问题**：Phase 3 实际实施中，"任务字段按角色优先级排序"被实现在前端 `sortedFields` computed 中，依赖 `authStore.user.role_assignments`。但 `role_assignments` 返回的是 `role` ID，不是 `role.name`，管线 fields_config 中 `priority_roles` 存储的也可能是 ID。两者匹配逻辑需在开发前明确约定。

**规则**：**跨模块引用字段（如 priority_roles）时必须约定使用 ID 还是 name 作为匹配键。** 建议统一使用 ID 匹配（避免改名后断裂），并为每个关联字段在 serializer 中同时输出 `_id` 和 `_name` 方便前端选择。

### 10. 占位 model 与实际 API 的字段名差异

**问题**：Phase 2 PipelineEditor.vue 调用 `getResourceTypes()` 时，后端 ResourceType 模型的字段名与设计文档中的 `schema` 不同（实际为 `field_schema`），虽然影响较小但说明占位模型在设计文档更新后未同步。

**规则**：**设计文档中的字段名应与实际模型代码定期对照。** 在 Phase 开始前应先用 `inspectdb` 或读取 models.py 确认字段名，避免按文档写出与实际不一致的前端调用代码。
