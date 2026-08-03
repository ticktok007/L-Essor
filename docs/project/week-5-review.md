# Week 5 Review
**Project:** Campus Innovation & Engagement Intelligence Hub
**Phase:** 2 — Backend Foundation (Day 25 close)
**Author:** Sanjay (24AM0100), Chennai Institute of Technology

## Completed this week

| Day | Deliverable |
|---|---|
| Day 21–24 | DRF serializers, ViewSets, bulk `load_synthetic_data`, pgvector columns + ivfflat ANN indexes |
| Day 25 | B-tree indexes on `role`, `department`, `funding_stage`, `sector`; `scripts/load_test_filtered_queries.py` |

## Performance check

- Ran `python scripts/load_test_filtered_queries.py` after synthetic load.
- Workload: users by `role`, profiles by `department`, startups by `funding_stage` / `sector`, plus one combined startup filter — same shapes as leadership dashboard list endpoints.
- Script reports total and average ms over 25 iterations; re-run after scaling toward **20,000+ profiles** to confirm latency stays acceptable.

## Indexing status

| Column | Table / model | Index name | Type |
|---|---|---|---|
| `role` | `auth_user` / `User` | `auth_user_role_btree_idx` | B-tree |
| `department` | `accounts_profile` / `Profile` | `accounts_profile_department_btree_idx` | B-tree |
| `funding_stage` | `ecosystem_startup` / `Startup` | `ecosystem_startup_funding_stage_btree_idx` | B-tree |
| `sector` | `ecosystem_startup` / `Startup` | `ecosystem_startup_sector_btree_idx` | B-tree |

Migrations: `accounts/migrations/0002_add_profile_filter_indexes.py`, `ecosystem/migrations/0002_add_startup_filter_indexes.py`.

## Notes

- `Startup.funding_stage` indexed alongside `sector` to match synthetic CSV / master schema; populated on ingest via `load_synthetic_data`.
- Department filter benchmark uses equality (B-tree friendly); portal search may still use `icontains` — add trigram/GiST only if explain plans show sequential scans at scale.
- Capture `EXPLAIN ANALYZE` for any query over budget before Phase 3 matching load tests.
