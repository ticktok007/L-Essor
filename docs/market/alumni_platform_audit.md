# Alumni Platform Competitive Audit
**Module:** Market Research — Alumni Platforms
**Project:** Campus Innovation & Engagement Intelligence Hub
**Last updated:** Day 3, Phase 0 (Jul 08, 2026)
**Author:** Sanjay (24AM0100), Chennai Institute of Technology

---

## 1. Almabase

**What it does well**
- Clean alumni directory with verified profile management and deduplication
- Donation and fundraising campaigns with payment gateway integration
- Event management (reunions, webinars) with RSVP and attendance tracking
- Email/newsletter campaigns with open-rate analytics
- CRM-style relationship tagging for development office outreach

**Where it stops short**
- No semantic matching — connections are manual directory searches, not AI-suggested
- No graph layer — cannot identify super-connectors, community clusters, or influence paths
- No predictive signals — cannot flag which alumni are drifting toward disengagement before they go silent
- Alumni engagement metric is binary (active/inactive), not a scored, multi-dimensional index
- No student-facing layer — alumni and students live in separate systems with no intelligent bridge

**Gap my project exploits**
- Replace the static directory with semantic embeddings: an alumni who worked in HealthTech is auto-surfaced to a student building a MedTech startup, no manual search needed
- Graph SNA layer reveals which alumni are high-betweenness connectors worth prioritising for outreach — Almabase has no concept of ecosystem influence
- Predictive engagement model flags declining alumni before they fully disengage, enabling proactive re-engagement campaigns

---

## 2. Graduway

**What it does well**
- Mentorship programme management with structured request/accept workflows
- Career services integration — job postings visible to current students
- Mobile-first alumni community feed (LinkedIn-lite within the institution)
- SSO and LMS integrations for smooth onboarding
- Basic analytics on mentorship hours and job placement rates

**Where it stops short**
- Mentor–mentee matching is keyword-tag based (self-selected tags), not semantic — mismatches are common when alumni do not tag themselves accurately
- No investor or startup layer — purely alumni-student, no innovation-ecosystem dimension
- No graph intelligence — the "community" is a flat feed, not a mapped network
- Analytics are descriptive (what happened) not predictive (what is about to happen)
- No portfolio generation — student achievements must be entered manually, no NER extraction from certificates

**Gap my project exploits**
- MiniLM-L12-v2 embeddings on mentor expertise vs. student goals replace fragile keyword tags with genuine semantic compatibility scores
- Investor and startup profiles bring the full innovation ecosystem into one platform — not just alumni-student mentorship but investor–founder matchmaking too
- Predictive engagement model adds the "about to disengage" signal Graduway's descriptive analytics cannot produce

---

## 3. PeopleGrove

**What it does well**
- "Success network" framing — explicitly built for career guidance and professional connections
- Smart matching algorithm (rule-based filters on industry, role, location)
- Peer-to-peer connection requests alongside alumni-student mentorship
- Appointment scheduling and video session integration
- Outcome tracking — users can log career milestones post-connection

**Where it stops short**
- Matching is rule-based filtering, not vector-similarity — cannot capture latent semantic overlap between a founder's pitch and a mentor's unstated domain expertise
- No startup or incubation layer — purely career networking, no innovation pipeline visibility
- No graph SNA — cannot identify network bridges, isolated clusters, or community structure
- No institutional NIRF/accreditation metrics output — analytics are user-facing, not leadership-facing
- Outcome tracking is self-reported, not NER-extracted from verified documents

**Gap my project exploits**
- Vector-similarity matching surfaces non-obvious mentor–founder pairings that rule-based filters would miss (e.g. a supply-chain alumni matching a logistics-tech startup even if neither used those exact keywords)
- Leadership/NIRF dashboard is entirely absent from PeopleGrove — direct addressable gap for Indian institutional accreditation context
- NER-extracted, certificate-verified achievements replace self-reported outcomes, raising data credibility for NIRF submission

---

## 4. Hivebrite

**What it does well**
- Highly customisable branded community portal — institutions can white-label fully
- Sub-group management (chapters, cohorts, clubs, regional networks)
- Integrated event, job board, and membership management in one product
- Rich media directory with profile photos, career timelines, and interests
- API access for third-party integrations

**Where it stops short**
- No AI matchmaking of any kind — connections are entirely user-initiated via search
- No graph intelligence layer — sub-groups are manually created silos, not auto-discovered communities
- No predictive analytics — engagement data is historical reporting only
- No startup/investor dimension — purely community and events, no innovation-pipeline tracking
- Customisability is a UI concern, not an intelligence concern — rich profiles do not produce insights

**Gap my project exploits**
- Auto-discovered community clusters via Louvain community detection replace manually managed sub-groups — communities emerge from actual interaction patterns, not admin decisions
- Predictive at-risk model adds foresight Hivebrite's historical reporting cannot provide
- Investor–founder–mentor matchmaking layer is entirely absent — Hivebrite has no concept of startup deal flow within an alumni community
