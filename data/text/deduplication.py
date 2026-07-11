"""
deduplication.py
Campus Innovation & Engagement Intelligence Hub — Phase 1, Day 13

Near-duplicate detection and removal for synthetic text records.
Standard library only.
"""

import difflib
import re
from typing import Any


# ── Text normalisation ────────────────────────────────────────────────────────

def normalize_text(text: str) -> str:
    """
    Lowercase, collapse whitespace, strip punctuation noise.
    Keeps alphanumeric tokens and single spaces.
    """
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)   # remove punctuation
    text = re.sub(r"\s+", " ", text)        # collapse whitespace
    return text.strip()


# ── Similarity ────────────────────────────────────────────────────────────────

def text_similarity(a: str, b: str) -> float:
    """
    Returns a similarity score in [0.0, 1.0] using difflib SequenceMatcher.
    Inputs are normalized internally.
    """
    na = normalize_text(a)
    nb = normalize_text(b)
    if not na and not nb:
        return 1.0
    if not na or not nb:
        return 0.0
    return difflib.SequenceMatcher(None, na, nb).ratio()


# ── Near-duplicate detection ───────────────────────────────────────────────────

def find_near_duplicates(
    records: list[dict],
    text_key: str,
    similarity_threshold: float = 0.92,
) -> list[tuple[int, int, float]]:
    """
    Returns a list of (index_i, index_j, similarity_score) for all pairs
    where normalized text similarity >= similarity_threshold.
    Runs in O(n²) — suitable for moderate n.
    """
    results: list[tuple[int, int, float]] = []
    texts = [normalize_text(r.get(text_key, "")) for r in records]
    n     = len(texts)
    for i in range(n):
        for j in range(i + 1, n):
            sim = difflib.SequenceMatcher(None, texts[i], texts[j]).ratio()
            if sim >= similarity_threshold:
                results.append((i, j, round(sim, 4)))
    return results


# ── Deduplication ─────────────────────────────────────────────────────────────

def deduplicate_records(
    records: list[dict],
    text_key: str,
    similarity_threshold: float = 0.92,
) -> list[dict]:
    """
    Remove near-identical records based on normalized text similarity.
    - Preserves the FIRST occurrence.
    - Removes later records with similarity >= similarity_threshold to any kept record.
    - Does NOT mutate the input list.
    - Maintains stable order.

    Uses a greedy O(n²) approach: for each candidate, check against all
    already-kept records.
    """
    if not records:
        return []

    kept_texts: list[str] = []
    kept_records: list[dict[str, Any]] = []

    for record in records:
        candidate = normalize_text(record.get(text_key, ""))
        is_dup    = False
        for kept in kept_texts:
            sim = difflib.SequenceMatcher(None, candidate, kept).ratio()
            if sim >= similarity_threshold:
                is_dup = True
                break
        if not is_dup:
            kept_texts.append(candidate)
            kept_records.append(dict(record))   # shallow copy — no mutation of input

    return kept_records