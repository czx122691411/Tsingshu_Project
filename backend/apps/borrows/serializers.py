from rest_framework import serializers
from .models import Book, Borrow
from apps.members.serializers import MemberListSerializer


class BookSerializer(serializers.ModelSerializer):
    """书籍序列化器"""
    available = serializers.ReadOnlyField()

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'isbn', 'total', 'available', 'note', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class BookListSerializer(serializers.ModelSerializer):
    """书籍列表序列化器"""
    available = serializers.ReadOnlyField()

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'isbn', 'total', 'available']


class BorrowSerializer(serializers.ModelSerializer):
    """借阅记录序列化器"""
    member_code = serializers.CharField(source='member.code', read_only=True)
    member_name = serializers.CharField(source='member.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Borrow
        fields = [
            'id', 'member', 'member_code', 'member_name', 'book', 'book_title',
            'borrow_date', 'due_date', 'return_date', 'status', 'status_display',
            'note', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'status', 'created_at']


class BorrowListSerializer(serializers.ModelSerializer):
    """借阅记录列表序列化器"""
    member_code = serializers.CharField(source='member.code', read_only=True)
    member_name = serializers.CharField(source='member.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Borrow
        fields = [
            'id', 'member_code', 'member_name', 'book_title',
            'borrow_date', 'due_date', 'return_date', 'status', 'status_display'
        ]


class BorrowCreateSerializer(serializers.ModelSerializer):
    """借阅创建序列化器"""
    member_name = serializers.CharField(source='member.name', read_only=True)

    class Meta:
        model = Borrow
        fields = ['member', 'book', 'borrow_date', 'due_date', 'note', 'member_name']

    def validate(self, data):
        book = data['book']
        # 检查库存
        if book.available <= 0:
            raise serializers.ValidationError({"book": "该书库存不足"})

        return data

    def create(self, validated_data):
        validated_data.pop('member_name', None)
        borrow = Borrow.objects.create(**validated_data)
        return borrow


class ReturnSerializer(serializers.Serializer):
    """归还序列化器"""
    note = serializers.CharField(max_length=200, required=False, allow_blank=True)
