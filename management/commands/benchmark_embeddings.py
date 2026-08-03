# management/commands/benchmark_embeddings.py
from django.core.management.base import BaseCommand, CommandError
from matching.embeddings import encode_batch
from matching.benchmarking import benchmark_embeddings

class Command(BaseCommand):
    help = "Benchmark embedding throughput and memory usage."

    def add_arguments(self, parser):
        parser.add_argument('--samples', type=int, default=100)
        parser.add_argument('--budget', type=float, default=512.0, help="Memory budget in MB")

    def handle(self, *args, **options):
        num_samples = options['samples']
        budget = options['budget']
        
        # Generate synthetic test sentences
        test_data = [f"This is a synthetic sample sentence number {i} for benchmarking." for i in range(num_samples)]
        
        self.stdout.write(f"Running benchmark with {num_samples} samples...")
        
        metrics = benchmark_embeddings(test_data, encode_batch, memory_budget_mb=budget)
        
        self.stdout.write("-" * 30)
        self.stdout.write(f"Throughput: {metrics['throughput_sps']} sentences/sec")
        self.stdout.write(f"Elapsed:    {metrics['seconds_elapsed']}s")
        self.stdout.write(f"Peak Memory: {metrics['memory_mb']} MB")
        self.stdout.write("-" * 30)
        
        if not metrics['within_budget']:
            self.stdout.write(self.style.ERROR(f"FAIL: Memory usage exceeded budget of {budget}MB"))
            raise SystemExit(1)
            
        self.stdout.write(self.style.SUCCESS(f"PASS: System cleared budget of {budget}MB"))