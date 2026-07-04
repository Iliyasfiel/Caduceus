"""
Caduceus Tasks 应用配置
"""
from django.apps import AppConfig


class TasksConfig(AppConfig):
    """
    Tasks 应用配置类
    定义应用的基本信息和启动行为
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.tasks'
    verbose_name = '任务协作'

    def ready(self):
        """
        应用启动时的初始化操作
        导入信号处理器以确保信号被正确注册
        """
        # 导入信号处理器
        import apps.tasks.signals