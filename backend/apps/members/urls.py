from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MemberViewSet, MemberAuthViewSet

router = DefaultRouter()
router.register(r'', MemberViewSet, basename='member')

urlpatterns = [
    path('', include(router.urls)),
    # 会员认证（不需要登录）- 使用router注册
]

# 单独添加会员认证ViewSet（不需要权限）
from rest_framework.routers import SimpleRouter
auth_router = SimpleRouter()
auth_router.register(r'auth', MemberAuthViewSet, basename='member-auth')
urlpatterns += auth_router.urls
