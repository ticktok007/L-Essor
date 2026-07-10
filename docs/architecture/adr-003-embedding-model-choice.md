# ADR-003 — Embedding Model Choice
**Project:** Campus Innovation & Engagement Intelligence Hub
**Date:** Day 4, Phase 0 (Jul 09, 2026)
**Author:** Sanjay (24AM0100), Chennai Institute of Technology

---

## Title
Use all-MiniLM-L12-v2 as the sentence embedding model for semantic matchmaking
and portfolio/pitch text encoding.

## Status
**ACCEPTED**

---

## Context

The AI matchmaking engine requires dense vector representations of:
- Startup pitch summaries (100–500 words typically)
- Investor mandate descriptions (50–200 words)
- Mentor expertise profiles (free-text, 50–300 words)
- Student skill and interest descriptions (free-text, 20–150 words)

Requirements for the embedding model:
1. **Semantic quality** sufficient to distinguish a HealthTech pitch from an
   EdTech pitch, and to capture latent overlap between a "supply-chain expert"
   mentor and a "logistics-tech" startup even without shared keywords.
2. **CPU-only inference** — no GPU available on the free-tier deployment target.
3. **Low latency** — batch embedding on ingestion is acceptable; per-request
   embedding at match time must complete in < 1 second.
4. **Local execution** — no external API dependency; no PII exposure of
   student/investor text to a third-party service.
5. **384-dimensional output** — low enough to keep pgvector index size small
   at 20,000 profile scale.

---

## Decision

Use **`sentence-transformers/all-MiniLM-L12-v2`** loaded via the
`sentence-transformers` library.

- 33M parameters — 4× smaller than BERT-base (110M), 40% smaller than
  DistilBERT (66M).
- 384-dimensional output vectors — compact, cheap to store in pgvector, fast
  to index.
- Pre-trained on 1B+ sentence pairs (including S2ORC scientific papers, Reddit
  comments, StackExchange Q&A, NLI datasets) — strong domain coverage for
  startup/tech/academic language without fine-tuning.
- Achieves 97% of BERT-base's SBERT performance on semantic similarity
  benchmarks (STSB Spearman r = 0.879 vs BERT-base 0.905) at 4× the speed.
- CPU inference: ~50–80ms per sentence on a standard x86 core; batch of 100
  sentences in ~2–4 seconds — well within the ingestion pipeline's tolerance.
- Uncased tokenisation — correct for pitch summaries and mandate text where
  mixed capitalisation is common and proper-noun casing is irrelevant to
  semantic matching.
- `encode()` call is synchronous and stateless — trivially wrappable in a
  Celery task and cacheable by input hash.

### Usage pattern
```python
from sentence_transformers import SentenceTransformer

_model = SentenceTransformer('all-MiniLM-L12-v2')  # loaded once at startup

def encode(text: str) -> list[float]:
    if not text or not text.strip():
        return [0.0] * 384
    return _model.encode(text[:512], normalize_embeddings=True).tolist()
```
Model is loaded once in `apps.py` `ready()` hook; all subsequent calls reuse
the in-memory instance — no repeated disk I/O per request.

---

## Consequences

**Positive**
- Runs on CPU with no GPU dependency — compatible with Render/Railway free tier.
- 384-dim vectors keep the pgvector `ivfflat` index compact and fast at
  20,000 profile scale (~30 MB for the full investor mandate index).
- `normalize_embeddings=True` produces unit vectors — cosine similarity reduces
  to a dot product, which pgvector computes efficiently with the `<=>` operator.
- No external API call at match time — latency is deterministic, no rate limits,
  no downtime dependency, no PII leaves the server.
- No fine-tuning required for the domain — pre-training corpus already includes
  technical, academic, and startup-relevant text.

**Negative / Trade-offs**
- 512-token input limit — pitch summaries longer than ~380 words are silently
  truncated. Mitigation: the ingestion pipeline logs a warning and stores the
  truncation flag on the `Startup` record; users are prompted to keep pitches
  concise.
- Not the strongest model for very long documents (full research papers, long
  investor theses). For the short-to-medium texts this project embeds, the
  accuracy delta vs. larger models is negligible.
- Model weights (~90 MB) must be bundled in the Docker image or downloaded on
  first boot. Documented in the Dockerfile: `RUN python -c "from
  sentence_transformers import SentenceTransformer;
  SentenceTransformer('all-MiniLM-L12-v2')"` pre-warms the cache at build time.

---

## Alternatives Considered

| Option | Reason Not Chosen |
|---|---|
| **OpenAI text-embedding-3-small** | Per-request API cost ($0.02 / 1M tokens — non-trivial at scale), external latency, and PII exposure of student/alumni/startup text to OpenAI's API. Local model preferred. |
| **OpenAI text-embedding-3-large** | Same PII and cost concerns; 3,072-dim output increases pgvector storage and index time ~8× with no accuracy gain on short pitch texts. |
| **BERT-base-uncased (SBERT fine-tuned)** | 110M parameters, ~4× slower CPU inference, requires 768-dim pgvector columns (2× storage), no meaningful accuracy improvement on the short texts this project processes. |
| **all-MiniLM-L6-v2** | 6-layer vs 12-layer variant — ~1.5× faster but measurable accuracy drop on STSB (Spearman r = 0.814 vs 0.879). The L12 variant's extra accuracy is worth the modest speed cost for a matchmaking use case where ranking quality matters. |
| **DistilBERT-base (SBERT)** | 66M parameters, 768-dim output, slower than MiniLM-L12 on semantic similarity tasks despite being smaller than BERT-base. No advantage over MiniLM-L12-v2 on either speed or accuracy for this use case. |
| **GTE-small / E5-small-v2** | Comparable accuracy to MiniLM-L12-v2 but smaller sentence-transformers ecosystem support and less community validation on startup/academic domain text. MiniLM-L12-v2 has broader production evidence. |
