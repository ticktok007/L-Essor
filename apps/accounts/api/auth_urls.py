"""
apps/accounts/api/auth_urls.py
Campus Innovation & Engagement Intelligence Hub
JWT authentication routes.

Include in root urls.py:
    path("api/v1/auth/", include("apps.accounts.api.auth_urls")),
"""

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # POST  /api/v1/auth/token/          → obtain access + refresh tokens
    path("token/",         TokenObtainPairView.as_view(),  name="token_obtain"),
    # POST  /api/v1/auth/token/refresh/  → exchange refresh token for new access token
    path("token/refresh/", TokenRefreshView.as_view(),     name="token_refresh"),
]