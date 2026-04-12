from datetime import date, timedelta
from django.utils import timezone
from django.db import models
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import Book, Borrow
from .serializers import (
    BookSerializer, BookListSerializer,
    BorrowSerializer, BorrowListSerializer,
    BorrowCreateSerializer, ReturnSerializer
)


class BookViewSet(viewsets.ModelViewSet):
    """书籍视图集"""
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'author', 'isbn']
    ordering_fields = ['title', 'created_at']
    ordering = ['title']

    def get_queryset(self):
        return Book.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return BookListSerializer
        return BookSerializer


class BorrowViewSet(viewsets.ModelViewSet):
    """借阅记录视图集"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'member', 'book']
    search_fields = ['book_title']
    ordering_fields = ['borrow_date', 'due_date']
    ordering = ['-borrow_date']

    def get_queryset(self):
        return Borrow.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return BorrowListSerializer
        if self.action == 'create':
            return BorrowCreateSerializer
        return BorrowSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        """归还图书"""
        borrow = self.get_object()

        if borrow.return_date:
            return Response(
                {"error": "该书已归还"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ReturnSerializer(data=request.data)
        if serializer.is_valid():
            borrow.return_date = timezone.now().date()
            borrow.note = serializer.validated_data.get('note', borrow.note)
            borrow.save()
            return Response({"message": "归还成功"})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StatsViewSet(viewsets.ViewSet):
    """统计视图集"""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """仪表盘统计数据"""
        from apps.members.models import Member

        today = timezone.now().date()

        # 会员统计
        total_members = Member.objects.count()
        active_members = Member.objects.filter(status='active').count()
        expiring_members = Member.objects.filter(status='expiring').count()
        expired_members = Member.objects.filter(status='expired').count()

        # 借阅统计
        borrowing_count = Borrow.objects.filter(return_date__isnull=True).count()
        overdue_count = Borrow.objects.filter(
            return_date__isnull=True,
            due_date__lt=today
        ).count()

        # 书籍统计
        total_books = Book.objects.count()
        total_copies = Book.objects.aggregate(total=models.Sum('total'))['total'] or 0

        return Response({
            'members': {
                'total': total_members,
                'active': active_members,
                'expiring': expiring_members,
                'expired': expired_members,
            },
            'borrows': {
                'borrowing': borrowing_count,
                'overdue': overdue_count,
            },
            'books': {
                'total': total_books,
                'total_copies': total_copies,
            }
        })
