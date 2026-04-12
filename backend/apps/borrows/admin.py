from django.contrib import admin
from .models import Book, Borrow


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'total', 'available']
    search_fields = ['title', 'author', 'isbn']


@admin.register(Borrow)
class BorrowAdmin(admin.ModelAdmin):
    list_display = ['id', 'member', 'book_title', 'borrow_date', 'due_date', 'return_date', 'status']
    list_filter = ['status']
    search_fields = ['book_title', 'member__name']
