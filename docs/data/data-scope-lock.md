# Data Scope Lock — Phase 1
**Project:** Campus Innovation & Engagement Intelligence Hub
**Locked:** Day 6, Phase 1 (Jul 13, 2026)
**Author:** Sanjay (24AM0100), Chennai Institute of Technology
**Covers:** Phase 1 data build window (Days 6–15)

---

## Confirmed Data Sources Now

| Source | Method | Status |
|---|---|---|
| Synthetic user / profile data | `generate_ecosystem_data.py` via Faker | ✅ Active |
| Synthetic startup + pitch text | Same generator, vocabulary bank | ✅ Active |
| Synthetic investor / mentor profiles | Same generator | ✅ Active |
| Synthetic interaction edges | Same generator, controlled degree distribution | ✅ Active |
| Synthetic achievements + competition results | Same generator | ✅ Active |
| Engineered ML signals (AIS, Grit Index, TRL–MRL Gap) | Computed columns in generator | ✅ Active |
| Target labels (`success_prediction_label`, `at_risk_label`) | Engineered with 30/70 class balance | ✅ Active |

---

## Confirmed Tables Now

| Table | Rows Target | Frozen Schema Reference |
|---|---|---|
| `users` | ≥ 3,000 | `docs/data/master-schema.md` |
| `profiles` | ≥ 3,000 | `docs/data/master-schema.md` |
| `startups` | ≥ 500 | `docs/data/master-schema.md` |
| `investors` | ≥ 300 | `docs/data/master-schema.md` |
| `mentors` | ≥ 300 | `docs/data/master-schema.md` |
| `interactions` | ≥ 5,000 | `docs/data/master-schema.md` |
| `achievements` | ≥ 2,000 | `docs/data/master-schema.md` |
| `competitions` | ≥ 100 | `docs/data/master-schema.md` |

All tables exported as CSVs to `data/synthetic/v1.0/` and tagged
`v1.0-synthetic-data` after QA pass.

---

## Deferred Sources

| Source | Reason Deferred |
|---|---|
| LinkedIn profile data | Permanently excluded — see `linkedin-acquisition-decision.md` |
| Institutional MIS/ERP import | Post-Phase 10 / production onboarding only |
| DistilBERT NER extraction from real certificates | Phase 6 — requires Django + file upload pipeline first |
| Third-party enrichment (Clearbit, ORCID) | Post-production; requires signed DPA and user consent flow |
| Real alumni self-reported data | Phase 7 — requires Alumni Portal to exist |
| AngelList / Crunchbase startup data | No compliant bulk API available; excluded from all phases |

---

## Scope Confirmation

> **Phase 1 data scope is closed.**
>
> The synthetic generator is the sole data source for all build, test, and
> demo activity through Phase 10. No real PII enters the system before Phase 10
> institutional onboarding. No external API is called during Phase 1.
> Schema changes require updating `master-schema.md` and `erd-skeleton.md`
> in the same commit before any generator code is modified.
