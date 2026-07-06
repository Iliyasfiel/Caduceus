"""
Caduceus Accounts API Views
提供用户、角色、小组和角色分配的 API 接口
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from ..models import User, Role, Group, RoleAssignment
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    RoleSerializer, GroupSerializer, RoleAssignmentSerializer
)


@method_decorator(csrf_exempt, name='dispatch')
class UserViewSet(viewsets.ModelViewSet):
    """
    用户 API ViewSet
    提供用户的 CRUD 操作和当前用户信息获取
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        """根据动作选择不同的序列化器"""
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        获取当前登录用户信息
        用于前端获取当前用户状态
        """
        if request.user.is_authenticated:
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        return Response({'detail': '未登录'}, status=status.HTTP_401_UNAUTHORIZED)


class RoleViewSet(viewsets.ModelViewSet):
    """
    角色 API ViewSet
    提供角色的 CRUD 操作
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    业务小组 API ViewSet
    提供小组的 CRUD 操作
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """
        获取小组的成员列表
        返回该小组中所有角色分配信息
        """
        group = self.get_object()
        assignments = RoleAssignment.objects.filter(group=group)
        serializer = RoleAssignmentSerializer(assignments, many=True)
        return Response(serializer.data)


class RoleAssignmentViewSet(viewsets.ModelViewSet):
    """
    角色分配 API ViewSet
    提供用户-角色-小组关联的 CRUD 操作
    """
    queryset = RoleAssignment.objects.all()
    serializer_class = RoleAssignmentSerializer

    def get_queryset(self):
        """支持按用户、角色、小组过滤"""
        queryset = super().get_queryset()
        user_id = self.request.query_params.get('user')
        role_id = self.request.query_params.get('role')
        group_id = self.request.query_params.get('group')

        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if role_id:
            queryset = queryset.filter(role_id=role_id)
        if group_id:
            queryset = queryset.filter(group_id=group_id)

        return queryset


# 认证视图（使用 Django Session 认证）
class AuthViewSet(viewsets.ViewSet):
    """
    认证 API ViewSet
    提供登录、登出接口
    使用 Django Session 认证
    """
    permission_classes = [AllowAny]

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        """重写 dispatch 以豁免 CSRF 验证，确保前后端分离架构下的登录正常"""
        return super().dispatch(request, *args, **kwargs)

    @action(detail=False, methods=['post'])
    def login(self, request):
        """
        用户登录
        接收 username 和 password，验证后创建 Session
        """
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'detail': '用户名和密码不能为空'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            serializer = UserSerializer(user)
            return Response(serializer.data)

        return Response({'detail': '用户名或密码错误'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        """
        用户登出
        清除 Session
        """
        logout(request)
        return Response({'detail': '已登出'})

    @action(detail=False, methods=['get'])
    def status(self, request):
        """
        获取认证状态
        返回当前是否登录及用户信息
        """
        if request.user.is_authenticated:
            serializer = UserSerializer(request.user)
            return Response({'is_authenticated': True, 'user': serializer.data})
        return Response({'is_authenticated': False})