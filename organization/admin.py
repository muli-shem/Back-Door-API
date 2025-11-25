from django.contrib import admin
from organization.models import Announcement, Event, MembershipApplication

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'priority', 'created_at']
    list_filter = ['priority', 'created_at']
    search_fields = ['title', 'message']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'venue']
    list_filter = ['date']
    search_fields = ['title', 'venue']

@admin.register(MembershipApplication)
class MembershipApplicationAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'status', 'submitted_at']
    list_filter = ['status', 'submitted_at']
    search_fields = ['full_name', 'email']