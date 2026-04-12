from django.db import models
from django.utils import timezone
from datetime import timedelta
from apps.users.models import User
from apps.members.models import Member


class Book(models.Model):
    """书籍模型"""
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, verbose_name='书名')
    author = models.CharField(max_length=100, blank=True, verbose_name='作者')
    isbn = models.CharField(max_length=20, blank=True, verbose_name='ISBN')
    total = models.IntegerField(default=1, verbose_name='总库存')
    note = models.TextField(blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'books'
        verbose_name = '书籍'
        verbose_name_plural = '书籍'
        ordering = ['title']

    def __str__(self):
        return self.title

    @property
    def available(self):
        """可借数量"""
        borrowed_count = self.borrows.filter(return_date__isnull=True).count()
        return max(0, self.total - borrowed_count)


class Borrow(models.Model):
    """借阅记录模型"""
    STATUS_CHOICES = (
        ('borrowing', '借出中'),
        ('overdue', '逾期'),
        ('returned', '已归还'),
    )

    id = models.AutoField(primary_key=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='borrows', verbose_name='会员')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrows', verbose_name='书籍')
    book_title = models.CharField(max_length=200, verbose_name='书名（快照）')
    borrow_date = models.DateField(verbose_name='借出日期')
    due_date = models.DateField(verbose_name='应还日期')
    return_date = models.DateField(null=True, blank=True, verbose_name='归还日期')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, verbose_name='状态')
    note = models.TextField(blank=True, verbose_name='备注')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_borrows', verbose_name='操作者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'borrows'
        verbose_name = '借阅记录'
        verbose_name_plural = '借阅记录'
        ordering = ['-borrow_date']

    def __str__(self):
        return f"{self.member.name} - {self.book_title}"

    def save(self, *args, **kwargs):
        """保存时自动计算状态和书名快照"""
        if not self.book_title:
            self.book_title = self.book.title
        self.status = self.calculate_status()
        super().save(*args, **kwargs)

    def calculate_status(self):
        """计算借阅状态"""
        if self.return_date:
            return 'returned'

        today = timezone.now().date()
        if self.due_date and today > self.due_date:
            return 'overdue'
        return 'borrowing'

    @property
    def is_overdue(self):
        """是否逾期"""
        return self.status == 'overdue'
