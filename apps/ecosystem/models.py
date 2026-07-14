"""
apps/ecosystem/models.py
Campus Innovation & Engagement Intelligence Hub — Phase 2
Startup, Investor, Mentor, Competition, Achievement, Interaction
"""

import uuid
from django.conf import settings
from django.db import models


# ── Existing models (Startup, Investor, Mentor) remain above ──────────────────
# Only the three new lifecycle models are shown here for the Week 4 delivery.
# Paste below the existing Startup / Investor / Mentor definitions.


# ── Shared choices ────────────────────────────────────────────────────────────

class AchievementCategory(models.TextChoices):
    COMPETITION  = "competition",   "Competition"
    PATENT       = "patent",        "Patent"
    PUBLICATION  = "publication",   "Publication"
    TECH_TRANSFER = "tech_transfer", "Tech Transfer"
    LEADERSHIP   = "leadership",    "Leadership"
    PROJECT      = "project",       "Project"
    INTERNSHIP   = "internship",    "Internship"
    FELLOWSHIP   = "fellowship",    "Fellowship"
    AWARD        = "award",         "Award"


class InteractionType(models.TextChoices):
    MENTORSHIP       = "mentorship",        "Mentorship"
    FUNDING_MATCH    = "funding_match",     "Funding Match"
    CLUB_MEMBERSHIP  = "club_membership",   "Club Membership"
    COMPETITION_TEAM = "competition_team",  "Competition Team"
    MOU              = "mou",               "MoU"


class InteractionOutcome(models.TextChoices):
    PENDING  = "pending",  "Pending"
    ACCEPTED = "accepted", "Accepted"
    DECLINED = "declined", "Declined"
    CLOSED   = "closed",   "Closed"


# ── Competition ───────────────────────────────────────────────────────────────

class Competition(models.Model):
    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name            = models.CharField(max_length=200)
    organiser       = models.CharField(max_length=150, blank=True)
    event_date      = models.DateField(null=True, blank=True)
    deadline        = models.DateField(null=True, blank=True)
    nirf_recognised = models.BooleanField(default=False)
    eligible_roles  = models.JSONField(default=list)   # ["student", "alumni"]
    created_by      = models.ForeignKey(
                          settings.AUTH_USER_MODEL,
                          on_delete=models.SET_NULL,
                          null=True,
                          blank=True,
                          related_name="competitions_created",
                      )
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ecosystem_competition"
        ordering = ["-event_date"]

    def __str__(self) -> str:
        return self.name


# ── Achievement ───────────────────────────────────────────────────────────────

class Achievement(models.Model):
    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile         = models.ForeignKey(
                          "accounts.Profile",
                          on_delete=models.CASCADE,
                          related_name="achievements",
                      )
    startup         = models.ForeignKey(
                          "ecosystem.Startup",
                          on_delete=models.SET_NULL,
                          null=True,
                          blank=True,
                          related_name="achievements",
                      )
    competition     = models.ForeignKey(
                          Competition,
                          on_delete=models.SET_NULL,
                          null=True,
                          blank=True,
                          related_name="achievements",
                      )
    category        = models.CharField(
                          max_length=30,
                          choices=AchievementCategory.choices,
                          default=AchievementCategory.COMPETITION,
                      )
    title           = models.CharField(max_length=240)
    rank_or_prize   = models.CharField(max_length=120, blank=True)
    date            = models.DateField(null=True, blank=True)
    verified        = models.BooleanField(default=False)
    certificate_path = models.CharField(max_length=512, blank=True)
    ner_confidence  = models.FloatField(null=True, blank=True)
    topic_tags      = models.JSONField(default=list)    # ["Leadership", "ML"]
    nirf_countable  = models.BooleanField(default=False)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ecosystem_achievement"
        ordering = ["-date", "-created_at"]

    def __str__(self) -> str:
        return f"{self.title} — {self.profile}"


# ── Interaction ───────────────────────────────────────────────────────────────

class Interaction(models.Model):
    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor         = models.ForeignKey(
                        settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                        related_name="interactions_initiated",
                    )
    target        = models.ForeignKey(
                        settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                        related_name="interactions_received",
                    )
    type          = models.CharField(
                        max_length=30,
                        choices=InteractionType.choices,
                    )
    outcome       = models.CharField(
                        max_length=20,
                        choices=InteractionOutcome.choices,
                        default=InteractionOutcome.PENDING,
                    )
    duration_hours = models.FloatField(null=True, blank=True)
    startup       = models.ForeignKey(
                        "ecosystem.Startup",
                        on_delete=models.SET_NULL,
                        null=True,
                        blank=True,
                        related_name="interactions",
                    )
    success_label = models.BooleanField(null=True, blank=True)   # telemetry: written on "Connect" click
    notes         = models.TextField(blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ecosystem_interaction"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.actor} → {self.target} [{self.type} / {self.outcome}]"