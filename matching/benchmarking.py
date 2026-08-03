# matching/benchmarking.py
import time
import os
import psutil
from typing import List, Callable, Dict, Any

def benchmark_embeddings(
    texts: List[str], 
    embed_fn: Callable[[List[str]], Any], 
    memory_budget_mb: float = 512.0
) -> Dict[str, Any]:
    """
    Measures embedding throughput and memory usage.
    Returns metrics and budget compliance status.
    """
    process = psutil.Process(os.getpid())
    initial_mem = process.memory_info().rss / (1024 * 1024)
    
    start_time = time.perf_counter()
    _ = embed_fn(texts)
    end_time = time.perf_counter()
    
    final_mem = process.memory_info().rss / (1024 * 1024)
    elapsed = end_time - start_time
    count = len(texts)
    
    throughput = count / elapsed if elapsed > 0 else 0
    peak_mem_delta = final_mem - initial_mem
    
    return {
        "sentences_processed": count,
        "seconds_elapsed": round(elapsed, 4),
        "throughput_sps": round(throughput, 2),
        "memory_mb": round(final_mem, 2),
        "memory_delta_mb": round(peak_mem_delta, 2),
        "within_budget": final_mem <= memory_budget_mb
    }