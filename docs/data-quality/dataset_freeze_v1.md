# Dataset Freeze — v1.0
**Project:** Campus Innovation & Engagement Intelligence Hub
**Version:** v1.0
**Freeze Date:** 2026-07-15
**Phase:** 1 — Synthetic Data Foundation (Days 6–15)

---

## Version Label
`v1.0-synthetic-baseline`
Git tag: `git tag -a v1.0-synthetic-data -m "Phase 1 synthetic dataset frozen"`

---

## Tables Included

| Table | Rows | Source Generator |
|---|---|---|
| `users` | 600 | `generate_ecosystem_data.py` (students + alumni + investors/mentors) |
| `startups` | 120 | `generate_startup_data.py` |
| `investors` | ~50 | `generate_ecosystem_data.py` (investor subset) |
| `interactions` | 500 | `generate_interaction_data.py` |
| `achievements` | 250 | `generate_interaction_data.py` |
| `competitions` | 300 | `generate_interaction_data.py` |

Exported formats: **CSV** (human-readable, git-diffable) and **Parquet** (typed, columnar, ML-ready).
Manifest: `data/final/dataset_freeze_manifest.json`

---

## Why This Is the Baseline

This frozen dataset is the authoritative starting point for all downstream work:

- **Phase 2 (Backend):** `load_synthetic_data` management command ingests these exact files into PostgreSQL. Schema is locked to `docs/data/master-schema.md`.
- **Phase 3 (Matching):** MiniLM embeddings are generated from `startups.pitch_summary` and `investors.mandate_text` in these files.
- **Phase 4 (ML):** XGBoost and Random Forest models are trained on feature vectors derived from these rows. Label distributions are enforced (success_label: 35–65%, at_risk_label: 20–50%).
- **Phase 5 (Graph):** NetworkX graph is constructed from `interactions` edges in this dataset.
- **Reproducibility:** All generators use `seed=42`. Any downstream team member can regenerate identical files by running the four generator scripts in order.

---

## Freeze Policy

> **Do not silently regenerate this dataset.**

- If a bug is found in a generator, create `v1.1` with a new freeze note documenting what changed and why.
- All model training, embedding generation, and graph construction in Phases 2–10 must reference this version explicitly.
- New real institutional data introduced at Phase 10 onboarding is treated as `v2.0` and does not overwrite this synthetic baseline.
- The frozen files in `data/final/` are the single source of truth. Files in `data/synthetic/` and `data/processed/` are intermediate working artifacts.

---

## Sanity Check Status at Freeze

| Check | Result |
|---|---|
| Class balance — success_prediction_label | ✅ Within [0.35, 0.65] |
| Class balance — at_risk_label | ✅ Within [0.20, 0.50] |
| Null scan — all required columns | ✅ Zero nulls |
| Outlier detection — numeric features | ✅ All within bounds |
| Referential integrity | ✅ No orphan IDs |
| Distribution realism | ✅ Hub-and-spoke graph, varied pitch text |
| Generator review | ✅ PASS=19, FAIL=0 |