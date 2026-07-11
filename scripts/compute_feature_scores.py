"""
compute_feature_scores.py
Campus Innovation & Engagement Intelligence Hub — Phase 1, Day 10

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

ROOT         = Path(__file__).resolve().parent.parent
COMP_CSV     = ROOT / "data" / "synthetic" / "competition_records.csv"
ACH_CSV      = ROOT / "data" / "synthetic" / "achievement_records.csv"
OUT_DIR      = ROOT / "data" / "processed"
OUT_CSV      = OUT_DIR / "profile_feature_scores.csv"
OUT_JSON     = OUT_DIR / "feature_score_summary.json"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Scoring constants ─────────────────────────────────────────────────────────

# AIS weights
W_WIN         = 5.0   # competition win or top award
W_FINALIST    = 2.0   # finalist / runner-up
W_LEADERSHIP  = 4.0   # organizer role or leadership achievement
W_NATIONAL    = 3.0   # national-impact achievement
W_REGIONAL    = 1.5   # regional-impact achievement
W_CAMPUS      = 0.5   # campus-impact achievement
W_BREADTH     = 1.0   # per unique achievement type (portfolio breadth)

# Grit weights
W_ENTRY       = 1.0   # each competition entered
W_WIN_BONUS   = 2.0   # bonus per win (persistence rewarded less than pure entry)
W_YEAR_SPREAD = 3.0   # reward for competing across multiple distinct years

# Tokens that indicate a win-level result
WIN_TOKENS    = {"1st", "2nd", "3rd", "winner", "grand", "best", "prize", "award", "jury"}
# Tokens that indicate finalist level
FINALIST_TOKENS = {"finalist", "top"}
# Participation roles considered leadership-style
LEADERSHIP_ROLES = {"organizer", "mentor_judge"}
# Achievement types considered leadership-oriented
LEADERSHIP_ACH_TYPES = {"leadership_role", "fellowship", "award"}

# Review flag thresholds (on normalized 0–100 scores)
FLAG_HIGH_POTENTIAL  = (70, 70)   # ais >= x AND grit >= y
FLAG_EMERGING_LEADER = (70, 0)    # ais >= x (grit any)
FLAG_STEADY_BUILDER  = (0,  60)   # grit >= y (ais any)
# else: needs_support

# ── Helpers ───────────────────────────────────────────────────────────────────

def _is_win(result: str) -> bool:
    r = result.lower()
    return any(t in r for t in WIN_TOKENS)

def _is_finalist(result: str) -> bool:
    r = result.lower()
    return any(t in r for t in FINALIST_TOKENS) and not _is_win(result)

def _normalize(values: dict[str, float]) -> dict[str, float]:
    """Min-max normalize a {id: raw} dict to 0–100. Safe on zero-range."""
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

def build_competition_features(
    rows: list[dict[str, str]]
) -> dict[str, dict[str, Any]]:
    """Returns per-profile competition stats."""
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
        year   = r.get("year", "").strip()

        d = data[pid]
        d["competitions_entered"] += 1
        if year:
            d["years"].add(year)
        if _is_win(result):
            d["competitions_won"] += 1
        elif _is_finalist(result):
            d["finalist_count"] += 1
        if role in LEADERSHIP_ROLES:
            d["organizer_count"] += 1
    return data


def build_achievement_features(
    rows: list[dict[str, str]]
) -> dict[str, dict[str, Any]]:
    """Returns per-profile achievement stats."""
    data: dict[str, dict[str, Any]] = collections.defaultdict(lambda: {
        "achievement_count":    0,
        "national_impact_count": 0,
        "regional_impact_count": 0,
        "campus_impact_count":   0,
        "leadership_ach_count":  0,
        "ach_types":            set(),
    })
    for r in rows:
        pid     = r["profile_id"].strip()
        impact  = r.get("impact_level", "campus").strip().lower()
        atype   = r.get("achievement_type", "").strip().lower()

        d = data[pid]
        d["achievement_count"]  += 1
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

# ── Score computation ─────────────────────────────────────────────────────────

def compute_scores(
    comp: dict[str, dict[str, Any]],
    ach:  dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    all_pids = sorted(set(comp) | set(ach))
    raw_ais:  dict[str, float] = {}
    raw_grit: dict[str, float] = {}
    records:  list[dict[str, Any]] = []

    for pid in all_pids:
        c = comp.get(pid, {})
        a = ach.get(pid,  {})

        entered    = c.get("competitions_entered", 0)
        won        = c.get("competitions_won",     0)
        finalist   = c.get("finalist_count",       0)
        organizer  = c.get("organizer_count",      0)
        years      = c.get("years", set())
        year_spread = len(years)

        ach_count     = a.get("achievement_count",     0)
        national      = a.get("national_impact_count", 0)
        regional      = a.get("regional_impact_count", 0)
        campus        = a.get("campus_impact_count",   0)
        leadership_a  = a.get("leadership_ach_count",  0)
        unique_types  = len(a.get("ach_types", set()))

        leadership_total = leadership_a + organizer

        # portfolio_scale: breadth across all activity
        portfolio_scale = round(
            math.log1p(entered + ach_count) * (1 + 0.1 * unique_types), 3
        )

        # AIS raw
        ais_raw = (
            W_WIN        * won
            + W_FINALIST   * finalist
            + W_LEADERSHIP * leadership_total
            + W_NATIONAL   * national
            + W_REGIONAL   * regional
            + W_CAMPUS     * campus
            + W_BREADTH    * portfolio_scale
        )

        # Grit raw
        grit_raw = (
            W_ENTRY      * entered
            + W_WIN_BONUS  * won
            + W_YEAR_SPREAD * year_spread
        )

        raw_ais[pid]  = round(ais_raw,  4)
        raw_grit[pid] = round(grit_raw, 4)

        records.append({
            "profile_id":            pid,
            "competitions_entered":  entered,
            "competitions_won":      won,
            "finalist_count":        finalist,
            "organizer_count":       organizer,
            "leadership_role_count": leadership_total,
            "achievement_count":     ach_count,
            "national_impact_count": national,
            "regional_impact_count": regional,
            "campus_impact_count":   campus,
            "portfolio_scale":       portfolio_scale,
            "ais_raw":               raw_ais[pid],
            "ais_normalized":        None,   # filled after normalization
            "grit_raw":              raw_grit[pid],
            "grit_normalized":       None,
            "review_flag":           None,
        })

    # Normalize
    norm_ais  = _normalize(raw_ais)
    norm_grit = _normalize(raw_grit)

    for rec in records:
        pid = rec["profile_id"]
        a_n = norm_ais[pid]
        g_n = norm_grit[pid]
        rec["ais_normalized"]  = a_n
        rec["grit_normalized"] = g_n
        rec["review_flag"]     = _review_flag(a_n, g_n)

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

    # Summary stats
    ais_vals  = [r["ais_normalized"]  for r in records]
    grit_vals = [r["grit_normalized"] for r in records]
    flag_counts: collections.Counter = collections.Counter(r["review_flag"] for r in records)

    top_ais  = sorted(records, key=lambda r: r["ais_normalized"],  reverse=True)[:5]
    top_grit = sorted(records, key=lambda r: r["grit_normalized"], reverse=True)[:5]

    summary = {
        "project":           "Campus Innovation & Engagement Intelligence Hub",
        "phase":             "1 — Day 10",
        "total_profiles":    len(records),
        "average_ais":       round(statistics.mean(ais_vals),  2) if ais_vals  else 0,
        "average_grit":      round(statistics.mean(grit_vals), 2) if grit_vals else 0,
        "top_ais_profiles":  [{"profile_id": r["profile_id"], "ais_normalized": r["ais_normalized"]}  for r in top_ais],
        "top_grit_profiles": [{"profile_id": r["profile_id"], "grit_normalized": r["grit_normalized"]} for r in top_grit],
        "review_flag_counts": dict(flag_counts),
        "scoring_notes": {
            "AIS_weights":  {"win": W_WIN, "finalist": W_FINALIST, "leadership": W_LEADERSHIP,
                             "national": W_NATIONAL, "regional": W_REGIONAL,
                             "campus": W_CAMPUS, "breadth": W_BREADTH},
            "Grit_weights": {"entry": W_ENTRY, "win_bonus": W_WIN_BONUS,
                             "year_spread": W_YEAR_SPREAD},
            "normalization": "min-max to 0–100; equal-value sets mapped to 50",
            "review_flags":  {
                "high_potential":  f"ais_n >= {FLAG_HIGH_POTENTIAL[0]} AND grit_n >= {FLAG_HIGH_POTENTIAL[1]}",
                "emerging_leader": f"ais_n >= {FLAG_EMERGING_LEADER[0]}",
                "steady_builder":  f"grit_n >= {FLAG_STEADY_BUILDER[1]}",
                "needs_support":   "all others",
            },
        },
    }
    write_json(OUT_JSON, summary)

    print(f"\n  avg AIS={summary['average_ais']}  avg Grit={summary['average_grit']}")
    print(f"  flags: {dict(flag_counts)}")
    print(f"\nDone → {OUT_DIR.resolve()}")


if __name__ == "__main__":
    main()