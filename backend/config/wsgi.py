"""
Caduceus WSGI 配置
用于传统的 HTTP 服务部署（如 Gunicorn）
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()