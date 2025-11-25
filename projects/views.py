from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from projects.models import Idea, Proposal, Milestone
from projects.serializers import IdeaSerializer, ProposalSerializer, MilestoneSerializer

class IdeaViewSet(viewsets.ModelViewSet):
    serializer_class = IdeaSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Idea.objects.all()
        return Idea.objects.filter(user=self.request.user) | Idea.objects.filter(status='Approved')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ProposalViewSet(viewsets.ModelViewSet):
    serializer_class = ProposalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Proposal.objects.all()

class MilestoneViewSet(viewsets.ModelViewSet):
    serializer_class = MilestoneSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Milestone.objects.all()