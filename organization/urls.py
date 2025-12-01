from django.urls import path, include
from rest_framework.routers import DefaultRouter
from organization.views import (
    AnnouncementViewSet, EventViewSet, MembershipApplicationViewSet, 
    recent_announcements, next_event, organization_stats
)

router = DefaultRouter()
router.register(r'announcements', AnnouncementViewSet, basename='announcement')
router.register(r'events', EventViewSet, basename='event')
router.register(r'applications', MembershipApplicationViewSet, basename='application')

urlpatterns = [
    # ✅ CUSTOM ROUTES FIRST - these need to match before the router patterns
    path('announcements/recent/', recent_announcements, name='recent_announcements'),
    path('events/next/', next_event, name='next_event'),
    path('stats/', organization_stats, name='org_stats'),
    
    # ✅ ROUTER LAST - catch-all patterns
    path('', include(router.urls)),
]