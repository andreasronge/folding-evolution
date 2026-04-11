"""Fitness evaluation with data-dependence gate."""

from __future__ import annotations

from typing import Any, Callable

from .individual import Individual


def evaluate_fitness(
    individual: Individual,
    target_fn: Callable[[dict], Any],
    contexts: list[dict],
) -> float:
    """Evaluate fitness as fraction of contexts where program output matches target.

    Data-dependence gate: if the program produces the same output for ALL contexts,
    fitness is 0 (the program is not using context data).
    """
    if individual.program is None:
        return 0.0

    outputs = []
    matches = 0
    for ctx in contexts:
        result = individual.program.evaluate(ctx)
        target = target_fn(ctx)
        outputs.append(result)
        if result == target:
            matches += 1

    # Data-dependence gate: all outputs identical means not data-dependent
    if len(set(repr(o) for o in outputs)) <= 1:
        return 0.0

    return matches / len(contexts)
