from django.contrib import admin
from finance.models import MMFTopUp, WithdrawalRequest, AuditRecord

@admin.register(MMFTopUp)
class MMFTopUpAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'month', 'status', 'date']
    list_filter = ['status', 'month', 'date']
    search_fields = ['user__email', 'user__full_name', 'transaction_id']
    readonly_fields = ['date']

@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'approval_status', 'date']
    list_filter = ['approval_status', 'date']
    search_fields = ['user__email', 'user__full_name']
    readonly_fields = ['date']

@admin.register(AuditRecord)
class AuditRecordAdmin(admin.ModelAdmin):
    list_display = ['auditor', 'month', 'total_topups', 'total_withdrawals', 'created_at']
    list_filter = ['month', 'created_at']
    search_fields = ['auditor__email']
    readonly_fields = ['created_at']