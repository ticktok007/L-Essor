# matching/mentor_features.py
from typing import List, Set

def normalize_terms(values: List[str]) -> Set[str]:
    """Normalizes a list of strings into a set of clean lowercase terms."""
    if not values:
        return set()
    return {str(v).lower().strip() for v in values if v}

def matched_terms(a: List[str], b: List[str]) -> List[str]:
    """Returns the intersection of two term lists."""
    set_a = normalize_terms(a)
    set_b = normalize_terms(b)
    return sorted(list(set_a.intersection(set_b)))

def overlap_score(a: List[str], b: List[str]) -> float:
    """
    Computes a simple overlap score (0.0 - 1.0).
    Normalized by the size of the first set (mentee interests).
    """
    set_a = normalize_terms(a)
    set_b = normalize_terms(b)
    if not set_a:
        return 0.0
    intersection = set_a.intersection(set_b)
    return round(len(intersection) / len(set_a), 4)