# Generated manually for Phase 2 V2 refactor

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pipeline', '0002_initial'),
    ]

    operations = [
        # Pipeline 模型变更：移除旧字段
        migrations.RemoveField(
            model_name='pipeline',
            name='definition',
        ),
        migrations.RemoveField(
            model_name='pipeline',
            name='is_active',
        ),
        # Pipeline 模型变更：新增 V2 字段
        migrations.AddField(
            model_name='pipeline',
            name='nodes',
            field=models.JSONField(blank=True, default=list, verbose_name='任务节点配置'),
        ),
        migrations.AddField(
            model_name='pipeline',
            name='edges',
            field=models.JSONField(blank=True, default=list, verbose_name='阶段连接'),
        ),
        # 重命名字段 creator → created_by
        migrations.RenameField(
            model_name='pipeline',
            old_name='creator',
            new_name='created_by',
        ),
        # PipelineInstance 模型变更：移除旧字段
        migrations.RemoveField(
            model_name='pipelineinstance',
            name='execution_history',
        ),
        # PipelineInstance 模型变更：修改 status choices
        migrations.AlterField(
            model_name='pipelineinstance',
            name='status',
            field=models.CharField(
                choices=[('running', '运行中'), ('completed', '已完成')],
                default='running',
                max_length=20,
                verbose_name='状态'
            ),
        ),
        migrations.AlterField(
            model_name='pipelineinstance',
            name='current_node',
            field=models.CharField(blank=True, max_length=100, verbose_name='当前阶段'),
        ),
        migrations.AlterField(
            model_name='pipeline',
            name='name',
            field=models.CharField(max_length=200, verbose_name='管线名称'),
        ),
    ]
