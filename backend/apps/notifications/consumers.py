"""
Caduceus 站内通知 WebSocket Consumer
通过 Django Channels 实现通知实时推送
前端连接 /ws/notifications/ 后可接收实时通知
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from apps.notifications.models import Notification


class NotificationConsumer(AsyncWebsocketConsumer):
    """站内通知 WebSocket 消费者，管理用户连接与消息分发"""

    async def connect(self):
        """建立 WebSocket 连接，验证用户登录后将用户加入专属通知组"""
        user = self.scope.get("user")

        if user is None or user.is_anonymous:
            await self.close()
            return

        self.group_name = f"user_{user.id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        await self.accept()

    async def disconnect(self, close_code):
        """断开 WebSocket 连接，将用户从专属通知组中移除"""
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name,
            )

    async def receive(self, text_data=None, bytes_data=None):
        """接收前端发送的消息，支持标记通知已读等操作"""
        try:
            payload = json.loads(text_data)
        except (json.JSONDecodeError, TypeError):
            return

        action = payload.get("action")

        if action == "mark_read":
            notification_id = payload.get("notification_id")
            if notification_id:
                user = self.scope.get("user")
                if user and not user.is_anonymous:
                    await self._mark_notification_read(user, notification_id)

    async def notification_message(self, event):
        """
        处理通知消息事件，将通知推送给前端
        由 channel_layer 的 group_send 触发，event 中携带通知数据
        """
        await self.send(text_data=json.dumps({
            "type": event["type"],
            "data": event["data"],
        }))

    async def _mark_notification_read(self, user, notification_id):
        """标记指定通知为已读状态"""
        from channels.db import database_sync_to_async

        @database_sync_to_async
        def _mark_read():
            try:
                notification = Notification.objects.get(
                    id=notification_id,
                    recipient=user,
                )
                notification.is_read = True
                notification.save(update_fields=["is_read"])
                return True
            except Notification.DoesNotExist:
                return False

        return await _mark_read()
