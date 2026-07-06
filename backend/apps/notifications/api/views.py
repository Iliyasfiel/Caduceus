"""
Caduceus Notifications API Views
提供通知的 REST API 接口
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    """
    通知 API ViewSet
    提供通知的 CRUD 操作，仅返回当前用户的通知
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        只返回当前用户的未读通知
        按创建时间倒序排列
        """
        return self.request.user.notifications.all()

    def perform_create(self, serializer):
        """
        创建通知时自动设置接收者为当前用户
        实际业务中通知由信号系统创建，此方法作为兜底
        """
        serializer.save(recipient=self.request.user)

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """
        获取当前用户未读通知数量
        用于前端显示未读标记（红点/角标）
        """
        count = request.user.notifications.filter(is_read=False).count()
        return Response({'count': count})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """
        将当前用户所有未读通知标记为已读
        提供一键全部已读功能
        """
        updated = request.user.notifications.filter(is_read=False).update(is_read=True)
        return Response({'marked_read': updated})
