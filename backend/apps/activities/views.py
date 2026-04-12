from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count, Sum, Q, F, DecimalField
from django.db.models.functions import ExtractYear, TruncDate
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.shortcuts import get_object_or_404

from .models import Activity, ActivityParticipation, ActivityType
from .serializers import (
    ActivityListSerializer, ActivityDetailSerializer,
    ActivityCreateSerializer, ActivityParticipationSerializer,
    ActivityCalendarSerializer, MemberActivitySummarySerializer,
    MemberActivityDetailSerializer, RegisterActivitySerializer,
    ActivityTypeSerializer
)
from .permissions import IsAdminUser, IsAdminOrReadOnly


class ActivityTypeViewSet(viewsets.ModelViewSet):
    """活动类型视图集"""
    permission_classes = [IsAdminUser]
    queryset = ActivityType.objects.all()
    serializer_class = ActivityTypeSerializer
    filterset_fields = ['is_active']
    search_fields = ['name', 'code']
    ordering = ['id']


class ActivityViewSet(viewsets.ModelViewSet):
    """活动视图集"""
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['activity_type', 'status']
    search_fields = ['title', 'location', 'description']
    ordering_fields = ['start_time', 'created_at']
    ordering = ['-start_time']

    def get_queryset(self):
        """获取查询集，支持时间范围筛选"""
        queryset = Activity.objects.all()

        # 支持时间范围筛选
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(start_time__gte=start_date)
        if end_date:
            queryset = queryset.filter(start_time__lte=end_date)

        return queryset

    def get_serializer_class(self):
        """根据操作返回不同的序列化器"""
        if self.action == 'list':
            return ActivityListSerializer
        if self.action == 'create':
            return ActivityCreateSerializer
        return ActivityDetailSerializer

    def perform_create(self, serializer):
        """创建活动时记录创建者"""
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        """更新活动"""
        serializer.save()

    def perform_destroy(self, instance):
        """删除活动前检查是否有已报名的会员"""
        if instance.registered_count > 0:
            return Response(
                {'error': '该活动已有会员报名，无法删除'},
                status=status.HTTP_400_BAD_REQUEST
            )
        instance.delete()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def register(self, request, pk=None):
        """
        会员报名活动
        POST /api/activities/{id}/register/
        """
        from apps.members.models import Member

        activity = self.get_object()

        # 检查活动是否已结束
        if activity.is_finished:
            return Response(
                {'error': '该活动已结束，无法报名'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = RegisterActivitySerializer(data=request.data)
        if serializer.is_valid():
            member_id = serializer.validated_data['member_id']

            # 检查会员是否存在
            try:
                member = Member.objects.get(id=member_id)
            except Member.DoesNotExist:
                return Response(
                    {'error': '会员不存在'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 检查是否已报名
            if ActivityParticipation.objects.filter(
                member=member,
                activity=activity
            ).exists():
                return Response(
                    {'error': f'会员 {member.name} 已报名该活动'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 创建参与记录
            participation = ActivityParticipation.objects.create(
                member=member,
                activity=activity,
                paid_amount=activity.fee,
                note=serializer.validated_data.get('note', ''),
                created_by=request.user
            )

            result_serializer = ActivityParticipationSerializer(participation)
            return Response(
                {'message': f'会员 {member.name} 报名成功', 'participation': result_serializer.data},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unregister(self, request, pk=None):
        """
        取消活动报名
        POST /api/activities/{id}/unregister/
        """
        activity = self.get_object()

        # 检查活动是否已开始或结束
        now = timezone.now()
        if now >= activity.start_time:
            return Response(
                {'error': '活动已开始或已结束，无法取消报名'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 注意：这里需要根据实际业务逻辑找到对应的参与记录并删除
        # 如果有当前登录会员信息，可以通过 member_id 筛选

        return Response(
            {'message': '取消报名功能需要根据实际业务逻辑完善'},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def calendar(self, request):
        """
        获取活动日历数据
        GET /api/activities/calendar/?year=2024&month=5
        """
        year = request.query_params.get('year')
        month = request.query_params.get('month')

        if not year or not month:
            # 默认返回当前月份
            now = timezone.now()
            year = now.year
            month = now.month

        try:
            year = int(year)
            month = int(month)
        except ValueError:
            return Response(
                {'error': '年份和月份必须为有效数字'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 获取指定月份的活动
        from django.db.models import functions
        start_of_month = datetime(year, month, 1)
        if month == 12:
            start_of_next_month = datetime(year + 1, 1, 1)
        else:
            start_of_next_month = datetime(year, month + 1, 1)

        activities = Activity.objects.filter(
            start_time__gte=start_of_month,
            start_time__lt=start_of_next_month
        ).order_by('start_time')

        # 按日期分组（使用本地时区）
        calendar_data = {}
        for activity in activities:
            # 将UTC时间转换为本地时间后再提取日期
            local_time = timezone.localtime(activity.start_time)
            date_key = local_time.date()
            if date_key not in calendar_data:
                calendar_data[date_key] = []
            calendar_data[date_key].append(ActivityListSerializer(activity).data)

        # 转换为列表格式
        result = [
            {
                'date': date,
                'activities': calendar_data[date]
            }
            for date in sorted(calendar_data.keys())
        ]

        return Response(result)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def summary(self, request):
        """
        获取活动统计摘要
        GET /api/activities/summary/
        """
        total_activities = Activity.objects.count()
        upcoming_count = Activity.objects.filter(status='upcoming').count()
        ongoing_count = Activity.objects.filter(status='ongoing').count()
        finished_count = Activity.objects.filter(status='finished').count()

        total_participations = ActivityParticipation.objects.count()
        total_revenue = ActivityParticipation.objects.aggregate(
            total=Sum('paid_amount')
        )['total'] or 0

        return Response({
            'total_activities': total_activities,
            'upcoming_count': upcoming_count,
            'ongoing_count': ongoing_count,
            'finished_count': finished_count,
            'total_participations': total_participations,
            'total_revenue': float(total_revenue)
        })


class MemberActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """会员活动统计视图集"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def activity_summary(self, request):
        """
        获取所有会员的活动参与统计
        GET /api/members/activity-summary/?year=2024
        """
        from apps.members.models import Member

        year = request.query_params.get('year')

        # 构建查询
        participations = ActivityParticipation.objects.select_related(
            'member', 'activity'
        ).annotate(
            year=ExtractYear('registered_at')
        ).order_by('member__code', '-registered_at')

        if year:
            participations = participations.filter(year=int(year))

        # 按会员分组统计
        members_data = {}
        for participation in participations:
            member = participation.member
            reg_year = participation.registered_at.year

            if member.id not in members_data:
                members_data[member.id] = {
                    'member_id': member.id,
                    'member_name': member.name,
                    'member_code': member.code,
                    'total_count': 0,
                    'total_fee': 0,
                    'yearly_breakdown': {}
                }

            members_data[member.id]['total_count'] += 1
            members_data[member.id]['total_fee'] += float(participation.paid_amount)

            if reg_year not in members_data[member.id]['yearly_breakdown']:
                members_data[member.id]['yearly_breakdown'][reg_year] = {
                    'year': reg_year,
                    'count': 0,
                    'total_fee': 0
                }

            members_data[member.id]['yearly_breakdown'][reg_year]['count'] += 1
            members_data[member.id]['yearly_breakdown'][reg_year]['total_fee'] += float(participation.paid_amount)

        # 转换为列表并排序
        result = []
        for member_id in sorted(members_data.keys()):
            member_data = members_data[member_id]
            # 将年度分解转换为排序的列表
            yearly_breakdown = sorted(
                member_data['yearly_breakdown'].values(),
                key=lambda x: x['year'],
                reverse=True
            )
            member_data['yearly_breakdown'] = yearly_breakdown
            # 格式化总费用
            member_data['total_fee'] = round(member_data['total_fee'], 2)
            result.append(member_data)

        # 按总参与次数排序
        result.sort(key=lambda x: x['total_count'], reverse=True)

        serializer = MemberActivitySummarySerializer(result, many=True)
        import sys
        print(f'[DEBUG] MemberActivitySummary data: {serializer.data}', file=sys.stderr)
        print(f'[DEBUG] Type: {type(serializer.data)}', file=sys.stderr)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def activities(self, request, pk=None):
        """
        获取指定会员参与的活动列表
        GET /api/members/{member_id}/activities/
        """
        from apps.members.models import Member

        member = get_object_or_404(Member, id=pk)
        participations = ActivityParticipation.objects.filter(
            member=member
        ).select_related(
            'activity', 'created_by'
        ).order_by('-registered_at')

        serializer = MemberActivityDetailSerializer(participations, many=True)
        return Response({
            'member_id': member.id,
            'member_name': member.name,
            'member_code': member.code,
            'activities': serializer.data
        })
