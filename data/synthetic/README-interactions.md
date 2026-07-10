# Synthetic Interaction Dataset — README
**Project:** Campus Innovation & Engagement Intelligence Hub
**Phase:** 1 — Synthetic Data Foundation
**Generator:** `scripts/generate_interaction_data.py`
**Seed:** 42 (fully reproducible)

---

## Files in This Directory

### `interaction_edges.csv`
Graph edge table — the backbone of the NetworkX Social Network Analysis layer.
Every row is a directed relationship between two ecosystem nodes.

| Field | Description |
|---|---|
| `edge_id` | Unique ID — format `EDG000001` |
| `source_profile_id` | Initiating node: `STU-####`, `ALU-####`, `INV-####`, `MEN-####` |
| `target_profile_id` | Receiving node: profile ID or `CLB-####` (club/community) |
| `edge_type` | `mentor_mentee` / `investor_founder` / `club_membership` |
| `relationship_strength` | `weak` / `medium` / `strong` |
| `interaction_count` | Integer; logically consistent with `relationship_strength` |
| `first_interaction_context` | Short realistic description of how the relationship started |
| `last_interaction_context` | Short realistic description of most recent interaction |
| `created_at` | ISO date of first interaction |

**Graph shape note:** Hub nodes are seeded deliberately. A small number of
`MEN-####` and `INV-####` IDs appear at significantly higher degree than
average, mirroring real campus super-connector dynamics. Degree distribution
plot confirms hub-and-spoke shape.

---

### `competition_records.csv`
One row per competition participation event. Used by the Competition & Achievement
Tracker, NIRF Innovation Achievements metric, and participation-rate analytics.

| Field | Description |
|---|---|
| `competition_id` | Unique ID — format `CMP00001` |
| `profile_id` | Participating profile: `STU-####` or `ALU-####` |
| `competition_name` | Realistic hackathon / challenge / demo day name |
| `competition_type` | `hackathon` / `innovation_challenge` / `startup_pitch` / `demo_day` / etc. |
| `year` | Participation year (2019–2025) |
| `participation_role` | `participant` / `finalist` / `winner` / `organizer` / `mentor_judge` |
| `result` | Logically consistent with `participation_role` |
| `team_size` | Integer; 0 for non-competing roles |
| `theme` | Domain theme of the competition |

---

### `achievement_records.csv`
One row per achievement. Source data for the Portfolio Generator's NER pipeline,
NIRF submission counts, and the Achievement Impact Score (AIS) feature.

| Field | Description |
|---|---|
| `achievement_id` | Unique ID — format `ACH000001` |
| `profile_id` | Owning profile: `STU-####` or `ALU-####` |
| `achievement_type` | `hackathon_win` / `leadership_role` / `incubator_selection` / `research_demo` / `prototype_completion` / `grant_recognition` / `patent_filing` / `publication` / `fellowship` / `award` |
| `title` | Realistic achievement title |
| `issuing_body` | Realistic issuing organisation |
| `year` | Year of achievement (2019–2025) |
| `impact_level` | `campus` / `regional` / `national` |
| `notes` | Short realistic context note |

---

### `interaction_generation_summary.json`
Machine-readable run summary including graph statistics.

| Field | Description |
|---|---|
| `project` | Project name |
| `phase` | Build phase |
| `seed` | Random seed used |
| `generated_files` | Map of filename → row count |
| `graph_stats.total_edges` | Total directed edges generated |
| `graph_stats.total_unique_nodes` | Count of unique node IDs across all edges |
| `graph_stats.edge_type_counts` | Breakdown of edges by type |
| `graph_stats.average_degree` | Mean node degree across the graph |
| `graph_stats.max_degree` | Highest degree node count |
| `graph_stats.top_hub_nodes` | Top 5 highest-degree node IDs |

---

### `degree_distribution.png`
Histogram of node degree counts. Used as a sanity check to confirm the
interaction graph has a realistic hub-and-spoke shape (power-law-like
distribution) rather than uniform random connectivity. A flat distribution
would indicate the graph is not realistic for SNA purposes.

---

## Regenerating

```bash
pip install faker matplotlib
python scripts/generate_interaction_data.py
```

Same seed always produces byte-identical CSV and JSON output.
The PNG will be visually identical but may have minor rendering differences
across platforms.

To scale up, edit the constants at the top of the script:
`NUM_EDGES`, `NUM_COMPETITIONS`, `NUM_ACHIEVEMENTS`.

## Important
All data is entirely synthetic. No real names, organisations, or interaction
histories are used. Safe for development, testing, CI pipelines, and demo.
Do not commit real institutional interaction data into this directory.