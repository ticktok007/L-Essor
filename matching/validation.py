# matching/validation.py
from .embeddings import encode
from .utils import safe_cosine_similarity

def validate_match_logic(startup_text, expected_investor_text, unrelated_texts):
    """
    Validates that a specific startup text ranks higher against its intended 
    investor mandate than against a list of unrelated noise texts.
    """
    s_vec = encode(startup_text)
    target_vec = encode(expected_investor_text)
    target_score = safe_cosine_similarity(s_vec, target_vec)
    
    better_than_noise = True
    failures = []
    
    for noise in unrelated_texts:
        n_vec = encode(noise)
        n_score = safe_cosine_similarity(s_vec, n_vec)
        if n_score >= target_score:
            better_than_noise = False
            failures.append(noise)
            
    return better_than_noise, target_score, failures