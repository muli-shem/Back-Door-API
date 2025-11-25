from django.contrib import admin
from members.models import MemberProfile

@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'county', 'profession', 'created_at']
    list_filter = ['county', 'profession', 'created_at']
    search_fields = ['user__full_name', 'user__email', 'county']
    readonly_fields = ['created_at', 'updated_at']