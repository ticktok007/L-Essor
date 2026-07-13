# Skill Scoring System Design
**Project:** Campus Innovation & Engagement Intelligence Hub
**Phase:** 1 — Feature Engineering
**Version:** 1.0
**Author:** Sanjay (24AM0100), Chennai Institute of Technology

---

## Problem Statement

Participation in a hackathon or competition does not prove individual skill.
A 4-person team can win Smart India Hackathon with one person doing all the
technical work and three people handling slides and logistics. A flat
"won = skilled" scoring system cannot distinguish between these cases.

Similarly, an internship where a student paid ₹20,000 to a training institute
is categorically different from an internship where a company paid the student
₹25,000/month to work on real production systems. Both are called "internships"
in a CV, but they carry completely different evidence weights.

This document defines the complete point-based system that resolves these
ambiguities through layered, evidence-weighted scoring.

---

## Scope

- Applies to: student profiles and alumni profiles
- Inputs: competition records, achievement records (internships), self-declared skills
- Outputs: `raw_skill_score`, `skill_level`, per-skill `confidence` upgrades
- Phase 1: synthetic baseline (self-declared confidence = 0.10)
- Phase 6: NER upgrades confidence from certificate role extraction
- Phase 7: Mentor endorsement adds highest-trust confidence boost

---

## 1. Structured Skills Format

All profiles store skills as a structured JSON array, not a flat string.

```json
[
  {
    "skill":      "Machine Learning",
    "confidence": 0.10,
    "level":      "unknown",
    "sources":    ["self_declared"]
  }
]
```

**Confidence scale:**

| Range | Meaning |
|---|---|
| 0.00–0.15 | Self-declared only — no verification |
| 0.16–0.35 | Some indirect evidence (participation, low-tier competition) |
| 0.36–0.60 | Moderate evidence (win, certificate NER, unpaid internship) |
| 0.61–0.80 | Strong evidence (paid internship, Tier A win, small team) |
| 0.81–1.00 | Very strong evidence (mentor endorsement + multiple verified signals) |

**Level progression** (upgraded when confidence crosses thresholds):

| Confidence | Level |
|---|---|
| < 0.50 | unknown (not enough evidence to classify) |
| ≥ 0.50 | reflects current `skill_level` from point score |

---

## 2. Competition Scoring

### 2a. Outcome Base Points

| Outcome | Base Points |
|---|---|
| Just registered (no submission) | 0 |
| Participated / Submitted | 3 |
| Shortlisted (top 20–50) | 5 |
| Finalist — Top 10 | 8 |
| Finalist — Top 5 | 11 |
| 3rd Place | 14 |
| 2nd Place | 17 |
| 1st Place | 20 |
| Special / Jury / Domain Award | 12 |
| Organizer | 4 |
| Mentor / Judge | 3 |

### 2b. Team Size Multiplier

Smaller teams imply greater individual contribution.

| Team Size | Multiplier | Rationale |
|---|---|---|
| 1 | 2.0× | Every line of work is yours |
| 2 | 1.5× | High individual contribution |
| 3 | 1.2× | Moderate |
| 4 | 0.8× | Could be a minor contributor |
| 5 | 0.6× | Likely specialized, narrow role |
| 6+ | 0.4× | Highly diluted signal |

Organizer and judge roles: team-size multiplier is not applied (1.0×).

### 2c. Competition Difficulty Tier

| Tier | Examples | Multiplier |
|---|---|---|
| S | ICPC, NASA Space Apps, Google Hash Code, IEEE Xtreme | 2.5× |
| A | Smart India Hackathon, Microsoft Imagine Cup, Google Solution Challenge | 2.0× |
| B | NASSCOM 10K, TiE Challenge, IIM Eureka, State-level hackathons | 1.5× |
| C | College fests, department hackathons, local ideathons | 1.0× |
| D | No-barrier online hackathons, participation-certificate-only events | 0.6× |

### 2d. Formula

competition_points = base_points × team_size_multiplier × tier_multiplier

**Example calculations:**
Smart India Hackathon (Tier A), 1st Place, 4-member team:
= 20 × 0.8 × 2.0 = 32 points
NASA Space Apps (Tier S), 1st Place, 2-member team:
= 20 × 1.5 × 2.5 = 75 points
College internal hackathon (Tier C), submitted, 6-member team:
= 3 × 0.4 × 1.0 = 1.2 points  ← nearly negligible (correct)
SIH, just shortlisted, 4-member team:
= 5 × 0.8 × 2.0 = 8 points

---

## 3. Internship Scoring

### 3a. Payment Type Base Points

| Type | Base Points | Rationale |
|---|---|---|
| Paid by student | 2 | Student bought a certificate. Skill signal near zero. |
| Unpaid | 8 | Some genuine work. Company extracted value; student learned. |
| Stipend (₹5K–₹15K/month) | 18 | Company valued contribution enough to pay. Real work happened. |
| Paid (₹15K+/month) | 25 | Market-rate signal. Treated as a real contributor. |

### 3b. Mode Multiplier

| Mode | Multiplier | Rationale |
|---|---|---|
| Online | 0.6× | Harder to verify attendance and hands-on work |
| Hybrid | 0.85× | Partial signal |
| Offline | 1.0× | Full presence, lab access, harder to fake |

**Special rule for paid-by-student:** mode multiplier is always 0.4× regardless
of stated mode, and final points are hard-capped at 3. Even offline, a training
institute is not a real workplace.

### 3c. Duration Multiplier

| Duration | Multiplier |
|---|---|
| < 4 weeks | 0.5× |
| 4–8 weeks | 0.8× |
| 8–12 weeks | 1.0× |
| 12–24 weeks | 1.2× |
| > 24 weeks | 1.4× |

### 3d. Company Tier Multiplier

| Tier | Examples | Multiplier |
|---|---|---|
| S | Google, Microsoft, Amazon, Meta | 2.0× |
| A | Infosys, TCS, Zoho, Freshworks, CPCL, Razorpay | 1.5× |
| B | Mid-size product companies, funded startups, PSUs | 1.2× |
| C | Small companies, early startups, local firms | 1.0× |
| D | Unknown / unverifiable | 0.7× |

### 3e. Formula
internship_points = base × mode_multiplier × duration_multiplier × company_multiplier
IF paid_by_student:
mode_multiplier = 0.4  (override)
internship_points = min(internship_points, 3.0)  (hard cap)

**Example calculations:**
CPCL (Tier A), offline, stipend, 8 weeks:
= 18 × 1.0 × 0.8 × 1.5 = 21.6 points
Google India (Tier S), offline, paid, 12 weeks:
= 25 × 1.0 × 1.0 × 2.0 = 50 points
Training institute, paid by student, online, 4 weeks:
= 2 × 0.4 × 0.5 × 0.7 = 0.28 → capped at 3 points
Unknown company, unpaid, online, 6 weeks:
= 8 × 0.6 × 0.8 × 0.8 = 3.07 points

---

## 4. Overall Skill Score and Level
raw_skill_score = Σ competition_points + Σ internship_points

| Score Range | Skill Level |
|---|---|
| 0–10 | Beginner |
| 11–25 | Developing |
| 26–50 | Intermediate |
| 51–80 | Proficient |
| 81–120 | Advanced |
| 120+ | Expert |

---

## 5. Skill Confidence Boosts Per Event

| Event | Confidence Boost |
|---|---|
| Tier S win, 1–2 member team | +0.40 |
| Tier A/S win, any team | +0.25 |
| Tier B win | +0.15 |
| Any participation | +0.05 |
| Paid internship, offline | +0.30 |
| Stipend internship, offline | +0.20 |
| Unpaid internship, offline | +0.12 |
| Paid-by-student internship | +0.03 |
| Mentor endorsement (Phase 7) | +0.35 |
| Certificate NER role extraction (Phase 6) | +0.20 |

Confidence is **capped at 1.0** per skill. Boosts compound from all events.

---

## 6. Known Limitations

| Limitation | Mitigation |
|---|---|
| Team role unknown from participation data alone | Phase 6 NER extracts role from certificate (ML Engineer, Team Lead, etc.) |
| Self-declared skills unverified | Confidence starts at 0.10; only upgrades with verified evidence |
| Company tier hard-coded for known companies | Unknown companies default to Tier C; admin can override in Phase 7 |
| Internship type self-reported | In Phase 6, NER cross-checks certificate against known training institute names |
| Competition tier assigned heuristically | Admin can override tier in the Leadership Portal (Phase 7) |
| No GitHub/code contribution signal yet | Roadmap item for Phase 10+ (GitHub OAuth integration) |

---

## 7. Files

| File | Role |
|---|---|
| `scripts/compute_skill_scores.py` | Full scoring engine — reads enriched CSVs, writes profile_skill_scores.csv |
| `data/generation/skill_data_enricher.py` | Adds competition_tier, internship_type, company_tier to synthetic records |
| `scripts/generate_ecosystem_data.py` | Updated to output structured skills JSON (confidence=0.10 baseline) |
| `tests/test_skill_scores.py` | Unit tests for every formula in this document |
| `data/processed/profile_skill_scores.csv` | Per-profile output: points, level, updated skills JSON |
| `data/processed/skill_score_summary.json` | Aggregate stats and scoring constants |

---

## 8. Run Order

```bash
python scripts/generate_ecosystem_data.py       # structured skills in output
python scripts/generate_interaction_data.py     # competition + achievement records
python data/generation/skill_data_enricher.py   # add tier/team/internship fields
python scripts/compute_skill_scores.py          # compute final scores
python tests/test_skill_scores.py               # verify all formulas
```