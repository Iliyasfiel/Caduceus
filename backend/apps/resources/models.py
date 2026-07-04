"""
Caduceus Resources 模块数据模型
定义资源类型和资源项等核心业务实体
Phase 4 待实现，此处为占位模型
"""
from django.db import models
from django.conf import settings


class ResourceType(models.Model):
    """
    资源类型模型（占位）
    定义资源的分类模板
    Phase 4 将完善实现
    """
    # 资源类型名称
    name = models.CharField(max_length=50, verbose_name='名称')

    # 资源类型描述
    description = models.TextField(blank=True, verbose_name='描述')

    # 资源类型图标（可选）
    icon = models.CharField(max_length=50, blank=True, verbose_name='图标')

    # 字段定义（JSONB 格式，定义该类型资源的字段结构）
    field_schema = models.JSONField(default=dict, blank=True, verbose_name='字段定义')

    # 生命周期配置（JSONB 格式，定义资源状态流转和事件通知）
    lifecycle_config = models.JSONField(default=dict, blank=True, verbose_name='生命周期配置')

    # 是否启用
    is_active = models.BooleanField(default=True, verbose_name='是否启用')

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '资源类型'
        verbose_name_plural = '资源类型'
        db_table = 'resources_type'
        ordering = ['name']

    def __str__(self):
        return self.name


class ResourceItem(models.Model):
    """
    资源项模型（占位）
    定义具体的资源实例
    Phase 4 将完善实现
    """
    # 关联资源类型
    resource_type = models.ForeignKey(
        ResourceType,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='资源类型'
    )

    # 资源名称
    name = models.CharField(max_length=100, verbose_name='名称')

    # 资源描述
    description = models.TextField(blank=True, verbose_name='描述')

    # 资源字段值（JSONB 格式，根据 resource_type.field_schema 存储）
    field_values = models.JSONField(default=dict, blank=True, verbose_name='字段值')

    # 资源状态
    status = models.CharField(
        max_length=20,
        choices=[
            ('available', '可用'),
            ('reserved', '已预约'),
            ('in_use', '使用中'),
            ('maintenance', '维护中'),
            ('unavailable', '不可用')
        ],
        default='available',
        verbose_name='状态'
    )

    # 资源位置（可选）
    location = models.CharField(max_length=100, blank=True, verbose_name='位置')

    # 创建者
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_resources',
        verbose_name='创建者'
    )

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '资源项'
        verbose_name_plural = '资源项'
        db_table = 'resources_item'
        ordering = ['resource_type', 'name']

    def __str__(self):
        return f'{self.resource_type.name} - {self.name}'


class ResourceLog(models.Model):
    """
    资源事件日志模型
    记录资源的生命周期事件（创建、调度、故障上报、维修等）
    每条日志关联一个资源项，记录事件类型、操作人和摘要信息
    """
    resource = models.ForeignKey(
        ResourceItem,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name='所属资源'
    )
    event_key = models.CharField(max_length=50, verbose_name='事件类型')
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='操作人'
    )
    summary = models.TextField(blank=True, verbose_name='事件摘要')
    details = models.JSONField(default=dict, blank=True, verbose_name='扩展详情')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')

    class Meta:
        verbose_name = '资源事件日志'
        verbose_name_plural = '资源事件日志'
        db_table = 'resources_log'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.resource.name} - {self.event_key}'