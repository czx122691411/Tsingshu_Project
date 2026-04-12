from datetime import date, timedelta
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Member, Payment
from .serializers import (
    MemberSerializer, MemberListSerializer,
    MemberCreateSerializer, PaymentSerializer, RenewSerializer
)


class MemberViewSet(viewsets.ModelViewSet):
    """会员视图集"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['name', 'phone', 'code']
    ordering_fields = ['code', 'created_at']
    ordering = ['code']

    def get_queryset(self):
        return Member.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return MemberListSerializer
        if self.action == 'create':
            return MemberCreateSerializer
        return MemberSerializer

    def create(self, request, *args, **kwargs):
        print(f"DEBUG - create called")
        print(f"DEBUG - request.data: {request.data}")
        print(f"DEBUG - request.user: {request.user}")
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        print(f"DEBUG - perform_create called, user: {self.request.user}")
        try:
            serializer.save(created_by=self.request.user)
            print(f"DEBUG - member created successfully")
        except Exception as e:
            print(f"DEBUG - Error creating member: {e}")
            print(f"DEBUG - Error type: {type(e)}")
            print(f"DEBUG - Error args: {e.args}")
            raise

    def perform_update(self, serializer):
        serializer.save()

    @action(detail=True, methods=['post'])
    def renew(self, request, pk=None):
        """会员续费"""
        member = self.get_object()
        serializer = RenewSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            note = serializer.validated_data.get('note', '续费')

            today = timezone.now().date()

            # 计算新的到期日期：如果未到期则从到期日+1年，否则从今天+1年
            if member.end_date >= today:
                new_end_date = member.end_date + timedelta(days=365)
            else:
                new_end_date = today + timedelta(days=365)

            member.end_date = new_end_date
            member.pay_date = today
            member.save()

            # 创建缴费记录
            Payment.objects.create(
                member=member,
                amount=amount,
                pay_date=today,
                note=note,
                created_by=request.user
            )

            return Response({
                'message': '续费成功',
                'new_end_date': new_end_date,
                'amount': amount
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def payments(self, request, pk=None):
        """获取会员缴费流水"""
        member = self.get_object()
        payments = member.payments.all()
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)


class MemberAuthViewSet(viewsets.ViewSet):
    """会员认证视图集（不需要登录）"""
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def login(self, request):
        """
        会员登录
        POST /api/members/auth/login/
        {
            "code": "M-0001",
            "phone_last4": "1234"
        }
        """
        code = request.data.get('code')
        phone_last4 = request.data.get('phone_last4')

        if not code or not phone_last4:
            return Response(
                {'error': '请提供会员号和手机号后4位'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            member = Member.objects.get(code=code)
            # 验证手机号后4位
            if not member.phone or not member.phone.endswith(phone_last4):
                return Response(
                    {'error': '会员号或手机号后4位不正确'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # 检查会员状态
            if member.status != 'active':
                return Response(
                    {'error': f'会员账户{member.get_status_display()}，无法登录'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # 生成JWT token
            from apps.users.models import User
            # 为会员创建临时用户会话
            try:
                user = User.objects.get(username=f'member_{member.id}')
            except User.DoesNotExist:
                user = User.objects.create_user(
                    username=f'member_{member.id}',
                    email=f'member_{member.id}@temp.com',
                    password=f'temp_{member.code}',
                    role='member',
                    first_name=member.name
                )

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response({
                'access': access_token,
                'refresh': str(refresh),
                'member': {
                    'id': member.id,
                    'code': member.code,
                    'name': member.name,
                    'phone': member.phone,
                    'status': member.status,
                    'end_date': member.end_date
                }
            })

        except Member.DoesNotExist:
            return Response(
                {'error': '会员不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
