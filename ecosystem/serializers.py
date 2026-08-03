# ecosystem/serializers.py
from rest_framework import serializers
from .models import Startup, Investor, Mentor, Competition, Achievement, Interaction

class StartupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Startup
        fields = [
            'id', 'founder', 'startup_name', 'tagline', 'pitch_summary', 
            'sector', 'stage', 'trl', 'website_url', 'deck_url', 
            'team_size', 'is_active', 'created_at', 'updated_at'
        ]
        # Ensure heavy vectors are not in the documentation/API response
        extra_kwargs = {
            'pitch_embedding': {'write_only': True}
        }

class InvestorSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = Investor
        fields = [
            'id', 'user', 'full_name', 'firm_name', 'designation', 
            'mandate', 'sectors', 'stages', 'check_size_min', 
            'check_size_max', 'portfolio_count', 'website_url', 
            'linkedin_url', 'is_active'
        ]
        # Ensure heavy vectors are not in the documentation/API response
        extra_kwargs = {
            'mandate_embedding': {'write_only': True}
        }

class MentorSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = Mentor
        fields = '__all__'

class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = '__all__'

class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = '__all__'

class InteractionSummarySerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source='actor.user.full_name', read_only=True)
    target_name = serializers.CharField(source='target.user.full_name', read_only=True)

    class Meta:
        model = Interaction
        fields = ['id', 'actor', 'actor_name', 'target', 'target_name', 'type', 'outcome', 'created_at']