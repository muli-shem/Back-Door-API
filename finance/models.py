from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class MMFTopUp(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Success', 'Success'),
        ('Failed', 'Failed'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='topups')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    month = models.DateField()
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    transaction_id = models.CharField(max_length=100, blank=True, unique=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name = 'MMF Top Up'
        verbose_name_plural = 'MMF Top Ups'
        unique_together = ['user', 'month']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.amount} ({self.month})"

class WithdrawalRequest(models.Model):
    APPROVAL_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='withdrawals')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    reason = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    approval_status = models.CharField(max_length=20, choices=APPROVAL_CHOICES, default='Pending')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_withdrawals')
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name = 'Withdrawal Request'
        verbose_name_plural = 'Withdrawal Requests'
    
    def __str__(self):
        return f"{self.user.full_name} - {self.amount} ({self.approval_status})"

class AuditRecord(models.Model):
    auditor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='audits')
    month = models.DateField()
    total_topups = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_withdrawals = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    member_count = models.IntegerField(default=0)
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-month']
        unique_together = ['auditor', 'month']
    
    def __str__(self):
        return f"Audit - {self.month} by {self.auditor.full_name}"