"""
Caduceus Pipeline App 配置
管线编辑器模块，待 Phase 2 完善实现
"""
from django.apps import AppConfig


class PipelineConfig(AppConfig):
    """管线编辑器应用配置，管理管线模板与实例"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.pipeline'
    verbose_name = '管线编辑器'