# tests/test_benchmarking.py
import pytest
from matching.benchmarking import benchmark_embeddings
from matching.thresholds import apply_similarity_threshold

def mock_embed(texts):
    return [[0.1] * 384 for _ in texts]

def test_benchmark_metrics():
    texts = ["Sample"] * 10
    metrics = benchmark_embeddings(texts, mock_embed, memory_budget_mb=1000)
    
    assert metrics['sentences_processed'] == 10
    assert metrics['throughput_sps'] > 0
    assert isinstance(metrics['within_budget'], bool)

def test_threshold_pruning_low_signal():
    results = [
        {'id': 1, 'similarity_score': 90.0},
        {'id': 2, 'similarity_score': 30.0}, # Below floor
    ]
    pruned = apply_similarity_threshold(results, min_score=40.0)
    assert len(pruned) == 1
    assert pruned[0]['id'] == 1

def test_threshold_pruning_duplicates():
    # Results are usually sorted by score DESC
    results = [
        {'id': 1, 'similarity_score': 95.0},
        {'id': 2, 'similarity_score': 94.9}, # Near duplicate score
        {'id': 3, 'similarity_score': 80.0},
    ]
    # duplicate_epsilon=0.5 means if |95.0 - 94.9| < 0.5, skip id 2
    pruned = apply_similarity_threshold(results, min_score=40.0, duplicate_epsilon=0.5)
    assert len(pruned) == 2
    assert [r['id'] for r in pruned] == [1, 3]

def test_empty_results_handling():
    assert apply_similarity_threshold([], min_score=40.0) == []