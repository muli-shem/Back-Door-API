from django.urls import path, include
from rest_framework.routers import DefaultRouter
from organization.views import (
    AnnouncementViewSet, EventViewSet, MembershipApplicationViewSet, 
    recent_announcements, next_event, organization_stats
)

router = DefaultRouter()
router.register(r'announcements', AnnouncementViewSet)
router.register(r'events', EventViewSet, basename='event')
router.register(r'applications', MembershipApplicationViewSet)

urlpatterns = [
    path('announcements/recent/', recent_announcements, name='recent_announcements'),
    path('events/next/', next_event, name='next_event'),
    path('stats/', organization_stats, name='org_stats'),
    path('', include(router.urls)),
]