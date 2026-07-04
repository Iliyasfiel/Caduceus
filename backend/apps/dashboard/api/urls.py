"""
Caduceus Dashboard API URL 配置
定义仪表盘统计数据的 REST API 路由
"""
from django.urls import path
from .views import DashboardStatsView

urlpatterns = [
    path('stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
]
