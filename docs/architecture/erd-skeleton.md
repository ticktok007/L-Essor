# ERD Skeleton
**Project:** Campus Innovation & Engagement Intelligence Hub
**Delivered:** Day 5, Phase 0 (Jul 10, 2026)
**Author:** Sanjay (24AM0100), Chennai Institute of Technology
**Note:** Core fields only. Audit columns (created_at, updated_at) implied on all tables.

---

## Entities

### User
| Field | Type | Notes |
|---|---|---|
| `id` | UUID (PK) | |
| `email` | VARCHAR UNIQUE | login identifier |
| `password_hash` | VARCHAR | managed by Django auth |
| `role` | ENUM | `student`, `alumni`, `investor`, `mentor`, `incubation_admin`, `leadership` |
| `is_active` | BOOLEAN | soft-disable without delete |

---

### Profile
| Field | Type | Notes |
|---|---|---|
| `id` | UUID (PK) | |
| `user_id` | UUID (FK → User) | 1:1 |
| `full_name` | VARCHAR | |
| `department` | VARCHAR | |
| `cohort_year` | INT | enrollment or graduation year |
| `bio` | TEXT | |
| `skills_list` | JSONB | `["Python", "ML", "React"]` |
| `skills_embedding` | VECTOR(384) | MiniLM encoding of skills + bio |
| `betweenness_centrality` | FLOAT | computed nightly by NetworkX |
| `pagerank_score` | FLOAT | computed nightly by NetworkX |
| `community_id` | INT | Louvain cluster label |
| `achievement_impact_score` | FLOAT | AIS composite, recomputed on Achievement write |
| `grit_index` | FLOAT | competitions entered vs won ratio |
| `at_risk_flag` | BOOLEAN | engagement-risk model output |
| `profile_completion_pct` | FLOAT | derived field, updated on profile save |

**Relationships:** 1 User → 1 Profile

---

### Startup
| Field | Type | Notes |
|---|---|---|
| `id` | UUID (PK) | |
| `founder_id` | UUID (FK → Profile) | primary founder |
| `name` | VARCHAR | |
| `sector` | VARCHAR | e.g. HealthTech, FinTech |
| `pitch_summary` | TEXT | source text for embedding |
| `pitch_embedding` | VECTOR(384) | MiniLM encoding of pitch_summary |
| `funding_stage` | ENUM | `pre-seed`, `seed`, `series-a`, `grant` |
| `trl_level` | INT | 1–9 Technology Readiness Level |
| `mrl_level` | INT | 1–9 Market Readiness Level |
| `trl_mrl_gap` | FLOAT | computed: `trl_level - mrl_level` |
| `incubation_status` | ENUM | `pre-incubation`, `active`, `graduated`, `exited` |
| `success_probability` | FLOAT | XGBoost model output |
| `at_risk_flag` | BOOLEAN | engagement-risk model output |
| `mentorship_hours` | FLOAT | aggregated from Interaction records |

**Relationships:** Many Startups → 1 Profile (founder); 1 Startup → Many Interactions; 1 Startup → Many Achievements

---

### Investor
| Field | Type | Notes |
|---|---|---|
| `id` | UUID (PK) | |
| `profile_id` | UUID (FK → Profile) | 1:1 |
| `firm_name` | VARCHAR | |
| `mandate_text` | TEXT | source text for embedding |
| `mandate_embedding` | VECTOR(384) | MiniLM encoding of mandate_text |
| `sector_focus` | JSONB | `["HealthTech", "EdTech"]` |
| `check_size_min_inr` | BIGINT | |
| `check_size_max_inr` | BIGINT | |
| `stage_preference` | JSONB | `["seed", "series-a"]` |

**Relationships:** 1 Investor → 1 Profile; 1 Investor → Many Interactions (with Startups)

---

### Mentor
| Field | Type | Notes |
|---|---|---|
| `id` | UUID (PK) | |
| `profile_id` | UUID (FK → Profile) | 1:1 |
| `expertise_text` | TEXT | source text for embedding |
| `expertise_embedding` | VECTOR(384) | MiniLM encoding of expertise_text |
| `domain_tags` | JSONB | `["Product", "Fundraising", "Tech"]` |
| `available_for_mentoring` | BOOLEAN | alumni toggle |
| `total_sessions_logged` | INT | aggregated from Interaction records |

**Relationships:** 1 Mentor → 1 Profile; 1 Mentor → Many Interactions (with students/founders)

---

### Competition
| Field | Type | Notes |
|---|---|---|
| `id` | UUID (PK) | |
| `name` | VARCHAR | e.g. Smart India Hackathon 2026 |
| `organiser` | VARCHAR | |
| `event_date` | DATE | |
| `deadline` | DATE | registration deadline |
| `nirf_recognised` | BOOLEAN | flags events countable toward NIRF Innovation Achievements |
| `eligible_roles` | JSONB | `["student", "alumni"]` |
| `created_by` | UUID (FK → Profile) | incubation admin who created the record |

**Relationships:** 1 Competition → Many Achievements (results logged post-event)

---

### Interaction
| Field | Type | Notes |
|---|---|---|
| `id` | UUID (PK) | |
| `actor_id` | UUID (FK → Profile) | who initiated |
| `target_id` | UUID (FK → Profile) | who received |
| `type` | ENUM | `mentorship`, `funding_match`, `club_membership`, `competition_team`, `mou` |
| `outcome` | ENUM | `pending`, `accepted`, `declined`, `closed` |
| `duration_hours` | FLOAT | for mentorship sessions |
| `startup_id` | UUID (FK → Startup, nullable) | set when type = `funding_match` |
| `success_label` | BOOLEAN (nullable) | telemetry: set to `true` on "Connect" click → feeds XGBoost retraining |
| `notes` | TEXT | session notes (mentor) or deal notes (investor) |

**Relationships:** Interaction is the edge table for the NetworkX graph (actor → target). Many Interactions → 1 Profile (actor); Many Interactions → 1 Profile (target). Nullable FK to Startup for investor-founder interactions.

---

### Achievement
| Field | Type | Notes |
|---|---|---|
| `id` | UUID (PK) | |
| `profile_id` | UUID (FK → Profile) | who owns this achievement |
| `startup_id` | UUID (FK → Startup, nullable) | set if achievement belongs to a startup |
| `competition_id` | UUID (FK → Competition, nullable) | set if achievement is a competition result |
| `category` | ENUM | `competition`, `patent`, `publication`, `tech_transfer`, `leadership`, `project` |
| `title` | VARCHAR | extracted by DistilBERT NER from certificate |
| `rank_or_prize` | VARCHAR | e.g. "1st Place", "Best Innovation Award" |
| `date` | DATE | |
| `verified` | BOOLEAN | NER-extracted and above confidence threshold |
| `certificate_path` | VARCHAR | S3/local path to uploaded PDF |
| `ner_confidence` | FLOAT | NER extraction confidence score |
| `topic_tags` | JSONB | LDA-generated tags e.g. `["Leadership", "ML"]` |
| `nirf_countable` | BOOLEAN | eligible to appear in NIRF submission |

**Relationships:** Many Achievements → 1 Profile; Optional FK to Startup and Competition.

---

## Relationship Summary

| From | To | Cardinality | Via |
|---|---|---|---|
| User | Profile | 1 : 1 | `Profile.user_id` |
| Profile | Startup | 1 : Many | `Startup.founder_id` |
| Profile | Investor | 1 : 1 | `Investor.profile_id` |
| Profile | Mentor | 1 : 1 | `Mentor.profile_id` |
| Profile | Achievement | 1 : Many | `Achievement.profile_id` |
| Profile | Interaction (as actor) | 1 : Many | `Interaction.actor_id` |
| Profile | Interaction (as target) | 1 : Many | `Interaction.target_id` |
| Startup | Achievement | 1 : Many | `Achievement.startup_id` |
| Startup | Interaction | 1 : Many | `Interaction.startup_id` |
| Competition | Achievement | 1 : Many | `Achievement.competition_id` |
| Investor | Interaction | 1 : Many | via `actor_id` where `type='funding_match'` |
| Mentor | Interaction | 1 : Many | via `actor_id` where `type='mentorship'` |

**Graph edge table:** `Interaction` is the sole edge table consumed by NetworkX.
Every row with `outcome='accepted'` becomes a directed edge `actor_id → target_id`
in the ecosystem graph. No separate graph schema required.

**Feature store columns:** `Profile.betweenness_centrality`, `Profile.pagerank_score`,
`Profile.community_id`, `Profile.at_risk_flag`, `Startup.success_probability`,
`Startup.at_risk_flag` are all written by the nightly Celery Beat task and read
by DRF serializers — no separate feature store infrastructure.
