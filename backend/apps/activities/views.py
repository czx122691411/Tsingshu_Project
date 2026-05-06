from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count, Sum, Q, F, DecimalField
from django.db.models.functions import ExtractYear, TruncDate
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.shortcuts import get_object_or_404
import os
import logging

logger = logging.getLogger(__name__)

from .models import Activity, ActivityParticipation, ActivityType
from .serializers import (
    ActivityListSerializer, ActivityDetailSerializer,
    ActivityCreateSerializer, ActivityUpdateSerializer, ActivityParticipationSerializer,
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

    def destroy(self, request, *args, **kwargs):
        """删除活动类型前检查是否被活动引用"""
        from django.db.models import ProtectedError
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            instance = self.get_object()
            activity_count = instance.activities.count()
            return Response(
                {'detail': f'该活动类型已被 {activity_count} 个活动使用，无法删除。请先删除或修改这些活动。'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ActivityViewSet(viewsets.ModelViewSet):
    """活动视图集"""
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['activity_type', 'status']
    search_fields = ['title', 'description']
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
        if self.action in ['update', 'partial_update']:
            return ActivityUpdateSerializer
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
        会员报名活动（支持批量报名）
        POST /api/activities/{id}/register/
        请求体：
        - member_ids: 会员ID列表（支持单个会员或批量）
        - note: 备注（可选）
        """
        from apps.members.models import Member

        activity = self.get_object()

        # 检查活动是否已结束
        if activity.is_finished:
            return Response(
                {'error': '该活动已结束，无法报名'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 获取会员ID列表
        member_ids = request.data.get('member_ids')
        if not member_ids:
            # 兼容旧的单会员报名接口
            member_id = request.data.get('member_id')
            if member_id:
                member_ids = [member_id]
            else:
                return Response(
                    {'error': '请选择会员'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # 确保 member_ids 是列表
        if isinstance(member_ids, int):
            member_ids = [member_ids]
        elif isinstance(member_ids, str):
            member_ids = [int(member_ids)]

        note = request.data.get('note', '')

        results = {
            'success': [],
            'failed': [],
            'already_registered': []
        }

        for member_id in member_ids:
            # 检查会员是否存在
            try:
                member = Member.objects.get(id=member_id)
            except Member.DoesNotExist:
                results['failed'].append({
                    'member_id': member_id,
                    'reason': '会员不存在'
                })
                continue

            # 检查是否已报名
            if ActivityParticipation.objects.filter(
                member=member,
                activity=activity
            ).exists():
                results['already_registered'].append({
                    'member_id': member_id,
                    'member_name': member.name
                })
                continue

            # 创建参与记录
            participation = ActivityParticipation.objects.create(
                member=member,
                activity=activity,
                paid_amount=activity.fee,
                note=note,
                created_by=request.user
            )

            result_serializer = ActivityParticipationSerializer(participation)
            results['success'].append({
                'member_id': member_id,
                'member_name': member.name,
                'participation': result_serializer.data
            })

        # 构建返回消息
        total = len(member_ids)
        success_count = len(results['success'])
        already_count = len(results['already_registered'])
        failed_count = len(results['failed'])

        message_parts = []
        if success_count > 0:
            message_parts.append(f'成功报名 {success_count} 人')
        if already_count > 0:
            message_parts.append(f'{already_count} 人已报名')
        if failed_count > 0:
            message_parts.append(f'{failed_count} 人失败')

        message = '、'.join(message_parts)

        return Response({
            'message': message,
            'results': results
        }, status=status.HTTP_201_CREATED if success_count > 0 else status.HTTP_400_BAD_REQUEST)

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

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated], parser_classes=[MultiPartParser, FormParser])
    def upload_cover(self, request):
        """
        上传活动封面图片
        POST /api/activities/upload-cover/
        支持的图片格式：jpg、jpeg、png、gif、webp
        """
        from django.conf import settings

        logger.info(f'[UPLOAD_COVER] Upload request received. FILES: {list(request.FILES.keys())}, CONTENT_TYPE: {request.content_type}')

        if 'file' not in request.FILES:
            logger.warning('[UPLOAD_COVER] No file in request.FILES')
            return Response(
                {'error': '请选择要上传的图片'},
                status=status.HTTP_400_BAD_REQUEST
            )

        file = request.FILES['file']
        logger.info(f'[UPLOAD_COVER] File received: name={file.name}, size={file.size}, content_type={file.content_type}')

        # 验证文件类型
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        file_ext = os.path.splitext(file.name)[1].lower()

        if file_ext not in allowed_extensions:
            logger.warning(f'[UPLOAD_COVER] Invalid file extension: {file_ext}')
            return Response(
                {'error': f'只支持以下图片格式：{", ".join(allowed_extensions)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 验证文件大小（最大5MB）
        max_size = 5 * 1024 * 1024
        if file.size > max_size:
            logger.warning(f'[UPLOAD_COVER] File too large: {file.size} bytes')
            return Response(
                {'error': '图片大小不能超过5MB'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 验证是否为图片
        if not file.content_type.startswith('image/'):
            logger.warning(f'[UPLOAD_COVER] Invalid content type: {file.content_type}')
            return Response(
                {'error': '只能上传图片文件'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 保存文件
        from django.core.files.storage import default_storage
        from datetime import datetime

        # 生成文件路径：activity_covers/年/月/原文件名
        now = timezone.now()
        relative_path = f'activity_covers/{now.year}/{now.month:02d}/{file.name}'

        # 处理文件名冲突
        counter = 1
        original_path = relative_path
        while default_storage.exists(relative_path):
            name, ext = os.path.splitext(file.name)
            relative_path = f'activity_covers/{now.year}/{now.month:02d}/{name}_{counter}{ext}'
            counter += 1

        # 保存文件
        try:
            saved_path = default_storage.save(relative_path, file)
            file_url = settings.MEDIA_URL + saved_path
            logger.info(f'[UPLOAD_COVER] File saved successfully: saved_path={saved_path}, file_url={file_url}')
        except Exception as e:
            logger.error(f'[UPLOAD_COVER] Error saving file: {str(e)}', exc_info=True)
            return Response(
                {'error': f'保存文件失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({
            'url': file_url,
            'path': saved_path
        }, status=status.HTTP_201_CREATED)


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
