from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from organization.models import Announcement, Event, MembershipApplication
from organization.serializers import AnnouncementSerializer, EventSerializer, MembershipApplicationSerializer
from django.utils import timezone

class AnnouncementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.AllowAny]

class EventViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return Event.objects.filter(date__gte=timezone.now())

class MembershipApplicationViewSet(viewsets.ModelViewSet):
    queryset = MembershipApplication.objects.all()
    serializer_class = MembershipApplicationSerializer
    permission_classes = [permissions.AllowAny]

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def recent_announcements(request):
    announcements = Announcement.objects.all()[:5]
    serializer = AnnouncementSerializer(announcements, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def next_event(request):
    event = Event.objects.filter(date__gte=timezone.now()).first()
    if event:
        serializer = EventSerializer(event)
        return Response(serializer.data)
    return Response({'detail': 'No upcoming events'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def organization_stats(request):
    pending_apps = MembershipApplication.objects.filter(status='Pending').count()
    total_events = Event.objects.filter(date__gte=timezone.now()).count()
    total_announcements = Announcement.objects.count()
    
    return Response({
        'pending_applications': pending_apps,
        'upcoming_events': total_events,
        'total_announcements': total_announcements,
    })