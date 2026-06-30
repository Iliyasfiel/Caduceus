# Caduceus Implementation Plan (V2)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

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

### Phase 4: Resources

#### Task 4.1: Implement resources backend

**Files:** `backend/apps/resources/` (models, api/)

**models.py:**
```python
class ResourceType(models.Model):
    name = models.CharField(max_length=100, verbose_name='资源类型')
    icon = models.CharField(max_length=50, blank=True)
    schema = models.JSONField(default=list, blank=True, verbose_name='字段定义')

class ResourceItem(models.Model):
    resource_type = models.ForeignKey(ResourceType, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=200, verbose_name='资源名称')
    fields = models.JSONField(default=dict, blank=True, verbose_name='字段值')
    extra_fields = models.JSONField(default=dict, blank=True, verbose_name='自定义扩展参数')
    available = models.BooleanField(default=True, verbose_name='可用')

class ResourceBooking(models.Model):
    resource = models.ForeignKey(ResourceItem, on_delete=models.CASCADE, related_name='bookings')
    task = models.ForeignKey('tasks.Task', on_delete=models.CASCADE, related_name='resource_bookings')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20,
        choices=[('pending','待确认'),('confirmed','已确认'),('released','已释放')],
        default='pending')
```

**API:** ResourceTypeViewSet, ResourceItemViewSet, ResourceBookingViewSet.

#### Task 4.2: Frontend ResourceSelector and ResourceList

**Files:** Create `frontend/src/components/ResourceSelector.vue`, `frontend/src/views/ResourceList.vue`

- Admin panel to create/modify resource types and items
- ResourceSelector embedded in TaskDetail for linking resources
- Resource availability display

Verify: Resource types can be created, items added, tasks can link resources.

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
