# Stack Lock
**Module:** Architecture Decisions — Final Stack
**Project:** Campus Innovation & Engagement Intelligence Hub
**Locked:** Day 4, Phase 0 (Jul 09, 2026)
**Author:** Sanjay (24AM0100), Chennai Institute of Technology
**Status:** LOCKED — do not change without a new ADR

---

## Final Chosen Stack

| Layer | Technology | Version Target |
|---|---|---|
| Backend framework | Django + Django REST Framework | Django 5.x, DRF 3.15.x |
| Database | PostgreSQL + pgvector extension | PostgreSQL 16, pgvector 0.7.x |
| Embedding model | all-MiniLM-L12-v2 | sentence-transformers 3.x |
| ML / predictive | XGBoost + scikit-learn | XGBoost 2.x, scikit-learn 1.5.x |
| Graph intelligence | NetworkX | 3.x |
| NLP / NER | DistilBERT (HuggingFace pipeline) | transformers 4.x |
| Task queue | Celery + Redis | Celery 5.x, Redis 7.x |
| Error monitoring | Sentry | sentry-sdk 2.x |
| Frontend | React + Chart.js / Recharts | React 18.x |
| Containerisation | Docker + Docker Compose | Docker 26.x |
| CI/CD | GitHub Actions | — |
| Deployment target | Render / Railway | — |

---

## What Each Core Tool Is Responsible For

### Django + Django REST Framework
- Owns all business logic, authentication (JWT via simplejwt), and role-based permissions.
- Exposes every platform capability as versioned DRF endpoints under `/api/v1/`.
- Hosts the Django Admin panel for internal data QA.
- Runs management commands for bulk synthetic data ingestion and model retraining triggers.

### PostgreSQL + pgvector
- Single source of truth for all relational data: users, profiles, startups, investors, mentors, interactions, achievements, competitions.
- Stores 384-dimensional MiniLM embedding vectors in `VectorField` columns on `Startup` and `Investor` models.
- Executes approximate nearest-neighbour (ANN) queries natively via the `ivfflat` index — no separate vector database process required.
- Serves as the feature store: computed ML features (AIS, Grit Index, TRL–MRL gap) live as typed columns alongside raw entity data.

### all-MiniLM-L12-v2
- Encodes startup pitch summaries, investor mandates, mentor expertise descriptions, and student skill profiles into 384-dimensional dense vectors.
- Powers cosine-similarity matching for investor–founder, mentor–mentee, and peer-team matchmaking.
- Runs entirely on CPU at inference time — no GPU required for the embedding step, keeping deployment costs at zero on a free-tier host.

---

## Why This Stack Fits the Project

- **No infrastructure sprawl.** pgvector eliminates a separate vector database; NetworkX eliminates Neo4j; a single PostgreSQL instance covers relational data, vector search, and the feature store. The entire backend fits in one Docker Compose file.
- **Deployable on a free tier.** Django + Postgres on Render/Railway, Redis on Upstash — the full stack runs at zero recurring cost for a demo/hackathon deployment, which matters for evaluators reproducing the build.
- **Python-native end to end.** Django, scikit-learn, XGBoost, NetworkX, HuggingFace, Celery — no context-switching between language runtimes. A single `requirements.txt` describes the entire backend.
- **NIRF-submission-ready from day one.** DRF's structured API responses and Django's ORM aggregations are sufficient to power the 19-metric NIRF dashboard without a separate analytics pipeline.
- **Incrementally upgradeable.** pgvector → Qdrant/Weaviate, NetworkX → Neo4j GDS, XGBoost → LightGCN — each component can be swapped independently behind its existing API contract when scale demands it. No rewrite required.

---

## Not Chosen — Short Notes

| Alternative | Rejected Because |
|---|---|
| FastAPI instead of Django | Django Admin, Django ORM, simplejwt, and drf-spectacular save 2–3 weeks of boilerplate at this scale. FastAPI's async advantage is not needed; bottleneck is ML inference, not I/O concurrency. |
| Qdrant / Weaviate / Pinecone as vector store | Adds a second database process, second connection pool, and second deployment unit for a capability pgvector already provides. Operational overhead not justified at ≤ 20,000 profiles. |
| Neo4j as graph database | Requires a separate server process, Cypher DSL, and Java-based infrastructure for graph algorithms that NetworkX provides as pure-Python calls on the existing PostgreSQL interaction data. See ADR-002. |
| OpenAI text-embedding-3-small | Per-request API cost, latency dependency on an external service, and data-privacy exposure of student/alumni PII. MiniLM-L12-v2 runs locally, is free, and performs comparably on short-text semantic similarity. See ADR-003. |
| BERT-base / RoBERTa for embeddings | 4× larger (110M vs 33M parameters), 4× slower inference, with no meaningful accuracy gain on the short pitch-summary and mandate texts this project embeds. See ADR-003. |
| MongoDB as primary database | No native vector support, weaker relational integrity for the many-to-many interaction graph, and no pgvector ecosystem. PostgreSQL handles both relational and vector workloads in one process. |
