# Caduceus - 轻量级开源协同工作平台

> 信息全透明，操作有边界

Caduceus 是一款轻量级、开源的协同工作平台。它不是传统的 OA 或项目管理软件，而是一个**聚焦角色间信息流转的信息枢纽**——让多人多角色的协作团队能够以透明的信息共享和灵活的流程编排，高效地协同完成工作。

## ✨ 核心理念

- **流程是协作的加速器，而非限制协作的锁链**
- **信息全透明，操作有边界** — 所有协作者可查看任务的全部信息，但谁能执行什么操作由角色和权限控制
- **管理员可在线自定义流程** — 通过可视化管线编辑器，无需二次开发即可适应不同协作场景

## 🎯 目标场景

首期对标 **50 人以内的小团队**，覆盖行政接待、活动管理、会议协调等多角色分工协作场景。

典型场景特征：
- 信息渐进式明确（发起时信息不全，后续补充）
- 频繁的中途变更（行程调整、人员增减）
- 变更需要即时传达给所有相关角色
- 资源（酒店、餐厅、车辆等）与任务联动
- 多角色并行协作（讲解员、接待、会务、司机等）

## 🏗️ 技术栈

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

## 📁 项目结构

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
├── .trae/rules/                # AI 辅助开发规范
├── docker-compose.yml          # 开发环境
├── docker-compose.prod.yml     # 生产环境
└── README.md
```

## 🎨 UI 重设计（ui-redesign 分支）

`ui-redesign` 分支对前端视觉层进行系统性重写，**不动任何业务逻辑**。设计基线来自 Vercel 模板（`design_libraries/dl_builtin_vercel`），通过设计令牌 + 基础组件两层实现跨页面视觉一致。

### 核心原则

- **业务逻辑零改动**：所有 store 调用、API 调用、CRUD 流程、路由协议、字段排序、阶段流转、资源关联、分享 token 生成全部保留
- **感知层替换**：`alert()` → `useToast()`；`confirm()` → `useConfirm()`（移动端友好、不依赖浏览器原生丑陋弹窗）
- **token 化彻底**：所有页面样式只用 `var(--color-*)` / `var(--text-*)` / `var(--space-*)` 等 token，新页面自动跟随主题
- **dark mode 自动跟随**：通过 `<html data-theme="dark">` 三态策略，无需在每个组件写媒体查询

### 设计令牌层

文件：`frontend/src/styles/tokens.css`

| 类别 | token | 说明 |
|------|-------|------|
| 颜色 | `--color-primary` / `--color-destructive` / `--color-success` / 等 | 完整 Vercel 色板 + light/dark 双套 |
| 文字 | `--text-xs/sm/base/lg/xl/2xl` + `--leading-tight/normal` | 字号阶梯 |
| 间距 | `--space-1` ~ `--space-12` | 4px 基础单位 |
| 圆角 | `--radius-sm/md/lg/full` | 4 / 8 / 12 / 999 |
| 阴影 | `--shadow-sm/md/lg/xl` | 4 档阴影 |
| 动效 | `--transition-fast/normal` | 150ms / 250ms |
| 语义色 | `--badge-{neutral/info/success/warning/danger}-{bg,fg}` | Badge / Status 等语义配色 |

**暗色模式三态**：`<html>` 上不设 `data-theme` 时跟随系统 `prefers-color-scheme`；可手动写 `light` / `dark` 覆盖（`useThemeStore` 管理）。

### 基础组件（12 个）

文件：`frontend/src/components/ui/`

| 组件 | 用途 | 关键能力 |
|------|------|----------|
| `UiButton` | 按钮 | 4 variant × 3 size × loading/block |
| `UiInput` | 输入框 | label / error / hint / prefix / type=number 自动转换 |
| `UiSelect` | 下拉选择 | v-model + 状态枚举选项简化调用 |
| `UiCard` | 卡片 | header / footer / hoverable / padding 控制 |
| `UiBadge` | 状态徽章 | 5 tone × dark mode 自动反转 |
| `UiModal` | 弹窗 | center / drawer 两种 variant + ESC 关闭 + overlay 点击 |
| `UiTabs` | Tab 切换 | count 支持 + 自动激活样式 |
| `UiEmptyState` | 空状态 | 图标 + 标题 + 描述 + CTA |
| `UiToast` | 全局通知 | 消费 `useToastStore` |
| `UiConfirm` | 确认弹窗 | 消费 `useConfirmStore` |
| `UiSpinner` | 加载指示器 | 3 size + tone + label |
| `UiThemeToggle` | 主题切换 | ☀ / ☾ / ◐ 三态循环 |

### 全局 Store

文件：`frontend/src/stores/`

| Store | 用途 |
|-------|------|
| `useToastStore` + `useToast()` | 全局通知（success/error/info/warning），3 秒自动消失 |
| `useConfirmStore` + `useConfirm()` | 全局确认弹窗，`useConfirm()(opts) → Promise<boolean>` |
| `useThemeStore` | 主题三态 + localStorage 持久化 + 系统偏好监听 |

### 已完成 Polish 范围

**页面（8 个）**：

- `Login.vue` — token 化 + UiInput/UiButton
- `Dashboard.vue` — 统计卡 + 任务列表 token 化
- `TaskList.vue` — UiCard/UiBadge/UiModal/UiSelect + 合并展示 + 创建弹窗
- `TaskDetail.vue` — 时间线 / 信息区 / 字段表单 / 评论 / 日志 / 分享弹窗
- `ResourceList.vue` — UiTabs + 双子模块（条目/类型）+ 3 个弹窗 + 操作日志
- `AdminPanel.vue` — UiTabs + 3 个 tab（用户/角色/组）+ 3 个弹窗
- `PipelineEditor.vue` — UiButton + 全局 toast
- `SharePage.vue` — 公开页 token 化 + UiSpinner loading
- `AppLayout.vue` — 顶栏 + 侧栏 Vercel 风格重构

**子组件（5 个）**：

- `NotificationBell.vue` — token 化
- `ResourceSelector.vue` — token 化 + UiBadge + mobile 全屏化（5 行 CSS）
- `TaskMergeGroup.vue` — token 化 + UiBadge 状态色
- `PipelineCanvas.vue` — 布局层 token 化（Vue Flow 节点视觉保留）
- `App.vue` — 挂载全局 `<UiToast />` + `<UiConfirm />`

### 后续计划

- **Phase 5（响应式适配）**：基于现有 token 层扩展 breakpoints（640 / 768 / 1024 / 1280）+ 通用工具类，桌面优先 + CSS 响应式
- **移动端边界处理**：PipelineEditor 桌面专属（显示"请用桌面访问"占位）；SharePage 完整移动端适配；UiModal mobile 自动全屏

### 开发约定（新增）

新页面 / 新组件遵循：

1. 样式**只用 token**（`var(--color-*)` / `var(--space-*)` 等），不写硬编码颜色 / 尺寸
2. 弹窗**走 UiModal**（`v-model` 协议）；状态色**走 UiBadge tone**
3. 全局通知**用 `useToast()`**；删除类操作**用 `useConfirm()`**
4. import 用 `@/components/ui` 统一入口；Pinia store 用 `@/stores/` 统一管理

### 验证记录

- `npm run build` 0 错误 0 警告
- 所有页面 `alert()` / `confirm()` 残留：0
- 主题三态切换：light / dark / system 均正常
- dark mode：已 token 化的所有页面自动跟随

## 🚀 快速开始

### 环境要求

- Docker & Docker Compose
- 或 Python 3.12+ 和 Node.js 20+

### 使用 Docker Compose（推荐）

```bash
# 克隆仓库
git clone https://github.com/Iliyasfiel/Caduceus.git
cd Caduceus

# 启动开发环境（PostgreSQL + Redis）
docker compose up -d postgres redis

# 执行数据库迁移
docker compose run --rm backend python manage.py migrate

# 创建超级管理员
docker compose run --rm backend python manage.py createsuperuser

# 启动所有服务
docker compose up
```

访问地址：
- 前端: http://localhost:3000
- 后端 API: http://localhost:8000/api/
- Django Admin: http://localhost:8000/admin/

### 本地开发（推荐）

**后端：使用虚拟环境**

```bash
cd backend

# 创建并激活虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 使用 SQLite 运行（无需安装 PostgreSQL）
DB_ENGINE=sqlite CHANNEL_BACKEND=memory python manage.py migrate
DB_ENGINE=sqlite CHANNEL_BACKEND=memory python manage.py createsuperuser
DB_ENGINE=sqlite CHANNEL_BACKEND=memory python manage.py runserver
```

**前端：**

```bash
cd frontend
npm install
npm run dev
```

## 🎨 核心功能

### 1. 灵活的角色体系

- 管理员可预设角色类型（讲解员、接待员、司机、会务等）
- 一个用户可以拥有多种角色权限
- 支持创建业务小组（如讲解组、车队），可设置主管
- 主管可管理本组成员的任务分配

### 2. 任务协作

- 发起人可以创建任务，支持草稿态
- 一个任务可关联多个执行人，每个执行人以特定角色参与
- 支持灵活的自定义字段（由管线定义字段结构）
- 每个字段可标记"对哪些角色优先展示"
- 所有参与角色可查看任务的全部信息和变更记录
- 任务详情页中，字段按当前用户角色优先级置顶
- 支持任务评论、变更历史时间线
- 角色级任务合并展示（个人视图聚合）

### 3. 可视化管线编辑器

**管线定义的是信息流，而非工作流。**

- 画布上只有"任务节点"一种视觉元素
- 每个节点可配置：字段定义、参与角色、关联资源类型
- 字段归属于任务本身而非单个节点，字段值全局唯一
- 节点完成是软约束，不阻塞信息修改
- 管线模板与任务实例分离

### 4. 资源库 ✅

- 管理员可定义资源类型（酒店、餐厅、车辆、会议室等），每种资源类型可自定义字段结构
- 支持资源条目 CRUD（名称、状态、字段值、位置），按类型分组管理
- ResourceLog 生命周期事件日志（记录创建、调度、故障上报、维修等操作）
- ResourceSelector 选择器组件，支持在任务详情页关联资源
- 资源状态流转：可用 → 已预约 → 使用中 / 维护中 / 不可用

### 5. 实时通知

- 任务被指派、信息变更、新增评论等场景触发通知
- 通过 WebSocket 实时推送到前端
- 顶部导航栏通知铃铛，点击查看详情
- 通知支持标记已读/未读
- 适配器模式预留扩展接口（邮件/微信/钉钉）

### 6. 数据统计 🔄

- 仪表盘展示基础统计卡片（Phase 5 待实现）
- 本月任务总数、完成数、完成率
- 进行中的任务数
- 资源调用次数

### 7. 公开分享 🔄

- 支持生成 UUID 令牌的公开分享链接（Phase 5 待实现）
- 分享页无需登录即可访问
- 只展示预设字段和进度信息
- 支持设置分享链接过期时间

## 📱 响应式设计

前端页面采用响应式布局，在手机浏览器上可正常使用核心功能：
- 侧边栏在移动端折叠为汉堡菜单
- 布局自动适配不同屏幕尺寸

## 🔐 权限矩阵

| 操作 | 发起人 | 执行人 | 主管（本组） | 管理员 |
|------|--------|--------|------------|--------|
| 查看任务全部信息 | ✅ | ✅ | ✅ | ✅ |
| 创建任务 | ✅ | ✅ 有发起权 | ✅ | ✅ |
| 编辑任务信息 | ✅ 自己发起的 | ✅ 反馈进度 | ✅ 本组任务 | ✅ 全部 |
| 分配/改派执行人 | ✅ 自己发起的 | 🚫 | ✅ 本组任务 | ✅ 全部 |
| 确认完成/关闭任务 | ✅ 自己发起的 | 🚫 | ✅ 本组任务 | ✅ 全部 |
| 创建/编辑管线 | 🚫 | 🚫 | 🚫 | ✅ |
| 管理用户和角色 | 🚫 | 🚫 | 🚫 | ✅ |

## 🛣️ 开发路线图

### ✅ Phase 0 - 项目脚手架
- Django 后端脚手架
- Vue 3 前端脚手架
- Docker Compose 配置

### ✅ Phase 1 - Accounts & Tasks Core
- 灵活角色体系（User, Role, RoleAssignment, Group）
- 任务协作基础版（Task, TaskAssignment, TaskComment, TaskLog）
- 前端登录页、响应式布局、任务列表/详情

### ✅ Phase 2 - Pipeline Editor
- 管线模型 V2（nodes + edges JSONB 结构）
- Pipeline CRUD API（序列化器 + ViewSet + 路由）
- Vue Flow 可视化编辑器（PipelineCanvas 画布 + PipelineEditor 页面）
- 单任务节点类型画布，支持字段配置、角色配置、资源类型配置
- 节点间连线表达阶段推进方向

### ✅ Phase 3 - Notifications
- Notification 数据模型（类型/标题/内容/链接/已读标记）
- 通知 REST API（列表查询、未读计数、单个/批量已读标记）
- WebSocket 实时推送（NotificationConsumer + WebSocketBackend 适配器）
- TaskLog → Notification 信号联动（任务变更自动生成通知）
- 前端通知铃铛组件实时更新（WebSocket 连接 + badge + 点击跳转）

### ✅ Phase 4 - Resources
- ResourceType + ResourceItem + ResourceLog 数据模型（生命周期事件日志）
- 资源 REST API（类型/条目/日志 三个 ViewSet）
- ResourceList 资源库管理页面（资源类型管理 + 资源条目 CRUD + 操作日志查看）
- ResourceSelector 组件（任务详情页关联资源选择器）
- TaskDetail 集成资源关联功能

### ✅ Phase 5 - Dashboard & More
- Dashboard 聚合统计 API（本月任务/完成率/进行中/资源调用）
- 仪表盘首页（4 张统计卡片 + 最近任务列表）
- 任务合并展示（TaskMergeGroup 组件，管线分组折叠）
- 公开分享页面（SharePage.vue，无需登录查看进度+公开字段）
- 任务详情页分享链接生成（复制链接 + 过期时间设置）

### ✅ Phase 6 - Stage Marking & Admin Panel
- 管线阶段标记完成（时间轴三态：已完成/进行中/未开始，点击推进）
- 阶段标记后通知下一阶段角色（自动创建 Notification）
- 管理面板：用户管理（创建/编辑/禁用/角色分配）
- 管理面板：角色管理（CRUD + role_type 配置）
- 管理面板：组管理（CRUD + 成员统计）

### 🔄 Phase 7 - UI 重设计（`ui-redesign` 分支）
- 设计令牌层（颜色 / 字号 / 间距 / 圆角 / 阴影 / 动效 / 语义色）
- 12 个基础组件（UiButton / UiInput / UiSelect / UiCard / UiBadge / UiModal / UiTabs / UiEmptyState / UiToast / UiConfirm / UiSpinner / UiThemeToggle）
- 全局 Store：`useToast` / `useConfirm` / `useThemeStore`
- 8 个页面 + 5 个子组件 polish（业务逻辑零改动）
- dark mode 三态（light / dark / system）
- 详见上方 `🎨 UI 重设计（ui-redesign 分支）` 章节

## 🤝 贡献指南

欢迎贡献代码！请遵循以下规范：

- 所有代码文件必须包含中文注释说明用途
- 后端使用 Django ORM + DRF ViewSet + Serializer 模式
- 前端使用 Vue 3 Composition API + `<script setup>` 语法
- API 调用统一放在 `src/api/` 目录
- 状态管理使用 Pinia，放在 `src/stores/` 目录
- 组件使用 PascalCase 命名
- Python 文件使用 snake_case 命名
- **前端样式**：只使用 `frontend/src/styles/tokens.css` 中的设计令牌，不写硬编码颜色 / 尺寸
- **前端交互**：弹窗优先使用 `UiModal`，状态色使用 `UiBadge` tone，全局通知用 `useToast()`，确认操作用 `useConfirm()`
- 详细约定见上方 `🎨 UI 重设计` 章节

## 📄 开源协议

Apache 2.0 License

## 📚 相关文档

- [产品需求文档 (PRD)](designingDocument/caduceus-prd.md)
- [设计文档](designingDocument/caduceus-design.md)
- [实现计划](designingDocument/caduceus-implementation.md)

## 演示数据（demo-data）

根目录的 [`demo-data/`](./demo-data/) 目录用于存放开发演示用的临时数据，**允许提交**到远程仓库。

### 用途
- 在本地手动验证页面效果时（Dashboard、任务详情、资源列表、Pipeline 编辑器等）可作为参考数据
- 新成员 onboarding 时快速了解各模块的数据结构

### 典型内容
- `resource-types.example.json`：5 种典型资源类型示例（会议室 / 设备 / 耗材 / 权限 / 服务）

### 加载方式
详见 [`demo-data/README.md`](./demo-data/README.md)。常用方式：
- **手动参考**：对照 JSON 字段在后台页面录入
- **Django fixtures 批量导入**：`python manage.py loaddata <fixture_path>`（需先转为标准 fixtures 格式）

### 清理
本目录数据**不影响业务代码运行**，随时可整体删除。需要重置开发数据库时执行 `python manage.py flush`。

### 仓库治理约束
- ✅ 允许提交：`demo-data/`
- ❌ 禁止提交：虚拟环境（`venv/`、`.venv/` 等）、`node_modules/`、`db.sqlite3`、`.env`、用户隐私数据

详细规则见 `.trae/rules/project_rules.md` 的"仓库治理"小节。
