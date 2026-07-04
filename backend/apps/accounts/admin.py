"""
Caduceus Accounts Admin 配置
在 Django Admin 中管理用户、角色、小组和角色分配
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Role, Group, RoleAssignment


# 角色分配内联，嵌入到用户 Admin 中
class RoleAssignmentInline(admin.TabularInline):
    """
    角色分配内联表
    在用户详情页中直接管理该用户的角色分配
    """
    model = RoleAssignment
    extra = 1
    fields = ('role', 'group', 'is_supervisor')


# 自定义用户 Admin，继承 Django 默认 UserAdmin
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    用户管理界面
    继承 Django UserAdmin，添加 profile 字段展示
    """
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions')

    fieldsets = BaseUserAdmin.fieldsets + (
        ('扩展信息', {'fields': ('profile',)}),
    )

    # 内联显示角色分配，方便直接管理用户角色
    inlines = [RoleAssignmentInline]


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """
    角色管理界面
    管理员可在此创建/修改角色类型
    """
    list_display = ('name', 'role_type', 'description')
    list_filter = ('role_type',)
    search_fields = ('name', 'description')


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """
    业务小组管理界面
    管理员可在此创建/修改业务小组
    """
    list_display = ('name', 'description')
    search_fields = ('name', 'description')


@admin.register(RoleAssignment)
class RoleAssignmentAdmin(admin.ModelAdmin):
    """
    角色分配管理界面
    管理用户-角色-小组的关联关系
    """
    list_display = ('user', 'role', 'group', 'is_supervisor')
    list_filter = ('role', 'group', 'is_supervisor')
    search_fields = ('user__username', 'role__name', 'group__name')
    raw_id_fields = ('user',)  # 用户下拉框改为 ID 输入，适合大量用户场景