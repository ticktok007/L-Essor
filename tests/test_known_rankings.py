# tests/test_known_rankings.py
import pytest
from django.urls import reverse
from django.db import connection
from accounts.models import User
from matching.test_pairs import GOOD_PAIRS, BAD_PAIRS
from matching.test_data import create_test_investor, create_test_startup
from matching.ranking_checks import assert_in_top_k, assert_not_in_top_k, assert_sorted_desc

@pytest.mark.django_db
class TestKnownRankings:
    def setup_method(self):
        self.user = User.objects.create_user(email="test@hub.com", password="p", role="student")
        self.investor_map = {}
        
        # 1. Populate DB with 4 target investors
        for pair in GOOD_PAIRS:
            inv = create_test_investor(f"{pair['sector']} Fund", pair['investor_mandate'], [pair['sector']])
            self.investor_map[pair['sector']] = inv

    @pytest.mark.parametrize("pair", GOOD_PAIRS)
    def test_positive_match_ranking(self, api_client, pair):
        startup = create_test_startup(self.user, "Target Startup", pair['startup_pitch'], pair['sector'])
        target_investor = self.investor_map[pair['sector']]
        
        api_client.force_authenticate(user=self.user)
        url = reverse('recommend-investor')
        res = api_client.get(f"{url}?startup_id={startup.id}")
        
        assert res.status_code == 200
        assert_in_top_k(res.data, target_investor.id, k=5)
        assert_sorted_desc(res.data)

    def test_negative_match_exclusion(self, api_client):
        """Clearly unrelated pairs must not appear in the top 5 when pool > 5."""
        # 2. Add a 'Noise' investor to push total count to 6
        create_test_investor("Generic Noise", "We invest in high-growth retail and generic consumer goods.", ["Retail"])
        
        # 3. Create the unrelated investor we want to exclude
        noise_inv = create_test_investor("BioTech Only", BAD_PAIRS[1]['investor_mandate'], ["BioTech"])
        
        # 4. Create a Fintech startup
        startup = create_test_startup(self.user, "Fintech App", GOOD_PAIRS[1]['startup_pitch'], "FinTech")
        
        api_client.force_authenticate(user=self.user)
        url = reverse('recommend-investor')
        res = api_client.get(f"{url}?startup_id={startup.id}")
        
        # Now there are 6 investors. The BioTech one should be at Rank 6.
        assert_not_in_top_k(res.data, noise_inv.id, k=5)

    def test_deterministic_ranking(self, api_client):
        pair = GOOD_PAIRS[0]
        startup = create_test_startup(self.user, "Static Startup", pair['startup_pitch'], pair['sector'])
        api_client.force_authenticate(user=self.user)
        url = reverse('recommend-investor')
        res1 = api_client.get(f"{url}?startup_id={startup.id}").data
        res2 = api_client.get(f"{url}?startup_id={startup.id}").data
        assert [r['id'] for r in res1] == [r['id'] for r in res2]

    def test_zero_vector_failure_handling(self, api_client):
        startup = create_test_startup(self.user, "Empty Startup", "", "None")
        startup.pitch_embedding = [0.0] * 384
        startup.save()
        api_client.force_authenticate(user=self.user)
        url = reverse('recommend-investor')
        res = api_client.get(f"{url}?startup_id={startup.id}")
        assert res.status_code in [400, 200]
        if res.status_code == 200:
            for match in res.data:
                assert match['similarity_score'] == 0.0