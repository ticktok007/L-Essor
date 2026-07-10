# Figma Wireframe Brief — Role-Based Portal Shells
**Project:** Campus Innovation & Engagement Intelligence Hub
**Fidelity:** Low — structural layout only, no colour, no icons, no final copy
**Delivered:** Day 5, Phase 0 (Jul 10, 2026)
**Author:** Sanjay (24AM0100), Chennai Institute of Technology

---

## General Rules (apply to all 5 shells)

- Desktop-first, 1280px canvas width
- Left sidebar navigation (64px collapsed icon rail + 220px expanded label rail)
- Top bar: institution logo left, role badge + user avatar right
- Content area: remainder of viewport, single scrollable column
- No colour fills — use stroke boxes and greyscale fills only
- Annotate every widget with its data source in a callout box beside it

---

## 1. Student Portal

**Purpose:** Central hub for a student to track their own achievements, find
mentors/teammates, enter competitions, and generate their portfolio.

### Sidebar Items

Home
My Achievements
Find a Mentor
Find Teammates
Competitions
My Portfolio

### Primary Widgets / Sections
| Section | Content |
|---|---|
| Profile Completion Bar | % complete with inline "Add missing fields" CTA |
| Achievement Timeline | Chronological cards: competition, patent, publication, project |
| Mentor Match Shortlist | Top-3 recommended mentors, compatibility score badge, "Request" button |
| Open Competitions | List of upcoming events with deadline, eligibility, "Register" CTA |
| Portfolio Preview | One-line summary of auto-generated portfolio + "Download PDF" CTA |
| Skill Gap Nudge | Banner: "You are missing X skill that 80% of funded founders have" |

### Key CTAs
- Upload Certificate → triggers NER pipeline
- Request Mentor Connection
- Register for Competition
- Download Portfolio PDF

### Wireframe Notes
- Achievement Timeline: use card stack pattern, vertically scrollable
- Mentor Shortlist: 3-column card row, each card has avatar placeholder + score pill
- Portfolio Preview: single box with dashed border, "Generated" state vs "Not yet generated" empty state both needed
- No charts on this portal — data density should stay low

---

## 2. Alumni Portal

**Purpose:** Allow alumni to maintain a live profile, offer mentorship, view
campus activity, and stay loosely connected with minimal effort.

### Sidebar Items

Home
My Profile
Mentorship
Campus Feed
My Connections

### Primary Widgets / Sections
| Section | Content |
|---|---|
| Profile Status Card | Completion % + "Update Employment" CTA |
| Active Mentees | List of current mentee connections with last-session date |
| Mentorship Offer Toggle | On/Off switch: "Open to mentoring" with domain tags selector |
| Campus Highlights Feed | Recent competition wins, new startups, upcoming events |
| Connection History | Timeline of all interactions with students/founders |
| Alumni Network Map | Placeholder box labelled "Ecosystem Graph — my connections" |

### Key CTAs
- Update Profile / Employment
- Toggle Mentorship Availability
- Accept / Decline Mentee Request
- View Connection

### Wireframe Notes
- Keep home screen to 2 columns max — alumni engage briefly, not deeply
- Mentorship toggle must be prominent (top of sidebar or top of home card)
- Campus Feed: chronological list, not infinite scroll — paginate at 10 items
- Alumni Network Map: placeholder only at this fidelity; implemented in Phase 7

---

## 3. Investor / Mentor Portal

**Purpose:** Surface a compatibility-ranked shortlist of founders or mentees
matched to the user's stated mandate or expertise, and manage connection actions.

### Sidebar Items

Home
My Mandate / Expertise
Match Shortlist
Active Connections
Deal Pipeline (Investor only)
Session Log (Mentor only)

### Primary Widgets / Sections
| Section | Content |
|---|---|
| Mandate / Expertise Card | Free-text field + sector tag chips + "Save & Re-match" CTA |
| Match Shortlist | Ranked list of top-5 startups (Investor) or mentees (Mentor), each with compatibility score, TRL badge, stage pill |
| Match Detail Drawer | Slide-in panel: full pitch summary, founder profile, achievement count, "Connect" / "Pass" actions |
| Active Connections | Table: name, role, last interaction date, session hours (Mentor) or funding stage (Investor) |
| Deal Pipeline | Kanban: Matched → Connected → Due Diligence → Closed (Investor role only) |
| Session Log | Table: mentee, date, duration, notes field (Mentor role only) |

### Key CTAs
- Save Mandate / Expertise → triggers re-embedding + re-ranking
- Connect (accept match)
- Pass (dismiss match — feeds negative signal to model)
- Log Session (Mentor)
- Move Stage (Investor Deal Pipeline)

### Wireframe Notes
- Match Shortlist: most critical widget — give it 60% of the content area
- Compatibility score: pill badge with % value, not a bar chart
- Match Detail Drawer: full-width overlay panel, not a separate page
- Investor/Mentor variants share the same shell; role flag hides/shows Deal Pipeline vs Session Log

---

## 4. Incubation Cell Portal

**Purpose:** Give incubation cell admins a live roster of startups, at-risk
alerts, and event management tools in one view.

### Sidebar Items

Dashboard
Startup Roster
At-Risk Alerts
Mentor Assignments
Events & Competitions
Reports

### Primary Widgets / Sections
| Section | Content |
|---|---|
| Stat Strip | 4 cards: Active Incubatees · At-Risk Count · Mentorship Hours This Month · Avg Success Probability |
| Startup Roster Table | Columns: Name, Founder, Stage, TRL, Success Probability %, Days in Incubation, Mentor Assigned, Actions |
| At-Risk Alert List | Red-flagged rows: startup name, risk score, last activity date, "Assign Mentor" CTA |
| Mentor Assignment Panel | Drag-assign interface: unassigned mentees list + available mentors list |
| Events Table | Upcoming competitions: name, date, eligible cohorts, "Send Invite" CTA |
| Stage Funnel Chart | Placeholder box: Pre-Incubation → Prototype → Active → Graduated |

### Key CTAs
- Assign Mentor
- Send Intervention Alert
- Create Event
- Export Cohort Report

### Wireframe Notes
- Startup Roster: most-used screen — make it the default landing view, not Dashboard
- At-Risk list: always visible as a sidebar badge count + dedicated screen
- Success Probability column: colour-coded pill (green ≥ 70%, amber 40–69%, red < 40%)
- Stage Funnel: placeholder box at this fidelity — implemented as `IncubationFunnelChart` in Phase 7

---

## 5. Leadership Portal

**Purpose:** Give institutional leadership a live NIRF Innovation KPI view,
ecosystem health summary, and audit-ready export — always current, no manual
assembly.

### Sidebar Items

NIRF Dashboard
Ecosystem Overview
Alumni Engagement
Innovation Output
Export Reports

### Primary Widgets / Sections
| Section | Content |
|---|---|
| NIRF Score Summary Strip | 4 score cards: Financial Support · Research Output · Innovation Achievements · Incubation (weightage % shown) |
| Period Selector | Semester / Year dropdown — filters all widgets below |
| KPI Metric Cards | 19 metrics from traceability sheet, grouped by NIRF category, each with current value + trend arrow |
| Participation Rate Chart | Placeholder box: line chart — semester × axis, competition participation rate |
| Alumni Engagement Gauge | Placeholder box: engagement rate % vs 40% target |
| Ecosystem Graph Thumbnail | Placeholder box labelled "Ecosystem Network — click to expand" |
| At-Risk Panel | Two lists: At-Risk Incubatees · At-Risk Departments |
| Export Button | "Export NIRF Report PDF" — top-right of every screen |

### Key CTAs
- Export NIRF Report PDF
- Drill into any KPI metric card → filtered detail view
- Change Period (semester/year selector)

### Wireframe Notes
- This portal is read-only for leadership — no create/edit actions
- NIRF Score Strip must be above the fold on all screen sizes
- Every metric card must show: metric name (exact name from traceability sheet), current value, target value, trend arrow
- Ecosystem Graph Thumbnail: placeholder only at this fidelity; wired in Phase 7
- Export button is persistent — pin to top-right regardless of active screen
