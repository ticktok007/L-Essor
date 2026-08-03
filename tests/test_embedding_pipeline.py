# tests/test_embedding_pipeline.py
import pytest
from django.core.management import call_command
from accounts.models import User
from ecosystem.models import Startup, Investor
from matching.embeddings import encode

@pytest.mark.django_db
class TestEmbeddingPipeline:
    def setup_method(self):
        # Create user to satisfy NOT NULL founder/user constraints
        self.user = User.objects.create_user(
            email="founder@test.com", 
            password="password123", 
            role="student"
        )
        self.startup = Startup.objects.create(
            founder=self.user,
            startup_name="Test AI", 
            pitch_summary="Automating campus infrastructure with computer vision."
        )
        self.investor = Investor.objects.create(
            user=self.user,
            firm_name="Alumni Fund",
            mandate_text="Investing in deep-tech startups within the university ecosystem."
        )

    def test_pipeline_populates_vectors(self):
        assert self.startup.pitch_embedding is None
        call_command('embed_pitch_and_mandate', chunk_size=10)
        
        self.startup.refresh_from_db()
        self.investor.refresh_from_db()
        
        assert self.startup.pitch_embedding is not None
        assert len(self.startup.pitch_embedding) == 384
        assert self.investor.mandate_embedding is not None
        assert len(self.investor.mandate_embedding) == 384

    def test_vector_integrity_roundtrip(self):
        call_command('embed_pitch_and_mandate')
        self.startup.refresh_from_db()
        
        stored = self.startup.pitch_embedding
        fresh = encode(self.startup.pitch_summary)
        
        similarity = sum(s * f for s, f in zip(stored, fresh))
        assert similarity >= 0.99

    def test_pipeline_idempotency(self):
        call_command('embed_pitch_and_mandate')
        self.startup.refresh_from_db()
        first_vector = list(self.startup.pitch_embedding)
        
        call_command('embed_pitch_and_mandate')
        self.startup.refresh_from_db()
        second_vector = list(self.startup.pitch_embedding)
        
        assert first_vector == second_vector

    def test_handle_empty_fields(self):
        Startup.objects.create(founder=self.user, startup_name="Empty", pitch_summary="")
        call_command('embed_pitch_and_mandate')
        empty_startup = Startup.objects.get(startup_name="Empty")
        assert sum(empty_startup.pitch_embedding) == 0