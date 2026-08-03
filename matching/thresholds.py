# matching/thresholds.py
from typing import List, Dict, Any

def apply_similarity_threshold(
    results: List[Dict[str, Any]], 
    min_score: float = 40.0, 
    duplicate_epsilon: float = 0.5
) -> List[Dict[str, Any]]:
    """
    Prunes results based on a floor threshold and removes near-duplicates 
    (results with nearly identical scores) to ensure diversity in top-N.
    """
    # 1. Filter by floor (Low signal)
    filtered = [r for r in results if r['similarity_score'] >= min_score]
    
    if not filtered:
        return []

    # 2. Prune near-duplicates (Crowding prevention)
    unique_results = []
    last_score = -1.0
    
    for res in filtered:
        current_score = res['similarity_score']
        # If score is too close to the previous one, skip (assuming sorted input)
        if abs(current_score - last_score) > duplicate_epsilon:
            unique_results.append(res)
            last_score = current_score
            
    return unique_results

def calibrate_threshold(results: List[Dict[str, Any]], target_distinct: int = 5) -> float:
    """
    Heuristic to suggest a threshold that would have resulted in 
    exactly target_distinct results.
    """
    if len(results) <= target_distinct:
        return 0.0
    return results[target_distinct - 1]['similarity_score']