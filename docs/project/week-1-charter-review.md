# Week 1 Charter Review
**Project:** Campus Innovation & Engagement Intelligence Hub
**Review date:** Day 5, Phase 0 (Jul 10, 2026)
**Author:** Sanjay (24AM0100), Chennai Institute of Technology
**Purpose:** Confirm all Week 1 deliverables before Phase 1 (Synthetic Data) begins.

---

## Week 1 Completed

| Deliverable | File / Artefact | Status |
|---|---|---|
| Project kickoff & charter alignment | Day 1 scorecard + persona definitions | ✅ Done |
| NIRF KPI analysis & traceability sheet | `docs/nirf/nirf_innovation_kpi_analysis.md`, `nirf_kpi_feature_traceability.md` | ✅ Done |
| Competitor audit — alumni platforms | `docs/market/alumni_platform_audit.md` | ✅ Done |
| Competitor audit — incubator tools | `docs/market/incubator_tool_audit.md` | ✅ Done |
| Whitespace memo | `docs/market/whitespace_memo.md` | ✅ Done |
| Architecture Decision Records (ADR 001–003) | `docs/architecture/adr-001` → `adr-003` | ✅ Done |
| Stack lock | `docs/architecture/stack_lock.md` | ✅ Done |
| Figma wireframe brief (5 portal shells) | `docs/product/figma-wireframe-brief.md` | ✅ Done |
| ERD skeleton (8 entities) | `docs/architecture/erd-skeleton.md` | ✅ Done |
| GitHub repo + branch strategy | `main` / `dev` branches live, alias configured | ✅ Done |
| Local dev environment | Docker, PostgreSQL 16, pgvector, Python 3.11, Node 20 | ✅ Done |

---

## In Scope for Phase 1 (Synthetic Data Foundation)

- Design and implement `generate_ecosystem_data.py` producing ≥ 10,000 synthetic rows
- Implement all 8 entities from the ERD skeleton as Django models
- Engineer custom ML signals: AIS, Grit Index, TRL–MRL Gap, `at_risk_label`, `success_prediction_label`
- Export final synthetic CSVs and write data dictionary
- Freeze synthetic dataset as `v1.0`
- All work lands on `dev` via `feature-*` branches per the confirmed branch strategy

---

## Out of Scope for Phase 1

- Django project scaffold and DRF endpoints (Phase 2)
- pgvector installation or embedding generation (Phase 2)
- Any ML model training (Phase 4)
- Frontend work of any kind (Phase 7)
- LinkedIn API integration or live data scraping (explicitly excluded for the entire project — synthetic data only)
- Graph construction or NetworkX compute (Phase 5)

---

## Risks / Open Checks

| Risk | Mitigation |
|---|---|
| Synthetic data label imbalance (too many `success=True`) | Enforce stratified target distribution in the generator: 30% success, 70% failure — matches real-world base rates |
| Pitch/mandate text too repetitive for NLP to distinguish | Use vocabulary bank + sentence template variety in Phase 1 generator; benchmark cosine similarity spread before freezing v1.0 |
| ERD field types not yet validated against Django ORM | First migration run in Phase 2 is the validation step — field types adjusted there if needed |
| Figma wireframes not yet executed by a designer | Wireframe brief is complete; execution can proceed independently and in parallel with Phase 1 |
| `pgvector` extension availability on target PaaS (Render/Railway) | Both Render and Railway support pgvector on PostgreSQL 16 instances — confirmed in ADR-001 |

---

## Scope Confirmation

> **Phase 0 is complete. Phase 1 begins Day 6 (Jul 13, 2026).**
>
> All architecture decisions are locked (ADR-001 through ADR-003).
> The ERD skeleton is the authoritative schema reference for the Phase 1
> synthetic data generator. No schema changes are permitted in Phase 1 without
> updating `erd-skeleton.md` in the same commit.
> The NIRF traceability sheet metric names are frozen — any rename requires
> updating both `nirf_kpi_feature_traceability.md` and `nirf_dashboard_design.md`.
