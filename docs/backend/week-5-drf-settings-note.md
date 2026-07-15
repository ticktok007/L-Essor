# DRF Settings Patch — Week 5
**Project:** Campus Innovation & Engagement Intelligence Hub
**Delivered:** Week 5, Phase 2

## Required Settings Updates

### 1. Add `django-filter` to `INSTALLED_APPS` in `campushub/settings/base.py`

```python
INSTALLED_APPS = [
    # ... existing apps ...
    "django_filters",   # ← add this
]
```

### 2. Add `DjangoFilterBackend` to `REST_FRAMEWORK` in `campushub/settings/base.py`

```python
REST_FRAMEWORK = {
    # ... existing keys ...
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
}
```

### 3. Add to `requirements.txt`

django-filter>=24.0,<25.0

Then install:

```bash
pip install django-filter
```

## Third-Party Dependency
`django-filter` — provides `DjangoFilterBackend` and the `filterset_fields`
declarative filtering used by all six ViewSets in `apps/ecosystem/views.py`.

## Exit Status
Apply these three changes before running the ViewSet integration tests in Week 6.