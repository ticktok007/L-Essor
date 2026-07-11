"""
benchmark_vectorization.py
Campus Innovation & Engagement Intelligence Hub — Phase 1, Day 12

Benchmarks slow vs vectorized generator performance and reports
label distributions before/after enforcement.

Run: python benchmarks/benchmark_vectorization.py
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data.generation.distribution_enforcer import (
    enforce_all_targets,
    summarize_label_distribution,
)
from data.generation.vectorized_generator import (
    generate_slow_records,
    generate_vectorized_records,
)


def _avg_time(fn, repeats: int) -> tuple[float, Any]:
    """Run fn() `repeats` times; return (avg_seconds, last_result)."""
    result = None
    total  = 0.0
    for _ in range(repeats):
        t0     = time.perf_counter()
        result = fn()
        total += time.perf_counter() - t0
    return round(total / repeats, 4), result


def run_benchmark(n: int = 50_000, seed: int = 42, repeats: int = 3) -> dict:
    """
    Benchmarks slow, vectorized, and vectorized+enforcement generators.
    Returns a summary dict suitable for JSON serialisation.
    """
    print(f"Benchmarking n={n:,} records, {repeats} repeat(s) each ...\n")

    # Slow
    slow_avg, slow_records = _avg_time(lambda: generate_slow_records(n, seed), repeats)
    print(f"  slow          : {slow_avg:.4f}s avg")

    # Vectorized
    vec_avg, vec_records = _avg_time(lambda: generate_vectorized_records(n, seed), repeats)
    print(f"  vectorized    : {vec_avg:.4f}s avg")

    # Vectorized + enforcement
    def _vec_and_enforce():
        r = generate_vectorized_records(n, seed)
        return enforce_all_targets(r)

    enf_avg, enf_records = _avg_time(_vec_and_enforce, repeats)
    print(f"  vec+enforce   : {enf_avg:.4f}s avg")

    speedup = round(slow_avg / vec_avg, 2) if vec_avg > 0 else float("inf")
    print(f"\n  speedup       : {speedup}×  (slow / vectorized)")

    dist_before = summarize_label_distribution(vec_records)
    dist_after  = summarize_label_distribution(enf_records)

    return {
        "benchmark_params": {"n": n, "seed": seed, "repeats": repeats},
        "timings_seconds": {
            "slow_avg":              slow_avg,
            "vectorized_avg":        vec_avg,
            "vectorized_enforce_avg": enf_avg,
            "speedup_ratio":         speedup,
        },
        "label_distribution_before_enforcement": dist_before,
        "label_distribution_after_enforcement":  dist_after,
    }


if __name__ == "__main__":
    result = run_benchmark()
    print()
    print(json.dumps(result, indent=2))