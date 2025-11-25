from django.contrib import admin
from projects.models import Idea, Proposal, Milestone

@admin.register(Idea)
class IdeaAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'user__email']

@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ['idea', 'approved_by', 'created_at']
    search_fields = ['idea__title']

@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ['title', 'idea', 'status', 'due_date']
    list_filter = ['status', 'due_date']