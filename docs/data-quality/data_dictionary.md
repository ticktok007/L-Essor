# Data Dictionary — Synthetic Dataset v1.0
**Project:** Campus Innovation & Engagement Intelligence Hub
**Version:** v1.0
**Phase:** 1 — Synthetic Data Foundation
**Tables:** users · startups · investors · interactions · achievements · competitions

---

## Table: `users`

| Column | Type | Required | Description | Generation Rule | Example |
|---|---|---|---|---|---|
| `user_id` | STRING | ✅ | Unique user identifier | From source ID (`STU#####`, `ALM#####`, `INV#####`, `MEN#####`) | `STU00001` |
| `email` | STRING | ✅ | Unique fictional email address | Faker `en_IN` unique email | `anita.sharma@example.com` |
| `role` | STRING | ✅ | Platform role | Derived from source table: `student`, `alumni`, `investor`, `mentor` | `student` |
| `full_name` | STRING | ✅ | Full display name | Faker `en_IN` name | `Anita Sharma` |
| `is_active` | BOOLEAN | ✅ | Account active flag | Always `true` in synthetic baseline | `true` |

---

## Table: `startups`

| Column | Type | Required | Description | Generation Rule | Example |
|---|---|---|---|---|---|
| `startup_id` | STRING | ✅ | Unique startup identifier | Sequential `STA#####` | `STA00001` |
| `name` | STRING | ✅ | Startup display name | `{Faker.last_name} + Tech/AI/Labs/etc.` | `Sharma Tech` |
| `sector` | STRING | ✅ | Primary sector | Sampled from 12-sector pool | `HealthTech` |
| `subsector` | STRING | ✅ | Domain within sector | Sampled per-sector | `Telemedicine` |
| `funding_stage` | STRING | ✅ | Current funding stage | Weighted sample: pre-seed 30%, seed 25%, grant 20%, series-a 10%, bootstrapped 15% | `seed` |
| `trl_level` | INTEGER | ✅ | Technology Readiness Level | Sampled within stage-specific range [1–9] | `4` |
| `mrl_level` | STRING | ⬜ | Market Readiness Level | Not generated in Phase 1; computed in Phase 4 | `` |
| `trl_mrl_gap` | STRING | ⬜ | TRL minus MRL | Not generated in Phase 1; computed in Phase 4 | `` |
| `founded_year` | INTEGER | ✅ | Year of founding | Stage-specific window (e.g. pre-seed: last 1–2 years) | `2024` |
| `hq_city` | STRING | ✅ | Headquarters city | Sampled from 10 Indian cities | `Chennai` |
| `team_size` | INTEGER | ✅ | Current headcount | Stage-scaled: 2–8 (early), 6–35 (later) | `6` |
| `pitch_summary` | STRING | ✅ | 2–4 sentence pitch | Multi-frame hybrid generator using sector vocabulary bank | `Rural patients travel 80km...` |
| `incubation_status` | STRING | ✅ | Incubation lifecycle stage | Defaulted to `pre-incubation` in Phase 1 | `pre-incubation` |
| `founder_count` | INTEGER | ✅ | Number of founders | 1–3 (early stage), 2–4 (later stage); must equal rows in `interactions` | `2` |

---

## Table: `investors`

| Column | Type | Required | Description | Generation Rule | Example |
|---|---|---|---|---|---|
| `profile_id` | STRING | ✅ | Unique investor profile ID | Sequential `INV#####` | `INV00001` |
| `firm_name` | STRING | ✅ | Firm or organisation name | Faker company name | `Sharma Capital Partners` |
| `mandate_text` | STRING | ✅ | Investment thesis description | Multi-frame mandate renderer (4 frame families) | `We invest in seed-stage HealthTech...` |
| `sector_focus` | STRING | ✅ | Pipe-separated sector focus list | 2 sectors sampled per investor | `HealthTech\|EdTech` |
| `stage_preference` | STRING | ✅ | Preferred engagement mode | Sampled from engagement preference pool | `warm_intro` |
| `check_size_inr` | INTEGER | ✅ | Typical cheque size in INR | Tiered: 0, 5L, 10L, 25L, 50L, 1Cr, 2.5Cr | `1000000` |
| `expertise_tags` | STRING | ✅ | Pipe-separated expertise areas | 4 tags sampled from expertise pool | `Product Strategy\|Fundraising` |

---

## Table: `interactions`

| Column | Type | Required | Description | Generation Rule | Example |
|---|---|---|---|---|---|
| `edge_id` | STRING | ✅ | Unique edge identifier | Sequential `EDG######` | `EDG000001` |
| `source_profile_id` | STRING | ✅ | Initiating node ID | Hub-weighted sampling from MEN/INV/STU/ALU pools | `MEN-0077` |
| `target_profile_id` | STRING | ✅ | Receiving node ID | Hub-weighted sampling from complementary pool | `STU-0042` |
| `edge_type` | STRING | ✅ | Relationship type | Weighted sample: mentor_mentee 40%, investor_founder 30%, club_membership 30% | `mentor_mentee` |
| `relationship_strength` | STRING | ✅ | Categorical strength | Weighted: weak 30%, medium 45%, strong 25% | `medium` |
| `interaction_count` | INTEGER | ✅ | Number of interactions | Range tied to strength: weak 1–3, medium 4–10, strong 11–30 | `6` |
| `first_interaction_context` | STRING | ✅ | How relationship started | Sampled from type-specific context pool | `Intro via incubation cell referral` |
| `last_interaction_context` | STRING | ✅ | Most recent interaction | Sampled from type-specific context pool | `Monthly check-in on startup metrics` |
| `created_at` | DATE | ✅ | First interaction date | Random date in [2019–2025] | `2023-04-11` |
| `outcome` | STRING | ✅ | Interaction outcome | Fixed `accepted` in Phase 1 (all edges are active) | `accepted` |
| `success_label` | STRING | ⬜ | ML telemetry label | Empty in Phase 1; written by platform on live "Connect" click | `` |

---

## Table: `achievements`

| Column | Type | Required | Description | Generation Rule | Example |
|---|---|---|---|---|---|
| `achievement_id` | STRING | ✅ | Unique achievement identifier | Sequential `ACH######` | `ACH000001` |
| `profile_id` | STRING | ✅ | Owning profile | Hub-weighted from STU/ALU pool | `STU-0142` |
| `category` | STRING | ✅ | Achievement type | Weighted sample across 10 types | `hackathon_win` |
| `title` | STRING | ✅ | Achievement title | Sampled from per-type title pool | `Winner — Smart India Hackathon 2024` |
| `issuing_body` | STRING | ✅ | Issuing organisation | Sampled from per-type issuer pool | `Ministry of Education GoI` |
| `year` | INTEGER | ✅ | Year of achievement | Random in [2019–2025] | `2023` |
| `impact_level` | STRING | ✅ | Geographic impact scope | Weighted: campus 50%, regional 30%, national 20% | `national` |
| `notes` | STRING | ✅ | Short context note | Sampled from note pool | `Cited in NIRF Innovation submission.` |
| `verified` | BOOLEAN | ✅ | NER-verified flag | `false` in Phase 1 — set by NER pipeline in Phase 6 | `false` |
| `nirf_countable` | BOOLEAN | ✅ | Counts toward NIRF Innovations | `false` in Phase 1 — set by admin in Phase 7 | `false` |

---

## Table: `competitions`

| Column | Type | Required | Description | Generation Rule | Example |
|---|---|---|---|---|---|
| `competition_id` | STRING | ✅ | Unique competition record ID | Sequential `CMP#####` | `CMP00001` |
| `profile_id` | STRING | ✅ | Participating profile | Hub-weighted from STU/ALU pool | `ALU-0033` |
| `name` | STRING | ✅ | Competition name | Sampled from 20-name realistic pool | `Smart India Hackathon` |
| `competition_type` | STRING | ✅ | Format category | Sampled: hackathon, innovation_challenge, startup_pitch, demo_day, etc. | `hackathon` |
| `year` | INTEGER | ✅ | Participation year | Random in [2019–2025] | `2024` |
| `participation_role` | STRING | ✅ | Role in competition | Weighted: participant 45%, finalist 25%, winner 15%, organizer 8%, mentor_judge 7% | `finalist` |
| `result` | STRING | ✅ | Outcome of participation | Sampled from role-appropriate result pool | `Top 5 finalist` |
| `team_size` | INTEGER | ✅ | Team headcount | 1–5 for participant/finalist/winner; 0 for organizer/judge roles | `3` |
| `theme` | STRING | ✅ | Competition domain theme | Sampled from 10 innovation themes | `Healthcare & MedTech` |
| `nirf_recognised` | BOOLEAN | ✅ | NIRF-eligible event flag | `false` in Phase 1 — set by admin in Phase 7 | `false` |