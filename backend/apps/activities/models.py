from django.db import models
from django.utils import timezone
from apps.users.models import User
from apps.members.models import Member


class ActivityType(models.Model):
    """活动类型模型"""
    name = models.CharField(max_length=50, unique=True, verbose_name='类型名称')
    code = models.CharField(max_length=20, unique=True, verbose_name='类型代码')
    color = models.CharField(max_length=20, default='#409eff', verbose_name='显示颜色')
    description = models.TextField(blank=True, verbose_name='描述')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'activity_types'
        verbose_name = '活动类型'
        verbose_name_plural = '活动类型'
        ordering = ['id']

    def __str__(self):
        return self.name


class Activity(models.Model):
    """活动模型"""
    STATUS_CHOICES = (
        ('upcoming', '即将开始'),
        ('ongoing', '进行中'),
        ('finished', '已结束'),
    )

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, verbose_name='讲座主题')
    activity_type = models.ForeignKey(
        ActivityType,
        on_delete=models.PROTECT,
        related_name='activities',
        verbose_name='活动类型'
    )
    location = models.CharField(max_length=200, verbose_name='地点')
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='费用')
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='upcoming',
        verbose_name='状态'
    )
    description = models.TextField(blank=True, verbose_name='活动描述')
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_activities',
        verbose_name='创建者'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'activities'
        verbose_name = '活动'
        verbose_name_plural = '活动'
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.title} ({self.activity_type.name if self.activity_type else '未设置'}) - {self.start_time.strftime('%Y-%m-%d %H:%M')}"

    def save(self, *args, **kwargs):
        """保存时自动更新状态"""
        self.status = self.calculate_status()
        super().save(*args, **kwargs)

    def calculate_status(self):
        """根据时间自动计算状态"""
        now = timezone.now()
        if now < self.start_time:
            return 'upcoming'
        elif self.end_time and now >= self.end_time:
            return 'finished'
        else:
            # 如果没有设置结束时间，开始后2小时视为结束
            if not self.end_time:
                end_time = self.start_time.replace(hour=self.start_time.hour + 2)
                if now >= end_time:
                    return 'finished'
            return 'ongoing'

    @property
    def registered_count(self):
        """已报名人数"""
        return self.participations.count()

    @property
    def is_finished(self):
        """活动是否已结束"""
        return self.status == 'finished'


class ActivityParticipation(models.Model):
    """活动参与记录模型"""

    id = models.AutoField(primary_key=True)
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='activity_participations',
        verbose_name='会员'
    )
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name='participations',
        verbose_name='活动'
    )
    registered_at = models.DateTimeField(auto_now_add=True, verbose_name='报名时间')
    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='实际支付金额'
    )
    note = models.TextField(blank=True, verbose_name='备注')
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_participations',
        verbose_name='操作者'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'activity_participations'
        verbose_name = '活动参与记录'
        verbose_name_plural = '活动参与记录'
        ordering = ['-registered_at']
        # 联合唯一约束：同一会员不能重复报名同一活动
        unique_together = ['member', 'activity']

    def __str__(self):
        return f"{self.member.name} - {self.activity.title} ({self.registered_at.strftime('%Y-%m-%d')})"

    def save(self, *args, **kwargs):
        """保存时自动设置支付金额为活动费用"""
        if not self.paid_amount or self.paid_amount == 0:
            self.paid_amount = self.activity.fee
        super().save(*args, **kwargs)
