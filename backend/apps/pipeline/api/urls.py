"""
Caduceus Pipeline API URLs
定义管线模板与管线实例的路由
"""
from rest_framework.routers import DefaultRouter
from .views import PipelineViewSet, PipelineInstanceViewSet

router = DefaultRouter()

router.register(r'pipelines', PipelineViewSet, basename='pipeline')
router.register(r'pipeline-instances', PipelineInstanceViewSet, basename='pipeline-instance')

urlpatterns = router.urls
