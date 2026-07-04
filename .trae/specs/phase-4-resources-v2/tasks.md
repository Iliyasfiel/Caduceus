# Tasks

- [x] Task 1: 完善 ResourceList.vue 资源库管理页面
  - [x] 顶部 Tab 切换（资源条目管理 / 资源类型管理）
  - [x] 资源类型管理 Tab：类型列表 + 新建/编辑弹窗
  - [x] 资源条目管理 Tab：左侧类型树 + 右侧条目表格 + 新建/编辑/删除 + 操作日志入口

- [x] Task 2: 新建 ResourceSelector.vue
  - [x] 下拉选择资源类型筛选
  - [x] 资源条目多选列表
  - [x] 确认后 emit 选中结果
  - [x] 已关联标识

- [x] Task 3: TaskDetail.vue 集成 ResourceSelector
  - [x] 右侧面板新增"关联资源"区域
  - [x] 已关联资源列表展示
  - [x] 点击"+ 关联资源"弹出 ResourceSelector
  - [x] 确认后 PATCH 任务关联资源

- [x] Task 4: 更新 README Phase 4 为 ✅
  - [x] Phase 4 标记 ✅，补充资源库 + 生命周期日志说明

# Task Dependencies
- Task 2 独立可并行
- Task 3 依赖 Task 2（需 ResourceSelector 就绪）
- Task 4 依赖 Task 1-3
