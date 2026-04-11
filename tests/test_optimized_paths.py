"""Tests for optimized experiment paths: Rust VM scoring, batch develop,
parallel seeds, and final population consistency.

These tests verify that the optimized code paths produce results equivalent
to the original Python implementations, ensuring the speedups don't alter
experimental semantics.
"""

import random

import pytest

from folding_evolution.alphabet import random_genotype


def _deep_equal(a, b) -> bool:
    """Compare values ignoring dict key ordering (Rust HashMap vs Python dict)."""
    if type(a) != type(b):
        return False
    if isinstance(a, dict):
        if set(a.keys()) != set(b.keys()):
            return False
        return all(_deep_equal(a[k], b[k]) for k in a)
    if isinstance(a, list):
        if len(a) != len(b):
            return False
        return all(_deep_equal(x, y) for x, y in zip(a, b))
    return a == b
from folding_evolution.config import EvolutionConfig
from folding_evolution.data_contexts import make_contexts
from folding_evolution.dynamics import (
    evaluate_multi_target,
    run_regime_shift,
    run_regime_shift_comparison,
    run_regime_shift_comparison_parallel,
    _evolve_phase,
)
from folding_evolution.individual import Individual
from folding_evolution.phenotype import develop, develop_batch
from folding_evolution.stats import StatsCollector

# --- Conditional imports for Rust VM ---
try:
    from _folding_rust import (
        RustContexts,
        RustTargetOutputs,
        rust_develop_and_score_batch,
        rust_vm_evaluate,
    )
    HAS_RUST_VM = True
except ImportError:
    HAS_RUST_VM = False

CONTEXTS = make_contexts()

MULTI_TARGETS = [
    lambda ctx: len(ctx["products"]),
    lambda ctx: ctx["products"][0],
    lambda ctx: len(ctx["products"][1:]),
]

SINGLE_TARGETS = [lambda ctx: len(ctx["products"])]


def _small_config(seed=42):
    return EvolutionConfig(
        population_size=20,
        genotype_length=30,
        generations=10,
        tournament_size=3,
        elite_count=2,
        mutation_rate=0.3,
        crossover_rate=0.7,
        seed=seed,
    )


# ---------------------------------------------------------------------------
# 1. rust_develop_and_score_batch vs Python evaluate_multi_target
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not HAS_RUST_VM, reason="Rust VM not available")
class TestBatchScoringEquivalence:
    """rust_develop_and_score_batch must match Python scoring."""

    def test_multi_target_scoring_1000_genotypes(self):
        rust_ctx = RustContexts(CONTEXTS)
        target_outputs = [[t(ctx) for ctx in CONTEXTS] for t in MULTI_TARGETS]
        rust_targets = RustTargetOutputs(target_outputs)

        rng = random.Random(42)
        genotypes = [random_genotype(50, rng) for _ in range(1000)]

        rust_results = rust_develop_and_score_batch(genotypes, rust_ctx, rust_targets)

        mismatches = []
        for i, g in enumerate(genotypes):
            prog = develop(g)
            ind = Individual(genotype=g)
            ind.program = prog
            py_fitness = evaluate_multi_target(ind, MULTI_TARGETS, CONTEXTS)
            rust_fitness = rust_results[i][0]

            diff = abs(py_fitness - rust_fitness)
            if diff > 1e-10:
                # Only closure-gate artifacts are acceptable
                py_out = prog.evaluate(CONTEXTS[0])
                if not callable(py_out):
                    mismatches.append(
                        f"  [{i}] py={py_fitness:.6f} rust={rust_fitness:.6f} "
                        f"src={prog.source}"
                    )

        if mismatches:
            pytest.fail(
                f"{len(mismatches)} non-closure scoring mismatches:\n"
                + "\n".join(mismatches[:10])
            )

    def test_single_target_scoring_500_genotypes(self):
        rust_ctx = RustContexts(CONTEXTS)
        target_outputs = [[t(ctx) for ctx in CONTEXTS] for t in SINGLE_TARGETS]
        rust_targets = RustTargetOutputs(target_outputs)

        rng = random.Random(99)
        genotypes = [random_genotype(50, rng) for _ in range(500)]

        rust_results = rust_develop_and_score_batch(genotypes, rust_ctx, rust_targets)

        mismatches = []
        for i, g in enumerate(genotypes):
            prog = develop(g)
            ind = Individual(genotype=g)
            ind.program = prog
            py_fitness = evaluate_multi_target(ind, SINGLE_TARGETS, CONTEXTS)
            rust_fitness = rust_results[i][0]

            diff = abs(py_fitness - rust_fitness)
            if diff > 1e-10:
                py_out = prog.evaluate(CONTEXTS[0])
                if not callable(py_out):
                    mismatches.append(
                        f"  [{i}] py={py_fitness:.6f} rust={rust_fitness:.6f} "
                        f"src={prog.source}"
                    )

        if mismatches:
            pytest.fail(
                f"{len(mismatches)} non-closure scoring mismatches:\n"
                + "\n".join(mismatches[:10])
            )


# ---------------------------------------------------------------------------
# 2. rust_vm_evaluate vs Python evaluator
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not HAS_RUST_VM, reason="Rust VM not available")
class TestVmEvaluateEquivalence:
    """rust_vm_evaluate must match Python evaluator per-context."""

    def test_1000_genotypes_all_contexts(self):
        rust_ctx = RustContexts(CONTEXTS)

        rng = random.Random(42)
        genotypes = [random_genotype(50, rng) for _ in range(1000)]

        mismatches = []
        for g in genotypes:
            prog = develop(g)
            vm_results = rust_vm_evaluate(g, rust_ctx)

            for ci, ctx in enumerate(CONTEXTS):
                py_result = prog.evaluate(ctx)
                rust_result = vm_results[ci]

                # Skip closures (repr includes memory address)
                if callable(py_result):
                    continue

                # Use deep equality to ignore dict key ordering
                # (Rust HashMap vs Python dict insertion order)
                if not _deep_equal(py_result, rust_result):
                    mismatches.append(
                        f"  {g[:20]}... ctx{ci}: py={repr(py_result)[:40]} "
                        f"rust={repr(rust_result)[:40]} src={prog.source}"
                    )

        if mismatches:
            pytest.fail(
                f"{len(mismatches)} eval mismatches:\n"
                + "\n".join(mismatches[:10])
            )


# ---------------------------------------------------------------------------
# 3. develop_batch equivalence
# ---------------------------------------------------------------------------

class TestDevelopBatchEquivalence:
    """develop_batch must match per-individual develop."""

    def test_500_genotypes_source_and_bonds(self):
        rng = random.Random(42)
        genotypes = [random_genotype(50, rng) for _ in range(500)]

        individual = [develop(g) for g in genotypes]
        batch = develop_batch(genotypes)

        mismatches = []
        for i, (ind, bat) in enumerate(zip(individual, batch)):
            if ind.source != bat.source or ind.bond_count != bat.bond_count:
                mismatches.append(
                    f"  [{i}] ind=({ind.source}, {ind.bond_count}) "
                    f"bat=({bat.source}, {bat.bond_count})"
                )

        if mismatches:
            pytest.fail(
                f"{len(mismatches)} batch develop mismatches:\n"
                + "\n".join(mismatches[:10])
            )


# ---------------------------------------------------------------------------
# 4. Parallel vs sequential regime shift comparison
# ---------------------------------------------------------------------------

class TestParallelEquivalence:
    """Parallel seed execution must produce identical results to sequential.

    Uses subprocess because fork-based multiprocessing can deadlock
    under pytest's stdout capture.
    """

    def test_2_seeds_match_sequential(self):
        import subprocess
        import sys

        script = '''
import sys
from folding_evolution.config import EvolutionConfig
from folding_evolution.data_contexts import make_contexts
from folding_evolution.dynamics import run_regime_shift_comparison, run_regime_shift_comparison_parallel

config = EvolutionConfig(population_size=10, genotype_length=30, generations=5,
                         tournament_size=3, elite_count=2, mutation_rate=0.3,
                         crossover_rate=0.7, seed=42)
contexts = make_contexts()
targets = [lambda ctx: len(ctx["products"])]

seq = run_regime_shift_comparison(config, targets, targets, 3, 2, contexts, n_seeds=2)
par = run_regime_shift_comparison_parallel(config, targets, targets, 3, 2, contexts, n_seeds=2, n_workers=2)

ok = True
for i in range(2):
    sf = seq["folding_runs"][i]["history"][-1].best_fitness
    pf = par["folding_runs"][i]["history"][-1].best_fitness
    sd = seq["direct_runs"][i]["history"][-1].best_fitness
    pd = par["direct_runs"][i]["history"][-1].best_fitness
    if sf != pf or sd != pd:
        print(f"MISMATCH seed {i}: folding seq={sf} par={pf} direct seq={sd} par={pd}", file=sys.stderr)
        ok = False

sys.exit(0 if ok else 1)
'''
        result = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            pytest.fail(
                f"Parallel/sequential mismatch:\n{result.stderr}\n{result.stdout}"
            )


# ---------------------------------------------------------------------------
# 5. Final population has callable programs and consistent fitness
# ---------------------------------------------------------------------------

class TestFinalPopulationConsistency:
    """After _evolve_phase, all individuals must have callable programs
    and fitness that matches what the program actually produces."""

    def test_callable_programs(self):
        config = _small_config()
        rng = random.Random(42)
        pop = [Individual(genotype=random_genotype(30, rng)) for _ in range(20)]
        stats = StatsCollector()

        result_pop = _evolve_phase(
            pop, SINGLE_TARGETS, CONTEXTS, develop, config,
            generations=5, rng=rng, stats=stats, gen_offset=0,
        )

        for ind in result_pop:
            assert ind.program is not None, "program is None"
            assert callable(ind.program.evaluate), (
                f"program.evaluate not callable for {ind.genotype[:20]}..."
            )

    def test_fitness_matches_program(self):
        """Stored fitness must match what re-evaluating the program produces."""
        config = _small_config()
        rng = random.Random(42)
        pop = [Individual(genotype=random_genotype(30, rng)) for _ in range(20)]
        stats = StatsCollector()

        result_pop = _evolve_phase(
            pop, SINGLE_TARGETS, CONTEXTS, develop, config,
            generations=5, rng=rng, stats=stats, gen_offset=0,
        )

        for ind in result_pop:
            recomputed = evaluate_multi_target(ind, SINGLE_TARGETS, CONTEXTS)
            assert abs(ind.fitness - recomputed) < 1e-10, (
                f"Stale fitness: stored={ind.fitness:.6f} "
                f"recomputed={recomputed:.6f} src={ind.program.source}"
            )

    def test_programs_actually_evaluate(self):
        """Programs can be called on contexts without raising."""
        config = _small_config()
        rng = random.Random(42)
        pop = [Individual(genotype=random_genotype(30, rng)) for _ in range(20)]
        stats = StatsCollector()

        result_pop = _evolve_phase(
            pop, SINGLE_TARGETS, CONTEXTS, develop, config,
            generations=5, rng=rng, stats=stats, gen_offset=0,
        )

        for ind in result_pop:
            for ctx in CONTEXTS:
                # Should not raise
                ind.program.evaluate(ctx)
