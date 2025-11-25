from django.db import models
from django.conf import settings

class Idea(models.Model):
    STATUS_CHOICES = [
        ('Submitted', 'Submitted'),
        ('Reviewing', 'Reviewing'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ideas')
    title = models.CharField(max_length=255)
    problem_statement = models.TextField()
    proposed_solution = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Submitted')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Blessed Mind Idea'
        verbose_name_plural = 'Blessed Mind Ideas'
    
    def __str__(self):
        return self.title

class Proposal(models.Model):
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name='proposals')
    document_url = models.URLField()
    description = models.TextField(blank=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_proposals')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Proposal for {self.idea.title}"

class Milestone(models.Model):
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=[('Not Started', 'Not Started'), ('In Progress', 'In Progress'), ('Completed', 'Completed')])
    
    def __str__(self):
        return self.title