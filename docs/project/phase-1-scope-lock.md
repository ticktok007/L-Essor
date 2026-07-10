# Phase 1 Scope Lock
**Project:** Campus Innovation & Engagement Intelligence Hub
**Locked:** Day 5, Phase 0 (Jul 10, 2026)
**Author:** Sanjay (24AM0100), Chennai Institute of Technology
**Covers:** Phase 1 — Synthetic Data Foundation & Feature Engineering (Days 6–15)

---

## Confirmed Users / Roles

| Role | In Phase 1 Scope |
|---|---|
| Student | ✅ Generate profile records |
| Alumni | ✅ Generate profile records |
| Investor / VC | ✅ Generate profile + mandate records |
| Mentor | ✅ Generate profile + expertise records |
| Incubation Cell Admin | ✅ Generate as user role; no portal work |
| Leadership | ✅ Generate as user role; no portal work |

---

## Confirmed Foundational Artifacts

| Artifact | Status |
|---|---|
| ERD skeleton (8 entities) | ✅ Frozen — `docs/architecture/erd-skeleton.md` |
| Stack lock | ✅ Frozen — `docs/architecture/stack_lock.md` |
| ADR-001 through ADR-003 | ✅ Accepted |
| NIRF KPI traceability sheet | ✅ Frozen — metric names must not change |
| Branch strategy | ✅ Active — all Phase 1 work on `feature-*` off `dev` |

---

## Confirmed Phase 1 Deliverables

| Deliverable | Target |
|---|---|
| `generate_ecosystem_data.py` | Vectorised generator, no slow Python loops |
| Synthetic user / profile records | ≥ 3,000 rows |
| Synthetic startup records with pitch text | ≥ 500 rows |
| Synthetic investor / mentor records | ≥ 300 rows each |
| Synthetic interaction records (graph edges) | ≥ 5,000 rows |
| Synthetic competition / achievement records | ≥ 2,000 rows |
| Engineered ML features | AIS, Grit Index, TRL–MRL Gap per record |
| Target labels | `success_prediction_label`, `at_risk_label` with 30/70 split enforced |
| Data validation pass | Class balance check, null scan, referential integrity, degree distribution plot |
| Exported CSVs | One file per entity, versioned as `v1.0` |
| Data dictionary | Column-level documentation for every generated field |
| Frozen dataset tag | `git tag v1.0-synthetic-data` on `dev` after QA pass |

---

## Explicit Exclusions — Phase 1 Window

- No Django project creation or `manage.py` commands
- No database migrations or PostgreSQL connection
- No pgvector setup or embedding generation
- No ML model training of any kind
- No frontend code
- No DRF endpoints
- No live data ingestion from any external source (LinkedIn, AngelList, etc.)
- No NetworkX graph construction
- No Celery or Redis setup
- No Sentry integration
- No deployment or CI/CD configuration
