"""
Caduceus Resources API URLs
定义资源类型与资源项的路由
"""
from rest_framework.routers import DefaultRouter
from .views import ResourceTypeViewSet, ResourceItemViewSet, ResourceLogViewSet

router = DefaultRouter()

router.register(r'resource-types', ResourceTypeViewSet, basename='resource-type')
router.register(r'resource-items', ResourceItemViewSet, basename='resource-item')
router.register(r'resource-logs', ResourceLogViewSet, basename='resource-log')

urlpatterns = router.urls
