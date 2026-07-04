"""
Caduceus Tasks API URLs
定义任务、任务分配、评论和日志的路由
"""
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, TaskAssignmentViewSet, TaskCommentViewSet, TaskLogViewSet

# 创建路由器
router = DefaultRouter()

# 注册 ViewSet
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'assignments', TaskAssignmentViewSet, basename='assignment')
router.register(r'comments', TaskCommentViewSet, basename='comment')
router.register(r'logs', TaskLogViewSet, basename='log')

# 导出 URL 列表
urlpatterns = router.urls