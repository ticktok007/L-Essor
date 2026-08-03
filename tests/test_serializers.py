# tests/test_serializers.py
import pytest
from dashboard.serializers import StudentOwnProfileSerializer, LeadershipDashboardSerializer

@pytest.mark.django_db
def test_student_profile_serializer(sample_profile):
    serializer = StudentOwnProfileSerializer(instance=sample_profile)
    data = serializer.data
    assert data['full_name'] == "Test Student"
    assert 'at_risk_flag' in data

def test_leadership_dashboard_serializer():
    data = {
        "total_profiles": 10,
        "total_students": 5,
        "total_startups": 2,
        "total_achievements": 20,
        "at_risk_students": 1,
        "department_counts": {"CS": 5},
        "recent_startups": []
    }
    serializer = LeadershipDashboardSerializer(data=data)
    assert serializer.is_valid()    