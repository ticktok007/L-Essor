# Week 4 Review
**Project:** Campus Innovation & Engagement Intelligence Hub
**Phase:** 2 — Backend Foundation
**Review date:** Week 4 close

## Completed This Week

| Item | Status |
|---|---|
| `Competition` model — NIRF-recognised event master list | ✅ Done |
| `Achievement` model — verified award/patent/publication record with NER fields | ✅ Done |
| `Interaction` model — graph edge table (actor → target, typed, outcome-tracked) | ✅ Done |
| Initial migrations generated for `accounts` and `ecosystem` apps | ✅ Done |
| Migration review completed — all checks passed | ✅ Done |
| Schema foundation for lifecycle history locked | ✅ Done |

## Decisions Locked

- `Interaction` is the sole edge table for NetworkX graph construction — no
  separate graph schema or database.
- `Achievement.verified` and `Achievement.ner_confidence` are set by the NER
  pipeline in Phase 6, not by user input.
- `Achievement.nirf_countable` is an admin-only flag set during NIRF
  submission preparation in Phase 7.
- `success_label` on `Interaction` is written by platform telemetry on
  "Connect" click — feeds XGBoost retraining in Phase 8.
- SQLite used for Phase 2 local dev; PostgreSQL + pgvector migration target
  confirmed for Day 17.

## Risks / Follow-ups

| Risk | Action |
|---|---|
| `Interaction.success_label` is nullable — early model training has sparse signal | Expected; label sparsity handled in Phase 4 with synthetic label enforcement |
| `Achievement.certificate_path` stores a local path string — no S3/storage backend wired yet | Add `django-storages` + S3 config before Phase 6 certificate upload work |
| PostgreSQL `JSONField` behaviour differs from SQLite in edge cases | Run full migration test against PostgreSQL before Phase 2 closes |

## Exit Status
**Week 4 complete. Lifecycle schema is locked.**
Phase 2 continues with DRF serializers and ViewSets (Days 21–28).


# Week 4 Review
**Project:** Campus Innovation & Engagement Intelligence Hub
**Phase:** 2 — Backend Foundation
**Review date:** Week 4 close

## Completed This Week

| Item | Status |
|---|---|
| JWT auth via `djangorestframework-simplejwt` | ✅ Done |
| Custom `TokenObtainPairSerializer` — injects `role` + `full_name` into token | ✅ Done |
| `SIMPLE_JWT` config in `config/jwt.py` | ✅ Done |
| `BaseRolePermission` + `IsStudent`, `IsAlumni`, `IsInvestor`, `IsMentor`, `IsAdmin` | ✅ Done |
| Auth routes wired: `/api/v1/auth/token/` and `/api/v1/auth/token/refresh/` | ✅ Done |
| `REST_FRAMEWORK` updated: `JWTAuthentication` as default auth class | ✅ Done |
| Role-aware route protection verified in Django shell | ✅ Done |

## Decisions Locked

- Token auth only — no session auth on API routes.
- Role resolved from JWT payload, not from a DB call per request.
- Token blacklisting deferred to Phase 8 (MLOps layer).
- Refresh rotation disabled — stateless approach for current scale.
- `is_staff` / `is_superuser` reserved for Django Admin only; `IsAdmin`
  permission class uses `user.role == "admin"`.

## Risks / Follow-ups

| Risk | Action |
|---|---|
| Access tokens have 60-min lifetime — no revocation without blacklist | Acceptable for Phase 2; revisit in Phase 8 if security requirements tighten |
| Object-level permissions (cross-profile data leakage) not yet enforced | Each ViewSet must implement `has_object_permission` in Phase 2 serializer/viewset work |
| `simplejwt` not yet in `requirements.txt` | Add `djangorestframework-simplejwt>=5.3,<6.0` before Phase 2 closes |

## Exit Status
**Week 4 complete. Auth and access-control foundation is locked.**
Phase 2 continues with serializers and ViewSets (Days 21–28).