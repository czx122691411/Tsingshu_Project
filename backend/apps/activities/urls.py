from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ActivityViewSet, MemberActivityViewSet, ActivityTypeViewSet

router = DefaultRouter()
router.register(r'activities', ActivityViewSet, basename='activity')
router.register(r'activity-types', ActivityTypeViewSet, basename='activity-type')

# 添加自定义路由，避免与 members 模块冲突
urlpatterns = [
    path('', include(router.urls)),
    # 会员活动统计（使用自定义路径避免冲突）
    path('activity-stats/', MemberActivityViewSet.as_view({'get': 'activity_summary'}), name='member-activity-summary'),
    # 会员活动列表
    path('members/<int:pk>/activities/', MemberActivityViewSet.as_view({'get': 'activities'}), name='member-activities'),
]
