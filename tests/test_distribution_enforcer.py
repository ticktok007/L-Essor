"""
tests/test_distribution_enforcer.py
Campus Innovation & Engagement Intelligence Hub — Distribution Enforcer Tests
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data.generation.distribution_enforcer import (
    SUCCESS_MAX_RATIO,
    SUCCESS_MIN_RATIO,
    RISK_MAX_RATIO,
    RISK_MIN_RATIO,
    enforce_all_targets,
    enforce_binary_label_distribution,
    summarize_label_distribution,
)
from data.generation.vectorized_generator import generate_vectorized_records


def _make_records(n: int, pos_ratio: float, label: str, score_key: str) -> list[dict]:
    """Build minimal test records with controlled positive ratio."""
    records = []
    n_pos = int(n * pos_ratio)
    for i in range(n):
        lbl = 1 if i < n_pos else 0
        records.append({
            "record_id":                i + 1,
            label:                      lbl,
            score_key:                  i,   # monotone score proxy
            "success_prediction_label": lbl if label == "success_prediction_label" else 0,
            "at_risk_label":            lbl if label == "at_risk_label" else 0,
            "success_score":            i if score_key == "success_score" else 0,
            "risk_score":               i if score_key == "risk_score"    else 0,
        })
    return records


class TestEnforceBinaryLabel(unittest.TestCase):

    # ── Low positive ratio raised into bounds ──────────────────────────────

    def test_low_ratio_raised_to_min(self):
        records = _make_records(1000, pos_ratio=0.05,
                                label="success_prediction_label", score_key="success_score")
        result  = enforce_binary_label_distribution(
            records, "success_prediction_label", 0.35, 0.65
        )
        ratio = sum(1 for r in result if r["success_prediction_label"] == 1) / len(result)
        self.assertGreaterEqual(ratio, 0.35)
        self.assertLessEqual(ratio,    0.65)

    # ── High positive ratio lowered into bounds ────────────────────────────

    def test_high_ratio_lowered_to_max(self):
        records = _make_records(1000, pos_ratio=0.90,
                                label="success_prediction_label", score_key="success_score")
        result  = enforce_binary_label_distribution(
            records, "success_prediction_label", 0.35, 0.65
        )
        ratio = sum(1 for r in result if r["success_prediction_label"] == 1) / len(result)
        self.assertGreaterEqual(ratio, 0.35)
        self.assertLessEqual(ratio,    0.65)

    # ── Already in bounds — no unnecessary flipping ────────────────────────

    def test_in_bounds_unchanged_labels(self):
        records = _make_records(1000, pos_ratio=0.50,
                                label="success_prediction_label", score_key="success_score")
        result  = enforce_binary_label_distribution(
            records, "success_prediction_label", 0.35, 0.65
        )
        ratio = sum(1 for r in result if r["success_prediction_label"] == 1) / len(result)
        self.assertGreaterEqual(ratio, 0.35)
        self.assertLessEqual(ratio,    0.65)

    # ── Input not mutated ──────────────────────────────────────────────────

    def test_original_not_mutated(self):
        records  = _make_records(200, pos_ratio=0.05,
                                 label="success_prediction_label", score_key="success_score")
        original = [r["success_prediction_label"] for r in records]
        enforce_binary_label_distribution(
            records, "success_prediction_label", 0.35, 0.65
        )
        self.assertEqual([r["success_prediction_label"] for r in records], original)

    # ── Output length unchanged ────────────────────────────────────────────

    def test_output_length_unchanged(self):
        records = _make_records(500, pos_ratio=0.10,
                                label="success_prediction_label", score_key="success_score")
        result  = enforce_binary_label_distribution(
            records, "success_prediction_label", 0.35, 0.65
        )
        self.assertEqual(len(result), 500)

    # ── Empty input safe ──────────────────────────────────────────────────

    def test_empty_input(self):
        result = enforce_binary_label_distribution([], "success_prediction_label", 0.35, 0.65)
        self.assertEqual(result, [])

    # ── at_risk_label enforcement ─────────────────────────────────────────

    def test_at_risk_low_ratio_raised(self):
        records = _make_records(1000, pos_ratio=0.05,
                                label="at_risk_label", score_key="risk_score")
        result  = enforce_binary_label_distribution(
            records, "at_risk_label", 0.20, 0.50
        )
        ratio = sum(1 for r in result if r["at_risk_label"] == 1) / len(result)
        self.assertGreaterEqual(ratio, 0.20)
        self.assertLessEqual(ratio,    0.50)

    def test_at_risk_high_ratio_lowered(self):
        records = _make_records(1000, pos_ratio=0.90,
                                label="at_risk_label", score_key="risk_score")
        result  = enforce_binary_label_distribution(
            records, "at_risk_label", 0.20, 0.50
        )
        ratio = sum(1 for r in result if r["at_risk_label"] == 1) / len(result)
        self.assertGreaterEqual(ratio, 0.20)
        self.assertLessEqual(ratio,    0.50)


class TestEnforceAllTargets(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Use real generator records for integration-style tests
        cls.raw     = generate_vectorized_records(2000, seed=42)
        cls.enforced = enforce_all_targets(cls.raw)

    def test_both_labels_in_required_range(self):
        n = len(self.enforced)
        s_ratio = sum(1 for r in self.enforced if r["success_prediction_label"] == 1) / n
        r_ratio = sum(1 for r in self.enforced if r["at_risk_label"] == 1) / n
        self.assertGreaterEqual(s_ratio, SUCCESS_MIN_RATIO)
        self.assertLessEqual(s_ratio,    SUCCESS_MAX_RATIO)
        self.assertGreaterEqual(r_ratio, RISK_MIN_RATIO)
        self.assertLessEqual(r_ratio,    RISK_MAX_RATIO)

    def test_original_not_mutated(self):
        raw_s = [r["success_prediction_label"] for r in self.raw]
        enforce_all_targets(self.raw)
        self.assertEqual([r["success_prediction_label"] for r in self.raw], raw_s)

    def test_output_length_unchanged(self):
        self.assertEqual(len(self.enforced), len(self.raw))

    def test_feature_columns_unchanged(self):
        for orig, enf in zip(self.raw, self.enforced):
            self.assertEqual(orig["trl_mrl_gap"],      enf["trl_mrl_gap"])
            self.assertEqual(orig["mentorship_hours"],  enf["mentorship_hours"])
            self.assertEqual(orig["achievement_count"], enf["achievement_count"])

    def test_summarize_returns_expected_keys(self):
        s = summarize_label_distribution(self.enforced)
        for key in ("total_records", "success_positive_ratio", "at_risk_positive_ratio"):
            self.assertIn(key, s)

    def test_summarize_ratios_in_range(self):
        s = summarize_label_distribution(self.enforced)
        self.assertGreaterEqual(s["success_positive_ratio"], SUCCESS_MIN_RATIO)
        self.assertLessEqual(s["success_positive_ratio"],    SUCCESS_MAX_RATIO)
        self.assertGreaterEqual(s["at_risk_positive_ratio"], RISK_MIN_RATIO)
        self.assertLessEqual(s["at_risk_positive_ratio"],    RISK_MAX_RATIO)


if __name__ == "__main__":
    unittest.main()