from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User
from .serializers import UserSerializer, LoginSerializer, RegisterSerializer


class LoginView(TokenObtainPairView):
    """登录视图"""
    serializer_class = LoginSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """获取当前用户信息"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """注册新用户"""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "用户创建成功"},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """登出（前端删除token即可）"""
    return Response({"message": "登出成功"})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_list_view(request):
    """用户列表（仅管理员）"""
    if request.user.role != 'admin':
        return Response(
            {"error": "权限不足"},
            status=status.HTTP_403_FORBIDDEN
        )
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)
