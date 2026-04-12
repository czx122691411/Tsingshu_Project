from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, BorrowViewSet, StatsViewSet

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')
router.register(r'borrows', BorrowViewSet, basename='borrow')
router.register(r'stats', StatsViewSet, basename='stats')

urlpatterns = [
    path('', include(router.urls)),
]
