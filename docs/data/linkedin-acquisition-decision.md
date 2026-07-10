# LinkedIn Acquisition Decision
**Project:** Campus Innovation & Engagement Intelligence Hub
**Decided:** Day 6, Phase 1 (Jul 13, 2026)
**Author:** Sanjay (24AM0100), Chennai Institute of Technology
**Status:** CLOSED — live LinkedIn dependency rejected

---

## Decision

LinkedIn scraping and direct LinkedIn API dependence are **rejected** as data
acquisition paths for this project. Neither approach is used at any stage —
build, demo, or production.

---

## Why Not Viable

### Terms of Service / Compliance Risk
- LinkedIn's User Agreement §8.2 explicitly prohibits scraping, crawling, and
  automated data extraction without prior written consent.
- The *hiQ Labs v. LinkedIn* (9th Circuit, 2022) ruling does not grant blanket
  scraping rights — it narrowly addressed public data access under the CFAA
  and does not override LinkedIn's ToS for commercial or institutional use.
- An Indian university platform built on scraped LinkedIn data exposes the
  institution to GDPR (for alumni in EU), IT Act 2000, and potential LinkedIn
  legal action — a compliance risk no hackathon project or production system
  should accept.
- LinkedIn's Official API (LinkedIn Partner Program) requires a formal
  partnership application, legal review, and approval that takes months and is
  routinely denied to university projects.

### 24-Hour Cache Limit Problem
- LinkedIn's API terms require that any fetched data be discarded or
  re-fetched every 24 hours — it cannot be stored in a persistent database.
- This platform's core value depends on a **persistent, queryable profile
  store** (20,000+ alumni profiles with career history, skills, and
  interaction history). A 24-hour data expiry makes that impossible.
- Rebuilding 20,000 profiles every 24 hours would exhaust any API rate limit
  in hours and violates cache terms simultaneously.

### Anti-Bot / Scraping Fragility
- LinkedIn deploys bot detection (device fingerprinting, CAPTCHA, rate limiting,
  IP blocking, session invalidation) that breaks scrapers within days of
  deployment — often within hours on headless browser approaches.
- Any feature built on scraping becomes a production incident on an
  unpredictable schedule, not a stable system dependency.
- Bypassing bot detection via proxy rotation or browser emulation escalates the
  ToS violation from civil to potential criminal liability under the CFAA
  (US) and comparable Indian IT Act provisions.

### Why This Makes It Unsuitable as a Core System Dependency
- A core system dependency must be **reliable, legal, persistent, and
  reproducible**. Live LinkedIn data fails all four:
  - Not reliable (bot detection, rate limits)
  - Not legal (ToS violation)
  - Not persistent (24-hour cache limit)
  - Not reproducible (scraper breakage is non-deterministic)
- Building the matchmaking engine, portfolio generator, or NIRF dashboard on
  top of a dependency that can legally cease to function overnight is an
  architectural flaw, not a feature.

---

## Project Impact

- The alumni career-tracking module **does not** depend on LinkedIn at any
  stage.
- Alumni profile data is **self-reported** via the Alumni Portal (verified by
  the institution) and **NER-extracted** from uploaded certificates.
- The investor and mentor profile data is **self-entered** at registration and
  **enriched by the platform's own NER pipeline**, not external scraping.
- The matchmaking engine operates entirely on **platform-resident data** — no
  live external API call is made at match time.

---

## Approved Path Forward

| Need | Approved Approach |
|---|---|
| Alumni career history | Self-update via Alumni Portal; institution bulk-import from their existing alumni spreadsheet at onboarding |
| Skills and expertise | DistilBERT NER extraction from uploaded certificates and CVs |
| Investor/mentor profile | Self-entered mandate + domain tags at registration |
| External enrichment (future) | Compliant third-party data providers (see `hybrid-data-strategy.md`) under a formal DPA — not LinkedIn scraping |
| Build/demo phase | Faker-based synthetic data (`generate_ecosystem_data.py`) — no external dependency at all |
