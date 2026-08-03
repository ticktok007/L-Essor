"""
success_features.py
Campus Innovation & Engagement Intelligence Hub
Phase 1 — Week 2: Feature Engineering for Predictive Analytics Pipeline
"""

from typing import Any

# ── Safe coercion helpers ─────────────────────────────────────────────────────

def _int(val: Any, default: int = 0) -> int:
    try:
        if val is None:
            return default
        return int(val)
    except (TypeError, ValueError):
        return default

def _float(val: Any, default: float = 0.0) -> float:
    try:
        if val is None:
            return default
        return float(val)
    except (TypeError, ValueError):
        return default

def _clamp(val: int, lo: int = 1, hi: int = 9) -> int:
    return max(lo, min(hi, val))

# ── A. TRL–MRL Gap ───────────────────────────────────────────────────────────

def trl_mrl_gap(record: dict) -> int:
    """
    Returns technology_readiness_level - market_readiness_level.
    """
    trl = _clamp(_int(record.get("technology_readiness_level"), 1))
    mrl = _clamp(_int(record.get("market_readiness_level"),     1))
    return trl - mrl

# ── B. Mentorship Hours ───────────────────────────────────────────────────────

def mentorship_hours(record: dict) -> float:
    """
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
    Ensures: won <= participated, both >= 0.
    """
    p_field = record.get("competitions_participated")
    w_field = record.get("competitions_won")

    # If both fields are missing, try the list-based approach
    if p_field is None and w_field is None:
        comps = record.get("competitions", [])
        if not isinstance(comps, list):
            comps = []
        participated = 0
        won = 0
        for c in comps:
            if not isinstance(c, dict): continue
            if c.get("participated", True): participated += 1
            if c.get("won", False): won += 1
        return participated, won

    # Convert to integers, defaulting to 0
    p = _int(p_field, 0)
    w = _int(w_field, 0)

    # 1. Correct if won > participated
    if w > p:
        p = w
    
    # 2. FINAL CLAMP: Ensure both are at least 0 (Fixes the test failure)
    p = max(0, p)
    w = max(0, w)
        
    return p, w

# ── D. Portfolio Achievement Scale 1–10 ──────────────────────────────────────

def _tier(val: int, breakpoints: list[tuple[int, int]]) -> int:
    result = 0
    for threshold, score in breakpoints:
        if val >= threshold:
            result = score
    return result

_ACH_TIERS  = [(1, 1), (3, 2), (6, 3), (9, 4)]
_WIN_TIERS  = [(1, 1), (2, 2)]
_LEAD_TIERS = [(1, 1), (2, 2)]
_PORT_TIERS = [(2, 1), (4, 2)]

def portfolio_achievement_scale(record: dict) -> int:
    """
    Bounded 1–10 portfolio impact score.
    Logic: 4 (ach) + 2 (wins) + 2 (lead) + 2 (port) = 10 total.
    """
    _, won = competitions_participated_and_won(record)
    
    ach   = _int(record.get("achievement_count"), 0)
    lead  = _int(record.get("leadership_roles_count"), 0)
    port  = _int(record.get("portfolio_items_count"), 0)

    raw = (
        _tier(ach,  _ACH_TIERS)
        + _tier(won,  _WIN_TIERS)
        + _tier(lead, _LEAD_TIERS)
        + _tier(port, _PORT_TIERS)
    )
    
    if raw == 0:
        return 1
    return min(10, raw)

# ── Convenience builder ───────────────────────────────────────────────────────

def build_success_features(record: dict) -> dict:
    p, w = competitions_participated_and_won(record)
    return {
        "trl_mrl_gap":                       trl_mrl_gap(record),
        "mentorship_hours":                   mentorship_hours(record),
        "competitions_participated":          p,
        "competitions_won":                   w,
        "portfolio_achievement_scale_1_to_10": portfolio_achievement_scale(record),
    }