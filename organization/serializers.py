from rest_framework import serializers
from organization.models import Announcement, Event, MembershipApplication

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['id', 'title', 'message', 'priority', 'image', 'created_at']
        read_only_fields = ['id', 'created_at']

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'date', 'venue', 'description', 'image', 'link', 'created_at']
        read_only_fields = ['id', 'created_at']

class MembershipApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipApplication
        fields = ['id', 'full_name', 'email', 'county', 'motivation', 'status', 'submitted_at']
        read_only_fields = ['id', 'submitted_at']