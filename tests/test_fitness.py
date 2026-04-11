"""Tests for fitness evaluation and data-dependence gate."""

from folding_evolution.data_contexts import make_contexts
from folding_evolution.fitness import evaluate_fitness
from folding_evolution.individual import Individual
from folding_evolution.phenotype import Program


def _make_individual_with_fn(fn):
    """Create an individual with a custom evaluate function."""
    program = Program(ast=None, source="test", bond_count=0, evaluate=fn)
    return Individual(genotype="test", program=program)


def test_perfect_fitness():
    contexts = make_contexts()
    target_fn = lambda ctx: len(ctx["products"])
    ind = _make_individual_with_fn(lambda ctx: len(ctx["products"]))
    fitness = evaluate_fitness(ind, target_fn, contexts)
    assert fitness == 1.0


def test_zero_fitness_wrong_answers():
    contexts = make_contexts()
    target_fn = lambda ctx: len(ctx["products"])
    # Returns varying but wrong answers
    counter = iter(range(100))
    ind = _make_individual_with_fn(lambda ctx: -next(counter))
    fitness = evaluate_fitness(ind, target_fn, contexts)
    assert fitness == 0.0


def test_data_dependence_gate_blocks_constant():
    """Programs that return the same value for all contexts get fitness 0."""
    contexts = make_contexts()
    target_fn = lambda ctx: 42
    # This program always returns 42 — matches target but is constant
    ind = _make_individual_with_fn(lambda ctx: 42)
    fitness = evaluate_fitness(ind, target_fn, contexts)
    assert fitness == 0.0, "Data-dependence gate should block constant outputs"


def test_data_dependence_gate_passes_varying():
    """Programs with varying outputs pass the gate."""
    contexts = make_contexts()
    target_fn = lambda ctx: len(ctx["products"])
    ind = _make_individual_with_fn(lambda ctx: len(ctx["products"]))
    fitness = evaluate_fitness(ind, target_fn, contexts)
    assert fitness > 0.0


def test_no_program_gives_zero():
    ind = Individual(genotype="test", program=None)
    contexts = make_contexts()
    fitness = evaluate_fitness(ind, lambda ctx: 1, contexts)
    assert fitness == 0.0


def test_partial_fitness():
    """An individual that matches some but not all contexts."""
    contexts = make_contexts()
    # products sizes are 2, 3, 5, 7, 4
    target_fn = lambda ctx: len(ctx["products"])
    # Returns varying values, matching only some
    vals = iter([2, 3, 999, 888, 777])
    ind = _make_individual_with_fn(lambda ctx: next(vals))
    fitness = evaluate_fitness(ind, target_fn, contexts)
    assert fitness == 2 / 5


def test_contexts_have_varying_sizes():
    """Verify contexts produce different counts for count(products)."""
    contexts = make_contexts()
    sizes = [len(ctx["products"]) for ctx in contexts]
    assert len(set(sizes)) > 1, "Contexts must have varying product counts"
