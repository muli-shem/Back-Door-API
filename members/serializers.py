from rest_framework import serializers
from members.models import MemberProfile
from accounts.serializers import CustomUserSerializer

class MemberProfileSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    
    class Meta:
        model = MemberProfile
        fields = ['id', 'user', 'phone', 'county', 'skills', 'profession', 'portfolio_url', 'bio', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']