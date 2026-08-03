# accounts/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProfileDetailView, ProfileViewSet

router = DefaultRouter()
router.register(r'profiles', ProfileViewSet, basename='profile') # Ensure 'profiles' plural

urlpatterns = [
    path('', include(router.urls)),
    path('profile/<uuid:pk>/', ProfileDetailView.as_view(), name='profile-detail'),
]