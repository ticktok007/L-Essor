"""
generate_interaction_data.py
Campus Innovation & Engagement Intelligence Hub
Phase 1 — Synthetic Data Foundation: Interaction Edges, Competitions, Achievements

Generates CSVs, a JSON summary, and a degree-distribution PNG into data/synthetic/.
Run with: python generate_interaction_data.py

Requirements: pip install faker matplotlib
Python 3.11+
"""

import collections
import csv
import json
import math
import random
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")  # non-interactive backend — no display needed
import matplotlib.pyplot as plt
from faker import Faker

# ---------------------------------------------------------------------------
# Seed + output
# ---------------------------------------------------------------------------

SEED = 42
random.seed(SEED)
fake = Faker("en_IN")
Faker.seed(SEED)

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "synthetic"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Record counts
# ---------------------------------------------------------------------------

NUM_EDGES          = 500
NUM_COMPETITIONS   = 300
NUM_ACHIEVEMENTS   = 250

# ---------------------------------------------------------------------------
# Node ID pools
# ---------------------------------------------------------------------------

# Deliberately small pools so popular nodes accumulate many edges → hubs
STU_IDS  = [f"STU-{i:04d}" for i in range(1, 301)]    # 300 students
ALU_IDS  = [f"ALU-{i:04d}" for i in range(1, 201)]    # 200 alumni
INV_IDS  = [f"INV-{i:04d}" for i in range(1, 51)]     # 50 investors
MEN_IDS  = [f"MEN-{i:04d}" for i in range(51, 101)]   # 50 mentors
CLB_IDS  = [f"CLB-{i:04d}" for i in range(1, 21)]     # 20 clubs/communities

# Hub nodes: a small set that will be preferentially sampled
HUB_STU  = random.sample(STU_IDS, 12)
HUB_ALU  = random.sample(ALU_IDS, 8)
HUB_MEN  = random.sample(MEN_IDS, 6)
HUB_INV  = random.sample(INV_IDS, 5)

def _hub_weighted(pool: list[str], hubs: list[str], hub_weight: int = 6) -> str:
    """Sample from pool with hub nodes appearing hub_weight× more often."""
    weighted = pool + hubs * hub_weight
    return random.choice(weighted)

# ---------------------------------------------------------------------------
# Domain data
# ---------------------------------------------------------------------------

EDGE_TYPES = ["mentor_mentee", "investor_founder", "club_membership"]

STRENGTH_LEVELS = ["weak", "medium", "strong"]

STRENGTH_TO_COUNT = {
    "weak":   (1, 3),
    "medium": (4, 10),
    "strong": (11, 30),
}

MENTOR_CONTEXTS = [
    "Weekly 1:1 session on product strategy",
    "Intro call via incubation cell referral",
    "Mock investor pitch review session",
    "Resume and career path advisory",
    "Technical architecture review",
    "Demo day preparation workshop",
    "Monthly check-in on startup metrics",
    "Grant application guidance session",
]

INVESTOR_CONTEXTS = [
    "Warm intro via alumni network",
    "Post-demo-day follow-up meeting",
    "Due diligence call on seed round",
    "Initial screening call via platform match",
    "Co-investor introduction at startup event",
    "Term sheet discussion meeting",
    "Portfolio company referral meeting",
]

CLUB_CONTEXTS = [
    "Joined entrepreneurship club as core member",
    "Enrolled in IEEE technical chapter",
    "Became lead of coding club",
    "Active contributor in design thinking cell",
    "Joined AI/ML reading group",
    "Core team member of startup incubation cell",
    "Mentorship pod member in innovation hub",
    "Volunteer organiser for hackathon chapter",
]

COMPETITION_NAMES = [
    "Smart India Hackathon",
    "TOYCATHON",
    "NASA Space Apps Challenge",
    "Google Solution Challenge",
    "Microsoft Imagine Cup",
    "NASSCOM 10K Startups",
    "TiE Entrepreneurial Challenge",
    "CII Young Indians Innovation Challenge",
    "NIDHI Prayas Demo Day",
    "IIM Ahmedabad Eureka!",
    "Anna University Innovation Challenge",
    "IIT Madras Shaastra Hackathon",
    "Startup Tamil Nadu Ideathon",
    "T-Hub LabStart Cohort",
    "Sequoia Surge Campus Pitch",
    "India Innovation Challenge Design Contest",
    "Vernacular AI Hackathon by AI4Bharat",
    "BIRAC BIG Grant Pitching Forum",
    "National Entrepreneurship Challenge (IIT Bombay)",
    "Kerala Startup Mission Demo Day",
]

COMPETITION_TYPES = [
    "hackathon", "innovation_challenge", "startup_pitch",
    "demo_day", "design_sprint", "ideathon", "product_showcase",
]

COMPETITION_THEMES = [
    "Healthcare & MedTech", "EdTech & Skill Development",
    "FinTech & Financial Inclusion", "AgriTech & Rural Development",
    "CleanTech & Sustainability", "Smart Cities & GovTech",
    "Deep Tech & AI/ML", "Cybersecurity",
    "Logistics & Supply Chain", "Women Empowerment & Social Impact",
]

PARTICIPATION_ROLES = ["participant", "finalist", "winner", "organizer", "mentor_judge"]

RESULT_BY_ROLE = {
    "participant":   ["Participated", "Shortlisted in top 50", "Completed submission"],
    "finalist":      ["Top 10 finalist", "Top 5 finalist", "National finalist"],
    "winner":        ["1st Place", "2nd Place", "3rd Place", "Best Innovation Award", "Special Jury Prize"],
    "organizer":     ["Organised successfully; 400+ participants", "Coordinated 3 tracks; 200 teams"],
    "mentor_judge":  ["Evaluated 30 teams as domain expert judge", "Mentored 5 finalist teams"],
}

ACHIEVEMENT_TYPES = [
    "hackathon_win", "leadership_role", "incubator_selection",
    "research_demo", "prototype_completion", "grant_recognition",
    "patent_filing", "publication", "fellowship", "award",
]

ACHIEVEMENT_TITLES = {
    "hackathon_win":        ["Winner — Smart India Hackathon 2024", "1st Place — IIT Madras Shaastra Hack", "Best Prototype Award — NASA Space Apps", "Grand Prix — Google Solution Challenge India"],
    "leadership_role":      ["President, Entrepreneurship Cell", "Technical Lead, IEEE Student Chapter", "Club Captain, AI/ML Research Group", "Core Organiser, Annual Innovation Summit"],
    "incubator_selection":  ["Selected — NIDHI PRAYAS Cohort 7", "Admitted — T-Hub LabStart Programme", "Accepted — CIIE.CO Pre-Incubation", "Inducted — Anna University BioNEST"],
    "research_demo":        ["Research Demonstration at ICCV 2024", "Poster Presentation, NeurIPS Student Workshop", "Demo at NASSCOM AI Symposium", "Paper Presentation, ICSE 2023"],
    "prototype_completion": ["Working Prototype of IoT Health Monitor", "MVP Completion — AI Crop Disease Detector", "Hardware Prototype for EV Charging Hub", "Functional Demo of NLP Invoice Parser"],
    "grant_recognition":    ["BIRAC BIG Grant Recipient", "DST-NIMAT Grant Awardee", "TIDE 2.0 Cohort Member", "AIM-iCREATE Finalist"],
    "patent_filing":        ["Patent Filed: Adaptive Learning Algorithm (2024)", "Patent Application: Multimodal Soil Sensor Array", "Provisional Patent: Low-Power Edge AI Module"],
    "publication":          ["Published in IEEE Transactions on Neural Networks", "Accepted at ACM SIGCHI 2024", "Paper in Springer LNCS Vol. 14221"],
    "fellowship":           ["Prime Minister's Research Fellowship", "Google Generation Scholar", "Infosys Foundation Fellowship", "Qualcomm Innovation Fellowship India"],
    "award":                ["Best Student Innovator — NASSCOM", "Young Entrepreneur Award — CII", "Top 30 Under 30 Innovators — Inc42", "DRDO Young Scientist Award"],
}

ISSUING_BODIES = {
    "hackathon_win":        ["Ministry of Education, GoI", "IIT Madras", "NASA", "Google"],
    "leadership_role":      ["Chennai Institute of Technology", "IEEE India Council", "Student Council", "Institution's Innovation Cell"],
    "incubator_selection":  ["DST-NIDHI", "T-Hub Hyderabad", "CIIE.CO Ahmedabad", "Anna University"],
    "research_demo":        ["IEEE", "NeurIPS Foundation", "NASSCOM", "ACM"],
    "prototype_completion": ["Incubation Cell, CIT", "IIC — Institution's Innovation Cell", "Dept. of ECE, CIT"],
    "grant_recognition":    ["BIRAC", "DST India", "MeitY TIDE 2.0", "Atal Innovation Mission"],
    "patent_filing":        ["Indian Patent Office", "USPTO"],
    "publication":          ["IEEE", "ACM", "Springer"],
    "fellowship":           ["PMRF, MHRD", "Google", "Infosys Foundation", "Qualcomm"],
    "award":                ["NASSCOM", "CII", "Inc42 Media", "DRDO"],
}

IMPACT_LEVELS = ["campus", "regional", "national"]

ACHIEVEMENT_NOTES = [
    "Recognised at annual convocation ceremony.",
    "Featured in institution newsletter.",
    "Covered by regional media.",
    "Cited in NIRF Innovation submission.",
    "Led to incubation cell admission.",
    "Resulted in follow-on collaboration with industry partner.",
    "Contributed to NIRF Innovation Achievements count.",
    "Team received ₹50K prize money.",
    "Outcome used as evidence in grant application.",
    "Presented at national-level summit post-win.",
]

# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------

def _random_date(start_year: int = 2019, end_year: int = 2025) -> str:
    start = date(start_year, 1, 1)
    end   = date(end_year, 12, 31)
    return (start + timedelta(days=random.randint(0, (end - start).days))).isoformat()

def _year(start: int = 2019, end: int = 2025) -> int:
    return random.randint(start, end)

# ---------------------------------------------------------------------------
# Generator functions
# ---------------------------------------------------------------------------

def generate_edges(n: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for i in range(1, n + 1):
        edge_type = random.choices(
            EDGE_TYPES,
            weights=[40, 30, 30],
            k=1,
        )[0]

        if edge_type == "mentor_mentee":
            source = _hub_weighted(MEN_IDS, HUB_MEN, hub_weight=8)
            target = _hub_weighted(STU_IDS + ALU_IDS[:50], HUB_STU + HUB_ALU[:4], hub_weight=5)
            src_ctx = random.choice(MENTOR_CONTEXTS)
            tgt_ctx = random.choice(MENTOR_CONTEXTS)

        elif edge_type == "investor_founder":
            source = _hub_weighted(INV_IDS, HUB_INV, hub_weight=8)
            target = _hub_weighted(STU_IDS[:80] + ALU_IDS[:100], HUB_STU[:6] + HUB_ALU[:4], hub_weight=5)
            src_ctx = random.choice(INVESTOR_CONTEXTS)
            tgt_ctx = random.choice(INVESTOR_CONTEXTS)

        else:  # club_membership
            source = _hub_weighted(STU_IDS + ALU_IDS[:60], HUB_STU + HUB_ALU[:3], hub_weight=4)
            target = random.choice(CLB_IDS)
            src_ctx = random.choice(CLUB_CONTEXTS)
            tgt_ctx = random.choice(CLUB_CONTEXTS)

        strength = random.choices(STRENGTH_LEVELS, weights=[30, 45, 25], k=1)[0]
        lo, hi   = STRENGTH_TO_COUNT[strength]

        rows.append({
            "edge_id":                    f"EDG{i:06d}",
            "source_profile_id":          source,
            "target_profile_id":          target,
            "edge_type":                  edge_type,
            "relationship_strength":      strength,
            "interaction_count":          random.randint(lo, hi),
            "first_interaction_context":  src_ctx,
            "last_interaction_context":   tgt_ctx,
            "created_at":                 _random_date(),
        })
    return rows


def generate_competitions(n: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    all_profiles = STU_IDS + ALU_IDS
    for i in range(1, n + 1):
        role   = random.choices(
            PARTICIPATION_ROLES,
            weights=[45, 25, 15, 8, 7],
            k=1,
        )[0]
        result = random.choice(RESULT_BY_ROLE[role])
        rows.append({
            "competition_id":    f"CMP{i:05d}",
            "profile_id":        _hub_weighted(all_profiles, HUB_STU + HUB_ALU, hub_weight=4),
            "competition_name":  random.choice(COMPETITION_NAMES),
            "competition_type":  random.choice(COMPETITION_TYPES),
            "year":              _year(2019, 2025),
            "participation_role": role,
            "result":            result,
            "team_size":         random.randint(1, 5) if role in ("participant", "finalist", "winner") else 0,
            "theme":             random.choice(COMPETITION_THEMES),
        })
    return rows


def generate_achievements(n: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    all_profiles = STU_IDS + ALU_IDS
    for i in range(1, n + 1):
        ach_type = random.choices(
            ACHIEVEMENT_TYPES,
            weights=[18, 15, 12, 8, 10, 10, 7, 7, 7, 6],
            k=1,
        )[0]
        rows.append({
            "achievement_id":  f"ACH{i:06d}",
            "profile_id":      _hub_weighted(all_profiles, HUB_STU + HUB_ALU, hub_weight=4),
            "achievement_type": ach_type,
            "title":           random.choice(ACHIEVEMENT_TITLES[ach_type]),
            "issuing_body":    random.choice(ISSUING_BODIES[ach_type]),
            "year":            _year(2019, 2025),
            "impact_level":    random.choices(
                                   IMPACT_LEVELS,
                                   weights=[50, 30, 20],
                                   k=1,
                               )[0],
            "notes":           random.choice(ACHIEVEMENT_NOTES),
        })
    return rows

# ---------------------------------------------------------------------------
# Graph stats + degree distribution plot
# ---------------------------------------------------------------------------

def compute_graph_stats(edges: list[dict[str, Any]]) -> dict[str, Any]:
    degree: dict[str, int] = collections.Counter()
    edge_type_counts: dict[str, int] = collections.Counter()
    for e in edges:
        degree[e["source_profile_id"]] += 1
        degree[e["target_profile_id"]] += 1
        edge_type_counts[e["edge_type"]] += 1

    degrees      = list(degree.values())
    avg_deg      = sum(degrees) / len(degrees) if degrees else 0
    max_deg      = max(degrees) if degrees else 0
    top_hubs     = [node for node, _ in collections.Counter(degree).most_common(5)]

    return {
        "total_edges":        len(edges),
        "total_unique_nodes": len(degree),
        "edge_type_counts":   dict(edge_type_counts),
        "average_degree":     round(avg_deg, 2),
        "max_degree":         max_deg,
        "top_hub_nodes":      top_hubs,
        "_degree_counts":     degree,   # internal — stripped before JSON write
    }


def plot_degree_distribution(degree: dict[str, int], out_path: Path) -> None:
    values = list(degree.values())

    # Build histogram buckets manually (no numpy/pandas)
    max_d  = max(values)
    n_bins = min(30, max_d + 1)
    bin_w  = math.ceil(max_d / n_bins)
    buckets: dict[int, int] = collections.Counter()
    for v in values:
        buckets[v // bin_w] += 1

    xs = sorted(buckets.keys())
    ys = [buckets[x] for x in xs]
    labels = [str(x * bin_w) for x in xs]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(range(len(xs)), ys, color="#5B7CF6", edgecolor="white", linewidth=0.5)
    ax.set_xticks(range(len(xs)))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    ax.set_xlabel("Node Degree (number of edges)", fontsize=10)
    ax.set_ylabel("Number of Nodes", fontsize=10)
    ax.set_title(
        "Degree Distribution Sanity Check — Campus Ecosystem Interaction Graph\n"
        "(Should show hub-and-spoke shape: few high-degree nodes, many low-degree)",
        fontsize=10,
        pad=14,
    )
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    plt.savefig(out_path, dpi=120)
    plt.close(fig)
    print(f"  ✓ {out_path.name}")

# ---------------------------------------------------------------------------
# Writers
# ---------------------------------------------------------------------------

def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"  ✓ {path.name}  ({len(rows)} rows)")


def write_json(path: Path, obj: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
    print(f"  ✓ {path.name}")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("Campus Innovation & Engagement Intelligence Hub")
    print("Phase 1 — Interaction Data Generator\n")

    edges        = generate_edges(NUM_EDGES)
    competitions = generate_competitions(NUM_COMPETITIONS)
    achievements = generate_achievements(NUM_ACHIEVEMENTS)

    write_csv(OUTPUT_DIR / "interaction_edges.csv",    edges)
    write_csv(OUTPUT_DIR / "competition_records.csv",  competitions)
    write_csv(OUTPUT_DIR / "achievement_records.csv",  achievements)

    stats  = compute_graph_stats(edges)
    degree = stats.pop("_degree_counts")   # remove internal field before JSON

    plot_degree_distribution(degree, OUTPUT_DIR / "degree_distribution.png")

    summary = {
        "project": "Campus Innovation & Engagement Intelligence Hub",
        "phase":   "1 — Synthetic Data Foundation",
        "seed":    SEED,
        "generated_files": {
            "interaction_edges.csv":   len(edges),
            "competition_records.csv": len(competitions),
            "achievement_records.csv": len(achievements),
        },
        "graph_stats": stats,
        "note": "Entirely synthetic data. No real PII. Safe for build and demo.",
    }
    write_json(OUTPUT_DIR / "interaction_generation_summary.json", summary)

    print(f"\nGraph stats: {stats['total_unique_nodes']} nodes | "
          f"{stats['total_edges']} edges | "
          f"avg degree {stats['average_degree']} | "
          f"max degree {stats['max_degree']}")
    print(f"Top hub nodes: {', '.join(stats['top_hub_nodes'])}")
    print(f"\nAll files written to: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()