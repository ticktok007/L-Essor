"""
skill_data_enricher.py
Campus Innovation & Engagement Intelligence Hub — Phase 1, Day 15

Enriches existing synthetic competition_records.csv and achievement_records.csv
with fields needed by the skill scoring engine:
  - competition_records  → competition_tier, team_size (if missing)
  - achievement_records  → internship_type, internship_mode,
                           internship_duration_weeks, company_tier,
                           competition_tier, team_size

Run: python data/generation/skill_data_enricher.py
Outputs:
  data/synthetic/competition_records_enriched.csv
  data/synthetic/achievement_records_enriched.csv
"""

import csv
import json
import random
from pathlib import Path

SEED = 42
random.seed(SEED)

ROOT   = Path(__file__).resolve().parent.parent.parent
SYN    = ROOT / "data" / "synthetic"

# ── Competition tier mapping ───────────────────────────────────────────────────
# Maps competition names to difficulty tiers S / A / B / C / D.
# Competitions not in this map default to tier C.

COMPETITION_TIER_MAP: dict[str, str] = {
    # Tier S — international, highly competitive
    "NASA Space Apps Challenge":            "S",
    "Google Hash Code":                     "S",
    "ICPC":                                 "S",
    "IEEE Xtreme":                          "S",
    "ACM ICPC":                             "S",
    # Tier A — national flagship
    "Smart India Hackathon":                "A",
    "Microsoft Imagine Cup":                "A",
    "Google Solution Challenge":            "A",
    "TOYCATHON":                            "A",
    "National Entrepreneurship Challenge IIT Bombay": "A",
    "India Innovation Challenge Design Contest":      "A",
    "BIRAC BIG Pitching Forum":             "A",
    # Tier B — reputed national / state
    "NASSCOM 10K Startups":                 "B",
    "TiE Entrepreneurial Challenge":        "B",
    "CII Young Indians Innovation Challenge": "B",
    "NIDHI Prayas Demo Day":                "B",
    "IIM Ahmedabad Eureka!":                "B",
    "Kerala Startup Mission Demo Day":      "B",
    "Sequoia Surge Campus Pitch":           "B",
    "Vernacular AI Hackathon by AI4Bharat": "B",
    # Tier C — university / state level
    "Anna University Innovation Challenge": "C",
    "IIT Madras Shaastra Hackathon":        "C",
    "Startup Tamil Nadu Ideathon":          "C",
    "T-Hub LabStart Cohort":                "C",
    # Tier D — low-barrier / participation-only
    "Online Hackathon":                     "D",
    "Virtual Ideathon":                     "D",
}

TIERS         = ["S", "A", "B", "C", "D"]
TIER_WEIGHTS  = [2, 8, 20, 55, 15]    # realistic distribution

# ── Company tier mapping ───────────────────────────────────────────────────────

COMPANY_TIER_MAP: dict[str, str] = {
    # S
    "Google India": "S", "Microsoft India": "S", "Amazon India": "S",
    # A
    "Infosys": "A", "TCS": "A", "Wipro": "A", "HCL Technologies": "A",
    "Tech Mahindra": "A", "Cognizant": "A", "Accenture": "A",
    "IBM India": "A", "Oracle India": "A", "SAP Labs India": "A",
    "Zoho Corporation": "A", "Freshworks": "A", "PhonePe": "A",
    "Razorpay": "A", "CRED": "A", "Flipkart": "A",
    # B
    "Swiggy": "B", "Zomato": "B", "Ola": "B", "Paytm": "B",
    "Meesho": "B", "BrowserStack": "B", "Postman": "B",
    "HashedIn": "B", "Sigmoid": "B", "ThoughtWorks": "B",
    "Mphasis": "B", "LTIMindtree": "B", "Persistent Systems": "B",
    "BPCL": "B", "CPCL": "B",
}

INTERNSHIP_TYPES  = ["paid_by_student", "unpaid", "stipend", "paid"]
INTERNSHIP_MODES  = ["online", "offline", "hybrid"]
DURATION_BANDS    = [4, 6, 8, 10, 12, 16, 20, 24]

# Realistic weighted distributions
ITYPE_WEIGHTS     = [10, 20, 45, 25]
IMODE_WEIGHTS     = [30, 50, 20]
TEAM_SIZE_WEIGHTS = [15, 25, 30, 20, 7, 3]   # 1,2,3,4,5,6 members

# ── Helpers ───────────────────────────────────────────────────────────────────

def _load(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _save(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f"  ✓ {path.name}  ({len(rows)} rows)")


def _competition_tier(name: str) -> str:
    return COMPETITION_TIER_MAP.get(
        name,
        random.choices(TIERS, weights=TIER_WEIGHTS, k=1)[0]
    )


def _company_tier(name: str) -> str:
    return COMPANY_TIER_MAP.get(name, "C")


def _team_size(tier: str, role: str) -> int:
    """
    Larger competitions tend to have larger teams.
    Solo submissions rare except in coding competitions.
    """
    if role in ("organizer", "mentor_judge"):
        return 0
    if tier == "S":
        weights = [25, 30, 25, 15, 4, 1]   # smaller teams in competitive coding
    elif tier == "A":
        weights = [5, 15, 30, 35, 10, 5]
    else:
        weights = [5, 10, 25, 35, 15, 10]
    return random.choices([1, 2, 3, 4, 5, 6], weights=weights, k=1)[0]


# ── Enrichment functions ──────────────────────────────────────────────────────

def enrich_competition_records(rows: list[dict]) -> list[dict]:
    enriched = []
    for r in rows:
        r = dict(r)
        name = r.get("competition_name", r.get("name", ""))
        role = r.get("participation_role", "participant")
        tier = _competition_tier(name)

        r["competition_tier"] = tier

        # Only add team_size if not already present or is 0 and role is competing
        existing_ts = r.get("team_size", "")
        if existing_ts == "" or existing_ts == "0" and role not in ("organizer", "mentor_judge"):
            r["team_size"] = str(_team_size(tier, role))

        enriched.append(r)
    return enriched


def enrich_achievement_records(rows: list[dict]) -> list[dict]:
    """
    For competition achievements: add competition_tier, team_size.
    For internship achievements: add internship_type, internship_mode,
        internship_duration_weeks, company_tier.
    For all other types: add null/empty fields so schema is consistent.
    """
    INTERNSHIP_TYPES_SET = {
        "internship", "industry_internship", "research_internship",
        "corporate_internship",
    }
    COMPETITION_TYPES_SET = {
        "hackathon_win", "competition_win", "competition",
    }

    enriched = []
    for r in rows:
        r = dict(r)
        atype = r.get("achievement_type", "").lower()

        # ── Competition achievement fields ──
        if atype in COMPETITION_TYPES_SET:
            title = r.get("title", "")
            # Try to extract competition name from title
            tier  = "C"
            for cname, ctier in COMPETITION_TIER_MAP.items():
                if cname.lower() in title.lower():
                    tier = ctier
                    break
            else:
                tier = random.choices(TIERS, weights=TIER_WEIGHTS, k=1)[0]
            r["competition_tier"]          = tier
            r["team_size"]                 = str(random.choices(
                                                [1,2,3,4,5,6],
                                                weights=TEAM_SIZE_WEIGHTS, k=1)[0])
            r["internship_type"]           = ""
            r["internship_mode"]           = ""
            r["internship_duration_weeks"] = ""
            r["company_tier"]              = ""

        # ── Internship achievement fields ──
        elif "internship" in atype or "fellowship" in atype:
            itype    = random.choices(INTERNSHIP_TYPES,  weights=ITYPE_WEIGHTS,  k=1)[0]
            imode    = random.choices(INTERNSHIP_MODES,  weights=IMODE_WEIGHTS,  k=1)[0]
            duration = random.choice(DURATION_BANDS)
            issuer   = r.get("issuing_body", "")
            ctier    = _company_tier(issuer)

            # Paid-by-student internships are almost always online
            if itype == "paid_by_student":
                imode = random.choices(["online", "offline"], weights=[80, 20], k=1)[0]

            r["competition_tier"]          = ""
            r["team_size"]                 = ""
            r["internship_type"]           = itype
            r["internship_mode"]           = imode
            r["internship_duration_weeks"] = str(duration)
            r["company_tier"]              = ctier

        # ── All other achievement types ──
        else:
            r["competition_tier"]          = ""
            r["team_size"]                 = ""
            r["internship_type"]           = ""
            r["internship_mode"]           = ""
            r["internship_duration_weeks"] = ""
            r["company_tier"]              = ""

        enriched.append(r)
    return enriched


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("Campus Innovation & Engagement Intelligence Hub")
    print("Phase 1 — Skill Data Enricher\n")

    comp_rows = _load(SYN / "competition_records.csv")
    ach_rows  = _load(SYN / "achievement_records.csv")

    if not comp_rows:
        print("  WARN: competition_records.csv not found — run generate_interaction_data.py first")
    else:
        enriched_comp = enrich_competition_records(comp_rows)
        _save(SYN / "competition_records_enriched.csv", enriched_comp)
        print(f"       Added: competition_tier, team_size")

    if not ach_rows:
        print("  WARN: achievement_records.csv not found — run generate_interaction_data.py first")
    else:
        enriched_ach = enrich_achievement_records(ach_rows)
        _save(SYN / "achievement_records_enriched.csv", enriched_ach)
        print(f"       Added: competition_tier, team_size, internship_type,")
        print(f"              internship_mode, internship_duration_weeks, company_tier")

    print(f"\nDone → {SYN.resolve()}")


if __name__ == "__main__":
    main()