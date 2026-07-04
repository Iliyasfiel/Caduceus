# Tasks

- [x] Task 1: 实现 Dashboard 聚合统计 API
  - [x] 创建 [backend/apps/dashboard/api/views.py](file:///Users/zhaofuqing/Documents/Developer/Caduceus/backend/apps/dashboard/api/views.py)：DashboardStatsView（APIView，GET 聚合返回统计 + 最近任务）
  - [x] 创建 [backend/apps/dashboard/api/urls.py](file:///Users/zhaofuqing/Documents/Developer/Caduceus/backend/apps/dashboard/api/urls.py)：注册路由 /stats/
  - [x] 修改 [backend/config/urls.py](file:///Users/zhaofuqing/Documents/Developer/Caduceus/backend/config/urls.py)：取消注释 dashboard 路由
  - [x] 创建 [frontend/src/api/dashboard.js](file:///Users/zhaofuqing/Documents/Developer/Caduceus/frontend/src/api/dashboard.js)

- [x] Task 2: 完善 Dashboard.vue 仪表盘前端
  - [x] 修改 [frontend/src/views/Dashboard.vue](file:///Users/zhaofuqing/Documents/Developer/Caduceus/frontend/src/views/Dashboard.vue)：从 /api/dashboard/stats/ 加载数据，渲染 4 个统计卡片 + 最近任务列表

- [x] Task 3: 实现公开分享页面
  - [x] 创建 [frontend/src/views/SharePage.vue](file:///Users/zhaofuqing/Documents/Developer/Caduceus/frontend/src/views/SharePage.vue)：公开分享页面（无登录、展示进度+公开字段+过期处理）
  - [x] 后端新增公开查看 action：TaskViewSet 新增 public_share 通过 token 查询
  - [x] 修改 [frontend/src/views/TaskDetail.vue](file:///Users/zhaofuqing/Documents/Developer/Caduceus/frontend/src/views/TaskDetail.vue)：顶部工具栏添加分享按钮 + 链接生成/复制对话框

- [x] Task 4: 实现任务合并展示组件
  - [x] 创建 [frontend/src/components/TaskMergeGroup.vue](file:///Users/zhaofuqing/Documents/Developer/Caduceus/frontend/src/components/TaskMergeGroup.vue)：合并组渲染（可折叠）
  - [x] 修改 [frontend/src/views/TaskList.vue](file:///Users/zhaofuqing/Documents/Developer/Caduceus/frontend/src/views/TaskList.vue)：集成合并展示逻辑 + 手动切换开关

- [x] Task 5: 更新 README Phase 5
  - [x] Phase 5 标记为 ✅
  - [x] 补充 Dashboard/分享/合并展示功能说明

# Task Dependencies
- Task 2 依赖 Task 1（dashboard API 就绪后前端才能联调）
- Task 3 独立可并行
- Task 4 独立可并行
- Task 5 依赖 Task 1-4 全部完成
