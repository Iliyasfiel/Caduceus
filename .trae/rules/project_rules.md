# Caduceus Project Rules

## Technology Stack
- Backend: Django 5 + Django REST Framework
- Frontend: Vue 3 (Composition API + `<script setup`) + Vite
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
- `<script setup>` syntax for all components
- API calls in src/api/, not in components
- Pinia stores in src/stores/
- PascalCase for component names

## Naming
- Django models: singular PascalCase
- API endpoints: plural kebab-case
- Vue components: PascalCase
- Python files: snake_case

## Design Document Driven Development (IMPORTANT)
- 开发前必须查阅 `designingDocument/` 目录下的设计文档，严格按照文档规范实现
- 主要设计文档包括：`caduceus-prd.md`（产品需求）、`caduceus-design.md`（架构设计）、`caduceus-implementation.md`（实现计划）
- 需求或实现有疑问时，优先参考设计文档，而非自行猜测

## Implementation Workflow
1. 查阅 designingDocument 中的相关文档，明确需求和设计
2. Define Model → Generate Migration → Verify migration passes
3. Define Serializer (clarify input/output fields)
4. Implement ViewSet + URL registration
5. Test API is callable
6. Implement frontend pages
7. 每个阶段开发完成或有新 feature 加入时，更新 `README.md`

## README Maintenance (IMPORTANT)
- 每个实现阶段（Phase）完成后，必须更新 `README.md` 记录完成的功能和使用方式
- 新增 feature 时，同步更新 `README.md` 补充新功能的说明
- README 应保持能反映项目当前最新状态

## Git Commit Convention
- Use conventional commit format: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`
- Commit messages in Chinese preferred for this project

## 仓库治理

### 虚拟环境
- **禁止**将任何 Python 虚拟环境提交到远程仓库，包括但不限于：`venv/`、`.venv/`、`env/`、`.env-virtual/`、`virtualenv/` 等。
- 依赖通过 `requirements.txt`（或 `pyproject.toml`）管理。Clone 仓库后应在本地重建虚拟环境：
  ```bash
  python3 -m venv backend/.venv
  source backend/.venv/bin/activate
  pip install -r backend/requirements.txt
  ```
- 已在 `.gitignore` 中忽略 `venv/` 与 `.venv/`，避免误提交。

### 演示数据（demo-data）
- 根目录下的 `demo-data/` 目录用于存放**开发演示用的临时数据**（如示例资源类型、示例任务等），用于手动验证页面效果。
- **`demo-data/` 允许提交**到远程仓库（与 `node_modules/`、`.venv/` 等被忽略的目录形成对比）。
- 存放内容规范：
  - ✅ 允许：非敏感的、可复现的、用于手动验证的演示数据（如示例资源类型 JSON、示例用户、示例任务）。
  - ❌ 禁止：生产数据、真实用户隐私、任何含 API Key/Token/密码的内容。
- 使用方式详见 `demo-data/README.md` 与 `README.md` 的"演示数据（demo-data）"章节。

### 临时文件（dev-tmp）
- 开发过程中产生的**临时文件**（如对话中临时整理出的需求讨论文档、生成图片用的脚本文件、一次性草稿、调试用的样例数据等），必须放在**项目根目录下的 `dev-tmp/`** 文件夹中集中管理，**不得散落在仓库其他位置**。
- 适用范围：
  - ✅ 必须放入：`dev-tmp/` — 临时需求讨论文档、图片生成脚本、一次性草稿、调试样例。
  - ❌ 禁止散落：根目录、`.trae/`、`designingDocument/`、`demo-data/`、`backend/`、`frontend/` 等正式目录（避免污染正式产物）。
- `dev-tmp/` 视为**临时目录**，默认**不提交**远程仓库（应在 `.gitignore` 中忽略 `dev-tmp/`）。
- **删除确认流程（IMPORTANT）**：清理 `dev-tmp/` 内任何文件 / 子目录前，必须**先向用户确认**该临时内容是否需要同步沉淀到项目正式文档（如 `designingDocument/`、`README.md`、`docs/` 等）：
  1. 列出待删除的文件清单及其内容概要；
  2. 询问用户："是否需要将上述内容同步到项目正式文档？（如不需要再删除）"；
  3. 用户明确答复"无需同步"或"已同步"后，方可执行删除。
- 同步建议场景：
  - 需求讨论文档中提炼出的最终结论 → 合并进 `designingDocument/caduceus-prd.md` 或对应 design 文档；
  - 图片生成脚本中可复用的逻辑 → 沉淀为正式工具或文档示例；
  - 调试样例中有保留价值的部分 → 转存到 `demo-data/`。