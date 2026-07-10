# ADR-002 — Graph Engine Choice
**Project:** Campus Innovation & Engagement Intelligence Hub
**Date:** Day 4, Phase 0 (Jul 09, 2026)
**Author:** Sanjay (24AM0100), Chennai Institute of Technology

---

## Title
Use NetworkX (in-process Python) instead of Neo4j for the graph intelligence layer.

## Status
**ACCEPTED**

---

## Context

The Social Network Analysis module requires constructing and analysing a graph
of campus ecosystem relationships:
- **Nodes:** User profiles (students, alumni, investors, mentors)
- **Edges:** Interactions stored in the `interactions` table
  (mentor sessions, investor–founder touches, club memberships, competition teams)

Required graph operations:
- Betweenness Centrality — identify super-connectors bridging isolated clusters
- PageRank — surface transitive influence across the network
- Louvain Community Detection — auto-discover sub-ecosystems
- Ego network queries — direct + 2-hop connections for an individual node
- Link prediction heuristics (Common Neighbours / Jaccard) — post-MVP

At the project's target scale (≤ 20,000 nodes, estimated ≤ 200,000 edges) all
these operations are computationally tractable in-process with NetworkX on a
standard compute instance.

The decision is whether to introduce Neo4j as a graph database or compute graph
intelligence in-process using NetworkX on data sourced from PostgreSQL.

---

## Decision

Use **NetworkX 3.x** as the graph computation engine, running as a Python
library within the Django/Celery process. No graph database is deployed.

- On a nightly Celery Beat schedule, a task reads the full `interactions` table
  from PostgreSQL and constructs a `networkx.Graph` in memory.
- Centrality scores (betweenness, PageRank) and community labels (Louvain) are
  computed and written back to `profiles.betweenness_centrality`,
  `profiles.pagerank_score`, and `profiles.community_id` columns in PostgreSQL.
- The `/api/v1/graph/ecosystem/` DRF endpoint reads pre-computed scores from
  PostgreSQL — no live graph traversal on request.
- Ego network queries (direct + 2-hop) are computed on-demand from the
  `interactions` table using a lightweight subgraph extraction, not a full
  graph reload.

---

## Consequences

**Positive**
- Zero additional infrastructure: no Neo4j container, no JVM, no Cypher DSL,
  no separate graph backup. The graph layer adds exactly one Python package
  (`networkx`) and one Celery task.
- Entire graph stack is Python: NetworkX, python-louvain (`community` package),
  and standard NetworkX centrality functions — no new language or query
  paradigm for the development team to learn.
- Pre-computed scores stored in PostgreSQL columns are queryable with standard
  Django ORM — the leadership dashboard reads `profiles.betweenness_centrality`
  the same way it reads any other field.
- Single Docker Compose file still describes the entire backend — no Neo4j
  service entry.
- Free-tier deployment stays viable — Neo4j's free tier (AuraDB) has a 200,000
  node / 400,000 relationship limit and no persistent storage on the free plan.

**Negative / Trade-offs**
- Graph is recomputed in bulk nightly (not real-time). For this project's
  use case (ecosystem intelligence for leadership, not live social feeds) a
  24-hour staleness window is acceptable. The `computed_at` timestamp is
  surfaced on the dashboard so users understand freshness.
- In-memory graph construction at > 500,000 edges may exceed available RAM on
  a small PaaS instance. Upgrade path: move to Neo4j GDS or a graph projection
  layer behind the existing `GraphService` abstraction — API contracts unchanged.
- Cypher's expressive traversal syntax (multi-hop patterns, path queries) is
  not available. For the operations required (centrality, community, ego
  network), NetworkX's API is sufficient and more readable.

---

## Alternatives Considered

| Option | Reason Not Chosen |
|---|---|
| **Neo4j Community (self-hosted)** | Requires a JVM-based container, Cypher DSL, the `neo4j` Python driver, a separate backup strategy, and a separate deployment unit. Infrastructure cost not justified for graph operations that NetworkX handles natively in-process. |
| **Neo4j AuraDB (managed)** | Free tier storage and relationship limits, paid tier cost, external network call from Celery task, and PII exposure of student interaction data to a third-party service. |
| **Amazon Neptune** | AWS vendor lock-in, cost, and operational overhead entirely disproportionate to the project's scale and deployment target (Render/Railway). |
| **DGL / PyTorch Geometric (GNN)** | Graph Neural Networks (LightGCN, GraphSAGE) are explicitly deferred as Post-MVP items. They require GPU infrastructure and labelled training data not available at this stage. Documented as a roadmap item for evaluators. |
| **igraph (Python)** | Faster than NetworkX at very large scale but less readable API, smaller ecosystem, and no meaningful performance advantage at ≤ 200,000 edges. |
