"""
tests/test_vectorized_generator.py
Campus Innovation & Engagement Intelligence Hub — Vectorized Generator Tests
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data.generation.vectorized_generator import (
    REQUIRED_KEYS,
    generate_slow_records,
    generate_vectorized_records,
)


class TestVectorizedGenerator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.small   = generate_vectorized_records(200,  seed=42)
        cls.large   = generate_vectorized_records(10_500, seed=7)
        cls.slow_sm = generate_slow_records(200, seed=42)

    # ── Row count ──────────────────────────────────────────────────────────────

    def test_row_count_small(self):
        self.assertEqual(len(self.small), 200)

    def test_row_count_large(self):
        self.assertEqual(len(self.large), 10_500)

    def test_slow_row_count(self):
        self.assertEqual(len(self.slow_sm), 200)

    # ── Required keys ──────────────────────────────────────────────────────────

    def test_required_keys_present_vectorized(self):
        missing = set(REQUIRED_KEYS) - set(self.small[0].keys())
        self.assertEqual(missing, set(), f"Missing keys: {missing}")

    def test_required_keys_present_slow(self):
        missing = set(REQUIRED_KEYS) - set(self.slow_sm[0].keys())
        self.assertEqual(missing, set(), f"Missing keys: {missing}")

    def test_score_keys_present(self):
        r = self.small[0]
        self.assertIn("success_score", r)
        self.assertIn("risk_score",    r)

    # ── TRL / MRL bounds ──────────────────────────────────────────────────────

    def test_trl_in_bounds(self):
        for r in self.small:
            self.assertGreaterEqual(r["technology_readiness_level"], 1)
            self.assertLessEqual(r["technology_readiness_level"],    9)

    def test_mrl_in_bounds(self):
        for r in self.small:
            self.assertGreaterEqual(r["market_readiness_level"], 1)
            self.assertLessEqual(r["market_readiness_level"],    9)

    # ── trl_mrl_gap ───────────────────────────────────────────────────────────

    def test_trl_mrl_gap_correct(self):
        for r in self.small:
            expected = r["technology_readiness_level"] - r["market_readiness_level"]
            self.assertEqual(r["trl_mrl_gap"], expected)

    # ── mentorship_hours ──────────────────────────────────────────────────────

    def test_mentorship_hours_nonnegative(self):
        for r in self.small:
            self.assertGreaterEqual(r["mentorship_hours"], 0.0)

    # ── competitions ──────────────────────────────────────────────────────────

    def test_competitions_won_leq_participated(self):
        for r in self.small:
            self.assertLessEqual(r["competitions_won"], r["competitions_participated"])

    def test_competitions_participated_nonnegative(self):
        for r in self.small:
            self.assertGreaterEqual(r["competitions_participated"], 0)

    def test_competitions_won_nonnegative(self):
        for r in self.small:
            self.assertGreaterEqual(r["competitions_won"], 0)

    # ── Portfolio scale ───────────────────────────────────────────────────────

    def test_portfolio_scale_bounds(self):
        for r in self.small:
            s = r["portfolio_achievement_scale_1_to_10"]
            self.assertGreaterEqual(s, 1)
            self.assertLessEqual(s,   10)

    # ── Binary labels ─────────────────────────────────────────────────────────

    def test_success_label_binary(self):
        for r in self.small:
            self.assertIn(r["success_prediction_label"], (0, 1))

    def test_at_risk_label_binary(self):
        for r in self.small:
            self.assertIn(r["at_risk_label"], (0, 1))

    # ── Large-scale test ──────────────────────────────────────────────────────

    def test_large_scale_row_count_and_keys(self):
        self.assertEqual(len(self.large), 10_500)
        missing = set(REQUIRED_KEYS) - set(self.large[0].keys())
        self.assertEqual(missing, set())

    def test_large_scale_no_invalid_labels(self):
        for r in self.large:
            self.assertIn(r["success_prediction_label"], (0, 1))
            self.assertIn(r["at_risk_label"],            (0, 1))

    # ── Determinism ───────────────────────────────────────────────────────────

    def test_deterministic_same_seed(self):
        a = generate_vectorized_records(50, seed=99)
        b = generate_vectorized_records(50, seed=99)
        self.assertEqual(a, b)

    def test_different_seeds_differ(self):
        a = generate_vectorized_records(50, seed=1)
        b = generate_vectorized_records(50, seed=2)
        self.assertNotEqual(a, b)


if __name__ == "__main__":
    unittest.main()