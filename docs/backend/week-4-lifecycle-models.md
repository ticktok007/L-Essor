# Lifecycle Models — Competition, Achievement, Interaction
**Project:** Campus Innovation & Engagement Intelligence Hub
**Delivered:** Week 4, Phase 2

## Status
ACCEPTED — implemented and ready for migrations

## Context
The platform must track the complete lifecycle of a campus innovator: from
first hackathon entry to prototype builder to startup founder to alumni mentor.
Three models capture the events that produce this trail. Without them, the
AI matchmaking engine, predictive analytics, and portfolio generator have no
verified, timestamped evidence to work from.

## Decision
Add three models to `apps/ecosystem/models.py`:

- **Competition** — master list of events (hackathons, demo days, ideathons).
  Includes NIRF-recognition flag and eligible-role scoping so admin can define
  which user types may register.

- **Achievement** — one row per award, publication, patent, or role held by a
  profile. Nullable FK to `Competition` links a result to its event. The
  `verified` flag and `ner_confidence` float are set by the Phase 6 NER
  pipeline when a certificate is uploaded; `nirf_countable` is set by admin
  during NIRF submission preparation.

- **Interaction** — the edge table for the NetworkX graph (Phase 5). Every
  mentor session, investor introduction, club membership, and MoU is a row
  here. `actor → target` with `outcome = accepted` becomes a directed edge.
  `success_label` is written by the platform on each "Connect" click and feeds
  the XGBoost retraining loop (Phase 8).

## Consequences
- These three tables are the primary source of truth for the graph layer,
  portfolio generator, NIRF dashboard metrics, and the AIS / Grit Index
  feature-engineering pipeline.
- The `Interaction` table replaces any need for a separate graph database at
  Phase 2 scale — NetworkX consumes it directly.
- `Achievement.topic_tags` and `Achievement.verified` are written by the NER
  pipeline in Phase 6; they are nullable/blank at creation time.

## Integration Notes
- Foreign keys use `settings.AUTH_USER_MODEL` (lazy string) for actor/target
  in `Interaction` and `created_by` in `Competition`.
- `Profile` and `Startup` are referenced from `accounts.Profile` and
  `ecosystem.Startup` respectively.
- All three models are registered in `ecosystem/admin.py` in the next step.
- `Interaction.type` and `Interaction.outcome` use `TextChoices`; the set of
  valid edge types must stay in sync with the NetworkX graph-construction task
  in Phase 5.