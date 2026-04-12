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
        'title', 'activity_type', 'location',
        'start_time', 'end_time', 'fee',
        'status', 'registered_count', 'created_at'
    ]
    list_filter = ['activity_type', 'status', 'start_time']
    search_fields = ['title', 'location', 'description']
    readonly_fields = ['status', 'created_at', 'updated_at']
    date_hierarchy = 'start_time'

    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'activity_type', 'description')
        }),
        ('时间地点', {
            'fields': ('start_time', 'end_time', 'location')
        }),
        ('费用与状态', {
            'fields': ('fee', 'status')
        }),
        ('系统信息', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

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
