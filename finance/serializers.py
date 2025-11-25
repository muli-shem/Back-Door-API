from rest_framework import serializers
from finance.models import MMFTopUp, WithdrawalRequest, AuditRecord
from accounts.serializers import CustomUserSerializer

class MMFTopUpSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    
    class Meta:
        model = MMFTopUp
        fields = ['id', 'user', 'amount', 'month', 'date', 'status', 'transaction_id', 'notes']
        read_only_fields = ['id', 'date']

class WithdrawalRequestSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    approved_by = CustomUserSerializer(read_only=True)
    
    class Meta:
        model = WithdrawalRequest
        fields = ['id', 'user', 'amount', 'reason', 'date', 'approval_status', 'approved_by', 'notes']
        read_only_fields = ['id', 'date', 'approved_by']

class AuditRecordSerializer(serializers.ModelSerializer):
    auditor = CustomUserSerializer(read_only=True)
    
    class Meta:
        model = AuditRecord
        fields = ['id', 'auditor', 'month', 'total_topups', 'total_withdrawals', 'member_count', 'comments', 'created_at']
        read_only_fields = ['id', 'created_at']