"""
Caduceus Accounts API URLs
定义用户、角色、小组和角色分配的路由
"""
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RoleViewSet, GroupViewSet, RoleAssignmentViewSet, AuthViewSet

# 创建路由器
router = DefaultRouter()

# 注册 ViewSet
router.register(r'users', UserViewSet, basename='user')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'groups', GroupViewSet, basename='group')
router.register(r'assignments', RoleAssignmentViewSet, basename='assignment')
router.register(r'auth', AuthViewSet, basename='auth')

# 导出 URL 列表
urlpatterns = router.urls