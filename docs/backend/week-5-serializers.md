# Serializers — Profile, Startup, Investor, Achievement
**Project:** Campus Innovation & Engagement Intelligence Hub
**Delivered:** Week 5, Phase 2

## Status
ACCEPTED — implemented and ready for ViewSet wiring

## Scope
| Serializer | Model | App |
|---|---|---|
| `ProfileSerializer` | `accounts.Profile` | accounts |
| `StartupSerializer` | `ecosystem.Startup` | ecosystem |
| `InvestorSerializer` | `ecosystem.Investor` | ecosystem |
| `AchievementSerializer` | `ecosystem.Achievement` | ecosystem |

## Design Rules
- All serializers use `ModelSerializer`.
- Read fields (id, computed scores, graph metrics) are explicitly marked `read_only=True`.
- Nested history fields are **always read-only** — write paths use flat FK IDs only.
- No `create()` or `update()` overrides unless a computed field requires pre-processing.
- Nested serializers are declared inline as small classes to avoid circular imports.
- `source=` is used wherever reverse-relation names differ from the desired JSON key.

## Lifecycle History Policy
Lifecycle history (achievements, interactions) is exposed as **nested read-only arrays**
on the parent serializer. This gives the frontend a single API call to reconstruct a
profile's full event trail without separate requests per entity. Write operations
on history items use their own dedicated endpoints, not the parent serializer.

## Exit Status
Serializer foundation locked. ViewSets and routing are next (Days 22–25).