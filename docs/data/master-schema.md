# Master Schema
**Project:** Campus Innovation & Engagement Intelligence Hub
**Defined:** Day 6, Phase 1 (Jul 13, 2026)
**Author:** Sanjay (24AM0100), Chennai Institute of Technology
**Note:** Audit columns (`created_at`, `updated_at`) implied on all tables.
**Extends:** `docs/architecture/erd-skeleton.md` (ERD skeleton is the
authoritative entity diagram; this file is the implementation-ready schema).

---

## Table: `users`

**Purpose:** Authentication and role identity. Owned by Django's auth layer.

- `id` UUID PK
- `email` VARCHAR(254) UNIQUE NOT NULL
- `password_hash` VARCHAR(128) NOT NULL — Django PBKDF2
- `role` VARCHAR(24) NOT NULL — `student` | `alumni` | `investor` | `mentor` | `incubation_admin` | `leadership`
- `is_active` BOOLEAN DEFAULT TRUE
- `last_login` TIMESTAMPTZ

**FK:** none — root table
**Relationship:** 1 `users` row → 1 `profiles` row (enforced by unique FK on `profiles.user_id`)

---

## Table: `profiles`

**Purpose:** All non-auth identity data, computed ML signals, and graph scores.
Central join target for every other table.

- `id` UUID PK
- `user_id` UUID NOT NULL UNIQUE FK → `users.id` ON DELETE CASCADE
- `full_name` VARCHAR(120) NOT NULL
- `department` VARCHAR(80)
- `cohort_year` SMALLINT
- `bio` TEXT
- `skills_list` JSONB DEFAULT '[]' — `["Python","ML"]`
- `skills_embedding` VECTOR(384) — MiniLM encoding, nightly refresh
- `betweenness_centrality` FLOAT DEFAULT 0.0 — NetworkX, nightly
- `pagerank_score` FLOAT DEFAULT 0.0 — NetworkX, nightly
- `community_id` INTEGER — Louvain cluster, nightly
- `achievement_impact_score` FLOAT DEFAULT 0.0 — AIS composite
- `grit_index` FLOAT DEFAULT 0.0 — competitions entered / won
- `at_risk_flag` BOOLEAN DEFAULT FALSE — engagement-risk model
- `profile_completion_pct` FLOAT DEFAULT 0.0 — derived on save
- `data_source` VARCHAR(32) DEFAULT 'self_reported' — provenance tag

**FK:** `user_id` → `users.id`
**Relationship:** Parent of `startups`, `investors`, `mentors`, `achievements`; both actor and target in `interactions`

---

## Table: `startups`

**Purpose:** Startup entity record including pitch text, embedding, incubation
state, ML scores, and funding journey.

- `id` UUID PK
- `founder_id` UUID NOT NULL FK → `profiles.id`
- `name` VARCHAR(120) NOT NULL
- `sector` VARCHAR(80)
- `pitch_summary` TEXT — source text for embedding (max 512 tokens)
- `pitch_embedding` VECTOR(384) — MiniLM encoding of `pitch_summary`
- `funding_stage` VARCHAR(24) — `pre-seed` | `seed` | `series-a` | `grant` | `bootstrapped`
- `trl_level` SMALLINT CHECK (1–9)
- `mrl_level` SMALLINT CHECK (1–9)
- `trl_mrl_gap` FLOAT — computed: `trl_level - mrl_level`
- `incubation_status` VARCHAR(24) — `pre-incubation` | `active` | `graduated` | `exited`
- `success_probability` FLOAT — XGBoost output, nightly refresh
- `at_risk_flag` BOOLEAN DEFAULT FALSE — engagement-risk model
- `mentorship_hours` FLOAT DEFAULT 0.0 — aggregated from `interactions`
- `competitions_entered` INTEGER DEFAULT 0 — aggregated from `achievements`
- `competitions_won` INTEGER DEFAULT 0 — aggregated from `achievements`

**FK:** `founder_id` → `profiles.id`
**Relationship:** 1 `startups` → Many `achievements`; 1 `startups` → Many `interactions` (via `interactions.startup_id`)

---

## Table: `investors`

**Purpose:** Investor/VC profile including mandate text, embedding, and
matching preferences.

- `id` UUID PK
- `profile_id` UUID NOT NULL UNIQUE FK → `profiles.id` ON DELETE CASCADE
- `firm_name` VARCHAR(120)
- `mandate_text` TEXT — source text for embedding
- `mandate_embedding` VECTOR(384) — MiniLM encoding of `mandate_text`
- `sector_focus` JSONB DEFAULT '[]' — `["HealthTech","FinTech"]`
- `stage_preference` JSONB DEFAULT '[]' — `["seed","series-a"]`
- `check_size_min_inr` BIGINT
- `check_size_max_inr` BIGINT
- `total_matches_converted` INTEGER DEFAULT 0 — telemetry counter

**Note:** `mentors` table follows the same pattern as `investors` with
`expertise_text`, `expertise_embedding`, `domain_tags JSONB`,
`available_for_mentoring BOOLEAN`, `total_sessions_logged INTEGER`.
Both reference `profiles.id` 1:1.

**FK:** `profile_id` → `profiles.id`
**Relationship:** Investor interactions recorded in `interactions` WHERE `type = 'funding_match'`

---

## Table: `interactions`

**Purpose:** Every relationship event between two profiles — the single edge
table consumed by NetworkX to build the ecosystem graph.

- `id` UUID PK
- `actor_id` UUID NOT NULL FK → `profiles.id` — who initiated
- `target_id` UUID NOT NULL FK → `profiles.id` — who received
- `type` VARCHAR(32) NOT NULL — `mentorship` | `funding_match` | `club_membership` | `competition_team` | `mou`
- `outcome` VARCHAR(24) DEFAULT 'pending' — `pending` | `accepted` | `declined` | `closed`
- `startup_id` UUID FK → `startups.id` NULLABLE — set when `type = 'funding_match'`
- `duration_hours` FLOAT NULLABLE — set when `type = 'mentorship'`
- `success_label` BOOLEAN NULLABLE — telemetry: TRUE on "Connect" click; feeds XGBoost retraining
- `session_date` DATE NULLABLE
- `notes` TEXT NULLABLE
- `computed_at` TIMESTAMPTZ — timestamp of last graph score recalculation that included this edge

**FK:** `actor_id` → `profiles.id`; `target_id` → `profiles.id`; `startup_id` → `startups.id`
**Graph edge rule:** Rows WHERE `outcome = 'accepted'` become directed edges `actor_id → target_id` in the NetworkX graph. All other rows are excluded from graph construction.
**Relationship:** Many-to-many self-join on `profiles`; optional join to `startups`

---

## Table: `achievements`

**Purpose:** Every verified or unverified achievement record for a profile —
competition results, patents, publications, tech transfers, leadership roles.

- `id` UUID PK
- `profile_id` UUID NOT NULL FK → `profiles.id`
- `startup_id` UUID FK → `startups.id` NULLABLE — set if startup-level achievement
- `competition_id` UUID FK → `competitions.id` NULLABLE — set if competition result
- `category` VARCHAR(32) NOT NULL — `competition` | `patent` | `publication` | `tech_transfer` | `leadership` | `project`
- `title` VARCHAR(240) NOT NULL — NER-extracted or manually entered
- `rank_or_prize` VARCHAR(120) NULLABLE — `"1st Place"`, `"Best Innovation"`
- `date` DATE
- `verified` BOOLEAN DEFAULT FALSE — TRUE when NER confidence ≥ 0.80
- `certificate_path` VARCHAR(512) NULLABLE — storage path to uploaded PDF
- `ner_confidence` FLOAT NULLABLE — NER pipeline confidence score
- `topic_tags` JSONB DEFAULT '[]' — LDA tags: `["Leadership","ML"]`
- `nirf_countable` BOOLEAN DEFAULT FALSE — eligible for NIRF Innovation Achievements count

**FK:** `profile_id` → `profiles.id`; optional `startup_id` → `startups.id`; optional `competition_id` → `competitions.id`
**Relationship:** Many `achievements` → 1 `profiles`; Many `achievements` → 1 `competitions`

---

## Table: `competitions`

**Purpose:** Master list of competitions and events — used for achievement
registration, event management, and NIRF participation tracking.

- `id` UUID PK
- `name` VARCHAR(200) NOT NULL
- `organiser` VARCHAR(120)
- `event_date` DATE
- `registration_deadline` DATE
- `nirf_recognised` BOOLEAN DEFAULT FALSE — TRUE = counts toward NIRF Innovation Achievements
- `eligible_roles` JSONB DEFAULT '["student"]' — `["student","alumni"]`
- `created_by` UUID FK → `profiles.id` — incubation admin who created record
- `participation_count` INTEGER DEFAULT 0 — updated on achievement registration

**FK:** `created_by` → `profiles.id`
**Relationship:** 1 `competitions` → Many `achievements` (results logged post-event)
