# matching/serializers.py
from rest_framework import serializers

class InvestorMatchRequest(serializers.Serializer):
    startup_id = serializers.UUIDField()
    limit = serializers.IntegerField(default=5, min_value=1, max_value=20)

class InvestorMatchResult(serializers.Serializer):
    id = serializers.UUIDField()
    firm_name = serializers.CharField()
    mandate_text = serializers.CharField()
    compatibility_score = serializers.FloatField()
    sector_focus = serializers.ListField(child=serializers.CharField(), source='sectors')
    stage_preference = serializers.ListField(child=serializers.CharField(), source='stages')

class InvestorMatchResponse(serializers.Serializer):
    startup_id = serializers.UUIDField()
    matches = InvestorMatchResult(many=True)
    total_investors = serializers.IntegerField()