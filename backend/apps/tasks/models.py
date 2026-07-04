"""
Caduceus Tasks 模块数据模型
定义任务、任务分配、评论和变更日志等核心业务实体
"""
from django.db import models
from django.conf import settings
import uuid


class Task(models.Model):
    """
    任务模型 - 协同工作的基本单元
    所有参与角色共享任务全部信息，字段全局共享（非节点独占）
    """
    # 任务标题和描述
    title = models.CharField(max_length=200, verbose_name='标题')
    description = models.TextField(blank=True, verbose_name='描述')

    # 任务状态：草稿 → 待处理 → 进行中 → 已完成 / 已取消
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', '草稿'),
            ('pending', '待处理'),
            ('in_progress', '进行中'),
            ('completed', '已完成'),
            ('cancelled', '已取消')
        ],
        default='draft',
        verbose_name='状态'
    )

    # 发起人（创建者）
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tasks',
        verbose_name='发起人'
    )

    # 关联的管线（可选）
    pipeline = models.ForeignKey(
        'pipeline.Pipeline',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='关联管线'
    )

    # 自定义字段（JSONB 数组，全局共享）
    # 字段值全局唯一，每个字段含 key/label/type/value/priority_roles/is_public
    # 示例：[{"key":"visit_unit","label":"来访单位","type":"text","value":"XXX公司","priority_roles":[],"is_public":true}]
    fields = models.JSONField(default=list, blank=True, verbose_name='自定义字段')

    # 关联资源（多对多）
    resources = models.ManyToManyField(
        'resources.ResourceItem',
        blank=True,
        verbose_name='关联资源'
    )

    # 关联任务（多对多，自引用）
    # 用于角色级任务合并展示
    related_tasks = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=True,
        verbose_name='关联任务'
    )

    # 公开分享令牌（UUID）
    share_token = models.UUIDField(
        default=uuid.uuid4,
        null=True,
        blank=True,
        unique=True,
        verbose_name='分享令牌'
    )

    # 分享时展示的字段配置
    share_fields = models.JSONField(default=list, blank=True, verbose_name='分享字段配置')

    # 分享链接过期时间
    share_expires_at = models.DateTimeField(null=True, blank=True, verbose_name='分享过期时间')

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '任务'
        verbose_name_plural = '任务'
        db_table = 'tasks_task'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def is_share_valid(self):
        """检查分享链接是否有效（未过期）"""
        if not self.share_token:
            return False
        if self.share_expires_at and self.share_expires_at < timezone.now():
            return False
        return True


class TaskAssignment(models.Model):
    """
    任务执行人关联模型
    支持多执行人以不同角色参与同一任务
    """
    # 关联任务
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name='任务'
    )

    # 执行人
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='执行人'
    )

    # 执行人参与的角色
    role = models.ForeignKey(
        'accounts.Role',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='角色'
    )

    # 执行人状态：待处理 → 已接取 → 已完成
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', '待处理'),
            ('accepted', '已接取'),
            ('completed', '已完成')
        ],
        default='pending',
        verbose_name='执行状态'
    )

    # 接取时间（抢单模式的接取时间）
    accepted_at = models.DateTimeField(null=True, blank=True, verbose_name='接取时间')

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '任务分配'
        verbose_name_plural = '任务分配'
        db_table = 'tasks_assignment'
        # 同一任务中同一用户以同一角色只能分配一次
        unique_together = ['task', 'user', 'role']

    def __str__(self):
        return f'{self.task.title} - {self.user.username} ({self.role.name if self.role else "无角色"})'


class TaskComment(models.Model):
    """
    任务评论模型
    执行人可在任务下发布评论进行协作沟通
    """
    # 关联任务
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='任务'
    )

    # 评论作者
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='作者'
    )

    # 评论内容
    content = models.TextField(verbose_name='内容')

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '任务评论'
        verbose_name_plural = '任务评论'
        db_table = 'tasks_comment'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.task.title} - {self.author.username}: {self.content[:30]}...'


class TaskLog(models.Model):
    """
    任务变更日志模型
    完整记录每次修改，方便追溯历史
    """
    # 关联任务
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name='任务'
    )

    # 操作者
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='操作者'
    )

    # 操作类型：created, updated, status_changed, assigned, commented 等
    action = models.CharField(max_length=50, verbose_name='操作类型')

    # 变更详情（JSONB 格式，记录旧值→新值的 diff）
    changes = models.JSONField(default=dict, blank=True, verbose_name='变更详情')

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '任务日志'
        verbose_name_plural = '任务日志'
        db_table = 'tasks_log'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.task.title} - {self.action} by {self.operator.username}'


# 导入 timezone 用于 is_share_valid 方法
from django.utils import timezone