# Synthetic Data Validation Plan
**Project:** Campus Innovation & Engagement Intelligence Hub
**Phase:** 1 — Data Validation & QA
**Applies to:** All outputs under `data/synthetic/` and `data/processed/`

---

## Scope

Validate that the synthetic dataset is structurally correct, statistically
realistic, and fit for downstream ML feature engineering and model training.

---

## Validation Areas

### 1. Class Balance — Target Labels
- `success_prediction_label`: required positive ratio in [0.35, 0.65]
- `at_risk_label`: required positive ratio in [0.20, 0.50]
- Failure condition: degenerate labels (all 0 or all 1), or ratio outside bounds

### 2. Null Scans
- All required columns in every generated CSV must have zero nulls
- Required columns are defined per schema in `docs/data/master-schema.md`
- Failure condition: any null in a non-nullable column

### 3. Outlier Scans
Key numeric features must stay within plausible bounds:

| Feature | Expected Range |
|---|---|
| `technology_readiness_level` | 1–9 |
| `market_readiness_level` | 1–9 |
| `mentorship_hours` | 0–200 |
| `competitions_participated` | 0–30 |
| `competitions_won` | 0 ≤ won ≤ participated |
| `portfolio_achievement_scale_1_to_10` | 1–10 |
| `ais_normalized` | 0.0–100.0 |
| `grit_normalized` | 0.0–100.0 |

### 4. Referential Integrity
- Every `startup_founder_links.startup_id` must exist in `startup_profiles.startup_id`
- Every `startup_funding_timeline.startup_id` must exist in `startup_profiles.startup_id`
- Every `competition_records.profile_id` must follow `STU-####` or `ALU-####` format
- Every `achievement_records.profile_id` must follow `STU-####` or `ALU-####` format
- `founder_count` in `startup_profiles` must equal the number of founder-link rows per startup

### 5. Distribution Realism
- Funding stage distribution must not be degenerate (no single stage > 60%)
- Degree distribution in `interaction_edges` must show hub-and-spoke shape
- AIS histogram must not be a spike at one value
- Text pitch summaries must have unique-text ratio ≥ 0.80

### 6. Generator Script Review Expectations
- All generators use a fixed seed and are deterministic
- No generator depends on live external data sources
- Output directory is created automatically
- Each generator produces a JSON summary alongside its CSVs