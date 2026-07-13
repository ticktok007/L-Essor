"""
Root URL configuration — Campus Innovation & Engagement Intelligence Hub
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    # App routes wired in Phase 2 as DRF ViewSets are built
    # path("api/v1/accounts/",  include("accounts.urls")),
    # path("api/v1/ecosystem/", include("ecosystem.urls")),
    # path("api/v1/matching/",  include("matching.urls")),
    # path("api/v1/analytics/", include("analytics.urls")),
    # path("api/v1/graph/",     include("graph.urls")),
    # path("api/v1/portfolio/", include("portfolio.urls")),
]