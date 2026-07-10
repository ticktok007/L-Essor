# Synthetic Dataset — README
**Project:** Campus Innovation & Engagement Intelligence Hub
**Phase:** 1 — Synthetic Data Foundation
**Generator:** `scripts/generate_ecosystem_data.py`
**Seed:** 42 (fully reproducible — same seed always produces the same files)

---

## Files in This Directory

### `student_profiles.csv`
Synthetic current-student records.

| Field | Description |
|---|---|
| `student_id` | Unique ID — format `STU00001` |
| `full_name` | Realistic Indian name (Faker `en_IN`) |
| `email` | Unique fictional email |
| `role` | Always `student` |
| `cohort` | Entry–graduation year range e.g. `2022–2026` |
| `department` | Indian higher-education style department |
| `degree` | Full degree title matching department |
| `graduation_year` | 4 years after cohort entry |
| `current_status` | e.g. `Final Year Student`, `Startup Founder` |
| `skills` | Pipe-separated skill list e.g. `Python\|React\|ML` |
| `achievements_count` | Integer count of achievements (0–12) |

---

### `alumni_profiles.csv`
Synthetic graduated-alumni records.

| Field | Description |
|---|---|
| `alumni_id` | Unique ID — format `ALM00001` |
| `full_name` | Realistic Indian name |
| `email` | Unique fictional email |
| `role` | Always `alumni` |
| `cohort` | Entry–graduation year range |
| `department` | Department at time of study |
| `degree` | Degree title |
| `graduation_year` | Historical graduation year (2008–2025) |
| `current_company` | Realistic Indian tech / product company |
| `current_title` | Realistic job title |
| `employment_history` | JSON string — list of `{company, title, years}` |
| `skills` | Pipe-separated skill list |
| `mentorship_interest` | `yes` / `no` / `maybe` |

---

### `investor_mentor_profiles.csv`
Synthetic investor and mentor records (~50% each).

| Field | Description |
|---|---|
| `profile_id` | `INV00001` (investor) or `MEN00051` (mentor) |
| `full_name` | Realistic name |
| `email` | Unique fictional email |
| `role` | `investor` or `mentor` |
| `organization` | Fictional company name |
| `sector_focus` | Pipe-separated sectors e.g. `HealthTech\|EdTech` |
| `check_size_inr` | INR amount for investors; `0` for mentors |
| `expertise_tags` | Pipe-separated expertise areas |
| `mandate_text` | Short realistic investment thesis or mentorship offer |
| `engagement_preference` | `office_hours`, `async_review`, `warm_intro`, or `advisory_sessions` |

---

### `generation_summary.json`
Machine-readable summary of the generation run.

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
python scripts/generate_ecosystem_data.py
```

Deleting and re-running with the same seed produces byte-identical output.
To change record counts, edit the constants at the top of the script:
`NUM_STUDENTS`, `NUM_ALUMNI`, `NUM_INVESTORS_MENTORS`.

## Important
This data is entirely synthetic. It contains no real personal information.
It is safe for development, testing, CI pipelines, and demo presentations.
Do not commit real institutional data into this directory at any stage.