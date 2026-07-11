"""
target_labels.py
Campus Innovation & Engagement Intelligence Hub
Phase 1 — Week 2: ML Target Label Engineering

Depends on: ml/features/success_features.py
"""

from ml.features.success_features import (
    build_success_features,
    mentorship_hours,
    competitions_participated_and_won,
    portfolio_achievement_scale,
    trl_mrl_gap,
)

# ── E. Success Prediction Label ───────────────────────────────────────────────

_SUCCESS_THRESHOLD = 6

def success_prediction_label(record: dict) -> int:
    """
    Binary label: 1 = likely successful startup, 0 = otherwise.
    Deterministic score-based logic; threshold = 6.
    """
    feats = build_success_features(record)
    score = 0

    # mentorship_hours
    mh = feats["mentorship_hours"]
    if mh >= 20:
        score += 2
    elif mh >= 8:
        score += 1

    # competitions_won
    cw = feats["competitions_won"]
    if cw >= 2:
        score += 2
    elif cw == 1:
        score += 1

    # portfolio scale
    ps = feats["portfolio_achievement_scale_1_to_10"]
    if ps >= 8:
        score += 2
    elif ps >= 5:
        score += 1

    # trl_mrl_gap
    gap = feats["trl_mrl_gap"]
    if -1 <= gap <= 2:
        score += 2
    elif -3 <= gap <= 3:
        score += 1

    # funding stage
    fundable_stages = {"seed", "pre-seed", "grant-funded", "revenue-generating"}
    if str(record.get("funding_stage", "")).lower() in fundable_stages:
        score += 1

    # traction (max +1 total)
    traction = 0
    if int(record.get("users_count", 0) or 0) >= 1000:
        traction = 1
    elif float(record.get("revenue", 0) or 0) > 0:
        traction = 1
    elif int(record.get("pilot_customers", 0) or 0) >= 3:
        traction = 1
    score += traction

    return 1 if score >= _SUCCESS_THRESHOLD else 0

# ── F. At-Risk Label ──────────────────────────────────────────────────────────

_RISK_THRESHOLD = 5

def at_risk_label(record: dict) -> int:
    """
    Binary label: 1 = at risk of disengagement, 0 = not at risk.
    Deterministic risk-score logic; threshold = 5.
    """
    feats = build_success_features(record)
    risk  = 0

    # mentorship_hours
    mh = feats["mentorship_hours"]
    if mh < 2:
        risk += 2
    elif mh < 6:
        risk += 1

    # competitions_participated
    cp = feats["competitions_participated"]
    if cp == 0:
        risk += 2
    elif cp <= 1:
        risk += 1

    # competitions_won
    if feats["competitions_won"] == 0:
        risk += 1

    # portfolio scale
    ps = feats["portfolio_achievement_scale_1_to_10"]
    if ps <= 2:
        risk += 2
    elif ps <= 4:
        risk += 1

    # last_active_days_ago
    lad = record.get("last_active_days_ago")
    if lad is not None:
        lad = int(lad)
        if lad > 45:
            risk += 2
        elif lad > 21:
            risk += 1

    # submissions_count_last_90_days
    sub = record.get("submissions_count_last_90_days")
    if sub is not None:
        sub = int(sub)
        if sub == 0:
            risk += 2
        elif sub <= 2:
            risk += 1

    return 1 if risk >= _RISK_THRESHOLD else 0

# ── Convenience builder ───────────────────────────────────────────────────────

def build_labels(record: dict) -> dict:
    """
    Returns both ML target labels for a single record dict.
    """
    return {
        "success_prediction_label": success_prediction_label(record),
        "at_risk_label":            at_risk_label(record),
    }   