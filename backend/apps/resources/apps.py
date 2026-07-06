"""
Caduceus Resources App 配置
资源库模块，待 Phase 4 完善实现
"""
from django.apps import AppConfig


class ResourcesConfig(AppConfig):
    """资源库应用配置，管理资源类型与资源条目"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.resources'
    verbose_name = '资源库'

    def ready(self):
        import apps.resources.signals  # noqa