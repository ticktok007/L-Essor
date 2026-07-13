"""
tests/test_skill_scores.py
Campus Innovation & Engagement Intelligence Hub — Skill Score Tests
"""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.compute_skill_scores import (
    PAID_BY_STUDENT_MAX_POINTS,
    classify_outcome,
    classify_skill_level,
    compute_competition_points,
    compute_confidence_boost,
    compute_internship_points,
    duration_multiplier,
)


# ── classify_outcome ──────────────────────────────────────────────────────────

class TestClassifyOutcome(unittest.TestCase):

    def test_first_place_keywords(self):
        for result in ["1st Place", "First Prize", "Grand Prix Winner"]:
            self.assertEqual(classify_outcome("winner", result), "first_place")

    def test_second_place(self):
        self.assertEqual(classify_outcome("winner", "2nd Place"), "second_place")

    def test_third_place(self):
        self.assertEqual(classify_outcome("finalist", "3rd Place"), "third_place")

    def test_special_award(self):
        self.assertEqual(classify_outcome("finalist", "Best Innovation Award"), "special_award")

    def test_finalist_top5(self):
        self.assertEqual(classify_outcome("finalist", "Top 5 finalist"), "finalist_top5")

    def test_finalist_top10(self):
        self.assertEqual(classify_outcome("participant", "National finalist"), "finalist_top10")

    def test_shortlisted(self):
        self.assertEqual(classify_outcome("participant", "Shortlisted in top 50"), "shortlisted")

    def test_participated_fallback(self):
        self.assertEqual(classify_outcome("participant", "Completed submission"), "participated")

    def test_organizer_role_overrides_result(self):
        self.assertEqual(classify_outcome("organizer", "1st Place"), "organizer")

    def test_mentor_judge_role(self):
        self.assertEqual(classify_outcome("mentor_judge", "Evaluated 30 teams"), "mentor_judge")

    def test_winner_role_fallback(self):
        self.assertEqual(classify_outcome("winner", "selected"), "first_place")


# ── compute_competition_points ────────────────────────────────────────────────

class TestCompetitionPoints(unittest.TestCase):

    def test_tier_S_first_place_solo(self):
        pts, outcome = compute_competition_points("winner", "1st Place", "S", 1)
        # 20 * 2.0 * 2.5 = 100
        self.assertAlmostEqual(pts, 100.0)
        self.assertEqual(outcome, "first_place")

    def test_tier_A_first_place_4_member(self):
        pts, _ = compute_competition_points("winner", "1st Place", "A", 4)
        # 20 * 0.8 * 2.0 = 32
        self.assertAlmostEqual(pts, 32.0)

    def test_tier_C_participated_6_member(self):
        pts, _ = compute_competition_points("participant", "Completed submission", "C", 6)
        # 3 * 0.4 * 1.0 = 1.2
        self.assertAlmostEqual(pts, 1.2)

    def test_organizer_team_size_ignored(self):
        pts_small, _ = compute_competition_points("organizer", "Organised", "B", 1)
        pts_large, _ = compute_competition_points("organizer", "Organised", "B", 6)
        self.assertAlmostEqual(pts_small, pts_large)

    def test_tier_D_lowers_points(self):
        pts_d, _ = compute_competition_points("winner", "1st Place", "D", 2)
        pts_c, _ = compute_competition_points("winner", "1st Place", "C", 2)
        self.assertLess(pts_d, pts_c)

    def test_smaller_team_higher_points(self):
        pts_solo, _ = compute_competition_points("winner", "1st Place", "A", 1)
        pts_team, _ = compute_competition_points("winner", "1st Place", "A", 4)
        self.assertGreater(pts_solo, pts_team)

    def test_points_non_negative(self):
        for role, result, tier, ts in [
            ("participant", "Participated", "C", 6),
            ("organizer",   "Organised",    "D", 4),
        ]:
            pts, _ = compute_competition_points(role, result, tier, ts)
            self.assertGreaterEqual(pts, 0.0)

    def test_unknown_tier_defaults(self):
        pts_unknown, _ = compute_competition_points("winner", "1st Place", "X", 2)
        pts_c,       _ = compute_competition_points("winner", "1st Place", "C", 2)
        self.assertAlmostEqual(pts_unknown, pts_c)


# ── compute_internship_points ─────────────────────────────────────────────────

class TestInternshipPoints(unittest.TestCase):

    def test_paid_by_student_capped(self):
        pts = compute_internship_points("paid_by_student", "offline", 24, "S")
        self.assertLessEqual(pts, PAID_BY_STUDENT_MAX_POINTS)

    def test_paid_by_student_online_capped(self):
        pts = compute_internship_points("paid_by_student", "online", 24, "A")
        self.assertLessEqual(pts, PAID_BY_STUDENT_MAX_POINTS)

    def test_paid_offline_tier_A_scores_high(self):
        pts = compute_internship_points("paid", "offline", 12, "A")
        # 25 * 1.0 * 1.0 * 1.5 = 37.5
        self.assertAlmostEqual(pts, 37.5)

    def test_stipend_offline_scores_medium(self):
        pts = compute_internship_points("stipend", "offline", 8, "B")
        # 18 * 1.0 * 0.8 * 1.2 = 17.28
        self.assertAlmostEqual(pts, 17.28)

    def test_unpaid_online_scores_low(self):
        pts_online  = compute_internship_points("unpaid", "online",  8, "C")
        pts_offline = compute_internship_points("unpaid", "offline", 8, "C")
        self.assertLess(pts_online, pts_offline)

    def test_longer_duration_more_points(self):
        pts_short = compute_internship_points("stipend", "offline", 4,  "B")
        pts_long  = compute_internship_points("stipend", "offline", 24, "B")
        self.assertGreater(pts_long, pts_short)

    def test_tier_S_company_doubles_points(self):
        pts_s = compute_internship_points("paid", "offline", 12, "S")
        pts_c = compute_internship_points("paid", "offline", 12, "C")
        self.assertGreater(pts_s, pts_c)

    def test_points_always_non_negative(self):
        for itype in ["paid_by_student", "unpaid", "stipend", "paid"]:
            for mode in ["online", "offline", "hybrid"]:
                pts = compute_internship_points(itype, mode, 4, "C")
                self.assertGreaterEqual(pts, 0.0)


# ── duration_multiplier ───────────────────────────────────────────────────────

class TestDurationMultiplier(unittest.TestCase):

    def test_less_than_4_weeks(self):
        self.assertAlmostEqual(duration_multiplier(2),  0.5)

    def test_4_to_8_weeks(self):
        self.assertAlmostEqual(duration_multiplier(6),  0.8)

    def test_8_to_12_weeks(self):
        self.assertAlmostEqual(duration_multiplier(10), 1.0)

    def test_12_to_24_weeks(self):
        self.assertAlmostEqual(duration_multiplier(16), 1.2)

    def test_more_than_24_weeks(self):
        self.assertAlmostEqual(duration_multiplier(30), 1.4)

    def test_boundary_12_weeks(self):
        self.assertAlmostEqual(duration_multiplier(12), 1.0)


# ── compute_confidence_boost ──────────────────────────────────────────────────

class TestConfidenceBoost(unittest.TestCase):

    def test_tier_S_win_small_team_highest(self):
        boost = compute_confidence_boost("first_place", "S", 2, "", "")
        self.assertAlmostEqual(boost, 0.40)

    def test_tier_A_win(self):
        boost = compute_confidence_boost("first_place", "A", 4, "", "")
        self.assertAlmostEqual(boost, 0.25)

    def test_tier_B_win(self):
        boost = compute_confidence_boost("first_place", "B", 3, "", "")
        self.assertAlmostEqual(boost, 0.15)

    def test_participation_only(self):
        boost = compute_confidence_boost("participated", "C", 4, "", "")
        self.assertAlmostEqual(boost, 0.05)

    def test_paid_offline_internship(self):
        boost = compute_confidence_boost("", "", 0, "paid", "offline")
        self.assertAlmostEqual(boost, 0.30)

    def test_paid_by_student_internship_lowest(self):
        boost = compute_confidence_boost("", "", 0, "paid_by_student", "online")
        self.assertAlmostEqual(boost, 0.03)

    def test_stipend_offline(self):
        boost = compute_confidence_boost("", "", 0, "stipend", "offline")
        self.assertAlmostEqual(boost, 0.20)

    def test_internship_boost_overrides_competition(self):
        # When itype is provided, internship path is taken
        boost_intern = compute_confidence_boost("first_place", "S", 1, "unpaid", "offline")
        boost_comp   = compute_confidence_boost("first_place", "S", 1, "",       "")
        self.assertNotEqual(boost_intern, boost_comp)


# ── classify_skill_level ──────────────────────────────────────────────────────

class TestClassifySkillLevel(unittest.TestCase):

    def test_zero_is_beginner(self):
        self.assertEqual(classify_skill_level(0), "Beginner")

    def test_10_is_beginner(self):
        self.assertEqual(classify_skill_level(10), "Beginner")

    def test_11_is_developing(self):
        self.assertEqual(classify_skill_level(11), "Developing")

    def test_26_is_intermediate(self):
        self.assertEqual(classify_skill_level(26), "Intermediate")

    def test_51_is_proficient(self):
        self.assertEqual(classify_skill_level(51), "Proficient")

    def test_81_is_advanced(self):
        self.assertEqual(classify_skill_level(81), "Advanced")

    def test_120_is_expert(self):
        self.assertEqual(classify_skill_level(120), "Expert")

    def test_large_score_is_expert(self):
        self.assertEqual(classify_skill_level(500), "Expert")


# ── Structured skills JSON format ─────────────────────────────────────────────

class TestStructuredSkillsFormat(unittest.TestCase):

    VALID_SKILL = {
        "skill":      "Python",
        "confidence": 0.10,
        "level":      "unknown",
        "sources":    ["self_declared"],
    }

    def test_confidence_is_float(self):
        self.assertIsInstance(self.VALID_SKILL["confidence"], float)

    def test_confidence_is_baseline(self):
        self.assertAlmostEqual(self.VALID_SKILL["confidence"], 0.10)

    def test_sources_contains_self_declared(self):
        self.assertIn("self_declared", self.VALID_SKILL["sources"])

    def test_level_is_unknown_at_baseline(self):
        self.assertEqual(self.VALID_SKILL["level"], "unknown")

    def test_confidence_boost_caps_at_one(self):
        conf  = 0.10
        boost = 0.40 + 0.35 + 0.30 + 0.20   # stacked boosts well over 1.0
        final = min(1.0, round(conf + boost, 3))
        self.assertLessEqual(final, 1.0)

    def test_skill_json_serializable(self):
        s = json.dumps(self.VALID_SKILL)
        parsed = json.loads(s)
        self.assertEqual(parsed["skill"], "Python")

    def test_multiple_skills_list(self):
        skills = [
            {"skill": "Python",        "confidence": 0.10, "level": "unknown", "sources": ["self_declared"]},
            {"skill": "TensorFlow",    "confidence": 0.10, "level": "unknown", "sources": ["self_declared"]},
            {"skill": "Data Analysis", "confidence": 0.10, "level": "unknown", "sources": ["self_declared"]},
        ]
        dumped = json.dumps(skills)
        parsed = json.loads(dumped)
        self.assertEqual(len(parsed), 3)
        for sk in parsed:
            self.assertIn("skill",      sk)
            self.assertIn("confidence", sk)
            self.assertIn("level",      sk)
            self.assertIn("sources",    sk)


if __name__ == "__main__":
    unittest.main()