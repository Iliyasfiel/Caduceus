"""
Caduceus Pipeline API Serializers
定义管线模板与管线实例的序列化器，包含 nodes 和 edges 的 JSON 结构验证
"""
from rest_framework import serializers
from ..models import Pipeline, PipelineInstance


class PipelineSerializer(serializers.ModelSerializer):
    """
    管线模板序列化器
    用于管线模板的 CRUD 操作，包含 nodes 和 edges 的 JSON 结构校验
    """
    creator_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Pipeline
        fields = [
            'id', 'name', 'description', 'nodes', 'edges',
            'created_by', 'creator_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def validate_nodes(self, value):
        """
        验证 nodes 字段的 JSON 结构
        每个节点必须包含 id、label、fields_config、roles、resource_types
        """
        if not isinstance(value, list):
            raise serializers.ValidationError('nodes 必须是数组')

        for i, node in enumerate(value):
            if not isinstance(node, dict):
                raise serializers.ValidationError(f'nodes[{i}] 必须是对象')

            if 'id' not in node:
                raise serializers.ValidationError(f'nodes[{i}] 缺少 id 字段')

            if 'label' not in node:
                raise serializers.ValidationError(f'nodes[{i}] 缺少 label 字段')

            fields_config = node.get('fields_config', [])
            if not isinstance(fields_config, list):
                raise serializers.ValidationError(f'nodes[{i}].fields_config 必须是数组')

            for j, field in enumerate(fields_config):
                if not isinstance(field, dict):
                    raise serializers.ValidationError(
                        f'nodes[{i}].fields_config[{j}] 必须是对象'
                    )
                for required_key in ['key', 'label', 'type']:
                    if required_key not in field:
                        raise serializers.ValidationError(
                            f'nodes[{i}].fields_config[{j}] 缺少 {required_key} 字段'
                        )
                if 'priority_roles' not in field:
                    raise serializers.ValidationError(
                        f'nodes[{i}].fields_config[{j}] 缺少 priority_roles 字段'
                    )
                if 'is_public' not in field:
                    raise serializers.ValidationError(
                        f'nodes[{i}].fields_config[{j}] 缺少 is_public 字段'
                    )

            roles = node.get('roles', [])
            if not isinstance(roles, list):
                raise serializers.ValidationError(f'nodes[{i}].roles 必须是数组')

            for j, role in enumerate(roles):
                if not isinstance(role, dict):
                    raise serializers.ValidationError(
                        f'nodes[{i}].roles[{j}] 必须是对象'
                    )
                for required_key in ['role_id', 'merge_default', 'merge_time_window']:
                    if required_key not in role:
                        raise serializers.ValidationError(
                            f'nodes[{i}].roles[{j}] 缺少 {required_key} 字段'
                        )

            resource_types = node.get('resource_types', [])
            if not isinstance(resource_types, list):
                raise serializers.ValidationError(f'nodes[{i}].resource_types 必须是数组')

        return value

    def validate_edges(self, value):
        """
        验证 edges 字段的 JSON 结构
        每条边必须包含 id、source、target
        """
        if not isinstance(value, list):
            raise serializers.ValidationError('edges 必须是数组')

        for i, edge in enumerate(value):
            if not isinstance(edge, dict):
                raise serializers.ValidationError(f'edges[{i}] 必须是对象')

            for required_key in ['id', 'source', 'target']:
                if required_key not in edge:
                    raise serializers.ValidationError(
                        f'edges[{i}] 缺少 {required_key} 字段'
                    )

        return value


class PipelineInstanceSerializer(serializers.ModelSerializer):
    """
    管线实例序列化器
    用于管线运行实例的 CRUD 操作
    """
    pipeline_name = serializers.CharField(source='pipeline.name', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = PipelineInstance
        fields = [
            'id', 'pipeline', 'pipeline_name', 'task', 'task_title',
            'current_node', 'status', 'status_display', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
