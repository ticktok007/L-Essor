"""
tests/test_hybrid_text_generator.py
Campus Innovation & Engagement Intelligence Hub — Hybrid Text Generator Tests
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data.text.hybrid_text_generator import (
    compute_text_diversity_stats,
    generate_investor_records,
    generate_mentor_records,
    generate_startup_records,
)

STARTUP_REQUIRED_KEYS  = {"record_id", "entity_type", "sector", "stage",
                           "problem_area", "target_user", "value_proposition",
                           "technology_tags", "pitch_summary"}
INVESTOR_REQUIRED_KEYS = {"record_id", "entity_type", "sector_focus",
                           "preferred_stage", "check_size_band",
                           "interest_themes", "support_style", "mandate_text"}
MENTOR_REQUIRED_KEYS   = INVESTOR_REQUIRED_KEYS   # same schema


class TestGenerateStartupRecords(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.records = generate_startup_records(60, seed=42)

    def test_row_count(self):
        self.assertEqual(len(self.records), 60)

    def test_required_keys(self):
        for r in self.records:
            missing = STARTUP_REQUIRED_KEYS - set(r.keys())
            self.assertEqual(missing, set(), f"Missing: {missing}")

    def test_entity_type(self):
        for r in self.records:
            self.assertEqual(r["entity_type"], "startup")

    def test_pitch_summary_non_empty(self):
        for r in self.records:
            self.assertIsInstance(r["pitch_summary"], str)
            self.assertGreater(len(r["pitch_summary"].strip()), 0)

    def test_technology_tags_length(self):
        for r in self.records:
            tags = r["technology_tags"]
            self.assertIsInstance(tags, list)
            self.assertGreaterEqual(len(tags), 2)
            self.assertLessEqual(len(tags),    4)

    def test_deterministic_same_seed(self):
        a = generate_startup_records(20, seed=7)
        b = generate_startup_records(20, seed=7)
        self.assertEqual(a, b)

    def test_different_seeds_differ(self):
        a = generate_startup_records(20, seed=1)
        b = generate_startup_records(20, seed=2)
        self.assertNotEqual(a, b)


class TestGenerateInvestorRecords(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.records = generate_investor_records(40, seed=42)

    def test_row_count(self):
        self.assertEqual(len(self.records), 40)

    def test_required_keys(self):
        for r in self.records:
            missing = INVESTOR_REQUIRED_KEYS - set(r.keys())
            self.assertEqual(missing, set())

    def test_entity_type(self):
        for r in self.records:
            self.assertEqual(r["entity_type"], "investor")

    def test_mandate_text_non_empty(self):
        for r in self.records:
            self.assertGreater(len(r["mandate_text"].strip()), 0)

    def test_interest_themes_is_list(self):
        for r in self.records:
            self.assertIsInstance(r["interest_themes"], list)


class TestGenerateMentorRecords(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.records = generate_mentor_records(40, seed=42)

    def test_row_count(self):
        self.assertEqual(len(self.records), 40)

    def test_entity_type(self):
        for r in self.records:
            self.assertEqual(r["entity_type"], "mentor")

    def test_mandate_text_non_empty(self):
        for r in self.records:
            self.assertGreater(len(r["mandate_text"].strip()), 0)

    def test_check_size_is_advisory(self):
        for r in self.records:
            self.assertEqual(r["check_size_band"], "advisory only")


class TestDiversityStats(unittest.TestCase):

    def test_returns_expected_keys(self):
        records = generate_startup_records(30, seed=1)
        stats   = compute_text_diversity_stats(records, "pitch_summary")
        for key in ("record_count", "unique_text_count", "unique_text_ratio",
                    "avg_token_count", "top_repeated_phrases"):
            self.assertIn(key, stats)

    def test_record_count_matches(self):
        records = generate_startup_records(25, seed=5)
        stats   = compute_text_diversity_stats(records, "pitch_summary")
        self.assertEqual(stats["record_count"], 25)

    def test_unique_ratio_above_zero(self):
        records = generate_startup_records(30, seed=3)
        stats   = compute_text_diversity_stats(records, "pitch_summary")
        self.assertGreater(stats["unique_text_ratio"], 0.0)

    def test_unique_ratio_meaningful_variety(self):
        # With 6 sectors × 6 frames we expect high variety at n=36
        records = generate_startup_records(36, seed=10)
        stats   = compute_text_diversity_stats(records, "pitch_summary")
        # At least 60% unique texts — generous lower bound for deterministic generation
        self.assertGreater(stats["unique_text_ratio"], 0.60)

    def test_avg_token_count_positive(self):
        records = generate_startup_records(10, seed=2)
        stats   = compute_text_diversity_stats(records, "pitch_summary")
        self.assertGreater(stats["avg_token_count"], 0)

    def test_mandate_diversity_investors(self):
        records = generate_investor_records(24, seed=9)
        stats   = compute_text_diversity_stats(records, "mandate_text")
        self.assertGreater(stats["unique_text_ratio"], 0.60)


if __name__ == "__main__":
    unittest.main()