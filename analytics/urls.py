from django.urls import path
from .views import StartupSuccessPredictionView

urlpatterns = [
    path('startup-success/', StartupSuccessPredictionView.as_view(), name='predict-success'),
]