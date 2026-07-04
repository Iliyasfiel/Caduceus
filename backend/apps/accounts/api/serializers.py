"""
Caduceus Accounts API Serializers
定义用户、角色、小组和角色分配的序列化器
"""
from rest_framework import serializers
from ..models import User, Role, Group, RoleAssignment


class UserSerializer(serializers.ModelSerializer):
    """
    用户序列化器
    用于用户信息的读取和展示
    """
    # 嵌套展示用户的角色分配
    role_assignments = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile', 'is_active', 'is_staff', 'role_assignments']
        read_only_fields = ['id', 'is_active', 'is_staff']

    def get_role_assignments(self, obj):
        """获取用户的角色分配列表"""
        assignments = obj.role_assignments.all()
        return RoleAssignmentSerializer(assignments, many=True).data


class UserCreateSerializer(serializers.ModelSerializer):
    """
    用户创建序列化器
    用于创建新用户，包含密码字段
    """
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'profile']

    def validate(self, data):
        """验证两次密码输入一致"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError('两次密码输入不一致')
        return data

    def create(self, validated_data):
        """创建用户，使用 set_password 加密密码"""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    用户更新序列化器
    用于更新用户信息，不含密码字段
    """
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'profile']


class RoleSerializer(serializers.ModelSerializer):
    """
    角色序列化器
    用于角色的 CRUD 操作
    """
    role_type_display = serializers.CharField(source='get_role_type_display', read_only=True)

    class Meta:
        model = Role
        fields = ['id', 'name', 'role_type', 'role_type_display', 'description']


class GroupSerializer(serializers.ModelSerializer):
    """
    业务小组序列化器
    用于小组的 CRUD 操作
    """
    # 统计小组成员数量
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'name', 'description', 'member_count']

    def get_member_count(self, obj):
        """获取小组成员数量"""
        return RoleAssignment.objects.filter(group=obj).count()


class RoleAssignmentSerializer(serializers.ModelSerializer):
    """
    角色分配序列化器
    用于用户-角色-小组关联的 CRUD
    """
    user_name = serializers.CharField(source='user.username', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = RoleAssignment
        fields = ['id', 'user', 'user_name', 'role', 'role_name', 'group', 'group_name', 'is_supervisor']