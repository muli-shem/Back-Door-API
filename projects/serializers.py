from rest_framework import serializers
from projects.models import Idea, Proposal, Milestone
from accounts.serializers import CustomUserSerializer

class MilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = ['id', 'title', 'description', 'due_date', 'status']

class ProposalSerializer(serializers.ModelSerializer):
    approved_by = CustomUserSerializer(read_only=True)
    
    class Meta:
        model = Proposal
        fields = ['id', 'document_url', 'description', 'approved_by', 'created_at']
        read_only_fields = ['id', 'created_at']

class IdeaSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    proposals = ProposalSerializer(many=True, read_only=True)
    milestones = MilestoneSerializer(many=True, read_only=True)
    
    class Meta:
        model = Idea
        fields = ['id', 'user', 'title', 'problem_statement', 'proposed_solution', 'status', 'proposals', 'milestones', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']