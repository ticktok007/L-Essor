# Nested Lifecycle History Policy
**Project:** Campus Innovation & Engagement Intelligence Hub
**Delivered:** Week 5, Phase 2

## Included Nested History

| Parent Serializer | Nested Field | Source (reverse relation) | Records |
|---|---|---|---|
| `ProfileSerializer` | `achievements` | `profile.achievements` | All achievements owned by this profile |
| `ProfileSerializer` | `outgoing_interactions` | `profile.user.interactions_initiated` | Interactions where user is actor |
| `ProfileSerializer` | `incoming_interactions` | `profile.user.interactions_received` | Interactions where user is target |
| `StartupSerializer` | `achievements` | `startup.achievements` | Achievements linked to this startup |
| `StartupSerializer` | `interactions` | `startup.interactions` | Interactions linked to this startup |
| `AchievementSerializer` | `competition_summary` | `achievement.competition` | Flat read-only summary of the linked competition |

## Read-Only Rules
- Every nested history field carries `read_only=True`.
- Nested serializers never expose write fields such as `certificate_path` updates or `verified` toggles — those are handled by dedicated endpoints in Phase 6.
- `InvestorSerializer.profile_summary` is a condensed read-only view of the linked Profile; it never allows profile edits through the investor endpoint.

## Ordering Rules
| Nested Field | Ordering |
|---|---|
| `achievements` | `-date`, `-created_at` |
| `outgoing_interactions` | `-created_at` |
| `incoming_interactions` | `-created_at` |
| `startup.interactions` | `-created_at` |

Ordering is enforced by `Meta.ordering` on the model, so serializers inherit it without additional `order_by` calls.

## Exit Status
Lifecycle history policy locked. No client-side sorting required for Phase 2 release.