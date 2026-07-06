"""
Caduceus Resources API Serializers
定义资源类型与资源项的序列化器
"""
from rest_framework import serializers
from ..models import ResourceType, ResourceItem, ResourceLog


class ResourceTypeSerializer(serializers.ModelSerializer):
    """
    资源类型序列化器
    用于资源类型的 CRUD 操作，序列化所有字段
    """

    class Meta:
        model = ResourceType
        fields = [
            'id', 'name', 'description', 'icon',
            'field_schema', 'lifecycle_config', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ResourceItemSerializer(serializers.ModelSerializer):
    """
    资源项序列化器
    用于资源项的 CRUD 操作，序列化所有字段
    creator 为只读字段，由后端在创建时自动填充为当前用户
    """
    resource_type_name = serializers.CharField(source='resource_type.name', read_only=True)

    class Meta:
        model = ResourceItem
        fields = [
            'id', 'resource_type', 'resource_type_name', 'name',
            'description', 'field_values', 'status', 'location',
            'creator', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'creator', 'status', 'created_at', 'updated_at']


class ResourceLogSerializer(serializers.ModelSerializer):
    """
    资源事件日志序列化器
    提供资源生命周期事件的序列化，自动填充操作人
    """
    operator_name = serializers.CharField(source='operator.username', read_only=True)

    class Meta:
        model = ResourceLog
        fields = [
            'id', 'resource', 'event_key', 'operator', 'operator_name',
            'summary', 'details', 'created_at'
        ]
        read_only_fields = ['id', 'operator', 'created_at']
