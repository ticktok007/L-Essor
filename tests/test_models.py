# tests/test_models.py
import pytest
from accounts.models import User, Profile

@pytest.mark.django_db
def test_user_creation():
    user = User.objects.create(email="test@test.com", role="student")
    assert str(user) == " <test@test.com> [student]"
    assert user.role == "student"

@pytest.mark.django_db
def test_profile_link(sample_user):
    profile = Profile.objects.create(user=sample_user, department="CS")
    assert profile.user.email == "student@test.com"
    assert str(profile) == "Profile(Test Student)"

@pytest.mark.django_db
def test_startup_creation(sample_startup):
    assert sample_startup.startup_name == "Innovate Corp"
    assert sample_startup.founder.role == "student"

@pytest.mark.django_db
def test_achievement_logic(sample_achievement):
    assert not sample_achievement.verified
    assert sample_achievement.category == "competition"