# Ingestion Validation Checks
**Project:** Campus Innovation & Engagement Intelligence Hub
**Phase:** 2 — Backend Foundation

## Checks Performed

| Check | How enforced |
|---|---|
| Required CSV files exist | `_load_csv` raises `CommandError` if file not found |
| Load order is FK-safe | Hardcoded sequence: users → profiles → competitions → startups → investors → interactions → achievements |
| JSON fields are valid | `_json()` calls `json.loads`; malformed values raise `CommandError` immediately |
| Foreign keys resolve | Each loader checks the parent ID set before building the model instance; unknown IDs raise `CommandError` |
| Large files use chunked inserts | `_bulk_insert` iterates in slices of `--chunk-size`; default 1000 rows per batch |
| Transactions per table | Each `_load_*` call wraps its `bulk_create` in `transaction.atomic` |
| Boolean fields parsed safely | `_bool()` accepts `true/false/1/0/yes/no` case-insensitively |
| Nullable fields default to `None` | `_none()` converts empty strings; applied to all optional FK and scalar fields |

## Failure Conditions

| Condition | Behaviour |
|---|---|
| Missing CSV file | `CommandError` raised immediately — command aborts |
| Unknown FK ID | `CommandError` raised on the offending row — current table transaction rolls back |
| Malformed JSON | `CommandError` raised with field name and raw value — current table transaction rolls back |
| Unparseable int/float/date | `CommandError` raised with raw value — current table transaction rolls back |
| `--flush-existing` on non-dev database | Operator responsibility — command does not check the database alias |

## Exit Status
All checks implemented in `load_synthetic_data.py`. No silent data corruption paths.