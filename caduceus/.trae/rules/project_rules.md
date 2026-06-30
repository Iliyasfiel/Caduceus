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

## Implementation Workflow
1. Define Model → Generate Migration → Verify migration passes
2. Define Serializer (clarify input/output fields)
3. Implement ViewSet + URL registration
4. Test API is callable
5. Implement frontend pages

## Git Commit Convention
- Use conventional commit format: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`
- Commit messages in Chinese preferred for this project