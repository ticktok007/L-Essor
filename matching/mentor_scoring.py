# matching/mentor_scoring.py
from typing import List, Dict, Any
from accounts.models import Profile
from ecosystem.models import Mentor
from .mentor_features import overlap_score, matched_terms
from .utils import safe_cosine_similarity

def score_mentor_match(mentor: Mentor, mentee_profile: Profile, alpha: float = 0.6) -> Dict[str, Any]:
    """
    Blends content-based overlap and embedding similarity into a final score.
    Score = alpha * content_score + (1 - alpha) * embedding_score
    """
    # 1. Content Score (Interests overlap)
    # Assume Mentor profile also has interests, or use Mentor.expertise_areas
    mentor_profile = mentor.user.profile
    mentor_terms = mentor.expertise_areas + mentor_profile.interests
    
    c_score = overlap_score(mentee_profile.interests, mentor_terms)
    
    # 2. Embedding Score (Cosine Similarity)
    # Fallback to 0.0 if embeddings are missing
    e_score = 0.0
    if mentee_profile.skills_embedding and mentor_profile.skills_embedding:
        e_score = safe_cosine_similarity(
            mentee_profile.skills_embedding, 
            mentor_profile.skills_embedding
        )
    
    # 3. Blending
    final_score = (alpha * c_score) + ((1 - alpha) * e_score)
    
    return {
        "mentor_id": mentor.id,
        "name": mentor.user.full_name,
        "content_score": round(c_score * 100, 2),
        "embedding_score": round(e_score * 100, 2),
        "final_match_score": round(final_score * 100, 2),
        "matched_terms": matched_terms(mentee_profile.interests, mentor_terms)
    }

def rank_mentors_for_mentee(mentee_profile: Profile, mentors: List[Mentor], alpha: float = 0.6) -> List[Dict[str, Any]]:
    """Scores and ranks a list of mentors for a specific mentee."""
    results = [score_mentor_match(m, mentee_profile, alpha) for m in mentors]
    return sorted(results, key=lambda x: x["final_match_score"], reverse=True)