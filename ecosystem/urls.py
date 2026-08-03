# ecosystem/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StartupViewSet, 
    InvestorViewSet, 
    MentorViewSet, 
    CompetitionViewSet, 
    AchievementViewSet, 
    InteractionViewSet
)

# Initialize the DRF Router
router = DefaultRouter()

# Register Ecosystem ViewSets
router.register(r'startups', StartupViewSet, basename='startup')
router.register(r'investors', InvestorViewSet, basename='investor')
router.register(r'mentors', MentorViewSet, basename='mentor')
router.register(r'competitions', CompetitionViewSet, basename='competition')
router.register(r'achievements', AchievementViewSet, basename='achievement')
router.register(r'interactions', InteractionViewSet, basename='interaction')

urlpatterns = [
    path('', include(router.urls)),
]