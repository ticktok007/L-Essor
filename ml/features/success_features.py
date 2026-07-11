"""
success_features.py
Campus Innovation & Engagement Intelligence Hub
Phase 1 — Week 2: Feature Engineering for Predictive Analytics Pipeline
"""

from typing import Any

# ── Safe coercion helpers ─────────────────────────────────────────────────────

def _int(val: Any, default: int = 0) -> int:
    try:
        return int(val)
    except (TypeError, ValueError):
        return default

def _float(val: Any, default: float = 0.0) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return default

def _clamp(val: int, lo: int = 1, hi: int = 9) -> int:
    return max(lo, min(hi, val))

# ── A. TRL–MRL Gap ───────────────────────────────────────────────────────────

def trl_mrl_gap(record: dict) -> int:
    """
    Returns technology_readiness_level - market_readiness_level.
    Both are clamped to [1, 9]; missing values default to 1.
    Positive  => tech maturity ahead of market readiness.
    Zero      => balanced.
    Negative  => market readiness ahead of tech maturity.
    """
    trl = _clamp(_int(record.get("technology_readiness_level"), 1))
    mrl = _clamp(_int(record.get("market_readiness_level"),     1))
    return trl - mrl

# ── B. Mentorship Hours ───────────────────────────────────────────────────────

def mentorship_hours(record: dict) -> float:
    """
    Prefer explicit 'mentorship_hours' field.
    Otherwise derive: mentor_sessions_count * avg_session_duration_hours.
    Result is non-negative, rounded to 2 decimals.
    """
    explicit = record.get("mentorship_hours")
    if explicit is not None:
        return round(max(0.0, _float(explicit)), 2)
    sessions  = max(0, _int(record.get("mentor_sessions_count"), 0))
    avg_dur   = max(0.0, _float(record.get("avg_session_duration_hours"), 0.0))
    return round(sessions * avg_dur, 2)

# ── C. Competitions Participated / Won ────────────────────────────────────────

def competitions_participated_and_won(record: dict) -> tuple[int, int]:
    """
    Returns (competitions_participated, competitions_won).
    Prefers explicit integer fields; falls back to 'competitions' list.
    Enforces: won <= participated, both >= 0.
    """
    explicit_p = record.get("competitions_participated")
    explicit_w = record.get("competitions_won")

    if explicit_p is not None and explicit_w is not None:
        p = max(0, _int(explicit_p))
        w = max(0, _int(explicit_w))
        if w > p:               # safe correction
            p = w
        return p, w

    comps = record.get("competitions", [])
    if not isinstance(comps, list):
        comps = []

    participated = 0
    won          = 0
    for c in comps:
        if not isinstance(c, dict):
            continue
        # participated defaults to True when field absent but entry exists
        if c.get("participated", True):
            participated += 1
        if c.get("won", False):
            won += 1

    # safe correction
    if won > participated:
        participated = won
    return participated, won

# ── D. Portfolio Achievement Scale 1–10 ──────────────────────────────────────

def _tier(val: int, breakpoints: list[tuple[int, int]]) -> int:
    """Return score for val using ascending (threshold, score) pairs."""
    result = 0
    for threshold, score in breakpoints:
        if val >= threshold:
            result = score
    return result

_ACH_TIERS: list[tuple[int, int]] = [(1, 1), (3, 2), (6, 3), (9, 4)]
_WIN_TIERS: list[tuple[int, int]] = [(1, 1), (2, 2)]
_LEAD_TIERS: list[tuple[int, int]] = [(1, 1), (2, 2)]
_PORT_TIERS: list[tuple[int, int]] = [(2, 1), (4, 2)]

def portfolio_achievement_scale(record: dict) -> int:
    """
    Bounded 1–10 portfolio impact score.
      achievement_count      → up to 4 pts
      wins                   → up to 2 pts
      leadership_roles_count → up to 2 pts
      portfolio_items_count  → up to 2 pts
    Returns integer in [1, 10].
    """
    _, won = competitions_participated_and_won(record)

    ach   = max(0, _int(record.get("achievement_count"),      0))
    lead  = max(0, _int(record.get("leadership_roles_count"), 0))
    port  = max(0, _int(record.get("portfolio_items_count"),  0))

    raw = (
        _tier(ach,  _ACH_TIERS)
        + _tier(won,  _WIN_TIERS)
        + _tier(lead, _LEAD_TIERS)
        + _tier(port, _PORT_TIERS)
    )
    return max(1, min(10, raw if raw > 0 else 1))

# ── Convenience builder ───────────────────────────────────────────────────────

def build_success_features(record: dict) -> dict:
    """
    Compute and return all engineered features for a single record dict.
    Safe to call on partial records; missing fields fall back to defaults.
    """
    p, w = competitions_participated_and_won(record)
    return {
        "trl_mrl_gap":                       trl_mrl_gap(record),
        "mentorship_hours":                   mentorship_hours(record),
        "competitions_participated":          p,
        "competitions_won":                   w,
        "portfolio_achievement_scale_1_to_10": portfolio_achievement_scale(record),
    }