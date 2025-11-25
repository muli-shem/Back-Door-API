from django.db import models
from django.conf import settings
from django.core.validators import URLValidator

class MemberProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='member_profile')
    phone = models.CharField(max_length=20, blank=True)
    county = models.CharField(max_length=100, blank=True)
    skills = models.TextField(blank=True, help_text="Comma-separated skills")
    profession = models.CharField(max_length=100, blank=True)
    portfolio_url = models.URLField(blank=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Member Profile'
        verbose_name_plural = 'Member Profiles'
    
    def __str__(self):
        return f"{self.user.full_name}'s Profile"