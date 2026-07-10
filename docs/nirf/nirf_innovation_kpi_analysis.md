# NIRF Innovation KPI Analysis
**Module:** NIRF Innovation Ranking — KPI Deep Dive
**Project:** Campus Innovation & Engagement Intelligence Hub
**Last updated:** Day 2, Phase 0 (Jul 07, 2026)
**Author:** Sanjay (24AM0100), Chennai Institute of Technology

---

## Overview

NIRF Innovation Ranking evaluates institutions across 5 parameters. This file covers
the 4 that this platform directly measures, tracks, or improves. The 5th (Teaching,
Learning & Resources) is out of scope for this platform.

| Parameter | Weightage |
|---|---|
| Financial Support for Innovation | 25% |
| Research & Innovation Output | 30% |
| Innovation Achievements | 15% |
| Pre-Incubation & Incubation | 10% |
| *(Teaching, Learning & Resources)* | *(20% — out of scope)* |

---

## 1. Financial Support for Innovation — 25%

### What NIRF is actually measuring
- Whether the institution **allocates real budget** toward innovation activities — seed funds, grants, and prizes awarded to students and startups.
- How many **funded projects** (internal grants, state/central scheme funds, industry-sponsored research) were active in the reporting year.
- The **total quantum of funding** disbursed, not just promised — NIRF cross-checks claimed figures against audited accounts.
- Whether **external funding** (DST-NIRF, SERB, BIRAC, industry CSR) was attracted — external grants signal ecosystem credibility beyond internal spend.
- Whether the institution has a **formal seed-fund or equity-free grant mechanism** for incubatees.

### Typical data sources on campus today
- Accounts/finance department spreadsheets (grant disbursements per project)
- Incubation cell's own MoU and funding-round records
- Individual faculty/student grant applications and awards (scattered, often in email)
- State/central government scheme portals (DST, TIDE 2.0, AIM, etc.)

### How the platform helps
- The **Startup Progress Tracker** stores every milestone funding event (seed, grant, angel round) as a timestamped record — gives finance/admin a single queryable source instead of chasing email trails.
- The **Investor Matchmaking Engine** directly improves the probability of a startup closing a round, which creates a real funding event that goes into the NIRF count.
- The **Leadership Analytics Dashboard** aggregates total funds mobilised per semester, auto-formatted for NIRF submission — no manual spreadsheet assembly.
- The **predictive success model (XGBoost)** flags which startups are closest to a fundable milestone — admin can prioritise seed-fund allocation toward highest-ROI candidates.

---

## 2. Research & Innovation Output — 30%

### What NIRF is actually measuring
- **Patent filings and grants** — Indian and international, weighted by grant status.
- **Publications** in peer-reviewed journals (SCI/Scopus indexed) by students and faculty connected to innovation programs.
- **Technology Transfer / Licensing** events where an innovation moves from lab to market.
- **Startup spin-offs** that originated from research — shows research → commercialisation pipeline health.
- The **quality of output**, not just quantity — NIRF scores granted patents higher than filed; licensed tech higher than benchtop demo.

### Typical data sources on campus today
- Research cell's patent registry (Excel, rarely current)
- Scopus/Web of Science exports (faculty-level, not student-level)
- Manual annual report compiled by the IQAC/R&D cell
- Technology transfer records (if any) in incubation center files

### How the platform helps
- The **Achievement Tracker** records patent filings, journal publications, and licensing events against specific student/alumni/startup profiles — replaces the scattered research-cell spreadsheet.
- **DistilBERT NER** extracts publication titles, patent numbers, and co-inventor names directly from uploaded certificates/PDFs, reducing manual data entry to near-zero.
- The **Portfolio Generator** auto-tags each achievement as Patent / Publication / Tech Transfer using TF-IDF + LDA — these tags map directly to NIRF sub-metric categories.
- The **Graph Intelligence layer (NetworkX)** identifies research collaboration clusters across departments — a metric NIRF implicitly values through cross-functional innovation output.

---

## 3. Innovation Achievements — 15%

### What NIRF is actually measuring
- **Awards and recognition** in national/international competitions (Smart India Hackathon, TOYCATHON, NASA Space Apps, etc.).
- **Medals, prizes, and ranks** obtained by students at NIRF-recognised events — events need to be on an approved list.
- **Proof of participation** in challenge-based programs, not just enrolment — outcome evidence required.
- Whether achievements are **institution-wide or limited to one department** — breadth matters.
- **Year-over-year growth** in participation volume and win rate — NIRF rewards improving trajectory, not just absolute count.

### Typical data sources on campus today
- Club organisers' WhatsApp groups and Excel sheets (ad-hoc, siloed by club)
- Student council records (rarely complete)
- Individual student certificates (physical, un-digitised)
- Placement cell records (only for final-year wins that appear on CVs)

### How the platform helps
- The **Competition & Achievement Tracker** creates one centralised log of every competition entered, rank achieved, and prize won — across all clubs, departments, and cohorts.
- **DistilBERT NER** extracts event name, date, rank, and prize from uploaded certificates — eliminating manual data entry.
- The **Student Portal's Achievement Timeline** makes participation visible to the student themselves — visibility drives participation (directly maps to PS success criterion #3: +35% competition participation).
- The **Leadership Dashboard** shows cross-departmental achievement breadth, trend charts per semester, and win-rate trajectory — exactly the trajectory narrative NIRF rewards.
- The **Graph Intelligence layer** identifies under-participating cohorts/departments so admin can intervene proactively.

---

## 4. Pre-Incubation & Incubation — 10%

### What NIRF is actually measuring
- Whether the institution has a **functional, physical incubation facility** with verified occupancy.
- The **number of active incubatees** and the quality of support they receive (mentoring hours, workshops, investor access).
- **Startup survival and graduation rates** — startups that exit incubation and operate independently are scored highest.
- Whether there is a **structured pre-incubation pathway** (ideation → validation → prototype → incubation) rather than direct admission.
- **MoU count with industry and investors** — formalised ecosystem relationships, not just informal goodwill.

### Typical data sources on campus today
- Incubation cell's own admission and occupancy register
- Mentor visit logs (paper-based or sporadic email threads)
- Workshop attendance sheets (physically signed, rarely digitised)
- Startup exit/survival records (most cells do not track post-exit)

### How the platform helps
- The **Startup Progress Tracker** records every incubatee milestone — admission, pre-incubation stage completion, prototype, funding, exit — building the survival-and-graduation audit trail NIRF requires.
- The **Mentor Matchmaking Engine (KNN)** and **mentorship_hours** field directly produce the "mentoring support provided" metric NIRF asks for.
- The **Incubation Cell Portal** gives admins a live roster with startup stage, TRL level, and days-in-incubation — replacing the occupancy register.
- The **Predictive Model (XGBoost / at-risk classifier)** flags incubatees likely to stall before graduation, enabling proactive support — directly improving the survival rate NIRF scores.
- The **MoU / Industry Partner records** (stored as Investor/Mentor profile connections) give a queryable count of formalised ecosystem relationships.

---

*Next: see `nirf_kpi_feature_traceability.md` for the direct KPI → platform feature mapping.*
