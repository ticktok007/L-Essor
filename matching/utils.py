# matching/utils.py
import re
from typing import List

def normalize_text(text: str) -> str:
    """Cleans text for consistent cache keys and embeddings."""
    if not text:
        return ""
    # Lowercase, trim, and collapse all whitespace to single spaces
    t = text.lower().strip()
    return re.sub(r'\s+', ' ', t)

def zero_vector(dim: int = 384) -> List[float]:
    """Returns a zero-initialized vector."""
    return [0.0] * dim

def is_same_text(text1: str, text2: str) -> bool:
    """Checks if two strings are semantically identical after normalization."""
    return normalize_text(text1) == normalize_text(text2)