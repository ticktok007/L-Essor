"""
generate_ecosystem_data.py
Campus Innovation & Engagement Intelligence Hub — Phase 1 (updated Day 15)

Structured skills format added: each skill is now a dict with
confidence=0.10 (self-declared baseline) ready for Phase 6 NER upgrades.
"""

import csv
import json
import random
from pathlib import Path

from faker import Faker

SEED = 42
random.seed(SEED)

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "synthetic"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NUM_STUDENTS          = 300
NUM_ALUMNI            = 200
NUM_INVESTORS_MENTORS = 100

DEPARTMENTS = [
    "Computer Science & Engineering",
    "Electronics & Communication Engineering",
    "Mechanical Engineering",
    "Civil Engineering",
    "Information Technology",
    "Electrical Engineering",
    "Biotechnology",
    "Chemical Engineering",
    "Artificial Intelligence & Machine Learning",
    "Data Science & Business Analytics",
]

DEGREES = {
    "Computer Science & Engineering":              "B.E. Computer Science & Engineering",
    "Electronics & Communication Engineering":     "B.E. Electronics & Communication Engineering",
    "Mechanical Engineering":                      "B.E. Mechanical Engineering",
    "Civil Engineering":                           "B.E. Civil Engineering",
    "Information Technology":                      "B.Tech Information Technology",
    "Electrical Engineering":                      "B.E. Electrical Engineering",
    "Biotechnology":                               "B.Tech Biotechnology",
    "Chemical Engineering":                        "B.E. Chemical Engineering",
    "Artificial Intelligence & Machine Learning":  "B.E. Computer Science & Engineering (AI/ML)",
    "Data Science & Business Analytics":           "B.Tech Data Science & Business Analytics",
}

SKILL_POOL = [
    "Python", "Java", "C++", "JavaScript", "TypeScript", "React", "Node.js",
    "Django", "FastAPI", "Flask", "Machine Learning", "Deep Learning",
    "Natural Language Processing", "Computer Vision", "Data Analysis",
    "SQL", "PostgreSQL", "MongoDB", "Redis", "Docker", "Kubernetes",
    "AWS", "GCP", "Azure", "TensorFlow", "PyTorch", "scikit-learn",
    "Pandas", "NumPy", "OpenCV", "Embedded Systems", "VLSI Design",
    "CAD/CAM", "IoT", "Blockchain", "Cybersecurity", "Networking",
    "Android Development", "iOS Development", "Flutter", "UI/UX Design",
    "Figma", "Agile", "Product Management", "Business Analysis",
    "Financial Modelling", "Market Research", "Public Speaking",
    "Technical Writing", "Research & Development",
]

SECTORS = [
    "HealthTech", "EdTech", "FinTech", "AgriTech", "CleanTech",
    "DeepTech", "SaaS", "E-Commerce", "LogisticsTech", "HRTech",
    "CyberSecurity", "AI/ML Infrastructure", "BioTech", "SpaceTech",
    "GovTech", "LegalTech", "RetailTech", "ManufacturingTech",
]

EXPERTISE_TAGS_POOL = [
    "Product Strategy", "Fundraising", "Go-to-Market", "B2B Sales",
    "Deep Tech", "Hardware", "Regulatory Affairs", "Clinical Trials",
    "Financial Modelling", "Supply Chain", "Marketing", "Brand Building",
    "Enterprise SaaS", "Developer Tools", "Open Source", "Community Building",
    "Impact Investing", "ESG", "Angel Investing", "Venture Capital",
    "Team Building", "Leadership Coaching", "Design Thinking",
    "Lean Startup", "OKR Frameworks", "International Expansion",
]

COMPANIES = [
    "Infosys", "TCS", "Wipro", "HCL Technologies", "Tech Mahindra",
    "Cognizant", "Accenture", "IBM India", "Oracle India", "SAP Labs India",
    "Microsoft India", "Google India", "Amazon India", "Flipkart",
    "Zoho Corporation", "Freshworks", "PhonePe", "Razorpay", "CRED",
    "Swiggy", "Zomato", "Ola", "Paytm", "BYJU'S", "Unacademy",
    "Meesho", "BrowserStack", "Postman", "HashedIn", "Sigmoid",
    "ThoughtWorks", "Mphasis", "LTIMindtree", "Persistent Systems",
]

TITLES = [
    "Software Engineer", "Senior Software Engineer", "Data Scientist",
    "Data Engineer", "Product Manager", "Associate Product Manager",
    "ML Engineer", "DevOps Engineer", "Full Stack Developer",
    "Frontend Developer", "Backend Developer", "Engineering Manager",
    "Technical Lead", "Solutions Architect", "Research Scientist",
    "Business Analyst", "Consultant", "Senior Consultant",
    "Co-Founder & CTO", "Co-Founder & CEO", "VP Engineering",
]

ENGAGEMENT_PREFERENCES = [
    "office_hours", "async_review", "warm_intro", "advisory_sessions",
]

MANDATE_TEMPLATES = [
    "Looking to back early-stage {sector} startups with strong technical founders and a clear path to $1M ARR.",
    "Focused on {sector} and {sector2} opportunities at the pre-seed and seed stage.",
    "Investing in {sector} companies solving real-world problems in India and Southeast Asia.",
    "Passionate about {sector} and the intersection of AI with traditional industries.",
    "Sector-agnostic but deeply interested in {sector} and {sector2}.",
    "Supporting {sector} founders building for Bharat. Prefer B2B SaaS models.",
    "Deep operational experience in {sector}. Happy to mentor or invest at pre-seed.",
]

MENTOR_MANDATE_TEMPLATES = [
    "Happy to mentor early-stage founders on {tag} and {tag2}. Prefer weekly async check-ins.",
    "Offering guidance on {tag} for student entrepreneurs and early incubatees.",
    "Available for advisory sessions on {tag}, {tag2}, and navigating the Indian startup ecosystem.",
    "Mentoring founders on {tag} with a focus on first-principles thinking.",
    "Open to mentoring student startups on {tag} and {tag2}.",
]

CURRENT_STATUSES = [
    "Final Year Student", "3rd Year Student", "2nd Year Student",
    "Research Intern", "Summer Intern", "Startup Founder",
    "Project Researcher", "Club Lead",
]

fake = Faker("en_IN")
Faker.seed(SEED)


# ── Structured skills helper ───────────────────────────────────────────────────

def _structured_skills(n: int = 5) -> str:
    """
    Returns a JSON string representing a list of skill dicts.
    Each skill starts with confidence=0.10 (self-declared baseline).
    Schema is forward-compatible with Phase 6 NER upgrades which will
    add evidence entries and raise confidence scores.

    Format:
    [
      {
        "skill": "Python",
        "confidence": 0.10,
        "level": "unknown",
        "sources": ["self_declared"]
      },
      ...
    ]
    """
    selected = random.sample(SKILL_POOL, min(n, len(SKILL_POOL)))
    skill_list = [
        {
            "skill":      s,
            "confidence": 0.10,
            "level":      "unknown",    # upgraded to beginner/intermediate/advanced in Phase 6
            "sources":    ["self_declared"],
        }
        for s in selected
    ]
    return json.dumps(skill_list)


def _expertise(n: int = 4) -> str:
    return "|".join(random.sample(EXPERTISE_TAGS_POOL, min(n, len(EXPERTISE_TAGS_POOL))))


def _sectors(n: int = 2) -> list[str]:
    return random.sample(SECTORS, n)


def _cohort_and_grad(is_student: bool) -> tuple[str, int]:
    entry = random.randint(2022, 2025) if is_student else random.randint(2008, 2021)
    grad  = entry + 4
    return f"{entry}–{grad}", grad


def _employment_history(current_company: str, current_title: str, n_past: int = 2) -> str:
    history = []
    for _ in range(n_past):
        history.append({
            "company": random.choice(COMPANIES),
            "title":   random.choice(TITLES),
            "years":   str(random.randint(1, 4)),
        })
    history.append({
        "company": current_company,
        "title":   current_title,
        "years":   f"{random.randint(1, 5)} (current)",
    })
    return json.dumps(history)


def _check_size() -> int:
    return random.choice([0, 500_000, 1_000_000, 2_500_000, 5_000_000, 10_000_000, 25_000_000])


def _mandate(role: str, sectors: list[str], expertise: list[str], check_inr: int) -> str:
    if role == "investor":
        template  = random.choice(MANDATE_TEMPLATES)
        check_lbl = str(check_inr // 100_000) if check_inr else "10"
        s1, s2    = (sectors + sectors)[:2]
        return (template
                .replace("{sector}", s1)
                .replace("{sector2}", s2)
                .replace("{check}", check_lbl))
    template = random.choice(MENTOR_MANDATE_TEMPLATES)
    t1 = expertise[0] if expertise else "Product Strategy"
    t2 = expertise[1] if len(expertise) > 1 else "Fundraising"
    return template.replace("{tag}", t1).replace("{tag2}", t2)


# ── Generators ────────────────────────────────────────────────────────────────

def generate_students(n: int) -> list[dict]:
    rows = []
    for i in range(1, n + 1):
        dept   = random.choice(DEPARTMENTS)
        cohort, grad_year = _cohort_and_grad(is_student=True)
        rows.append({
            "student_id":       f"STU{i:05d}",
            "full_name":        fake.name(),
            "email":            fake.unique.email(),
            "role":             "student",
            "cohort":           cohort,
            "department":       dept,
            "degree":           DEGREES[dept],
            "graduation_year":  grad_year,
            "current_status":   random.choice(CURRENT_STATUSES),
            # Structured JSON skills — confidence 0.10 baseline, Phase 6 upgrades later
            "skills":           _structured_skills(random.randint(3, 7)),
            "achievements_count": random.randint(0, 12),
        })
    return rows


def generate_alumni(n: int) -> list[dict]:
    rows = []
    for i in range(1, n + 1):
        dept    = random.choice(DEPARTMENTS)
        cohort, grad_year = _cohort_and_grad(is_student=False)
        company = random.choice(COMPANIES)
        title   = random.choice(TITLES)
        rows.append({
            "alumni_id":          f"ALM{i:05d}",
            "full_name":          fake.name(),
            "email":              fake.unique.email(),
            "role":               "alumni",
            "cohort":             cohort,
            "department":         dept,
            "degree":             DEGREES[dept],
            "graduation_year":    grad_year,
            "current_company":    company,
            "current_title":      title,
            "employment_history": _employment_history(company, title,
                                                       n_past=random.randint(1, 3)),
            # Structured JSON skills — confidence 0.10 baseline, Phase 6 upgrades later
            "skills":             _structured_skills(random.randint(4, 8)),
            "mentorship_interest": random.choice(["yes", "no", "maybe"]),
        })
    return rows


def generate_investors_mentors(n: int) -> list[dict]:
    rows = []
    for i in range(1, n + 1):
        role     = "investor" if i <= n // 2 else "mentor"
        sectors  = _sectors(2)
        exp_list = random.sample(EXPERTISE_TAGS_POOL, 4)
        check    = _check_size() if role == "investor" else 0
        rows.append({
            "profile_id":          f"INV{i:05d}" if role == "investor" else f"MEN{i:05d}",
            "full_name":           fake.name(),
            "email":               fake.unique.email(),
            "role":                role,
            "organization":        fake.company(),
            "sector_focus":        "|".join(sectors),
            "check_size_inr":      check,
            "expertise_tags":      "|".join(exp_list),
            "mandate_text":        _mandate(role, sectors, exp_list, check),
            "engagement_preference": random.choice(ENGAGEMENT_PREFERENCES),
        })
    return rows


# ── Writers ────────────────────────────────────────────────────────────────────

def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"  ✓ {path.name}  ({len(rows)} rows)")


def write_summary(path: Path, counts: dict[str, int]) -> None:
    summary = {
        "project":         "Campus Innovation & Engagement Intelligence Hub",
        "phase":           "1 — Synthetic Data Foundation",
        "seed":            SEED,
        "skills_format":   "structured_json_v1",
        "skills_note":     (
            "Each skill is a dict with confidence=0.10 (self-declared baseline). "
            "Phase 6 NER pipeline upgrades confidence when certificate evidence found. "
            "Phase 7 mentor endorsement adds further confidence boosts."
        ),
        "generated_files": counts,
        "total_records":   sum(counts.values()),
        "note":            "Entirely synthetic data. No real PII. Safe for build and demo.",
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"  ✓ {path.name}")


def main() -> None:
    print("Campus Innovation & Engagement Intelligence Hub")
    print("Phase 1 — Synthetic Data Generator (skills: structured JSON v1)\n")

    students = generate_students(NUM_STUDENTS)
    alumni   = generate_alumni(NUM_ALUMNI)
    inv_men  = generate_investors_mentors(NUM_INVESTORS_MENTORS)

    write_csv(OUTPUT_DIR / "student_profiles.csv",          students)
    write_csv(OUTPUT_DIR / "alumni_profiles.csv",           alumni)
    write_csv(OUTPUT_DIR / "investor_mentor_profiles.csv",  inv_men)

    write_summary(
        OUTPUT_DIR / "generation_summary.json",
        {
            "student_profiles.csv":         len(students),
            "alumni_profiles.csv":          len(alumni),
            "investor_mentor_profiles.csv": len(inv_men),
        },
    )

    print(f"\nAll files written to: {OUTPUT_DIR.resolve()}")
    print("\nSkills format: structured JSON with confidence=0.10 baseline")
    print("Example skill entry:")
    import json as _json
    sample = _json.loads(students[0]["skills"])[0]
    print(f"  {_json.dumps(sample, indent=4)}")


if __name__ == "__main__":
    main()