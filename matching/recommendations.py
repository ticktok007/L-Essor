# matching/recommendations.py
from django.db import connection
from pgvector.django import CosineDistance
from ecosystem.models import Investor, Mentor, Startup
from .utils import safe_cosine_similarity

def get_knn_recommendations(model, query_vector, vector_field, top_k=5):
    """
    Retrieves top-K nearest neighbors.
    Uses native pgvector for Postgres, and a Python fallback for SQLite/Tests.
    """
    if connection.vendor == 'postgresql':
        queryset = model.objects.annotate(
            distance=CosineDistance(vector_field, query_vector)
        ).order_by('distance')[:top_k]
    else:
        # ── Python Fallback for SQLite/CI ──
        all_objs = list(model.objects.all())
        for obj in all_objs:
            target_vec = getattr(obj, vector_field)
            # Distance = 1 - Similarity
            sim = safe_cosine_similarity(query_vector, target_vec)
            obj.distance = 1.0 - sim
        
        # Sort by distance and slice
        queryset = sorted(all_objs, key=lambda x: getattr(x, 'distance', 1.0))[:top_k]

    results = []
    for obj in queryset:
        dist = float(getattr(obj, 'distance', 1.0))
        # Ensure score is strictly 0.0 if distance is 1.0 (no match)
        score = round((1.0 - max(0.0, min(1.0, dist))) * 100, 2)
        
        name = getattr(obj, 'firm_name', getattr(obj, 'user', None))
        if hasattr(name, 'full_name'): name = name.full_name
        
        snippet = getattr(obj, 'mandate_text', getattr(obj, 'bio', ''))
        
        results.append({
            "id": obj.id,
            "name": str(name),
            "similarity_score": score,
            "snippet": (snippet[:100] + '...') if len(snippet) > 100 else snippet
        })
    
    return sorted(results, key=lambda x: x['similarity_score'], reverse=True)