from drf_spectacular.utils import extend_schema, OpenApiTypes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class EcosystemGraphView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Graph Intelligence"],
        summary="Export ecosystem graph",
        responses={200: OpenApiTypes.OBJECT},
    )
    def get(self, request):
        return Response({"nodes": [], "edges": []})