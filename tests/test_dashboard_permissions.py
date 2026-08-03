# tests/test_dashboard_permissions.py
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from accounts.models import User, Profile

@pytest.mark.django_db
class TestDashboardPermissions:
    def setup_method(self):
        self.client = APIClient()
        # Create users with full_name on the User model
        self.student = User.objects.create(
            email="s@test.com", 
            role="student", 
            full_name="Student One"
        )
        self.other_student = User.objects.create(
            email="o@test.com", 
            role="student", 
            full_name="Student Two"
        )
        self.leadership = User.objects.create(
            email="l@test.com", 
            role="leadership", 
            full_name="Admin User"
        )
        
        # Profile usually created via signals, but ensuring they exist for tests
        # Removed full_name from here as it's not a Profile field
        Profile.objects.get_or_create(user=self.student)
        Profile.objects.get_or_create(user=self.other_student)

    def test_student_gets_own_dashboard(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get(reverse('my-dashboard'))
        assert response.status_code == 200
        assert "achievements_count" in response.data

    def test_leadership_gets_aggregate_dashboard(self):
        self.client.force_authenticate(user=self.leadership)
        response = self.client.get(reverse('my-dashboard'))
        assert response.status_code == 200
        assert "total_students" in response.data

    def test_student_cannot_access_other_profile(self):
        self.client.force_authenticate(user=self.student)
        # Using the Profile ID
        url = reverse('profile-detail', kwargs={'pk': self.other_student.profile.id})
        response = self.client.get(url)
        assert response.status_code == 403

    def test_student_can_access_own_profile(self):
        self.client.force_authenticate(user=self.student)
        url = reverse('profile-detail', kwargs={'pk': self.student.profile.id})
        response = self.client.get(url)
        assert response.status_code == 200