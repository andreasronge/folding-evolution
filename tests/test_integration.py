"""Integration tests for the full pipeline: genotype -> program -> evaluation."""

import random
import time

from folding_evolution.phenotype import develop


CTX = {
    "products": [
        {"price": 600, "name": "Widget", "status": "active"},
        {"price": 400, "name": "Gadget", "status": "inactive"},
        {"price": 800, "name": "Doohickey", "status": "active"},
    ],
    "employees": [
        {"name": "Alice", "department": "eng"},
        {"name": "Bob", "department": "sales"},
    ],
    "orders": [
        {"id": 1, "amount": 100},
        {"id": 2, "amount": 500},
    ],
    "expenses": [
        {"amount": 200, "category": "travel"},
    ],
}


class TestGoldenGenotype:
    """Milestone 1 acceptance criteria for QDaK5XASBw."""

    def test_evaluation(self):
        prog = develop("QDaK5XASBw")
        result = prog.evaluate(CTX)
        assert result == [
            {"price": 600, "name": "Widget", "status": "active"},
            {"price": 800, "name": "Doohickey", "status": "active"},
        ]

    def test_source_string(self):
        prog = develop("QDaK5XASBw")
        assert prog.source == "(filter (fn x (> (get x :price) 500)) data/products)"

    def test_bond_count(self):
        prog = develop("QDaK5XASBw")
        assert prog.bond_count == 4


class TestRobustness:
    def test_1000_random_genotypes(self):
        """All 1000 random genotypes complete without exception."""
        rng = random.Random(42)
        for _ in range(1000):
            length = 30
            genotype = "".join(
                rng.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")
                for _ in range(length)
            )
            prog = develop(genotype)
            # evaluate should not raise
            prog.evaluate(CTX)


class TestBenchmark:
    def test_benchmark_1000_genotypes(self):
        """Benchmark develop() on 1000 random genotypes of length 50."""
        # Clear the cache so we measure actual computation
        develop.cache_clear()

        rng = random.Random(99)
        genotypes = [
            "".join(
                rng.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")
                for _ in range(50)
            )
            for _ in range(1000)
        ]

        start = time.perf_counter()
        for g in genotypes:
            develop(g)
        elapsed = time.perf_counter() - start

        print(f"\nBenchmark: 1000 develop() calls on length-50 genotypes: {elapsed:.3f}s")
        # Should complete in reasonable time (< 10s)
        assert elapsed < 10.0
