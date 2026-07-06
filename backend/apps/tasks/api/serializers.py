"""
Caduceus Tasks API Serializers
定义任务、任务分配、评论和日志的序列化器
"""
from rest_framework import serializers
from ..models import Task, TaskAssignment, TaskComment, TaskLog


class TaskAssignmentSerializer(serializers.ModelSerializer):
    """
    任务分配序列化器
    用于任务执行人信息的读取和展示
    """
    # 关联字段的只读展示
    user_name = serializers.CharField(source='user.username', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = TaskAssignment
        fields = [
            'id', 'task', 'user', 'user_name', 'role', 'role_name',
            'status', 'status_display', 'accepted_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'accepted_at', 'created_at', 'updated_at']


class TaskCommentSerializer(serializers.ModelSerializer):
    """
    任务评论序列化器
    用于评论的 CRUD 操作
    """
    # 作者信息的只读展示
    author_name = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = TaskComment
        fields = ['id', 'task', 'author', 'author_name', 'content', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']

    def create(self, validated_data):
        """
        创建评论时自动设置作者为当前用户
        需要在视图中通过 context 传递 request
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['author'] = request.user
        return super().create(validated_data)


class TaskLogSerializer(serializers.ModelSerializer):
    """
    任务变更日志序列化器
    用于日志信息的只读展示
    """
    operator_name = serializers.CharField(source='operator.username', read_only=True)

    class Meta:
        model = TaskLog
        fields = ['id', 'task', 'operator', 'operator_name', 'action', 'changes', 'created_at']
        read_only_fields = ['id', 'task', 'operator', 'action', 'changes', 'created_at']


class TaskSerializer(serializers.ModelSerializer):
    """
    任务序列化器
    用于任务信息的读取和展示
    """
    # 创建者信息的只读展示
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    # 嵌套展示任务分配信息
    assignments = TaskAssignmentSerializer(many=True, read_only=True)

    # 嵌套展示评论信息（最新的几条）
    recent_comments = serializers.SerializerMethodField()

    # 关联的资源数量
    resources_count = serializers.SerializerMethodField()

    # 关联的任务数量
    related_tasks_count = serializers.SerializerMethodField()

    # 管线的只读展示信息
    pipeline_name = serializers.CharField(source='pipeline.name', read_only=True, default=None)
    pipeline_nodes = serializers.SerializerMethodField()
    pipeline_edges = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'status_display',
            'creator', 'creator_name', 'pipeline', 'pipeline_name',
            'pipeline_nodes', 'pipeline_edges',
            'current_node',
            'fields', 'resources', 'resources_count',
            'related_tasks', 'related_tasks_count',
            'share_token', 'share_fields', 'share_expires_at',
            'assignments', 'recent_comments',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'creator', 'share_token', 'pipeline_name', 'pipeline_nodes',
            'pipeline_edges', 'created_at', 'updated_at'
        ]

    def get_recent_comments(self, obj):
        """获取最新的 5 条评论"""
        comments = obj.comments.all()[:5]
        return TaskCommentSerializer(comments, many=True).data

    def get_resources_count(self, obj):
        """获取关联资源数量"""
        return obj.resources.count()

    def get_related_tasks_count(self, obj):
        """获取关联任务数量"""
        return obj.related_tasks.count()

    def get_pipeline_nodes(self, obj):
        """获取关联管线的节点配置"""
        if obj.pipeline:
            return obj.pipeline.nodes
        return []

    def get_pipeline_edges(self, obj):
        """获取关联管线的连线配置"""
        if obj.pipeline:
            return obj.pipeline.edges
        return []


class TaskCreateSerializer(serializers.ModelSerializer):
    """
    任务创建序列化器
    用于创建新任务，包含初始化逻辑
    """
    # 执行人 ID 列表（可选，创建时直接分配）
    assignee_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text='执行人用户 ID 列表'
    )

    # 角色 ID 列表（与 assignee_ids 对应）
    role_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text='角色 ID 列表，与 assignee_ids 一一对应'
    )

    class Meta:
        model = Task
        fields = [
            'title', 'description', 'status', 'pipeline',
            'fields', 'current_node', 'assignee_ids', 'role_ids'
        ]

    def validate(self, data):
        """验证执行人和角色列表的对应关系"""
        assignee_ids = data.get('assignee_ids', [])
        role_ids = data.get('role_ids', [])

        if assignee_ids and role_ids:
            if len(assignee_ids) != len(role_ids):
                raise serializers.ValidationError('执行人列表和角色列表长度必须一致')

        return data

    def create(self, validated_data):
        """
        创建任务并分配执行人
        如果绑定管线，自动从管线节点中提取字段配置初始化 fields
        """
        # 提取分配信息
        assignee_ids = validated_data.pop('assignee_ids', [])
        role_ids = validated_data.pop('role_ids', [])

        # 设置创建者
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['creator'] = request.user

        # 如果绑定了管线但 fields 为空，从管线节点中自动初始化
        pipeline = validated_data.get('pipeline')
        fields = validated_data.get('fields', [])
        if pipeline and not fields:
            validated_data['fields'] = self._build_fields_from_pipeline(pipeline)

        # 如果绑定了管线且未指定 current_node，自动设为管线第一个节点 id
        if validated_data.get('pipeline') and not validated_data.get('current_node'):
            pipeline = validated_data['pipeline']
            if pipeline.nodes and len(pipeline.nodes) > 0:
                validated_data['current_node'] = pipeline.nodes[0].get('id', '')

        # 创建任务
        task = Task.objects.create(**validated_data)

        # 创建任务分配
        if assignee_ids and role_ids:
            from django.contrib.auth import get_user_model
            from apps.accounts.models import Role

            User = get_user_model()
            for user_id, role_id in zip(assignee_ids, role_ids):
                try:
                    user = User.objects.get(id=user_id)
                    role = Role.objects.get(id=role_id) if role_id else None
                    TaskAssignment.objects.create(
                        task=task,
                        user=user,
                        role=role
                    )
                except (User.DoesNotExist, Role.DoesNotExist):
                    pass

        return task

    def _build_fields_from_pipeline(self, pipeline):
        """
        从管线所有节点中展平 fields_config 为任务的字段列表
        去重逻辑：相同 key 的字段只保留第一个
        """
        fields = []
        seen_keys = set()
        for node in pipeline.nodes:
            for field_config in node.get('fields_config', []):
                key = field_config.get('key')
                if key and key not in seen_keys:
                    seen_keys.add(key)
                    fields.append({
                        'key': key,
                        'label': field_config.get('label', key),
                        'type': field_config.get('type', 'text'),
                        'value': '',
                        'priority_roles': field_config.get('priority_roles', []),
                        'is_public': field_config.get('is_public', False)
                    })
        return fields


class TaskUpdateSerializer(serializers.ModelSerializer):
    """
    任务更新序列化器
    用于更新任务信息，不包含分配逻辑
    """
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'status', 'pipeline',
            'current_node',
            'fields', 'resources', 'related_tasks',
            'share_fields', 'share_expires_at'
        ]

    def update(self, instance, validated_data):
        """更新任务，并记录变更"""
        # 记录变更前的状态
        old_status = instance.status

        # 更新任务
        instance = super().update(instance, validated_data)

        # 如果状态变更，记录日志（通过 signals 自动完成）
        return instance


class TaskShareSerializer(serializers.ModelSerializer):
    """
    任务分享序列化器
    用于生成和更新分享配置
    """
    class Meta:
        model = Task
        fields = ['share_fields', 'share_expires_at']

    def update(self, instance, validated_data):
        """更新分享配置"""
        instance.share_fields = validated_data.get('share_fields', instance.share_fields)
        instance.share_expires_at = validated_data.get('share_expires_at', instance.share_expires_at)
        instance.save()
        return instance