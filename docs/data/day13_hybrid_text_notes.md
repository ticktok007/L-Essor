# Day 13 Hybrid Text Generation Notes
**Project:** Campus Innovation & Engagement Intelligence Hub
**Phase:** 1 — Synthetic Data Foundation
**Files:** `data/text/hybrid_text_generator.py`, `data/text/text_variation_bank.py`, `data/text/deduplication.py`

---

## Scope
Produce synthetic startup pitch summaries and investor/mentor mandate texts with
genuine semantic variety for the Phase 3 embedding-based NLP matcher.

---

## Hybrid Generation Approach

| Field type | Method |
|---|---|
| Structured fields (`sector`, `stage`, `check_size_band`, etc.) | Deterministic selection from typed pools in `text_variation_bank.py` |
| Free-text fields (`pitch_summary`, `mandate_text`) | Multi-frame rendering: sentence frame family selected per record × varied clause content from sector-specific pools |

Six PITCH_FRAMES families for startups (problem→solution, user-first,
outcome-first, context→gap, thesis, comparative).
Four INVESTOR_MANDATE_FRAMES (thesis-driven, operator-value-add,
market-outcome, portfolio-fit).
Four MENTOR_MANDATE_FRAMES (hands-on builder, strategic advisor, domain
specialist, network connector).

---

## Semantic Variety Strategy
Variety comes from three independent axes of variation:
1. **Frame family** — different sentence skeleton per record.
2. **Clause content** — sector-specific problem, user, value, and tech pools
   have 5–6 distinct phrases each, not synonym swaps.
3. **Field combination** — problem × user × value × tech combinations produce
   combinatorial variety well beyond the pool sizes.

Target: unique-text ratio ≥ 0.80 at n=60 for each entity type.

---

## Deduplication Approach
`deduplication.py` normalises text (lowercase, strip punctuation, collapse
whitespace) then uses `difflib.SequenceMatcher` for O(n²) pairwise similarity.
Default threshold: 0.92. Strategy: keep first occurrence; remove later records
whose normalised text is within threshold of any kept record. Feature columns
are never modified — only the record membership in the output list changes.
Input list is never mutated.

---

## Assumptions
- Standard library only — no sentence-transformers or NLTK at this stage.
- Slow O(n²) deduplication is acceptable for n < 5,000; Phase 3 embedding
  similarity will provide production-grade deduplication at scale.
- Sector cycling (`i % len(SECTORS)`) distributes records evenly; callers can
  pass a pre-shuffled sector list for non-uniform distributions.
- `text_similarity` normalises inputs internally so callers need not pre-process.