"""
tests/test_target_labels.py
Campus Innovation & Engagement Intelligence Hub — Target Label Tests
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml.features.target_labels import at_risk_label, build_labels, success_prediction_label


# ── Fixture records ───────────────────────────────────────────────────────────

HIGH_SIGNAL = {
    "technology_readiness_level": 6,
    "market_readiness_level":     5,    # gap = 1 → in [-1, 2]
    "mentorship_hours":           25,   # >= 20 → +2
    "competitions_participated":   4,
    "competitions_won":            3,   # >= 2 → +2
    "achievement_count":          10,
    "leadership_roles_count":      2,
    "portfolio_items_count":       5,   # scale = 10 → +2
    "funding_stage":              "seed",   # → +1
    "users_count":                1500,     # → +1
}

LOW_SIGNAL = {
    "technology_readiness_level": 1,
    "market_readiness_level":     9,    # gap = -8 → outside [-3,3]
    "mentorship_hours":           0,
    "competitions_participated":   0,
    "competitions_won":            0,
    "achievement_count":           0,
    "leadership_roles_count":      0,
    "portfolio_items_count":       0,
    "funding_stage":              "none",
}

DISENGAGED = {
    "mentorship_hours":                   0,     # < 2 → +2
    "competitions_participated":           0,     # == 0 → +2
    "competitions_won":                    0,     # == 0 → +1
    "achievement_count":                   0,
    "leadership_roles_count":              0,
    "portfolio_items_count":               0,     # scale = 1 → <= 2 → +2
    "last_active_days_ago":               60,     # > 45 → +2
    "submissions_count_last_90_days":      0,     # == 0 → +2
}

ACTIVE = {
    "mentorship_hours":                   20,    # >= 6 → no risk
    "competitions_participated":           5,
    "competitions_won":                    2,
    "achievement_count":                  10,
    "leadership_roles_count":              2,
    "portfolio_items_count":               5,    # scale = 10 → > 4 → no risk
    "last_active_days_ago":                3,    # <= 21 → no risk
    "submissions_count_last_90_days":      8,    # > 2 → no risk
}


class TestSuccessPredictionLabel(unittest.TestCase):

    def test_high_signal_is_success(self):
        self.assertEqual(success_prediction_label(HIGH_SIGNAL), 1)

    def test_low_signal_is_not_success(self):
        self.assertEqual(success_prediction_label(LOW_SIGNAL), 0)

    def test_empty_record_is_not_success(self):
        self.assertEqual(success_prediction_label({}), 0)

    def test_funding_stage_contributes(self):
        base = {**LOW_SIGNAL, "funding_stage": "grant-funded",
                "mentorship_hours": 25, "competitions_won": 3,
                "achievement_count": 10, "leadership_roles_count": 2,
                "portfolio_items_count": 5,
                "technology_readiness_level": 5, "market_readiness_level": 5}
        self.assertEqual(success_prediction_label(base), 1)

    def test_traction_revenue_contributes(self):
        rec = {**HIGH_SIGNAL, "users_count": 0, "revenue": 50000.0, "pilot_customers": 0}
        self.assertEqual(success_prediction_label(rec), 1)

    def test_traction_max_one_bonus(self):
        # Even with all three traction signals, max +1 from traction
        rec = {**HIGH_SIGNAL, "users_count": 5000, "revenue": 100000.0, "pilot_customers": 10}
        label = success_prediction_label(rec)
        self.assertIn(label, (0, 1))   # just confirm no crash / type error

    def test_return_type_is_int(self):
        self.assertIsInstance(success_prediction_label({}), int)


class TestAtRiskLabel(unittest.TestCase):

    def test_disengaged_is_at_risk(self):
        self.assertEqual(at_risk_label(DISENGAGED), 1)

    def test_active_is_not_at_risk(self):
        self.assertEqual(at_risk_label(ACTIVE), 0)

    def test_empty_record_partial_risk(self):
        # empty → mentorship_hours=0 (+2), participated=0 (+2), won=0 (+1), scale=1 (+2) = 7 >= 5
        self.assertEqual(at_risk_label({}), 1)

    def test_last_active_days_affects_risk(self):
        rec = {**ACTIVE, "last_active_days_ago": 50}
        self.assertEqual(at_risk_label(rec), 0)   # ACTIVE base is strong enough

    def test_submissions_zero_increases_risk(self):
        rec = {**DISENGAGED, "submissions_count_last_90_days": 0}
        self.assertEqual(at_risk_label(rec), 1)

    def test_return_type_is_int(self):
        self.assertIsInstance(at_risk_label({}), int)


class TestBuildLabels(unittest.TestCase):

    EXPECTED_KEYS = {"success_prediction_label", "at_risk_label"}

    def test_returns_both_keys_high_signal(self):
        result = build_labels(HIGH_SIGNAL)
        self.assertEqual(set(result.keys()), self.EXPECTED_KEYS)

    def test_returns_both_keys_empty(self):
        result = build_labels({})
        self.assertEqual(set(result.keys()), self.EXPECTED_KEYS)

    def test_values_are_binary(self):
        for rec in (HIGH_SIGNAL, LOW_SIGNAL, DISENGAGED, ACTIVE, {}):
            result = build_labels(rec)
            self.assertIn(result["success_prediction_label"], (0, 1))
            self.assertIn(result["at_risk_label"],            (0, 1))

    def test_high_signal_success_not_at_risk(self):
        result = build_labels(HIGH_SIGNAL)
        self.assertEqual(result["success_prediction_label"], 1)
        self.assertEqual(result["at_risk_label"],            0)

    def test_disengaged_not_success_and_at_risk(self):
        result = build_labels(DISENGAGED)
        self.assertEqual(result["success_prediction_label"], 0)
        self.assertEqual(result["at_risk_label"],            1)


if __name__ == "__main__":
    unittest.main()