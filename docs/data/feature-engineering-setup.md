# Feature Engineering Setup
**Project:** Campus Innovation & Engagement Intelligence Hub
**Phase:** 1 — Day 10

## Input Files Expected
- `data/synthetic/competition_records.csv`
- `data/synthetic/achievement_records.csv`

## Run Command
```bash
python scripts/compute_feature_scores.py
```

## Purpose
Computes the Achievement Impact Score (AIS) and Grit Index for every profile
in the synthetic dataset. Outputs normalized 0–100 scores and review flags
into `data/processed/` for downstream ML feature use.