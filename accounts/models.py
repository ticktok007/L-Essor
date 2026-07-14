# Accounts models — Campus Innovation & Engagement Intelligence Hub
# Custom User model and Profile defined in Phase 2 (Django + DRF scaffold).
"""
accounts/models.py
Campus Innovation & Engagement Intelligence Hub — Phase 2
Custom User model (email-based auth) + Profile
"""

import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


# ── Role choices ──────────────────────────────────────────────────────────────

class UserRole(models.TextChoices):
    STUDENT   = "student",   "Student"
    ALUMNI    = "alumni",    "Alumni"
    INVESTOR  = "investor",  "Investor"
    MENTOR    = "mentor",    "Mentor"
    ADMIN     = "admin",     "Admin"


# ── Custom manager ────────────────────────────────────────────────────────────

class UserManager(BaseUserManager):

    def create_user(self, email: str, password: str = None, **extra_fields):
        if not email:
            raise ValueError("Email is required.")
        email = self.normalize_email(email)
        user  = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str, **extra_fields):
        extra_fields.setdefault("is_staff",    True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role",         UserRole.ADMIN)
        return self.create_user(email, password, **extra_fields)


# ── User ──────────────────────────────────────────────────────────────────────

class User(AbstractBaseUser, PermissionsMixin):
    id                = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email             = models.EmailField(unique=True)
    full_name         = models.CharField(max_length=150)
    role              = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.STUDENT)
    is_email_verified = models.BooleanField(default=False)
    is_active         = models.BooleanField(default=True)
    is_staff          = models.BooleanField(default=False)
    date_joined       = models.DateTimeField(auto_now_add=True)

    objects        = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        db_table = "auth_user"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self) -> str:
        return f"{self.full_name} <{self.email}> [{self.role}]"


# ── Profile ───────────────────────────────────────────────────────────────────

class Profile(models.Model):
    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user            = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    headline        = models.CharField(max_length=200, blank=True)
    bio             = models.TextField(blank=True)
    department      = models.CharField(max_length=120, blank=True)
    program         = models.CharField(max_length=120, blank=True)
    graduation_year = models.PositiveIntegerField(null=True, blank=True)
    skills          = models.JSONField(default=list)   # [{"skill": "Python", "confidence": 0.10, ...}]
    interests       = models.JSONField(default=list)
    linkedin_url    = models.URLField(blank=True)
    github_url      = models.URLField(blank=True)
    portfolio_url   = models.URLField(blank=True)
    location        = models.CharField(max_length=120, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounts_profile"

    def __str__(self) -> str:
        return f"Profile({self.user.full_name})"