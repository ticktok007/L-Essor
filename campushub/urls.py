# campushub/urls.py
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # OpenAPI Schema & Swagger UI
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    # API Endpoints
    path("api/v1/auth/", include("accounts.api.auth_urls")),
    path("api/v1/accounts/", include("accounts.urls")),
    path("api/v1/ecosystem/", include("ecosystem.urls")),
    path("api/v1/dashboard/", include("dashboard.urls")),
    path("api/v1/match/", include("matching.urls")),
    path("api/v1/predict/", include("analytics.urls")),
    path("api/v1/graph/", include("graph.urls")),
    path("api/v1/portfolio/", include("portfolio.urls")),
]