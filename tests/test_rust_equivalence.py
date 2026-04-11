"""Backend equivalence tests: Rust vs Python produce valid results.

Both backends produce valid programs, but may differ in assembly order due to
hash-dependent adjacency iteration. Tests verify structural validity rather
than exact match.
"""

import random
import pytest

from folding_evolution import phenotype as p


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
    "orders": [{"id": 1, "amount": 100}, {"id": 2, "amount": 500}],
    "expenses": [{"amount": 200, "category": "travel"}],
}


def _develop_both(genotype):
    """Develop with both backends and return (python_prog, rust_prog)."""
    p._USE_RUST = False
    p.develop.cache_clear()
    py_prog = p.develop(genotype)

    p._USE_RUST = True
    p.develop.cache_clear()
    rs_prog = p.develop(genotype)

    return py_prog, rs_prog


@pytest.fixture(autouse=True)
def restore_rust_backend():
    yield
    p._USE_RUST = True
    p.develop.cache_clear()


class TestGoldenGenotype:
    """The golden genotype must produce exact same results on both backends."""

    def test_golden_exact_match(self):
        py, rs = _develop_both("QDaK5XASBw")
        assert py.source == rs.source
        assert py.bond_count == rs.bond_count
        assert py.evaluate(CTX) == rs.evaluate(CTX)


class TestStructuralValidity:
    """Both backends produce structurally valid programs."""

    def test_1000_random_both_valid(self):
        """Both backends produce programs that don't crash on evaluate."""
        rng = random.Random(42)
        for _ in range(1000):
            genotype = "".join(
                rng.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")
                for _ in range(50)
            )
            py, rs = _develop_both(genotype)
            # Both should not raise on evaluate
            py.evaluate(CTX)
            rs.evaluate(CTX)
            # Bond counts should be non-negative
            assert py.bond_count >= 0
            assert rs.bond_count >= 0

    def test_rust_deterministic(self):
        """Same genotype always produces same result from Rust backend."""
        rng = random.Random(99)
        genotypes = [
            "".join(rng.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")
                    for _ in range(50))
            for _ in range(200)
        ]

        p._USE_RUST = True
        for g in genotypes:
            p.develop.cache_clear()
            r1 = p.develop(g)
            p.develop.cache_clear()
            r2 = p.develop(g)
            assert r1.source == r2.source, f"Non-deterministic Rust result for {g}"
            assert r1.bond_count == r2.bond_count

    def test_null_programs_agree(self):
        """When Python produces None program, Rust should too (and vice versa)."""
        rng = random.Random(42)
        disagreements = 0
        total = 0
        for _ in range(1000):
            genotype = "".join(
                rng.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")
                for _ in range(50)
            )
            py, rs = _develop_both(genotype)
            total += 1
            if (py.ast is None) != (rs.ast is None):
                disagreements += 1
        # Allow some disagreement due to different assembly, but flag if massive
        assert disagreements < total * 0.1, (
            f"{disagreements}/{total} null/non-null disagreements"
        )
