# Phase 0 · Day 1 — Success Criteria Scorecard & User Personas
**Campus Innovation & Engagement Intelligence Hub**
*Logged: Monday, Jul 06, 2026 — Day 1 of 115*

> Source: original hackathon problem statement, "Problem Statement 4: Campus
> Innovation & Engagement Intelligence Hub" — re-read line-by-line as the
> first task of Phase 0.

---

## 1. Measurable Success Criteria — Tracked Scorecard

| # | Success Criterion (as stated in the PS) | Target | How It Will Be Measured | Primary Module | Baseline (Day 1) | Status |
|---|---|---|---|---|---|---|
| 1 | Alumni engagement rate | ≥ 40% increase | % of alumni actively logging in, connecting, or updating their profile per term, vs. pre-platform baseline | Matchmaking (Ph.3) + Alumni Portal (Ph.7) | No platform exists yet | 🔴 Not started |
| 2 | Startup funding success rate | +30% via better investor matching | % of platform-matched startups closing a funding round within 2 semesters of being matched | Investor matching — cosine similarity (Ph.3) | No matching mechanism exists | 🔴 Not started |
| 3 | Student competition participation | +35% via better visibility | % of eligible students registering/attending ≥1 competition per semester | Graph Intelligence (Ph.5) + Event Portal (Ph.7) | Unknown — no centralized tracking today | 🔴 Not started |
| 4 | Mentor–mentee connections | ≥ 50 meaningful connections / semester | Count of mentor↔mentee matches initiated **and** accepted via the platform | Mentor matching — KNN (Ph.3) | 0 (pre-platform) | 🔴 Not started |
| 5 | Alumni profile completion | 80% complete (employment + achievements) | % of alumni profiles with all required fields filled | Portfolio Generator (Ph.6) + Alumni Portal (Ph.7) | 0% | 🔴 Not started |
| 6 | NIRF/ARIIA-aligned innovation KPIs | "Measurable KPIs" (no numeric target given in the PS) | Direct 1:1 dashboard mapping to NIRF's 4 weighted categories: Financial Support (25%), Research/Innovation Output (30%), Innovation Achievements (15%), Pre-/Incubation (10%) | Leadership Analytics Dashboard (Ph.7) | No such mapping exists today | 🔴 Not started |
| 7 | Digital portfolios for graduates | 100% of graduating cohort | % of graduating students with an auto-generated portfolio PDF on file | Automated Portfolio Generator (Ph.6) | 0% | 🔴 Not started |

### Observations

- **Criteria 1, 2, 3 are relative (%), not absolute — a real baseline matters.** "40% increase" is meaningless without a starting number. Recommend a quick parallel side-task: pull whatever scattered current data exists (last semester's event attendance sheets, the alumni cell's spreadsheet, past funding rounds) into a rough Day-1 baseline. Evaluators explicitly score "Measurable Impact and Business Value" — showing a real before/after number, even a rough one, is far stronger than an assumed 0.
- **Criterion 6 is the only vague one.** Everything else has a hard number; this one just says "generate measurable innovation KPIs." Treat the 4 NIRF weightage percentages (found later in the source doc) as the de facto target, since that's the only concrete anchor available.
- **Criteria 4 and 7 are binary/countable**, not rate-based — easiest to demo convincingly to evaluators since they don't need a "before" number to be credible.
- **Every criterion maps to a module already scheduled in the 115-day plan** — none of the 7 require scope not already covered by Phases 3, 5, 6, or 7.

---

## 2. User Personas

### 🎓 Student
- **Who:** Current students and student entrepreneurs (incl. incubatees running their own startup)
- **Goal:** Build a visible track record; find the right teammates, mentors, or competitions; get discovered if building something real
- **Pain today:** Achievements are scattered across WhatsApp screenshots, paper certificates, and memory — invisible outside their own department or club
- **Wants from the platform:** One place to log wins, a matchmaking nudge toward relevant mentors/teammates, a portfolio that builds itself

### 🎉 Alumni
- **Who:** Alumni network across cohorts and industries
- **Goal:** Stay loosely connected and give back (mentor, refer, occasionally invest) without high effort
- **Pain today:** The institution has no reliable channel beyond a stale spreadsheet; there's no incentive to keep a profile updated
- **Wants from the platform:** A profile that's low-friction to maintain, light-touch ways to mentor or engage, visibility into what's happening on campus now

### 💰 Investor / VC
- **Who:** Investors, venture capitalists, and angel investors evaluating student/alumni startups
- **Goal:** Find genuinely promising, vetted deals without wading through unfiltered noise
- **Pain today:** No signal on which pitches are credible vs. hype; no visibility into TRL, traction, or founder history
- **Wants from the platform:** A ranked, compatibility-scored shortlist matched to their stated sector/mandate, backed by real traction data

### 🧑‍🏫 Mentor
- **Who:** Mentors and industry experts (including technical/cultural club domain experts)
- **Goal:** Spend limited time on well-matched mentees, not random assignments
- **Pain today:** Matching is ad hoc (whoever asks first, or whoever a coordinator remembers); mentor time gets wasted on mismatched pairings
- **Wants from the platform:** A compatibility-matched mentee shortlist by skills/interest overlap, and dead-simple session logging

### 🏢 Incubation-Cell Admin
- **Who:** Incubation center and entrepreneurship cell staff overseeing startups and incubatees
- **Goal:** Track every startup's funding stage and health, catch at-risk founders/students early, run competitions efficiently
- **Pain today:** Fragmented spreadsheets per cohort; no predictive signal on who's disengaging until it's too late
- **Wants from the platform:** A single roster view with success-probability and at-risk flags, plus one place to manage events and participation

### 🏛️ Leadership
- **Who:** Institutional leadership, placement cells, and the bodies reporting to accreditation/ranking committees
- **Goal:** Report accurate NIRF/ARIIA-aligned innovation metrics; demonstrate ecosystem ROI to the board
- **Pain today:** No unified analytics — assembling NIRF submission data today is a manual, error-prone scramble every cycle
- **Wants from the platform:** A live dashboard mapped directly to the 4 NIRF weightage categories, always audit-ready

---
*Logged as part of Phase 0 → Day 1: Project Kickoff & Charter. Next up: Day 2 — NIRF/ARIIA compliance mapping.*
