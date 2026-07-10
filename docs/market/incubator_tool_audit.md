# Incubator & Startup Tool Competitive Audit
**Module:** Market Research — Incubator Tools
**Project:** Campus Innovation & Engagement Intelligence Hub
**Last updated:** Day 3, Phase 0 (Jul 08, 2026)
**Author:** Sanjay (24AM0100), Chennai Institute of Technology

---

## 1. AcceleratorApp

**What it does well**
- End-to-end cohort management — application, selection, milestone tracking, and reporting
- KPI dashboards for programme managers showing cohort health at a glance
- Mentor session scheduling and hours logging
- Resource library and document sharing per cohort
- Investor relations module with deal-flow tracking across cohorts

**Where it stops short**
- Milestone tracking is manual — startups self-report progress, no predictive signal on which are likely to stall
- Mentor matching is admin-assigned, not AI-suggested — relies on coordinator knowledge, not semantic compatibility
- No graph layer — cannot identify which mentors or alumni are connectors bridging otherwise isolated startup clusters
- No student-lifecycle view — cohort starts at incubation application; pre-incubation academic history is invisible
- Analytics are programme-level, not ecosystem-level — no cross-cohort pattern recognition

**Gap my project exploits**
- XGBoost at-risk classifier adds a predictive layer AcceleratorApp entirely lacks — admin sees who is about to stall before they self-report failure
- Semantic KNN mentor matching replaces admin-assigned pairings with compatibility-scored suggestions
- Student lifecycle continuity — a student's competition wins, GPA-trajectory, and club history feed the success predictor long before they apply for incubation

---

## 2. F6S

**What it does well**
- Largest public startup profile database — global deal-flow aggregation
- Programme listing and application management for accelerators and grant schemes
- Startup–investor introduction requests at scale
- Integration with government and EU-funded innovation schemes
- Perks/discounts marketplace for startups (AWS, Stripe, Notion credits)

**Where it stops short**
- Purely public and transactional — no private campus intelligence, no institution-specific analytics
- No semantic matching — introductions are keyword-filtered and manually reviewed
- No graph SNA — network is a flat marketplace, not a mapped relationship graph
- No predictive analytics — no model for startup success probability or investor conversion likelihood
- Completely decoupled from the student lifecycle — F6S has no concept of a student's academic and competition history

**Gap my project exploits**
- Private, institution-specific intelligence layer is the core differentiator — F6S is a public marketplace, the project is a closed campus-intelligence system with verified data
- Semantic pitch-to-mandate matching (cosine similarity via MiniLM) replaces keyword filtering — surfaces investor–startup compatibility that keyword search misses
- Student-lifecycle continuity ties a founder's incubation performance back to their academic journey — no global platform can do this with verified institutional data

---

## 3. StartupOS

**What it does well**
- Structured venture-building methodology with stage-gate checkpoints (Idea → Validate → Build → Scale)
- Mentor and advisor network management with session notes and deliverable tracking
- Investor-ready data room generation per startup
- OKR and milestone tracking tied to stage gates
- Reporting templates aligned to investor due-diligence requirements

**Where it stops short**
- Stage-gate methodology is rigid — not well suited to university innovation ecosystems where startups move non-linearly
- No NLP or AI layer — compatibility matching between startup and mentor/investor is entirely manual
- No graph intelligence — ecosystem relationships are tracked per-startup in isolation, not as a network
- Engagement metrics are activity-based (sessions logged, OKRs completed), not outcome-predictive
- No student or alumni dimension — purely a startup operating tool, not a campus ecosystem platform

**Gap my project exploits**
- TRL–MRL Gap feature and XGBoost success model add an AI-scored readiness signal StartupOS cannot produce — evaluators see not just "what stage" but "how likely to succeed"
- Graph SNA connects startups to each other and to the broader alumni/investor network — StartupOS treats each startup as an isolated record
- Alumni and student layers extend the platform horizontally across the entire campus innovation lifecycle, not just post-incubation startups

---

## 4. Gust

**What it does well**
- Long-established angel investment platform with standardised funding application forms
- Due-diligence workflow management for angel groups and syndicates
- Startup profile credentialing (team, traction, financials) in a structured format
- Cap table and round management tools
- Large investor network with warm-introduction facilitation

**Where it stops short**
- Investor–startup matching is entirely manual — investors browse and filter; no AI ranking or compatibility scoring
- No campus or institutional layer — Gust operates at the deal level, not the ecosystem level
- No graph layer — relationship mapping between founders, angels, and advisors is not surfaced
- No predictive model — no startup success probability, no investor conversion likelihood
- No student or mentor dimension — purely a funding transaction platform

**Gap my project exploits**
- Cosine-similarity pitch-to-mandate matching ranks investor–startup compatibility automatically — replaces Gust's browse-and-filter with a scored, personalised shortlist
- Campus context enriches the startup profile beyond what Gust shows — a founder's competition wins, mentorship hours, and TRL trajectory are signals Gust cannot access
- Predictive success model gives the incubation cell a fundability score per startup before they even approach an investor — proactive pipeline curation that Gust has no equivalent for
