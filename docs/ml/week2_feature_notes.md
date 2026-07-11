# Week 2 Feature Engineering Notes
**Project:** Campus Innovation & Engagement Intelligence Hub
**Phase:** 1 — Predictive Analytics Pipeline Prep
**Files:** `ml/features/success_features.py`, `ml/features/target_labels.py`

---

## Scope
Engineering five predictive features and two binary ML target labels from
synthetic profile and startup records. All logic is deterministic, pure-function,
and dependency-free (standard library only).

---

## Engineered Features

| Feature | Module | Logic |
|---|---|---|
| `trl_mrl_gap` | `success_features` | `TRL - MRL`; both clamped to [1–9]; missing → 1 |
| `mentorship_hours` | `success_features` | Explicit field preferred; else `sessions × avg_duration`; non-negative |
| `competitions_participated` | `success_features` | Explicit field preferred; else count from `competitions` list |
| `competitions_won` | `success_features` | Same derivation; enforced ≤ participated |
| `portfolio_achievement_scale_1_to_10` | `success_features` | Weighted tiers: achievements (4 pts) + wins (2 pts) + leadership (2 pts) + portfolio breadth (2 pts); clamped to [1–10] |

All feature weights and thresholds are defined as module-level constants for
auditability and recalibration in Phase 4.

---

## Target Labels

### `success_prediction_label` (binary, 0/1)
Score-based; threshold = 6. Signals:
- `mentorship_hours` ≥ 20 → +2; ≥ 8 → +1
- `competitions_won` ≥ 2 → +2; = 1 → +1
- `portfolio_scale` ≥ 8 → +2; ≥ 5 → +1
- `trl_mrl_gap` ∈ [−1, 2] → +2; ∈ [−3, 3] → +1
- `funding_stage` in approved set → +1
- traction (users / revenue / pilots) → max +1

### `at_risk_label` (binary, 0/1 where 1 = at risk)
Risk-score-based; threshold = 5. Signals:
- `mentorship_hours` < 2 → +2; < 6 → +1
- `competitions_participated` = 0 → +2; ≤ 1 → +1
- `competitions_won` = 0 → +1
- `portfolio_scale` ≤ 2 → +2; ≤ 4 → +1
- `last_active_days_ago` > 45 → +2; > 21 → +1
- `submissions_count_last_90_days` = 0 → +2; ≤ 2 → +1

---

## Assumptions
- All inputs are Python dicts; missing keys fall back to documented defaults.
- `portfolio_achievement_scale` uses `competitions_won` internally — ensure
  `competitions_participated/won` are computed before calling it in pipelines.
- Label thresholds (6 for success, 5 for at-risk) are scaffolding values;
  recalibrate against real outcomes after institutional onboarding in Phase 10.
- `at_risk_label` optional signals (`last_active_days_ago`,
  `submissions_count_last_90_days`) are silently skipped when absent — the
  label remains valid on partial records.