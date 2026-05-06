from django.contrib import admin
from .models import Activity, ActivityParticipation, ActivityType


@admin.register(ActivityType)
class ActivityTypeAdmin(admin.ModelAdmin):
    """活动类型管理后台"""
    list_display = ['name', 'code', 'color', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    """活动管理后台"""
    list_display = [
        'title', 'activity_type', 'cover_image_thumbnail',
        'start_time', 'end_time', 'fee',
        'status', 'registered_count', 'created_at'
    ]
    list_filter = ['activity_type', 'status', 'start_time']
    search_fields = ['title', 'description']
    readonly_fields = ['status', 'created_at', 'updated_at']
    date_hierarchy = 'start_time'

    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'activity_type', 'cover_image', 'description')
        }),
        ('时间', {
            'fields': ('start_time', 'end_time')
        }),
        ('费用与状态', {
            'fields': ('fee', 'status')
        }),
        ('系统信息', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def cover_image_thumbnail(self, obj):
        """显示封面缩略图"""
        if obj.cover_image:
            from django.utils.html import format_html
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />', obj.cover_image.url)
        return '无封面'
    cover_image_thumbnail.short_description = '封面'

    def registered_count(self, obj):
        """显示已报名人数"""
        return obj.registered_count
    registered_count.short_description = '已报名人数'


@admin.register(ActivityParticipation)
class ActivityParticipationAdmin(admin.ModelAdmin):
    """活动参与记录管理后台"""
    list_display = [
        'member', 'activity', 'registered_at',
        'paid_amount', 'created_by', 'created_at'
    ]
    list_filter = ['registered_at', 'activity__activity_type']
    search_fields = ['member__name', 'member__code', 'activity__title']
    readonly_fields = ['registered_at', 'created_at']
    date_hierarchy = 'registered_at'

    fieldsets = (
        ('参与信息', {
            'fields': ('member', 'activity', 'registered_at')
        }),
        ('费用信息', {
            'fields': ('paid_amount',)
        }),
        ('其他信息', {
            'fields': ('note', 'created_by'),
            'classes': ('collapse',)
        }),
    )
