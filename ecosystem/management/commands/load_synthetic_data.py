# ecosystem/management/commands/load_synthetic_data.py
import csv
import json
import uuid
import re
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from accounts.models import Profile, User
from ecosystem.models import Achievement, Competition, Interaction, Investor, Startup

class Command(BaseCommand):
    help = "Ingests Hub data with ID normalization to ensure FK integrity."

    def add_arguments(self, parser):
        parser.add_argument("--base-dir", default="data")
        parser.add_argument("--flush-existing", action="store_true")

    def _normalize_id(self, val):
        """Standardizes IDs (e.g., 'STU-001' -> 'STU00001') for consistent hashing."""
        if not val or val == "": return None
        val = str(val).replace("-", "").upper()
        match = re.match(r"([A-Z]+)([0-9]+)", val)
        if match:
            prefix, num = match.groups()
            # Consolidate common aliases
            if prefix == "ALU": prefix = "ALM" 
            return f"{prefix}{int(num):05d}"
        return val

    def _to_uuid(self, val):
        normalized = self._normalize_id(val)
        if not normalized: return None
        return uuid.uuid5(uuid.NAMESPACE_DNS, normalized)

    def handle(self, *args, **options):
        data_root = Path(options["base_dir"])
        final_dir = data_root / "final"
        synth_dir = data_root / "synthetic"
        
        if options["flush_existing"]:
            self.stdout.write("Flushing database...")
            Achievement.objects.all().delete()
            Interaction.objects.all().delete()
            Investor.objects.all().delete()
            Startup.objects.all().delete()
            Competition.objects.all().delete()
            Profile.objects.all().delete()
            User.objects.all().delete()

        # 1. Load Users
        user_rows = self._load_csv(final_dir / "users.csv")
        user_uuids = set()
        users_to_create = []
        for r in user_rows:
            u_uuid = self._to_uuid(r["user_id"])
            if u_uuid in user_uuids: continue
            users_to_create.append(User(
                id=u_uuid, email=r["email"], role=r["role"], 
                full_name=r.get("full_name", ""), is_active=True
            ))
            user_uuids.add(u_uuid)
        User.objects.bulk_create(users_to_create)
        self.stdout.write(f"✓ Loaded {len(users_to_create)} users")

        # 2. Load Profiles
        profile_uuids = set()
        profiles_to_create = []
        for filename in ["student_profiles.csv", "alumni_profiles.csv"]:
            rows = self._load_csv(synth_dir / filename)
            id_key = "student_id" if "student" in filename else "alumni_id"
            for r in rows:
                u_uuid = self._to_uuid(r[id_key])
                p_uuid = uuid.uuid5(u_uuid, "profile")
                if p_uuid in profile_uuids: continue
                profiles_to_create.append(Profile(
                    id=p_uuid, user_id=u_uuid, department=r.get("department", ""),
                    graduation_year=int(r["graduation_year"]) if r.get("graduation_year") else None,
                    skills=json.loads(r["skills"]) if r.get("skills") and r["skills"].startswith('[') else []
                ))
                profile_uuids.add(p_uuid)
        Profile.objects.bulk_create(profiles_to_create)
        self.stdout.write(f"✓ Loaded {len(profiles_to_create)} profiles")

        # 3. Map Startups to Founders
        startup_founder_map = {}
        linker_rows = self._load_csv(synth_dir / "startup_founder_links.csv")
        for lr in linker_rows:
            if lr["is_primary_contact"] == "yes":
                startup_founder_map[lr["startup_id"]] = self._to_uuid(lr["founder_profile_id"])

        # 4. Load Startups (Filtering for existing users)
        startup_rows = self._load_csv(final_dir / "startups.csv")
        startups_to_create = []
        for r in startup_rows:
            f_id = startup_founder_map.get(r["startup_id"])
            # Only add if founder exists in User table
            if f_id and f_id in user_uuids:
                startups_to_create.append(Startup(
                    id=self._to_uuid(r["startup_id"]), startup_name=r["name"],
                    founder_id=f_id, sector=r.get("sector", ""),
                    stage=r.get("funding_stage", "idea"), 
                    trl=int(r["trl_level"]) if r.get("trl_level") else None
                ))
        Startup.objects.bulk_create(startups_to_create)
        self.stdout.write(f"✓ Loaded {len(startups_to_create)} startups")

        # 5. Load Competitions
        comp_rows = self._load_csv(final_dir / "competitions.csv")
        comps = [Competition(id=self._to_uuid(r["competition_id"]), name=r["name"]) for r in comp_rows]
        Competition.objects.bulk_create(comps)
        self.stdout.write(f"✓ Loaded {len(comps)} competitions")

        # 6. Load Interactions (Profile-to-Profile)
        interaction_rows = self._load_csv(final_dir / "interactions.csv")
        interactions = []
        for r in interaction_rows:
            actor_p = uuid.uuid5(self._to_uuid(r["source_profile_id"]), "profile")
            target_p = uuid.uuid5(self._to_uuid(r["target_profile_id"]), "profile")
            if actor_p in profile_uuids and target_p in profile_uuids:
                interactions.append(Interaction(
                    id=self._to_uuid(r["edge_id"]), actor_id=actor_p, target_id=target_p,
                    type=r["edge_type"], outcome=r.get("outcome", "accepted")
                ))
        Interaction.objects.bulk_create(interactions)
        self.stdout.write(f"✓ Loaded {len(interactions)} interactions")

    def _load_csv(self, path):
        if not path.exists():
            raise CommandError(f"File not found: {path}")
        with open(path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))