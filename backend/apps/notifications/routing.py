"""
Caduceus 站内通知 WebSocket 路由配置
定义通知模块的 WebSocket URL 路由规则
"""
from django.urls import path
from apps.notifications.consumers import NotificationConsumer

websocket_urlpatterns = [
    path("ws/notifications/", NotificationConsumer.as_asgi()),
]
