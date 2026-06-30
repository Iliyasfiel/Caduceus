"""
Caduceus Pipeline 模块数据模型
定义管线和管线实例等核心业务实体
Phase 2 待实现，此处为占位模型
"""
from django.db import models
from django.conf import settings


class Pipeline(models.Model):
    """
    管线模型（占位）
    定义工作流程的可执行模板
    Phase 2 将完善实现
    """
    # 管线名称
    name = models.CharField(max_length=100, verbose_name='名称')

    # 管线描述
    description = models.TextField(blank=True, verbose_name='描述')

    # 管线定义（JSONB 格式，包含节点、连接等信息）
    definition = models.JSONField(default=dict, blank=True, verbose_name='管线定义')

    # 创建者
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_pipelines',
        verbose_name='创建者'
    )

    # 是否启用
    is_active = models.BooleanField(default=True, verbose_name='是否启用')

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '管线'
        verbose_name_plural = '管线'
        db_table = 'pipeline_pipeline'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class PipelineInstance(models.Model):
    """
    管线实例模型（占位）
    记录管线的具体执行实例
    Phase 2 将完善实现
    """
    # 关联管线
    pipeline = models.ForeignKey(
        Pipeline,
        on_delete=models.CASCADE,
        related_name='instances',
        verbose_name='管线'
    )

    # 关联任务
    task = models.OneToOneField(
        'tasks.Task',
        on_delete=models.CASCADE,
        related_name='pipeline_instance',
        verbose_name='关联任务'
    )

    # 执行状态
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', '待执行'),
            ('running', '执行中'),
            ('completed', '已完成'),
            ('failed', '已失败'),
            ('cancelled', '已取消')
        ],
        default='pending',
        verbose_name='状态'
    )

    # 当前节点位置
    current_node = models.CharField(max_length=50, blank=True, verbose_name='当前节点')

    # 执行历史（JSONB 格式，记录节点执行情况）
    execution_history = models.JSONField(default=list, blank=True, verbose_name='执行历史')

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '管线实例'
        verbose_name_plural = '管线实例'
        db_table = 'pipeline_instance'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.pipeline.name} - {self.task.title}'