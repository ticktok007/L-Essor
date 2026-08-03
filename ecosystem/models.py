"""
ecosystem/models.py
Campus Innovation & Engagement Intelligence Hub
Startup, Investor, Mentor, Competition, Achievement, Interaction domain models
"""

import uuid
from django.conf import settings
from django.db import models
from pgvector.django import VectorField


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
    pitch_embedding    = VectorField(dimensions=384, null=True, blank=True)
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
        indexes = [
            models.Index(fields=["stage"], name="startup_stage_idx"),
            models.Index(fields=["sector"], name="startup_sector_idx"),
        ]

    class Meta:
        db_table = "ecosystem_startup"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["sector"],        name="startup_sector_idx"),
            models.Index(fields=["stage"],         name="startup_stage_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.startup_name} [{self.stage}]"


# ── Investor ──────────────────────────────────────────────────────────────────

class Investor(models.Model):
    id                = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField("accounts.User", on_delete=models.CASCADE, related_name="investor_profile")
    firm_name         = models.CharField(max_length=150)
    designation       = models.CharField(max_length=120, blank=True)
    mandate_text           = models.TextField(blank=True)
    mandate_embedding = VectorField(dimensions=384, null=True, blank=True)
    sectors           = models.JSONField(default=list)   # ["HealthTech", "FinTech"]
    stages            = models.JSONField(default=list)   # ["idea", "mvp"]
    check_size_min    = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    check_size_max    = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    portfolio_count   = models.PositiveIntegerField(default=0)
    website_url       = models.URLField(blank=True)
    linkedin_url      = models.URLField(blank=True)
    is_active         = models.BooleanField(default=True)
    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)

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


# ── Shared choices ────────────────────────────────────────────────────────────

class AchievementCategory(models.TextChoices):
    COMPETITION   = "competition",   "Competition"
    PATENT        = "patent",        "Patent"
    PUBLICATION   = "publication",   "Publication"
    TECH_TRANSFER = "tech_transfer", "Tech Transfer"
    LEADERSHIP    = "leadership",    "Leadership"
    PROJECT       = "project",       "Project"
    INTERNSHIP    = "internship",    "Internship"
    FELLOWSHIP    = "fellowship",    "Fellowship"
    AWARD         = "award",         "Award"


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
    id               = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile          = models.ForeignKey(
                           "accounts.Profile",
                           on_delete=models.CASCADE,
                           related_name="achievements",
                       )
    startup          = models.ForeignKey(
                           "ecosystem.Startup",
                           on_delete=models.SET_NULL,
                           null=True,
                           blank=True,
                           related_name="achievements",
                       )
    competition      = models.ForeignKey(
                           Competition,
                           on_delete=models.SET_NULL,
                           null=True,
                           blank=True,
                           related_name="achievements",
                       )
    category         = models.CharField(
                           max_length=30,
                           choices=AchievementCategory.choices,
                           default=AchievementCategory.COMPETITION,
                       )
    title            = models.CharField(max_length=240)
    rank_or_prize    = models.CharField(max_length=120, blank=True)
    date             = models.DateField(null=True, blank=True)
    verified         = models.BooleanField(default=False)
    certificate_path = models.CharField(max_length=512, blank=True)
    ner_confidence   = models.FloatField(null=True, blank=True)
    topic_tags       = models.JSONField(default=list)    # ["Leadership", "ML"]
    nirf_countable   = models.BooleanField(default=False)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ecosystem_achievement"
        ordering = ["-date", "-created_at"]

    def __str__(self) -> str:
        return f"{self.title} — {self.profile}"


# ── Interaction ───────────────────────────────────────────────────────────────

class Interaction(models.Model):
    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(
        "accounts.Profile", 
        on_delete=models.CASCADE, 
        related_name="interactions_initiated"
    )
    target = models.ForeignKey(
        "accounts.Profile", 
        on_delete=models.CASCADE, 
        related_name="interactions_received"
    )
    type           = models.CharField(
                         max_length=30,
                         choices=InteractionType.choices,
                     )
    outcome        = models.CharField(
                         max_length=20,
                         choices=InteractionOutcome.choices,
                         default=InteractionOutcome.PENDING,
                     )
    duration_hours = models.FloatField(null=True, blank=True)
    startup        = models.ForeignKey(
                         "ecosystem.Startup",
                         on_delete=models.SET_NULL,
                         null=True,
                         blank=True,
                         related_name="interactions",
                     )
    success_label  = models.BooleanField(null=True, blank=True)   # telemetry: written on "Connect" click
    notes          = models.TextField(blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ecosystem_interaction"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.actor} → {self.target} [{self.type} / {self.outcome}]"

