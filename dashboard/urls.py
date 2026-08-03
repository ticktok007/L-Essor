# dashboard/urls.py
from django.urls import path
from .views import MyDashboardView

urlpatterns = [
    path("my/", MyDashboardView.as_view(), name="my-dashboard"),
]