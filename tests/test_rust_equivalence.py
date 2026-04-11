"""Backend equivalence tests: Rust must produce identical results to Python.

Exact phenotype equivalence: same source, same bond_count, same evaluation
result on fixed contexts. Any divergence means the Rust backend is a new
representation variant, not an implementation optimization.
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
    """Develop with both backends."""
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
    def test_exact_match(self):
        py, rs = _develop_both("QDaK5XASBw")
        assert py.source == rs.source
        assert py.bond_count == rs.bond_count
        assert py.evaluate(CTX) == rs.evaluate(CTX)


class TestExactEquivalence:
    """Exact phenotype equivalence over random genotypes."""

    def test_1000_random_length30_source_and_bonds(self):
        rng = random.Random(42)
        mismatches = []
        for i in range(1000):
            genotype = "".join(
                rng.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")
                for _ in range(30)
            )
            py, rs = _develop_both(genotype)
            if py.source != rs.source or py.bond_count != rs.bond_count:
                mismatches.append((i, genotype, py.source, rs.source, py.bond_count, rs.bond_count))

        if mismatches:
            msg = f"{len(mismatches)} mismatches out of 1000:\n"
            for idx, g, ps, rs_src, pb, rb in mismatches[:10]:
                msg += f"  [{idx}] {g}: py=({ps}, {pb}) rust=({rs_src}, {rb})\n"
            pytest.fail(msg)

    def test_1000_random_length50_source_and_bonds(self):
        rng = random.Random(99)
        mismatches = []
        for i in range(1000):
            genotype = "".join(
                rng.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")
                for _ in range(50)
            )
            py, rs = _develop_both(genotype)
            if py.source != rs.source or py.bond_count != rs.bond_count:
                mismatches.append((i, genotype, py.source, rs.source, py.bond_count, rs.bond_count))

        if mismatches:
            msg = f"{len(mismatches)} mismatches out of 1000:\n"
            for idx, g, ps, rs_src, pb, rb in mismatches[:10]:
                msg += f"  [{idx}] {g}: py=({ps}, {pb}) rust=({rs_src}, {rb})\n"
            pytest.fail(msg)

    def test_500_random_eval_equivalence(self):
        """Identical evaluate() results on fixed context."""
        rng = random.Random(777)
        mismatches = []
        for i in range(500):
            genotype = "".join(
                rng.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")
                for _ in range(50)
            )
            py, rs = _develop_both(genotype)
            py_result = py.evaluate(CTX)
            rs_result = rs.evaluate(CTX)
            # Skip callable results (fn expressions return closures, not comparable by repr)
            if callable(py_result) or callable(rs_result):
                continue
            if repr(py_result) != repr(rs_result):
                mismatches.append((i, genotype, py_result, rs_result, py.source, rs.source))

        if mismatches:
            msg = f"{len(mismatches)} eval mismatches out of 500:\n"
            for idx, g, pr, rr, ps, rs_src in mismatches[:10]:
                msg += f"  [{idx}] {g}: py_eval={pr} rust_eval={rr}\n"
                msg += f"         py_src={ps} rust_src={rs_src}\n"
            pytest.fail(msg)

    def test_rust_deterministic(self):
        """Same genotype always produces same result from Rust backend."""
        rng = random.Random(123)
        p._USE_RUST = True
        for _ in range(500):
            genotype = "".join(
                rng.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")
                for _ in range(50)
            )
            p.develop.cache_clear()
            r1 = p.develop(genotype)
            p.develop.cache_clear()
            r2 = p.develop(genotype)
            assert r1.source == r2.source, f"Non-deterministic for {genotype}"
            assert r1.bond_count == r2.bond_count
