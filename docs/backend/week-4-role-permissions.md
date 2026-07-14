# Role-Based Access Control
**Project:** Campus Innovation & Engagement Intelligence Hub
**Delivered:** Week 4, Phase 2

## Status
ACCEPTED — implemented and active

## Context
Five stakeholder portals expose different data and actions to different user
types. A student must not see raw investor mandate data; an investor must not
edit student achievement records; only an admin can trigger bulk data operations.
DRF's built-in `IsAuthenticated` is insufficient — role-level scoping is needed.

## Decision
Define a `BaseRolePermission` class and five concrete subclasses in
`apps/accounts/permissions.py`:

| Class | Allowed role |
|---|---|
| `IsStudent` | `student` |
| `IsAlumni` | `alumni` |
| `IsInvestor` | `investor` |
| `IsMentor` | `mentor` |
| `IsAdmin` | `admin` |

All classes:
- Require `request.user.is_authenticated` first.
- Read `request.user.role` (set on the custom `User` model via `UserRole`
  TextChoices).
- Return `True` only when the role matches.

Composite permission via DRF's `|` operator is supported where a view
legitimately serves multiple roles:
```python
permission_classes = [IsInvestor | IsMentor]
```

## Consequences
- Every ViewSet declares its own `permission_classes` explicitly — no implicit
  global default beyond `IsAuthenticated`.
- `IsAdmin` is used for internal data-management endpoints (bulk ingestion,
  model retraining triggers in Phase 8).
- Object-level permission (`has_object_permission`) is left to individual
  ViewSets where cross-profile data access must be blocked.

## Integration Notes
- Import from `apps.accounts.permissions` in any ViewSet or APIView.
- Add `IsAuthenticated` alongside the role class when a route requires both:
```python
  permission_classes = [IsAuthenticated, IsStudent]
```
- The `IsAdmin` class maps to `role == "admin"`, NOT to Django's `is_staff`
  or `is_superuser` — those remain for Django Admin panel access only.