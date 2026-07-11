"""
tests/test_success_features.py
Campus Innovation & Engagement Intelligence Hub — Feature Engineering Tests
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml.features.success_features import (
    build_success_features,
    competitions_participated_and_won,
    mentorship_hours,
    portfolio_achievement_scale,
    trl_mrl_gap,
)


class TestTRLMRLGap(unittest.TestCase):

    def test_normal_gap(self):
        self.assertEqual(trl_mrl_gap({"technology_readiness_level": 7, "market_readiness_level": 4}), 3)

    def test_balanced(self):
        self.assertEqual(trl_mrl_gap({"technology_readiness_level": 5, "market_readiness_level": 5}), 0)

    def test_negative_gap(self):
        self.assertEqual(trl_mrl_gap({"technology_readiness_level": 2, "market_readiness_level": 6}), -4)

    def test_missing_defaults_to_one(self):
        self.assertEqual(trl_mrl_gap({}), 0)   # default 1 - 1 = 0

    def test_clamp_above_nine(self):
        self.assertEqual(trl_mrl_gap({"technology_readiness_level": 15, "market_readiness_level": 0}), 8)  # 9-1

    def test_clamp_below_one(self):
        self.assertEqual(trl_mrl_gap({"technology_readiness_level": -3, "market_readiness_level": -5}), 0)  # 1-1

    def test_string_inputs_coerced(self):
        self.assertEqual(trl_mrl_gap({"technology_readiness_level": "6", "market_readiness_level": "3"}), 3)

    def test_invalid_inputs_default(self):
        self.assertEqual(trl_mrl_gap({"technology_readiness_level": "abc", "market_readiness_level": None}), 0)


class TestMentorshipHours(unittest.TestCase):

    def test_explicit_field(self):
        self.assertEqual(mentorship_hours({"mentorship_hours": 12.5}), 12.5)

    def test_derived_from_sessions(self):
        self.assertEqual(mentorship_hours({"mentor_sessions_count": 4, "avg_session_duration_hours": 1.5}), 6.0)

    def test_explicit_takes_priority(self):
        rec = {"mentorship_hours": 10, "mentor_sessions_count": 4, "avg_session_duration_hours": 2}
        self.assertEqual(mentorship_hours(rec), 10.0)

    def test_never_negative(self):
        self.assertEqual(mentorship_hours({"mentorship_hours": -5}), 0.0)

    def test_missing_returns_zero(self):
        self.assertEqual(mentorship_hours({}), 0.0)

    def test_partial_derived_missing_avg(self):
        self.assertEqual(mentorship_hours({"mentor_sessions_count": 5}), 0.0)

    def test_rounding(self):
        self.assertEqual(mentorship_hours({"mentor_sessions_count": 3, "avg_session_duration_hours": 1.3333}), 4.0)


class TestCompetitionCounts(unittest.TestCase):

    def test_explicit_fields(self):
        rec = {"competitions_participated": 5, "competitions_won": 2}
        p, w = competitions_participated_and_won(rec)
        self.assertEqual(p, 5)
        self.assertEqual(w, 2)

    def test_safe_correction_won_exceeds_participated(self):
        rec = {"competitions_participated": 2, "competitions_won": 5}
        p, w = competitions_participated_and_won(rec)
        self.assertGreaterEqual(p, w)

    def test_list_based_derivation(self):
        rec = {"competitions": [
            {"participated": True, "won": True},
            {"participated": True, "won": False},
            {"participated": True, "won": False},
        ]}
        p, w = competitions_participated_and_won(rec)
        self.assertEqual(p, 3)
        self.assertEqual(w, 1)

    def test_empty_list(self):
        p, w = competitions_participated_and_won({"competitions": []})
        self.assertEqual(p, 0)
        self.assertEqual(w, 0)

    def test_list_defaults_participated_true(self):
        rec = {"competitions": [{"won": False}, {"won": True}]}
        p, w = competitions_participated_and_won(rec)
        self.assertEqual(p, 2)
        self.assertEqual(w, 1)

    def test_both_non_negative(self):
        rec = {"competitions_participated": -3, "competitions_won": -1}
        p, w = competitions_participated_and_won(rec)
        self.assertGreaterEqual(p, 0)
        self.assertGreaterEqual(w, 0)

    def test_no_field_no_list(self):
        p, w = competitions_participated_and_won({})
        self.assertEqual(p, 0)
        self.assertEqual(w, 0)


class TestPortfolioScale(unittest.TestCase):

    def test_lower_bound_empty_record(self):
        self.assertEqual(portfolio_achievement_scale({}), 1)

    def test_upper_bound_maxed_record(self):
        rec = {
            "achievement_count":      15,
            "competitions_won":        5,
            "leadership_roles_count":  3,
            "portfolio_items_count":   6,
        }
        self.assertEqual(portfolio_achievement_scale(rec), 10)

    def test_mid_range(self):
        rec = {
            "achievement_count":      4,
            "competitions_won":        1,
            "leadership_roles_count":  1,
            "portfolio_items_count":   2,
        }
        score = portfolio_achievement_scale(rec)
        self.assertGreaterEqual(score, 1)
        self.assertLessEqual(score, 10)

    def test_clamped_to_ten(self):
        rec = {
            "achievement_count":       100,
            "competitions_won":        100,
            "leadership_roles_count":  100,
            "portfolio_items_count":   100,
        }
        self.assertEqual(portfolio_achievement_scale(rec), 10)


class TestBuildSuccessFeatures(unittest.TestCase):

    EXPECTED_KEYS = {
        "trl_mrl_gap",
        "mentorship_hours",
        "competitions_participated",
        "competitions_won",
        "portfolio_achievement_scale_1_to_10",
    }

    def test_returns_all_keys_empty_record(self):
        result = build_success_features({})
        self.assertEqual(set(result.keys()), self.EXPECTED_KEYS)

    def test_returns_all_keys_full_record(self):
        rec = {
            "technology_readiness_level": 6,
            "market_readiness_level":     4,
            "mentorship_hours":           15,
            "competitions_participated":   4,
            "competitions_won":            2,
            "achievement_count":           7,
            "leadership_roles_count":      2,
            "portfolio_items_count":       4,
        }
        result = build_success_features(rec)
        self.assertEqual(set(result.keys()), self.EXPECTED_KEYS)

    def test_values_are_correct_types(self):
        result = build_success_features({})
        self.assertIsInstance(result["trl_mrl_gap"],                       int)
        self.assertIsInstance(result["mentorship_hours"],                   float)
        self.assertIsInstance(result["competitions_participated"],          int)
        self.assertIsInstance(result["competitions_won"],                   int)
        self.assertIsInstance(result["portfolio_achievement_scale_1_to_10"], int)


if __name__ == "__main__":
    unittest.main()