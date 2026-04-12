from rest_framework import serializers
from django.db.models import Count, Sum, Q
from django.db.models.functions import ExtractYear
from .models import Activity, ActivityParticipation, ActivityType


class ActivityTypeSerializer(serializers.ModelSerializer):
    """活动类型序列化器"""

    class Meta:
        model = ActivityType
        fields = ['id', 'name', 'code', 'color', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ActivityParticipationSerializer(serializers.ModelSerializer):
    """活动参与记录序列化器"""
    member_name = serializers.CharField(source='member.name', read_only=True)
    member_code = serializers.CharField(source='member.code', read_only=True)
    activity_title = serializers.CharField(source='activity.title', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = ActivityParticipation
        fields = [
            'id', 'member', 'member_name', 'member_code',
            'activity', 'activity_title', 'registered_at',
            'paid_amount', 'note', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'registered_at', 'created_at']


class ActivityListSerializer(serializers.ModelSerializer):
    """活动列表序列化器（简化版）"""
    activity_type_name = serializers.CharField(source='activity_type.name', read_only=True)
    activity_type_code = serializers.CharField(source='activity_type.code', read_only=True)
    activity_type_color = serializers.CharField(source='activity_type.color', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    registered_count = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Activity
        fields = [
            'id', 'title', 'activity_type', 'activity_type_name', 'activity_type_code', 'activity_type_color',
            'location', 'start_time', 'end_time', 'fee', 'status',
            'status_display', 'registered_count', 'created_by_name'
        ]

    def get_registered_count(self, obj):
        """获取已报名人数"""
        return obj.registered_count


class ActivityDetailSerializer(serializers.ModelSerializer):
    """活动详情序列化器"""
    activity_type_display = serializers.CharField(source='activity_type.name', read_only=True)
    activity_type_name = serializers.CharField(source='activity_type.name', read_only=True)
    activity_type_code = serializers.CharField(source='activity_type.code', read_only=True)
    activity_type_color = serializers.CharField(source='activity_type.color', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    registered_count = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    participations = ActivityParticipationSerializer(many=True, read_only=True)

    class Meta:
        model = Activity
        fields = [
            'id', 'title', 'activity_type', 'activity_type_display', 'activity_type_name', 'activity_type_code', 'activity_type_color',
            'location', 'start_time', 'end_time', 'fee', 'status',
            'status_display', 'description', 'registered_count',
            'created_by_name', 'created_at', 'updated_at', 'participations'
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']

    def get_registered_count(self, obj):
        """获取已报名人数"""
        return obj.registered_count


class ActivityCreateSerializer(serializers.ModelSerializer):
    """活动创建序列化器"""

    class Meta:
        model = Activity
        fields = [
            'title', 'activity_type', 'location',
            'start_time', 'end_time', 'fee', 'description'
        ]


class ActivityCalendarSerializer(serializers.Serializer):
    """活动日历序列化器"""
    date = serializers.DateField()
    activities = ActivityListSerializer(many=True)


class MemberActivitySummarySerializer(serializers.Serializer):
    """会员活动统计汇总序列化器"""
    member_id = serializers.IntegerField()
    member_name = serializers.CharField()
    member_code = serializers.CharField()
    total_count = serializers.IntegerField()
    total_fee = serializers.DecimalField(max_digits=10, decimal_places=2)
    yearly_breakdown = serializers.ListField()


class MemberActivityDetailSerializer(serializers.ModelSerializer):
    """会员参与活动详情序列化器"""
    activity_title = serializers.CharField(source='activity.title', read_only=True)
    activity_type_name = serializers.CharField(source='activity.activity_type.name', read_only=True)
    activity_type_code = serializers.CharField(source='activity.activity_type.code', read_only=True)
    activity_type_color = serializers.CharField(source='activity.activity_type.color', read_only=True)
    activity_location = serializers.CharField(source='activity.location', read_only=True)
    activity_start_time = serializers.DateTimeField(source='activity.start_time', read_only=True)
    activity_fee = serializers.DecimalField(source='activity.fee', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = ActivityParticipation
        fields = [
            'id', 'activity', 'activity_title', 'activity_type_name', 'activity_type_code', 'activity_type_color',
            'activity_location', 'activity_start_time',
            'activity_fee', 'registered_at', 'paid_amount', 'note'
        ]


class RegisterActivitySerializer(serializers.Serializer):
    """报名活动序列化器"""
    member_id = serializers.IntegerField(required=True, help_text='会员ID')
    note = serializers.CharField(required=False, allow_blank=True, max_length=500)

    def validate_member_id(self, value):
        """验证会员ID是否存在"""
        from apps.members.models import Member
        try:
            Member.objects.get(id=value)
            return value
        except Member.DoesNotExist:
            raise serializers.ValidationError('会员不存在')
