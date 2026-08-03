# matching/peer_clustering.py
import collections
from typing import List, Dict, Any, Optional
from sklearn.cluster import KMeans
from .peer_features import build_feature_matrix

def generate_peer_teams(students: List[Dict[str, Any]], team_size: int = 4, n_clusters: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Groups students into clusters using K-Means.
    If n_clusters is not provided, it is derived from total students / team_size.
    """
    if not students:
        return []
    
    count = len(students)
    k = n_clusters if n_clusters else max(1, count // team_size)
    
    matrix = build_feature_matrix(students)
    kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto')
    labels = kmeans.fit_predict(matrix)
    
    clusters = collections.defaultdict(list)
    for idx, label in enumerate(labels):
        clusters[int(label)].append(students[idx])
    
    teams = []
    for label, members in clusters.items():
        # Identify shared and complementary skills for metadata
        all_pos = [m.get('skills_possessed', '').split('|') for m in members]
        flat_pos = [item.strip() for sublist in all_pos for item in sublist if item.strip()]
        
        # Shared: Skills appearing in more than 50% of members
        shared = [s for s, c in collections.Counter(flat_pos).items() if c > (len(members) / 2)]
        
        # Balance Score: Heuristic based on diversity of 'skills_possessed'
        balance_score = min(100, len(set(flat_pos)) * 10) 
        
        teams.append({
            "team_id": label,
            "member_ids": [m.get('id') for m in members],
            "member_names": [m.get('full_name') for m in members],
            "top_shared_skills": shared[:3],
            "balance_score": float(balance_score),
            "size": len(members)
        })
        
    return teams