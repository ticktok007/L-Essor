# accounts/serializers.py
from rest_framework import serializers
from .models import Profile

class ProfileSummarySerializer(serializers.ModelSerializer):
    """Minimal representation for listings."""
    full_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'full_name', 'department', 'headline']

class ProfileSerializer(serializers.ModelSerializer):
    """Full representation for detail views and documentation."""
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Profile
        fields = [
            'id', 'full_name', 'email', 'department', 'graduation_year', 
            'bio', 'skills', 'interests', 'location', 
            'achievement_impact_score', 'grit_index', 'at_risk_flag'
        ]