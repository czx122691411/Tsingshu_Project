"""
URL configuration for member_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls')),
    path('api/members/', include('apps.members.urls')),
    path('api/', include('apps.borrows.urls')),
    # 新增：活动管理模块（需要放在 members 之后，因为 members 视图集中有 activity-summary 等端点）
    path('api/', include('apps.activities.urls')),
]
