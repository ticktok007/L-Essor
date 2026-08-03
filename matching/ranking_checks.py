# matching/ranking_checks.py
from typing import List, Dict, Any

def assert_in_top_k(results: List[Dict[str, Any]], target_id: Any, k: int = 5):
    """Verifies that the target ID exists within the top K results."""
    top_ids = [str(r['id']) for r in results[:k]]
    assert str(target_id) in top_ids, f"ID {target_id} not found in top {k}. Found: {top_ids}"

def assert_not_in_top_k(results: List[Dict[str, Any]], target_id: Any, k: int = 5):
    """Verifies that the target ID is absent from the top K results."""
    top_ids = [str(r['id']) for r in results[:k]]
    assert str(target_id) not in top_ids, f"ID {target_id} incorrectly found in top {k}"

def assert_sorted_desc(results: List[Dict[str, Any]]):
    """Verifies that scores are strictly descending."""
    scores = [r['similarity_score'] for r in results]
    assert scores == sorted(scores, reverse=True), "Results are not sorted by score descending"

def assert_valid_scores(results: List[Dict[str, Any]]):
    """Ensures scores are within a realistic 0-100 range and are not NaN."""
    for r in results:
        score = r['similarity_score']
        assert 0 <= score <= 100, f"Invalid score found: {score}"