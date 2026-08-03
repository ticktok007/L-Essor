# Week 5 Data Load Review
**Project:** Campus Innovation & Engagement Intelligence Hub
**Phase:** 2 — Backend Foundation
**Review date:** Week 5 close — Day 23

## Completed This Week

| Item | Status |
|---|---|
| `load_synthetic_data` management command implemented | ✅ Done |
| Chunked `bulk_create` with configurable `--chunk-size` | ✅ Done |
| Deterministic FK-safe table load order (7 tables) | ✅ Done |
| `--flush-existing` reverse-order delete before reload | ✅ Done |
| `transaction.atomic` wrapping per table | ✅ Done |
| JSON field parsing with loud `CommandError` on failure | ✅ Done |
| FK validation — unresolvable IDs raise `CommandError` | ✅ Done |
| Dev database bootstrapped and verified with ViewSet smoke tests | ✅ Done |
| `management/__init__.py` and `commands/__init__.py` package files added | ✅ Done |

## Decisions Locked
- Command targets dev database only — no prod path.
- Explicit PKs from CSV are preserved — `update_or_create` not used.
- JSON fields parsed strictly — silent fallback to empty list is not allowed.
- `--flush-existing` deletes in reverse FK order to avoid integrity errors.
- `profiles.csv` field `full_name` is ignored on load — `full_name` lives on
  `User`, not `Profile`; the User row carries it.

## Risks / Follow-ups

| Risk | Action |
|---|---|
| CSV field names in `data/final/` may drift from model field names after schema changes | Re-run `scripts/export_final_dataset.py` and update command field mapping together |
| Large `interactions.csv` (500+ rows) may be slow on SQLite | Expected; PostgreSQL + pgvector migration (Day 17) resolves this |
| `competition.created_by_id` is nullable — rows with empty value load as `None` | Confirmed correct — most competitions have no admin creator in synthetic data |

## Exit Status
**Week 5 data load complete. Dev database bootstrapped. Backend testing can proceed.**