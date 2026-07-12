# Statistical Sanity Checks Specification
**Project:** Campus Innovation & Engagement Intelligence Hub
**Phase:** 1 — Data Validation & QA

---

## Scope
Automated checks run against all files in `data/synthetic/` and
`data/processed/` after each generator run. Checks are deterministic
and produce a pass/fail result per check.

---

## Checks

### 1. Class Balance — Target Labels

| Label | Min Positive Ratio | Max Positive Ratio |
|---|---|---|
| `success_prediction_label` | 0.35 | 0.65 |
| `at_risk_label` | 0.20 | 0.50 |

- Compute `positive_count / total_rows` for each label
- Check that result is within inclusive bounds
- Check that neither label is all-zero or all-one

### 2. Null Scans — Required Columns

For each generated CSV, assert zero null/empty values in these columns:

| File | Required Non-Null Columns |
|---|---|
| `student_profiles.csv` | `student_id`, `full_name`, `email`, `role`, `department`, `skills` |
| `alumni_profiles.csv` | `alumni_id`, `full_name`, `email`, `role`, `graduation_year` |
| `startup_profiles.csv` | `startup_id`, `sector`, `funding_stage`, `trl_level`, `pitch_summary` |
| `investor_mentor_profiles.csv` | `profile_id`, `role`, `mandate_text`, `sector_focus` |
| `interaction_edges.csv` | `edge_id`, `source_profile_id`, `target_profile_id`, `edge_type` |
| `profile_feature_scores.csv` | `profile_id`, `ais_normalized`, `grit_normalized`, `review_flag` |

### 3. Outlier Detection — Key Numeric Features

Assert the following hard bounds (any row outside = failure):

| Column | Min | Max |
|---|---|---|
| `technology_readiness_level` | 1 | 9 |
| `market_readiness_level` | 1 | 9 |
| `mentorship_hours` | 0.0 | 500.0 |
| `competitions_participated` | 0 | 50 |
| `competitions_won` | 0 | `competitions_participated` |
| `portfolio_achievement_scale_1_to_10` | 1 | 10 |
| `ais_normalized` | 0.0 | 100.0 |
| `grit_normalized` | 0.0 | 100.0 |

### 4. Referential Integrity

- `startup_founder_links.startup_id` ⊆ `startup_profiles.startup_id`
- `startup_funding_timeline.startup_id` ⊆ `startup_profiles.startup_id`
- For each `startup_id` in `startup_profiles`, count of matching rows in `startup_founder_links` must equal `founder_count`
- `competition_records.profile_id` must match regex `^(STU|ALU)-\d{4}$`
- `achievement_records.profile_id` must match regex `^(STU|ALU)-\d{4}$`
- `interaction_edges.edge_type` values must be in `{mentor_mentee, investor_founder, club_membership}`

---

## Failure Conditions

Any of the following causes a hard failure:
- Label ratio outside required bounds
- Any null in a required non-null column
- Any numeric value outside its declared bounds
- `competitions_won` > `competitions_participated` for any row
- Missing startup IDs in cross-link files
- `founder_count` mismatch
- Invalid `edge_type` value

Soft warnings (logged but not blocking):
- Single funding stage exceeding 60% of all startups
- Unique pitch text ratio below 0.80
- Average node degree in interaction graph below 2.0

---

## Output Artifacts

- `data/processed/sanity_check_report.json` — pass/fail per check + counts
- `data/processed/failed_rows.csv` — rows that triggered hard failures (if any)
- Console summary: total checks, passed, failed, warnings