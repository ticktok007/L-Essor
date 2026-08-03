# management/commands/check_orphan_records.py
from django.core.management.base import BaseCommand
from accounts.models import Profile, User
from ecosystem.models import Startup, Achievement, Interaction, Investor, Mentor

class Command(BaseCommand):
    help = "Checks for orphan records across key entities."

    def handle(self, *args, **options):
        orphans = {
            "Profiles without User": Profile.objects.filter(user__isnull=True).count(),
            "Startups without Founder": Startup.objects.filter(founder__isnull=True).count(),
            "Achievements without Profile": Achievement.objects.filter(profile__isnull=True).count(),
            "Interactions (Bad Actor)": Interaction.objects.filter(actor__isnull=True).count(),
            "Interactions (Bad Target)": Interaction.objects.filter(target__isnull=True).count(),
            "Investors without User": Investor.objects.filter(user__isnull=True).count(),
            "Mentors without User": Mentor.objects.filter(user__isnull=True).count(),
        }

        has_issues = False
        self.stdout.write(self.style.MIGRATE_HEADING("--- Orphan Record Report ---"))
        for label, count in orphans.items():
            if count > 0:
                self.stdout.write(self.style.ERROR(f"{label}: {count}"))
                has_issues = True
            else:
                self.stdout.write(f"{label}: 0")

        if has_issues:
            exit(1)
        self.stdout.write(self.style.SUCCESS("No orphan records found."))