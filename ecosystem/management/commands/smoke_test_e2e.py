# ecosystem/management/commands/smoke_test_e2e.py
import uuid
from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import User, Profile
from ecosystem.models import Startup, Interaction, InteractionType, InteractionOutcome

class Command(BaseCommand):
    help = "Performs a resilient end-to-end smoke test of the backend foundation."

    def handle(self, *args, **options):
        self.stdout.write("Starting Resilient E2E Smoke Test...")
        try:
            with transaction.atomic():
                # 1. Create Actor User & Profile
                actor_email = f"actor-{uuid.uuid4().hex[:8]}@test.com"
                actor_user = User.objects.create_user(
                    email=actor_email, password="password", full_name="Actor Student", role="student"
                )
                # Ensure profile exists
                actor_profile, _ = Profile.objects.get_or_create(user=actor_user)
                self.stdout.write(self.style.SUCCESS(f"[PASS] Created Actor: {actor_user.email}"))

                # 2. Create Startup linked to Profile
                startup = Startup.objects.create(
                    founder=actor_user, 
                    startup_name="E2E Innovation Lab", 
                    sector="DeepTech"
                )
                self.stdout.write(self.style.SUCCESS(f"[PASS] Created Startup: {startup.startup_name}"))

                # 3. Create Target User & Profile
                target_email = f"target-{uuid.uuid4().hex[:8]}@test.com"
                target_user = User.objects.create_user(
                    email=target_email, password="password", full_name="Target Mentor", role="mentor"
                )
                target_profile, _ = Profile.objects.get_or_create(user=target_user)
                self.stdout.write(self.style.SUCCESS(f"[PASS] Created Target: {target_user.email}"))

                # 4. Create Interaction
                interaction = Interaction.objects.create(
                    actor=actor_profile, 
                    target=target_profile, 
                    type=InteractionType.MENTORSHIP, 
                    outcome=InteractionOutcome.ACCEPTED,
                    startup=startup
                )
                self.stdout.write(self.style.SUCCESS(f"[PASS] Created Interaction: {interaction.id}"))

                # 5. Role Scoping & Integrity Check
                # Fetch back and verify relationships
                fetched_startup = Startup.objects.get(id=startup.id)
                assert fetched_startup.founder == actor_user
                
                fetched_interaction = Interaction.objects.get(id=interaction.id)
                assert fetched_interaction.actor == actor_profile
                assert fetched_interaction.target == target_profile

                self.stdout.write(self.style.SUCCESS("[PASS] Data Integrity: Relationships verified"))

                # 6. Cleanup (Automatic via transaction rollback is safer for smoke tests, 
                # but we will delete manually to confirm delete logic)
                interaction.delete()
                startup.delete()
                actor_user.delete()
                target_user.delete()
                self.stdout.write(self.style.SUCCESS("[PASS] Cleanup complete"))

            self.stdout.write(self.style.SUCCESS("\nALL E2E SMOKE TESTS PASSED (v1.0 Frozen)"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\nSMOKE TEST FAILED: {str(e)}"))
            import traceback
            self.stdout.write(traceback.format_exc())
            exit(1)