# dashboard/serializers.py
from rest_framework import serializers
from accounts.models import Profile

class StudentOwnProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = Profile
        fields = [
            'id', 'full_name', 'department', 'graduation_year', 'bio', 
            'skills', 'achievement_impact_score', 'grit_index', 
            'at_risk_flag', 'profile_completion_pct'
        ]

class StudentDashboardSerializer(serializers.Serializer):
    profile = StudentOwnProfileSerializer()
    achievements_count = serializers.IntegerField()
    startups_count = serializers.IntegerField()
    recent_achievements = serializers.ListField(child=serializers.DictField())

class LeadershipDashboardSerializer(serializers.Serializer):
    total_profiles = serializers.IntegerField()
    total_students = serializers.IntegerField()
    total_startups = serializers.IntegerField()
    total_achievements = serializers.IntegerField()
    at_risk_students = serializers.IntegerField()
    department_counts = serializers.DictField()
    recent_startups = serializers.ListField(child=serializers.DictField())