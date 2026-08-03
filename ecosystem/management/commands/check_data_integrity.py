# management/commands/check_data_integrity.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Count
from accounts.models import Profile, User
from ecosystem.models import Startup, Achievement, Interaction

class Command(BaseCommand):
    help = "Performs logical data integrity checks."

    def handle(self, *args, **options):
        now = timezone.now()
        issues = []

        # Duplicate emails
        dupes = User.objects.values('email').annotate(c=Count('id')).filter(c__gt=1)
        if dupes.exists(): issues.append(f"Duplicate emails found: {dupes.count()}")

        # TRL/MRL bounds
        bad_trl = Startup.objects.filter(trl__lt=1) | Startup.objects.filter(trl__gt=9)
        if bad_trl.exists(): issues.append(f"Startups with invalid TRL: {bad_trl.count()}")

        # Future achievements
        future_ach = Achievement.objects.filter(date__gt=now.date())
        if future_ach.exists(): issues.append(f"Achievements with future dates: {future_ach.count()}")

        # Score bounds
        bad_scores = Profile.objects.filter(achievement_impact_score__lt=0) | Profile.objects.filter(grit_index__lt=0)
        if bad_scores.exists(): issues.append(f"Profiles with negative scores: {bad_scores.count()}")

        self.stdout.write(self.style.MIGRATE_HEADING("--- Data Integrity Report ---"))
        if not issues:
            self.stdout.write(self.style.SUCCESS("All integrity checks passed."))
            exit(0)
        
        for issue in issues:
            self.stdout.write(self.style.ERROR(f"ISSUE: {issue}"))
        exit(1)