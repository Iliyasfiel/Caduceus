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

| 层级 | 选型 |
|------|------|
| 前端 | Vue 3（Composition API + `<script setup>`）+ Vite + Pinia + Vue Flow |
| 后端 | Django 5 + Django REST Framework + Django Channels（WebSocket） |
| 数据 | PostgreSQL 16（JSONB）+ Redis 7（Channels channel layer） |
| 部署 | Docker Compose（Nginx + Django + PostgreSQL + Redis） |

> 完整选型理由与依赖清单见 [`designingDocument/caduceus-design.md`](designingDocument/caduceus-design.md) §技术栈。

## 📁 项目结构

```
caduceus/
├── backend/                # Django 5 + DRF + Channels
├── frontend/               # Vue 3 + Vite + Pinia
├── designingDocument/      # 需求 / 设计 / 实施 三层文档（详见 §📚 文档索引）
├── demo-data/              # 可提交的演示数据（详见 §📦 演示数据）
├── .trae/rules/            # 项目开发规范
├── docker-compose.yml      # 开发环境
└── docker-compose.prod.yml # 生产环境
```

## 🎨 核心功能

| 模块 | 一句话简介 | 详细设计 |
|------|----------|---------|
| 角色体系 | 灵活的“角色 + 业务小组 + 主管”模型 | [`caduceus-design.md` §数据模型](designingDocument/caduceus-design.md) |
| 任务协作 | 多执行人 + 角色感知 + 自定义字段 | [`caduceus-design.md` §数据模型](designingDocument/caduceus-design.md) |
| 管线编辑器 | 信息流可视化建模（管理员在线自定义流程） | [`caduceus-design.md` §管线设计](designingDocument/caduceus-design.md) |
| 资源库 | 自定义资源类型 + 条目 CRUD + 生命周期日志 | [`caduceus-design.md` §资源库](designingDocument/caduceus-design.md) |
| 实时通知 | WebSocket 推送 + 站内铃铛 + 已读标记 | [`caduceus-design.md` §通知](designingDocument/caduceus-design.md) |
| 仪表盘 | 本月任务统计 / 完成率 / 进行中 / 资源调用 | [`caduceus-implementation.md`](designingDocument/caduceus-implementation.md) |
| 公开分享 | UUID token 公开链接，无需登录查看进度 | [`caduceus-design.md` §分享](designingDocument/caduceus-design.md) |

> 完整需求条目、功能描述、原型示意见 [`caduceus-prd.md`](designingDocument/caduceus-prd.md)；UI 视觉风格、组件清单、主题规范见 [`caduceus-design.md`](designingDocument/caduceus-design.md) §11 / §12。

## 📱 响应式设计

前端页面在手机浏览器上可正常使用核心功能，侧边栏统一采用 GitHub 风格 drawer（默认收起 + 全屏遮罩 + 多触发方式关闭），主内容区与侧边栏状态解耦、零重排。

> drawer 实现细节、桌面 / 移动边界处理见 [`caduceus-design.md`](designingDocument/caduceus-design.md) §11 与 `dev-tmp/ui-design-principles-and-polish.md` §4。

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

## 🚀 快速开始

### 环境要求

- Docker & Docker Compose；或
- Python 3.12+ 和 Node.js 20+

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

### 本地开发（推荐）

**后端（venv + SQLite + 内存通道，无需任何外部依赖）**

```bash
cd backend

python3 -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate

pip install -r requirements.txt

# 一次性环境变量 + 跑迁移 / 建超级用户 / 启服务
$env:DB_ENGINE="sqlite"; $env:CHANNEL_BACKEND="memory"
.\.venv\Scripts\python.exe manage.py migrate
$env:DJANGO_SUPERUSER_USERNAME="admin"
$env:DJANGO_SUPERUSER_PASSWORD="admin12345"
$env:DJANGO_SUPERUSER_EMAIL="admin@example.com"
.\.venv\Scripts\python.exe manage.py createsuperuser --noinput
.\.venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
```

> PowerShell 用户如遇 `python` 跳到 Microsoft Store，详见 [`.trae/rules/project_rules.md`](.trae/rules/project_rules.md) “仓库治理”。

**前端**

```bash
cd frontend
npm install
npx vite --host --port 3000
```

### 访问地址

| 入口 | URL |
|------|-----|
| 前端 SPA | http://localhost:3000/ |
| 后端 API | http://127.0.0.1:8000/api/ |
| API（经 Vite 代理） | http://127.0.0.1:3000/api/ |
| Django Admin | http://127.0.0.1:8000/admin/ |

## 🛣️ 开发路线图

| 阶段 | 主题 | 状态 |
|------|------|------|
| Phase 0 | 项目脚手架（Django / Vue / Docker Compose） | ✅ |
| Phase 1 | 角色体系 + 任务协作基础 | ✅ |
| Phase 2 | 管线编辑器（V2 JSONB 模型 + Vue Flow） | ✅ |
| Phase 3 | 实时通知（WebSocket + 信号联动） | ✅ |
| Phase 4 | 资源库（类型 / 条目 / 生命周期日志） | ✅ |
| Phase 5 | 仪表盘 + 任务合并展示 + 公开分享 | ✅ |
| Phase 6 | 阶段标记 + 管理面板（用户 / 角色 / 组） | ✅ |
| Phase 7 | UI 重设计（设计令牌 + 13 个基础组件 + 三态主题） | ✅ |

> 各阶段对应的实施步骤、文件清单、验收标准见 [`caduceus-implementation.md`](designingDocument/caduceus-implementation.md)。

### 后续 Polish（不单独开 Phase）

- **UiSelect v2 自渲染 popper**（2026-07-06）：替换原生 `<select>`，暗色模式天然正确；新增 size（sm/md）/ searchable / multiple / asyncLoader 能力。详见 [§1.2 第 8 条 + §5.5](dev-tmp/design/ui-design-principles-and-polish.md)。**禁止在新代码中使用原生 `<select>`**

## 🤝 贡献指南

欢迎贡献代码。请先阅读：

- 📘 [需求文档 `caduceus-prd.md`](designingDocument/caduceus-prd.md) — 了解产品定位与功能边界
- 📐 [设计文档 `caduceus-design.md`](designingDocument/caduceus-design.md) — 了解架构与数据模型
- 🛠️ [实施计划 `caduceus-implementation.md`](designingDocument/caduceus-implementation.md) — 按阶段认领任务
- 📏 [`.trae/rules/project_rules.md`](.trae/rules/project_rules.md) — 项目硬约束（命名 / 注释 / 仓库治理）

### 硬约束速览

- 所有代码文件必须包含中文注释说明用途
- 后端：Django ORM + DRF ViewSet + Serializer 模式
- 前端：Vue 3 Composition API + `<script setup>` 语法
- API 调用统一放在 `src/api/`；状态管理用 `src/stores/`
- 组件使用 PascalCase；Python 文件使用 snake_case
- 前端样式**只使用** `frontend/src/styles/tokens.css` 中的设计令牌
- 前端图标**走 `UiIcon`**；弹窗走 `UiModal`；状态色走 `UiBadge` tone；全局通知用 `useToast()`；确认操作用 `useConfirm()`

## 📚 文档索引

> README 只做项目介绍 + 快速开始 + 贡献引导。所有细节都在下面的设计文档里，按“需求 → 设计 → 实施”三层组织；UI 视觉风格基线已合并到设计文档 §11 / §12，组件 API / Polish 记录 / P1 路线图在 `dev-tmp/` 临时目录。

| 文档 | 关注点 | 适合谁 |
|------|--------|--------|
| 📘 [产品需求文档（PRD）`caduceus-prd.md`](designingDocument/caduceus-prd.md) | 产品定位、目标用户、功能需求列表、原型示意 | 产品 / 想了解“做什么” |
| 📐 [设计文档 `caduceus-design.md`](designingDocument/caduceus-design.md) | 技术栈、架构、数据模型、接口约定、权限、关键流程，**§11 风格基线 + §12 基础组件清单** | 架构师 / 前端 / 想了解“怎么设计” |
| 🛠️ [实施计划 `caduceus-implementation.md`](designingDocument/caduceus-implementation.md) | 分阶段任务、文件结构、每步实现与验收 | 开发 / 想认领任务 |
| 📏 [`.trae/rules/project_rules.md`](.trae/rules/project_rules.md) | 项目硬约束（命名 / 注释 / 仓库治理 / dev-tmp） | 所有贡献者 |
| 🗂️ [`dev-tmp/design/`](dev-tmp/design/) | UI 临时文档（组件 API 参考 / 设计原则 / Polish 记录 / 路线图） | 任何改动 UI 的人 |

## 📦 演示数据（demo-data）

根目录的 [`demo-data/`](./demo-data/) 目录用于存放开发演示用的临时数据，**允许提交**到远程仓库。

- **用途**：本地手动验证页面效果（Dashboard / 任务详情 / 资源列表 / Pipeline 编辑器等）；新成员 onboarding 时快速了解数据结构。
- **典型内容**：`resource-types.example.json`（5 种典型资源类型示例：会议室 / 设备 / 耗材 / 权限 / 服务）。
- **加载方式**：手动对照 JSON 在后台录入；或转成标准 Django fixtures 后用 `python manage.py loaddata` 批量导入。详见 [`demo-data/README.md`](./demo-data/README.md)。
- **清理**：本目录数据不影响业务代码运行，随时可整体删除；需要重置开发数据库时执行 `python manage.py flush`。
- **仓库治理**：详见 [`.trae/rules/project_rules.md`](.trae/rules/project_rules.md) “仓库治理”小节（✅ 允许 `demo-data/`；❌ 禁止 `venv/`、`.venv/`、`node_modules/`、`db.sqlite3`、`.env`、用户隐私）。

## 📄 开源协议

Apache 2.0 License