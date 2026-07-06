"""
Caduceus Resources 信号处理模块
定义资源事件日志保存后的状态自动推导和通知联动逻辑
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ResourceLog
from apps.notifications.models import Notification
from apps.accounts.models import Role, RoleAssignment


@receiver(post_save, sender=ResourceLog)
def on_resource_log_saved(sender, instance, created, **kwargs):
    """
    ResourceLog 保存后信号处理
    1. 根据 lifecycle_config 自动推导并更新资源状态
    2. 根据 notify_roles 配置向对应角色用户发送通知
    """
    if not created:
        return

    resource = instance.resource
    resource_type = resource.resource_type
    lifecycle_config = resource_type.lifecycle_config or {}
    events = lifecycle_config.get('events', [])

    if not events:
        return

    # 查找匹配 event_key 的事件配置
    matched_event = None
    for event in events:
        if event.get('key') == instance.event_key:
            matched_event = event
            break

    if matched_event is None:
        return

    # 1. 根据 lifecycle_config 自动推导并更新资源状态
    # 如果配置了 status_value 则使用，否则使用 event_key 自身
    status_value = matched_event.get('status_value', instance.event_key)
    if resource.status != status_value:
        resource.status = status_value
        resource.save(update_fields=['status'])

    # 2. 通知联动：查找需要通知的角色并发送通知
    notify_roles = matched_event.get('notify_roles', [])
    if not notify_roles:
        return

    # 获取事件显示名称
    event_label = matched_event.get('label', instance.event_key)

    # 查询需要通知的角色对应的所有用户
    roles = Role.objects.filter(name__in=notify_roles)
    role_ids = roles.values_list('id', flat=True)
    user_ids = RoleAssignment.objects.filter(
        role_id__in=role_ids
    ).values_list('user_id', flat=True).distinct()

    # 为每个符合条件的用户创建通知
    operator = instance.operator
    summary = instance.summary or ''
    notifications = [
        Notification(
            recipient_id=user_id,
            type='resource_changed',
            title=f'{resource.name} - {event_label}',
            content=f'操作人: {operator.username}，摘要: {summary}',
            link=f'/resources/{resource.id}'
        )
        for user_id in user_ids
    ]

    if notifications:
        Notification.objects.bulk_create(notifications)
