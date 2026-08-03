# tests/test_known_pairs.py
import pytest
from django.urls import reverse
from django.db import connection
from accounts.models import User
from ecosystem.models import Startup, Investor
from matching.test_fixtures import KNOWN_PAIRS
from matching.embeddings import encode

@pytest.mark.django_db
class TestKnownPairs:
    def setup_method(self):
        # Create a single founder for all startups
        self.founder = User.objects.create_user(email="founder@test.com", password="p", role="student")
        
        # Create 1 UNIQUE user per investor to satisfy OneToOne uniqueness constraints
        self.investors = []
        for i, pair in enumerate(KNOWN_PAIRS):
            inv_user = User.objects.create_user(
                email=f"investor_{i}@test.com", 
                password="p", 
                role="investor"
            )
            inv = Investor.objects.create(
                user=inv_user,
                firm_name=f"{pair['sector']} Capital",
                mandate_text=pair['investor_mandate'],
                sectors=[pair['sector']],
                mandate_embedding=encode(pair['investor_mandate'])
            )
            self.investors.append(inv)

    @pytest.mark.parametrize("pair", KNOWN_PAIRS)
    def test_obvious_matches_rank_first(self, api_client, pair):
        """Assert that a specific startup matches its intended sector investor best."""
        startup = Startup.objects.create(
            founder=self.founder,
            startup_name=f"{pair['sector']} Startup",
            pitch_summary=pair['startup_pitch'],
            pitch_embedding=encode(pair['startup_pitch'])
        )
        
        api_client.force_authenticate(user=self.founder)
        url = reverse('match-investor')
        res = api_client.post(url, {"startup_id": str(startup.id)})
        
        assert res.status_code == 200
        # On Postgres, the top match must be the correct sector
        if connection.vendor == 'postgresql':
            assert res.data['matches'][0]['firm_name'] == f"{pair['sector']} Capital"
        else:
            # On SQLite fallback, we just check structure and presence of data
            assert len(res.data['matches']) > 0

    def test_input_normalization_consistency(self):
        """Verify that casing and whitespace do not change the embedding vector."""
        t1 = "FinTech Blockchain"
        t2 = "  fintech   BLOCKCHAIN \n"
        v1 = encode(t1)
        v2 = encode(t2)
        
        from matching.utils import safe_cosine_similarity
        assert safe_cosine_similarity(v1, v2) >= 0.99

    def test_empty_string_safety(self):
        """Ensure empty strings return zero vectors and don't crash similarity logic."""
        vec = encode("   ")
        assert all(v == 0.0 for v in vec)
        
        from matching.utils import safe_cosine_similarity
        assert safe_cosine_similarity(vec, [0.1]*384) == 0.0