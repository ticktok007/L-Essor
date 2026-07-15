"""
apps/ecosystem/urls.py
Campus Innovation & Engagement Intelligence Hub — Phase 2, Week 5
DefaultRouter registration for all ecosystem ViewSets.

Include in root urls.py:
    path("api/v1/", include("apps.ecosystem.urls")),
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from ecosystem.views import (
    AchievementViewSet,
    CompetitionViewSet,
    InteractionViewSet,
    InvestorViewSet,
    ProfileViewSet,
    StartupViewSet,
)

router = DefaultRouter()
router.register(r"profiles",      ProfileViewSet,     basename="profile")
router.register(r"startups",      StartupViewSet,     basename="startup")
router.register(r"investors",     InvestorViewSet,    basename="investor")
router.register(r"achievements",  AchievementViewSet, basename="achievement")
router.register(r"interactions",  InteractionViewSet, basename="interaction")
router.register(r"competitions",  CompetitionViewSet, basename="competition")

urlpatterns = [
    path("", include(router.urls)),
]