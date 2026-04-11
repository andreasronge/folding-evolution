"""Tests for regime-shift dynamics."""

from folding_evolution.config import EvolutionConfig
from folding_evolution.data_contexts import make_contexts
from folding_evolution.dynamics import run_regime_shift, partial_credit
from folding_evolution.phenotype import develop
from folding_evolution.direct import develop_direct


def _small_config():
    return EvolutionConfig(
        population_size=20,
        genotype_length=30,
        generations=10,
        tournament_size=3,
        elite_count=2,
        mutation_rate=0.3,
        crossover_rate=0.7,
        seed=42,
    )


def _targets_a():
    return [lambda ctx: len(ctx["products"])]


def _targets_b():
    return [lambda ctx: len(ctx["employees"])]


def test_regime_shift_completes():
    """A regime shift run completes and returns the expected structure."""
    config = _small_config()
    contexts = make_contexts()

    result = run_regime_shift(
        config, _targets_a(), _targets_b(),
        regime_a_gens=5, regime_b_gens=5,
        contexts=contexts, develop_fn=develop,
    )

    assert "history" in result
    assert "shift_gen" in result
    assert "fitness_jumps" in result
    assert result["shift_gen"] == 5
    assert len(result["history"]) == 10


def test_regime_shift_direct_completes():
    """Direct encoding regime shift completes."""
    config = _small_config()
    contexts = make_contexts()

    result = run_regime_shift(
        config, _targets_a(), _targets_b(),
        regime_a_gens=5, regime_b_gens=5,
        contexts=contexts, develop_fn=develop_direct,
    )

    assert len(result["history"]) == 10
    assert result["shift_gen"] == 5


def test_history_has_correct_generations():
    """Generation numbers in history are sequential."""
    config = _small_config()
    contexts = make_contexts()

    result = run_regime_shift(
        config, _targets_a(), _targets_b(),
        regime_a_gens=5, regime_b_gens=5,
        contexts=contexts, develop_fn=develop,
    )

    gens = [s.generation for s in result["history"]]
    assert gens == list(range(10))


def test_same_initial_genotypes():
    """When given initial_genotypes, both runs start from the same population."""
    config = _small_config()
    contexts = make_contexts()

    from folding_evolution.alphabet import random_genotype
    import random
    rng = random.Random(99)
    genotypes = [random_genotype(30, rng) for _ in range(20)]

    result = run_regime_shift(
        config, _targets_a(), _targets_b(),
        regime_a_gens=3, regime_b_gens=3,
        contexts=contexts, develop_fn=develop,
        initial_genotypes=genotypes,
    )

    assert len(result["history"]) == 6


def test_multi_target():
    """Multiple targets per regime work correctly."""
    config = _small_config()
    contexts = make_contexts()

    targets_a = [
        lambda ctx: len(ctx["products"]),
        lambda ctx: ctx["products"][0],
    ]
    targets_b = [
        lambda ctx: len(ctx["employees"]),
    ]

    result = run_regime_shift(
        config, targets_a, targets_b,
        regime_a_gens=3, regime_b_gens=3,
        contexts=contexts, develop_fn=develop,
    )

    assert len(result["history"]) == 6


# --- partial_credit tests ---

def test_partial_credit_exact_match():
    assert partial_credit(5, 5) == 1.0
    assert partial_credit([1, 2], [1, 2]) == 1.0


def test_partial_credit_none():
    assert partial_credit(None, 5) == 0.0


def test_partial_credit_numeric_near():
    score = partial_credit(4, 5)
    assert 0.5 < score < 1.0


def test_partial_credit_numeric_far():
    score = partial_credit(100, 5)
    assert score == 0.1


def test_partial_credit_list_length():
    score = partial_credit([1, 2, 3], [1, 2, 3, 4, 5])
    assert 0.1 < score < 1.0


def test_partial_credit_wrong_type():
    assert partial_credit("hello", 5) == 0.05
