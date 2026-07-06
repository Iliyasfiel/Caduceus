"""
Caduceus Pipeline 模块数据模型
定义管线模板与管线运行实例的核心业务实体
管线定义的是信息流而非工作流——画布上只有一种任务节点
"""
from django.db import models
from django.conf import settings


class Pipeline(models.Model):
    """
    管线模板 - 定义信息流结构
    画布上只有"任务节点"一种视觉元素，每个节点内部配置字段、角色和资源类型
    节点间通过 edges 表达阶段推进方向
    """
    # 管线名称
    name = models.CharField(max_length=200, verbose_name='管线名称')

    # 管线描述
    description = models.TextField(blank=True, verbose_name='描述')

    # 任务节点配置（JSONB 数组）
    # nodes 结构：[{
    #   "id": "node_1",
    #   "label": "前期准备",
    #   "fields_config": [
    #     {"key":"visit_unit","label":"来访单位","type":"text","priority_roles":[],"is_public":true}
    #   ],
    #   "roles": [
    #     {"role_id": 1, "merge_default": true, "merge_time_window": 30}
    #   ],
    #   "resource_types": [1, 2]
    # }]
    nodes = models.JSONField(default=list, blank=True, verbose_name='任务节点配置')

    # 节点间连线（JSONB 数组），表达阶段推进方向
    # edges 结构：[{"id":"edge_1","source":"node_1","target":"node_2"}]
    edges = models.JSONField(default=list, blank=True, verbose_name='阶段连接')

    # 创建者
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_pipelines',
        verbose_name='创建者'
    )

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
    管线运行实例 - 与任务一对一关联
    current_node 为参考性标记，不锁定其他节点的信息修改
    """
    # 关联管线模板
    pipeline = models.ForeignKey(
        Pipeline,
        on_delete=models.CASCADE,
        related_name='instances',
        verbose_name='管线'
    )

    # 关联任务（一对一）
    task = models.OneToOneField(
        'tasks.Task',
        on_delete=models.CASCADE,
        related_name='pipeline_instance',
        verbose_name='关联任务'
    )

    # 当前所处节点 ID（参考性标记，不锁定其他节点）
    current_node = models.CharField(max_length=100, blank=True, verbose_name='当前阶段')

    # 实例状态
    status = models.CharField(
        max_length=20,
        choices=[
            ('running', '运行中'),
            ('completed', '已完成')
        ],
        default='running',
        verbose_name='状态'
    )

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