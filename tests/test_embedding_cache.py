# tests/test_embedding_cache.py
import pytest
from django.core.cache import cache
from matching.embeddings import encode, DIMENSIONS
from matching.embedding_cache import make_cache_key

@pytest.mark.django_db
class TestEmbeddingCache:
    def setup_method(self):
        cache.clear()

    def test_cache_hit_returns_same_data(self):
        text = "L'Essor Innovation Hub"
        # First call: computes
        vec1 = encode(text, namespace="startup")
        
        # Manually corrupt cache to verify we are reading from it
        key = make_cache_key("startup", text)
        corrupted_vec = [1.0] * DIMENSIONS
        cache.set(key, corrupted_vec)
        
        # Second call: should hit cache and get corrupted vec
        vec2 = encode(text, namespace="startup")
        assert vec2 == corrupted_vec
        assert vec2 != vec1

    def test_cache_miss_on_text_change(self):
        text1 = "Pitch version 1"
        text2 = "Pitch version 2"
        vec1 = encode(text1)
        vec2 = encode(text2)
        assert vec1 != vec2

    def test_normalization_in_cache_key(self):
        text_clean = "blockchain fintech"
        text_messy = "  BLOCKCHAIN   fintech \n"
        
        vec1 = encode(text_clean)
        # Manually set cache
        key = make_cache_key("default", text_clean)
        marker_vec = [0.5] * DIMENSIONS
        cache.set(key, marker_vec)
        
        # Messy text should resolve to the same key
        vec2 = encode(text_messy)
        assert vec2 == marker_vec

    def test_empty_input_bypasses_cache(self):
        # Empty inputs return zero vectors and shouldn't bloat the cache
        text = "   "
        vec = encode(text)
        assert sum(vec) == 0.0
        
        # Verify no cache entry was created for this input
        key = make_cache_key("default", text)
        assert cache.get(key) is None

    def test_namespace_isolation(self):
        text = "Consistent Text"
        # Same text, different namespaces should have different keys
        key1 = make_cache_key("startup", text)
        key2 = make_cache_key("investor", text)
        assert key1 != key2