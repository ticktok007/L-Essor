# matching/embedding_cache.py
import hashlib
from typing import List, Optional, Callable
from django.core.cache import cache
from .utils import normalize_text

MODEL_VERSION = "all-MiniLM-L12-v2"
CACHE_TTL = 60 * 60 * 24  # 1 hour default (Redis typically handles longer)

def make_cache_key(namespace: str, text: str) -> str:
    """Generates a unique cache key based on normalized text and model version."""
    clean_text = normalize_text(text)
    text_hash = hashlib.sha256(clean_text.encode()).hexdigest()
    return f"embed:{namespace}:{MODEL_VERSION}:{text_hash}"

def get_or_compute_embedding(
    text: str, 
    compute_fn: Callable[[str], List[float]], 
    namespace: str = "default"
) -> List[float]:
    """Retrieves from cache or computes and stores a new embedding."""
    if not text or not text.strip():
        return compute_fn(text)

    key = make_cache_key(namespace, text)
    cached_vec = cache.get(key)
    
    if cached_vec is not None:
        return cached_vec
    
    vector = compute_fn(text)
    cache.set(key, vector, timeout=CACHE_TTL)
    return vector

def invalidate_embedding(namespace: str, text: str):
    """Explicitly removes a text embedding from cache."""
    key = make_cache_key(namespace, text)
    cache.delete(key)