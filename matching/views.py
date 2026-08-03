# matching/views.py
from django.shortcuts import get_object_or_404
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from pgvector.django import CosineDistance

from accounts.models import Profile
from ecosystem.models import Startup, Investor, Mentor
from .serializers import InvestorMatchRequest
from .recommendations import get_knn_recommendations
from .peer_clustering import generate_peer_teams
from .mentor_scoring import rank_mentors_for_mentee

# ── 1. Match Views (POST/GET) ──

class InvestorMatchView(APIView):
    """Day 34: Direct semantic matching for a specific startup."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = InvestorMatchRequest(data=request.data)
        ser.is_valid(raise_exception=True)
        startup = get_object_or_404(Startup, id=ser.validated_data['startup_id'])
        
        if not startup.pitch_embedding:
            return Response({"detail": "no pitch embedding"}, status=400)
            
        limit = ser.validated_data['limit']
        if connection.vendor == 'postgresql':
            investors = Investor.objects.annotate(
                distance=CosineDistance('mandate_embedding', startup.pitch_embedding)
            ).order_by('distance')[:limit]
        else:
            investors = Investor.objects.all()[:limit]
            for inv in investors: inv.distance = 0.5
        
        matches = []
        for inv in investors:
            dist = max(0.0, min(1.0, float(getattr(inv, 'distance', 1.0))))
            matches.append({
                "id": inv.id,
                "firm_name": inv.firm_name,
                "mandate_text": inv.mandate_text,
                "compatibility_score": round((1.0 - dist) * 100, 2),
                "sectors": inv.sectors,
                "stages": inv.stages
            })
        return Response({"startup_id": startup.id, "matches": matches, "total_investors": Investor.objects.count()})

class PeerMatchView(APIView):
    """Week 9: K-Means clustering for peer groups."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        team_size = int(request.query_params.get('team_size', 4))
        queryset = Profile.objects.filter(user__role='student').select_related('user')
        students = []
        for p in queryset:
            students.append({
                "id": str(p.id),
                "full_name": p.user.full_name,
                "skills_possessed": "|".join(p.skills) if isinstance(p.skills, list) else "",
                "skills_seeking": p.bio or ""
            })
        if len(students) < 2:
            return Response({"detail": "Not enough students"}, status=400)
        teams = generate_peer_teams(students, team_size=team_size)
        return Response({"total_students": len(students), "suggested_teams": teams}, status=200)

class MentorMatchView(APIView):
    """Week 10: Blended content + embedding scoring for mentors."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        mentee_id = request.query_params.get('mentee_id')
        alpha = float(request.query_params.get('alpha', 0.6))
        mentee_profile = get_object_or_404(Profile, id=mentee_id) if mentee_id else get_object_or_404(Profile, user=request.user)
        mentors = list(Mentor.objects.filter(is_active=True).select_related('user', 'user__profile'))
        if not mentors:
            return Response([], status=200)
        ranked_matches = rank_mentors_for_mentee(mentee_profile, mentors, alpha)
        return Response({"mentee_id": mentee_profile.id, "matches": ranked_matches}, status=200)

# ── 2. Recommendation Views (GET) ──

class BaseRecommendView(APIView):
    """Week 7: KNN-style recommendation base."""
    permission_classes = [IsAuthenticated]
    model = None
    vector_field = ""

    def get(self, request):
        startup_id = request.query_params.get('startup_id')
        top_k = int(request.query_params.get('top_k', 5))
        if not startup_id:
            return Response({"detail": "startup_id is required"}, status=400)
        startup = get_object_or_404(Startup, id=startup_id)
        if not startup.pitch_embedding:
            return Response({"detail": "Startup has no embedding"}, status=400)
        recommendations = get_knn_recommendations(self.model, startup.pitch_embedding, self.vector_field, top_k)
        return Response(recommendations, status=200)

class InvestorRecommendView(BaseRecommendView):
    model = Investor
    vector_field = "mandate_embedding"

class MentorRecommendView(BaseRecommendView):
    model = Mentor
    vector_field = "mandate_embedding"