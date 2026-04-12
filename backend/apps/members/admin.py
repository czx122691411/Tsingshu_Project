from django.contrib import admin
from .models import Member, Payment


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'phone', 'status', 'start_date', 'end_date']
    list_filter = ['status']
    search_fields = ['code', 'name', 'phone']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['member', 'amount', 'pay_date', 'note']
    list_filter = ['pay_date']
    search_fields = ['member__code', 'member__name']
