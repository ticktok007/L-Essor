# Vector Fields and Indexing
**Project:** Campus Innovation & Engagement Intelligence Hub
**Module:** ecosystem — Startup, Investor
**Phase:** 2 (fields) / 3 (embeddings populated)

## Purpose
Enable cosine-similarity approximate nearest-neighbour (ANN) search across
startup pitch summaries and investor mandate texts directly within PostgreSQL,
eliminating the need for a separate vector database at Phase 2–5 scale.

## Model Changes

| Model | Field | Type | Dimensions |
|---|---|---|---|
| `Startup` | `pitch_embedding` | `VectorField` | 384 |
| `Investor` | `mandate_embedding` | `VectorField` | 384 |

Both fields are `null=True, blank=True` — empty until the Phase 3 embedding
pipeline populates them via the `all-MiniLM-L12-v2` model (sentence-transformers).
Vectors are unit-normalised before storage so cosine similarity reduces to a
dot-product, which pgvector computes efficiently with the `<=>` operator.

## Index Strategy
- **Index type:** `ivfflat` (Inverted File with Flat quantisation)
- **Operator class:** `vector_cosine_ops` (cosine distance)
- **`lists` parameter:** `100` — suitable for datasets up to ~500k vectors;
  increase to `lists = sqrt(n_rows)` as the corpus grows past 100k rows.
- **Created with:** `CONCURRENTLY` — no table lock during index build.
- Indexes are created via `RunSQL` in migration `0002` with full reverse SQL
  for clean rollback.

## Notes
- `pgvector` extension is already enabled on the PostgreSQL instance (ADR-001);
  this migration does not re-create it.
- The `ivfflat` index requires at least one non-null vector row before it can
  be probed; the Phase 3 batch-embedding pipeline must run before the matching
  engine queries the index.
- Upgrade path: swap `ivfflat` for `hnsw` (exact, higher recall) by adding a
  new migration — the DRF query layer uses pgvector's `<=>` operator and is
  index-type agnostic.
- See `docs/architecture/adr-001-vector-store-choice.md` for the full decision
  rationale behind PostgreSQL + pgvector over a dedicated vector database.