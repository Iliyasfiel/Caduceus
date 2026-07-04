"""
Caduceus Accounts 模块数据模型
定义用户、角色、角色分配和业务小组等核心实体
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    用户模型 - 基础账号
    继承 Django AbstractUser，后续通过 RoleAssignment 分配角色权限
    profile 字段用于存储扩展信息（如联系方式等）
    """
    # 扩展信息（JSON 格式，灵活存储）
    profile = models.JSONField(default=dict, blank=True, verbose_name='扩展信息')

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        db_table = 'accounts_user'

    def __str__(self):
        return self.username

    def get_roles(self):
        """获取用户拥有的所有角色"""
        return [assignment.role for assignment in self.role_assignments.all()]

    def get_groups(self):
        """获取用户所属的所有业务小组"""
        return [assignment.group for assignment in self.role_assignments.filter(group__isnull=False)]


class Role(models.Model):
    """
    角色定义 - 由管理员预设
    如：讲解员、接待员、司机、会务等
    """
    name = models.CharField(max_length=100, verbose_name='角色名称')
    role_type = models.CharField(
        max_length=20,
        choices=[
            ('initiator', '发起人'),
            ('executor', '执行人'),
            ('admin', '管理员')
        ],
        verbose_name='角色类型'
    )
    description = models.TextField(blank=True, verbose_name='描述')

    class Meta:
        verbose_name = '角色'
        verbose_name_plural = '角色'
        db_table = 'accounts_role'

    def __str__(self):
        return self.name


class Group(models.Model):
    """
    业务小组 - 如"讲解组"、"车队"、"接待组"
    用于组织相同业务角色的用户
    """
    name = models.CharField(max_length=100, verbose_name='组名称')
    description = models.TextField(blank=True, verbose_name='描述')

    class Meta:
        verbose_name = '业务小组'
        verbose_name_plural = '业务小组'
        db_table = 'accounts_group'

    def __str__(self):
        return self.name


class RoleAssignment(models.Model):
    """
    用户-角色关联 - 一个用户可拥有多个角色
    同时可关联业务小组，并标记是否为该组主管
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='role_assignments',
        verbose_name='用户'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        verbose_name='角色'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='所属小组'
    )
    is_supervisor = models.BooleanField(
        default=False,
        verbose_name='是否主管'
    )

    class Meta:
        verbose_name = '角色分配'
        verbose_name_plural = '角色分配'
        db_table = 'accounts_role_assignment'
        # 防止同一用户在同一组中重复分配同一角色
        unique_together = ['user', 'role', 'group']

    def __str__(self):
        group_name = self.group.name if self.group else '无组'
        supervisor_tag = ' (主管)' if self.is_supervisor else ''
        return f'{self.user.username} - {self.role.name}@{group_name}{supervisor_tag}'