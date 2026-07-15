"""
apps/ecosystem/views.py
Campus Innovation & Engagement Intelligence Hub — Phase 2, Week 5
CRUD ViewSets for all core ecosystem entities.
"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from accounts.models import Profile
from ecosystem.models import (
    Achievement,
    Competition,
    Interaction,
    Investor,
    Startup,
)
from ecosystem.serializers import (
    AchievementSerializer,
    CompetitionSummarySerializer,
    InvestorSerializer,
    InteractionSummarySerializer,
    ProfileSerializer,
    StartupSerializer,
)

# ── Shared pagination ─────────────────────────────────────────────────────────

class EcosystemPagination(PageNumberPagination):
    page_size            = 20
    page_size_query_param = "page_size"
    max_page_size        = 100


# ── Shared filter backends ────────────────────────────────────────────────────

FILTER_BACKENDS = [DjangoFilterBackend, SearchFilter, OrderingFilter]


# ── Profile ───────────────────────────────────────────────────────────────────

class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class   = ProfileSerializer
    pagination_class   = EcosystemPagination
    permission_classes = [IsAuthenticated]
    filter_backends    = FILTER_BACKENDS

    filterset_fields = ["department", "graduation_year", "location"]
    search_fields    = ["user__full_name", "bio", "headline"]
    ordering_fields  = [
        "user__full_name", "graduation_year",
        "achievement_impact_score", "grit_index", "pagerank_score",
    ]
    ordering = ["-id"]

    def get_queryset(self):
        return (
            Profile.objects
            .select_related("user")
            .prefetch_related("achievements", "user__interactions_initiated",
                              "user__interactions_received")
        )


# ── Startup ───────────────────────────────────────────────────────────────────

class StartupViewSet(viewsets.ModelViewSet):
    serializer_class   = StartupSerializer
    pagination_class   = EcosystemPagination
    permission_classes = [IsAuthenticated]
    filter_backends    = FILTER_BACKENDS

    filterset_fields = ["sector", "stage", "is_active", "founder"]
    search_fields    = ["startup_name", "tagline", "pitch_summary", "sector"]
    ordering_fields  = [
        "startup_name", "stage", "team_size",
        "trl",
    ]
    ordering = ["-id"]

    def get_queryset(self):
        return (
            Startup.objects
            .select_related("founder")
            .prefetch_related("achievements", "interactions")
        )

    def perform_create(self, serializer):
        serializer.save(founder=self.request.user)


# ── Investor ──────────────────────────────────────────────────────────────────

class InvestorViewSet(viewsets.ModelViewSet):
    serializer_class   = InvestorSerializer
    pagination_class   = EcosystemPagination
    permission_classes = [IsAuthenticated]
    filter_backends    = FILTER_BACKENDS

    filterset_fields = ["is_active"]
    search_fields    = ["firm_name", "designation", "mandate"]
    ordering_fields  = [
        "firm_name", "check_size_min", "check_size_max", "portfolio_count",
    ]
    ordering = ["firm_name"]

    def get_queryset(self):
        return (
            Investor.objects
            .select_related("user", "user__profile")
        )


# ── Achievement ───────────────────────────────────────────────────────────────

class AchievementSerializer_ (AchievementSerializer):
    """Local alias — avoids import shadowing."""
    pass


class AchievementViewSet(viewsets.ModelViewSet):
    serializer_class   = AchievementSerializer
    pagination_class   = EcosystemPagination
    permission_classes = [IsAuthenticated]
    filter_backends    = FILTER_BACKENDS

    filterset_fields = [
        "category", "verified", "nirf_countable",
        "profile", "startup", "competition",
    ]
    search_fields    = ["title", "rank_or_prize"]
    ordering_fields  = ["date", "ner_confidence", "title"]
    ordering         = ["-date", "-id"]

    def get_queryset(self):
        return (
            Achievement.objects
            .select_related("profile", "startup", "competition")
        )


# ── Interaction ───────────────────────────────────────────────────────────────

class InteractionViewSet(viewsets.ModelViewSet):
    serializer_class   = InteractionSummarySerializer
    pagination_class   = EcosystemPagination
    permission_classes = [IsAuthenticated]
    filter_backends    = FILTER_BACKENDS

    filterset_fields = ["type", "outcome", "actor", "target", "startup", "success_label"]
    search_fields    = ["notes"]
    ordering_fields  = ["duration_hours", "created_at", "id"]
    ordering         = ["-created_at"]

    def get_queryset(self):
        return (
            Interaction.objects
            .select_related("actor", "target", "startup")
        )

    def perform_create(self, serializer):
        serializer.save(actor=self.request.user)


# ── Competition ───────────────────────────────────────────────────────────────

class CompetitionViewSet(viewsets.ModelViewSet):
    serializer_class   = CompetitionSummarySerializer
    pagination_class   = EcosystemPagination
    permission_classes = [IsAuthenticated]
    filter_backends    = FILTER_BACKENDS

    filterset_fields = ["nirf_recognised", "organiser"]
    search_fields    = ["name", "organiser"]
    ordering_fields  = ["event_date", "deadline", "name"]
    ordering         = ["-event_date"]

    def get_queryset(self):
        return Competition.objects.select_related("created_by")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)