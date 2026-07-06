# Tasks

- [x] Task 1: 重构 Pipeline 模型为 V2 结构
  - [x] 修改 [backend/apps/pipeline/models.py](file:///Users/zhaofuqing/Documents/Developer/Caduceus/backend/apps/pipeline/models.py)：Pipeline 用 `nodes` + `edges` 替代 `definition`，PipelineInstance 移除 `execution_history` 简化 status choices
  - [x] 生成迁移：手动编写 `0003_v2_refactor.py`
  - [x] 迁移文件就绪，待 docker 环境执行 migrate 验证

- [x] Task 2: 实现 Pipeline CRUD API
  - [x] 创建 [backend/apps/pipeline/api/serializers.py](file:///Users/zhaofuqing/Documents/Developer/Caduceus/backend/apps/pipeline/api/serializers.py)：PipelineSerializer + PipelineInstanceSerializer，验证 nodes/edges JSON 结构
  - [x] 创建 [backend/apps/pipeline/api/views.py](file:///Users/zhaofuqing/Documents/Developer/Caduceus/backend/apps/pipeline/api/views.py)：PipelineViewSet + PipelineInstanceViewSet，created_by 自动设为当前用户
  - [x] 创建 [backend/apps/pipeline/api/urls.py](file:///Users/zhaofuqing/Documents/Developer/Caduceus/backend/apps/pipeline/api/urls.py)：注册路由
  - [x] 在 [backend/config/urls.py](file:///Users/zhaofuqing/Documents/Developer/Caduceus/backend/config/urls.py) 注册 pipeline 路由（取消注释）

- [x] Task 3: 前端管线编辑器画布组件 PipelineCanvas.vue
  - [x] 创建 [frontend/src/components/PipelineCanvas.vue](file:///Users/zhaofuqing/Documents/Developer/Caduceus/frontend/src/components/PipelineCanvas.vue)：基于 Vue Flow 的可拖拽画布
  - [x] 左侧面板：添加节点按钮，显示该管线中全部节点的字段/角色/资源配置摘要
  - [x] 右侧面板：选中节点后编辑 label、fields_config（key/label/type/priority_roles/is_public）、roles、resource_types
  - [x] 画布交互：节点间连线、节点拖拽移动、删除节点/连线
  - [x] v-model 输出 `{ nodes: [], edges: [] }` 匹配后端 Pipeline 模型

- [x] Task 4: 重构 PipelineEditor.vue 为完整管线编辑器
  - [x] 重构 [frontend/src/views/PipelineEditor.vue](file:///Users/zhaofuqing/Documents/Developer/Caduceus/frontend/src/views/PipelineEditor.vue)：包裹 PipelineCanvas，增加顶部工具栏（名称输入、保存按钮、返回按钮）、管线列表
  - [x] 支持创建新管线：POST /api/pipelines/
  - [x] 支持加载已有管线：GET /api/pipelines/{id}/，数据反序列化到画布
  - [x] 支持更新管线：PUT/PATCH /api/pipelines/{id}/
  - [x] 保存成功后显示提示，刷新管线列表

- [x] Task 5: 更新 README
  - [x] 更新 [README.md](file:///Users/zhaofuqing/Documents/Developer/Caduceus/README.md)：Phase 2 标记为 ✅，补充管线编辑器功能说明

# Task Dependencies
- Task 2 依赖 Task 1（需先有 V2 模型才能写 Serializer）
- Task 3 和 Task 2 可并行（前后端独立开发）
- Task 4 依赖 Task 3（PipelineEditor 包裹 PipelineCanvas）和 Task 2（需要后端 API 就绪）
- Task 5 依赖 Task 1-4 全部完成
