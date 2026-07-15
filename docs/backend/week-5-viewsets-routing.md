# ViewSets and Routing
**Project:** Campus Innovation & Engagement Intelligence Hub
**Delivered:** Week 5, Phase 2

## Status
ACCEPTED — implemented and ready for frontend wiring

## Scope

| ViewSet | Model | Route prefix |
|---|---|---|
| `ProfileViewSet` | `accounts.Profile` | `/api/v1/profiles/` |
| `StartupViewSet` | `ecosystem.Startup` | `/api/v1/startups/` |
| `InvestorViewSet` | `ecosystem.Investor` | `/api/v1/investors/` |
| `AchievementViewSet` | `ecosystem.Achievement` | `/api/v1/achievements/` |
| `InteractionViewSet` | `ecosystem.Interaction` | `/api/v1/interactions/` |
| `CompetitionViewSet` | `ecosystem.Competition` | `/api/v1/competitions/` |

## Delivery Rules
- All ViewSets use `ModelViewSet` (full CRUD).
- Routing uses `DefaultRouter` — no hand-written `urlpatterns` beyond `router.urls`.
- Every list endpoint supports `DjangoFilterBackend`, `SearchFilter`, and `OrderingFilter`.
- A shared `EcosystemPagination` class (page size 20, max 100) applies to all list views.
- `select_related` / `prefetch_related` added to querysets where list/detail performance benefits.

## Leadership Dashboard Support
- `ProfileViewSet` can be filtered by `at_risk_flag`, `community_id`, `department` —
  directly supports the at-risk and department-participation panels.
- `StartupViewSet` can be filtered by `incubation_status`, `at_risk_flag`, `sector` —
  feeds the incubation roster and NIRF Financial Support metrics.
- `AchievementViewSet` filterable by `nirf_countable`, `category`, `verified` —
  feeds the NIRF Innovation Achievements count.
- All list endpoints are orderable so the dashboard can surface top-N by any numeric signal.

## Exit Status
ViewSets and routing locked. Role-based permission scoping applied in Week 6.