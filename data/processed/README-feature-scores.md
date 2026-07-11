# Feature Scores — README
**Project:** Campus Innovation & Engagement Intelligence Hub | Phase 1 — Day 10
**Generator:** `scripts/compute_feature_scores.py` | Inputs: `data/synthetic/`

| File | Contents |
|---|---|
| `profile_feature_scores.csv` | Per-profile AIS and Grit Index scores (raw + normalised 0–100), competition/achievement breakdowns, and review flag — ready for ML feature matrix join in Phase 4 |
| `feature_score_summary.json` | Run metadata, average scores, top-5 profiles by AIS and Grit, review flag distribution, and full scoring weight constants for auditability |

## Regenerate
```bash
python scripts/compute_feature_scores.py
```
Requires `data/synthetic/competition_records.csv` and `data/synthetic/achievement_records.csv` to exist first.