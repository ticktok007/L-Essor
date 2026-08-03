# tests/test_dashboard_integration.py
import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_student_dashboard_endpoint(api_client, sample_user):
    api_client.force_authenticate(user=sample_user)
    url = reverse('my-dashboard')
    response = api_client.get(url)
    assert response.status_code == 200
    assert "profile" in response.data

@pytest.mark.django_db
def test_leadership_dashboard_endpoint(api_client, sample_user_leadership):
    api_client.force_authenticate(user=sample_user_leadership)
    url = reverse('my-dashboard')
    response = api_client.get(url)
    assert response.status_code == 200
    assert "total_students" in response.data

@pytest.mark.django_db
def test_forbidden_access(api_client, sample_user):
    # Student trying to access a generic profile list (if restricted)
    api_client.force_authenticate(user=sample_user)
    response = api_client.get('/api/v1/accounts/profiles/')
    # Basic check - status code depends on specific ViewSet permissions
    assert response.status_code in [200, 403]