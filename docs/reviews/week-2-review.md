# Week 2 Review
**Project:** Campus Innovation & Engagement Intelligence Hub
**Phase:** 1 — Synthetic Data Foundation
**Review date:** End of Week 2 (Day 10)
**Author:** Sanjay (24AM0100), Chennai Institute of Technology

---

## Completed This Week

| Day | Deliverable |
|---|---|
| Day 6 | LinkedIn acquisition decision; hybrid data strategy; master schema defined |
| Day 7 | `generate_ecosystem_data.py` — student, alumni, investor/mentor profiles (800+ rows) |
| Day 8 | `generate_startup_data.py` — startup profiles, vocabulary bank, founder links, funding timeline (120 startups, 450+ rows) |
| Day 9 | `generate_interaction_data.py` — interaction edges, competition records, achievement records, degree distribution plot |
| Day 10 | `compute_feature_scores.py` — AIS and Grit Index computed and normalised for all profiles |

---

## Outputs Produced

| File | Status |
|---|---|
| `data/synthetic/student_profiles.csv` | ✅ 300 rows |
| `data/synthetic/alumni_profiles.csv` | ✅ 200 rows |
| `data/synthetic/investor_mentor_profiles.csv` | ✅ 100 rows |
| `data/synthetic/startup_profiles.csv` | ✅ 120 rows |
| `data/synthetic/startup_vocabulary_bank.csv` | ✅ 144 phrases across 6 sectors |
| `data/synthetic/startup_founder_links.csv` | ✅ ~280 links |
| `data/synthetic/startup_funding_timeline.csv` | ✅ ~500 events |
| `data/synthetic/interaction_edges.csv` | ✅ 500 edges |
| `data/synthetic/competition_records.csv` | ✅ 300 records |
| `data/synthetic/achievement_records.csv` | ✅ 250 records |
| `data/synthetic/degree_distribution.png` | ✅ Hub-and-spoke shape confirmed |
| `data/processed/profile_feature_scores.csv` | ✅ AIS + Grit for all profiles |
| `data/processed/feature_score_summary.json` | ✅ Stats + flag distribution |

---

## Observations

- **AIS implemented.** Weighted composite of competition wins, finalist placements, leadership roles, impact levels (national/regional/campus), and portfolio breadth. Weights are explicit top-level constants — fully inspectable.
- **Grit Index implemented.** Persistence signal from competitions entered, win bonus, and year-spread across competition history. Rewards sustained participation, not only wins.
- **Synthetic interaction / competition / achievement foundations are now usable for downstream ML.** The profile_feature_scores.csv has clean, normalized 0–100 columns ready to join with any model feature matrix in Phase 4.
- **Degree distribution confirms hub-and-spoke structure.** A small number of MEN-#### and INV-#### nodes appear at 4–8× average degree — consistent with a real campus super-connector pattern.
- **Vocabulary bank produces varied pitch text.** Cosine similarity spread across pitch_embedding vectors (Phase 2 validation step) is the real test; visually, text is non-repetitive across sectors.

---

## Risks / Cleanup Before Week 3

| Risk | Action Required |
|---|---|
| Data realism still depends on later validation passes | Phase 2 will validate embedding spread via cosine similarity histogram before ML training begins — do not skip this step |
| AIS and Grit are computed from synthetic data only | Real-world label calibration needed post-onboarding; treat current scores as structural prototypes, not ground truth |
| `interaction_edges.csv` has no temporal ordering enforced | Phase 5 (NetworkX) must sort edges by `created_at` before graph construction to avoid anachronistic edges |
| `startup_founder_links.csv` references STU/ALU IDs not yet joined to profiles | Phase 2 management command (`load_synthetic_data`) must reconcile these foreign keys on ingestion |
| `review_flag` thresholds are arbitrary | Recalibrate flag boundaries in Phase 4 after XGBoost feature importance analysis; current flags are scaffolding only |