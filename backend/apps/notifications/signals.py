"""
Caduceus 通知模块信号处理
监听 TaskLog 的创建事件，自动生成对应的 Notification
并通过 WebSocket 实时推送给任务创建者
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.tasks.models import TaskLog
from apps.notifications.models import Notification
from apps.notifications.backends import WebSocketBackend

# action → notification type 映射表
ACTION_TYPE_MAP = {
    'created': 'task_updated',
    'updated': 'task_updated',
    'assigned': 'task_assigned',
    'assignment_status_changed': 'task_assigned',
    'commented': 'comment_added',
}

# 通知类型 → 标题模板映射表
TITLE_TEMPLATES = {
    'task_updated': '任务「{title}」有新更新',
    'task_assigned': '任务「{title}」指派有变更',
    'comment_added': '任务「{title}」有新评论',
}


def _build_content_summary(action, changes, operator_name):
    """
    根据变更详情构建通知内容摘要
    将 JSON 格式的 changes 字典转为可读文本

    Args:
        action: 操作类型字符串
        changes: 变更详情字典 (JSONB)
        operator_name: 操作者用户名

    Returns:
        格式化的变更摘要字符串
    """
    if not changes:
        return f'{operator_name} 执行了操作: {action}'

    lines = [f'{operator_name} 执行了以下变更:']
    for field, detail in changes.items():
        if isinstance(detail, dict):
            old_val = detail.get('old', '')
            new_val = detail.get('new', '')
            if old_val and new_val:
                lines.append(f'  · {field}: 「{old_val}」→「{new_val}」')
            elif new_val:
                lines.append(f'  · {field}: 设置为「{new_val}」')
            elif old_val:
                lines.append(f'  · {field}: 清除了「{old_val}」')
        else:
            lines.append(f'  · {field}: {detail}')
    return '\n'.join(lines)


def _get_notification_type(action):
    """
    根据 TaskLog 的 action 获取对应的通知类型
    未匹配的 action 默认返回 task_updated

    Args:
        action: TaskLog 操作类型字符串

    Returns:
        通知类型字符串
    """
    return ACTION_TYPE_MAP.get(action, 'task_updated')


def _get_title(notification_type, task_title):
    """
    根据通知类型和任务标题生成模板化标题

    Args:
        notification_type: 通知类型字符串
        task_title: 任务标题

    Returns:
        格式化的通知标题字符串
    """
    template = TITLE_TEMPLATES.get(notification_type, '任务「{title}」有新更新')
    return template.format(title=task_title)


@receiver(post_save, sender=TaskLog)
def create_notification_from_task_log(sender, instance, created, **kwargs):
    """
    监听 TaskLog 创建事件，自动生成并推送对应通知
    仅在 TaskLog 首次创建（created=True）时触发，
    避免更新日志时重复创建通知

    Args:
        sender: 信号发送者模型类 (TaskLog)
        instance: 新创建的 TaskLog 实例
        created: 是否为新建操作
    """
    if not created:
        return

    task = instance.task
    notification_type = _get_notification_type(instance.action)
    title = _get_title(notification_type, task.title)
    content = _build_content_summary(
        instance.action,
        instance.changes,
        instance.operator.username if instance.operator else '系统'
    )

    notification = Notification.objects.create(
        recipient=task.creator,
        type=notification_type,
        title=title,
        content=content,
        link=f'/tasks/{task.id}',
    )

    # 通过 WebSocket 实时推送给接收者
    WebSocketBackend().send(notification)
