FROM python:3.12-slim

LABEL maintainer="Caduceus Team"
LABEL description="Caduceus Django Backend Service"

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 复制入口脚本
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 创建静态文件目录
RUN mkdir -p /app/staticfiles

# 入口脚本：执行迁移后启动 Daphne
ENTRYPOINT ["/entrypoint.sh"]

# 默认启动 Daphne（ASGI 服务器）
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]