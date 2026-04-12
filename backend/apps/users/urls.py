from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import LoginView, me_view, register_view, logout_view, user_list_view

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('me/', me_view, name='me'),
    path('users/', user_list_view, name='user_list'),
]
