# matching/embeddings.py
import logging
import threading
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from .embedding_cache import get_or_compute_embedding
from .utils import normalize_text, zero_vector

logger = logging.getLogger(__name__)

MODEL_NAME = "all-MiniLM-L12-v2"
DIMENSIONS = 384
MAX_SEQ_LENGTH = 512

_model_instance: Optional[SentenceTransformer] = None
_model_lock = threading.Lock()

def get_model() -> SentenceTransformer:
    global _model_instance
    if _model_instance is None:
        with _model_lock:
            if _model_instance is None:
                _model_instance = SentenceTransformer(MODEL_NAME)
                _model_instance.max_seq_length = MAX_SEQ_LENGTH
    return _model_instance

def _raw_encode(text: str) -> List[float]:
    """Internal function to perform the actual ML inference."""
    if not text or not text.strip():
        return zero_vector(DIMENSIONS)
    
    # Truncation logic (approx 4 chars per token)
    safe_text = text[:MAX_SEQ_LENGTH * 4]
    model = get_model()
    embedding = model.encode(safe_text, normalize_embeddings=True)
    return embedding.tolist()

def encode(text: Optional[str], namespace: str = "default", use_cache: bool = True) -> List[float]:
    """
    Encodes text into a 384-dim vector with integrated caching.
    """
    if not text or not text.strip():
        return zero_vector(DIMENSIONS)

    if not use_cache:
        return _raw_encode(text)

    return get_or_compute_embedding(text, _raw_encode, namespace=namespace)

def encode_batch(texts: List[str], namespace: str = "default") -> List[List[float]]:
    """Encodes multiple strings using the cache for each."""
    return [encode(t, namespace=namespace) for t in texts]