"""
Caduceus Tasks API Views
提供任务、任务分配、评论和日志的 API 接口
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from ..models import Task, TaskAssignment, TaskComment, TaskLog
from .serializers import (
    TaskSerializer, TaskCreateSerializer, TaskUpdateSerializer, TaskShareSerializer,
    TaskAssignmentSerializer, TaskCommentSerializer, TaskLogSerializer
)


@method_decorator(csrf_exempt, name='dispatch')
class TaskViewSet(viewsets.ModelViewSet):
    """
    任务 API ViewSet
    提供任务的 CRUD 操作和自定义 action
    """
    queryset = Task.objects.all()

    def get_serializer_class(self):
        """根据动作选择不同的序列化器"""
        if self.action == 'create':
            return TaskCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TaskUpdateSerializer
        elif self.action == 'share':
            return TaskShareSerializer
        return TaskSerializer

    def perform_create(self, serializer):
        """创建任务时自动设置创建者"""
        serializer.save(creator=self.request.user)

    def get_queryset(self):
        """支持按状态、创建者、执行人过滤"""
        queryset = super().get_queryset()

        # 按状态过滤
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # 按创建者过滤
        creator_id = self.request.query_params.get('creator')
        if creator_id:
            queryset = queryset.filter(creator_id=creator_id)

        # 按执行人过滤（查找该用户被分配的任务）
        assignee_id = self.request.query_params.get('assignee')
        if assignee_id:
            queryset = queryset.filter(assignments__user_id=assignee_id).distinct()

        # 按角色过滤（查找该角色相关的任务）
        role_id = self.request.query_params.get('role')
        if role_id:
            queryset = queryset.filter(assignments__role_id=role_id).distinct()

        # 搜索任务标题
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)

        return queryset

    @action(detail=True, methods=['get'])
    def assignments(self, request, pk=None):
        """
        获取任务的执行人列表
        返回该任务的所有分配信息
        """
        task = self.get_object()
        assignments = task.assignments.all()
        serializer = TaskAssignmentSerializer(assignments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """
        分配执行人
        为任务添加新的执行人
        """
        task = self.get_object()

        user_id = request.data.get('user_id')
        role_id = request.data.get('role_id')

        if not user_id:
            return Response(
                {'detail': '缺少 user_id 参数'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 检查是否已分配
        existing = TaskAssignment.objects.filter(
            task=task,
            user_id=user_id,
            role_id=role_id
        ).first()

        if existing:
            return Response(
                {'detail': '该用户已以该角色被分配到此任务'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 创建分配
        assignment = TaskAssignment.objects.create(
            task=task,
            user_id=user_id,
            role_id=role_id
        )

        serializer = TaskAssignmentSerializer(assignment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def unassign(self, request, pk=None):
        """
        取消执行人分配
        移除任务的执行人
        """
        task = self.get_object()

        user_id = request.data.get('user_id')
        role_id = request.data.get('role_id')

        if not user_id:
            return Response(
                {'detail': '缺少 user_id 参数'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 查找并删除分配
        queryset = TaskAssignment.objects.filter(task=task, user_id=user_id)
        if role_id:
            queryset = queryset.filter(role_id=role_id)

        deleted_count = queryset.delete()[0]

        if deleted_count == 0:
            return Response(
                {'detail': '未找到对应的分配记录'},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response({'detail': f'已取消 {deleted_count} 个分配'})

    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """
        获取任务的评论列表
        返回该任务的所有评论
        """
        task = self.get_object()
        comments = task.comments.all()
        serializer = TaskCommentSerializer(comments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """
        添加评论
        为任务添加新评论
        """
        task = self.get_object()

        content = request.data.get('content')
        if not content:
            return Response(
                {'detail': '评论内容不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )

        comment = TaskComment.objects.create(
            task=task,
            author=request.user,
            content=content
        )

        serializer = TaskCommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """
        获取任务的变更日志
        返回该任务的所有历史记录
        """
        task = self.get_object()
        logs = task.logs.all()
        serializer = TaskLogSerializer(logs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def relate(self, request, pk=None):
        """
        关联其他任务
        建立任务之间的关联关系
        """
        task = self.get_object()

        related_task_ids = request.data.get('task_ids', [])
        if not isinstance(related_task_ids, list):
            return Response(
                {'detail': 'task_ids 必须是列表'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 验证任务是否存在
        existing_tasks = Task.objects.filter(id__in=related_task_ids)
        if existing_tasks.count() != len(related_task_ids):
            return Response(
                {'detail': '部分任务 ID 不存在'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 添加关联（多对多关系，自动去重）
        task.related_tasks.add(*related_task_ids)

        return Response({'detail': f'已关联 {len(related_task_ids)} 个任务'})

    @action(detail=True, methods=['post'])
    def unrelate(self, request, pk=None):
        """
        取消任务关联
        移除任务之间的关联关系
        """
        task = self.get_object()

        related_task_ids = request.data.get('task_ids', [])
        if not isinstance(related_task_ids, list):
            return Response(
                {'detail': 'task_ids 必须是列表'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 移除关联
        task.related_tasks.remove(*related_task_ids)

        return Response({'detail': f'已取消关联 {len(related_task_ids)} 个任务'})

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """
        接取任务
        执行人接取任务（抢单模式）
        """
        task = self.get_object()

        # 查找当前用户在此任务中的分配
        assignment = TaskAssignment.objects.filter(
            task=task,
            user=request.user
        ).first()

        if not assignment:
            return Response(
                {'detail': '您未被分配到此任务'},
                status=status.HTTP_403_FORBIDDEN
            )

        if assignment.status != 'pending':
            return Response(
                {'detail': f'任务状态为 {assignment.get_status_display()}，无法接取'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 更新状态
        assignment.status = 'accepted'
        assignment.accepted_at = timezone.now()
        assignment.save()

        serializer = TaskAssignmentSerializer(assignment)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        完成任务
        执行人标记任务为已完成
        """
        task = self.get_object()

        # 查找当前用户在此任务中的分配
        assignment = TaskAssignment.objects.filter(
            task=task,
            user=request.user
        ).first()

        if not assignment:
            return Response(
                {'detail': '您未被分配到此任务'},
                status=status.HTTP_403_FORBIDDEN
            )

        if assignment.status != 'accepted':
            return Response(
                {'detail': f'任务状态为 {assignment.get_status_display()}，无法完成'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 更新分配状态
        assignment.status = 'completed'
        assignment.save()

        # 检查是否所有分配都已完成，如果是则更新任务状态
        all_assignments = task.assignments.all()
        if all(a.status == 'completed' for a in all_assignments):
            task.status = 'completed'
            task.save()

        serializer = TaskAssignmentSerializer(assignment)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'post'])
    def share(self, request, pk=None):
        """
        任务分享配置
        GET: 获取分享配置
        POST: 更新分享配置
        """
        task = self.get_object()

        if request.method == 'GET':
            # 返回分享信息
            serializer = TaskShareSerializer(task)
            return Response({
                'share_token': task.share_token,
                'share_fields': task.share_fields,
                'share_expires_at': task.share_expires_at,
                'is_share_valid': task.is_share_valid()
            })

        # POST: 更新分享配置
        serializer = TaskShareSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancel_share(self, request, pk=None):
        """
        取消分享
        清除分享令牌和配置
        """
        task = self.get_object()

        task.share_token = None
        task.share_fields = []
        task.share_expires_at = None
        task.save()

        return Response({'detail': '已取消分享'})


class TaskAssignmentViewSet(viewsets.ModelViewSet):
    """
    任务分配 API ViewSet
    提供任务分配的 CRUD 操作
    """
    queryset = TaskAssignment.objects.all()
    serializer_class = TaskAssignmentSerializer

    def get_queryset(self):
        """支持按任务、用户、角色过滤"""
        queryset = super().get_queryset()

        task_id = self.request.query_params.get('task')
        if task_id:
            queryset = queryset.filter(task_id=task_id)

        user_id = self.request.query_params.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        role_id = self.request.query_params.get('role')
        if role_id:
            queryset = queryset.filter(role_id=role_id)

        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset


class TaskCommentViewSet(viewsets.ModelViewSet):
    """
    任务评论 API ViewSet
    提供评论的 CRUD 操作
    """
    queryset = TaskComment.objects.all()
    serializer_class = TaskCommentSerializer

    def perform_create(self, serializer):
        """创建评论时自动设置作者"""
        serializer.save(author=self.request.user)

    def get_queryset(self):
        """支持按任务过滤"""
        queryset = super().get_queryset()

        task_id = self.request.query_params.get('task')
        if task_id:
            queryset = queryset.filter(task_id=task_id)

        return queryset


class TaskLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    任务日志 API ViewSet
    提供日志的只读访问
    """
    queryset = TaskLog.objects.all()
    serializer_class = TaskLogSerializer

    def get_queryset(self):
        """支持按任务、操作者过滤"""
        queryset = super().get_queryset()

        task_id = self.request.query_params.get('task')
        if task_id:
            queryset = queryset.filter(task_id=task_id)

        operator_id = self.request.query_params.get('operator')
        if operator_id:
            queryset = queryset.filter(operator_id=operator_id)

        action = self.request.query_params.get('action')
        if action:
            queryset = queryset.filter(action=action)

        return queryset