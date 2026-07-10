# NIRF Leadership Dashboard — Design Spec
**Module:** NIRF Innovation Ranking — Dashboard Design
**Project:** Campus Innovation & Engagement Intelligence Hub
**Last updated:** Day 2, Phase 0 (Jul 07, 2026)
**Author:** Sanjay (24AM0100), Chennai Institute of Technology

> All card names, chart titles, and metric names in this file match
> `nirf_kpi_feature_traceability.md` exactly. Phase 7 implementation must not
> rename them.

---

## 1. Page Identity

| Property | Value |
|---|---|
| Route | `/dashboard/leadership/nirf` |
| Access role | `IsLeadership`, `IsAdmin` |
| React page component | `NIRFDashboardPage` |
| Backend permission class | `IsLeadershipOrAdmin` |
| Primary data fetch | `GET /api/v1/analytics/nirf/summary/` (aggregates all 4 sections) |
| Refresh cadence | On page load + manual "Refresh" button; no auto-poll (data is not real-time) |

---

## 2. Page Layout — Section Map

─────────────────────────────────────────────────────────┐
│  Header: NIRF Innovation Dashboard          [Refresh] [Export PDF] │
│  Subtitle: Reporting period selector  ←semester/year→          │
├───────────────────────────────────────────────────────────┤
│  SECTION A — NIRF Score Summary Strip (4 KPI score cards)        │
├───────────────────────────────────────────────────────────┤
│  SECTION B — Financial Support (25%)                              │
├───────────────────────────────────────────────────────────┤
│  SECTION C — Research & Innovation Output (30%)                   │
├───────────────────────────────────────────────────────────┤
│  SECTION D — Innovation Achievements (15%)                        │
├───────────────────────────────────────────────────────────┤
│  SECTION E — Pre-Incubation & Incubation (10%)                    │
├───────────────────────────────────────────────────────────┤
│  SECTION F — At-Risk Alerts Panel                                 │
└─────────────────────────────────────────────────────────┘


---

## 3. Section A — NIRF Score Summary Strip

**Component:** `NIRFScoreSummaryStrip`

Four side-by-side score cards, one per KPI. Each card shows:
- KPI name + weightage %
- Platform readiness % (how many required metrics have non-zero data)
- A coloured ring (green ≥ 80%, amber 50–79%, red < 50%)

| Card Title | Weightage | Readiness Source |
|---|---|---|
| Financial Support | 25% | `/api/v1/analytics/nirf/financial-support/` |
| Research & Innovation Output | 30% | `/api/v1/analytics/nirf/research-output/` |
| Innovation Achievements | 15% | `/api/v1/analytics/nirf/innovation-achievements/` |
| Pre-Incubation & Incubation | 10% | `/api/v1/analytics/nirf/incubation/` |

---

## 4. Section B — Financial Support (25%)

**Component:** `FinancialSupportSection`

| UI Element | Type | Metric Name | Endpoint |
|---|---|---|---|
| Total Funds Mobilised | Stat card (₹ value) | `total_funds_mobilised_inr` | `/api/v1/analytics/nirf/financial-support/` |
| Active Funded Projects | Stat card (count) | `active_funded_projects_count` | `/api/v1/analytics/nirf/financial-support/` |
| Investor Matches Converted | Stat card (count) | `investor_matches_converted` | `/api/v1/analytics/nirf/financial-support/` |
| Funds Mobilised Over Time | Line chart (semester × axis) | `total_funds_mobilised_inr` per semester | `/api/v1/analytics/nirf/financial-support/?group_by=semester` |
| High-Probability Fundable Startups | Ranked list (top 5) | `high_probability_fundable_startups` | `/api/v1/predict/startup-success/` |

**Sub-components:** `FundsLineChart`, `FundableStartupsList`

---

## 5. Section C — Research & Innovation Output (30%)

**Component:** `ResearchOutputSection`

| UI Element | Type | Metric Name | Endpoint |
|---|---|---|---|
| Patent Filings | Stat card | `patent_filings_count` | `/api/v1/analytics/nirf/research-output/` |
| Publications | Stat card | `publications_count` | `/api/v1/analytics/nirf/research-output/` |
| Tech Transfer Events | Stat card | `tech_transfer_events_count` | `/api/v1/analytics/nirf/research-output/` |
| Portfolios with Research Output | Stat card (%) | `portfolios_with_research_output_pct` | `/api/v1/analytics/nirf/research-output/` |
| Cross-Dept Collaboration Score | Gauge chart (0–1) | `cross_dept_collaboration_score` | `/api/v1/graph/ecosystem/` |
| Output Breakdown | Donut chart (patent / pub / transfer) | All three counts | `/api/v1/analytics/nirf/research-output/` |
| Output Over Time | Bar chart (semester × axis, stacked by type) | All three counts per semester | `/api/v1/analytics/nirf/research-output/?group_by=semester` |

**Sub-components:** `ResearchOutputDonut`, `ResearchOutputBarChart`, `CollaborationGauge`

---

## 6. Section D — Innovation Achievements (15%)

**Component:** `InnovationAchievementsSection`

| UI Element | Type | Metric Name | Endpoint |
|---|---|---|---|
| Competition Wins (Top-3) | Stat card | `competition_wins_count` | `/api/v1/analytics/nirf/innovation-achievements/` |
| Total Participation | Stat card | `competition_participation_count` | `/api/v1/analytics/nirf/innovation-achievements/` |
| Participation Rate | Stat card (%) + trend arrow | `competition_participation_rate_pct` | `/api/v1/analytics/nirf/innovation-achievements/` |
| Cross-Dept Breadth | Stat card (dept count) | `cross_dept_participation_breadth` | `/api/v1/analytics/nirf/innovation-achievements/` |
| Participation Rate Over Time | Line chart (semester × axis) | `competition_participation_rate_pct` per semester | `/api/v1/analytics/nirf/innovation-achievements/?group_by=semester` |
| Achievements by Department | Horizontal bar chart | `competition_participation_count` grouped by dept | `/api/v1/analytics/nirf/innovation-achievements/?group_by=department` |

**Sub-components:** `ParticipationRateLineChart`, `AchievementsByDeptChart`

---

## 7. Section E — Pre-Incubation & Incubation (10%)

**Component:** `IncubationSection`

| UI Element | Type | Metric Name | Endpoint |
|---|---|---|---|
| Active Incubatees | Stat card | `active_incubatees_count` | `/api/v1/analytics/nirf/incubation/` |
| Mentorship Hours Logged | Stat card | `total_mentorship_hours_logged` | `/api/v1/analytics/nirf/incubation/` |
| Startup Graduation Rate | Stat card (%) | `startup_graduation_rate_pct` | `/api/v1/analytics/nirf/incubation/` |
| Industry MoU Count | Stat card | `industry_mou_count` | `/api/v1/analytics/nirf/incubation/` |
| Incubatee Stage Funnel | Funnel chart (pre-incubation → prototype → active → graduated) | Stage counts from `startups.incubation_status` | `/api/v1/analytics/nirf/incubation/` |
| Mentorship Hours Over Time | Area chart (semester × axis) | `total_mentorship_hours_logged` per semester | `/api/v1/analytics/nirf/incubation/?group_by=semester` |

**Sub-components:** `IncubationFunnelChart`, `MentorshipAreaChart`

---

## 8. Section F — At-Risk Alerts Panel

**Component:** `AtRiskAlertsPanel`

Two alert lists, always visible at the bottom:

| List | Metric | Endpoint | Action Button |
|---|---|---|---|
| At-Risk Incubatees | `at_risk_incubatees_count` + names | `/api/v1/predict/engagement-risk/?entity=startup` | "Assign Mentor" |
| At-Risk Departments (low participation) | `at_risk_departments_list` | `/api/v1/predict/engagement-risk/?entity=department` | "Send Outreach" |

---

## 9. Export

**Component:** `NIRFExportButton`
- Triggers `GET /api/v1/analytics/nirf/export/?format=pdf`
- Backend renders a Django HTML template → wkhtmltopdf PDF
- Output is an audit-ready single-page summary with all 19 metrics, period label, and institution name
- Used directly for NIRF submission data compilation

---

## 10. React Component Tree (Phase 7 reference)

NIRFDashboardPage
├── NIRFDashboardHeader
│   ├── PeriodSelector
│   └── NIRFExportButton
├── NIRFScoreSummaryStrip
│   └── NIRFScoreCard × 4
├── FinancialSupportSection
│   ├── StatCard × 3
│   ├── FundsLineChart
│   └── FundableStartupsList
├── ResearchOutputSection
│   ├── StatCard × 4
│   ├── ResearchOutputDonut
│   ├── ResearchOutputBarChart
│   └── CollaborationGauge
├── InnovationAchievementsSection
│   ├── StatCard × 4
│   ├── ParticipationRateLineChart
│   └── AchievementsByDeptChart
├── IncubationSection
│   ├── StatCard × 4
│   ├── IncubationFunnelChart
│   └── MentorshipAreaChart
└── AtRiskAlertsPanel
├── AtRiskIncubateesList
└── AtRiskDepartmentsList

---

## 11. Backend Endpoints Summary (Phase 7 DRF routes)

GET  /api/v1/analytics/nirf/summary/                   # all 4 KPIs, one response
GET  /api/v1/analytics/nirf/financial-support/         # Section B data
GET  /api/v1/analytics/nirf/research-output/           # Section C data
GET  /api/v1/analytics/nirf/innovation-achievements/   # Section D data
GET  /api/v1/analytics/nirf/incubation/                # Section E data
GET  /api/v1/predict/startup-success/                  # fundable startups list
GET  /api/v1/predict/engagement-risk/                  # at-risk lists (Section F)
GET  /api/v1/graph/ecosystem/                          # collaboration score
GET  /api/v1/analytics/nirf/export/?format=pdf         # export (Section export btn)

All endpoints accept optional `?semester=<id>` and `?year=<yyyy>` query params
for the period selector in the dashboard header.

---

*This file is the single source of truth for Phase 7 NIRF dashboard implementation.
Do not rename metrics without updating `nirf_kpi_feature_traceability.md` in the same commit.*

Project directory tree for the NIRF module:

project_root/
└── docs/
    └── nirf/
        ├── nirf_innovation_kpi_analysis.md
        ├── nirf_kpi_feature_traceability.md
        └── nirf_dashboard_design.md
