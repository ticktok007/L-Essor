from django.urls import path
from .views import EcosystemGraphView

urlpatterns = [
    path('ecosystem/', EcosystemGraphView.as_view(), name='graph-ecosystem'),
]