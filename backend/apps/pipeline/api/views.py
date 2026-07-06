"""
Caduceus Pipeline API Views
提供管线模板与管线实例的 API 接口
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ..models import Pipeline, PipelineInstance
from .serializers import PipelineSerializer, PipelineInstanceSerializer


class PipelineViewSet(viewsets.ModelViewSet):
    """
    管线模板 API ViewSet
    提供管线模板的 CRUD 操作
    创建管线时自动将当前用户设为创建者
    """
    queryset = Pipeline.objects.all()
    serializer_class = PipelineSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """
        创建管线时自动设置 created_by 为当前登录用户
        创建者字段不在请求体中传入，由后端自动填充
        """
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        """支持按名称搜索过滤"""
        queryset = super().get_queryset()

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)

        return queryset


class PipelineInstanceViewSet(viewsets.ModelViewSet):
    """
    管线实例 API ViewSet
    提供管线运行实例的 CRUD 操作
    """
    queryset = PipelineInstance.objects.all()
    serializer_class = PipelineInstanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """支持按管线、任务、状态过滤"""
        queryset = super().get_queryset()

        pipeline_id = self.request.query_params.get('pipeline')
        if pipeline_id:
            queryset = queryset.filter(pipeline_id=pipeline_id)

        task_id = self.request.query_params.get('task')
        if task_id:
            queryset = queryset.filter(task_id=task_id)

        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset
