from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from finance.models import MMFTopUp, WithdrawalRequest, AuditRecord
from finance.serializers import MMFTopUpSerializer, WithdrawalRequestSerializer, AuditRecordSerializer
from django.db.models import Sum
from django.utils import timezone

class MMFTopUpViewSet(viewsets.ModelViewSet):
    serializer_class = MMFTopUpSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role == 'admin':
            return MMFTopUp.objects.all()
        return MMFTopUp.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class WithdrawalRequestViewSet(viewsets.ModelViewSet):
    serializer_class = WithdrawalRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role == 'admin':
            return WithdrawalRequest.objects.all()
        return WithdrawalRequest.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class AuditRecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditRecord.objects.all()
    serializer_class = AuditRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def finance_summary(request):
    user = request.user
    today = timezone.now().date()
    
    total_contributions = MMFTopUp.objects.filter(
        user=user, status='Success'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    this_month_total = MMFTopUp.objects.filter(
        user=user, status='Success', 
        date__month=today.month, date__year=today.year
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    pending_withdrawal = WithdrawalRequest.objects.filter(
        user=user, approval_status='Pending'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    approved_withdrawal = WithdrawalRequest.objects.filter(
        user=user, approval_status='Approved'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    return Response({
        'total_contributions': total_contributions,
        'this_month_total': this_month_total,
        'pending_withdrawal': pending_withdrawal,
        'approved_withdrawal': approved_withdrawal,
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def member_rankings(request):
    rankings = MMFTopUp.objects.filter(
        status='Success'
    ).values('user__full_name', 'user__id').annotate(
        total=Sum('amount')
    ).order_by('-total')[:20]
    
    return Response(rankings)