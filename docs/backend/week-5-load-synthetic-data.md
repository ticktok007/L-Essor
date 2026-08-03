# Bulk Synthetic Data Ingestion — load_synthetic_data
**Project:** Campus Innovation & Engagement Intelligence Hub
**Delivered:** Week 5, Phase 2 — Day 23 Backend Ingestion Milestone

## Status
ACCEPTED — management command implemented and ready for dev database bootstrap

## Scope
Ingests the frozen v1.0 synthetic dataset from `data/final/` into the local
development PostgreSQL (or SQLite dev) database via a single Django management
command. This is the Day 23 backend milestone: bulk-import the Phase 1 synthetic
CSV exports so serializer and ViewSet work can proceed against real data.

## Import Strategy
- Command name: `load_synthetic_data`
- Source directory: `data/final/` (configurable via `--base-dir`)
- Method: `csv.DictReader` → chunked `bulk_create` (default chunk 1000)
- Load order is deterministic and FK-safe (parents before children)
- `--flush-existing` deletes all existing rows in reverse FK order before loading
- Each table load is wrapped in `transaction.atomic` — partial loads roll back on error
- Invalid JSON fields and unresolvable FK IDs raise `CommandError` immediately
- Explicit primary keys from CSV are preserved (`update_or_create` not used — fresh load only)

## Exit Status
Command ready. Run `python manage.py load_synthetic_data` to bootstrap the dev database.