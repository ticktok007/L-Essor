# Distribution Visualization Specification
**Project:** Campus Innovation & Engagement Intelligence Hub
**Phase:** 1 — Data Validation & QA

---

## Scope
Visual sanity checks run after each full generator run to detect degenerate
or obviously artificial distributions before data is used for ML training.
All plots saved to `data/processed/plots/`.

---

## Required Plots

### 1. Funding Stage Count Chart
- **File:** `funding_stage_distribution.png`
- **Source:** `data/synthetic/startup_profiles.csv`, column `funding_stage`
- **Type:** Horizontal bar chart
- **X-axis:** Count of startups per stage
- **Y-axis:** Funding stage labels
- **Purpose:** Confirm no single stage dominates > 60% of records; confirm all
  defined stages appear at least once

### 2. Achievement Impact Score (AIS) Histogram
- **File:** `ais_histogram.png`
- **Source:** `data/processed/profile_feature_scores.csv`, column `ais_normalized`
- **Type:** Histogram with ~20 bins over range [0, 100]
- **X-axis:** AIS normalized score (0–100)
- **Y-axis:** Profile count
- **Purpose:** Confirm distribution is spread (not a spike at 0, 50, or 100);
  should be roughly bell-shaped or moderately right-skewed

### 3. Degree Distribution Plot
- **File:** `degree_distribution.png`
- **Source:** `data/synthetic/interaction_edges.csv`, columns `source_profile_id`
  and `target_profile_id`
- **Type:** Bar or histogram of node degree counts
- **X-axis:** Node degree (number of edges per node)
- **Y-axis:** Number of nodes with that degree
- **Purpose:** Confirm hub-and-spoke shape (few high-degree nodes, many
  low-degree nodes); a flat distribution indicates unrealistic uniform random
  connectivity

### 4. Grit Index Histogram
- **File:** `grit_histogram.png`
- **Source:** `data/processed/profile_feature_scores.csv`, column `grit_normalized`
- **Type:** Histogram with ~20 bins over range [0, 100]
- **Purpose:** Confirm distribution is not degenerate; should show spread across
  the range with a modest right skew

### 5. Target Label Balance Bar Charts
- **File:** `label_balance.png`
- **Source:** `data/processed/profile_feature_scores.csv`
- **Type:** Side-by-side bar chart: positive vs. negative count for each label
- **Purpose:** Visual confirmation that both labels are within required bounds;
  immediately reveals all-zero or all-one label problems

### 6. Review Flag Distribution
- **File:** `review_flag_distribution.png`
- **Source:** `data/processed/profile_feature_scores.csv`, column `review_flag`
- **Type:** Horizontal bar chart
- **Purpose:** Confirm all four review-flag categories appear; no single flag
  exceeds 70% of profiles

---

## Review Criteria

| Plot | Pass Criterion |
|---|---|
| Funding stage count | No stage > 60%; all stages present |
| AIS histogram | Visible spread across [0, 100]; no single bin > 40% of records |
| Degree distribution | Clear hub-and-spoke shape; max degree >> mean degree |
| Grit histogram | Spread across [0, 100]; not a spike |
| Label balance | Both labels within required ratio bounds |
| Review flag distribution | All four flags present; no flag > 70% |

---

## Output Artifacts

- `data/processed/plots/funding_stage_distribution.png`
- `data/processed/plots/ais_histogram.png`
- `data/processed/plots/degree_distribution.png`
- `data/processed/plots/grit_histogram.png`
- `data/processed/plots/label_balance.png`
- `data/processed/plots/review_flag_distribution.png`