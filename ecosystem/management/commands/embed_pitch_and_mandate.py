# ecosystem/management/commands/embed_pitch_and_mandate.py
import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from ecosystem.models import Startup, Investor
from matching.embeddings import encode_batch, encode

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Batch embeds Startup pitches and Investor mandates using all-MiniLM-L12-v2."

    def add_arguments(self, parser):
        parser.add_argument('--chunk-size', type=int, default=100, help="Number of records to process per batch.")
        parser.add_argument('--verify-only', action='store_true', help="Skip embedding and only verify existing vectors.")

    def handle(self, *args, **options):
        chunk_size = options['chunk_size']
        verify_only = options['verify_only']

        if not verify_only:
            self.stdout.write("Starting batch embedding process...")
            self._process_embeddings(Startup, 'pitch_summary', 'pitch_embedding', chunk_size)
            self._process_embeddings(Investor, 'mandate_text', 'mandate_embedding', chunk_size)
        
        self.stdout.write("Starting verification...")
        s_pass = self._verify(Startup, 'pitch_summary', 'pitch_embedding')
        i_pass = self._verify(Investor, 'mandate_text', 'mandate_embedding')

        if s_pass and i_pass:
            self.stdout.write(self.style.SUCCESS("✔ Verification Passed: Stored vectors match fresh computations."))
        else:
            self.stdout.write(self.style.ERROR("✘ Verification Failed: Potential drift or corruption detected."))
            exit(1)

    def _process_embeddings(self, model, text_field, vector_field, chunk_size):
        queryset = model.objects.all()
        total = queryset.count()
        processed = 0

        for i in range(0, total, chunk_size):
            batch = queryset[i:i+chunk_size]
            texts = [getattr(obj, text_field) for obj in batch]
            vectors = encode_batch(texts)

            with transaction.atomic():
                for obj, vector in zip(batch, vectors):
                    setattr(obj, vector_field, vector)
                    obj.save(update_fields=[vector_field])
            
            processed += len(batch)
            self.stdout.write(f"  Processed {processed}/{total} {model.__name__} records")

    def _verify(self, model, text_field, vector_field):
        samples = model.objects.exclude(**{f"{vector_field}__isnull": True})[:50]
        if not samples:
            return True

        for obj in samples:
            stored_vector = getattr(obj, vector_field)
            fresh_vector = encode(getattr(obj, text_field))
            
            # Check if both are zero vectors (valid for empty text)
            is_zero_stored = all(v == 0 for v in stored_vector)
            is_zero_fresh = all(v == 0 for v in fresh_vector)
            
            if is_zero_stored and is_zero_fresh:
                continue
                
            # If one is zero and other isn't, or dot product is low
            similarity = sum(s * f for s, f in zip(stored_vector, fresh_vector))
            if similarity < 0.99:
                self.stdout.write(self.style.WARNING(f"    Low similarity ({similarity:.4f}) for {model.__name__} ID: {obj.id}"))
                return False
        return True