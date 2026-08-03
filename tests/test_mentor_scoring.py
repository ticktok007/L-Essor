# tests/test_mentor_scoring.py
import pytest
from accounts.models import User, Profile
from ecosystem.models import Mentor
from matching.mentor_scoring import score_mentor_match

@pytest.mark.django_db
class TestMentorScoring:
    def setup_method(self):
        # ── 1. Setup Mentee (Student) ──
        self.u_stu = User.objects.create_user(
            email="s@t.com", password="p", role="student", full_name="Student"
        )
        self.p_stu, _ = Profile.objects.get_or_create(user=self.u_stu)
        self.p_stu.interests = ["python", "ai", "web"]
        
        # Student Vector: Focus on the first half of the dimensions
        self.p_stu.skills_embedding = [1.0] * 192 + [0.0] * 192
        self.p_stu.save()

        # ── 2. Setup Mentor 1 (High content overlap, Bad Vector) ──
        self.u_m1 = User.objects.create_user(
            email="m1@t.com", password="p", role="mentor", full_name="Mentor Good Content"
        )
        self.p_m1, _ = Profile.objects.get_or_create(user=self.u_m1)
        # Mentor 1 Vector: Points in the opposite direction (second half)
        self.p_m1.skills_embedding = [0.0] * 192 + [1.0] * 192
        self.p_m1.save()
        
        self.m1 = Mentor.objects.create(
            user=self.u_m1, expertise_areas=["python", "ai"], is_active=True
        )

        # ── 3. Setup Mentor 2 (Zero content overlap, Perfect Vector) ──
        self.u_m2 = User.objects.create_user(
            email="m2@t.com", password="p", role="mentor", full_name="Mentor Good Vector"
        )
        self.p_m2, _ = Profile.objects.get_or_create(user=self.u_m2)
        # Mentor 2 Vector: Points in the exact same direction as student
        self.p_m2.skills_embedding = [1.0] * 192 + [0.0] * 192
        self.p_m2.save()
        
        self.m2 = Mentor.objects.create(
            user=self.u_m2, expertise_areas=["marketing"], is_active=True
        )

    def test_content_overlap_logic(self):
        res = score_mentor_match(self.m1, self.p_stu, alpha=1.0)
        assert res["content_score"] > 66.0
        assert "python" in res["matched_terms"]

    def test_alpha_weighting_shift(self):
        # Scenario A: High alpha (0.9) -> Content is King
        # M1 (66% content) should beat M2 (0% content)
        score1 = score_mentor_match(self.m1, self.p_stu, alpha=0.9)
        score2 = score_mentor_match(self.m2, self.p_stu, alpha=0.9)
        assert score1["final_match_score"] > score2["final_match_score"]

        # Scenario B: Low alpha (0.1) -> Vector is King
        # M2 (100% similarity) should beat M1 (0% similarity)
        score1_v = score_mentor_match(self.m1, self.p_stu, alpha=0.1)
        score2_v = score_mentor_match(self.m2, self.p_stu, alpha=0.1)
        assert score2_v["final_match_score"] > score1_v["final_match_score"]

    def test_scoring_handles_missing_embeddings(self):
        self.p_m2.skills_embedding = None
        self.p_m2.save()
        res = score_mentor_match(self.m2, self.p_stu, alpha=0.5)
        assert res["embedding_score"] == 0.0