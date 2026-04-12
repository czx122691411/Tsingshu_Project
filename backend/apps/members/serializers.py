from rest_framework import serializers
from .models import Member, Payment


class PaymentSerializer(serializers.ModelSerializer):
    """缴费流水序列化器"""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'amount', 'pay_date', 'note', 'created_by_name', 'created_at']
        read_only_fields = ['id', 'created_at']


class MemberSerializer(serializers.ModelSerializer):
    """会员序列化器"""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Member
        fields = [
            'id', 'code', 'name', 'phone', 'start_date', 'end_date',
            'pay_date', 'status', 'status_display', 'note',
            'created_by_name', 'created_at', 'updated_at', 'payments'
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']


class MemberListSerializer(serializers.ModelSerializer):
    """会员列表序列化器（简化版）"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Member
        fields = [
            'id', 'code', 'name', 'phone', 'start_date', 'end_date',
            'pay_date', 'status', 'status_display', 'note'
        ]


class MemberCreateSerializer(serializers.ModelSerializer):
    """会员创建序列化器"""
    class Meta:
        model = Member
        fields = ['code', 'name', 'phone', 'start_date', 'end_date', 'pay_date', 'note']
        extra_kwargs = {
            'code': {'required': False, 'allow_blank': True}
        }

    def validate(self, attrs):
        print(f"DEBUG - validate called with attrs: {attrs}")
        # Convert empty string code to None for auto-generation
        if attrs.get('code') == '':
            attrs['code'] = None
        print(f"DEBUG - attrs after processing: {attrs}")
        return attrs

    def create(self, validated_data, **kwargs):
        """创建会员时自动生成会员号和初始缴费记录"""
        print(f"DEBUG - validated_data: {validated_data}")
        print(f"DEBUG - kwargs: {kwargs}")

        # Generate code if not provided or None
        code = validated_data.pop('code', None)
        if not code:
            code = Member.generate_code()

        # Get created_by from kwargs (passed from perform_create)
        created_by = kwargs.get('created_by')

        # Build member data with generated code
        member_data = {
            'code': code,
            **validated_data
        }

        # Only add created_by if it was provided
        if created_by:
            member_data['created_by'] = created_by

        print(f"DEBUG - member_data: {member_data}")
        member = Member.objects.create(**member_data)

        # 创建初始缴费记录
        Payment.objects.create(
            member=member,
            amount=365,
            pay_date=member.pay_date,
            note='会员费',
            created_by=self.context['request'].user
        )

        return member


class RenewSerializer(serializers.Serializer):
    """续费序列化器"""
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, default=365)
    note = serializers.CharField(max_length=200, default='续费')
