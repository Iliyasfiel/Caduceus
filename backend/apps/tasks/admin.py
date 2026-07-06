"""
Caduceus Tasks Admin 配置
在 Django Admin 中管理任务、分配、评论和日志
"""
from django.contrib import admin
from .models import Task, TaskAssignment, TaskComment, TaskLog


class TaskAssignmentInline(admin.TabularInline):
    """
    任务分配内联表
    在任务详情页中直接管理执行人分配
    """
    model = TaskAssignment
    extra = 1
    fields = ('user', 'role', 'status', 'accepted_at')
    raw_id_fields = ('user', 'role')


class TaskCommentInline(admin.TabularInline):
    """
    任务评论内联表
    在任务详情页中查看评论（只读）
    """
    model = TaskComment
    extra = 0
    fields = ('author', 'content', 'created_at')
    readonly_fields = ('author', 'content', 'created_at')

    # 评论只能查看，不能在 Admin 中添加
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    任务管理界面
    提供任务的列表展示和详情编辑
    """
    list_display = ('title', 'status', 'creator', 'pipeline', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description', 'creator__username')
    raw_id_fields = ('creator', 'pipeline')
    filter_horizontal = ('resources', 'related_tasks')
    readonly_fields = ('share_token', 'created_at', 'updated_at')

    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'description', 'status', 'creator')
        }),
        ('管线关联', {
            'fields': ('pipeline',),
            'classes': ('collapse',)
        }),
        ('自定义字段', {
            'fields': ('fields',)
        }),
        ('资源关联', {
            'fields': ('resources',),
            'classes': ('collapse',)
        }),
        ('任务关联', {
            'fields': ('related_tasks',),
            'classes': ('collapse',)
        }),
        ('分享设置', {
            'fields': ('share_token', 'share_fields', 'share_expires_at'),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # 内联显示执行人分配
    inlines = [TaskAssignmentInline, TaskCommentInline]


@admin.register(TaskAssignment)
class TaskAssignmentAdmin(admin.ModelAdmin):
    """
    任务分配管理界面
    管理任务与执行人的关联
    """
    list_display = ('task', 'user', 'role', 'status', 'accepted_at')
    list_filter = ('status', 'role')
    search_fields = ('task__title', 'user__username')
    raw_id_fields = ('task', 'user', 'role')


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    """
    任务评论管理界面
    管理任务下的评论
    """
    list_display = ('task', 'author', 'content_short', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('task__title', 'author__username', 'content')
    raw_id_fields = ('task', 'author')

    def content_short(self, obj):
        """显示评论内容的前 50 个字符"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_short.short_description = '内容摘要'


@admin.register(TaskLog)
class TaskLogAdmin(admin.ModelAdmin):
    """
    任务变更日志管理界面
    仅用于查看日志，不允许编辑
    """
    list_display = ('task', 'action', 'operator', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('task__title', 'operator__username')
    raw_id_fields = ('task', 'operator')

    # 日志只读，不允许添加/修改/删除
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False