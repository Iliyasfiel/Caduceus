"""
Caduceus 根 URL 配置
包含 API 路由和管理后台入口
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # API 路由
    path('api/accounts/', include('apps.accounts.api.urls')),
    path('api/tasks/', include('apps.tasks.api.urls')),
    # path('api/pipeline/', include('apps.pipeline.api.urls')),
    # path('api/resources/', include('apps.resources.api.urls')),
    # path('api/notifications/', include('apps.notifications.api.urls')),
    # path('api/dashboard/', include('apps.dashboard.api.urls')),
]