"""
distribution_enforcer.py
Campus Innovation & Engagement Intelligence Hub — Phase 1, Day 12

Enforces target-label class balance on a list[dict] of ML records.
Does NOT mutate the original list. Returns a new list.
"""

from typing import Any

# ── Required bounds ───────────────────────────────────────────────────────────

SUCCESS_MIN_RATIO = 0.35
SUCCESS_MAX_RATIO = 0.65
RISK_MIN_RATIO    = 0.20
RISK_MAX_RATIO    = 0.50

_SCORE_PROXY = {
    "success_prediction_label": "success_score",
    "at_risk_label":            "risk_score",
}


# ── Core enforcement ──────────────────────────────────────────────────────────

def enforce_binary_label_distribution(
    records: list[dict],
    label_key: str,
    min_positive_ratio: float,
    max_positive_ratio: float,
) -> list[dict]:
    """
    Adjust binary labels so the positive ratio falls within
    [min_positive_ratio, max_positive_ratio] (inclusive).

    Strategy:
    - If ratio too low  → flip the highest-score negatives to positive first.
    - If ratio too high → flip the lowest-score positives to negative first.

    Does not mutate original records. Returns a new list with shallow-copied dicts.
    Only the label field is changed; all feature columns are preserved.
    """
    if not records:
        return []

    score_key = _SCORE_PROXY.get(label_key, "success_score")
    n = len(records)

    # Shallow-copy each dict so originals are never mutated
    result: list[dict[str, Any]] = [dict(r) for r in records]

    def _current_ratio() -> float:
        return sum(1 for r in result if r[label_key] == 1) / n

    ratio = _current_ratio()

    if ratio < min_positive_ratio:
        # Need more positives — flip negatives with highest score first
        negatives = sorted(
            [i for i, r in enumerate(result) if r[label_key] == 0],
            key=lambda i: result[i].get(score_key, 0),
            reverse=True,   # highest score first
        )
        target_pos = int(min_positive_ratio * n)
        current_pos = sum(1 for r in result if r[label_key] == 1)
        for idx in negatives:
            if current_pos >= target_pos:
                break
            result[idx][label_key] = 1
            current_pos += 1

    elif ratio > max_positive_ratio:
        # Need fewer positives — flip positives with lowest score first
        positives = sorted(
            [i for i, r in enumerate(result) if r[label_key] == 1],
            key=lambda i: result[i].get(score_key, 0),
            reverse=False,  # lowest score first
        )
        target_pos = int(max_positive_ratio * n)
        current_pos = sum(1 for r in result if r[label_key] == 1)
        for idx in positives:
            if current_pos <= target_pos:
                break
            result[idx][label_key] = 0
            current_pos -= 1

    return result


def enforce_all_targets(records: list[dict]) -> list[dict]:
    """
    Apply required distribution bounds for both ML target labels.
    - success_prediction_label: [0.35, 0.65]
    - at_risk_label:            [0.20, 0.50]

    Returns a new list; does not mutate input.
    """
    result = enforce_binary_label_distribution(
        records,
        label_key="success_prediction_label",
        min_positive_ratio=SUCCESS_MIN_RATIO,
        max_positive_ratio=SUCCESS_MAX_RATIO,
    )
    result = enforce_binary_label_distribution(
        result,
        label_key="at_risk_label",
        min_positive_ratio=RISK_MIN_RATIO,
        max_positive_ratio=RISK_MAX_RATIO,
    )
    return result


def summarize_label_distribution(records: list[dict]) -> dict:
    """
    Returns counts and positive ratios for both target labels.
    """
    n = len(records)
    if n == 0:
        return {"total_records": 0}

    s_pos = sum(1 for r in records if r.get("success_prediction_label") == 1)
    r_pos = sum(1 for r in records if r.get("at_risk_label") == 1)

    return {
        "total_records":                n,
        "success_positive_count":       s_pos,
        "success_negative_count":       n - s_pos,
        "success_positive_ratio":       round(s_pos / n, 4),
        "at_risk_positive_count":       r_pos,
        "at_risk_negative_count":       n - r_pos,
        "at_risk_positive_ratio":       round(r_pos / n, 4),
    }