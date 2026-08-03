# matching/urls.py
from django.urls import path
from .views import (
    PeerMatchView, 
    InvestorRecommendView, 
    MentorRecommendView, 
    InvestorMatchView,
    MentorMatchView
)

urlpatterns = [
    # Match logic (Heuristic/Blended/Clustered)
    path("investor/match/", InvestorMatchView.as_view(), name="match-investor"),
    path("match/peers/", PeerMatchView.as_view(), name="match-peers"),
    path("match/mentor/", MentorMatchView.as_view(), name="match-mentor"),
    
    # Recommendation logic (Raw KNN)
    path("recommend/investor/", InvestorRecommendView.as_view(), name="recommend-investor"),
    path("recommend/mentor/", MentorRecommendView.as_view(), name="recommend-mentor"),
]