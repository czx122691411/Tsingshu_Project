from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """扩展用户模型"""
    ROLE_CHOICES = (
        ('admin', '管理员'),
        ('staff', '工作人员'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='staff', verbose_name='角色')
    email = models.EmailField(unique=True, verbose_name='邮箱')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
