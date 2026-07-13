"""
compute_skill_scores.py
Campus Innovation & Engagement Intelligence Hub — Phase 1, Day 15

Full point-based skill scoring engine.

Reads:
  data/synthetic/competition_records_enriched.csv
  data/synthetic/achievement_records_enriched.csv
  data/synthetic/student_profiles.csv
  data/synthetic/alumni_profiles.csv

Writes:
  data/processed/profile_skill_scores.csv
  data/processed/skill_score_summary.json

Run: python scripts/compute_skill_scores.py
"""

import csv
import json
import math
import statistics
from pathlib import Path
from typing import Any

ROOT     = Path(__file__).resolve().parent.parent
SYN      = ROOT / "data" / "synthetic"
PROC     = ROOT / "data" / "processed"
PROC.mkdir(parents=True, exist_ok=True)

OUT_CSV  = PROC / "profile_skill_scores.csv"
OUT_JSON = PROC / "skill_score_summary.json"

SEED = 42  # no RNG used; retained for reviewer consistency

# ═══════════════════════════════════════════════════════════════════════════════
# SCORING CONSTANTS — single source of truth, mirrors skill_scoring_design.md
# ═══════════════════════════════════════════════════════════════════════════════

# ── Competition: outcome base points ──────────────────────────────────────────

COMPETITION_BASE_POINTS: dict[str, float] = {
    "just_registered":   0.0,
    "participated":      3.0,
    "shortlisted":       5.0,
    "finalist_top10":    8.0,
    "finalist_top5":    11.0,
    "third_place":      14.0,
    "second_place":     17.0,
    "first_place":      20.0,
    "special_award":    12.0,
    "organizer":         4.0,   # effort recognised, not skill
    "mentor_judge":      3.0,
}

# ── Competition: team size multipliers ────────────────────────────────────────

TEAM_SIZE_MULTIPLIER: dict[int, float] = {
    1: 2.0,
    2: 1.5,
    3: 1.2,
    4: 0.8,
    5: 0.6,
    6: 0.4,
}
TEAM_SIZE_DEFAULT = 0.4   # 7+ members

# ── Competition: difficulty tier multipliers ──────────────────────────────────

TIER_MULTIPLIER: dict[str, float] = {
    "S": 2.5,
    "A": 2.0,
    "B": 1.5,
    "C": 1.0,
    "D": 0.6,
}
TIER_DEFAULT = 1.0

# ── Internship: payment type base points ─────────────────────────────────────

INTERNSHIP_BASE_POINTS: dict[str, float] = {
    "paid_by_student": 2.0,
    "unpaid":          8.0,
    "stipend":        18.0,
    "paid":           25.0,
}

# ── Internship: mode multipliers ─────────────────────────────────────────────

INTERNSHIP_MODE_MULTIPLIER: dict[str, float] = {
    "online":  0.6,
    "hybrid":  0.85,
    "offline": 1.0,
}
MODE_DEFAULT = 0.7

# ── Internship: duration multipliers (by weeks) ───────────────────────────────

def duration_multiplier(weeks: int) -> float:
    if weeks < 4:
        return 0.5
    if weeks <= 8:
        return 0.8
    if weeks <= 12:
        return 1.0
    if weeks <= 24:
        return 1.2
    return 1.4

# ── Internship: company tier multipliers ──────────────────────────────────────

COMPANY_TIER_MULTIPLIER: dict[str, float] = {
    "S": 2.0,
    "A": 1.5,
    "B": 1.2,
    "C": 1.0,
    "D": 0.7,
}
COMPANY_TIER_DEFAULT = 0.8   # unknown

# ── Internship: paid-by-student hard cap ─────────────────────────────────────

PAID_BY_STUDENT_MODE_OVERRIDE = 0.4   # ignores actual mode
PAID_BY_STUDENT_MAX_POINTS    = 3.0

# ── Skill confidence boosts (added per relevant event) ────────────────────────

CONFIDENCE_BOOST: dict[str, float] = {
    "tier_S_win_small_team":      0.40,
    "tier_A_win":                 0.25,
    "tier_B_win":                 0.15,
    "participation_any":          0.05,
    "internship_paid_offline":    0.30,
    "internship_stipend_offline": 0.20,
    "internship_unpaid_offline":  0.12,
    "internship_paid_by_student": 0.03,
    "mentor_endorsement":         0.35,   # Phase 7
    "certificate_ner":            0.20,   # Phase 6
}

# ── Overall skill level classification ────────────────────────────────────────

SKILL_LEVEL_BANDS: list[tuple[float, str]] = [
    (0,    "Beginner"),
    (11,   "Developing"),
    (26,   "Intermediate"),
    (51,   "Proficient"),
    (81,   "Advanced"),
    (120,  "Expert"),
]

def classify_skill_level(score: float) -> str:
    level = "Beginner"
    for threshold, label in SKILL_LEVEL_BANDS:
        if score >= threshold:
            level = label
    return level

# ═══════════════════════════════════════════════════════════════════════════════
# OUTCOME CLASSIFIER
# Maps raw result/role strings → canonical outcome keys
# ═══════════════════════════════════════════════════════════════════════════════

def classify_outcome(role: str, result: str) -> str:
    role   = (role   or "").lower().strip()
    result = (result or "").lower().strip()

    if role == "organizer":
        return "organizer"
    if role == "mentor_judge":
        return "mentor_judge"

    for kw in ["1st", "first", "grand prix", "gold"]:
        if kw in result:
            return "first_place"
    for kw in ["2nd", "second", "silver"]:
        if kw in result:
            return "second_place"
    for kw in ["3rd", "third", "bronze"]:
        if kw in result:
            return "third_place"
    for kw in ["special", "best innovation", "jury", "award"]:
        if kw in result:
            return "special_award"
    for kw in ["top 5", "top-5", "finalist"]:
        if kw in result:
            return "finalist_top5"
    for kw in ["top 10", "top-10", "national finalist", "shortlist"]:
        if kw in result:
            return "finalist_top10"
    for kw in ["shortlisted", "top 50", "top 30", "top 20"]:
        if kw in result:
            return "shortlisted"
    for kw in ["participated", "completed", "submitted", "participation"]:
        if kw in result:
            return "participated"

    # fallback: if winner role present but unrecognised wording
    if role == "winner":
        return "first_place"
    if role == "finalist":
        return "finalist_top5"
    return "participated"

# ═══════════════════════════════════════════════════════════════════════════════
# POINT CALCULATORS
# ═══════════════════════════════════════════════════════════════════════════════

def compute_competition_points(
    role:    str,
    result:  str,
    tier:    str,
    team_size: int,
) -> tuple[float, str]:
    """
    Returns (points, outcome_key).
    """
    outcome    = classify_outcome(role, result)
    base       = COMPETITION_BASE_POINTS.get(outcome, 3.0)
    ts_mult    = TEAM_SIZE_MULTIPLIER.get(team_size, TEAM_SIZE_DEFAULT)
    tier_mult  = TIER_MULTIPLIER.get(tier.upper(), TIER_DEFAULT)

    # Organizer / judge roles: team-size multiplier not applicable
    if outcome in ("organizer", "mentor_judge"):
        ts_mult = 1.0

    points = base * ts_mult * tier_mult
    return round(points, 3), outcome


def compute_internship_points(
    itype:    str,
    imode:    str,
    duration: int,
    ctier:    str,
) -> float:
    """
    Returns points for a single internship event.
    Paid-by-student internships are hard-capped at PAID_BY_STUDENT_MAX_POINTS.
    """
    base     = INTERNSHIP_BASE_POINTS.get(itype, 2.0)
    dur_mult = duration_multiplier(duration)
    co_mult  = COMPANY_TIER_MULTIPLIER.get(ctier.upper(), COMPANY_TIER_DEFAULT)

    if itype == "paid_by_student":
        mode_mult = PAID_BY_STUDENT_MODE_OVERRIDE
        points    = base * mode_mult * dur_mult * co_mult
        return round(min(points, PAID_BY_STUDENT_MAX_POINTS), 3)

    mode_mult = INTERNSHIP_MODE_MULTIPLIER.get(imode, MODE_DEFAULT)
    points    = base * mode_mult * dur_mult * co_mult
    return round(points, 3)


def compute_confidence_boost(
    outcome: str,
    tier:    str,
    team_size: int,
    itype:   str,
    imode:   str,
) -> float:
    """
    Returns the confidence boost to apply to relevant skills for this event.
    """
    tier = tier.upper() if tier else ""

    # Internship boosts
    if itype:
        if itype == "paid" and imode == "offline":
            return CONFIDENCE_BOOST["internship_paid_offline"]
        if itype == "stipend" and imode == "offline":
            return CONFIDENCE_BOOST["internship_stipend_offline"]
        if itype == "unpaid" and imode == "offline":
            return CONFIDENCE_BOOST["internship_unpaid_offline"]
        return CONFIDENCE_BOOST["internship_paid_by_student"]

    # Competition boosts
    if outcome == "first_place":
        if tier == "S" and team_size <= 2:
            return CONFIDENCE_BOOST["tier_S_win_small_team"]
        if tier in ("S", "A"):
            return CONFIDENCE_BOOST["tier_A_win"]
        if tier == "B":
            return CONFIDENCE_BOOST["tier_B_win"]
    return CONFIDENCE_BOOST["participation_any"]

# ═══════════════════════════════════════════════════════════════════════════════
# LOADERS
# ═══════════════════════════════════════════════════════════════════════════════

def load_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_profile_skills(path: Path) -> dict[str, list[dict]]:
    """
    Returns {profile_id: [{"skill":..,"confidence":..,"level":..,"sources":[..]}]}
    Handles both old pipe-separated strings and new structured JSON.
    """
    rows = load_csv(path)
    out: dict[str, list[dict]] = {}
    for r in rows:
        pid    = r.get("student_id") or r.get("alumni_id") or r.get("profile_id", "")
        skills_raw = r.get("skills", "[]")

        # Detect format
        try:
            parsed = json.loads(skills_raw)
            if isinstance(parsed, list) and parsed and isinstance(parsed[0], dict):
                out[pid] = parsed   # already structured
                continue
        except (json.JSONDecodeError, IndexError):
            pass

        # Old pipe-separated string → upgrade to structured with baseline confidence
        skill_names = [s.strip() for s in skills_raw.split("|") if s.strip()]
        out[pid] = [
            {
                "skill":      s,
                "confidence": 0.10,
                "level":      "unknown",
                "sources":    ["self_declared"],
            }
            for s in skill_names
        ]
    return out

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN AGGREGATOR
# ═══════════════════════════════════════════════════════════════════════════════

def build_skill_profile(
    profile_id:    str,
    comp_rows:     list[dict],
    ach_rows:      list[dict],
    base_skills:   list[dict],
) -> dict[str, Any]:
    """
    Aggregates all competition and internship events for one profile
    into a full skill score record.
    """
    comp_points_total  = 0.0
    intern_points_total = 0.0
    competition_events: list[dict] = []
    internship_events:  list[dict] = []
    total_confidence_boost = 0.0

    # ── Competition records ──
    for r in comp_rows:
        if r.get("profile_id", "").strip() != profile_id:
            continue
        role   = r.get("participation_role", "participant")
        result = r.get("result", "")
        tier   = r.get("competition_tier", "C") or "C"
        try:
            ts = int(r.get("team_size", 4) or 4)
        except ValueError:
            ts = 4

        pts, outcome = compute_competition_points(role, result, tier, ts)
        boost        = compute_confidence_boost(outcome, tier, ts, "", "")
        comp_points_total  += pts
        total_confidence_boost += boost

        competition_events.append({
            "name":       r.get("competition_name", r.get("name", "")),
            "tier":       tier,
            "team_size":  ts,
            "outcome":    outcome,
            "points":     pts,
            "conf_boost": boost,
        })

    # ── Achievement records (internships / fellowships) ──
    INTERNSHIP_ACH_TYPES = {
        "internship", "fellowship", "industry_internship",
        "research_internship", "corporate_internship",
    }
    for r in ach_rows:
        if r.get("profile_id", "").strip() != profile_id:
            continue
        atype = r.get("achievement_type", "").lower()

        if not any(t in atype for t in ("internship", "fellowship")):
            # competition-type achievements already covered via competition_records
            continue

        itype    = r.get("internship_type", "unpaid") or "unpaid"
        imode    = r.get("internship_mode", "offline") or "offline"
        try:
            duration = int(r.get("internship_duration_weeks", 8) or 8)
        except ValueError:
            duration = 8
        ctier    = r.get("company_tier", "C") or "C"

        pts   = compute_internship_points(itype, imode, duration, ctier)
        boost = compute_confidence_boost("", "", 0, itype, imode)
        intern_points_total    += pts
        total_confidence_boost += boost

        internship_events.append({
            "type":        itype,
            "mode":        imode,
            "duration_wk": duration,
            "company_tier": ctier,
            "points":      pts,
            "conf_boost":  boost,
        })

    raw_score = round(comp_points_total + intern_points_total, 3)
    level     = classify_skill_level(raw_score)

    # Update skill confidence (capped at 1.0 per skill)
    updated_skills = []
    for sk in base_skills:
        new_conf = min(1.0, round(sk["confidence"] + total_confidence_boost, 3))
        updated_skills.append({
            **sk,
            "confidence": new_conf,
            "level":      level if new_conf >= 0.50 else sk["level"],
        })

    return {
        "profile_id":              profile_id,
        "competition_points":      round(comp_points_total,   3),
        "internship_points":       round(intern_points_total, 3),
        "raw_skill_score":         raw_score,
        "skill_level":             level,
        "total_confidence_boost":  round(total_confidence_boost, 3),
        "competition_event_count": len(competition_events),
        "internship_event_count":  len(internship_events),
        "skills_json":             json.dumps(updated_skills),
        "competition_events_json": json.dumps(competition_events),
        "internship_events_json":  json.dumps(internship_events),
    }

# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    print("Campus Innovation & Engagement Intelligence Hub")
    print("Phase 1 Day 15 — Skill Score Computation\n")

    # Load enriched records (fall back to base if enriched not present)
    comp_path = SYN / "competition_records_enriched.csv"
    if not comp_path.exists():
        comp_path = SYN / "competition_records.csv"
        print("  WARN: enriched competition file not found — using base (no tier/team_size)")
    ach_path  = SYN / "achievement_records_enriched.csv"
    if not ach_path.exists():
        ach_path  = SYN / "achievement_records.csv"
        print("  WARN: enriched achievement file not found — using base")

    comp_rows = load_csv(comp_path)
    ach_rows  = load_csv(ach_path)
    print(f"  Loaded {len(comp_rows)} competition rows, {len(ach_rows)} achievement rows")

    # Load base skills from both student and alumni profiles
    all_skills: dict[str, list[dict]] = {}
    for fname in ["student_profiles.csv", "alumni_profiles.csv"]:
        all_skills.update(load_profile_skills(SYN / fname))
    print(f"  Loaded skills for {len(all_skills)} profiles")

    # Collect all unique profile IDs across both data sources
    all_pids: set[str] = set()
    for r in comp_rows:
        pid = r.get("profile_id", "").strip()
        if pid:
            all_pids.add(pid)
    for r in ach_rows:
        pid = r.get("profile_id", "").strip()
        if pid:
            all_pids.add(pid)

    records: list[dict[str, Any]] = []
    for pid in sorted(all_pids):
        base_skills = all_skills.get(pid, [])
        rec = build_skill_profile(pid, comp_rows, ach_rows, base_skills)
        records.append(rec)

    # Write CSV (without the nested JSON columns for readability)
    flat_records = []
    for rec in records:
        flat_records.append({
            "profile_id":              rec["profile_id"],
            "competition_points":      rec["competition_points"],
            "internship_points":       rec["internship_points"],
            "raw_skill_score":         rec["raw_skill_score"],
            "skill_level":             rec["skill_level"],
            "total_confidence_boost":  rec["total_confidence_boost"],
            "competition_event_count": rec["competition_event_count"],
            "internship_event_count":  rec["internship_event_count"],
            "skills_json":             rec["skills_json"],
        })

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=flat_records[0].keys())
        writer.writeheader()
        writer.writerows(flat_records)
    print(f"\n  ✓ {OUT_CSV.name}  ({len(flat_records)} profiles)")

    # Summary stats
    scores  = [r["raw_skill_score"] for r in records]
    levels  = {}
    for r in records:
        levels[r["skill_level"]] = levels.get(r["skill_level"], 0) + 1

    top5 = sorted(records, key=lambda r: r["raw_skill_score"], reverse=True)[:5]

    summary = {
        "project":       "Campus Innovation & Engagement Intelligence Hub",
        "phase":         "1 — Day 15",
        "seed":          SEED,
        "total_profiles": len(records),
        "score_stats": {
            "mean":   round(statistics.mean(scores),   2) if scores else 0,
            "median": round(statistics.median(scores), 2) if scores else 0,
            "max":    round(max(scores),               2) if scores else 0,
            "min":    round(min(scores),               2) if scores else 0,
        },
        "skill_level_distribution": levels,
        "top_5_profiles": [
            {"profile_id": r["profile_id"], "raw_skill_score": r["raw_skill_score"],
             "skill_level": r["skill_level"]}
            for r in top5
        ],
        "scoring_constants": {
            "team_size_multipliers":    TEAM_SIZE_MULTIPLIER,
            "tier_multipliers":         TIER_MULTIPLIER,
            "internship_base_points":   INTERNSHIP_BASE_POINTS,
            "paid_by_student_cap":      PAID_BY_STUDENT_MAX_POINTS,
            "skill_level_bands":        {label: thr for thr, label in SKILL_LEVEL_BANDS},
        },
    }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"  ✓ {OUT_JSON.name}")

    print(f"\n  Score stats: mean={summary['score_stats']['mean']}  "
          f"median={summary['score_stats']['median']}  "
          f"max={summary['score_stats']['max']}")
    print(f"  Skill levels: {levels}")
    print(f"\nDone → {PROC.resolve()}")


if __name__ == "__main__":
    main()