# accounts/views.py
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from .models import Profile
from .serializers import ProfileSerializer, ProfileSummarySerializer
from .permissions import IsStudentSelf, IsLeadership

@extend_schema(tags=["Accounts"])
class ProfileViewSet(viewsets.ModelViewSet):
    """
    Standard ViewSet for Profile management.
    Used for listing and general administration.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Retrieve user profile",
        description="Fetch detailed profile information including skills and scores.",
        examples=[
            OpenApiExample(
                "Profile Response",
                value={
                    "id": "uuid-v4",
                    "full_name": "Sanjay",
                    "department": "Computer Science",
                    "graduation_year": 2026,
                    "skills": [{"skill": "Python", "confidence": 0.9}],
                    "achievement_impact_score": 85.5
                }
            )
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

@extend_schema(tags=["Accounts"])
class ProfileDetailView(generics.RetrieveAPIView):
    """
    Specific detail view used to enforce object-level privacy.
    Students can only access their own profile.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSummarySerializer
    permission_classes = [IsAuthenticated, IsStudentSelf | IsLeadership]

    def get_serializer_class(self):
    # Fix: Safely check for user and authentication
        user = getattr(self.request, 'user', None)
        if user and user.is_authenticated and getattr(user, 'role', None) == 'student':
            return ProfileSerializer
        return ProfileSummarySerializer

    @extend_schema(
        summary="Restricted Profile Detail",
        description="Access-controlled endpoint. Students are restricted to 'Self' only."
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)