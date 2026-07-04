"""
Caduceus Resources API Views
提供资源类型与资源项的 API 接口
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ..models import ResourceType, ResourceItem, ResourceLog
from .serializers import ResourceTypeSerializer, ResourceItemSerializer, ResourceLogSerializer


class ResourceTypeViewSet(viewsets.ModelViewSet):
    """
    资源类型 API ViewSet
    提供资源类型的 CRUD 操作
    """
    queryset = ResourceType.objects.all()
    serializer_class = ResourceTypeSerializer
    permission_classes = [IsAuthenticated]


class ResourceItemViewSet(viewsets.ModelViewSet):
    """
    资源项 API ViewSet
    提供资源项的 CRUD 操作
    创建资源项时自动将当前用户设为创建者
    """
    queryset = ResourceItem.objects.all()
    serializer_class = ResourceItemSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """
        创建资源项时自动设置 creator 为当前登录用户
        creator 字段不在请求体中传入，由后端自动填充
        """
        serializer.save(creator=self.request.user)


class ResourceLogViewSet(viewsets.ModelViewSet):
    """
    资源事件日志 API ViewSet
    提供资源生命周期事件的 CRUD 操作
    创建日志时自动将当前用户设为操作人
    """
    queryset = ResourceLog.objects.all()
    serializer_class = ResourceLogSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(operator=self.request.user)
