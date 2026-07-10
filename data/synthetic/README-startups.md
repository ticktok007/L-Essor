# Synthetic Startup Dataset — README
**Project:** Campus Innovation & Engagement Intelligence Hub
**Phase:** 1 — Synthetic Data Foundation
**Generator:** `scripts/generate_startup_data.py`
**Seed:** 42 (fully reproducible)

---

## Files in This Directory

### `startup_profiles.csv`
One row per startup. Core entity record for the Startup Progress Tracker
and AI Matchmaking Engine.

| Field | Description |
|---|---|
| `startup_id` | Unique ID — format `STA00001` |
| `startup_name` | Fictional startup name |
| `sector` | Primary sector e.g. `HealthTech`, `EdTech` |
| `subsector` | Sub-domain within sector |
| `funding_stage` | `pre-seed` / `seed` / `grant` / `series-a` / `bootstrapped` |
| `trl_level` | Technology Readiness Level 1–9; aligned with `funding_stage` |
| `founded_year` | Year of founding; logically consistent with stage |
| `hq_city` | City from realistic Indian cities list |
| `team_size` | Headcount consistent with stage maturity |
| `pitch_summary` | 2–3 sentence pitch built from vocabulary bank |
| `problem_statement` | Specific problem statement from vocabulary bank |
| `solution_summary` | Specific solution from vocabulary bank |
| `traction_signal` | Stage-appropriate traction description |
| `founder_count` | Matches number of rows in `startup_founder_links.csv` for this startup |

---

### `startup_vocabulary_bank.csv`
Phrase library used by the text generation logic to produce varied, realistic
pitch text. Referenced at generation time — not an entity table.

| Field | Description |
|---|---|
| `vocab_id` | Unique ID — format `VOC00001` |
| `sector` | Sector this phrase belongs to |
| `phrase_type` | `problem` / `solution` / `customer` / `moat` / `traction` / `technology` |
| `phrase` | The phrase itself — realistic, sector-specific language |

---

### `startup_founder_links.csv`
Cross-link table between startups and their founder profiles. References
student or alumni IDs from the broader ecosystem dataset.

| Field | Description |
|---|---|
| `link_id` | Unique ID — format `FL00001` |
| `startup_id` | FK → `startup_profiles.startup_id` |
| `founder_profile_id` | `STU-####` (student) or `ALU-####` (alumni) |
| `founder_role` | Functional role: `CEO`, `CTO`, `CPO`, etc. |
| `founder_title` | Full title e.g. `Co-Founder & CTO` |
| `ownership_band` | Equity band e.g. `25–30%` |
| `is_primary_contact` | `yes` for first founder; `no` for others |

**Integrity rule:** Count of rows per `startup_id` equals `founder_count` in `startup_profiles.csv`.

---

### `startup_funding_timeline.csv`
Ordered sequence of funding and milestone events per startup. Used by the
Startup Progress Tracker, NIRF Financial Support metric, and the XGBoost
success predictor's temporal features.

| Field | Description |
|---|---|
| `event_id` | Unique ID — format `EV000001` |
| `startup_id` | FK → `startup_profiles.startup_id` |
| `event_date` | ISO date; chronologically ordered per startup |
| `event_type` | e.g. `incubated`, `grant_received`, `seed_round`, `revenue_milestone` |
| `stage_at_event` | Funding stage at the time of this event |
| `amount_in_inr` | INR amount; `0` where not applicable |
| `milestone_note` | Short realistic description of what happened |

**Integrity rule:** Final event's `stage_at_event` aligns with `startup_profiles.funding_stage`.

---

### `startup_generation_summary.json`
Machine-readable run summary.

| Field | Description |
|---|---|
| `project` | Project name |
| `phase` | Build phase |
| `seed` | Random seed used |
| `generated_files` | Map of filename → row count |
| `total_records` | Sum of all rows across all files |
| `note` | Confirms no real PII |

---

## Regenerating

```bash
pip install faker
python scripts/generate_startup_data.py
```

Same seed always produces byte-identical output.
To scale up, edit the constant at the top of the script: `NUM_STARTUPS`.

## Important
All data is entirely synthetic. No real company names, founder identities,
or funding amounts are used. Safe for development, testing, CI, and demo.
Do not commit real institutional startup data into this directory.