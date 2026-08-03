from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiTypes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from drf_spectacular.utils import extend_schema

class SuccessPredictionSerializer(serializers.Serializer):
    success_probability = serializers.FloatField()
    status = serializers.CharField()

class SuccessResponseSerializer(serializers.Serializer):
    success_probability = serializers.FloatField()

class PredictionRequestSerializer(serializers.Serializer):
    startup_id = serializers.UUIDField(help_text="UUID of the startup to analyze")

class PredictionResponseSerializer(serializers.Serializer):
    success_probability = serializers.FloatField()

class StartupSuccessPredictionView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SuccessPredictionSerializer


    @extend_schema(
        tags=["Predictive Analytics"],
        summary="Predict startup success probability",
        responses={200: PredictionResponseSerializer},
        examples=[OpenApiExample("Prediction", value={"success_probability": 0.78})]
    )
    def post(self, request):
        return Response({"success_probability": 0.78})