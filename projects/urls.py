from django.urls import path, include
from rest_framework.routers import DefaultRouter
from projects.views import IdeaViewSet, ProposalViewSet, MilestoneViewSet

router = DefaultRouter()
router.register(r'ideas', IdeaViewSet, basename='idea')
router.register(r'proposals', ProposalViewSet, basename='proposal')
router.register(r'milestones', MilestoneViewSet, basename='milestone')

urlpatterns = [
    path('', include(router.urls)),
]