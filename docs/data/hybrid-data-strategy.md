# Hybrid Data Strategy
**Project:** Campus Innovation & Engagement Intelligence Hub
**Defined:** Day 6, Phase 1 (Jul 13, 2026)
**Author:** Sanjay (24AM0100), Chennai Institute of Technology

---

## Current Build-Time Strategy (Phases 1–10)

**Approach:** Synthetic data only. No external data sources, no API calls, no
scraping, no real PII.

**Generator:** `data/generate_ecosystem_data.py` — Faker-based, vectorised,
produces all 6 core tables in a single run.

**Target volume:**

| Table | Target Rows |
|---|---|
| users / profiles | ≥ 3,000 |
| startups | ≥ 500 |
| investors | ≥ 300 |
| mentors | ≥ 300 |
| interactions | ≥ 5,000 |
| achievements | ≥ 2,000 |
| competitions | ≥ 100 |

**Why synthetic only:**
- Zero compliance risk — no real PII, no ToS violation, no data-sharing
  agreement required.
- Fully reproducible — `generate_ecosystem_data.py --seed 42` produces the
  same dataset on any machine, making CI and evaluator reproduction trivial.
- Controlled label distribution — target labels (`success_prediction_label`,
  `at_risk_label`) are engineered with the correct class balance (30/70) from
  the start; real-world data would require cleaning and labelling.
- Deployable as a demo on day one — no dependency on institutional data-sharing
  agreements that take weeks to execute.

**Frozen as:** `data/synthetic/v1.0/` after QA pass; tagged `v1.0-synthetic-data`
on `dev`.

---

## Future Enrichment Strategy (Post-Phase 10 / Production Onboarding)

**Approach:** Compliant institutional data import + opt-in third-party
enrichment under formal Data Processing Agreements (DPAs).

**Layer 1 — Institutional bulk import (primary path)**
- Institution exports alumni records from their existing MIS/ERP (Odoo, SAP,
  Banner) in a standard CSV/JSON format.
- One-time import via `manage.py load_institutional_data --source alumni.csv`.
- All imported records are flagged `data_source='institutional_import'` and
  require alumni self-verification before the profile becomes active.

**Layer 2 — Self-reported + NER-enriched (continuous)**
- Alumni, students, investors, and mentors update their own profiles via their
  respective portals.
- DistilBERT NER extracts verified skills, publications, and patent numbers from
  uploaded certificates, CVs, and pitch PDFs.
- NER-extracted fields are flagged `verified=True` only when confidence ≥ 0.80.

**Layer 3 — Compliant third-party enrichment (future, opt-in only)**
- Providers under active evaluation: Clearbit (company enrichment), Hunter.io
  (email verification), ORCID API (publication verification for faculty).
- All third-party enrichment requires:
  - A signed DPA between the institution and the provider.
  - Explicit opt-in consent from the user whose record is enriched.
  - Data stored in a separate `enrichment_metadata` JSONB column, not merged
    into core profile fields, so it can be purged on consent withdrawal.
- LinkedIn is **not** on this list. See `linkedin-acquisition-decision.md`.

---

## Ingestion Contract Requirements

Any future data source — institutional import, self-report, or third-party
enrichment — must satisfy all of the following before ingestion is permitted:

| Requirement | Specification |
|---|---|
| Format | CSV, JSON, or REST API with JSON response — no proprietary binary formats |
| Identity key | Must include `email` (alumni/student) or `pan_or_cin` (startup) for deduplication |
| PII handling | All fields containing name, email, phone, or address must be encrypted at rest (`pgcrypto`) |
| Consent flag | Source record must carry `consent_given: true` with timestamp; records without consent flag are rejected at ingestion |
| Provenance tag | Every ingested row tagged with `data_source`, `ingested_at`, and `ingestion_batch_id` |
| Conflict resolution | Incoming record never overwrites a user-verified field; flagged for manual review instead |
| Purge support | Ingestion pipeline must support `DELETE WHERE ingestion_batch_id = X` for full batch rollback |

---

## Non-Goals

- This platform does **not** scrape any external website at any stage.
- This platform does **not** store LinkedIn profile data in any form.
- This platform does **not** automatically enrich profiles without explicit
  user consent.
- Real-time external data sync is **not** a goal — all enrichment is batch,
  not streaming.
- This strategy does **not** replace the synthetic dataset during the build
  phase — real data is only introduced at institutional onboarding post-Phase 10.
