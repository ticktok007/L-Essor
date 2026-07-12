# Generator Review Checklist
**Project:** Campus Innovation & Engagement Intelligence Hub
**Phase:** 1 — Data Validation & QA
**Use for:** Self-review before merge and peer-review on PR

---

## Scope
Applies to any commit that modifies a file under `scripts/`, `data/generation/`,
or `data/text/`. Each item must be checked before the PR is approved.

---

## Checklist

### Schema Alignment
- [ ] Every generated CSV column matches the corresponding table definition in `docs/data/master-schema.md`
- [ ] Column names use snake_case and match exactly (no trailing spaces, no case drift)
- [ ] No extra undocumented columns appear in output files
- [ ] JSON summary file includes `generated_files` map with correct row counts

### Determinism / Seed Handling
- [ ] All randomness is controlled by a `seed` parameter with a clear default (42)
- [ ] Running the script twice with the same seed produces byte-identical CSV output
- [ ] Seed is recorded in the JSON summary file
- [ ] No use of `datetime.now()`, `uuid4()` without seed, or any non-deterministic source

### Referential Integrity Guarantees
- [ ] `startup_founder_links.startup_id` values are drawn only from `startup_profiles.startup_id`
- [ ] `startup_funding_timeline.startup_id` values are drawn only from `startup_profiles.startup_id`
- [ ] `founder_count` in `startup_profiles` equals the number of founder-link rows generated per startup
- [ ] `competition_records.profile_id` and `achievement_records.profile_id` follow `STU-####` or `ALU-####` format

### Realism of Categorical / Text Generation
- [ ] No funding stage exceeds 60% of total startup records
- [ ] All defined funding stages appear at least once at target scale
- [ ] Pitch summaries use multi-frame variation (not the same sentence skeleton every row)
- [ ] Unique pitch text ratio ≥ 0.80 for any batch of 60+ records
- [ ] Mandate texts for investors and mentors use distinct frame families
- [ ] Degree distribution in interaction edges shows hub-and-spoke shape (confirmed by plot)

### Statistical Sanity Checks Passing
- [ ] `success_prediction_label` positive ratio is in [0.35, 0.65]
- [ ] `at_risk_label` positive ratio is in [0.20, 0.50]
- [ ] Zero nulls in all required non-null columns
- [ ] All numeric features within declared bounds
- [ ] `competitions_won` ≤ `competitions_participated` for every row
- [ ] `sanity_check_report.json` shows zero hard failures

### Plot Review Completed
- [ ] Funding stage distribution plot reviewed — no single stage dominant
- [ ] AIS histogram reviewed — visible spread, no degenerate spike
- [ ] Degree distribution plot reviewed — hub-and-spoke shape confirmed
- [ ] Grit histogram reviewed — not degenerate
- [ ] Label balance chart reviewed — both labels within bounds
- [ ] Review flag distribution reviewed — all four flags present

### Code Clarity and Maintainability
- [ ] Record counts are defined as top-level constants, not magic numbers inline
- [ ] No `TODO`, `FIXME`, stub, or pseudocode remains
- [ ] Generator is runnable directly (`python scripts/<name>.py`) with no arguments required
- [ ] Output directory is created automatically (`mkdir(parents=True, exist_ok=True)`)
- [ ] Each generator has a `main()` function and `if __name__ == "__main__"` guard
- [ ] No dependency on external APIs, live data, or environment-specific paths

---

## Merge Gate

**A PR modifying any generator may not be merged unless all of the following are true:**

1. All checklist items above are ticked
2. `sanity_check_report.json` shows zero hard failures
3. All six distribution plots have been reviewed and pass their criteria
4. At least one other team member (or a self-review comment) has confirmed determinism by re-running the script independently