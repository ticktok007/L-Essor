# Ecosystem models — Campus Innovation & Engagement Intelligence Hub
# Startup, Investor, Mentor, Competition, Achievement models defined in Phase 2.
"""
ecosystem/models.py
Campus Innovation & Engagement Intelligence Hub — Phase 2
Startup, Investor, Mentor domain models
"""

import uuid
from django.db import models
from django.conf import settings


# ── Stage choices ─────────────────────────────────────────────────────────────

class StartupStage(models.TextChoices):
    IDEA          = "idea",          "Idea"
    MVP           = "mvp",           "MVP"
    EARLY_REVENUE = "early_revenue", "Early Revenue"
    GROWTH        = "growth",        "Growth"


# ── Startup ───────────────────────────────────────────────────────────────────

class Startup(models.Model):
    id                 = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    founder            = models.ForeignKey(
                             settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name="startups",
                         )
    startup_name       = models.CharField(max_length=150)
    tagline            = models.CharField(max_length=250, blank=True)
    pitch_summary      = models.TextField(blank=True)
    sector             = models.CharField(max_length=100, blank=True)
    problem_statement  = models.TextField(blank=True)
    solution_summary   = models.TextField(blank=True)
    stage              = models.CharField(
                             max_length=20,
                             choices=StartupStage.choices,
                             default=StartupStage.IDEA,
                         )
    trl                = models.PositiveIntegerField(null=True, blank=True)   # 1–9
    website_url        = models.URLField(blank=True)
    deck_url           = models.URLField(blank=True)
    team_size          = models.PositiveIntegerField(default=1)
    is_active          = models.BooleanField(default=True)
    created_at         = models.DateTimeField(auto_now_add=True)
    updated_at         = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ecosystem_startup"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.startup_name} [{self.stage}]"


# ── Investor ──────────────────────────────────────────────────────────────────

class Investor(models.Model):
    id               = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user             = models.OneToOneField(
                           settings.AUTH_USER_MODEL,
                           on_delete=models.CASCADE,
                           related_name="investor_profile",
                       )
    firm_name        = models.CharField(max_length=150)
    designation      = models.CharField(max_length=120, blank=True)
    mandate          = models.TextField(blank=True)
    sectors          = models.JSONField(default=list)   # ["HealthTech", "FinTech"]
    stages           = models.JSONField(default=list)   # ["idea", "mvp"]
    check_size_min   = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    check_size_max   = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    portfolio_count  = models.PositiveIntegerField(default=0)
    website_url      = models.URLField(blank=True)
    linkedin_url     = models.URLField(blank=True)
    is_active        = models.BooleanField(default=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ecosystem_investor"

    def __str__(self) -> str:
        return f"{self.user.full_name} @ {self.firm_name}"


# ── Mentor ────────────────────────────────────────────────────────────────────

class Mentor(models.Model):
    id                           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user                         = models.OneToOneField(
                                       settings.AUTH_USER_MODEL,
                                       on_delete=models.CASCADE,
                                       related_name="mentor_profile",
                                   )
    expertise_areas              = models.JSONField(default=list)   # ["Product Strategy", "Fundraising"]
    current_role                 = models.CharField(max_length=150, blank=True)
    organization                 = models.CharField(max_length=150, blank=True)
    years_of_experience          = models.PositiveIntegerField(null=True, blank=True)
    availability_hours_per_month = models.PositiveIntegerField(null=True, blank=True)
    bio                          = models.TextField(blank=True)
    linkedin_url                 = models.URLField(blank=True)
    is_active                    = models.BooleanField(default=True)
    created_at                   = models.DateTimeField(auto_now_add=True)
    updated_at                   = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ecosystem_mentor"

    def __str__(self) -> str:
        return f"{self.user.full_name} — {self.current_role} @ {self.organization}"