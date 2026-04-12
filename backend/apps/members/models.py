from django.db import models
from django.utils import timezone
from datetime import timedelta
from apps.users.models import User


class Member(models.Model):
    """会员模型"""
    STATUS_CHOICES = (
        ('active', '有效'),
        ('expiring', '30天内到期'),
        ('expired', '已到期'),
    )

    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=20, unique=True, verbose_name='会员号')
    name = models.CharField(max_length=50, verbose_name='姓名')
    phone = models.CharField(max_length=20, blank=True, verbose_name='电话')
    start_date = models.DateField(verbose_name='开始日期')
    end_date = models.DateField(verbose_name='到期日期')
    pay_date = models.DateField(verbose_name='缴费日期')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, verbose_name='状态')
    note = models.TextField(blank=True, verbose_name='备注')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_members', verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'members'
        verbose_name = '会员'
        verbose_name_plural = '会员'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

    def save(self, *args, **kwargs):
        """保存时自动计算状态"""
        self.status = self.calculate_status()
        super().save(*args, **kwargs)

    def calculate_status(self):
        """计算会员状态"""
        today = timezone.now().date()
        days_left = (self.end_date - today).days

        if days_left < 0:
            return 'expired'
        elif days_left <= 30:
            return 'expiring'
        else:
            return 'active'

    @classmethod
    def generate_code(cls):
        """生成新会员号"""
        from django.db.models import Max
        max_code = cls.objects.aggregate(Max('code'))['code__max']
        if max_code:
            try:
                num = int(max_code.split('-')[1])
                return f"M-{num + 1:04d}"
            except (IndexError, ValueError):
                pass
        return "M-0001"


class Payment(models.Model):
    """缴费流水模型"""
    id = models.AutoField(primary_key=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='payments', verbose_name='会员')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='金额')
    pay_date = models.DateField(verbose_name='缴费日期')
    note = models.CharField(max_length=200, blank=True, verbose_name='备注')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_payments', verbose_name='操作者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'payments'
        verbose_name = '缴费流水'
        verbose_name_plural = '缴费流水'
        ordering = ['-pay_date']

    def __str__(self):
        return f"{self.member.code} - ¥{self.amount} ({self.pay_date})"
