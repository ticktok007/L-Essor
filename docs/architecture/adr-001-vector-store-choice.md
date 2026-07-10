# ADR-001 — Vector Store Choice
**Project:** Campus Innovation & Engagement Intelligence Hub
**Date:** Day 4, Phase 0 (Jul 09, 2026)
**Author:** Sanjay (24AM0100), Chennai Institute of Technology

---

## Title
Use PostgreSQL + pgvector as the vector store instead of a dedicated vector database.

## Status
**ACCEPTED**

---

## Context

The AI matchmaking engine requires storing and querying dense embedding vectors
for:
- `Startup.pitch_embedding` — 384-dim MiniLM vector of the startup's pitch summary
- `Investor.mandate_embedding` — 384-dim MiniLM vector of the investor's mandate text
- `Mentor.expertise_embedding` — 384-dim MiniLM vector of mentor expertise description
- `Profile.skills_embedding` — 384-dim MiniLM vector of student/alumni skill profile

At the project's target scale (≤ 20,000 profiles, ≤ 500 concurrent users) the
vector query load is moderate: a single cosine-similarity ANN query over 20,000
vectors with an `ivfflat` index completes in < 10 ms on a standard PaaS Postgres
instance.

The project already requires PostgreSQL for all relational data. The decision is
whether to introduce a dedicated vector database (Qdrant, Weaviate, Pinecone) as
a second persistence layer or extend PostgreSQL with pgvector.

---

## Decision

Use **PostgreSQL 16 + pgvector 0.7.x** as the sole vector store.

- Add `VectorField(dimensions=384)` to the relevant Django models via
  `pgvector-django`.
- Create an `ivfflat` index with `lists=100` on each vector column for
  approximate nearest-neighbour search.
- Execute similarity queries using pgvector's native distance operators
  (`<=>` for cosine, `<->` for L2) directly in DRF querysets — no separate
  query client needed.
- All vector reads/writes share the same Django ORM transaction context as
  their owning entity — atomicity is free.

---

## Consequences

**Positive**
- Zero additional infrastructure: no second database process, no second
  connection pool, no second deployment unit, no second backup strategy.
- Django ORM access: `Startup.objects.order_by(CosineDistance('pitch_embedding', query_vector))[:5]` — readable, testable, and covered by the existing pytest suite.
- Single Docker Compose service covers both relational and vector workloads.
- Free-tier deployment on Render/Railway remains viable — a dedicated vector
  database service would require a paid tier or a second free-tier instance.
- Transactional consistency: a new startup record and its embedding vector are
  committed or rolled back together.

**Negative / Trade-offs**
- `ivfflat` is an approximate index (recall ~95% at `lists=100, probes=10`);
  pgvector's `hnsw` index (exact, higher recall) is available as an upgrade
  path if recall becomes a concern.
- At > 1M vectors, a dedicated ANN engine (Qdrant, Weaviate) would outperform
  pgvector on raw query throughput. The upgrade path is documented: swap the
  similarity query layer behind a `VectorSearchService` abstraction class
  without touching model definitions or API contracts.
- pgvector requires the extension to be enabled on the Postgres instance
  (`CREATE EXTENSION vector;`) — one-time setup, documented in the
  `load_synthetic_data` management command.

---

## Alternatives Considered

| Option | Reason Not Chosen |
|---|---|
| **Qdrant** | Excellent ANN performance, but requires a separate container, separate client library, and breaks transactional consistency with entity data. Unjustified at ≤ 20,000 vectors. |
| **Weaviate** | GraphQL query interface adds learning overhead; multi-modal features irrelevant to this project; same infrastructure-sprawl concern as Qdrant. |
| **Pinecone** | Fully managed, zero ops — but introduces per-query latency to an external API, a monthly cost, and PII exposure for student/alumni text embeddings. |
| **FAISS (in-memory)** | Fast and accurate, but in-memory only — vectors are lost on process restart, requiring a reload step on every worker boot. No persistence without a custom serialisation layer. |
| **SQLite + sqlite-vss** | Not viable for production: single-writer lock, no pgvector ecosystem, not supported on target PaaS deployment. |
