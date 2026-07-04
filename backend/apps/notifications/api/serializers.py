"""
Caduceus Notifications API Serializers
定义通知的序列化器
"""
from rest_framework import serializers
from ..models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    通知序列化器
    用于通知的序列化和反序列化
    """
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'type', 'type_display', 'title',
            'content', 'link', 'is_read', 'created_at'
        ]
        read_only_fields = ['recipient']
