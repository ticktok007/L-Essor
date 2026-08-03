# tests/test_peer_matching.py
import pytest
from django.urls import reverse
from rest_framework import status
from accounts.models import User, Profile

@pytest.mark.django_db
class TestPeerMatching:
    def setup_method(self):
        # Create a pool of 8 students with varied skills
        self.students = []
        skill_sets = [
            ("Python|Django", "React"),
            ("Python|FastAPI", "UI/UX"),
            ("React|Tailwind", "Python"),
            ("Figma|UI/UX", "Django"),
            ("Java|Spring", "Docker"),
            ("Docker|Kubernetes", "Java"),
            ("Solidity|Blockchain", "React"),
            ("React|Web3", "Solidity")
        ]
        
        for i, (pos, seek) in enumerate(skill_sets):
            user = User.objects.create_user(
                email=f"stu{i}@test.com", password="password123", role="student", full_name=f"Student {i}"
            )
            # FIX: Ensure profile exists
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.skills = pos.split('|') # Matches your model field 'skills'
            profile.bio = f"I want to learn {seek}"
            profile.save()
            self.students.append(user)

    def test_peer_match_returns_suggested_groupings(self, api_client):
        api_client.force_authenticate(user=self.students[0])
        url = reverse('match-peers')
        response = api_client.get(f"{url}?team_size=2")
        
        assert response.status_code == status.HTTP_200_OK
        assert "suggested_teams" in response.data
        assert response.data['total_students'] == 8
        assert len(response.data['suggested_teams']) >= 2

    def test_peer_match_metadata(self, api_client):
        api_client.force_authenticate(user=self.students[0])
        url = reverse('match-peers')
        response = api_client.get(url)
        
        team = response.data['suggested_teams'][0]
        assert "balance_score" in team
        assert "member_ids" in team
        assert "top_shared_skills" in team

    def test_peer_match_empty_skills_safety(self, api_client):
        u = User.objects.create_user(email="empty@test.com", password="password123", role="student")
        # Ensure profile exists for empty user
        Profile.objects.get_or_create(user=u)
        
        api_client.force_authenticate(user=u)
        url = reverse('match-peers')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK