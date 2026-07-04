# demo-data 演示数据目录

本目录用于存放**开发演示用的临时数据**，用于在本地手动验证页面效果（如 Dashboard 统计、任务详情、资源列表、Pipeline 编辑器等）。

## 允许存放的内容
- 示例资源类型（ResourceType）
- 示例任务（Task）
- 示例 Pipeline 节点配置
- 示例通知内容
- 任何用于手动演示的非敏感数据

## 禁止存放的内容
- 生产环境真实数据
- 真实用户隐私信息
- API Key、Token、密码等敏感凭据
- 自动生成的临时文件（应放 `/tmp/`）

## 使用方式

### 1. 作为参考手动录入
打开 `demo-data/resource-types.example.json`，对照字段在后台管理页面手动创建对应的资源类型。

### 2. 通过 Django Fixtures 批量导入
```bash
# 进入 Django 项目目录
cd backend

# 将 JSON 转换为 fixtures 格式后导入
python manage.py loaddata <fixture_path>
```
> 注意：`example.json` 是演示版，需根据 Model 实际字段调整为标准 Django fixtures 格式（包含 `model` / `pk` 字段）后才能直接 `loaddata`。

### 3. 清理
本目录的数据**不影响业务代码运行**，随时可整体删除。开发数据库可通过 `python manage.py flush` 重置。
