# tests/test_recommendations.py
import pytest
from django.urls import reverse
from accounts.models import User
from ecosystem.models import Startup, Investor, Mentor

@pytest.mark.django_db
class TestRecommendations:
    def setup_method(self):
        # 1. Create the primary user and a startup
        self.user = User.objects.create_user(email="rec@test.com", password="p", role="student")
        self.vec = [0.1] * 384
        self.startup = Startup.objects.create(
            founder=self.user, startup_name="S1", pitch_embedding=self.vec
        )
        
        # 2. Create 6 unique investors (Each needs its own User)
        # This tests the 'Top-5 default' logic
        for i in range(6):
            unique_user = User.objects.create_user(
                email=f"vc_{i}@test.com", 
                password="p", 
                role="investor"
            )
            Investor.objects.create(
                user=unique_user, 
                firm_name=f"VC{i}", 
                mandate_text=f"Mandate {i}", 
                mandate_embedding=self.vec
            )

    def test_investor_recommendation_default_limit(self, api_client):
        api_client.force_authenticate(user=self.user)
        url = reverse('recommend-investor')
        response = api_client.get(f"{url}?startup_id={self.startup.id}")
        
        assert response.status_code == 200
        # Should return top 5 even though 6 exist in DB
        assert len(response.data) == 5 
        assert "similarity_score" in response.data[0]
        assert "snippet" in response.data[0]

    def test_investor_recommendation_custom_k(self, api_client):
        api_client.force_authenticate(user=self.user)
        url = reverse('recommend-investor')
        response = api_client.get(f"{url}?startup_id={self.startup.id}&top_k=2")
        
        assert response.status_code == 200
        assert len(response.data) == 2

    def test_recommendation_missing_embedding(self, api_client):
        s2 = Startup.objects.create(founder=self.user, startup_name="NoVec")
        api_client.force_authenticate(user=self.user)
        url = reverse('recommend-investor')
        response = api_client.get(f"{url}?startup_id={s2.id}")
        
        assert response.status_code == 400

    def test_recommendation_404(self, api_client):
        api_client.force_authenticate(user=self.user)
        url = reverse('recommend-investor')
        import uuid
        response = api_client.get(f"{url}?startup_id={uuid.uuid4()}")
        assert response.status_code == 404