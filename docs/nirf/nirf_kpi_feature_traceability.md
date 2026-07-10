# NIRF KPI → Platform Feature Traceability Sheet
**Module:** NIRF Innovation Ranking — Feature Traceability
**Project:** Campus Innovation & Engagement Intelligence Hub
**Last updated:** Day 2, Phase 0 (Jul 07, 2026)
**Author:** Sanjay (24AM0100), Chennai Institute of Technology

> **Usage note:** This sheet is the authoritative mapping between NIRF metrics and
> platform features. It is reused directly in Phase 7 to wire the Leadership /
> NIRF Innovation Dashboard. Every `Dashboard Metric` name here must appear verbatim
> as a dashboard card, chart title, or API field name in Phase 7.

---

## Primary Traceability Table

| NIRF KPI | Weightage | Platform Feature / Module | Dashboard Metric (exact name) | Data Source / Table | Notes for Evaluators |
|---|---|---|---|---|---|
| Financial Support for Innovation | 25% | Startup Progress Tracker | `total_funds_mobilised_inr` | `startups.funding_events` (sum of `amount`) | Covers seed grants, angel rounds, and institutional grants — all stored as timestamped `FundingEvent` records |
| Financial Support for Innovation | 25% | Investor Matchmaking Engine (cosine similarity) | `investor_matches_converted` | `interactions` WHERE `type='funding_match'` AND `outcome='closed'` | A converted match = a real funding event → directly increases NIRF Financial Support count |
| Financial Support for Innovation | 25% | Leadership Analytics Dashboard | `active_funded_projects_count` | `startups` WHERE `funding_stage != 'pre-seed'` AND `status='active'` | Point-in-time count of startups with at least one closed funding event |
| Financial Support for Innovation | 25% | XGBoost Success Predictor | `high_probability_fundable_startups` | Model output stored in `startups.success_probability` | Enables admin to prioritise seed-fund allocation — shows evaluators proactive capital deployment |
| Research & Innovation Output | 30% | Achievement Tracker + DistilBERT NER | `patent_filings_count` | `achievements` WHERE `category='patent'` | NER auto-extracts patent number, filing date, inventors from uploaded PDF certificates |
| Research & Innovation Output | 30% | Achievement Tracker + DistilBERT NER | `publications_count` | `achievements` WHERE `category='publication'` | Scopus/SCI indexed papers extracted from uploaded PDFs; manually verified flag available |
| Research & Innovation Output | 30% | Portfolio Generator (TF-IDF + LDA topic tagger) | `tech_transfer_events_count` | `achievements` WHERE `category='tech_transfer'` | LDA auto-tags licensing/transfer events; links to associated startup record |
| Research & Innovation Output | 30% | Graph Intelligence (NetworkX) | `cross_dept_collaboration_score` | Computed from `interactions` edge set; stored in `profiles.betweenness_centrality` | Betweenness centrality of research-collaboration subgraph — proxy for interdisciplinary innovation output |
| Research & Innovation Output | 30% | Portfolio Generator (PDF export) | `portfolios_with_research_output_pct` | `portfolios` WHERE JSON contains `category IN ('patent','publication')` | % of student portfolios containing at least one verified research output |
| Innovation Achievements | 15% | Competition & Achievement Tracker | `competition_wins_count` | `achievements` WHERE `category='competition'` AND `rank <= 3` | Top-3 finishes at NIRF-recognised events (SIH, TOYCATHON, NASA Apps, etc.) |
| Innovation Achievements | 15% | Competition & Achievement Tracker | `competition_participation_count` | `achievements` WHERE `category='competition'` | Total entries across all competitions — breadth metric NIRF rewards |
| Innovation Achievements | 15% | Student Portal — Achievement Timeline | `competition_participation_rate_pct` | `achievements` JOIN `users` GROUP BY `semester` | Semester-over-semester participation rate; target: +35% vs. baseline (PS success criterion #3) |
| Innovation Achievements | 15% | Leadership Analytics Dashboard | `cross_dept_participation_breadth` | `achievements` JOIN `profiles.department` — COUNT DISTINCT departments | Measures institution-wide spread, not siloed to one dept |
| Innovation Achievements | 15% | Graph Intelligence (NetworkX) | `at_risk_departments_list` | Departments with centrality or participation score below threshold | Enables proactive outreach to under-participating departments before NIRF cycle |
| Pre-Incubation & Incubation | 10% | Startup Progress Tracker | `active_incubatees_count` | `startups` WHERE `incubation_status='active'` | Live occupancy count; replaces manual register |
| Pre-Incubation & Incubation | 10% | Mentor Matchmaking (KNN) + `mentorship_hours` field | `total_mentorship_hours_logged` | `interactions` WHERE `type='mentorship'` — SUM(`duration_hours`) | Directly maps to NIRF "mentoring support provided" sub-metric |
| Pre-Incubation & Incubation | 10% | Startup Progress Tracker | `startup_graduation_rate_pct` | `startups` WHERE `incubation_status='graduated'` / total admitted | Graduated = exited incubation and independently operating — highest-scored NIRF sub-outcome |
| Pre-Incubation & Incubation | 10% | Engagement-Risk Model (XGBoost classifier) | `at_risk_incubatees_count` | Model output stored in `startups.at_risk_flag` | Early-warning list for incubation cell admin; proactive support → improved survival rate |
| Pre-Incubation & Incubation | 10% | Incubation Cell Portal (admin view) | `industry_mou_count` | `investors` JOIN `interactions` WHERE `type='mou'` | Count of formalised industry/investor relationships — NIRF requires documented MoUs |

---

## Metric → API Endpoint Quick-Reference

> Endpoint names here become the actual DRF routes in Phase 7. Keep these names exact.

| Dashboard Metric | DRF Endpoint (Phase 7) |
|---|---|
| `total_funds_mobilised_inr` | `GET /api/v1/analytics/nirf/financial-support/` |
| `investor_matches_converted` | `GET /api/v1/analytics/nirf/financial-support/` |
| `active_funded_projects_count` | `GET /api/v1/analytics/nirf/financial-support/` |
| `high_probability_fundable_startups` | `GET /api/v1/predict/startup-success/` |
| `patent_filings_count` | `GET /api/v1/analytics/nirf/research-output/` |
| `publications_count` | `GET /api/v1/analytics/nirf/research-output/` |
| `tech_transfer_events_count` | `GET /api/v1/analytics/nirf/research-output/` |
| `cross_dept_collaboration_score` | `GET /api/v1/graph/ecosystem/` |
| `portfolios_with_research_output_pct` | `GET /api/v1/analytics/nirf/research-output/` |
| `competition_wins_count` | `GET /api/v1/analytics/nirf/innovation-achievements/` |
| `competition_participation_count` | `GET /api/v1/analytics/nirf/innovation-achievements/` |
| `competition_participation_rate_pct` | `GET /api/v1/analytics/nirf/innovation-achievements/` |
| `cross_dept_participation_breadth` | `GET /api/v1/analytics/nirf/innovation-achievements/` |
| `at_risk_departments_list` | `GET /api/v1/predict/engagement-risk/` |
| `active_incubatees_count` | `GET /api/v1/analytics/nirf/incubation/` |
| `total_mentorship_hours_logged` | `GET /api/v1/analytics/nirf/incubation/` |
| `startup_graduation_rate_pct` | `GET /api/v1/analytics/nirf/incubation/` |
| `at_risk_incubatees_count` | `GET /api/v1/predict/engagement-risk/` |
| `industry_mou_count` | `GET /api/v1/analytics/nirf/incubation/` |

---

## Coverage Summary

| NIRF KPI | Weightage | Metrics Mapped | Modules Involved |
|---|---|---|---|
| Financial Support | 25% | 4 | Startup Tracker, Investor Matching, XGBoost Predictor, Leadership Dashboard |
| Research & Innovation Output | 30% | 5 | Achievement Tracker, DistilBERT NER, Portfolio Generator, Graph Intelligence |
| Innovation Achievements | 15% | 5 | Competition Tracker, Student Portal, Leadership Dashboard, Graph Intelligence |
| Pre-Incubation & Incubation | 10% | 5 | Startup Tracker, Mentor Matching, Engagement-Risk Model, Incubation Cell Portal |
| **Total** | **80%** | **19** | **All 6 core modules** |

*The remaining 20% (Teaching, Learning & Resources) is outside this platform's scope.*

---

*Next: see `nirf_dashboard_design.md` for the Leadership Dashboard design spec that consumes these metrics.*
