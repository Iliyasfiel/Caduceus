"""
Caduceus 站内通知模块数据模型
定义站内通知实体，支持 WebSocket 实时推送
"""
from django.db import models
from django.conf import settings


class Notification(models.Model):
    """
    站内通知
    关联接收者用户，记录任务变更、指派、评论等事件
    通过 WebSocket 后端实时推送到前端
    """
    # 接收者 - 通知的接收用户
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='接收者'
    )

    # 通知类型
    type = models.CharField(
        max_length=50,
        choices=[
            ('task_assigned', '任务指派'),
            ('task_updated', '任务更新'),
            ('comment_added', '新增评论'),
            ('stage_changed', '阶段变更'),
        ],
        verbose_name='通知类型'
    )

    # 通知标题
    title = models.CharField(max_length=200, verbose_name='标题')

    # 通知内容
    content = models.TextField(blank=True, verbose_name='内容')

    # 点击跳转链接
    link = models.CharField(max_length=500, blank=True, verbose_name='跳转链接')

    # 已读标记
    is_read = models.BooleanField(default=False, verbose_name='已读')

    # 创建时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '通知'
        verbose_name_plural = '通知'
        db_table = 'notifications_notification'
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.get_type_display()}] {self.title}'