"""
Caduceus Accounts App 配置
用户/角色/权限管理模块
"""
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    verbose_name = '用户角色管理'