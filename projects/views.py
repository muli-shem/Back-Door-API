from rest_framework import viewsets, permissions
from rest_framework.response import Response
from projects.models import Idea, Proposal, Milestone
from projects.serializers import IdeaSerializer, ProposalSerializer, MilestoneSerializer

class IdeaViewSet(viewsets.ModelViewSet):
    serializer_class = IdeaSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Admin sees everything
        if hasattr(user, 'role') and user.role == 'admin':
            return Idea.objects.all()
        
        # Regular users see their own ideas + approved ones
        # This will return an empty queryset if no data exists - that's OK!
        return Idea.objects.filter(user=user) | Idea.objects.filter(status='approved')
    
    def list(self, request, *args, **kwargs):
        # Override list to always return 200 even if empty
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=200)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProposalViewSet(viewsets.ModelViewSet):
    serializer_class = ProposalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Return all proposals for now - adjust as needed
        return Proposal.objects.all()
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=200)


class MilestoneViewSet(viewsets.ModelViewSet):
    serializer_class = MilestoneSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Milestone.objects.all()