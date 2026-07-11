"""
tests/test_deduplication.py
Campus Innovation & Engagement Intelligence Hub — Deduplication Tests
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data.text.deduplication import (
    deduplicate_records,
    find_near_duplicates,
    normalize_text,
    text_similarity,
)


# ── Test helpers ──────────────────────────────────────────────────────────────

def _rec(rid: int, text: str) -> dict:
    return {"record_id": rid, "text": text}


class TestNormalizeText(unittest.TestCase):

    def test_lowercases(self):
        self.assertEqual(normalize_text("Hello World"), "hello world")

    def test_strips_punctuation(self):
        result = normalize_text("Hello, World! This is a test.")
        self.assertNotIn(",", result)
        self.assertNotIn("!", result)
        self.assertNotIn(".", result)

    def test_collapses_whitespace(self):
        result = normalize_text("  too   many    spaces  ")
        self.assertEqual(result, "too many spaces")

    def test_empty_string(self):
        self.assertEqual(normalize_text(""), "")

    def test_mixed(self):
        result = normalize_text("  Clinics!   Reduce??  Patient   No-Shows.  ")
        self.assertNotIn("!", result)
        self.assertEqual(result, result.strip())
        self.assertNotIn("  ", result)


class TestTextSimilarity(unittest.TestCase):

    def test_identical_is_one(self):
        self.assertAlmostEqual(text_similarity("hello world", "hello world"), 1.0)

    def test_empty_both_is_one(self):
        self.assertAlmostEqual(text_similarity("", ""), 1.0)

    def test_one_empty_is_zero(self):
        self.assertAlmostEqual(text_similarity("hello", ""), 0.0)

    def test_completely_different_is_low(self):
        sim = text_similarity("alpha beta gamma", "xyz uvw rst")
        self.assertLess(sim, 0.30)

    def test_near_identical_is_high(self):
        a = "clinics reduce patient no show rates"
        b = "clinics reduces patient no show rates"   # one word changed
        sim = text_similarity(a, b)
        self.assertGreater(sim, 0.85)

    def test_output_in_range(self):
        for a, b in [("foo", "bar"), ("abc", "abc"), ("a", "b")]:
            sim = text_similarity(a, b)
            self.assertGreaterEqual(sim, 0.0)
            self.assertLessEqual(sim,   1.0)


class TestDeduplicateRecords(unittest.TestCase):

    def test_exact_duplicates_removed(self):
        records = [_rec(1, "same text here"), _rec(2, "same text here"), _rec(3, "different one")]
        result  = deduplicate_records(records, "text", 0.92)
        texts   = [r["text"] for r in result]
        self.assertEqual(texts.count("same text here"), 1)
        self.assertIn("different one", texts)

    def test_near_duplicates_removed(self):
        records = [
            _rec(1, "clinics can reduce patient no show rates with reminders"),
            _rec(2, "clinics can reduce patient no-show rates with reminders"),  # tiny diff
            _rec(3, "completely unrelated sentence about quantum computing"),
        ]
        result = deduplicate_records(records, "text", 0.92)
        self.assertEqual(len(result), 2)

    def test_distinct_rows_preserved(self):
        records = [
            _rec(1, "smallholder farmers receive a fraction of consumer prices"),
            _rec(2, "gig workers have no access to micro insurance products"),
            _rec(3, "first generation learners cannot afford quality coaching"),
        ]
        result = deduplicate_records(records, "text", 0.92)
        self.assertEqual(len(result), 3)

    def test_original_not_mutated(self):
        records  = [_rec(1, "text one"), _rec(2, "text one")]
        original = [r.copy() for r in records]
        deduplicate_records(records, "text", 0.92)
        self.assertEqual(records, original)

    def test_first_occurrence_preserved(self):
        records = [_rec(1, "alpha beta gamma"), _rec(2, "alpha beta gamma"), _rec(3, "alpha beta gamma")]
        result  = deduplicate_records(records, "text", 0.92)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["record_id"], 1)

    def test_empty_input(self):
        self.assertEqual(deduplicate_records([], "text"), [])

    def test_single_record(self):
        self.assertEqual(len(deduplicate_records([_rec(1, "only one")], "text")), 1)

    def test_output_is_new_list(self):
        records = [_rec(1, "unique text")]
        result  = deduplicate_records(records, "text")
        result[0]["record_id"] = 999
        self.assertEqual(records[0]["record_id"], 1)   # original unchanged


class TestFindNearDuplicates(unittest.TestCase):

    def test_returns_list_of_tuples(self):
        records = [_rec(1, "same text"), _rec(2, "same text"), _rec(3, "other")]
        pairs   = find_near_duplicates(records, "text", 0.92)
        self.assertIsInstance(pairs, list)
        for item in pairs:
            self.assertEqual(len(item), 3)

    def test_detects_exact_duplicate_pair(self):
        records = [_rec(1, "identical phrase"), _rec(2, "identical phrase")]
        pairs   = find_near_duplicates(records, "text", 0.92)
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0][0], 0)
        self.assertEqual(pairs[0][1], 1)
        self.assertAlmostEqual(pairs[0][2], 1.0)

    def test_no_duplicates_returns_empty(self):
        records = [
            _rec(1, "entirely different sentence about health"),
            _rec(2, "completely unrelated topic about finance"),
        ]
        pairs = find_near_duplicates(records, "text", 0.92)
        self.assertEqual(pairs, [])

    def test_similarity_score_in_range(self):
        records = [_rec(1, "reduce patient wait times"), _rec(2, "reduce patient wait time")]
        pairs   = find_near_duplicates(records, "text", 0.70)
        for _, _, sim in pairs:
            self.assertGreaterEqual(sim, 0.0)
            self.assertLessEqual(sim,   1.0)


if __name__ == "__main__":
    unittest.main()