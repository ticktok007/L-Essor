# tests/conftest.py
import pytest
from rest_framework.test import APIClient
from accounts.models import User, Profile
from ecosystem.models import Startup, Achievement, Interaction

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def sample_user(db):
    return User.objects.create_user(
        email="student@test.com",
        password="password123",
        full_name="Test Student",
        role="student"
    )

@pytest.fixture
def sample_user_leadership(db):
    return User.objects.create_user(
        email="admin@test.com",
        password="password123",
        full_name="Test Admin",
        role="leadership"
    )

@pytest.fixture
def sample_profile(sample_user):
    profile, _ = Profile.objects.get_or_create(user=sample_user)
    return profile

@pytest.fixture
def sample_startup(sample_user):
    return Startup.objects.create(
        founder=sample_user,
        startup_name="Innovate Corp",
        sector="HealthTech",
        stage="mvp"
    )

@pytest.fixture
def sample_achievement(sample_profile):
    return Achievement.objects.create(
        profile=sample_profile,
        title="Hackathon Winner",
        category="competition"
    )