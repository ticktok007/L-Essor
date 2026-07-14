"""
apps/ecosystem/serializers.py
Campus Innovation & Engagement Intelligence Hub — Phase 2, Week 5
DRF serializers: Profile, Startup, Investor, Achievement
"""

from rest_framework import serializers

from accounts.models import Profile
from ecosystem.models import (
    Achievement,
    Competition,
    Interaction,
    Investor,
    Startup,
)


# ── Inline nested: Competition summary ────────────────────────────────────────

class CompetitionSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Competition
        fields = ["id", "name", "organiser", "event_date", "nirf_recognised"]
        read_only_fields = fields


# ── Inline nested: Interaction summary ────────────────────────────────────────

class InteractionSummarySerializer(serializers.ModelSerializer):
    actor_id  = serializers.UUIDField(source="actor.id",  read_only=True)
    target_id = serializers.UUIDField(source="target.id", read_only=True)

    class Meta:
        model  = Interaction
        fields = [
            "id", "actor_id", "target_id",
            "type", "outcome", "duration_hours",
            "success_label", "created_at",
        ]
        read_only_fields = fields


# ── Inline nested: Achievement summary (used inside Profile / Startup) ────────

class AchievementSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Achievement
        fields = [
            "id", "category", "title", "rank_or_prize",
            "date", "verified", "nirf_countable",
        ]
        read_only_fields = fields


# ── Inline nested: Profile summary (used inside Investor) ─────────────────────

class ProfileSummarySerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    email     = serializers.EmailField(source="user.email",    read_only=True)

    class Meta:
        model  = Profile
        fields = [
            "id", "full_name", "email",
            "department", "bio",
            "achievement_impact_score", "grit_index",
        ]
        read_only_fields = fields


# ── Achievement ───────────────────────────────────────────────────────────────

class AchievementSerializer(serializers.ModelSerializer):
    # Nested read-only competition summary
    competition_summary = CompetitionSummarySerializer(
        source="competition", read_only=True
    )

    class Meta:
        model  = Achievement
        fields = [
            "id",
            "profile",
            "startup",
            "competition",
            "competition_summary",
            "category",
            "title",
            "rank_or_prize",
            "date",
            "verified",
            "certificate_path",
            "ner_confidence",
            "topic_tags",
            "nirf_countable",
        ]
        read_only_fields = [
            "id",
            "competition_summary",
            "verified",
            "ner_confidence",
        ]
        extra_kwargs = {
            "startup":     {"required": False, "allow_null": True},
            "competition": {"required": False, "allow_null": True},
        }


# ── Profile ───────────────────────────────────────────────────────────────────

class ProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.full_name", read_only=True)

    # Nested read-only lifecycle history
    achievements = AchievementSummarySerializer(
        many=True, read_only=True
    )
    outgoing_interactions = InteractionSummarySerializer(
        source="user.interactions_initiated",
        many=True, read_only=True,
    )
    incoming_interactions = InteractionSummarySerializer(
        source="user.interactions_received",
        many=True, read_only=True,
    )

    class Meta:
        model  = Profile
        fields = [
            "id",
            "full_name",
            "department",
            "bio",
            "graduation_year",
            "skills",
            "interests",
            "location",
            "linkedin_url",
            "github_url",
            "portfolio_url",
            # Computed / graph scores — read-only, written by Celery tasks
            "betweenness_centrality",
            "pagerank_score",
            "community_id",
            "achievement_impact_score",
            "grit_index",
            "at_risk_flag",
            "profile_completion_pct",
            # Nested history
            "achievements",
            "outgoing_interactions",
            "incoming_interactions",
        ]
        read_only_fields = [
            "id",
            "full_name",
            "betweenness_centrality",
            "pagerank_score",
            "community_id",
            "achievement_impact_score",
            "grit_index",
            "at_risk_flag",
            "profile_completion_pct",
            "achievements",
            "outgoing_interactions",
            "incoming_interactions",
        ]

    def get_fields(self):
        """
        Dynamically add computed score fields that may not exist on the model
        yet (added via Celery in Phase 5/4). Fall back gracefully if absent.
        """
        fields = super().get_fields()
        computed = [
            "betweenness_centrality", "pagerank_score", "community_id",
            "achievement_impact_score", "grit_index",
            "at_risk_flag", "profile_completion_pct",
        ]
        for f in computed:
            if f not in [field.name for field in Profile._meta.get_fields()]:
                fields.pop(f, None)
        return fields


# ── Startup ───────────────────────────────────────────────────────────────────

class StartupSerializer(serializers.ModelSerializer):
    # Nested read-only lifecycle history
    achievements = AchievementSummarySerializer(
        many=True, read_only=True
    )
    interactions = InteractionSummarySerializer(
        many=True, read_only=True
    )

    class Meta:
        model  = Startup
        fields = [
            "id",
            "founder",
            "startup_name",
            "tagline",
            "pitch_summary",
            "sector",
            "problem_statement",
            "solution_summary",
            "stage",
            "trl",
            "website_url",
            "deck_url",
            "team_size",
            "is_active",
            # Computed — read-only
            "success_probability",
            "at_risk_flag",
            "mentorship_hours",
            "trl_mrl_gap",
            # Nested history
            "achievements",
            "interactions",
        ]
        read_only_fields = [
            "id",
            "success_probability",
            "at_risk_flag",
            "mentorship_hours",
            "trl_mrl_gap",
            "achievements",
            "interactions",
        ]
        extra_kwargs = {
            "founder": {"read_only": True},
        }

    def get_fields(self):
        fields = super().get_fields()
        computed = ["success_probability", "at_risk_flag", "mentorship_hours", "trl_mrl_gap"]
        for f in computed:
            if f not in [field.name for field in Startup._meta.get_fields()]:
                fields.pop(f, None)
        return fields


# ── Investor ──────────────────────────────────────────────────────────────────

class InvestorSerializer(serializers.ModelSerializer):
    # Condensed read-only profile — avoids full ProfileSerializer payload
    profile_summary = ProfileSummarySerializer(
        source="user.profile", read_only=True
    )

    class Meta:
        model  = Investor
        fields = [
            "id",
            "firm_name",
            "designation",
            "mandate",
            "sectors",
            "stages",
            "check_size_min",
            "check_size_max",
            "portfolio_count",
            "website_url",
            "linkedin_url",
            "is_active",
            # Nested read-only
            "profile_summary",
        ]
        read_only_fields = [
            "id",
            "profile_summary",
        ]