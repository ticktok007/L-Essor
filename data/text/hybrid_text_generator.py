"""
hybrid_text_generator.py
Campus Innovation & Engagement Intelligence Hub — Phase 1, Day 13

Hybrid text generator: structured fields from templates,
free-text fields from a multi-frame variation bank.

No external dependencies.
"""

import collections
import random
import re
from typing import Any

from data.text.text_variation_bank import (
    CHECK_SIZES,
    INVESTOR_INTEREST_THEMES,
    INVESTOR_MANDATE_FRAMES,
    INVESTOR_OUTCOME_PHRASES,
    MENTOR_MANDATE_FRAMES,
    MENTOR_SUPPORT_STYLES,
    PITCH_FRAMES,
    PROBLEM_AREAS,
    SECTORS,
    STAGES,
    TARGET_USERS,
    TECHNOLOGY_TAGS,
    VALUE_PROPOSITIONS,
)

# ── Helpers ───────────────────────────────────────────────────────────────────

def _rng(seed: int) -> random.Random:
    return random.Random(seed)


def _pick(rng: random.Random, pool: list) -> Any:
    return rng.choice(pool)


def _sample(rng: random.Random, pool: list, k: int) -> list:
    return rng.sample(pool, min(k, len(pool)))


def _entity_name(sector: str, idx: int) -> str:
    suffixes = ["AI", "Labs", "Tech", "Solutions", "Systems", "Platforms", "Ventures"]
    words    = {"healthtech": "Medi", "fintech": "Fino", "edtech": "Skilla",
                "agritech": "Agro", "climate": "Verdant", "mobility": "Nexus"}
    return f"{words.get(sector, 'Nova')}{idx % 90 + 10}"


# ── Pitch summary renderer ────────────────────────────────────────────────────

def render_pitch_summary(
    rng: random.Random,
    sector: str,
    entity_name: str,
    problem_area: str,
    target_user: str,
    value_proposition: str,
    tech_tags: list[str],
) -> str:
    frame = _pick(rng, PITCH_FRAMES)
    t1    = tech_tags[0] if tech_tags else "AI"
    t2    = tech_tags[1] if len(tech_tags) > 1 else "data analytics"
    return frame.format(
        sector=sector,
        entity_name=entity_name,
        problem_area=problem_area,
        target_user=target_user,
        value_proposition=value_proposition,
        tech1=t1,
        tech2=t2,
    ).strip()


# ── Mandate text renderer ─────────────────────────────────────────────────────

def render_mandate_text(
    rng: random.Random,
    entity_type: str,
    sector: str,
    stage: str,
    interest_themes: list[str],
    support_styles: list[str],
    outcome_phrase: str,
) -> str:
    if entity_type == "investor":
        frame = _pick(rng, INVESTOR_MANDATE_FRAMES)
        t1    = interest_themes[0] if interest_themes else "market expansion"
        t2    = interest_themes[1] if len(interest_themes) > 1 else "unit economics"
        return frame.format(
            sector_focus=sector,
            stage=stage,
            interest_theme1=t1,
            interest_theme2=t2,
            outcome_phrase=outcome_phrase,
        ).strip()
    else:  # mentor
        frame = _pick(rng, MENTOR_MANDATE_FRAMES)
        s1    = support_styles[0] if support_styles else "go-to-market strategy"
        s2    = support_styles[1] if len(support_styles) > 1 else "fundraising preparation"
        return frame.format(
            domain=sector,
            support1=s1,
            support2=s2,
        ).strip()


# ── Record builders ───────────────────────────────────────────────────────────

def build_startup_record(
    rng: random.Random,
    record_id: int,
    sector: str,
) -> dict[str, Any]:
    problem_area      = _pick(rng, PROBLEM_AREAS[sector])
    target_user       = _pick(rng, TARGET_USERS[sector])
    value_proposition = _pick(rng, VALUE_PROPOSITIONS[sector])
    tech_pool         = TECHNOLOGY_TAGS[sector]
    tech_tags         = _sample(rng, tech_pool, rng.randint(2, 4))
    entity_name       = _entity_name(sector, record_id)
    stage             = _pick(rng, STAGES)

    pitch = render_pitch_summary(
        rng, sector, entity_name, problem_area, target_user,
        value_proposition, tech_tags,
    )
    return {
        "record_id":         record_id,
        "entity_type":       "startup",
        "sector":            sector,
        "stage":             stage,
        "problem_area":      problem_area,
        "target_user":       target_user,
        "value_proposition": value_proposition,
        "technology_tags":   tech_tags,
        "pitch_summary":     pitch,
    }


def build_investor_record(
    rng: random.Random,
    record_id: int,
    sector: str,
) -> dict[str, Any]:
    stage           = _pick(rng, STAGES[:3])   # investors skip grant-stage
    check_size_band = _pick(rng, CHECK_SIZES[:-1])
    themes          = _sample(rng, INVESTOR_INTEREST_THEMES[sector], 2)
    outcome_phrase  = _pick(rng, INVESTOR_OUTCOME_PHRASES)

    mandate = render_mandate_text(
        rng, "investor", sector, stage, themes, [], outcome_phrase
    )
    return {
        "record_id":       record_id,
        "entity_type":     "investor",
        "sector_focus":    sector,
        "preferred_stage": stage,
        "check_size_band": check_size_band,
        "interest_themes": themes,
        "support_style":   "capital + network",
        "mandate_text":    mandate,
    }


def build_mentor_record(
    rng: random.Random,
    record_id: int,
    sector: str,
) -> dict[str, Any]:
    support_styles = _sample(rng, MENTOR_SUPPORT_STYLES[sector], 2)
    stage          = _pick(rng, STAGES)

    mandate = render_mandate_text(
        rng, "mentor", sector, stage, [], support_styles, ""
    )
    return {
        "record_id":       record_id,
        "entity_type":     "mentor",
        "sector_focus":    sector,
        "preferred_stage": stage,
        "check_size_band": "advisory only",
        "interest_themes": support_styles,
        "support_style":   "hands-on guidance",
        "mandate_text":    mandate,
    }


# ── Batch generators ──────────────────────────────────────────────────────────

def generate_startup_records(n: int, seed: int = 42) -> list[dict]:
    rng     = _rng(seed)
    sectors = SECTORS
    return [
        build_startup_record(rng, i + 1, sectors[i % len(sectors)])
        for i in range(n)
    ]


def generate_investor_records(n: int, seed: int = 42) -> list[dict]:
    rng     = _rng(seed)
    sectors = SECTORS
    return [
        build_investor_record(rng, i + 1, sectors[i % len(sectors)])
        for i in range(n)
    ]


def generate_mentor_records(n: int, seed: int = 42) -> list[dict]:
    rng     = _rng(seed)
    sectors = SECTORS
    return [
        build_mentor_record(rng, i + 1, sectors[i % len(sectors)])
        for i in range(n)
    ]


# ── Diversity stats ───────────────────────────────────────────────────────────

def compute_text_diversity_stats(
    records: list[dict],
    text_key: str,
) -> dict[str, Any]:
    """
    Report text diversity metrics for a field across a list of records.
    """
    texts  = [r.get(text_key, "") for r in records]
    tokens = [t.lower().split() for t in texts]

    # Unique text ratio
    unique_texts = set(texts)

    # Average token count
    total_tokens = sum(len(t) for t in tokens)
    avg_tokens   = round(total_tokens / len(texts), 2) if texts else 0.0

    # Top repeated bigrams
    bigram_counter: collections.Counter = collections.Counter()
    for tok in tokens:
        for i in range(len(tok) - 1):
            bigram_counter[(tok[i], tok[i + 1])] += 1
    top_bigrams = [
        {"phrase": f"{a} {b}", "count": c}
        for (a, b), c in bigram_counter.most_common(5)
    ]

    return {
        "record_count":       len(records),
        "unique_text_count":  len(unique_texts),
        "unique_text_ratio":  round(len(unique_texts) / len(records), 4) if records else 0.0,
        "avg_token_count":    avg_tokens,
        "top_repeated_phrases": top_bigrams,
    }