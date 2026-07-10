"""
generate_startup_data.py
Campus Innovation & Engagement Intelligence Hub
Phase 1 — Synthetic Data Foundation: Startup Records

Generates four CSVs and one JSON summary into data/synthetic/.
Run with: python generate_startup_data.py

Requirements: pip install faker
Python 3.11+
"""

import csv
import json
import random
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from faker import Faker

# ---------------------------------------------------------------------------
# Seed + output config
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

NUM_STARTUPS = 120

# ---------------------------------------------------------------------------
# Domain vocabularies
# ---------------------------------------------------------------------------

SECTORS = [
    "HealthTech", "EdTech", "FinTech", "AgriTech", "CleanTech",
    "LogisticsTech", "HRTech", "DeepTech", "GovTech", "RetailTech",
    "CyberSecurity", "BioTech",
]

SUBSECTORS = {
    "HealthTech":     ["Telemedicine", "Hospital Management", "Mental Health", "Diagnostics", "Wearables"],
    "EdTech":         ["Skill Development", "K-12 Tutoring", "Higher Education", "Corporate Training", "Test Prep"],
    "FinTech":        ["Lending", "Insurance Tech", "Payments", "Wealth Management", "Credit Scoring"],
    "AgriTech":       ["Precision Farming", "Supply Chain", "Crop Insurance", "Market Linkage", "Soil Analytics"],
    "CleanTech":      ["Solar Energy", "Waste Management", "EV Charging", "Carbon Credits", "Water Tech"],
    "LogisticsTech":  ["Last-Mile Delivery", "Fleet Management", "Cold Chain", "Warehouse Automation", "Freight Matching"],
    "HRTech":         ["Recruitment", "Payroll", "Employee Engagement", "Performance Management", "Upskilling"],
    "DeepTech":       ["Computer Vision", "NLP", "Robotics", "Quantum Computing", "Edge AI"],
    "GovTech":        ["e-Governance", "Digital Identity", "Smart City", "Public Health", "Tax Tech"],
    "RetailTech":     ["D2C", "Inventory Management", "Loyalty Platforms", "AR Commerce", "ONDC Integration"],
    "CyberSecurity":  ["Zero Trust", "Threat Intelligence", "Identity Management", "SOC Automation", "API Security"],
    "BioTech":        ["Genomics", "Drug Discovery", "Bioinformatics", "AgBio", "Synthetic Biology"],
}

FUNDING_STAGES = ["pre-seed", "seed", "grant", "series-a", "bootstrapped"]

# TRL range per funding stage — (min, max)
TRL_BY_STAGE = {
    "pre-seed":     (1, 3),
    "seed":         (3, 5),
    "grant":        (2, 5),
    "series-a":     (6, 8),
    "bootstrapped": (4, 7),
}

HQ_CITIES = [
    "Chennai", "Bengaluru", "Hyderabad", "Mumbai", "Pune",
    "Delhi", "Coimbatore", "Ahmedabad", "Kochi", "Jaipur",
]

TRACTION_BY_STAGE = {
    "pre-seed":     [
        "MVP in development; 15 design-partner interviews completed.",
        "Concept validated with 30 potential users via surveys.",
        "Prototype demoed at college tech fest; 3 LOIs collected.",
        "Problem validated; no paying customers yet.",
    ],
    "seed":         [
        "50 paying customers; ₹3L MRR growing 15% month-over-month.",
        "Pilot live with 2 SME clients; 92% retention over 3 months.",
        "120 beta users; NPS score 68; waitlist of 400.",
        "₹8L MRR; partnerships with 2 district hospitals signed.",
    ],
    "grant":        [
        "BIRAC BIG grant recipient; prototype validation underway.",
        "DST-NIDHI PRAYAS grant sanctioned; lab trials in progress.",
        "TIDE 2.0 cohort member; 6-month pilot with state government.",
        "AIM-iCREATE grant; product under regulatory review.",
    ],
    "series-a":     [
        "₹2.4Cr ARR; 30-member team; Series A of ₹12Cr closed.",
        "1,200 enterprise clients; expanding to 3 new states.",
        "₹5Cr ARR; DPIIT-recognised startup; international pilots live.",
        "B2B SaaS with ₹3.8Cr ARR and 110% net revenue retention.",
    ],
    "bootstrapped": [
        "Profitable from month 8; ₹1.2Cr ARR; zero external funding.",
        "Self-funded; 80 clients; growing via word-of-mouth.",
        "Bootstrap journey: ₹90L revenue in year 2; no debt.",
        "Founder-funded through consulting revenue; now product-led.",
    ],
}

FOUNDER_ROLES = ["CEO", "CTO", "CPO", "COO", "CMO", "CFO", "Head of Engineering", "Lead Scientist"]
FOUNDER_TITLES = {
    "CEO": ["Co-Founder & CEO", "Founder & CEO"],
    "CTO": ["Co-Founder & CTO", "Founder & CTO", "Co-Founder & Head of Technology"],
    "CPO": ["Co-Founder & CPO", "Co-Founder & Head of Product"],
    "COO": ["Co-Founder & COO", "Co-Founder & Head of Operations"],
    "CMO": ["Co-Founder & CMO", "Co-Founder & Head of Growth"],
    "CFO": ["Co-Founder & CFO"],
    "Head of Engineering": ["Co-Founder & Engineering Lead"],
    "Lead Scientist": ["Co-Founder & Chief Scientist", "Co-Founder & Research Lead"],
}
OWNERSHIP_BANDS = ["10–15%", "15–20%", "20–25%", "25–30%", "30–40%", "40–50%"]

FUNDING_EVENT_TYPES = [
    "incubated", "grant_received", "prototype_built", "pilot_signed",
    "angel_round", "revenue_milestone", "demo_day", "pre_seed_round",
    "seed_round", "series_a_round", "product_launched",
]

MILESTONE_NOTES = {
    "incubated":         ["Admitted to {inst} incubation centre.", "Selected for {inst} cohort {year}.", "Joined {inst} pre-incubation programme."],
    "grant_received":    ["Received ₹{amt}L BIRAC BIG grant.", "DST-NIDHI PRAYAS grant of ₹{amt}L sanctioned.", "TIDE 2.0 grant of ₹{amt}L disbursed.", "AIM-iCREATE grant of ₹{amt}L awarded."],
    "prototype_built":   ["Working prototype demonstrated to {n} pilot users.", "Hardware prototype passed bench tests.", "MVP built and tested internally."],
    "pilot_signed":      ["Pilot agreement signed with {org}.", "MoU executed with {org} for 3-month trial.", "LOI received from {n} SME clients."],
    "angel_round":       ["Angel round of ₹{amt}L closed with {n} angels.", "₹{amt}L raised from alumni angel network."],
    "revenue_milestone": ["First paying customer onboarded at ₹{amt}K/month.", "₹{amt}L ARR milestone crossed.", "Reached ₹{amt}L MRR."],
    "demo_day":          ["Presented at {inst} Demo Day; selected top-3 startup.", "Pitched at {inst} Investor Summit.", "Showcased at Smart India Hackathon finals."],
    "pre_seed_round":    ["Pre-seed round of ₹{amt}L closed.", "₹{amt}L raised at pre-seed from {n} investors."],
    "seed_round":        ["Seed round of ₹{amt}L closed.", "₹{amt}L seed investment from VC firm."],
    "series_a_round":    ["Series A of ₹{amt}Cr closed.", "₹{amt}Cr Series A led by institutional VC."],
    "product_launched":  ["Product launched on App Store and Play Store.", "SaaS platform went live; 50 sign-ups on day one.", "Public beta launched; 200 waitlist converts."],
}

INSTITUTIONS = ["IIT Madras", "NIT Trichy", "Anna University", "IIMB", "NSRCEL", "T-Hub", "CIIE.CO", "Forge"]
ORGS = ["Apollo Hospitals", "Titan Company", "BSNL", "National Skill Development Corporation",
        "Tamil Nadu e-Governance Agency", "SBI", "Ola", "Indian Railways", "BPCL", "Jio Platforms"]

# ---------------------------------------------------------------------------
# Vocabulary bank
# ---------------------------------------------------------------------------

VOCAB_BANK: list[dict[str, str]] = []

RAW_VOCAB: dict[str, dict[str, list[str]]] = {
    "HealthTech": {
        "problem":    ["Rural patients travel 80+ km for specialist consultations.", "Paper-based health records cause critical diagnostic delays.", "60% of chronic disease patients miss follow-up appointments.", "Mental health support is inaccessible in Tier-2 cities."],
        "solution":   ["AI-powered triage chatbot triages patients before specialist consult.", "Unified digital health record accessible across providers.", "Automated follow-up reminders via WhatsApp and IVR.", "On-demand video therapy with licensed clinical psychologists."],
        "customer":   ["Primary healthcare centres in semi-urban districts.", "District hospitals seeking digital transformation.", "Corporate HR teams managing employee wellness.", "Health-insurance companies reducing claims via preventive care."],
        "moat":       ["Proprietary symptom-to-disease ML model trained on 2M Indian records.", "Exclusive partnerships with 40 district hospitals.", "WhatsApp-native UX requiring zero app download.", "ABDM-compliant data layer ensuring regulatory fit."],
        "traction":   ["Serving 3,200 patients/month across 6 districts.", "Integrated with 14 PHCs; 91% patient satisfaction.", "₹6L MRR; 22% month-over-month growth."],
        "technology": ["ABDM-compliant FHIR APIs", "CNN-based X-ray diagnostic model", "NLP symptom extraction", "Federated learning for privacy-preserving analytics"],
    },
    "EdTech": {
        "problem":    ["First-generation learners cannot afford quality JEE/NEET coaching.", "College placement rates drop below 40% for non-metro engineering graduates.", "Upskilling programmes have 70% dropout rates due to poor engagement.", "School teachers lack tools to identify slow learners early."],
        "solution":   ["Affordable live-cohort JEE prep with AI-adaptive mock tests.", "Industry-linked micro-credential programmes with guaranteed interviews.", "Gamified skill tracks with peer accountability pods.", "AI-based learning-gap detector embedded in existing school LMS."],
        "customer":   ["Class 11–12 students in Tier-2 and Tier-3 cities.", "Engineering graduates seeking IT placements.", "Working professionals upskilling for data science roles.", "Government school teachers in rural districts."],
        "moat":       ["Vernacular content library in 6 Indian languages.", "Placement-outcome data from 8,000 alumni powering job-match algorithm.", "Partnerships with 120 companies for direct hiring.", "Adaptive engine built on 4 years of proprietary learning-path data."],
        "traction":   ["4,500 active learners; 78% course completion rate.", "180 placement partners; ₹3.2L MRR.", "3 state government pilots covering 900 schools."],
        "technology": ["Adaptive learning engine", "NLP-based doubt resolution", "Video-compression for low-bandwidth delivery", "Proctored online assessment"],
    },
    "FinTech": {
        "problem":    ["60% of MSMEs are rejected by formal credit channels due to thin credit files.", "Gig workers have no access to micro-insurance products.", "Rural households lose 20% of savings to informal money lenders.", "B2B invoice settlement delays strangle MSME cash flow."],
        "solution":   ["Alternative credit scoring using GST, UPI, and utility payment history.", "Pay-per-use micro-insurance embedded at point of gig-work assignment.", "NBFC-backed savings and credit product distributed via SHGs.", "Automated invoice discounting platform integrated with Tally and Zoho Books."],
        "customer":   ["MSMEs with annual turnover under ₹5Cr.", "Food-delivery and ride-share gig workers.", "Self-Help Groups in rural Maharashtra and Tamil Nadu.", "Small manufacturers needing working-capital liquidity."],
        "moat":       ["Bureau-plus-alternative-data underwriting model with 3.2% NPA at 18 months.", "Insurance regulator (IRDAI) sandbox approval for micro-insurance product.", "Co-lending partnership with 2 scheduled commercial banks.", "Real-time GST data integration via NIC API."],
        "traction":   ["₹12Cr loan book; 3.2% NPA; 900 active borrowers.", "18,000 gig workers insured; claim TAT 4 hours.", "₹4L MRR; NBFC partnership signed."],
        "technology": ["Account aggregator framework", "RBI-compliant data localisation", "ML-based fraud detection", "GST analytics pipeline"],
    },
    "AgriTech": {
        "problem":    ["Smallholder farmers receive 30% of consumer price for produce.", "Crop losses from pest infestation average 18% due to late detection.", "Agricultural credit is unavailable without land-title collateral.", "Post-harvest losses exceed 25% in perishable supply chains."],
        "solution":   ["FPO-linked direct market platform eliminating 3 layers of commission agents.", "Satellite and drone imagery with ML pest-detection alerting farmers 10 days early.", "Warehouse receipt financing using stored grain as collateral.", "IoT-enabled cold-chain monitoring with real-time temperature alerts."],
        "customer":   ["Smallholder farmers with 1–5 acres in Karnataka and Tamil Nadu.", "FPOs managing 500+ farmer members.", "Food processing companies needing traceable raw material supply.", "State agriculture departments running subsidy programmes."],
        "moat":       ["Ground-truth crop-disease dataset from 12,000 farm visits.", "Exclusive tie-up with 3 state warehousing corporations.", "Soil health card integration via government API.", "Last-mile network of 200 village-level tech entrepreneurs."],
        "traction":   ["6,000 farmer onboardings; ₹2.8Cr GMV in season 1.", "18 FPOs; 90-day pilot with state horticulture board.", "₹1.2Cr MRR; 14% post-harvest loss reduction reported by pilot farmers."],
        "technology": ["Multispectral satellite imagery", "IoT soil sensors", "Blockchain traceability", "Feature phone USSD interface"],
    },
    "CleanTech": {
        "problem":    ["Commercial rooftops capture less than 8% of viable solar potential.", "Municipal solid waste processing costs ₹1,800/tonne yet yields no revenue.", "EV charging deserts exist across National Highway corridors.", "Industrial units lack real-time visibility into energy wastage."],
        "solution":   ["Asset-light rooftop solar leasing model with zero upfront cost for SMEs.", "Waste-to-compost and RDF platform connecting municipalities with cement plants.", "Modular fast-charging hubs deployed at highway dhabas via franchise model.", "IoT energy-monitoring dashboard with ML anomaly detection for factories."],
        "customer":   ["SMEs with rooftop area over 2,000 sq ft.", "Municipal corporations processing 50–200 TPD of waste.", "Highway dhaba and hotel chains.", "Manufacturing units with monthly electricity bill above ₹5L."],
        "moat":       ["DISCOM-agnostic net-metering integration across 9 states.", "Proprietary RDF quality-certification accepted by 4 cement majors.", "FAME-II subsidy pass-through reducing charger capex 40%.", "Energy-savings performance contract with guaranteed ROI."],
        "traction":   ["3.2 MW solar deployed; ₹1.8Cr ARR.", "8 municipality contracts; 120 TPD waste processed.", "42 charging points live; ₹90L revenue in Q1.", "34 factory clients; average 18% energy cost reduction."],
        "technology": ["IoT power monitoring", "SCADA integration", "Digital twin for energy simulation", "Satellite rooftop area detection"],
    },
    "DeepTech": {
        "problem":    ["Quality inspection on manufacturing lines misses 12% of defects using manual visual checks.", "Indian-language voice interfaces fail below 70% accuracy on regional dialects.", "Predictive maintenance alerts arrive after failure, not before.", "Medical imaging diagnosis queues in public hospitals average 11 days."],
        "solution":   ["Edge-deployed computer vision model for zero-defect PCB and textile inspection.", "Dialect-aware ASR model fine-tuned on 900 hours of regional audio.", "Vibration-sensor ML pipeline predicting motor failures 72 hours ahead.", "AI radiology assistant prioritising critical findings in chest X-rays within 30 seconds."],
        "customer":   ["Automotive Tier-1 suppliers with high-volume assembly lines.", "State government digital-service kiosks serving non-literate citizens.", "Heavy industry plants with critical rotating machinery.", "Public district hospitals with radiology departments."],
        "moat":       ["Proprietary dataset of 480K labelled defect images across 6 product categories.", "Patented dialect normalisation layer improving WER by 34%.", "Physics-informed ML model reducing false-positive maintenance alerts by 60%.", "CDSCO medical device registration in progress; CE mark filed."],
        "traction":   ["Deployed at 3 Tier-1 auto plants; 0.3% defect escape rate.", "1.2M voice transactions/month at government kiosks.", "8 plants; prevented 14 unplanned shutdowns in 6 months.", "Pilot at 4 district hospitals; 94% radiologist agreement rate."],
        "technology": ["Edge inference on NVIDIA Jetson", "Transformer-based ASR", "FFT vibration analytics", "DICOM-compliant imaging pipeline"],
    },
}

# Flatten vocab bank into list of dicts
def _build_vocab_bank() -> list[dict[str, str]]:
    rows = []
    vid = 1
    for sector, phrase_types in RAW_VOCAB.items():
        for phrase_type, phrases in phrase_types.items():
            for phrase in phrases:
                rows.append({
                    "vocab_id": f"VOC{vid:05d}",
                    "sector": sector,
                    "phrase_type": phrase_type,
                    "phrase": phrase,
                })
                vid += 1
    return rows


def _vocab_phrase(sector: str, phrase_type: str) -> str:
    """Return a random phrase for the given sector and type, with broad fallback."""
    candidates = [
        r["phrase"] for r in VOCAB_BANK
        if r["sector"] == sector and r["phrase_type"] == phrase_type
    ]
    if not candidates:
        candidates = [
            r["phrase"] for r in VOCAB_BANK
            if r["phrase_type"] == phrase_type
        ]
    return random.choice(candidates) if candidates else f"[{phrase_type} placeholder]"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _trl(stage: str) -> int:
    lo, hi = TRL_BY_STAGE[stage]
    return random.randint(lo, hi)


def _founded_year(stage: str) -> int:
    current = date.today().year
    windows = {
        "pre-seed":     (current - 1, current),
        "seed":         (current - 3, current - 1),
        "grant":        (current - 2, current - 1),
        "series-a":     (current - 5, current - 2),
        "bootstrapped": (current - 4, current - 1),
    }
    lo, hi = windows.get(stage, (current - 3, current - 1))
    return random.randint(lo, hi)


def _pitch_summary(sector: str, stage: str) -> str:
    problem = _vocab_phrase(sector, "problem")
    solution = _vocab_phrase(sector, "solution")
    moat = _vocab_phrase(sector, "moat")
    return f"{problem} {solution} {moat}"


def _problem_statement(sector: str) -> str:
    return _vocab_phrase(sector, "problem")


def _solution_summary(sector: str) -> str:
    return _vocab_phrase(sector, "solution")


def _traction(stage: str) -> str:
    return random.choice(TRACTION_BY_STAGE.get(stage, TRACTION_BY_STAGE["pre-seed"]))


def _random_date_after(after: date, max_days_ahead: int = 400) -> date:
    return after + timedelta(days=random.randint(30, max_days_ahead))


def _milestone(event_type: str, year: int) -> tuple[str, int]:
    """Returns (milestone_note, amount_inr)."""
    templates = MILESTONE_NOTES.get(event_type, ["Milestone achieved."])
    tpl = random.choice(templates)
    amt_l = random.choice([5, 10, 15, 20, 25, 30, 50])   # lakhs
    amt_k = random.choice([10, 20, 30, 50])               # thousands
    amt_cr = random.choice([1, 2, 3, 5, 8, 12])           # crores
    note = (
        tpl
        .replace("{inst}", random.choice(INSTITUTIONS))
        .replace("{org}", random.choice(ORGS))
        .replace("{n}", str(random.randint(2, 10)))
        .replace("{year}", str(year))
        .replace("{amt}Cr", str(amt_cr))
        .replace("{amt}L", str(amt_l))
        .replace("{amt}K", str(amt_k))
        .replace("{amt}", str(amt_l))
    )
    # Determine INR amount
    inr = 0
    if "Cr" in tpl and "{amt}Cr" in tpl:
        inr = amt_cr * 10_000_000
    elif "L" in tpl and "{amt}L" in tpl:
        inr = amt_l * 100_000
    elif "K" in tpl and "{amt}K" in tpl:
        inr = amt_k * 1_000
    return note, inr


def _events_for_stage(stage: str) -> list[str]:
    """Return an ordered event-type sequence appropriate for the stage."""
    base = ["incubated", "prototype_built"]
    progressions = {
        "pre-seed":     base,
        "grant":        ["incubated", "grant_received", "prototype_built"],
        "seed":         base + ["demo_day", "pilot_signed", "pre_seed_round", "product_launched"],
        "series-a":     base + ["demo_day", "pilot_signed", "pre_seed_round", "product_launched", "revenue_milestone", "seed_round", "series_a_round"],
        "bootstrapped": ["incubated", "prototype_built", "product_launched", "revenue_milestone"],
    }
    return progressions.get(stage, base)


# ---------------------------------------------------------------------------
# Generators
# ---------------------------------------------------------------------------

def generate_startups(n: int) -> tuple[list[dict], list[dict], list[dict]]:
    """Returns (startup_profiles, founder_links, funding_events)."""
    profiles: list[dict] = []
    founder_links: list[dict] = []
    funding_events: list[dict] = []
    link_id = 1
    event_id = 1

    for i in range(1, n + 1):
        sid = f"STA{i:05d}"
        sector = random.choice(SECTORS)
        subsector = random.choice(SUBSECTORS[sector])
        stage = random.choices(
            FUNDING_STAGES,
            weights=[30, 25, 20, 10, 15],
            k=1,
        )[0]
        trl = _trl(stage)
        founded = _founded_year(stage)
        founder_count = random.randint(1, 3) if stage == "pre-seed" else random.randint(2, 4)

        # -- Startup profile --
        profiles.append({
            "startup_id":        sid,
            "startup_name":      f"{fake.last_name()} {random.choice(['Tech', 'AI', 'Labs', 'Solutions', 'Platforms', 'Systems', 'Ventures', 'Innovations'])}",
            "sector":            sector,
            "subsector":         subsector,
            "funding_stage":     stage,
            "trl_level":         trl,
            "founded_year":      founded,
            "hq_city":           random.choice(HQ_CITIES),
            "team_size":         random.randint(2, 8) if stage in ("pre-seed", "grant") else random.randint(6, 35),
            "pitch_summary":     _pitch_summary(sector, stage),
            "problem_statement": _problem_statement(sector),
            "solution_summary":  _solution_summary(sector),
            "traction_signal":   _traction(stage),
            "founder_count":     founder_count,
        })

        # -- Founder links --
        used_roles: set[str] = set()
        for j in range(founder_count):
            role = random.choice([r for r in FOUNDER_ROLES if r not in used_roles] or FOUNDER_ROLES)
            used_roles.add(role)
            # Alternate between student and alumni IDs
            prefix = random.choice(["STU", "ALU"])
            f_id = f"{prefix}-{random.randint(1, 300 if prefix == 'STU' else 200):04d}"
            founder_links.append({
                "link_id":            f"FL{link_id:05d}",
                "startup_id":         sid,
                "founder_profile_id": f_id,
                "founder_role":       role,
                "founder_title":      random.choice(FOUNDER_TITLES[role]),
                "ownership_band":     random.choice(OWNERSHIP_BANDS),
                "is_primary_contact": "yes" if j == 0 else "no",
            })
            link_id += 1

        # -- Funding timeline --
        event_types = _events_for_stage(stage)
        cursor = date(founded, random.randint(1, 6), random.randint(1, 28))
        for et in event_types:
            note, inr = _milestone(et, founded)
            funding_events.append({
                "event_id":       f"EV{event_id:06d}",
                "startup_id":     sid,
                "event_date":     cursor.isoformat(),
                "event_type":     et,
                "stage_at_event": stage if et in ("series_a_round", "seed_round", "pre_seed_round") else _map_event_to_stage(et, stage),
                "amount_in_inr":  inr,
                "milestone_note": note,
            })
            event_id += 1
            cursor = _random_date_after(cursor, max_days_ahead=300)

    return profiles, founder_links, funding_events


def _map_event_to_stage(event_type: str, final_stage: str) -> str:
    early = {"incubated", "prototype_built", "grant_received"}
    mid   = {"demo_day", "pilot_signed", "product_launched"}
    if event_type in early:
        return "pre-seed"
    if event_type in mid:
        return "seed" if final_stage in ("seed", "series-a") else final_stage
    return final_stage


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
    global VOCAB_BANK
    print("Campus Innovation & Engagement Intelligence Hub")
    print("Phase 1 — Startup Data Generator\n")

    # Build vocab bank first (used by text generation)
    VOCAB_BANK = _build_vocab_bank()
    write_csv(OUTPUT_DIR / "startup_vocabulary_bank.csv", VOCAB_BANK)

    # Generate all startup data
    profiles, founder_links, funding_events = generate_startups(NUM_STARTUPS)

    write_csv(OUTPUT_DIR / "startup_profiles.csv",         profiles)
    write_csv(OUTPUT_DIR / "startup_founder_links.csv",    founder_links)
    write_csv(OUTPUT_DIR / "startup_funding_timeline.csv", funding_events)

    summary = {
        "project": "Campus Innovation & Engagement Intelligence Hub",
        "phase":   "1 — Synthetic Data Foundation",
        "seed":    SEED,
        "generated_files": {
            "startup_vocabulary_bank.csv":  len(VOCAB_BANK),
            "startup_profiles.csv":         len(profiles),
            "startup_founder_links.csv":    len(founder_links),
            "startup_funding_timeline.csv": len(funding_events),
        },
        "total_records": len(VOCAB_BANK) + len(profiles) + len(founder_links) + len(funding_events),
        "note": "Entirely synthetic data. No real PII. Safe for build and demo.",
    }
    write_json(OUTPUT_DIR / "startup_generation_summary.json", summary)

    print(f"\nAll files written to: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()