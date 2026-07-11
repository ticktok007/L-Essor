"""
vectorized_generator.py
Campus Innovation & Engagement Intelligence Hub — Phase 1, Day 12

Provides slow (loop-based) and fast (numpy-vectorized) synthetic record generators.
Both follow the same schema and feature/label rules.

Usage:
    from data.generation.vectorized_generator import generate_vectorized_records
    records = generate_vectorized_records(n=10000)
"""

import math
import random
from typing import Any

import numpy as np

# ── Schema ────────────────────────────────────────────────────────────────────

REQUIRED_KEYS = [
    "record_id", "technology_readiness_level", "market_readiness_level",
    "trl_mrl_gap", "mentor_sessions_count", "avg_session_duration_hours",
    "mentorship_hours", "competitions_participated", "competitions_won",
    "leadership_roles_count", "achievement_count", "portfolio_items_count",
    "portfolio_achievement_scale_1_to_10",
    "success_score", "success_prediction_label",
    "risk_score",   "at_risk_label",
]

# ── Shared helpers (scalar + numpy-array compatible) ──────────────────────────

def _ach_tier(a: Any) -> Any:
    """achievement_count → contribution (0–4). Works on scalars and np arrays."""
    return np.where(a >= 9, 4,
           np.where(a >= 6, 3,
           np.where(a >= 3, 2,
           np.where(a >= 1, 1, 0))))

def _win_tier(w: Any) -> Any:
    return np.where(w >= 2, 2, np.where(w >= 1, 1, 0))

def _lead_tier(l: Any) -> Any:
    return np.where(l >= 2, 2, np.where(l >= 1, 1, 0))

def _port_tier(p: Any) -> Any:
    return np.where(p >= 4, 2, np.where(p >= 2, 1, 0))

def compute_portfolio_scale(
    achievement_count: Any,
    competitions_won: Any,
    leadership_roles_count: Any,
    portfolio_items_count: Any,
) -> Any:
    """
    Returns portfolio_achievement_scale_1_to_10.
    Accepts scalars or numpy arrays.
    """
    raw = (
        _ach_tier(achievement_count)
        + _win_tier(competitions_won)
        + _lead_tier(leadership_roles_count)
        + _port_tier(portfolio_items_count)
    )
    clamped = np.clip(raw, 1, 10)
    # If raw==0 the np.clip already returns 1 via the lower bound.
    return clamped


def compute_success_label(
    mentorship_hours: Any,
    competitions_won: Any,
    portfolio_scale: Any,
    trl_mrl_gap: Any,
) -> tuple[Any, Any]:
    """
    Returns (success_score, success_prediction_label).
    Accepts scalars or numpy arrays.
    Threshold = 5.
    """
    s = (
        np.where(mentorship_hours >= 20, 2, np.where(mentorship_hours >= 8, 1, 0))
        + np.where(competitions_won >= 2, 2, np.where(competitions_won == 1, 1, 0))
        + np.where(portfolio_scale >= 8, 2, np.where(portfolio_scale >= 5, 1, 0))
        + np.where((trl_mrl_gap >= -1) & (trl_mrl_gap <= 2), 2,
          np.where((trl_mrl_gap >= -3) & (trl_mrl_gap <= 3), 1, 0))
    )
    return s, (s >= 5).astype(int)


def compute_at_risk_label(
    mentorship_hours: Any,
    competitions_participated: Any,
    competitions_won: Any,
    portfolio_scale: Any,
) -> tuple[Any, Any]:
    """
    Returns (risk_score, at_risk_label).
    Accepts scalars or numpy arrays.
    Threshold = 4.
    """
    r = (
        np.where(mentorship_hours < 2, 2, np.where(mentorship_hours < 6, 1, 0))
        + np.where(competitions_participated == 0, 2,
          np.where(competitions_participated <= 1, 1, 0))
        + np.where(competitions_won == 0, 1, 0)
        + np.where(portfolio_scale <= 2, 2, np.where(portfolio_scale <= 4, 1, 0))
    )
    return r, (r >= 4).astype(int)


# ── Slow generator ─────────────────────────────────────────────────────────────

def generate_slow_records(n: int, seed: int = 42) -> list[dict]:
    """
    Loop-based baseline generator. Correct but O(n) Python overhead.
    Used for benchmark comparison only.
    """
    rng = random.Random(seed)
    records: list[dict[str, Any]] = []

    for i in range(1, n + 1):
        trl = rng.randint(1, 9)
        mrl = rng.randint(1, 9)
        gap = trl - mrl

        sessions   = max(0, int(rng.gauss(4, 3)))
        avg_dur    = round(rng.uniform(0.5, 3.0), 2)
        m_hours    = round(sessions * avg_dur, 2)

        participated = max(0, int(rng.gauss(3, 2)))
        won          = rng.randint(0, max(0, participated))

        leadership = max(0, int(rng.gauss(0.8, 0.9)))
        ach_count  = max(0, int(rng.gauss(4, 3)))
        port_items = max(0, int(rng.gauss(3, 2)))

        # scalar numpy calls are fine here
        scale = int(compute_portfolio_scale(ach_count, won, leadership, port_items))
        ss, slabel = compute_success_label(m_hours, won, scale, gap)
        rs, rlabel = compute_at_risk_label(m_hours, participated, won, scale)

        records.append({
            "record_id":                          i,
            "technology_readiness_level":          trl,
            "market_readiness_level":              mrl,
            "trl_mrl_gap":                         gap,
            "mentor_sessions_count":               sessions,
            "avg_session_duration_hours":          avg_dur,
            "mentorship_hours":                    m_hours,
            "competitions_participated":           participated,
            "competitions_won":                    won,
            "leadership_roles_count":              leadership,
            "achievement_count":                   ach_count,
            "portfolio_items_count":               port_items,
            "portfolio_achievement_scale_1_to_10": scale,
            "success_score":                       int(ss),
            "success_prediction_label":            int(slabel),
            "risk_score":                          int(rs),
            "at_risk_label":                       int(rlabel),
        })
    return records


# ── Vectorized generator ───────────────────────────────────────────────────────

def generate_vectorized_records(n: int, seed: int = 42) -> list[dict]:
    """
    Numpy-vectorized generator. All intermediate computations are array ops.
    Final conversion to list[dict] occurs once at the end.
    """
    rng = np.random.default_rng(seed)

    # -- Raw feature arrays --
    trl = rng.integers(1, 10, size=n)   # [1, 9]
    mrl = rng.integers(1, 10, size=n)
    gap = (trl - mrl).astype(np.int32)

    sessions = np.clip(
        np.round(rng.normal(4.0, 3.0, size=n)).astype(np.int32), 0, None
    )
    avg_dur = np.round(rng.uniform(0.5, 3.0, size=n), 2)
    m_hours = np.round(sessions * avg_dur, 2)
    m_hours = np.maximum(m_hours, 0.0)

    participated = np.clip(
        np.round(rng.normal(3.0, 2.0, size=n)).astype(np.int32), 0, None
    )
    # won ∈ [0, participated]
    won_frac = rng.uniform(0.0, 1.0, size=n)
    won = np.floor(won_frac * (participated + 1)).astype(np.int32)
    won = np.clip(won, 0, participated)

    leadership = np.clip(
        np.round(rng.normal(0.8, 0.9, size=n)).astype(np.int32), 0, None
    )
    ach_count  = np.clip(
        np.round(rng.normal(4.0, 3.0, size=n)).astype(np.int32), 0, None
    )
    port_items = np.clip(
        np.round(rng.normal(3.0, 2.0, size=n)).astype(np.int32), 0, None
    )

    # -- Derived arrays --
    scale        = compute_portfolio_scale(ach_count, won, leadership, port_items)
    ss, slabels  = compute_success_label(m_hours, won, scale, gap)
    rs, rlabels  = compute_at_risk_label(m_hours, participated, won, scale)

    # -- Vectorized avg_session rounding storage --
    avg_dur_r = np.round(avg_dur, 2)

    # -- Build list[dict] in one pass --
    ids = np.arange(1, n + 1, dtype=np.int32)

    records: list[dict[str, Any]] = [
        {
            "record_id":                          int(ids[i]),
            "technology_readiness_level":          int(trl[i]),
            "market_readiness_level":              int(mrl[i]),
            "trl_mrl_gap":                         int(gap[i]),
            "mentor_sessions_count":               int(sessions[i]),
            "avg_session_duration_hours":          float(avg_dur_r[i]),
            "mentorship_hours":                    float(m_hours[i]),
            "competitions_participated":           int(participated[i]),
            "competitions_won":                    int(won[i]),
            "leadership_roles_count":              int(leadership[i]),
            "achievement_count":                   int(ach_count[i]),
            "portfolio_items_count":               int(port_items[i]),
            "portfolio_achievement_scale_1_to_10": int(scale[i]),
            "success_score":                       int(ss[i]),
            "success_prediction_label":            int(slabels[i]),
            "risk_score":                          int(rs[i]),
            "at_risk_label":                       int(rlabels[i]),
        }
        for i in range(n)
    ]
    return records