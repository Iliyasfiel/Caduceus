"""
Caduceus Tasks 信号处理
自动记录任务变更日志
"""
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Task, TaskAssignment, TaskComment, TaskLog


def get_current_user():
    """
    获取当前操作用户
    在信号处理中通过 threadlocals 或其他方式获取
    注意：在 Django 信号中直接获取 request.user 较为困难，
    建议在视图层手动调用日志记录函数
    """
    # TODO: 实现更完善的用户追踪机制
    # 可以通过 django-threadlocals 或自定义 middleware 实现
    return None


def create_task_log(task, action, operator=None, changes=None):
    """
    创建任务日志的辅助函数
    可在视图层手动调用，确保准确记录操作者
    """
    if operator is None:
        operator = get_current_user()

    if operator is None:
        # 如果无法获取操作者，跳过日志记录
        return None

    return TaskLog.objects.create(
        task=task,
        operator=operator,
        action=action,
        changes=changes or {}
    )


@receiver(post_save, sender=Task)
def log_task_creation(sender, instance, created, **kwargs):
    """
    记录任务创建
    当新任务创建时自动生成日志
    """
    if created:
        # 创建日志（需要通过视图层传递操作者）
        # 这里仅作为示例，实际应通过视图层调用
        # create_task_log(
        #     instance,
        #     action='created',
        #     changes={
        #         'title': instance.title,
        #         'status': instance.status,
        #         'creator': instance.creator.username if instance.creator else None
        #     }
        # )
        pass


@receiver(post_save, sender=Task)
def log_task_update(sender, instance, created, **kwargs):
    """
    记录任务更新
    当任务信息更新时自动生成日志
    """
    if not created:
        # 更新日志（需要通过视图层传递操作者）
        # 这里仅作为示例，实际应通过视图层调用
        # create_task_log(
        #     instance,
        #     action='updated',
        #     changes={
        #         'title': instance.title,
        #         'status': instance.status
        #     }
        # )
        pass


@receiver(post_save, sender=TaskAssignment)
def log_task_assignment(sender, instance, created, **kwargs):
    """
    记录任务分配变更
    当执行人分配创建或更新时自动生成日志
    """
    if created:
        # 分配日志（需要通过视图层传递操作者）
        # create_task_log(
        #     instance.task,
        #     action='assigned',
        #     changes={
        #         'user': instance.user.username,
        #         'role': instance.role.name if instance.role else None,
        #         'status': instance.status
        #     }
        # )
        pass
    else:
        # 状态变更日志
        # create_task_log(
        #     instance.task,
        #     action='assignment_status_changed',
        #     changes={
        #         'user': instance.user.username,
        #         'role': instance.role.name if instance.role else None,
        #         'old_status': kwargs.get('old_status', 'unknown'),
        #         'new_status': instance.status
        #     }
        # )
        pass


@receiver(post_delete, sender=TaskAssignment)
def log_task_unassignment(sender, instance, **kwargs):
    """
    记录任务分配取消
    当执行人分配删除时自动生成日志
    """
    # 取消分配日志
    # create_task_log(
    #     instance.task,
    #     action='unassigned',
    #     changes={
    #         'user': instance.user.username,
    #         'role': instance.role.name if instance.role else None
    #     }
    # )
    pass


@receiver(post_save, sender=TaskComment)
def log_task_comment(sender, instance, created, **kwargs):
    """
    记录任务评论
    当评论创建时自动生成日志
    """
    if created:
        # 评论日志
        # create_task_log(
        #     instance.task,
        #     operator=instance.author,
        #     action='commented',
        #     changes={
        #         'content': instance.content[:100]  # 截取前 100 字符
        #     }
        # )
        pass


@receiver(m2m_changed, sender=Task.related_tasks.through)
def log_task_relation_change(sender, instance, action, pk_set, **kwargs):
    """
    记录任务关联变更
    当任务关联关系变更时自动生成日志
    """
    if action == 'post_add':
        # 添加关联
        # create_task_log(
        #     instance,
        #     action='related_tasks_added',
        #     changes={
        #         'related_task_ids': list(pk_set)
        #     }
        # )
        pass
    elif action == 'post_remove':
        # 移除关联
        # create_task_log(
        #     instance,
        #     action='related_tasks_removed',
        #     changes={
        #         'related_task_ids': list(pk_set)
        #     }
        # )
        pass


@receiver(m2m_changed, sender=Task.resources.through)
def log_task_resource_change(sender, instance, action, pk_set, **kwargs):
    """
    记录任务资源变更
    当任务资源关联变更时自动生成日志
    """
    if action == 'post_add':
        # 添加资源
        # create_task_log(
        #     instance,
        #     action='resources_added',
        #     changes={
        #         'resource_ids': list(pk_set)
        #     }
        # )
        pass
    elif action == 'post_remove':
        # 移除资源
        # create_task_log(
        #     instance,
        #     action='resources_removed',
        #     changes={
        #         'resource_ids': list(pk_set)
        #     }
        # )
        pass


@receiver(post_save, sender=TaskLog)
def on_task_stage_completed(sender, instance, created, **kwargs):
    """
    TaskLog 保存后信号处理
    检测 current_node 变更 → 查找下一阶段角色 → 创建通知
    """
    if not created:
        return

    changes = instance.changes or {}
    if 'current_node' not in changes:
        return

    new_node = changes.get('current_node')
    old_node = changes.get('old_current_node', '')

    if new_node == 'completed' or not new_node:
        return

    task = instance.task
    pipeline = task.pipeline
    if not pipeline:
        return

    nodes = pipeline.nodes or []
    current_node_config = None
    for node in nodes:
        if node.get('id') == new_node:
            current_node_config = node
            break

    if not current_node_config:
        return

    node_roles = current_node_config.get('roles', [])
    if not node_roles:
        return

    current_idx = None
    current_label = current_node_config.get('label', new_node)
    for i, node in enumerate(nodes):
        if node.get('id') == new_node:
            current_idx = i
            break

    next_label = ''
    if current_idx is not None and current_idx < len(nodes) - 1:
        next_label = nodes[current_idx + 1].get('label', '')

    from apps.accounts.models import RoleAssignment
    role_ids = [r.get('role_id') for r in node_roles if r.get('role_id')]
    if not role_ids:
        return

    user_ids = RoleAssignment.objects.filter(
        role_id__in=role_ids
    ).values_list('user_id', flat=True).distinct()

    if not user_ids:
        return

    from apps.notifications.models import Notification

    title = f'阶段「{current_label}」进行中'
    content = ''
    if next_label:
        content = f'可以开始处理「{next_label}」阶段的任务了'
    else:
        content = f'当前阶段：{current_label}'

    notifications = [
        Notification(
            recipient_id=user_id,
            type='stage_completed',
            title=title,
            content=content,
            link=f'/tasks/{task.id}'
        )
        for user_id in user_ids
    ]

    if notifications:
        Notification.objects.bulk_create(notifications)