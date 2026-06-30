#!/bin/bash
# Caduceus 后端服务启动入口脚本
# 执行数据库迁移后启动应用服务

set -e

echo "=== Caduceus Backend Startup ==="

# 等待数据库就绪（简单轮询）
echo "Waiting for database to be ready..."
while ! python manage.py migrate --check 2>/dev/null; do
    sleep 1
done
echo "Database is ready."

# 执行数据库迁移
echo "Running database migrations..."
python manage.py migrate --noinput

# 收集静态文件（生产环境）
if [ "$DJANGO_DEBUG" = "False" ]; then
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
fi

echo "=== Starting Application ==="

# 执行传入的命令（默认是 Daphne）
exec "$@"