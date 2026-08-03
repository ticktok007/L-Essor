"""
load_test_filtered_queries.py
Campus Innovation & Engagement Intelligence Hub — Phase 2, Day 25

Benchmark filtered ORM queries at leadership-dashboard list scale (20,000+ profiles).

Run from repo root:
  python scripts/load_test_filtered_queries.py
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "campushub.settings.dev")

import django  # noqa: E402

django.setup()

from django.db import connection, reset_queries  # noqa: E402

from accounts.models import Profile, User  # noqa: E402
from ecosystem.models import Startup  # noqa: E402

ITERATIONS = 25
WARMUP = 3


def bench(label: str, queryset) -> tuple[str, float, float, int]:
    for _ in range(WARMUP):
        list(queryset)

    reset_queries()
    start = time.perf_counter()
    count = 0
    for _ in range(ITERATIONS):
        count = len(list(queryset))
    elapsed_ms = (time.perf_counter() - start) * 1000
    avg_ms = elapsed_ms / ITERATIONS
    return label, elapsed_ms, avg_ms, count


def main() -> None:
    user_count = User.objects.count()
    profile_count = Profile.objects.count()
    startup_count = Startup.objects.count()

    workloads = [
        bench(
            "profiles_by_role",
            User.objects.filter(role="student").only("id", "role", "email"),
        ),
        bench(
            "profiles_by_department",
            Profile.objects.filter(department="Computer Science & Engineering"),
        ),
        bench(
            "startups_by_funding_stage",
            Startup.objects.filter(funding_stage="seed", is_active=True),
        ),
        bench(
            "startups_by_sector",
            Startup.objects.filter(sector="HealthTech", is_active=True),
        ),
        bench(
            "combined_startup_filters",
            Startup.objects.filter(
                sector="FinTech",
                funding_stage="pre-seed",
                is_active=True,
            ),
        ),
    ]

    print("Campus Innovation & Engagement Intelligence Hub — filtered query load test")
    print(
        f"rows: users={user_count} profiles={profile_count} startups={startup_count} "
        f"| iterations={ITERATIONS} | target_scale=20,000+ profiles"
    )
    print("")
    print(f"{'query':<28} {'total_ms':>10} {'avg_ms':>10} {'rows_last':>12}")
    print("-" * 64)
    for label, elapsed_ms, avg_ms, count in workloads:
        print(f"{label:<28} {elapsed_ms:>10.2f} {avg_ms:>10.2f} {count:>12}")
    print(f"\nqueries_logged_last_run={len(connection.queries)}")


if __name__ == "__main__":
    main()
