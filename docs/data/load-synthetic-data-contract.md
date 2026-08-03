# Synthetic Data Load Contract
**Project:** Campus Innovation & Engagement Intelligence Hub
**Phase:** 2 — Backend Foundation

## Expected Input Files

All files must exist in `data/final/` (or the path passed to `--base-dir`).

| File | Target Model | Notes |
|---|---|---|
| `users.csv` | `accounts.User` | Root identity table — loaded first |
| `profiles.csv` | `accounts.Profile` | Requires users to exist |
| `competitions.csv` | `ecosystem.Competition` | No FK on User except nullable `created_by` |
| `startups.csv` | `ecosystem.Startup` | Requires users (founder) |
| `investors.csv` | `ecosystem.Investor` | Requires profiles |
| `interactions.csv` | `ecosystem.Interaction` | Requires users and optionally startups |
| `achievements.csv` | `ecosystem.Achievement` | Requires profiles, optionally startups + competitions |

## Load Order

users
profiles
competitions
startups
investors
interactions
achievements

This order guarantees every foreign key reference resolves to an already-inserted parent row.

## Assumptions
- CSV files are the frozen v1.0 exports produced by `scripts/export_final_dataset.py`.
- Primary keys in CSV are UUIDs and are preserved as-is.
- Empty string values in nullable columns are converted to `None`.
- Boolean fields accept `true/false`, `1/0`, `yes/no` (case-insensitive).
- JSON fields (`skills_list`, `sector_focus`, `topic_tags`, `eligible_roles`,
  `stage_preference`) contain valid JSON strings; malformed values raise `CommandError`.
- This contract covers the dev database only — production ingestion uses a
  separate institutional data pipeline (Phase 10).

## Exit Status
Contract frozen alongside v1.0 synthetic dataset. Any schema change to
`data/final/` CSVs requires a corresponding update to the command field mapping.