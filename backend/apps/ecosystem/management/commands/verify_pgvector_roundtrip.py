"""
Verify pgvector round-trip — Campus Innovation & Engagement Intelligence Hub
Usage: python manage.py verify_pgvector_roundtrip
Requires: ecosystem_startup table (migrate after copying startup_vector_model.py).
"""
from django.core.management.base import BaseCommand
from pgvector.django import CosineDistance


class Command(BaseCommand):
    help = "Insert a Startup test vector and query nearest neighbour via cosine distance."

    def handle(self, *args, **options):
        from ecosystem.models import Startup

        test_vector = [0.01 * (i + 1) for i in range(384)]

        startup, created = Startup.objects.update_or_create(
            name="pgvector-roundtrip-test",
            defaults={
                "pitch_summary": "Campus Innovation & Engagement Intelligence Hub test pitch.",
                "pitch_embedding": test_vector,
            },
        )

        nearest = (
            Startup.objects.annotate(
                distance=CosineDistance("pitch_embedding", test_vector)
            )
            .order_by("distance")
            .first()
        )

        if nearest and nearest.pk == startup.pk:
            self.stdout.write(
                self.style.SUCCESS(
                    f"pgvector round-trip OK — nearest match: {nearest.name} "
                    f"(pk={nearest.pk}, created={created})"
                )
            )
        else:
            self.stderr.write(
                self.style.ERROR("pgvector round-trip FAILED — nearest row mismatch.")
            )
