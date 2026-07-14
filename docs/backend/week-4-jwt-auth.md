# JWT Authentication Setup
**Project:** Campus Innovation & Engagement Intelligence Hub
**Delivered:** Week 4, Phase 2

## Status
ACCEPTED — implemented and active

## Context
The platform serves six distinct roles across five stakeholder portals. Every API
endpoint must know who is calling and what role they hold before applying
business logic. Session-based auth is unsuitable for a decoupled React frontend.
A stateless JWT approach fits the architecture and the planned Celery async layer.

## Decision
Use `djangorestframework-simplejwt` for token issuance and verification.

- Access token lifetime: 60 minutes
- Refresh token lifetime: 7 days
- Token refresh rotation: disabled (stateless, simpler)
- Auth header: `Authorization: Bearer <token>`
- Custom token claim: `role` injected via a custom `TokenObtainPairSerializer`
  so the frontend knows the user's role on login without a second API call.

## Consequences
- Every protected DRF endpoint requires a valid `Bearer` token.
- Role is available in the token payload — no DB hit needed to resolve role on
  every request.
- Token blacklisting is not enabled in Phase 2; logout is client-side
  (discard the token). Blacklisting can be enabled in Phase 8 if required.
- Refresh token rotation is off — simpler for the current scale.

## Integration Notes
- `SIMPLE_JWT` config lives in `config/jwt.py` and is imported into `base.py`.
- `DEFAULT_AUTHENTICATION_CLASSES` in `REST_FRAMEWORK` is set to
  `JWTAuthentication` from simplejwt.
- Token obtain route: `POST /api/v1/auth/token/`
- Token refresh route: `POST /api/v1/auth/token/refresh/`
- Custom serializer (`CustomTokenObtainPairSerializer`) adds `role` and
  `full_name` to the token response body.