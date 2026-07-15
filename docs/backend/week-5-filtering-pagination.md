# Filtering and Pagination Rules
**Project:** Campus Innovation & Engagement Intelligence Hub
**Delivered:** Week 5, Phase 2

## Supported Filters

| ViewSet | Filter Fields |
|---|---|
| Profile | `department`, `cohort_year`, `at_risk_flag`, `community_id` |
| Startup | `sector`, `funding_stage`, `incubation_status`, `at_risk_flag`, `founder` |
| Investor | `stage_preference`, `profile__department` |
| Achievement | `category`, `verified`, `nirf_countable`, `profile`, `startup`, `competition` |
| Interaction | `type`, `outcome`, `actor`, `target`, `startup`, `success_label` |
| Competition | `nirf_recognised`, `organiser` |

**Search fields** use `icontains` across free-text columns (name, bio, pitch_summary, mandate, notes).

## Pagination Rules
- Class: `EcosystemPagination` (local to `apps/ecosystem/views.py`)
- Default page size: `20`
- Query param: `?page_size=N`
- Maximum page size: `100`
- Response shape: `{ count, next, previous, results }`

## Ordering Rules
- Applied via `OrderingFilter` with explicit `ordering_fields` per ViewSet.
- Default ordering is inherited from `Meta.ordering` on each model.
- Clients pass `?ordering=field` (ascending) or `?ordering=-field` (descending).
- Numeric signal ordering (e.g. `?ordering=-success_probability`) supports top-N
  ranking for leadership dashboard panels without a separate analytics endpoint.

## Exit Status
Filtering and pagination rules locked. No changes required before ViewSet wiring.