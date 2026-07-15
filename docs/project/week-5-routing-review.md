# Week 5 Routing Review
**Project:** Campus Innovation & Engagement Intelligence Hub
**Phase:** 2 — Backend Foundation
**Review date:** Week 5 close

## Completed This Week

| Item | Status |
|---|---|
| `ProfileViewSet` — CRUD + filter + search + ordering | ✅ Done |
| `StartupViewSet` — CRUD + filter + search + ordering | ✅ Done |
| `InvestorViewSet` — CRUD + filter + search + ordering | ✅ Done |
| `AchievementViewSet` — CRUD + filter + search + ordering | ✅ Done |
| `InteractionViewSet` — CRUD + filter + search + ordering | ✅ Done |
| `CompetitionViewSet` — CRUD + filter + search + ordering | ✅ Done |
| `DefaultRouter` registered in `apps/ecosystem/urls.py` | ✅ Done |
| `EcosystemPagination` (page 20, max 100) applied to all list views | ✅ Done |
| `select_related` / `prefetch_related` added to high-join querysets | ✅ Done |
| `django-filter` added to `INSTALLED_APPS` and `DEFAULT_FILTER_BACKENDS` | ✅ Done |

## Decisions Locked
- All six ViewSets use `ModelViewSet` — no partial read-only ViewSets at this stage.
- Pagination lives in `apps/ecosystem/views.py` — not in global DRF settings — to
  keep it app-scoped and independently tunable.
- `founder` on `StartupViewSet` is set from `request.user` in `perform_create()`,
  not from request body.
- Role-based `permission_classes` applied in Week 6 — ViewSets currently use
  `IsAuthenticated` only as placeholder.

## Risks / Follow-ups

| Risk | Action |
|---|---|
| `ProfileViewSet` search on `full_name` requires traversal via `user__full_name` | Confirm search field path against model in Week 6 integration test |
| `InvestorViewSet` filter on `profile__department` requires join — may be slow at scale | Add DB index on `profile.department` in next migration |
| No object-level permission on `InteractionViewSet` yet | Implement `has_object_permission` in Week 6 — actor must not edit target's interactions |

## Exit Status
**Week 5 routing complete. API structure ready for dashboard and frontend wiring.**
Phase 2 closes with permission scoping and integration tests in Week 6.