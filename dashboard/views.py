# dashboard/views.py
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsStudentOrLeadership
from .services import build_student_dashboard, build_leadership_dashboard
from .serializers import StudentDashboardSerializer, LeadershipDashboardSerializer

class MyDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsStudentOrLeadership]
    @extend_schema(
        tags=["Dashboard"],
        summary="Role-based aggregate dashboard",
        description="Returns personal metrics for students or institutional aggregates for leadership.",
        responses={200: dict},
        examples=[
            OpenApiExample(
                "Student Dashboard",
                value={
                    "profile": {"full_name": "Sanjay"},
                    "achievements_count": 12,
                    "startups_count": 1
                }
            ),
            OpenApiExample(
                "Leadership Dashboard",
                value={
                    "total_students": 5000,
                    "active_startups": 42,
                    "total_funding_inr": 15000000
                }
            )
        ]
    )
    @extend_schema(tags=["Dashboard"], summary="My Dashboard")
    def get(self, request):
        user = request.user
        if user.role == 'student':
            data = build_student_dashboard(user)
            serializer = StudentDashboardSerializer(data)
            return Response(serializer.data)
        
        if user.role == 'leadership':
            data = build_leadership_dashboard()
            serializer = LeadershipDashboardSerializer(data)
            return Response(serializer.data)
        
        return Response({"detail": "Role not supported."}, status=403)