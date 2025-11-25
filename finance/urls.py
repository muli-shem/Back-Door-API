from django.urls import path, include
from rest_framework.routers import DefaultRouter
from finance.views import MMFTopUpViewSet, WithdrawalRequestViewSet, AuditRecordViewSet, finance_summary, member_rankings

router = DefaultRouter()
router.register(r'topups', MMFTopUpViewSet, basename='topup')
router.register(r'withdrawals', WithdrawalRequestViewSet, basename='withdrawal')
router.register(r'audits', AuditRecordViewSet)

urlpatterns = [
    path('summary/', finance_summary, name='finance_summary'),
    path('rankings/', member_rankings, name='member_rankings'),
    path('', include(router.urls)),
]