# Day 12 Vectorization Notes
**Project:** Campus Innovation & Engagement Intelligence Hub
**Phase:** 1 — Synthetic Data Foundation
**Files:** `data/generation/vectorized_generator.py`, `data/generation/distribution_enforcer.py`

---

## Scope
Rewrite generator hot loops as numpy vectorized operations; enforce strict
target-label class balance; benchmark before vs. after.

---

## Vectorization Changes

| Aspect | Before (slow) | After (vectorized) |
|---|---|---|
| Field generation | Per-row `random.Random` calls in a Python `for` loop | Bulk `np.random.default_rng` array ops: `rng.integers`, `rng.normal`, `rng.uniform` |
| Derived features | Scalar conditionals per row | `np.where` chains operating on full arrays |
| Labels | Scalar comparisons per row | Array comparisons producing boolean arrays cast to `int` |
| Final conversion | N/A | Single list comprehension over pre-computed arrays |

Helper functions (`compute_portfolio_scale`, `compute_success_label`,
`compute_at_risk_label`) accept both scalars and numpy arrays so they are
reusable in both the slow baseline and Django model methods.

Expected speedup at n=50,000: **10–30×** depending on hardware (numpy BLAS
vs. CPython interpreter overhead).

---

## Label Distribution Enforcement

`distribution_enforcer.py` provides:

| Function | Purpose |
|---|---|
| `enforce_binary_label_distribution` | Adjusts a single label to land within `[min_ratio, max_ratio]` |
| `enforce_all_targets` | Applies both label constraints sequentially |
| `summarize_label_distribution` | Returns counts and ratios for both labels |

**Flip strategy:** Non-random. Negatives with the highest `success_score` /
`risk_score` are flipped first when ratio is too low; positives with the
lowest score are flipped first when ratio is too high. Only the label field
is modified — feature columns are never touched.

**Required bounds:**
- `success_prediction_label`: [0.35, 0.65]
- `at_risk_label`: [0.20, 0.50]

---

## Benchmark Outputs
Run `python benchmarks/benchmark_vectorization.py` for a live JSON report.
Fields include `slow_avg`, `vectorized_avg`, `vectorized_enforce_avg`,
`speedup_ratio`, and label distributions before/after enforcement.

---

## Assumptions
- `numpy` is the only non-standard-library dependency introduced.
- Slow and vectorized generators do not need identical row-by-row output —
  they share schema and scoring rules, not RNG state.
- Label enforcement operates on the final list only; source feature columns
  (TRL, MRL, mentorship_hours, etc.) are never altered.
- `success_score` and `risk_score` are stored on every record to support
  borderline-first flipping without recomputation.