# ecosystem/views.py
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Startup, Investor, Mentor, Competition, Achievement, Interaction
from .serializers import (
    StartupSerializer, 
    InvestorSerializer, 
    MentorSerializer, 
    CompetitionSerializer, 
    AchievementSerializer, 
    InteractionSummarySerializer
)

@extend_schema(tags=["Ecosystem - Startups"])
class StartupViewSet(viewsets.ModelViewSet):
    """ViewSet for managing student and alumni startups."""
    queryset = Startup.objects.all()
    serializer_class = StartupSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Register a startup",
        examples=[
            OpenApiExample(
                "Startup Request",
                value={
                    "startup_name": "MediTech AI",
                    "pitch_summary": "AI for rural diagnostics",
                    "sector": "HealthTech",
                    "stage": "mvp",
                    "trl": 4
                }
            )
        ]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

@extend_schema(tags=["Ecosystem - Investors"])
class InvestorViewSet(viewsets.ModelViewSet):
    """ViewSet for managing investor profiles and mandates."""
    queryset = Investor.objects.all()
    serializer_class = InvestorSerializer
    permission_classes = [IsAuthenticated]

@extend_schema(tags=["Ecosystem - Mentors"])
class MentorViewSet(viewsets.ModelViewSet):
    """ViewSet for managing mentor expertise and availability."""
    queryset = Mentor.objects.all()
    serializer_class = MentorSerializer
    permission_classes = [IsAuthenticated]

@extend_schema(tags=["Ecosystem - Events"])
class CompetitionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing hackathons and innovation challenges."""
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    permission_classes = [IsAuthenticated]

@extend_schema(tags=["Ecosystem - Portfolio"])
class AchievementViewSet(viewsets.ModelViewSet):
    """ViewSet for individual and startup achievements/awards."""
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
    permission_classes = [IsAuthenticated]

@extend_schema(tags=["Ecosystem - Social Graph"])
class InteractionViewSet(viewsets.ModelViewSet):
    """ViewSet for tracking mentor sessions and investor matches."""
    queryset = Interaction.objects.all()
    serializer_class = InteractionSummarySerializer
    permission_classes = [IsAuthenticated]