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