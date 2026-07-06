"""
Caduceus Notifications App 配置
站内通知模块，管理 WebSocket 推送与通知服务
"""
from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    """
    站内通知应用配置类
    定义应用的基本信息和启动行为
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notifications'
    verbose_name = '站内通知'

    def ready(self):
        """
        应用启动时的初始化操作
        导入信号处理器以确保信号被正确注册
        """
        import apps.notifications.signals