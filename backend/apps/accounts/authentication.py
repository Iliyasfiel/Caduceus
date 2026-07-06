"""
Caduceus 认证模块
前后端分离架构下，前端通过 Vite 代理访问后端 API，需要豁免 DRF Session 认证的 CSRF 强制检查
"""
from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    CSRF 豁免的 Session 认证类
    前后端分离开发时，前端 Vite dev server 和后端 Django 分开部署，
    标准 DRF SessionAuthentication 会强制要求 CSRF token 验证，
    此处重写 enforce_csrf 为空操作以豁免该检查
    """
    def enforce_csrf(self, request):
        pass
