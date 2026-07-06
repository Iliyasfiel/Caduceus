"""
Caduceus Dashboard App 配置
数据统计模块，待 Phase 5 完善实现
"""
from django.apps import AppConfig


class DashboardConfig(AppConfig):
    """数据统计应用配置，提供仪表盘聚合统计功能"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.dashboard'
    verbose_name = '数据统计'