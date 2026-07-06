"""
Caduceus 通知发送后端适配器
使用适配器模式（Strategy Pattern）抽象通知推送渠道
支持 WebSocket 实时推送，后续可扩展邮件、钉钉等渠道
"""
from abc import ABC, abstractmethod
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class NotificationBackend(ABC):
    """
    通知发送后端抽象基类
    所有通知推送渠道必须继承此类并实现 send 方法
    """

    @abstractmethod
    def send(self, notification):
        """
        发送通知的抽象方法
        子类需实现具体渠道的通知发送逻辑

        Args:
            notification: Notification 模型实例
        """
        pass


class WebSocketBackend(NotificationBackend):
    """WebSocket 实时推送后端，通过 Channels channel layer 将通知推送到用户浏览器"""

    def send(self, notification):
        """
        通过 Channel Layer 发送通知到用户专属组
        前端通过 WebSocket 连接实时接收通知

        Args:
            notification: Notification 模型实例，需包含 recipient 关联
        """
        channel_layer = get_channel_layer()
        group_name = f"user_{notification.recipient.id}"

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "notification_message",
                "data": {
                    "id": notification.id,
                    "type": notification.type,
                    "title": notification.title,
                    "content": notification.content,
                    "link": notification.link,
                    "is_read": notification.is_read,
                    "created_at": notification.created_at.isoformat(),
                },
            },
        )
