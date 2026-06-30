"""
Caduceus ASGI 配置
用于支持 Django Channels（WebSocket）
"""
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 获取 Django ASGI 应用
django_asgi_app = get_asgi_application()

# 协议类型路由器（目前仅支持 HTTP，WebSocket 路由待后续添加）
application = ProtocolTypeRouter({
    'http': django_asgi_app,
    # 'websocket': AuthMiddlewareStack(
    #     URLRouter([
    #         # WebSocket 路由待各 app 创建后添加
    #         # path('ws/notifications/', apps.notifications.consumers.NotificationConsumer.as_asgi()),
    #     ])
    # ),
})