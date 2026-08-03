# apps/ecosystem/management/commands/load_synthetic_data.py

import csv
import json
import uuid
from datetime import date, datetime
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from accounts.models import Profile, User
from ecosystem.models import Achievement, Competition, Interaction, Investor, Startup

def _bool(val: str) -> bool:
    return val.strip().lower() in ("true", "1", "yes")

def _uuid(val: str) -> uuid.UUID | None:
    if not val or val == "": return None
    try: return uuid.UUID(val)
    except: return None

class Command(BaseCommand):
    help = "Bulk-import synthetic dataset with ID mapping."

    def add_arguments(self, parser):
        parser.add_argument("--base-dir", default="data/final")
        parser.add_argument("--chunk-size", type=int, default=1000)
        parser.add_argument("--flush-existing", action="store_true")

    def handle(self, *args, **options):
        base = Path(options["base_dir"])
        chunk = options["chunk_size"]
        
        if options["flush_existing"]:
            Achievement.objects.all().delete()
            Interaction.objects.all().delete()
            Investor.objects.all().delete()
            Startup.objects.all().delete()
            Competition.objects.all().delete()
            Profile.objects.all().delete()
            User.objects.all().delete()
            self.stdout.write("Database flushed.")

        # 1. Load Users
        user_rows = self._load_csv(base / "users.csv")
        users = []
        for r in user_rows:
            users.append(User(id=_uuid(r["user_id"]), email=r["email"], role=r["role"], full_name=r.get("full_name", "")))
        User.objects.bulk_create(users)
        self.stdout.write(f"Loaded {len(users)} users.")

        # 2. Load Profiles & Create User->Profile Map
        profile_rows = self._load_csv(base / "profiles.csv")
        profiles = []
        user_to_profile = {} # CRUCIAL MAP
        for r in profile_rows:
            p_id = _uuid(r.get("id")) or uuid.uuid4()
            u_id = _uuid(r.get("user_id"))
            user_to_profile[str(u_id)] = p_id
            profiles.append(Profile(id=p_id, user_id=u_id, department=r.get("department", "")))
        Profile.objects.bulk_create(profiles)
        self.stdout.write(f"Loaded {len(profiles)} profiles.")

        # 3. Load Competitions
        comp_rows = self._load_csv(base / "competitions.csv")
        comps = [Competition(id=_uuid(r["id"]), name=r["name"]) for r in comp_rows]
        Competition.objects.bulk_create(comps)

        # 4. Load Startups
        startup_rows = self._load_csv(base / "startups.csv")
        startups = []
        for r in startup_rows:
            startups.append(Startup(id=_uuid(r["id"]), startup_name=r["name"], founder_id=r["founder_id"]))
        Startup.objects.bulk_create(startups)
        startup_ids = {str(s.id) for s in startups}

        # 5. Load Interactions (With ID Translation)
        interaction_rows = self._load_csv(base / "interactions.csv")
        interactions = []
        for r in interaction_rows:
            # Translate User ID from CSV to Profile ID for Database
            raw_actor = r.get("actor_id")
            raw_target = r.get("target_id")
            
            actor_profile_id = user_to_profile.get(raw_actor)
            target_profile_id = user_to_profile.get(raw_target)

            if not actor_profile_id or not target_profile_id:
                continue # Skip if mapping fails

            interactions.append(Interaction(
                id=uuid.uuid4(),
                actor_id=actor_profile_id,
                target_id=target_profile_id,
                type=r.get("edge_type", "mentorship"),
                outcome="accepted"
            ))
        
        with transaction.atomic():
            Interaction.objects.bulk_create(interactions)
        self.stdout.write(f"Loaded {len(interactions)} interactions.")

    def _load_csv(self, path):
        with open(path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))