# matching/peer_features.py
import numpy as np
from typing import List, Dict, Any
from .embeddings import encode

def normalize_skill(text: str) -> str:
    """Standardizes skill strings for better matching."""
    if not text:
        return ""
    return text.lower().strip().replace("-", " ")

def build_peer_feature_vector(student_data: Dict[str, Any]) -> np.ndarray:
    """
    Creates a composite feature vector representing a student's profile.
    Combines embeddings of skills_possessed and skills_seeking.
    Resulting vector dimension: 768 (384 + 384).
    """
    possessed = normalize_skill(student_data.get('skills_possessed', ""))
    seeking = normalize_skill(student_data.get('skills_seeking', ""))
    
    # Generate embeddings (Day 32 service)
    v_pos = np.array(encode(possessed))
    v_seek = np.array(encode(seeking))
    
    # Concatenate to form a complete persona vector
    return np.concatenate([v_pos, v_seek])

def build_feature_matrix(students: List[Dict[str, Any]]) -> np.ndarray:
    """Converts a list of student records into a NumPy matrix for clustering."""
    if not students:
        return np.array([])
    return np.array([build_peer_feature_vector(s) for s in students])