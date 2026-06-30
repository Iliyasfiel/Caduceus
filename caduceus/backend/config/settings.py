"""
Caduceus Django 项目配置文件
包含数据库、应用、中间件、Channels 等核心配置
"""
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 安全密钥（生产环境必须通过环境变量设置）
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-secret-key-change-in-production')

# 开发模式开关
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

# 允许的主机
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# 安装的应用
INSTALLED_APPS = [
    'daphne',  # ASGI 服务器，必须放在首位
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 第三方应用
    'rest_framework',
    'corsheaders',
    'channels',
    'django_extensions',

    # 本项目应用（待创建）
    'apps.accounts',
    'apps.tasks',
    'apps.pipeline',
    'apps.resources',
    'apps.notifications',
    'apps.dashboard',
]

# 中间件配置
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS 中间件，必须放在 CommonMiddleware 之前
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 根 URL 配置
ROOT_URLCONF = 'config.urls'

# 模板配置
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ASGI 应用入口（Channels WebSocket 支持）
ASGI_APPLICATION = 'config.asgi.application'

# 数据库配置（支持环境变量切换引擎，默认 PostgreSQL）
DB_ENGINE = os.environ.get('DB_ENGINE', 'postgresql')
if DB_ENGINE == 'sqlite':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_DB', 'caduceus'),
            'USER': os.environ.get('POSTGRES_USER', 'caduceus'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'caduceus_password'),
            'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
            'PORT': os.environ.get('POSTGRES_PORT', '5432'),
        }
    }

# Channels channel layer 配置（支持环境变量切换，默认 Redis）
CHANNEL_BACKEND = os.environ.get('CHANNEL_BACKEND', 'redis')
if CHANNEL_BACKEND == 'memory':
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        },
    }
else:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [(os.environ.get('REDIS_HOST', 'localhost'), int(os.environ.get('REDIS_PORT', 6379)))],
            },
        },
    }

# CORS 配置（开发环境允许所有来源）
CORS_ALLOW_ALL_ORIGINS = DEBUG

# DRF 配置
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# 国际化配置（中文）
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# 静态文件配置
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# 默认主键字段类型
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 自定义用户模型
AUTH_USER_MODEL = 'accounts.User'