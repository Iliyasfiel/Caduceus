"""
Caduceus Dashboard API Views
提供仪表盘聚合统计数据的 API 接口
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.timezone import now

from apps.tasks.models import Task
from apps.resources.models import ResourceLog


class DashboardStatsView(APIView):
    """
    仪表盘统计 API View
    GET 方法需认证，聚合返回本月任务统计、资源调用和最近任务
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """聚合返回仪表盘统计数据"""
        current = now()

        # 本月任务查询集
        month_tasks = Task.objects.filter(created_at__month=current.month)

        # 统计各项指标
        total_tasks = month_tasks.count()
        completed_tasks = month_tasks.filter(status='completed').count()
        in_progress_tasks = month_tasks.filter(status='in_progress').count()

        # 计算完成率（保留 1 位小数）
        if total_tasks > 0:
            completion_rate = round(completed_tasks / total_tasks * 100, 1)
        else:
            completion_rate = 0

        # 本月资源调用次数
        resource_usage_count = ResourceLog.objects.filter(
            created_at__month=current.month
        ).count()

        # 最近 5 条任务
        recent_tasks_qs = Task.objects.select_related('creator').order_by('-created_at')[:5]
        recent_tasks_data = []
        for task in recent_tasks_qs:
            recent_tasks_data.append({
                'id': task.id,
                'title': task.title,
                'status': task.status,
                'status_display': task.get_status_display(),
                'creator_name': task.creator.username,
                'created_at': task.created_at,
            })

        return Response({
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'in_progress_tasks': in_progress_tasks,
            'completion_rate': completion_rate,
            'resource_usage_count': resource_usage_count,
            'recent_tasks': recent_tasks_data,
        })
