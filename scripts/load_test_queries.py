import os
import sys
import time
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "campushub.settings.dev")
django.setup()

from django.db import connection, reset_queries
from django.conf import settings
settings.DEBUG = True

from accounts.models import Profile, User
from ecosystem.models import Startup

def timer(label, fn):
    reset_queries()
    t0 = time.perf_counter()
    result = fn()
    elapsed = round((time.perf_counter() - t0) * 1000, 2)
    count = result.count() if hasattr(result, "count") else len(result)
    print(f"[{elapsed:>8} ms] {label:<45} rows={count}")

def explain(sql):
    db = connection.vendor  # 'sqlite' or 'postgresql'
    with connection.cursor() as cur:
        if db == "postgresql":
            cur.execute(f"EXPLAIN ANALYZE {sql}")
        else:
            cur.execute(f"EXPLAIN QUERY PLAN {sql}")
        for row in cur.fetchall():
            print(" ", row[0] if db == "postgresql" else row)

def run():
    total_users    = User.objects.count()
    total_profiles = Profile.objects.count()
    total_startups = Startup.objects.count()

    print(f"\nDB backend  : {connection.vendor}")
    print(f"Users       : {total_users}")
    print(f"Profiles    : {total_profiles}")
    print(f"Startups    : {total_startups}\n")

    if total_users == 0:
        print("WARNING: Database is empty.")
        print("Run this first:")
        print("  python manage.py load_synthetic_data --flush-existing")
        print("  python manage.py load_synthetic_data --base-dir data/final")
        return

    timer("Profile filter by department",
          lambda: Profile.objects.filter(department="Computer Science & Engineering"))
    timer("User filter by role=student",
          lambda: User.objects.filter(role="student"))
    timer("User filter by role=alumni",
          lambda: User.objects.filter(role="alumni"))
    timer("Startup filter by sector=HealthTech",
          lambda: Startup.objects.filter(sector="HealthTech"))
    timer("Startup filter by stage=seed",
          lambda: Startup.objects.filter(stage="seed"))
    timer("Profile filter dept + order graduation_year",
          lambda: Profile.objects.filter(
              department="Information Technology"
          ).order_by("graduation_year"))
    timer("Startup sector + stage combined",
          lambda: Startup.objects.filter(sector="EdTech", stage="mvp"))
    timer("User role=investor",
          lambda: User.objects.filter(role="investor"))
    timer("Profile full table scan baseline",
          lambda: Profile.objects.all())

    print("\n--- EXPLAIN: role filter ---")
    explain("SELECT * FROM auth_user WHERE role = 'student'")

    print("\n--- EXPLAIN: sector filter ---")
    explain("SELECT * FROM ecosystem_startup WHERE sector = 'HealthTech'")

if __name__ == "__main__":
    run()