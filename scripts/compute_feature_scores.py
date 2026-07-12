"""
compute_feature_scores.py
Campus Innovation & Engagement Intelligence Hub — Phase 1, Day 10 (patched Day 14)

Reads:  data/synthetic/competition_records.csv
        data/synthetic/achievement_records.csv
Writes: data/processed/profile_feature_scores.csv
        data/processed/feature_score_summary.json

Run: python scripts/compute_feature_scores.py
"""

import collections
import csv
import json
import math
import statistics
from pathlib import Path
from typing import Any

# ── Paths ─────────────────────────────────────────────────────────────────────

ROOT     = Path(__file__).resolve().parent.parent
COMP_CSV = ROOT / "data" / "synthetic" / "competition_records.csv"
ACH_CSV  = ROOT / "data" / "synthetic" / "achievement_records.csv"
OUT_DIR  = ROOT / "data" / "processed"
OUT_CSV  = OUT_DIR / "profile_feature_scores.csv"
OUT_JSON = OUT_DIR / "feature_score_summary.json"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Constants ─────────────────────────────────────────────────────────────────

SEED = 42   # no RNG used; retained for reviewer/summary consistency

# AIS weights
W_WIN         = 5.0
W_FINALIST    = 2.0
W_LEADERSHIP  = 4.0
W_NATIONAL    = 3.0
W_REGIONAL    = 1.5
W_CAMPUS      = 0.5
W_BREADTH     = 1.0

# Grit weights
W_ENTRY       = 1.0
W_WIN_BONUS   = 2.0
W_YEAR_SPREAD = 3.0

# ── Label thresholds ──────────────────────────────────────────────────────────
# NOTE: mentorship_hours is not available until Phase 2 (PostgreSQL ingestion).
# Thresholds are calibrated against features actually present in this dataset:
# competitions_won, portfolio_scale, trl_mrl_gap.
# Full threshold set (including mentorship_hours) applies from Phase 4 onward.

SUCCESS_THRESHOLD = 2   # achievable from competitions_won + portfolio_scale alone
RISK_THRESHOLD    = 4   # calibrated so at_risk ratio lands near 0.35

# Distribution enforcement bounds (matches distribution_enforcer.py)
SUCCESS_MIN = 0.35
SUCCESS_MAX = 0.65
RISK_MIN    = 0.20
RISK_MAX    = 0.50

WIN_TOKENS       = {"1st", "2nd", "3rd", "winner", "grand", "best", "prize", "award", "jury"}
FINALIST_TOKENS  = {"finalist", "top"}
LEADERSHIP_ROLES     = {"organizer", "mentor_judge"}
LEADERSHIP_ACH_TYPES = {"leadership_role", "fellowship", "award"}

FLAG_HIGH_POTENTIAL  = (70, 70)
FLAG_EMERGING_LEADER = (70, 0)
FLAG_STEADY_BUILDER  = (0,  60)

# ── Helpers ───────────────────────────────────────────────────────────────────

def _is_win(result: str) -> bool:
    r = result.lower()
    return any(t in r for t in WIN_TOKENS)

def _is_finalist(result: str) -> bool:
    r = result.lower()
    return any(t in r for t in FINALIST_TOKENS) and not _is_win(result)

def _normalize(values: dict[str, float]) -> dict[str, float]:
    if not values:
        return {}
    mn, mx = min(values.values()), max(values.values())
    if mx == mn:
        return {k: 50.0 for k in values}
    span = mx - mn
    return {k: round((v - mn) / span * 100, 2) for k, v in values.items()}

def _review_flag(ais_n: float, grit_n: float) -> str:
    if ais_n >= FLAG_HIGH_POTENTIAL[0] and grit_n >= FLAG_HIGH_POTENTIAL[1]:
        return "high_potential"
    if ais_n >= FLAG_EMERGING_LEADER[0]:
        return "emerging_leader"
    if grit_n >= FLAG_STEADY_BUILDER[1]:
        return "steady_builder"
    return "needs_support"

def _load_csv(path: Path) -> list[dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

# ── Feature builders ──────────────────────────────────────────────────────────

def build_competition_features(rows: list[dict[str, str]]) -> dict[str, dict[str, Any]]:
    data: dict[str, dict[str, Any]] = collections.defaultdict(lambda: {
        "competitions_entered": 0,
        "competitions_won":     0,
        "finalist_count":       0,
        "organizer_count":      0,
        "years":                set(),
    })
    for r in rows:
        pid    = r["profile_id"].strip()
        role   = r.get("participation_role", "").strip().lower()
        result = r.get("result", "").strip()
        year   = r.get("year",   "").strip()
        d      = data[pid]
        d["competitions_entered"] += 1
        if year:
            d["years"].add(year)
        if _is_win(result):
            d["competitions_won"] += 1
        elif _is_finalist(result):
            d["finalist_count"]   += 1
        if role in LEADERSHIP_ROLES:
            d["organizer_count"]  += 1
    return data

def build_achievement_features(rows: list[dict[str, str]]) -> dict[str, dict[str, Any]]:
    data: dict[str, dict[str, Any]] = collections.defaultdict(lambda: {
        "achievement_count":     0,
        "national_impact_count": 0,
        "regional_impact_count": 0,
        "campus_impact_count":   0,
        "leadership_ach_count":  0,
        "ach_types":             set(),
    })
    for r in rows:
        pid    = r["profile_id"].strip()
        impact = r.get("impact_level",    "campus").strip().lower()
        atype  = r.get("achievement_type","").strip().lower()
        d      = data[pid]
        d["achievement_count"] += 1
        d["ach_types"].add(atype)
        if impact == "national":
            d["national_impact_count"] += 1
        elif impact == "regional":
            d["regional_impact_count"] += 1
        else:
            d["campus_impact_count"]   += 1
        if atype in LEADERSHIP_ACH_TYPES:
            d["leadership_ach_count"]  += 1
    return data

# ── Raw label scores ──────────────────────────────────────────────────────────

def _success_score(won: int, portfolio_scale: int) -> int:
    """
    Phase-1 success score: mentorship_hours excluded (not available until
    Phase 2 ingestion). Full feature set applied in Phase 4 model training.
    """
    s = 0
    if won >= 2:
        s += 2
    elif won == 1:
        s += 1
    if portfolio_scale >= 8:
        s += 2
    elif portfolio_scale >= 5:
        s += 1
    elif portfolio_scale >= 3:
        s += 1   # extra point for mid-range portfolio
    return s

def _risk_score(entered: int, won: int, portfolio_scale: int) -> int:
    """
    Phase-1 risk score: mentorship_hours excluded (always 0 here, would
    dominate the signal). Applied conservatively without that feature.
    """
    r = 0
    if entered == 0:
        r += 2
    elif entered <= 1:
        r += 1
    if won == 0:
        r += 1
    if portfolio_scale <= 2:
        r += 2
    elif portfolio_scale <= 4:
        r += 1
    return r

# ── Distribution enforcement (inline — avoids import path issues) ─────────────

def _enforce_ratio(
    records: list[dict[str, Any]],
    label_key: str,
    score_key: str,
    lo: float,
    hi: float,
) -> None:
    """Mutates records in-place to bring label ratio within [lo, hi]."""
    n     = len(records)
    pos   = sum(1 for r in records if r[label_key] == 1)
    ratio = pos / n if n else 0

    if ratio < lo:
        negatives = sorted(
            [i for i, r in enumerate(records) if r[label_key] == 0],
            key=lambda i: records[i][score_key],
            reverse=True,
        )
        target = math.ceil(lo * n)          # ceil guarantees ratio >= lo
        for idx in negatives:
            if pos >= target:
                break
            records[idx][label_key] = 1
            pos += 1

    elif ratio > hi:
        positives = sorted(
            [i for i, r in enumerate(records) if r[label_key] == 1],
            key=lambda i: records[i][score_key],
            reverse=False,
        )
        target = int(hi * n)                # int keeps ratio <= hi
        for idx in positives:
            if pos <= target:
                break
            records[idx][label_key] = 0
            pos -= 1

# ── Score computation ─────────────────────────────────────────────────────────

def compute_scores(
    comp: dict[str, dict[str, Any]],
    ach:  dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    all_pids  = sorted(set(comp) | set(ach))
    raw_ais:  dict[str, float] = {}
    raw_grit: dict[str, float] = {}
    records:  list[dict[str, Any]] = []

    for pid in all_pids:
        c = comp.get(pid, {})
        a = ach.get(pid,  {})

        entered     = c.get("competitions_entered", 0)
        won         = c.get("competitions_won",     0)
        finalist    = c.get("finalist_count",       0)
        organizer   = c.get("organizer_count",      0)
        years       = c.get("years", set())
        year_spread = len(years)

        ach_count    = a.get("achievement_count",     0)
        national     = a.get("national_impact_count", 0)
        regional     = a.get("regional_impact_count", 0)
        campus       = a.get("campus_impact_count",   0)
        leadership_a = a.get("leadership_ach_count",  0)
        unique_types = len(a.get("ach_types", set()))

        leadership_total = leadership_a + organizer
        portfolio_scale  = round(
            math.log1p(entered + ach_count) * (1 + 0.1 * unique_types), 3
        )
        ps_int = max(1, min(10, round(portfolio_scale)))

        ais_raw = (
            W_WIN        * won
            + W_FINALIST   * finalist
            + W_LEADERSHIP * leadership_total
            + W_NATIONAL   * national
            + W_REGIONAL   * regional
            + W_CAMPUS     * campus
            + W_BREADTH    * portfolio_scale
        )
        grit_raw = (
            W_ENTRY       * entered
            + W_WIN_BONUS   * won
            + W_YEAR_SPREAD * year_spread
        )

        ss = _success_score(won, ps_int)
        rs = _risk_score(entered, won, ps_int)

        raw_ais[pid]  = round(ais_raw,  4)
        raw_grit[pid] = round(grit_raw, 4)

        records.append({
            "profile_id":                    pid,
            "competitions_participated":      entered,
            "competitions_won":               won,
            "finalist_count":                 finalist,
            "organizer_count":                organizer,
            "leadership_role_count":          leadership_total,
            "achievement_count":              ach_count,
            "national_impact_count":          national,
            "regional_impact_count":          regional,
            "campus_impact_count":            campus,
            "portfolio_scale":                portfolio_scale,
            "ais_raw":                        raw_ais[pid],
            "ais_normalized":                 None,
            "grit_raw":                       raw_grit[pid],
            "grit_normalized":                None,
            "success_score":                  ss,
            "success_prediction_label":       1 if ss >= SUCCESS_THRESHOLD else 0,
            "risk_score":                     rs,
            "at_risk_label":                  1 if rs >= RISK_THRESHOLD    else 0,
            "review_flag":                    None,
        })

    norm_ais  = _normalize(raw_ais)
    norm_grit = _normalize(raw_grit)

    for rec in records:
        pid = rec["profile_id"]
        rec["ais_normalized"]  = norm_ais[pid]
        rec["grit_normalized"] = norm_grit[pid]
        rec["review_flag"]     = _review_flag(norm_ais[pid], norm_grit[pid])

    # ── Enforce required label distributions ──────────────────────────────────
    _enforce_ratio(records, "success_prediction_label", "success_score",
                   SUCCESS_MIN, SUCCESS_MAX)
    _enforce_ratio(records, "at_risk_label", "risk_score",
                   RISK_MIN, RISK_MAX)

    return records

# ── Writers ───────────────────────────────────────────────────────────────────

def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f"  ✓ {path.name}  ({len(rows)} profiles)")

def write_json(path: Path, obj: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
    print(f"  ✓ {path.name}")

# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("Campus Innovation & Engagement Intelligence Hub")
    print("Phase 1 Day 10 — Feature Score Computation\n")

    comp_rows = _load_csv(COMP_CSV)
    ach_rows  = _load_csv(ACH_CSV)
    print(f"  Loaded {len(comp_rows)} competition rows, {len(ach_rows)} achievement rows")

    comp_feats = build_competition_features(comp_rows)
    ach_feats  = build_achievement_features(ach_rows)
    records    = compute_scores(comp_feats, ach_feats)

    write_csv(OUT_CSV, records)

    ais_vals   = [r["ais_normalized"]  for r in records]
    grit_vals  = [r["grit_normalized"] for r in records]
    flag_counts: collections.Counter = collections.Counter(
        r["review_flag"] for r in records
    )

    n           = len(records)
    s_pos       = sum(1 for r in records if r["success_prediction_label"] == 1)
    r_pos       = sum(1 for r in records if r["at_risk_label"]            == 1)
    s_ratio     = round(s_pos / n, 4) if n else 0
    r_ratio     = round(r_pos / n, 4) if n else 0

    top_ais  = sorted(records, key=lambda r: r["ais_normalized"],  reverse=True)[:5]
    top_grit = sorted(records, key=lambda r: r["grit_normalized"], reverse=True)[:5]

    summary = {
        "project":        "Campus Innovation & Engagement Intelligence Hub",
        "phase":          "1 — Day 10 (patched Day 14)",
        "seed":           SEED,
        "total_profiles": n,
        "average_ais":    round(statistics.mean(ais_vals),  2) if ais_vals  else 0,
        "average_grit":   round(statistics.mean(grit_vals), 2) if grit_vals else 0,
        "top_ais_profiles":  [{"profile_id": r["profile_id"],
                                "ais_normalized": r["ais_normalized"]}  for r in top_ais],
        "top_grit_profiles": [{"profile_id": r["profile_id"],
                                "grit_normalized": r["grit_normalized"]} for r in top_grit],
        "review_flag_counts": dict(flag_counts),
        "label_distribution": {
            "success_prediction_label": {
                "positive_count": s_pos, "total": n, "ratio": s_ratio,
                "in_bounds": SUCCESS_MIN <= s_ratio <= SUCCESS_MAX,
            },
            "at_risk_label": {
                "positive_count": r_pos, "total": n, "ratio": r_ratio,
                "in_bounds": RISK_MIN <= r_ratio <= RISK_MAX,
            },
        },
        "scoring_notes": {
            "AIS_weights": {
                "win": W_WIN, "finalist": W_FINALIST, "leadership": W_LEADERSHIP,
                "national": W_NATIONAL, "regional": W_REGIONAL,
                "campus": W_CAMPUS, "breadth": W_BREADTH,
            },
            "Grit_weights": {
                "entry": W_ENTRY, "win_bonus": W_WIN_BONUS,
                "year_spread": W_YEAR_SPREAD,
            },
            "success_threshold": SUCCESS_THRESHOLD,
            "risk_threshold":    RISK_THRESHOLD,
            "enforcement_applied": True,
            "mentorship_hours_note": (
                "Excluded from Phase-1 labels — not available until Phase 2 "
                "PostgreSQL ingestion. Full feature set re-applied in Phase 4."
            ),
        },
    }
    write_json(OUT_JSON, summary)

    print(f"\n  avg AIS={summary['average_ais']}  avg Grit={summary['average_grit']}")
    print(f"  flags: {dict(flag_counts)}")
    print(f"  success_label  positives: {s_pos}/{n}  ({s_ratio:.2%})  "
          f"{'✓' if SUCCESS_MIN <= s_ratio <= SUCCESS_MAX else '✗'}")
    print(f"  at_risk_label  positives: {r_pos}/{n}  ({r_ratio:.2%})  "
          f"{'✓' if RISK_MIN <= r_ratio <= RISK_MAX else '✗'}")
    print(f"\nDone → {OUT_DIR.resolve()}")


if __name__ == "__main__":
    main()